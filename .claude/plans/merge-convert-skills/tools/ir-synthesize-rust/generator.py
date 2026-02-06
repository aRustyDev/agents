"""Rust code generator.

This module provides the core code generation logic for synthesizing
Rust source code from IR.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ir_core.models import (
        Constraint,
        Field_,
        Function,
        MethodSignature,
        Param,
        Receiver,
        TypeDef,
        TypeParam,
        TypeRef,
        Variant,
    )

    from .ownership import OwnershipChoice, OwnershipPlan, ParamOwnership

logger = logging.getLogger(__name__)


# IR type ID to Rust type mapping
IR_TO_RUST_TYPE = {
    "builtins.int": "i64",
    "builtins.float": "f64",
    "builtins.bool": "bool",
    "builtins.str": "String",
    "builtins.bytes": "Vec<u8>",
    "builtins.None": "()",
    "builtins.list": "Vec",
    "builtins.dict": "HashMap",
    "builtins.set": "HashSet",
    "typing.Optional": "Option",
    "typing.Any": "Box<dyn std::any::Any>",
    "typing.Callable": "Box<dyn Fn",  # Special handling needed
    "rust.Result": "Result",
    "rust.Box": "Box",
    "rust.Rc": "Rc",
    "rust.Arc": "Arc",
    "rust.RefCell": "RefCell",
    "rust.Mutex": "Mutex",
    "rust.RwLock": "RwLock",
}

# IR visibility to Rust visibility
IR_TO_RUST_VIS = {
    "public": "pub",
    "internal": "pub(crate)",
    "package": "pub(super)",
    "private": "",
    "protected": "pub(crate)",  # No direct equivalent
}


@dataclass
class SynthesisContext:
    """Context for synthesis operations.

    Attributes:
        ownership_plan: Current ownership plan
        imports_needed: Set of imports to add
        current_lifetimes: Active lifetime parameters
        indent_level: Current indentation level
        indent_str: Indentation string
    """

    ownership_plan: OwnershipPlan | None = None
    imports_needed: set[str] = field(default_factory=set)
    current_lifetimes: list[str] = field(default_factory=list)
    indent_level: int = 0
    indent_str: str = "    "

    def indent(self) -> str:
        """Get current indentation."""
        return self.indent_str * self.indent_level


class RustCodeGenerator:
    """Generate Rust code from IR constructs.

    This generator produces idiomatic Rust code with proper ownership,
    lifetimes, and type annotations.

    Example:
        generator = RustCodeGenerator()
        code = generator.gen_function(func, context)
    """

    def __init__(self) -> None:
        """Initialize the code generator."""
        pass

    def gen_type_ref(
        self, type_ref: "TypeRef", context: SynthesisContext
    ) -> str:
        """Generate Rust type from TypeRef.

        Args:
            type_ref: Type reference
            context: Synthesis context

        Returns:
            Rust type string
        """
        from ir_core.models import TypeRefKind

        if type_ref.kind == TypeRefKind.NAMED:
            return self._gen_named_type(type_ref, context)

        elif type_ref.kind == TypeRefKind.GENERIC:
            return type_ref.type_id or "T"

        elif type_ref.kind == TypeRefKind.REFERENCE:
            inner = self.gen_type_ref(
                TypeRef(
                    kind=TypeRefKind.NAMED,
                    type_id=type_ref.type_id,
                    args=type_ref.args,
                ),
                context,
            ) if type_ref.type_id else "T"

            lifetime = ""
            if type_ref.lifetime_name:
                lifetime = f"'{type_ref.lifetime_name} "

            if type_ref.mutable:
                return f"&{lifetime}mut {inner}"
            return f"&{lifetime}{inner}"

        elif type_ref.kind == TypeRefKind.TUPLE:
            elements = ", ".join(
                self.gen_type_ref(e, context)
                for e in type_ref.elements
            )
            return f"({elements})"

        elif type_ref.kind == TypeRefKind.FUNCTION:
            params = ", ".join(
                self.gen_type_ref(p, context)
                for p in type_ref.params
            )
            ret = self.gen_type_ref(type_ref.return_type, context) if type_ref.return_type else "()"
            return f"fn({params}) -> {ret}"

        elif type_ref.kind == TypeRefKind.UNION:
            # Rust doesn't have union types like TS
            # Use enum or first type
            if type_ref.members:
                return self.gen_type_ref(type_ref.members[0], context)
            return "Box<dyn std::any::Any>"

        return "/* unknown type */"

    def _gen_named_type(
        self, type_ref: "TypeRef", context: SynthesisContext
    ) -> str:
        """Generate a named type.

        Args:
            type_ref: Named type reference
            context: Synthesis context

        Returns:
            Rust type string
        """
        type_id = type_ref.type_id or ""

        # Map IR type to Rust
        if type_id in IR_TO_RUST_TYPE:
            base = IR_TO_RUST_TYPE[type_id]
        elif type_id.startswith("rust."):
            base = type_id[5:]  # Strip "rust." prefix
        else:
            # Use the last segment of the type ID
            base = type_id.rsplit(".", 1)[-1] if "." in type_id else type_id

        # Handle generic arguments
        if type_ref.args:
            args_str = ", ".join(
                self.gen_type_ref(arg, context)
                for arg in type_ref.args
            )
            return f"{base}<{args_str}>"

        # Add necessary imports
        if base in ("HashMap", "HashSet"):
            context.imports_needed.add("std::collections::" + base)
        elif base in ("Rc", "Arc"):
            context.imports_needed.add("std::sync::" + base if base == "Arc" else "std::rc::Rc")
        elif base in ("RefCell", "Mutex", "RwLock"):
            if base == "RefCell":
                context.imports_needed.add("std::cell::RefCell")
            else:
                context.imports_needed.add("std::sync::" + base)

        return base

    def gen_visibility(self, visibility: str) -> str:
        """Generate visibility modifier.

        Args:
            visibility: IR visibility

        Returns:
            Rust visibility string
        """
        rust_vis = IR_TO_RUST_VIS.get(visibility, "")
        return rust_vis + " " if rust_vis else ""

    def gen_type_params(
        self,
        params: list["TypeParam"],
        lifetimes: list[str] | None = None,
        constraints: list["Constraint"] | None = None,
    ) -> str:
        """Generate generic type parameters.

        Args:
            params: Type parameters
            lifetimes: Lifetime parameters
            constraints: Type constraints

        Returns:
            Rust generics string (including angle brackets)
        """
        parts: list[str] = []

        # Add lifetimes first
        if lifetimes:
            parts.extend(f"'{lt}" for lt in lifetimes)

        # Add type parameters
        for param in params:
            param_str = param.name
            if param.bounds:
                bounds_str = " + ".join(
                    self._constraint_to_rust(b) for b in param.bounds
                )
                param_str += f": {bounds_str}"
            parts.append(param_str)

        if not parts:
            return ""

        return f"<{', '.join(parts)}>"

    def _constraint_to_rust(self, bound: "TypeRef") -> str:
        """Convert a type bound to Rust syntax.

        Args:
            bound: Type bound

        Returns:
            Rust trait bound string
        """
        from ir_core.models import TypeRefKind

        if bound.kind == TypeRefKind.NAMED:
            type_id = bound.type_id or ""
            if type_id.startswith("rust."):
                return type_id[5:]
            return type_id.rsplit(".", 1)[-1]

        return "?Sized"

    def gen_where_clause(
        self, constraints: list["Constraint"] | None
    ) -> str:
        """Generate where clause.

        Args:
            constraints: Type constraints

        Returns:
            Rust where clause string
        """
        if not constraints:
            return ""

        clauses: list[str] = []
        for c in constraints:
            if c.bound:
                bound_str = self._constraint_to_rust(c.bound)
                clauses.append(f"{c.param}: {bound_str}")

        if not clauses:
            return ""

        return " where " + ", ".join(clauses)

    def gen_param(
        self,
        param: "Param",
        context: SynthesisContext,
        ownership: "ParamOwnership | None" = None,
    ) -> str:
        """Generate function parameter.

        Args:
            param: Parameter
            context: Synthesis context
            ownership: Ownership plan for this param

        Returns:
            Rust parameter string
        """
        from ir_core.models import Mutability

        from .ownership import LifetimeChoice, OwnershipChoice

        name = param.name

        # Determine type based on ownership
        base_type = self.gen_type_ref(param.type, context)

        if ownership:
            if ownership.ownership == OwnershipChoice.BORROWED:
                lifetime = ""
                if (
                    ownership.lifetime == LifetimeChoice.EXPLICIT
                    and ownership.lifetime_name
                ):
                    lifetime = f"'{ownership.lifetime_name} "
                type_str = f"&{lifetime}{base_type}"
            elif ownership.ownership == OwnershipChoice.MUT_BORROWED:
                lifetime = ""
                if (
                    ownership.lifetime == LifetimeChoice.EXPLICIT
                    and ownership.lifetime_name
                ):
                    lifetime = f"'{ownership.lifetime_name} "
                type_str = f"&{lifetime}mut {base_type}"
            else:
                type_str = base_type
        else:
            # Infer from mutability
            if param.mutability == Mutability.MUTABLE:
                type_str = f"&mut {base_type}"
            elif param.mutability == Mutability.MOVE:
                type_str = base_type
            else:
                type_str = f"&{base_type}"

        # Check if param needs mut keyword
        mut_kw = ""
        if param.mutability == Mutability.MUTABLE:
            mut_kw = "mut "

        return f"{mut_kw}{name}: {type_str}"

    def gen_receiver(
        self, receiver: "Receiver", context: SynthesisContext
    ) -> str:
        """Generate method receiver.

        Args:
            receiver: Receiver definition
            context: Synthesis context

        Returns:
            Rust receiver string
        """
        from ir_core.models import Mutability

        if receiver.mutability == Mutability.MUTABLE:
            return "&mut self"
        elif receiver.mutability == Mutability.MOVE:
            return "self"
        else:
            return "&self"

    def gen_function(
        self,
        func: "Function",
        context: SynthesisContext,
    ) -> str:
        """Generate function definition.

        Args:
            func: Function
            context: Synthesis context

        Returns:
            Rust function string
        """
        from ir_core.models import EffectKind

        lines: list[str] = []
        indent = context.indent()

        # Doc comment
        if func.doc_comment:
            for line in func.doc_comment.split("\n"):
                lines.append(f"{indent}/// {line}")

        # Build signature
        sig_parts: list[str] = []

        # Visibility
        vis = self.gen_visibility(func.visibility.value if hasattr(func.visibility, 'value') else str(func.visibility))
        if vis.strip():
            sig_parts.append(vis.strip())

        # Async/unsafe
        if any(e.kind == EffectKind.ASYNC for e in func.effects):
            sig_parts.append("async")
        if any(e.kind == EffectKind.UNSAFE for e in func.effects):
            sig_parts.append("unsafe")

        sig_parts.append("fn")
        sig_parts.append(func.name)

        # Generic parameters
        lifetimes = []
        if context.ownership_plan:
            lifetimes = context.ownership_plan.required_lifetimes

        generics = self.gen_type_params(
            func.type_params,
            lifetimes if lifetimes else None,
            func.constraints if hasattr(func, 'constraints') else None,
        )

        sig = " ".join(sig_parts) + generics

        # Parameters
        param_strs: list[str] = []

        # Add receiver if present
        if func.receiver:
            param_strs.append(self.gen_receiver(func.receiver, context))

        # Add regular parameters
        for param in func.params:
            ownership = None
            if context.ownership_plan:
                ownership = context.ownership_plan.params.get(param.name)
            param_strs.append(self.gen_param(param, context, ownership))

        sig += f"({', '.join(param_strs)})"

        # Return type
        ret_type = self.gen_type_ref(func.return_type, context)
        if ret_type != "()":
            sig += f" -> {ret_type}"

        # Where clause
        if hasattr(func, 'constraints') and func.constraints:
            sig += self.gen_where_clause(func.constraints)

        # Body or semicolon
        if func.body:
            sig += " {"
            lines.append(f"{indent}{sig}")
            lines.append(f"{indent}    todo!()")
            lines.append(f"{indent}}}")
        else:
            sig += ";"
            lines.append(f"{indent}{sig}")

        return "\n".join(lines)

    def gen_struct(
        self, type_def: "TypeDef", context: SynthesisContext
    ) -> str:
        """Generate struct definition.

        Args:
            type_def: Type definition
            context: Synthesis context

        Returns:
            Rust struct string
        """
        lines: list[str] = []
        indent = context.indent()

        # Visibility and name
        vis = self.gen_visibility(type_def.visibility.value if hasattr(type_def.visibility, 'value') else str(type_def.visibility))
        generics = self.gen_type_params(type_def.params, None, type_def.constraints)
        where_clause = self.gen_where_clause(type_def.constraints)

        # Check for tuple struct
        if type_def.body.fields and all(f.name.startswith("_") for f in type_def.body.fields):
            # Tuple struct
            field_types = ", ".join(
                f"{self.gen_visibility(f.visibility.value if hasattr(f.visibility, 'value') else str(f.visibility))}{self.gen_type_ref(f.type, context)}"
                for f in type_def.body.fields
            )
            lines.append(f"{indent}{vis}struct {type_def.name}{generics}({field_types}){where_clause};")
        elif not type_def.body.fields:
            # Unit struct
            lines.append(f"{indent}{vis}struct {type_def.name}{generics}{where_clause};")
        else:
            # Regular struct
            lines.append(f"{indent}{vis}struct {type_def.name}{generics}{where_clause} {{")
            context.indent_level += 1
            for field in type_def.body.fields:
                field_str = self.gen_field(field, context)
                lines.append(field_str)
            context.indent_level -= 1
            lines.append(f"{indent}}}")

        return "\n".join(lines)

    def gen_field(
        self, field: "Field_", context: SynthesisContext
    ) -> str:
        """Generate struct field.

        Args:
            field: Field definition
            context: Synthesis context

        Returns:
            Rust field string
        """
        indent = context.indent()
        vis = self.gen_visibility(field.visibility.value if hasattr(field.visibility, 'value') else str(field.visibility))
        type_str = self.gen_type_ref(field.type, context)

        return f"{indent}{vis}{field.name}: {type_str},"

    def gen_enum(
        self, type_def: "TypeDef", context: SynthesisContext
    ) -> str:
        """Generate enum definition.

        Args:
            type_def: Type definition
            context: Synthesis context

        Returns:
            Rust enum string
        """
        lines: list[str] = []
        indent = context.indent()

        vis = self.gen_visibility(type_def.visibility.value if hasattr(type_def.visibility, 'value') else str(type_def.visibility))
        generics = self.gen_type_params(type_def.params, None, type_def.constraints)
        where_clause = self.gen_where_clause(type_def.constraints)

        lines.append(f"{indent}{vis}enum {type_def.name}{generics}{where_clause} {{")

        context.indent_level += 1
        for variant in type_def.body.variants:
            variant_str = self.gen_variant(variant, context)
            lines.append(variant_str)
        context.indent_level -= 1

        lines.append(f"{indent}}}")

        return "\n".join(lines)

    def gen_variant(
        self, variant: "Variant", context: SynthesisContext
    ) -> str:
        """Generate enum variant.

        Args:
            variant: Variant definition
            context: Synthesis context

        Returns:
            Rust variant string
        """
        indent = context.indent()

        if variant.kind == "unit":
            disc = f" = {variant.discriminant}" if variant.discriminant is not None else ""
            return f"{indent}{variant.name}{disc},"

        elif variant.kind == "tuple":
            types = ", ".join(
                self.gen_type_ref(t, context)
                for t in variant.types
            )
            return f"{indent}{variant.name}({types}),"

        elif variant.kind == "struct":
            lines = [f"{indent}{variant.name} {{"]
            context.indent_level += 1
            for field in variant.fields:
                field_str = self.gen_field(field, context)
                lines.append(field_str)
            context.indent_level -= 1
            lines.append(f"{indent}}},")
            return "\n".join(lines)

        return f"{indent}{variant.name},"

    def gen_trait(
        self, type_def: "TypeDef", context: SynthesisContext
    ) -> str:
        """Generate trait definition.

        Args:
            type_def: Type definition
            context: Synthesis context

        Returns:
            Rust trait string
        """
        lines: list[str] = []
        indent = context.indent()

        vis = self.gen_visibility(type_def.visibility.value if hasattr(type_def.visibility, 'value') else str(type_def.visibility))
        generics = self.gen_type_params(type_def.params, None, None)

        # Build supertrait bounds
        supertraits = ""
        type_bounds = [c for c in type_def.constraints if c.param == "Self"]
        if type_bounds:
            bounds_str = " + ".join(
                self._constraint_to_rust(c.bound)
                for c in type_bounds
                if c.bound
            )
            if bounds_str:
                supertraits = f": {bounds_str}"

        # Non-Self constraints go in where clause
        other_constraints = [c for c in type_def.constraints if c.param != "Self"]
        where_clause = self.gen_where_clause(other_constraints) if other_constraints else ""

        lines.append(f"{indent}{vis}trait {type_def.name}{generics}{supertraits}{where_clause} {{")

        context.indent_level += 1

        # Required methods
        for method in type_def.body.required_methods:
            method_str = self.gen_method_signature(method, context)
            lines.append(method_str)

        context.indent_level -= 1

        lines.append(f"{indent}}}")

        return "\n".join(lines)

    def gen_method_signature(
        self, method: "MethodSignature", context: SynthesisContext
    ) -> str:
        """Generate trait method signature.

        Args:
            method: Method signature
            context: Synthesis context

        Returns:
            Rust method signature string
        """
        from ir_core.models import EffectKind

        indent = context.indent()

        # Build signature
        sig_parts: list[str] = []

        # Async
        if any(e.kind == EffectKind.ASYNC for e in method.effects):
            sig_parts.append("async")

        sig_parts.append("fn")
        sig_parts.append(method.name)

        generics = self.gen_type_params(method.type_params)
        sig = " ".join(sig_parts) + generics

        # Parameters (assume &self)
        param_strs = ["&self"]
        for param in method.params:
            param_strs.append(self.gen_param(param, context))

        sig += f"({', '.join(param_strs)})"

        # Return type
        ret_type = self.gen_type_ref(method.return_type, context)
        if ret_type != "()":
            sig += f" -> {ret_type}"

        sig += ";"

        return f"{indent}{sig}"

    def gen_impl(
        self,
        trait_name: str | None,
        self_type: str,
        methods: list["Function"],
        context: SynthesisContext,
    ) -> str:
        """Generate impl block.

        Args:
            trait_name: Trait being implemented (None for inherent impl)
            self_type: Type implementing the trait
            methods: Methods in the impl
            context: Synthesis context

        Returns:
            Rust impl block string
        """
        lines: list[str] = []
        indent = context.indent()

        if trait_name:
            lines.append(f"{indent}impl {trait_name} for {self_type} {{")
        else:
            lines.append(f"{indent}impl {self_type} {{")

        context.indent_level += 1
        for method in methods:
            method_str = self.gen_function(method, context)
            lines.append(method_str)
            lines.append("")
        context.indent_level -= 1

        lines.append(f"{indent}}}")

        return "\n".join(lines)
