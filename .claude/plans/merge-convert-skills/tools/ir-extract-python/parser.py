"""Python-specific tree-sitter parsing layer.

This module provides the PythonParser class for parsing Python source code
using tree-sitter and extracting specific language constructs.

Example:
    parser = PythonParser()
    tree = parser.parse(source_code, "module.py")

    functions = parser.extract_functions(tree)
    classes = parser.extract_classes(tree)
    imports = parser.extract_imports(tree)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ir_core.treesitter import (
    ASTNormalizer,
    GASTKind,
    GASTNode,
    ParseTree,
    TreeNode,
    TreeSitterAdapter,
)

# Python-specific node types
FUNCTION_TYPES = frozenset({
    "function_definition",
    "async_function_definition",
})

CLASS_TYPES = frozenset({
    "class_definition",
})

IMPORT_TYPES = frozenset({
    "import_statement",
    "import_from_statement",
    "future_import_statement",
})

EXPRESSION_TYPES = frozenset({
    "expression_statement",
    "assignment",
    "augmented_assignment",
    "return_statement",
    "yield",
    "pass_statement",
    "break_statement",
    "continue_statement",
    "raise_statement",
    "assert_statement",
    "delete_statement",
    "global_statement",
    "nonlocal_statement",
})

COMPOUND_TYPES = frozenset({
    "if_statement",
    "for_statement",
    "while_statement",
    "try_statement",
    "with_statement",
    "match_statement",
    "async_for_statement",
    "async_with_statement",
})


@dataclass
class ExtractedFunction:
    """Extracted function information from tree-sitter.

    Attributes:
        name: Function name
        node: Original tree node
        is_async: Whether this is an async function
        is_method: Whether this is a class method
        decorators: List of decorator names
        parameters: Parameter names
        return_annotation: Return type annotation text (if any)
        docstring: Function docstring (if any)
    """

    name: str
    node: TreeNode
    is_async: bool = False
    is_method: bool = False
    decorators: list[str] = field(default_factory=list)
    parameters: list[str] = field(default_factory=list)
    return_annotation: str | None = None
    docstring: str | None = None


@dataclass
class ExtractedClass:
    """Extracted class information from tree-sitter.

    Attributes:
        name: Class name
        node: Original tree node
        bases: Base class names
        decorators: List of decorator names
        methods: List of method names
        attributes: List of class attribute names
        docstring: Class docstring (if any)
    """

    name: str
    node: TreeNode
    bases: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    attributes: list[str] = field(default_factory=list)
    docstring: str | None = None


@dataclass
class ExtractedImport:
    """Extracted import information from tree-sitter.

    Attributes:
        node: Original tree node
        module: Module path being imported
        names: Names being imported
        aliases: Aliases for imported names
        is_from: Whether this is a from-import
        is_relative: Whether this is a relative import
        level: Number of leading dots for relative imports
    """

    node: TreeNode
    module: str | None
    names: list[str] = field(default_factory=list)
    aliases: dict[str, str] = field(default_factory=dict)
    is_from: bool = False
    is_relative: bool = False
    level: int = 0


class PythonParser:
    """Python-specific tree-sitter parser.

    This class provides Python-specific parsing functionality on top of the
    generic TreeSitterAdapter. It handles Python-specific constructs like
    async functions, decorators, comprehensions, and match statements.

    Attributes:
        adapter: TreeSitterAdapter for Python

    Example:
        parser = PythonParser()
        tree = parser.parse("def hello(): pass", "hello.py")

        # Extract all functions
        for func in parser.extract_functions(tree):
            print(func.child_by_field("name").text)
    """

    # Tree-sitter queries for Python constructs
    QUERY_FUNCTIONS = """
    (function_definition
        name: (identifier) @name
        parameters: (parameters) @params
        return_type: (type)? @return_type
        body: (block) @body
    ) @function

    (async_function_definition
        name: (identifier) @name
        parameters: (parameters) @params
        return_type: (type)? @return_type
        body: (block) @body
    ) @async_function
    """

    QUERY_CLASSES = """
    (class_definition
        name: (identifier) @name
        superclasses: (argument_list)? @bases
        body: (block) @body
    ) @class
    """

    QUERY_IMPORTS = """
    (import_statement) @import
    (import_from_statement) @from_import
    (future_import_statement) @future_import
    """

    QUERY_COMPREHENSIONS = """
    (list_comprehension) @list_comp
    (dictionary_comprehension) @dict_comp
    (set_comprehension) @set_comp
    (generator_expression) @gen_expr
    """

    QUERY_DECORATORS = """
    (decorator
        (call
            function: (identifier) @name
            arguments: (argument_list) @args
        )?
        (identifier)? @simple_name
    ) @decorator
    """

    def __init__(self) -> None:
        """Initialize the Python parser."""
        self._adapter = TreeSitterAdapter("python")
        self._normalizer = PythonNormalizer()

    def parse(self, source: str, file_path: str = "<string>") -> ParseTree:
        """Parse Python source code.

        Args:
            source: Python source code as string
            file_path: File path for error reporting

        Returns:
            ParseTree with root node and utilities
        """
        return self._adapter.parse(source, file_path)

    def parse_file(self, path: Path) -> ParseTree:
        """Parse a Python file.

        Args:
            path: Path to Python source file

        Returns:
            ParseTree for the file
        """
        return self._adapter.parse_file(path)

    def extract_functions(self, tree: ParseTree) -> list[TreeNode]:
        """Extract all function definitions from the tree.

        This returns top-level functions only. Methods within classes
        are included in the class extraction.

        Args:
            tree: ParseTree to search

        Returns:
            List of function definition TreeNodes
        """
        return self._adapter.find_nodes(tree, list(FUNCTION_TYPES))

    def extract_classes(self, tree: ParseTree) -> list[TreeNode]:
        """Extract all class definitions from the tree.

        Args:
            tree: ParseTree to search

        Returns:
            List of class definition TreeNodes
        """
        return self._adapter.find_nodes(tree, list(CLASS_TYPES))

    def extract_imports(self, tree: ParseTree) -> list[TreeNode]:
        """Extract all import statements from the tree.

        Args:
            tree: ParseTree to search

        Returns:
            List of import statement TreeNodes
        """
        return self._adapter.find_nodes(tree, list(IMPORT_TYPES))

    def extract_function_info(self, func_node: TreeNode) -> ExtractedFunction:
        """Extract detailed information from a function node.

        Args:
            func_node: Function definition TreeNode

        Returns:
            ExtractedFunction with parsed information
        """
        name_node = func_node.child_by_field("name")
        name = name_node.text if name_node else "<anonymous>"

        is_async = func_node.type == "async_function_definition"

        # Extract decorators
        decorators: list[str] = []
        for child in func_node.children:
            if child.type == "decorator":
                dec_name = self._extract_decorator_name(child)
                if dec_name:
                    decorators.append(dec_name)

        # Extract parameters
        params_node = func_node.child_by_field("parameters")
        parameters = self._extract_parameter_names(params_node)

        # Extract return annotation
        return_node = func_node.child_by_field("return_type")
        return_annotation = return_node.text if return_node else None

        # Extract docstring
        body_node = func_node.child_by_field("body")
        docstring = self._extract_docstring(body_node)

        return ExtractedFunction(
            name=name,
            node=func_node,
            is_async=is_async,
            decorators=decorators,
            parameters=parameters,
            return_annotation=return_annotation,
            docstring=docstring,
        )

    def extract_class_info(self, class_node: TreeNode) -> ExtractedClass:
        """Extract detailed information from a class node.

        Args:
            class_node: Class definition TreeNode

        Returns:
            ExtractedClass with parsed information
        """
        name_node = class_node.child_by_field("name")
        name = name_node.text if name_node else "<anonymous>"

        # Extract decorators
        decorators: list[str] = []
        for child in class_node.children:
            if child.type == "decorator":
                dec_name = self._extract_decorator_name(child)
                if dec_name:
                    decorators.append(dec_name)

        # Extract base classes
        bases_node = class_node.child_by_field("superclasses")
        bases = self._extract_base_classes(bases_node)

        # Extract body info
        body_node = class_node.child_by_field("body")
        methods: list[str] = []
        attributes: list[str] = []

        if body_node:
            for child in body_node.named_children():
                if child.type in FUNCTION_TYPES:
                    method_name = child.child_by_field("name")
                    if method_name:
                        methods.append(method_name.text)
                elif child.type == "expression_statement":
                    # Check for attribute assignment
                    expr = child.named_children()[0] if child.named_children() else None
                    if expr and expr.type == "assignment":
                        left = expr.child_by_field("left")
                        if left and left.type == "identifier":
                            attributes.append(left.text)

        # Extract docstring
        docstring = self._extract_docstring(body_node)

        return ExtractedClass(
            name=name,
            node=class_node,
            bases=bases,
            decorators=decorators,
            methods=methods,
            attributes=attributes,
            docstring=docstring,
        )

    def extract_import_info(self, import_node: TreeNode) -> ExtractedImport:
        """Extract detailed information from an import node.

        Args:
            import_node: Import statement TreeNode

        Returns:
            ExtractedImport with parsed information
        """
        is_from = import_node.type in ("import_from_statement", "future_import_statement")

        module: str | None = None
        names: list[str] = []
        aliases: dict[str, str] = {}
        is_relative = False
        level = 0

        if is_from:
            # from X import Y
            module_node = import_node.child_by_field("module_name")

            if module_node:
                if module_node.type == "relative_import":
                    is_relative = True
                    level = sum(1 for c in module_node.children if c.type == ".")
                    dotted = module_node.find_first("dotted_name")
                    if dotted:
                        module = dotted.text
                else:
                    module = module_node.text

            # Extract imported names
            for child in import_node.children:
                if child.type == "dotted_name":
                    names.append(child.text)
                elif child.type == "aliased_import":
                    name_node = child.child_by_field("name")
                    alias_node = child.child_by_field("alias")
                    if name_node:
                        names.append(name_node.text)
                        if alias_node:
                            aliases[name_node.text] = alias_node.text
                elif child.type == "wildcard_import":
                    names.append("*")

        else:
            # import X
            for child in import_node.children:
                if child.type == "dotted_name":
                    names.append(child.text)
                    if module is None:
                        module = child.text
                elif child.type == "aliased_import":
                    name_node = child.child_by_field("name")
                    alias_node = child.child_by_field("alias")
                    if name_node:
                        name = name_node.text
                        names.append(name)
                        if module is None:
                            module = name
                        if alias_node:
                            aliases[name] = alias_node.text

        return ExtractedImport(
            node=import_node,
            module=module,
            names=names,
            aliases=aliases,
            is_from=is_from,
            is_relative=is_relative,
            level=level,
        )

    def find_comprehensions(self, tree: ParseTree) -> list[TreeNode]:
        """Find all comprehension expressions in the tree.

        Args:
            tree: ParseTree to search

        Returns:
            List of comprehension TreeNodes
        """
        comp_types = [
            "list_comprehension",
            "dictionary_comprehension",
            "set_comprehension",
            "generator_expression",
        ]
        return self._adapter.find_nodes(tree, comp_types)

    def find_decorators(self, tree: ParseTree) -> list[TreeNode]:
        """Find all decorators in the tree.

        Args:
            tree: ParseTree to search

        Returns:
            List of decorator TreeNodes
        """
        return self._adapter.find_nodes(tree, ["decorator"])

    def find_with_statements(self, tree: ParseTree) -> list[TreeNode]:
        """Find all with/async with statements in the tree.

        Args:
            tree: ParseTree to search

        Returns:
            List of with statement TreeNodes
        """
        return self._adapter.find_nodes(tree, ["with_statement", "async_with_statement"])

    def find_match_statements(self, tree: ParseTree) -> list[TreeNode]:
        """Find all match statements (Python 3.10+) in the tree.

        Args:
            tree: ParseTree to search

        Returns:
            List of match statement TreeNodes
        """
        return self._adapter.find_nodes(tree, ["match_statement"])

    def find_try_statements(self, tree: ParseTree) -> list[TreeNode]:
        """Find all try/except statements in the tree.

        Args:
            tree: ParseTree to search

        Returns:
            List of try statement TreeNodes
        """
        return self._adapter.find_nodes(tree, ["try_statement"])

    def find_async_nodes(self, tree: ParseTree) -> list[TreeNode]:
        """Find all async-related nodes in the tree.

        Args:
            tree: ParseTree to search

        Returns:
            List of async TreeNodes (functions, for, with, await)
        """
        async_types = [
            "async_function_definition",
            "async_for_statement",
            "async_with_statement",
            "await",
        ]
        return self._adapter.find_nodes(tree, async_types)

    def normalize(self, tree: ParseTree) -> GASTNode:
        """Normalize a parse tree to Generic AST.

        Args:
            tree: ParseTree from tree-sitter

        Returns:
            Root GAST node
        """
        return self._normalizer.normalize(tree)

    def _extract_decorator_name(self, decorator_node: TreeNode) -> str | None:
        """Extract the name from a decorator node."""
        # Decorator can be: @name, @name.attr, @name(args), @name.attr(args)
        for child in decorator_node.named_children():
            if child.type == "identifier" or child.type == "attribute":
                return child.text
            elif child.type == "call":
                func = child.child_by_field("function")
                if func:
                    return func.text
        return None

    def _extract_parameter_names(self, params_node: TreeNode | None) -> list[str]:
        """Extract parameter names from a parameters node."""
        if not params_node:
            return []

        names: list[str] = []

        for child in params_node.named_children():
            if child.type == "identifier":
                names.append(child.text)
            elif child.type in ("typed_parameter", "default_parameter",
                               "typed_default_parameter"):
                name = child.child_by_field("name")
                if name:
                    names.append(name.text)
                elif child.children:
                    first = child.children[0]
                    if first.type == "identifier":
                        names.append(first.text)
            elif child.type == "list_splat_pattern":
                inner = child.named_children()[0] if child.named_children() else None
                if inner:
                    names.append(f"*{inner.text}")
            elif child.type == "dictionary_splat_pattern":
                inner = child.named_children()[0] if child.named_children() else None
                if inner:
                    names.append(f"**{inner.text}")

        return names

    def _extract_base_classes(self, bases_node: TreeNode | None) -> list[str]:
        """Extract base class names from an argument_list node."""
        if not bases_node:
            return []

        bases: list[str] = []

        for child in bases_node.named_children():
            if child.type == "identifier" or child.type == "attribute":
                bases.append(child.text)
            elif child.type == "subscript":
                # Generic base like Generic[T]
                bases.append(child.text)
            elif child.type == "keyword_argument":
                # metaclass=X or similar
                pass

        return bases

    def _extract_docstring(self, body_node: TreeNode | None) -> str | None:
        """Extract docstring from a block body."""
        if not body_node:
            return None

        children = list(body_node.named_children())
        if not children:
            return None

        first = children[0]
        if first.type == "expression_statement":
            expr = first.named_children()[0] if first.named_children() else None
            if expr and expr.type == "string":
                # Remove quotes
                text = expr.text
                if text.startswith('"""') or text.startswith("'''"):
                    return text[3:-3].strip()
                elif text.startswith('"') or text.startswith("'"):
                    return text[1:-1].strip()

        return None


