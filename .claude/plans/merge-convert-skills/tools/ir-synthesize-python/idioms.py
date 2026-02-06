"""Python idiom generation utilities.

This module provides the PythonIdiomGenerator class for generating idiomatic
Python patterns from IR constructs. It handles comprehensions, context managers,
dataclasses, async patterns, and other Python-specific idioms.

Example:
    idiom_gen = PythonIdiomGenerator()
    comprehension = idiom_gen.gen_comprehension(pattern)
    context_mgr = idiom_gen.gen_context_manager(pattern)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

from ir_core.models import (
    TypeDef,
    TypeKind,
    TypeRef,
    TypeRefKind,
    Function,
    Expression,
    ExpressionKind,
    ControlFlowGraph,
    Block,
    Statement,
    Terminator,
    TerminatorKind,
    EffectKind,
    Field_,
)

if TYPE_CHECKING:
    from .synthesizer import SynthesisContext


class IdiomKind(str, Enum):
    """Kinds of Python idioms.

    Attributes:
        LIST_COMPREHENSION: List comprehension pattern
        DICT_COMPREHENSION: Dict comprehension pattern
        SET_COMPREHENSION: Set comprehension pattern
        GENERATOR_EXPRESSION: Generator expression pattern
        CONTEXT_MANAGER: Context manager (with statement) pattern
        DATACLASS: Dataclass pattern
        ASYNC_AWAIT: Async/await pattern
        DECORATOR: Decorator pattern
        PATTERN_MATCHING: Match statement pattern (Python 3.10+)
        WALRUS: Walrus operator (:=) pattern
        F_STRING: F-string pattern
        UNPACKING: Tuple/list unpacking pattern
    """

    LIST_COMPREHENSION = "list_comprehension"
    DICT_COMPREHENSION = "dict_comprehension"
    SET_COMPREHENSION = "set_comprehension"
    GENERATOR_EXPRESSION = "generator_expression"
    CONTEXT_MANAGER = "context_manager"
    DATACLASS = "dataclass"
    ASYNC_AWAIT = "async_await"
    DECORATOR = "decorator"
    PATTERN_MATCHING = "pattern_matching"
    WALRUS = "walrus"
    F_STRING = "f_string"
    UNPACKING = "unpacking"


@dataclass
class Pattern:
    """Represents a detected or requested pattern.

    Attributes:
        kind: The kind of idiom
        source: Original IR element
        metadata: Additional pattern-specific data
    """

    kind: IdiomKind
    source: Any
    metadata: dict[str, Any]


@dataclass
class IdiomResult:
    """Result of idiom generation.

    Attributes:
        code: Generated code
        success: Whether generation succeeded
        imports_needed: Set of imports needed for the idiom
        notes: Any notes or warnings
    """

    code: str
    success: bool
    imports_needed: set[str]
    notes: list[str]


class PythonIdiomGenerator:
    """Generate idiomatic Python patterns from IR constructs.

    This class analyzes IR structures and generates idiomatic Python code
    patterns like comprehensions, context managers, and dataclasses.

    Example:
        idiom_gen = PythonIdiomGenerator()

        # Generate a list comprehension from a loop pattern
        result = idiom_gen.gen_comprehension(pattern)
        if result.success:
            print(result.code)  # [x * 2 for x in items if x > 0]

        # Generate a dataclass from a struct TypeDef
        result = idiom_gen.gen_dataclass(type_def, context)
    """

    def __init__(self, target_version: str = "3.11") -> None:
        """Initialize the idiom generator.

        Args:
            target_version: Target Python version for idiom selection
        """
        self.target_version = target_version
        self._version_tuple = self._parse_version(target_version)

    def gen_comprehension(self, pattern: Pattern) -> IdiomResult:
        """Generate a list/dict/set comprehension from a loop pattern.

        Args:
            pattern: Pattern containing loop information

        Returns:
            IdiomResult with generated comprehension
        """
        if pattern.kind == IdiomKind.LIST_COMPREHENSION:
            return self._gen_list_comprehension(pattern)
        elif pattern.kind == IdiomKind.DICT_COMPREHENSION:
            return self._gen_dict_comprehension(pattern)
        elif pattern.kind == IdiomKind.SET_COMPREHENSION:
            return self._gen_set_comprehension(pattern)
        elif pattern.kind == IdiomKind.GENERATOR_EXPRESSION:
            return self._gen_generator_expression(pattern)

        return IdiomResult(
            code="",
            success=False,
            imports_needed=set(),
            notes=["Unknown comprehension type"],
        )

    def gen_context_manager(self, pattern: Pattern) -> IdiomResult:
        """Generate a context manager pattern (with statement).

        Args:
            pattern: Pattern containing resource management information

        Returns:
            IdiomResult with generated context manager code
        """
        metadata = pattern.metadata

        resource_expr = metadata.get("resource_expr", "resource")
        resource_name = metadata.get("resource_name", "ctx")
        body = metadata.get("body", "pass")

        code = f"with {resource_expr} as {resource_name}:\n    {body}"

        return IdiomResult(
            code=code,
            success=True,
            imports_needed=set(),
            notes=[],
        )

    def gen_dataclass(
        self, type_def: TypeDef, context: "SynthesisContext"
    ) -> IdiomResult:
        """Generate a dataclass from a struct TypeDef.

        Args:
            type_def: TypeDef to convert to dataclass
            context: Synthesis context

        Returns:
            IdiomResult with generated dataclass code
        """
        imports_needed: set[str] = {"dataclasses.dataclass"}
        notes: list[str] = []

        # Check for field defaults requiring field()
        needs_field = any(
            field.default_value is not None or self._needs_field_factory(field)
            for field in type_def.body.fields
        )
        if needs_field:
            imports_needed.add("dataclasses.field")

        lines: list[str] = []

        # Decorator
        decorator_args: list[str] = []

        # Check for frozen (immutable) hint
        if any(a.kind == "frozen" for a in type_def.annotations):
            decorator_args.append("frozen=True")

        # Check for slots hint
        if any(a.kind == "slots" for a in type_def.annotations):
            if self._version_tuple >= (3, 10):
                decorator_args.append("slots=True")
            else:
                notes.append("slots=True requires Python 3.10+")

        if decorator_args:
            lines.append(f"@dataclass({', '.join(decorator_args)})")
        else:
            lines.append("@dataclass")

        # Class signature with generic params
        generics = ""
        if type_def.params:
            param_names = ", ".join(p.name for p in type_def.params)
            generics = f"[{param_names}]"

        lines.append(f"class {type_def.name}{generics}:")

        # Docstring
        doc = self._extract_docstring(type_def)
        if doc:
            lines.append(f'    """{doc}"""')
            lines.append("")

        # Fields
        for field in type_def.body.fields:
            field_line = self._gen_dataclass_field(field, context)
            lines.append(f"    {field_line}")

        # Empty class handling
        if not type_def.body.fields:
            lines.append("    pass")

        return IdiomResult(
            code="\n".join(lines),
            success=True,
            imports_needed=imports_needed,
            notes=notes,
        )

    def gen_async_pattern(self, pattern: Pattern) -> IdiomResult:
        """Generate async/await patterns.

        Args:
            pattern: Pattern containing async operation information

        Returns:
            IdiomResult with generated async code
        """
        metadata = pattern.metadata
        async_type = metadata.get("type", "await")

        if async_type == "await":
            return self._gen_await_expression(pattern)
        elif async_type == "async_for":
            return self._gen_async_for(pattern)
        elif async_type == "async_with":
            return self._gen_async_with(pattern)
        elif async_type == "gather":
            return self._gen_asyncio_gather(pattern)
        elif async_type == "create_task":
            return self._gen_create_task(pattern)

        return IdiomResult(
            code="",
            success=False,
            imports_needed=set(),
            notes=["Unknown async pattern type"],
        )

    def gen_pattern_match(self, pattern: Pattern) -> IdiomResult:
        """Generate a match statement (Python 3.10+).

        Args:
            pattern: Pattern containing match information

        Returns:
            IdiomResult with generated match statement
        """
        if self._version_tuple < (3, 10):
            # Fall back to if/elif chain
            return self._gen_match_as_if_chain(pattern)

        metadata = pattern.metadata
        subject = metadata.get("subject", "value")
        cases = metadata.get("cases", [])

        lines: list[str] = [f"match {subject}:"]

        for case in cases:
            case_pattern = case.get("pattern", "_")
            case_body = case.get("body", "pass")
            guard = case.get("guard")

            if guard:
                lines.append(f"    case {case_pattern} if {guard}:")
            else:
                lines.append(f"    case {case_pattern}:")

            for body_line in case_body.split("\n"):
                lines.append(f"        {body_line}")

        return IdiomResult(
            code="\n".join(lines),
            success=True,
            imports_needed=set(),
            notes=[],
        )

    def gen_decorator_pattern(self, pattern: Pattern) -> IdiomResult:
        """Generate a decorator pattern.

        Args:
            pattern: Pattern containing decorator information

        Returns:
            IdiomResult with generated decorator code
        """
        metadata = pattern.metadata
        decorator_type = metadata.get("type", "simple")

        if decorator_type == "simple":
            return self._gen_simple_decorator(pattern)
        elif decorator_type == "parametrized":
            return self._gen_parametrized_decorator(pattern)
        elif decorator_type == "class":
            return self._gen_class_decorator(pattern)

        return IdiomResult(
            code="",
            success=False,
            imports_needed=set(),
            notes=["Unknown decorator type"],
        )

    def gen_unpacking(self, pattern: Pattern) -> IdiomResult:
        """Generate unpacking patterns.

        Args:
            pattern: Pattern containing unpacking information

        Returns:
            IdiomResult with generated unpacking code
        """
        metadata = pattern.metadata
        source = metadata.get("source", "items")
        targets = metadata.get("targets", ["a", "b"])
        rest = metadata.get("rest")

        if rest:
            # Extended unpacking: a, *rest = items
            target_str = ", ".join(targets[:-1]) + f", *{rest}"
        else:
            target_str = ", ".join(targets)

        return IdiomResult(
            code=f"{target_str} = {source}",
            success=True,
            imports_needed=set(),
            notes=[],
        )

    def gen_walrus(self, pattern: Pattern) -> IdiomResult:
        """Generate walrus operator pattern (:=).

        Args:
            pattern: Pattern containing assignment expression information

        Returns:
            IdiomResult with generated walrus operator code
        """
        if self._version_tuple < (3, 8):
            return IdiomResult(
                code="",
                success=False,
                imports_needed=set(),
                notes=["Walrus operator requires Python 3.8+"],
            )

        metadata = pattern.metadata
        target = metadata.get("target", "x")
        value = metadata.get("value", "compute()")
        context_expr = metadata.get("context", "if")

        if context_expr == "if":
            condition = metadata.get("condition", "{target}")
            condition = condition.format(target=target)
            code = f"if ({target} := {value}) {condition}:"
        elif context_expr == "while":
            condition = metadata.get("condition", "{target}")
            condition = condition.format(target=target)
            code = f"while ({target} := {value}) {condition}:"
        else:
            code = f"({target} := {value})"

        return IdiomResult(
            code=code,
            success=True,
            imports_needed=set(),
            notes=[],
        )

    def gen_f_string(self, pattern: Pattern) -> IdiomResult:
        """Generate f-string from string formatting pattern.

        Args:
            pattern: Pattern containing string formatting information

        Returns:
            IdiomResult with generated f-string
        """
        metadata = pattern.metadata
        template = metadata.get("template", "")
        values = metadata.get("values", {})

        # Convert format string to f-string
        f_string = 'f"' + template + '"'

        return IdiomResult(
            code=f_string,
            success=True,
            imports_needed=set(),
            notes=[],
        )

    def detect_loop_comprehension(
        self, cfg: ControlFlowGraph
    ) -> Pattern | None:
        """Detect if a CFG represents a comprehension-compatible loop.

        Args:
            cfg: Control flow graph to analyze

        Returns:
            Pattern if comprehension is possible, None otherwise
        """
        # Look for a simple pattern:
        # 1. Initialize empty list/dict/set
        # 2. Loop over iterable
        # 3. Optionally filter
        # 4. Transform and append/add

        if len(cfg.blocks) < 2:
            return None

        # This is a simplified detection - a full implementation would
        # analyze the CFG more thoroughly
        entry_block = next((b for b in cfg.blocks if b.id == cfg.entry), None)
        if not entry_block:
            return None

        # Check for list initialization
        has_list_init = any(
            stmt.kind == "assign" and self._is_list_init(stmt)
            for stmt in entry_block.statements
        )

        if has_list_init:
            return Pattern(
                kind=IdiomKind.LIST_COMPREHENSION,
                source=cfg,
                metadata={
                    "iterable": "items",
                    "transform": "x",
                    "filter": None,
                },
            )

        return None

    def suggest_idiom(
        self, func: Function, context: "SynthesisContext"
    ) -> list[Pattern]:
        """Suggest idiomatic improvements for a function.

        Args:
            func: Function to analyze
            context: Synthesis context

        Returns:
            List of suggested idiom patterns
        """
        suggestions: list[Pattern] = []

        # Check for comprehension opportunities
        if func.body:
            comp_pattern = self.detect_loop_comprehension(func.body)
            if comp_pattern:
                suggestions.append(comp_pattern)

        # Check for async patterns
        if any(e.kind == EffectKind.ASYNC for e in func.effects):
            # Could suggest async context managers, gather patterns, etc.
            pass

        return suggestions

    def _gen_list_comprehension(self, pattern: Pattern) -> IdiomResult:
        """Generate a list comprehension."""
        metadata = pattern.metadata
        transform = metadata.get("transform", "x")
        iterable = metadata.get("iterable", "items")
        var = metadata.get("var", "x")
        filter_expr = metadata.get("filter")

        if filter_expr:
            code = f"[{transform} for {var} in {iterable} if {filter_expr}]"
        else:
            code = f"[{transform} for {var} in {iterable}]"

        return IdiomResult(
            code=code,
            success=True,
            imports_needed=set(),
            notes=[],
        )

    def _gen_dict_comprehension(self, pattern: Pattern) -> IdiomResult:
        """Generate a dict comprehension."""
        metadata = pattern.metadata
        key_expr = metadata.get("key", "k")
        value_expr = metadata.get("value", "v")
        iterable = metadata.get("iterable", "items")
        var = metadata.get("var", "item")
        filter_expr = metadata.get("filter")

        if filter_expr:
            code = f"{{{key_expr}: {value_expr} for {var} in {iterable} if {filter_expr}}}"
        else:
            code = f"{{{key_expr}: {value_expr} for {var} in {iterable}}}"

        return IdiomResult(
            code=code,
            success=True,
            imports_needed=set(),
            notes=[],
        )

    def _gen_set_comprehension(self, pattern: Pattern) -> IdiomResult:
        """Generate a set comprehension."""
        metadata = pattern.metadata
        transform = metadata.get("transform", "x")
        iterable = metadata.get("iterable", "items")
        var = metadata.get("var", "x")
        filter_expr = metadata.get("filter")

        if filter_expr:
            code = f"{{{transform} for {var} in {iterable} if {filter_expr}}}"
        else:
            code = f"{{{transform} for {var} in {iterable}}}"

        return IdiomResult(
            code=code,
            success=True,
            imports_needed=set(),
            notes=[],
        )

    def _gen_generator_expression(self, pattern: Pattern) -> IdiomResult:
        """Generate a generator expression."""
        metadata = pattern.metadata
        transform = metadata.get("transform", "x")
        iterable = metadata.get("iterable", "items")
        var = metadata.get("var", "x")
        filter_expr = metadata.get("filter")

        if filter_expr:
            code = f"({transform} for {var} in {iterable} if {filter_expr})"
        else:
            code = f"({transform} for {var} in {iterable})"

        return IdiomResult(
            code=code,
            success=True,
            imports_needed=set(),
            notes=[],
        )

    def _gen_await_expression(self, pattern: Pattern) -> IdiomResult:
        """Generate an await expression."""
        metadata = pattern.metadata
        expr = metadata.get("expression", "coro()")

        return IdiomResult(
            code=f"await {expr}",
            success=True,
            imports_needed=set(),
            notes=[],
        )

    def _gen_async_for(self, pattern: Pattern) -> IdiomResult:
        """Generate an async for loop."""
        metadata = pattern.metadata
        var = metadata.get("var", "item")
        iterable = metadata.get("iterable", "async_items()")
        body = metadata.get("body", "pass")

        code = f"async for {var} in {iterable}:\n    {body}"

        return IdiomResult(
            code=code,
            success=True,
            imports_needed=set(),
            notes=[],
        )

    def _gen_async_with(self, pattern: Pattern) -> IdiomResult:
        """Generate an async with statement."""
        metadata = pattern.metadata
        resource = metadata.get("resource", "async_resource()")
        name = metadata.get("name", "ctx")
        body = metadata.get("body", "pass")

        code = f"async with {resource} as {name}:\n    {body}"

        return IdiomResult(
            code=code,
            success=True,
            imports_needed=set(),
            notes=[],
        )

    def _gen_asyncio_gather(self, pattern: Pattern) -> IdiomResult:
        """Generate asyncio.gather pattern."""
        metadata = pattern.metadata
        tasks = metadata.get("tasks", ["task1()", "task2()"])

        tasks_str = ", ".join(tasks)
        code = f"results = await asyncio.gather({tasks_str})"

        return IdiomResult(
            code=code,
            success=True,
            imports_needed={"asyncio"},
            notes=[],
        )

    def _gen_create_task(self, pattern: Pattern) -> IdiomResult:
        """Generate asyncio.create_task pattern."""
        metadata = pattern.metadata
        coro = metadata.get("coro", "coro()")
        name = metadata.get("name", "task")

        code = f"{name} = asyncio.create_task({coro})"

        return IdiomResult(
            code=code,
            success=True,
            imports_needed={"asyncio"},
            notes=[],
        )

    def _gen_match_as_if_chain(self, pattern: Pattern) -> IdiomResult:
        """Generate if/elif chain for match statement (pre-3.10)."""
        metadata = pattern.metadata
        subject = metadata.get("subject", "value")
        cases = metadata.get("cases", [])

        lines: list[str] = []
        first = True

        for case in cases:
            case_pattern = case.get("pattern", "_")
            case_body = case.get("body", "pass")
            guard = case.get("guard")

            if case_pattern == "_":
                # Default case
                if first:
                    lines.append("if True:")
                else:
                    lines.append("else:")
            else:
                # Convert pattern to condition
                condition = self._pattern_to_condition(case_pattern, subject)
                if guard:
                    condition = f"{condition} and {guard}"

                keyword = "if" if first else "elif"
                lines.append(f"{keyword} {condition}:")

            for body_line in case_body.split("\n"):
                lines.append(f"    {body_line}")

            first = False

        return IdiomResult(
            code="\n".join(lines),
            success=True,
            imports_needed=set(),
            notes=["Generated if/elif chain instead of match (pre-Python 3.10)"],
        )

    def _gen_simple_decorator(self, pattern: Pattern) -> IdiomResult:
        """Generate a simple decorator."""
        metadata = pattern.metadata
        name = metadata.get("name", "my_decorator")
        wrapper_body = metadata.get("wrapper_body", "return func(*args, **kwargs)")

        code = f'''def {name}(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        {wrapper_body}
    return wrapper'''

        return IdiomResult(
            code=code,
            success=True,
            imports_needed={"functools"},
            notes=[],
        )

    def _gen_parametrized_decorator(self, pattern: Pattern) -> IdiomResult:
        """Generate a parametrized decorator."""
        metadata = pattern.metadata
        name = metadata.get("name", "my_decorator")
        params = metadata.get("params", ["param"])
        wrapper_body = metadata.get("wrapper_body", "return func(*args, **kwargs)")

        params_str = ", ".join(params)

        code = f'''def {name}({params_str}):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            {wrapper_body}
        return wrapper
    return decorator'''

        return IdiomResult(
            code=code,
            success=True,
            imports_needed={"functools"},
            notes=[],
        )

    def _gen_class_decorator(self, pattern: Pattern) -> IdiomResult:
        """Generate a class-based decorator."""
        metadata = pattern.metadata
        name = metadata.get("name", "MyDecorator")
        call_body = metadata.get("call_body", "return self.func(*args, **kwargs)")

        code = f'''class {name}:
    def __init__(self, func):
        self.func = func
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        {call_body}'''

        return IdiomResult(
            code=code,
            success=True,
            imports_needed={"functools"},
            notes=[],
        )

    def _gen_dataclass_field(
        self, field: Field_, context: "SynthesisContext"
    ) -> str:
        """Generate a dataclass field definition."""
        from .generator import PythonCodeGenerator

        gen = PythonCodeGenerator()
        type_str = gen.gen_type_annotation(field.type, context)

        if self._needs_field_factory(field):
            # Use field() for mutable defaults
            factory = self._get_field_factory(field)
            return f"{field.name}: {type_str} = field(default_factory={factory})"
        elif field.default_value is not None:
            return f"{field.name}: {type_str} = {field.default_value!r}"
        else:
            return f"{field.name}: {type_str}"

    def _needs_field_factory(self, field: Field_) -> bool:
        """Check if a field needs a field factory for its default."""
        default = field.default_value
        if default is None:
            return False

        # Mutable defaults need factories
        if isinstance(default, (list, dict, set)):
            return True

        return False

    def _get_field_factory(self, field: Field_) -> str:
        """Get the factory function for a field's default."""
        default = field.default_value
        if isinstance(default, list):
            return "list"
        elif isinstance(default, dict):
            return "dict"
        elif isinstance(default, set):
            return "set"
        return "lambda: None"

    def _pattern_to_condition(self, pattern: str, subject: str) -> str:
        """Convert a match pattern to an if condition."""
        # Simple pattern conversion
        if pattern.isidentifier():
            # Binding pattern - always matches
            return "True"
        elif pattern.startswith('"') or pattern.startswith("'"):
            # String literal
            return f'{subject} == {pattern}'
        elif pattern.isdigit() or (pattern.startswith("-") and pattern[1:].isdigit()):
            # Numeric literal
            return f'{subject} == {pattern}'
        elif pattern == "None":
            return f'{subject} is None'
        elif pattern == "True" or pattern == "False":
            return f'{subject} is {pattern}'
        else:
            # Complex pattern - needs more sophisticated handling
            return f'{subject} == {pattern}'

    def _is_list_init(self, stmt: Statement) -> bool:
        """Check if a statement initializes an empty list."""
        if stmt.value and hasattr(stmt.value, 'kind'):
            return stmt.value.kind == ExpressionKind.ARRAY and not stmt.value.elements
        return False

    def _extract_docstring(self, type_def: TypeDef) -> str | None:
        """Extract docstring from type definition."""
        for annotation in type_def.annotations:
            if annotation.kind == "docstring":
                return annotation.value.get("text")
        return None

    def _parse_version(self, version: str) -> tuple[int, int]:
        """Parse a version string into a tuple."""
        # Handle "3.11", "py311", etc.
        version = version.lower().replace("py", "")
        if "." in version:
            parts = version.split(".")
            return (int(parts[0]), int(parts[1]))
        elif len(version) >= 2:
            return (int(version[0]), int(version[1:]))
        return (3, 11)
