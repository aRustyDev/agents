"""Ownership planning for Rust code synthesis.

This module provides ownership analysis and planning for generating
borrow-checker-valid Rust code from IR.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ir_core.models import (
        Function,
        IRVersion,
        Param,
        TypeRef,
    )

logger = logging.getLogger(__name__)


class OwnershipChoice(str, Enum):
    """Ownership choice for a parameter or binding."""

    OWNED = "owned"  # T - takes ownership
    BORROWED = "borrowed"  # &T - shared borrow
    MUT_BORROWED = "mut_borrowed"  # &mut T - mutable borrow
    COPY = "copy"  # T where T: Copy


class LifetimeChoice(str, Enum):
    """Lifetime choice for a reference."""

    ELIDED = "elided"  # Let Rust infer
    EXPLICIT = "explicit"  # Named lifetime like 'a
    STATIC = "static"  # 'static


@dataclass
class ParamOwnership:
    """Ownership plan for a parameter.

    Attributes:
        name: Parameter name
        ownership: Chosen ownership mode
        lifetime: Lifetime choice if borrowed
        lifetime_name: Explicit lifetime name if needed
    """

    name: str
    ownership: OwnershipChoice
    lifetime: LifetimeChoice = LifetimeChoice.ELIDED
    lifetime_name: str | None = None


@dataclass
class BindingOwnership:
    """Ownership plan for a local binding.

    Attributes:
        name: Binding name
        ownership: Ownership mode
        is_mut: Whether binding is mutable
        moved_to: Where value is moved (if moved)
    """

    name: str
    ownership: OwnershipChoice
    is_mut: bool = False
    moved_to: str | None = None


@dataclass
class OwnershipPlan:
    """Complete ownership plan for a function.

    Attributes:
        function_id: Function being planned
        params: Ownership for each parameter
        bindings: Ownership for local bindings
        return_ownership: Ownership of return value
        return_lifetime: Lifetime of return (if reference)
        required_lifetimes: Lifetime parameters needed
    """

    function_id: str
    params: dict[str, ParamOwnership] = field(default_factory=dict)
    bindings: dict[str, BindingOwnership] = field(default_factory=dict)
    return_ownership: OwnershipChoice = OwnershipChoice.OWNED
    return_lifetime: LifetimeChoice = LifetimeChoice.ELIDED
    required_lifetimes: list[str] = field(default_factory=list)


# IR type IDs that map to Copy types in Rust
COPY_TYPE_IDS = frozenset({
    "builtins.int",
    "builtins.float",
    "builtins.bool",
    "builtins.None",
})


class OwnershipPlanner:
    """Plan ownership for Rust code synthesis.

    This planner analyzes IR to determine appropriate ownership modes
    for parameters, bindings, and return values to generate valid Rust code.

    Example:
        planner = OwnershipPlanner()
        plan = planner.plan_function(func, ir)
        for param, ownership in plan.params.items():
            print(f"{param}: {ownership.ownership}")
    """

    def __init__(self) -> None:
        """Initialize the ownership planner."""
        self._lifetime_counter = 0

    def plan_ir(self, ir: "IRVersion") -> dict[str, OwnershipPlan]:
        """Plan ownership for all functions in IR.

        Args:
            ir: IRVersion to plan

        Returns:
            Dict mapping function IDs to ownership plans
        """
        plans: dict[str, OwnershipPlan] = {}

        for func in ir.functions:
            plan = self.plan_function(func, ir)
            plans[func.id] = plan

        return plans

    def plan_function(
        self, func: "Function", ir: "IRVersion"
    ) -> OwnershipPlan:
        """Plan ownership for a function.

        Args:
            func: Function to plan
            ir: Full IR for context

        Returns:
            OwnershipPlan for the function
        """
        plan = OwnershipPlan(function_id=func.id)
        self._lifetime_counter = 0

        # Analyze parameters
        for param in func.params:
            ownership = self._plan_param_ownership(param, func, ir)
            plan.params[param.name] = ownership

            # Track required lifetimes
            if (
                ownership.lifetime == LifetimeChoice.EXPLICIT
                and ownership.lifetime_name
                and ownership.lifetime_name not in plan.required_lifetimes
            ):
                plan.required_lifetimes.append(ownership.lifetime_name)

        # Analyze return type
        if func.return_type:
            plan.return_ownership = self._plan_return_ownership(
                func.return_type, func, ir
            )

            # Check if return needs lifetime from params
            if self._is_reference_type(func.return_type):
                plan.return_lifetime = self._plan_return_lifetime(func, plan)

        return plan

    def _plan_param_ownership(
        self,
        param: "Param",
        func: "Function",
        ir: "IRVersion",
    ) -> ParamOwnership:
        """Plan ownership for a parameter.

        Args:
            param: Parameter to plan
            func: Containing function
            ir: Full IR

        Returns:
            ParamOwnership for the parameter
        """
        # Check if type is Copy
        if self._is_copy_type(param.type):
            return ParamOwnership(
                name=param.name,
                ownership=OwnershipChoice.COPY,
            )

        # Check annotations for ownership hints
        for ann in param.annotations:
            if ann.kind == "MM-002":  # Ownership annotation
                ownership_value = ann.value.get("ownership", "borrowed")
                if ownership_value == "owned":
                    return ParamOwnership(
                        name=param.name,
                        ownership=OwnershipChoice.OWNED,
                    )
                elif ownership_value == "mut_borrowed":
                    return ParamOwnership(
                        name=param.name,
                        ownership=OwnershipChoice.MUT_BORROWED,
                        lifetime=LifetimeChoice.ELIDED,
                    )
                else:
                    return ParamOwnership(
                        name=param.name,
                        ownership=OwnershipChoice.BORROWED,
                        lifetime=LifetimeChoice.ELIDED,
                    )

        # Default: borrow for complex types
        # Use mutable borrow if param is marked mutable
        from ir_core.models import Mutability
        if param.mutability == Mutability.MUTABLE:
            return ParamOwnership(
                name=param.name,
                ownership=OwnershipChoice.MUT_BORROWED,
                lifetime=LifetimeChoice.ELIDED,
            )

        return ParamOwnership(
            name=param.name,
            ownership=OwnershipChoice.BORROWED,
            lifetime=LifetimeChoice.ELIDED,
        )

    def _plan_return_ownership(
        self,
        return_type: "TypeRef",
        func: "Function",
        ir: "IRVersion",
    ) -> OwnershipChoice:
        """Plan ownership for return value.

        Args:
            return_type: Return type
            func: Function
            ir: Full IR

        Returns:
            Ownership choice for return
        """
        # Copy types return by value
        if self._is_copy_type(return_type):
            return OwnershipChoice.COPY

        # References return borrowed
        if self._is_reference_type(return_type):
            return OwnershipChoice.BORROWED

        # Default: return owned
        return OwnershipChoice.OWNED

    def _plan_return_lifetime(
        self, func: "Function", plan: "OwnershipPlan"
    ) -> LifetimeChoice:
        """Plan lifetime for reference return.

        Applies Rust lifetime elision rules.

        Args:
            func: Function
            plan: Current ownership plan

        Returns:
            Lifetime choice for return
        """
        # Count borrowed parameters
        borrowed_params = [
            p for p in plan.params.values()
            if p.ownership in (OwnershipChoice.BORROWED, OwnershipChoice.MUT_BORROWED)
        ]

        # Elision rule 1: If exactly one borrowed param, use its lifetime
        if len(borrowed_params) == 1:
            return LifetimeChoice.ELIDED

        # Elision rule 2: If receiver exists, use its lifetime
        if func.receiver:
            return LifetimeChoice.ELIDED

        # Multiple borrowed params - need explicit lifetimes
        if len(borrowed_params) > 1:
            # Assign explicit lifetimes
            for param in borrowed_params:
                if param.lifetime == LifetimeChoice.ELIDED:
                    param.lifetime = LifetimeChoice.EXPLICIT
                    param.lifetime_name = self._next_lifetime_name()
                    if param.lifetime_name not in plan.required_lifetimes:
                        plan.required_lifetimes.append(param.lifetime_name)

            return LifetimeChoice.EXPLICIT

        return LifetimeChoice.ELIDED

    def _is_copy_type(self, type_ref: "TypeRef") -> bool:
        """Check if a type is Copy.

        Args:
            type_ref: Type to check

        Returns:
            True if type implements Copy
        """
        from ir_core.models import TypeRefKind

        if type_ref.kind == TypeRefKind.REFERENCE:
            return True  # References are Copy

        if type_ref.type_id in COPY_TYPE_IDS:
            return True

        return False

    def _is_reference_type(self, type_ref: "TypeRef") -> bool:
        """Check if type is a reference.

        Args:
            type_ref: Type to check

        Returns:
            True if type is a reference
        """
        from ir_core.models import TypeRefKind
        return type_ref.kind == TypeRefKind.REFERENCE

    def _next_lifetime_name(self) -> str:
        """Generate next lifetime name."""
        self._lifetime_counter += 1
        if self._lifetime_counter <= 26:
            return chr(ord('a') + self._lifetime_counter - 1)
        return f"l{self._lifetime_counter}"


@dataclass
class UsageAnalysis:
    """Analysis of how a value is used.

    Attributes:
        is_consumed: Value is consumed/moved
        is_mutated: Value is mutated
        is_borrowed: Value is borrowed
        is_mut_borrowed: Value is mutably borrowed
        borrow_count: Number of times borrowed
    """

    is_consumed: bool = False
    is_mutated: bool = False
    is_borrowed: bool = False
    is_mut_borrowed: bool = False
    borrow_count: int = 0


def analyze_usage(
    param_name: str, func: "Function", ir: "IRVersion"
) -> UsageAnalysis:
    """Analyze how a parameter is used in a function.

    Args:
        param_name: Parameter name
        func: Function containing the parameter
        ir: Full IR

    Returns:
        Usage analysis for the parameter
    """
    # This is a simplified analysis
    # In a full implementation, we'd analyze the CFG

    analysis = UsageAnalysis()

    # Check function annotations for hints
    for ann in func.annotations:
        if ann.kind == "param_usage" and ann.value.get("param") == param_name:
            usage = ann.value.get("usage", "read")
            if usage == "consumed":
                analysis.is_consumed = True
            elif usage == "mutated":
                analysis.is_mutated = True
            elif usage == "borrowed":
                analysis.is_borrowed = True
            elif usage == "mut_borrowed":
                analysis.is_mut_borrowed = True

    return analysis
