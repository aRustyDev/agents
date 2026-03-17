"""Python-specific pattern recognition.

This module provides the PythonPatternMatcher class for recognizing
Python idioms and patterns in parsed code. These patterns are used to:

1. Create semantic annotations for the IR
2. Identify potential conversion challenges
3. Detect language-specific constructs

Patterns include:
- Comprehensions (list, dict, set, generator)
- Decorators and metaprogramming
- Context managers (with statements)
- Async patterns (async/await)
- Pattern matching (match/case)
- Exception handling idioms

Example:
    matcher = PythonPatternMatcher()

    # Find all comprehensions
    comprehensions = matcher.detect_comprehensions(tree.root)

    # Find async patterns
    async_patterns = matcher.detect_async_patterns(tree.root)
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum

from ir_core.models import AutomationLevel
from ir_core.treesitter import TreeNode, TSSourceSpan


class PatternKind(str, Enum):
    """Kinds of Python patterns that can be detected.

    Attributes:
        LIST_COMPREHENSION: [x for x in items]
        DICT_COMPREHENSION: {k: v for k, v in items}
        SET_COMPREHENSION: {x for x in items}
        GENERATOR_EXPRESSION: (x for x in items)
        DECORATOR: @decorator
        DECORATOR_FACTORY: @decorator(args)
        CONTEXT_MANAGER: with statement
        ASYNC_FUNCTION: async def
        ASYNC_FOR: async for
        ASYNC_WITH: async with
        AWAIT_EXPRESSION: await expr
        PATTERN_MATCH: match/case
        EXCEPTION_HANDLER: try/except
        EXCEPTION_CHAIN: raise from
        WALRUS_OPERATOR: := assignment expression
        FSTRING: f-string formatting
        PROPERTY_DECORATOR: @property
        CLASSMETHOD_DECORATOR: @classmethod
        STATICMETHOD_DECORATOR: @staticmethod
        DATACLASS: @dataclass
        PROTOCOL: typing.Protocol
        TYPE_ALIAS: TypeAlias
        GENERIC_CLASS: Generic[T]
        OVERLOAD: @overload
        METACLASS: metaclass=
        SLOTS: __slots__
        DUNDER_METHOD: __method__
    """

    # Comprehensions
    LIST_COMPREHENSION = "list_comprehension"
    DICT_COMPREHENSION = "dict_comprehension"
    SET_COMPREHENSION = "set_comprehension"
    GENERATOR_EXPRESSION = "generator_expression"

    # Decorators
    DECORATOR = "decorator"
    DECORATOR_FACTORY = "decorator_factory"
    PROPERTY_DECORATOR = "property_decorator"
    CLASSMETHOD_DECORATOR = "classmethod_decorator"
    STATICMETHOD_DECORATOR = "staticmethod_decorator"
    DATACLASS = "dataclass"
    OVERLOAD = "overload"

    # Context managers
    CONTEXT_MANAGER = "context_manager"
    CONTEXT_MANAGER_PROTOCOL = "context_manager_protocol"

    # Async
    ASYNC_FUNCTION = "async_function"
    ASYNC_FOR = "async_for"
    ASYNC_WITH = "async_with"
    AWAIT_EXPRESSION = "await_expression"
    ASYNC_GENERATOR = "async_generator"

    # Pattern matching
    PATTERN_MATCH = "pattern_match"
    PATTERN_GUARD = "pattern_guard"
    PATTERN_OR = "pattern_or"
    PATTERN_AS = "pattern_as"

    # Exceptions
    EXCEPTION_HANDLER = "exception_handler"
    EXCEPTION_CHAIN = "exception_chain"
    EXCEPTION_GROUP = "exception_group"

    # Python-specific syntax
    WALRUS_OPERATOR = "walrus_operator"
    FSTRING = "fstring"
    UNPACKING = "unpacking"
    STAR_EXPRESSION = "star_expression"

    # Type system
    PROTOCOL = "protocol"
    TYPE_ALIAS = "type_alias"
    GENERIC_CLASS = "generic_class"
    TYPEVAR = "typevar"
    PARAMSPEC = "paramspec"

    # Class features
    METACLASS = "metaclass"
    SLOTS = "slots"
    DUNDER_METHOD = "dunder_method"

    # Unsupported / Problematic
    EXEC_STATEMENT = "exec_statement"
    EVAL_CALL = "eval_call"
    DYNAMIC_IMPORT = "dynamic_import"
    GLOBALS_LOCALS = "globals_locals"


@dataclass
class Pattern:
    """A detected Python pattern.

    Attributes:
        kind: The pattern kind
        span: Source location (TSSourceSpan with byte offsets)
        description: Human-readable description
        confidence: Detection confidence (0.0-1.0)
        automation_level: How automatable conversion is
        details: Pattern-specific details
    """

    kind: PatternKind
    span: TSSourceSpan
    description: str
    confidence: float = 1.0
    automation_level: AutomationLevel = AutomationLevel.FULL
    details: dict[str, str] = field(default_factory=dict)


class PythonPatternMatcher:
    """Recognize Python idioms and patterns.

    This class provides methods to detect various Python-specific patterns
    in parsed source code. Detected patterns are used for:

    1. Semantic annotations in the IR
    2. Gap detection for cross-language conversion
    3. Understanding code structure and intent

    Example:
        matcher = PythonPatternMatcher()
        tree = parser.parse(source)

        # Detect all patterns
        all_patterns = list(matcher.detect_all(tree.root))

        # Detect specific pattern types
        comps = matcher.detect_comprehensions(tree.root)
        async_pats = matcher.detect_async_patterns(tree.root)
    """

    def detect_all(self, root: TreeNode) -> Iterator[Pattern]:
        """Detect all patterns in the tree.

        Args:
            root: Root TreeNode to search

        Yields:
            Detected Pattern objects
        """
        yield from self.detect_comprehensions(root)
        yield from self.detect_decorators(root)
        yield from self.detect_context_managers(root)
        yield from self.detect_async_patterns(root)
        yield from self.detect_pattern_matching(root)
        yield from self.detect_exception_patterns(root)
        yield from self.detect_type_patterns(root)
        yield from self.detect_python_specific(root)
        yield from self.detect_class_patterns(root)

    def detect_unsupported(self, root: TreeNode) -> list[Pattern]:
        """Detect patterns that are problematic for conversion.

        These patterns involve dynamic features that cannot be
        statically analyzed or converted to other languages.

        Args:
            root: Root TreeNode to search

        Returns:
            List of problematic patterns
        """
        patterns: list[Pattern] = []

        # exec() calls
        for node in root.find_all("call"):
            func = node.child_by_field("function")
            if func and func.text == "exec":
                patterns.append(Pattern(
                    kind=PatternKind.EXEC_STATEMENT,
                    span=node.span,
                    description="exec() cannot be statically analyzed",
                    automation_level=AutomationLevel.NONE,
                    details={"function": "exec"},
                ))

        # eval() calls
        for node in root.find_all("call"):
            func = node.child_by_field("function")
            if func and func.text == "eval":
                patterns.append(Pattern(
                    kind=PatternKind.EVAL_CALL,
                    span=node.span,
                    description="eval() cannot be statically analyzed",
                    automation_level=AutomationLevel.NONE,
                    details={"function": "eval"},
                ))

        # __import__ or importlib.import_module with variables
        for node in root.find_all("call"):
            func = node.child_by_field("function")
            if func:
                func_text = func.text
                if func_text in ("__import__", "importlib.import_module"):
                    args = node.child_by_field("arguments")
                    if args:
                        first_arg = args.named_children()[0] if args.named_children() else None
                        if first_arg and first_arg.type != "string":
                            patterns.append(Pattern(
                                kind=PatternKind.DYNAMIC_IMPORT,
                                span=node.span,
                                description="Dynamic import with non-literal module name",
                                automation_level=AutomationLevel.NONE,
                                details={"function": func_text},
                            ))

        # globals() or locals() modification
        for node in root.find_all("call"):
            func = node.child_by_field("function")
            if func and func.text in ("globals", "locals"):
                patterns.append(Pattern(
                    kind=PatternKind.GLOBALS_LOCALS,
                    span=node.span,
                    description=f"{func.text}() allows runtime namespace modification",
                    automation_level=AutomationLevel.NONE,
                    details={"function": func.text},
                ))

        return patterns

    def detect_comprehensions(self, root: TreeNode) -> list[Pattern]:
        """Detect comprehension patterns.

        Args:
            root: Root TreeNode to search

        Returns:
            List of comprehension patterns
        """
        patterns: list[Pattern] = []

        # List comprehensions
        for node in root.find_all("list_comprehension"):
            patterns.append(Pattern(
                kind=PatternKind.LIST_COMPREHENSION,
                span=node.span,
                description="List comprehension",
                details=self._extract_comprehension_details(node),
            ))

        # Dict comprehensions
        for node in root.find_all("dictionary_comprehension"):
            patterns.append(Pattern(
                kind=PatternKind.DICT_COMPREHENSION,
                span=node.span,
                description="Dictionary comprehension",
                details=self._extract_comprehension_details(node),
            ))

        # Set comprehensions
        for node in root.find_all("set_comprehension"):
            patterns.append(Pattern(
                kind=PatternKind.SET_COMPREHENSION,
                span=node.span,
                description="Set comprehension",
                details=self._extract_comprehension_details(node),
            ))

        # Generator expressions
        for node in root.find_all("generator_expression"):
            patterns.append(Pattern(
                kind=PatternKind.GENERATOR_EXPRESSION,
                span=node.span,
                description="Generator expression",
                details=self._extract_comprehension_details(node),
            ))

        return patterns

    def detect_decorators(self, root: TreeNode) -> list[Pattern]:
        """Detect decorator patterns.

        Args:
            root: Root TreeNode to search

        Returns:
            List of decorator patterns
        """
        patterns: list[Pattern] = []

        for node in root.find_all("decorator"):
            dec_name = self._get_decorator_name(node)
            kind = self._classify_decorator(dec_name)

            # Check if it's a decorator factory (has call)
            is_factory = node.find_first("call") is not None

            if is_factory and kind == PatternKind.DECORATOR:
                kind = PatternKind.DECORATOR_FACTORY

            patterns.append(Pattern(
                kind=kind,
                span=node.span,
                description=f"Decorator: {dec_name}",
                automation_level=self._decorator_automation_level(dec_name),
                details={"name": dec_name, "is_factory": str(is_factory)},
            ))

        return patterns

    def detect_context_managers(self, root: TreeNode) -> list[Pattern]:
        """Detect context manager patterns.

        Args:
            root: Root TreeNode to search

        Returns:
            List of context manager patterns
        """
        patterns: list[Pattern] = []

        # with statements
        for node in root.find_all("with_statement"):
            items = node.find_all("with_item")
            patterns.append(Pattern(
                kind=PatternKind.CONTEXT_MANAGER,
                span=node.span,
                description=f"Context manager with {len(items)} item(s)",
                details={"item_count": str(len(items))},
            ))

        # async with statements
        for node in root.find_all("async_with_statement"):
            items = node.find_all("with_item")
            patterns.append(Pattern(
                kind=PatternKind.ASYNC_WITH,
                span=node.span,
                description=f"Async context manager with {len(items)} item(s)",
                details={"item_count": str(len(items)), "async": "true"},
            ))

        # Classes implementing __enter__/__exit__
        for node in root.find_all("class_definition"):
            body = node.child_by_field("body")
            if body:
                methods = [
                    m.child_by_field("name").text
                    for m in body.find_all("function_definition")
                    if m.child_by_field("name")
                ]
                if "__enter__" in methods and "__exit__" in methods:
                    name_node = node.child_by_field("name")
                    patterns.append(Pattern(
                        kind=PatternKind.CONTEXT_MANAGER_PROTOCOL,
                        span=node.span,
                        description="Class implements context manager protocol",
                        details={"class_name": name_node.text if name_node else "unknown"},
                    ))

        return patterns

    def detect_async_patterns(self, root: TreeNode) -> list[Pattern]:
        """Detect async/await patterns.

        Args:
            root: Root TreeNode to search

        Returns:
            List of async patterns
        """
        patterns: list[Pattern] = []

        # Async functions
        for node in root.find_all("async_function_definition"):
            name_node = node.child_by_field("name")
            body = node.child_by_field("body")

            # Check if it's a generator (has yield)
            is_generator = body and (
                body.find_first("yield") is not None or
                body.find_first("yield_from") is not None
            )

            kind = PatternKind.ASYNC_GENERATOR if is_generator else PatternKind.ASYNC_FUNCTION

            patterns.append(Pattern(
                kind=kind,
                span=node.span,
                description=f"Async {'generator' if is_generator else 'function'}: {name_node.text if name_node else 'anonymous'}",
                details={
                    "name": name_node.text if name_node else "anonymous",
                    "is_generator": str(is_generator),
                },
            ))

        # Async for loops
        for node in root.find_all("async_for_statement"):
            patterns.append(Pattern(
                kind=PatternKind.ASYNC_FOR,
                span=node.span,
                description="Async for loop",
            ))

        # Await expressions
        for node in root.find_all("await"):
            patterns.append(Pattern(
                kind=PatternKind.AWAIT_EXPRESSION,
                span=node.span,
                description="Await expression",
            ))

        return patterns

    def detect_pattern_matching(self, root: TreeNode) -> list[Pattern]:
        """Detect pattern matching patterns (Python 3.10+).

        Args:
            root: Root TreeNode to search

        Returns:
            List of pattern matching patterns
        """
        patterns: list[Pattern] = []

        for node in root.find_all("match_statement"):
            cases = node.find_all("case_clause")

            patterns.append(Pattern(
                kind=PatternKind.PATTERN_MATCH,
                span=node.span,
                description=f"Match statement with {len(cases)} case(s)",
                details={"case_count": str(len(cases))},
            ))

            # Look for guards
            for case in cases:
                guard = case.find_first("if_clause")
                if guard:
                    patterns.append(Pattern(
                        kind=PatternKind.PATTERN_GUARD,
                        span=case.span,
                        description="Pattern case with guard",
                    ))

                # Look for or patterns
                or_pattern = case.find_first("or_pattern")
                if or_pattern:
                    patterns.append(Pattern(
                        kind=PatternKind.PATTERN_OR,
                        span=case.span,
                        description="Pattern with or alternatives",
                    ))

                # Look for as patterns
                as_pattern = case.find_first("as_pattern")
                if as_pattern:
                    patterns.append(Pattern(
                        kind=PatternKind.PATTERN_AS,
                        span=case.span,
                        description="Pattern with as binding",
                    ))

        return patterns

    def detect_exception_patterns(self, root: TreeNode) -> list[Pattern]:
        """Detect exception handling patterns.

        Args:
            root: Root TreeNode to search

        Returns:
            List of exception patterns
        """
        patterns: list[Pattern] = []

        for node in root.find_all("try_statement"):
            except_clauses = node.find_all("except_clause")
            finally_clause = node.find_first("finally_clause")
            else_clause = node.find_first("else_clause")

            patterns.append(Pattern(
                kind=PatternKind.EXCEPTION_HANDLER,
                span=node.span,
                description=f"Try statement with {len(except_clauses)} except clause(s)",
                details={
                    "except_count": str(len(except_clauses)),
                    "has_finally": str(finally_clause is not None),
                    "has_else": str(else_clause is not None),
                },
            ))

        # Exception chaining (raise from)
        for node in root.find_all("raise_statement"):
            from_clause = node.find_first("from_clause")
            if from_clause:
                patterns.append(Pattern(
                    kind=PatternKind.EXCEPTION_CHAIN,
                    span=node.span,
                    description="Exception chaining with 'from'",
                ))

        # Exception groups (Python 3.11+)
        for node in root.find_all("try_statement"):
            for except_clause in node.find_all("except_clause"):
                # Check for except* syntax
                if any(c.text == "*" for c in except_clause.children):
                    patterns.append(Pattern(
                        kind=PatternKind.EXCEPTION_GROUP,
                        span=except_clause.span,
                        description="Exception group handler (except*)",
                    ))

        return patterns

    def detect_type_patterns(self, root: TreeNode) -> list[Pattern]:
        """Detect typing-related patterns.

        Args:
            root: Root TreeNode to search

        Returns:
            List of type patterns
        """
        patterns: list[Pattern] = []

        # Protocol classes
        for node in root.find_all("class_definition"):
            bases = node.child_by_field("superclasses")
            if bases:
                for base in bases.named_children():
                    if "Protocol" in base.text:
                        name_node = node.child_by_field("name")
                        patterns.append(Pattern(
                            kind=PatternKind.PROTOCOL,
                            span=node.span,
                            description=f"Protocol class: {name_node.text if name_node else 'unknown'}",
                            details={"class_name": name_node.text if name_node else "unknown"},
                        ))
                        break

        # Generic classes
        for node in root.find_all("class_definition"):
            bases = node.child_by_field("superclasses")
            if bases:
                for base in bases.named_children():
                    if "Generic[" in base.text:
                        name_node = node.child_by_field("name")
                        patterns.append(Pattern(
                            kind=PatternKind.GENERIC_CLASS,
                            span=node.span,
                            description=f"Generic class: {name_node.text if name_node else 'unknown'}",
                            details={"class_name": name_node.text if name_node else "unknown"},
                        ))
                        break

        # TypeVar, ParamSpec definitions
        for node in root.find_all("assignment"):
            right = node.child_by_field("right")
            if right and right.type == "call":
                func = right.child_by_field("function")
                if func:
                    if func.text == "TypeVar":
                        left = node.child_by_field("left")
                        patterns.append(Pattern(
                            kind=PatternKind.TYPEVAR,
                            span=node.span,
                            description=f"TypeVar: {left.text if left else 'unknown'}",
                            details={"name": left.text if left else "unknown"},
                        ))
                    elif func.text == "ParamSpec":
                        left = node.child_by_field("left")
                        patterns.append(Pattern(
                            kind=PatternKind.PARAMSPEC,
                            span=node.span,
                            description=f"ParamSpec: {left.text if left else 'unknown'}",
                            details={"name": left.text if left else "unknown"},
                        ))

        # Type aliases
        for node in root.find_all("type_alias_statement"):
            name = node.child_by_field("name")
            patterns.append(Pattern(
                kind=PatternKind.TYPE_ALIAS,
                span=node.span,
                description=f"Type alias: {name.text if name else 'unknown'}",
                details={"name": name.text if name else "unknown"},
            ))

        return patterns

    def detect_python_specific(self, root: TreeNode) -> list[Pattern]:
        """Detect Python-specific syntax patterns.

        Args:
            root: Root TreeNode to search

        Returns:
            List of Python-specific patterns
        """
        patterns: list[Pattern] = []

        # Walrus operator (:=)
        for node in root.find_all("named_expression"):
            patterns.append(Pattern(
                kind=PatternKind.WALRUS_OPERATOR,
                span=node.span,
                description="Assignment expression (walrus operator)",
            ))

        # F-strings
        for node in root.find_all("string"):
            if node.text.startswith(("f'", 'f"', "F'", 'F"')):
                patterns.append(Pattern(
                    kind=PatternKind.FSTRING,
                    span=node.span,
                    description="F-string formatting",
                ))

        # Unpacking (* in assignment)
        for node in root.find_all("pattern_list"):
            for child in node.children:
                if child.type == "list_splat_pattern":
                    patterns.append(Pattern(
                        kind=PatternKind.UNPACKING,
                        span=node.span,
                        description="Unpacking assignment with *",
                    ))
                    break

        # Star expressions (*expr)
        for node in root.find_all("list_splat"):
            patterns.append(Pattern(
                kind=PatternKind.STAR_EXPRESSION,
                span=node.span,
                description="Star expression (*expr)",
            ))

        return patterns

    def detect_class_patterns(self, root: TreeNode) -> list[Pattern]:
        """Detect class-related patterns.

        Args:
            root: Root TreeNode to search

        Returns:
            List of class patterns
        """
        patterns: list[Pattern] = []

        for node in root.find_all("class_definition"):
            body = node.child_by_field("body")
            if not body:
                continue

            # Check for __slots__
            for stmt in body.named_children():
                if stmt.type == "expression_statement":
                    expr = stmt.named_children()[0] if stmt.named_children() else None
                    if expr and expr.type == "assignment":
                        left = expr.child_by_field("left")
                        if left and left.text == "__slots__":
                            patterns.append(Pattern(
                                kind=PatternKind.SLOTS,
                                span=stmt.span,
                                description="__slots__ definition",
                            ))

            # Check for dunder methods
            for method in body.find_all("function_definition"):
                name_node = method.child_by_field("name")
                if name_node:
                    name = name_node.text
                    if name.startswith("__") and name.endswith("__") and name != "__init__":
                        patterns.append(Pattern(
                            kind=PatternKind.DUNDER_METHOD,
                            span=method.span,
                            description=f"Dunder method: {name}",
                            details={"method_name": name},
                        ))

            # Check for metaclass
            bases = node.child_by_field("superclasses")
            if bases:
                for child in bases.children:
                    if child.type == "keyword_argument":
                        key = child.child_by_field("name")
                        if key and key.text == "metaclass":
                            patterns.append(Pattern(
                                kind=PatternKind.METACLASS,
                                span=node.span,
                                description="Class with metaclass",
                                automation_level=AutomationLevel.PARTIAL,
                            ))

        return patterns

    def _extract_comprehension_details(self, node: TreeNode) -> dict[str, str]:
        """Extract details from a comprehension node."""
        details: dict[str, str] = {}

        # Count for clauses
        for_clauses = node.find_all("for_in_clause")
        details["for_clause_count"] = str(len(for_clauses))

        # Check for conditions
        if_clauses = node.find_all("if_clause")
        details["condition_count"] = str(len(if_clauses))

        # Check for nested comprehension
        nested = (
            node.find_all("list_comprehension") +
            node.find_all("dictionary_comprehension") +
            node.find_all("set_comprehension") +
            node.find_all("generator_expression")
        )
        # Exclude self
        nested = [n for n in nested if n.span != node.span]
        details["is_nested"] = str(len(nested) > 0)

        return details

    def _get_decorator_name(self, node: TreeNode) -> str:
        """Get the name of a decorator."""
        # Check for call (decorator factory)
        call = node.find_first("call")
        if call:
            func = call.child_by_field("function")
            if func:
                return func.text

        # Check for identifier
        ident = node.find_first("identifier")
        if ident:
            return ident.text

        # Check for attribute
        attr = node.find_first("attribute")
        if attr:
            return attr.text

        return "unknown"

    def _classify_decorator(self, name: str) -> PatternKind:
        """Classify a decorator by name."""
        name_lower = name.lower()

        if name in ("property", "cached_property"):
            return PatternKind.PROPERTY_DECORATOR
        elif name in ("classmethod",):
            return PatternKind.CLASSMETHOD_DECORATOR
        elif name in ("staticmethod",):
            return PatternKind.STATICMETHOD_DECORATOR
        elif name in ("dataclass", "dataclasses.dataclass"):
            return PatternKind.DATACLASS
        elif name in ("overload", "typing.overload", "typing_extensions.overload"):
            return PatternKind.OVERLOAD

        return PatternKind.DECORATOR

    def _decorator_automation_level(self, name: str) -> AutomationLevel:
        """Determine automation level for a decorator."""
        # Standard decorators that have clear equivalents
        standard = {
            "property", "classmethod", "staticmethod",
            "dataclass", "dataclasses.dataclass",
            "abstractmethod", "abc.abstractmethod",
        }

        if name in standard:
            return AutomationLevel.FULL

        # Decorators that need manual review
        partial = {
            "cached_property", "functools.lru_cache",
            "contextmanager", "contextlib.contextmanager",
            "wraps", "functools.wraps",
        }

        if name in partial:
            return AutomationLevel.PARTIAL

        # Unknown decorators
        return AutomationLevel.PARTIAL