class PythonNormalizer(ASTNormalizer):
    """Python-specific AST normalizer.

    Converts Python tree-sitter CST nodes to normalized GAST nodes.
    """

    def __init__(self) -> None:
        super().__init__("python")
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register Python-specific node handlers."""
        # Functions
        self.register_handler("function_definition", self._normalize_function)
        self.register_handler("async_function_definition", self._normalize_function)

        # Classes
        self.register_handler("class_definition", self._normalize_class)

        # Imports
        self.register_handler("import_statement", self._normalize_import)
        self.register_handler("import_from_statement", self._normalize_import)

        # Control flow
        self.register_handler("if_statement", self._normalize_branch)
        self.register_handler("for_statement", self._normalize_loop)
        self.register_handler("while_statement", self._normalize_loop)
        self.register_handler("try_statement", self._normalize_try)
        self.register_handler("with_statement", self._normalize_with)
        self.register_handler("match_statement", self._normalize_match)

        # Expressions
        self.register_handler("call", self._normalize_call)
        self.register_handler("binary_operator", self._normalize_operator)
        self.register_handler("unary_operator", self._normalize_operator)
        self.register_handler("string", self._normalize_literal)
        self.register_handler("integer", self._normalize_literal)
        self.register_handler("float", self._normalize_literal)
        self.register_handler("true", self._normalize_literal)
        self.register_handler("false", self._normalize_literal)
        self.register_handler("none", self._normalize_literal)
        self.register_handler("identifier", self._normalize_identifier)
        self.register_handler("lambda", self._normalize_lambda)

        # Comprehensions
        self.register_handler("list_comprehension", self._normalize_comprehension)
        self.register_handler("dictionary_comprehension", self._normalize_comprehension)
        self.register_handler("set_comprehension", self._normalize_comprehension)
        self.register_handler("generator_expression", self._normalize_comprehension)

    def _normalize_function(self, node: TreeNode) -> GASTNode:
        """Normalize a function definition."""
        name_node = node.child_by_field("name")
        is_async = node.type == "async_function_definition"

        return GASTNode(
            kind=GASTKind.FUNCTION,
            span=node.span,
            attributes={
                "name": name_node.text if name_node else "<anonymous>",
                "async": is_async,
            },
            children=[self._normalize_node(c) for c in node.named_children()],
        )

    def _normalize_class(self, node: TreeNode) -> GASTNode:
        """Normalize a class definition."""
        name_node = node.child_by_field("name")

        return GASTNode(
            kind=GASTKind.CLASS,
            span=node.span,
            attributes={
                "name": name_node.text if name_node else "<anonymous>",
            },
            children=[self._normalize_node(c) for c in node.named_children()],
        )

    def _normalize_import(self, node: TreeNode) -> GASTNode:
        """Normalize an import statement."""
        return GASTNode(
            kind=GASTKind.IMPORT,
            span=node.span,
            attributes={
                "from": node.type == "import_from_statement",
            },
            children=[self._normalize_node(c) for c in node.named_children()],
        )

    def _normalize_branch(self, node: TreeNode) -> GASTNode:
        """Normalize an if statement."""
        return GASTNode(
            kind=GASTKind.BRANCH,
            span=node.span,
            attributes={},
            children=[self._normalize_node(c) for c in node.named_children()],
        )

    def _normalize_loop(self, node: TreeNode) -> GASTNode:
        """Normalize a for/while statement."""
        loop_type = "for" if "for" in node.type else "while"

        return GASTNode(
            kind=GASTKind.LOOP,
            span=node.span,
            attributes={
                "type": loop_type,
                "async": "async" in node.type,
            },
            children=[self._normalize_node(c) for c in node.named_children()],
        )

    def _normalize_try(self, node: TreeNode) -> GASTNode:
        """Normalize a try statement."""
        return GASTNode(
            kind=GASTKind.TRY,
            span=node.span,
            attributes={},
            children=[self._normalize_node(c) for c in node.named_children()],
        )

    def _normalize_with(self, node: TreeNode) -> GASTNode:
        """Normalize a with statement."""
        return GASTNode(
            kind="context_manager",
            span=node.span,
            attributes={
                "async": "async" in node.type,
            },
            children=[self._normalize_node(c) for c in node.named_children()],
        )

    def _normalize_match(self, node: TreeNode) -> GASTNode:
        """Normalize a match statement (Python 3.10+)."""
        return GASTNode(
            kind=GASTKind.MATCH,
            span=node.span,
            attributes={},
            children=[self._normalize_node(c) for c in node.named_children()],
        )

    def _normalize_call(self, node: TreeNode) -> GASTNode:
        """Normalize a function call."""
        func_node = node.child_by_field("function")

        return GASTNode(
            kind=GASTKind.CALL,
            span=node.span,
            attributes={
                "callee": func_node.text if func_node else None,
            },
            children=[self._normalize_node(c) for c in node.named_children()],
        )

    def _normalize_operator(self, node: TreeNode) -> GASTNode:
        """Normalize an operator expression."""
        op_node = node.child_by_field("operator")

        return GASTNode(
            kind=GASTKind.OPERATOR,
            span=node.span,
            attributes={
                "operator": op_node.text if op_node else None,
                "unary": node.type == "unary_operator",
            },
            children=[self._normalize_node(c) for c in node.named_children()],
        )

    def _normalize_literal(self, node: TreeNode) -> GASTNode:
        """Normalize a literal value."""
        return GASTNode(
            kind=GASTKind.LITERAL,
            span=node.span,
            attributes={
                "type": node.type,
                "value": node.text,
            },
        )

    def _normalize_identifier(self, node: TreeNode) -> GASTNode:
        """Normalize an identifier."""
        return GASTNode(
            kind=GASTKind.IDENTIFIER,
            span=node.span,
            attributes={
                "name": node.text,
            },
        )

    def _normalize_lambda(self, node: TreeNode) -> GASTNode:
        """Normalize a lambda expression."""
        return GASTNode(
            kind=GASTKind.LAMBDA,
            span=node.span,
            attributes={},
            children=[self._normalize_node(c) for c in node.named_children()],
        )

    def _normalize_comprehension(self, node: TreeNode) -> GASTNode:
        """Normalize a comprehension expression."""
        comp_type = node.type.replace("_comprehension", "").replace("_expression", "")

        return GASTNode(
            kind="comprehension",
            span=node.span,
            attributes={
                "type": comp_type,
            },
            children=[self._normalize_node(c) for c in node.named_children()],
        )
