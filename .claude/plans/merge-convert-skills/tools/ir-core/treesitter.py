"""Tree-sitter adapter for language-agnostic parsing.

This module provides a generic wrapper around tree-sitter for parsing
source code in any supported language. It follows the hybrid architecture
from ADR-009: tree-sitter for universal parsing, with language-specific
semantic enrichment added separately.

Features:
    - Language-agnostic API
    - Query execution for pattern matching
    - AST traversal utilities
    - Source span extraction
    - Error-tolerant parsing

Dependencies:
    - tree-sitter: Core parsing library
    - tree-sitter-language-pack: Pre-compiled language grammars

Example:
    adapter = TreeSitterAdapter("python")
    tree = adapter.parse("def hello(): pass")

    # Query for function definitions
    functions = adapter.query(tree, "(function_definition name: (identifier) @name)")
    for match in functions:
        print(match.captures["name"].text)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Iterator, TypeVar

if TYPE_CHECKING:
    pass


@dataclass
class SourceSpan:
    """Source location span from tree-sitter.

    Attributes:
        file: File path
        start_byte: Start byte offset
        end_byte: End byte offset
        start_point: (row, column) start position
        end_point: (row, column) end position
    """

    file: str
    start_byte: int
    end_byte: int
    start_point: tuple[int, int]
    end_point: tuple[int, int]

    @property
    def start_line(self) -> int:
        """1-indexed start line."""
        return self.start_point[0] + 1

    @property
    def start_col(self) -> int:
        """0-indexed start column."""
        return self.start_point[1]

    @property
    def end_line(self) -> int:
        """1-indexed end line."""
        return self.end_point[0] + 1

    @property
    def end_col(self) -> int:
        """0-indexed end column."""
        return self.end_point[1]


@dataclass
class TreeNode:
    """Wrapper around tree-sitter node.

    Provides a more Pythonic interface to tree-sitter nodes.

    Attributes:
        type: Node type string
        text: Node text content
        span: Source location
        is_named: Whether this is a named node
        is_error: Whether this is an error node
        children: Child nodes
        parent: Parent node (if any)
        _raw: Underlying tree-sitter node
    """

    type: str
    text: str
    span: SourceSpan
    is_named: bool
    is_error: bool
    children: list[TreeNode] = field(default_factory=list)
    parent: TreeNode | None = None
    _raw: Any = None

    def child_by_field(self, field_name: str) -> TreeNode | None:
        """Get child by field name.

        Args:
            field_name: Field name in the grammar

        Returns:
            Child node or None if not found
        """
        if self._raw is None:
            return None
        child = self._raw.child_by_field_name(field_name)
        if child is None:
            return None
        return TreeNode.from_raw(child, self.span.file, self)

    def children_by_field(self, field_name: str) -> list[TreeNode]:
        """Get all children with a field name.

        Args:
            field_name: Field name in the grammar

        Returns:
            List of matching child nodes
        """
        if self._raw is None:
            return []
        children = self._raw.children_by_field_name(field_name)
        return [TreeNode.from_raw(c, self.span.file, self) for c in children]

    def named_children(self) -> list[TreeNode]:
        """Get all named children (skipping anonymous nodes)."""
        return [c for c in self.children if c.is_named]

    def descendants(self) -> Iterator[TreeNode]:
        """Iterate over all descendants (depth-first)."""
        for child in self.children:
            yield child
            yield from child.descendants()

    def find_first(self, node_type: str) -> TreeNode | None:
        """Find first descendant of given type.

        Args:
            node_type: Node type to find

        Returns:
            First matching node or None
        """
        for node in self.descendants():
            if node.type == node_type:
                return node
        return None

    def find_all(self, node_type: str) -> list[TreeNode]:
        """Find all descendants of given type.

        Args:
            node_type: Node type to find

        Returns:
            List of matching nodes
        """
        return [n for n in self.descendants() if n.type == node_type]

    @classmethod
    def from_raw(
        cls,
        raw_node: Any,
        file_path: str,
        parent: TreeNode | None = None,
    ) -> TreeNode:
        """Create TreeNode from raw tree-sitter node.

        Args:
            raw_node: tree-sitter Node object
            file_path: Source file path
            parent: Parent TreeNode

        Returns:
            Wrapped TreeNode
        """
        span = SourceSpan(
            file=file_path,
            start_byte=raw_node.start_byte,
            end_byte=raw_node.end_byte,
            start_point=raw_node.start_point,
            end_point=raw_node.end_point,
        )

        node = cls(
            type=raw_node.type,
            text=raw_node.text.decode("utf-8") if isinstance(raw_node.text, bytes) else raw_node.text,
            span=span,
            is_named=raw_node.is_named,
            is_error=raw_node.type == "ERROR",
            parent=parent,
            _raw=raw_node,
        )

        # Build children
        node.children = [
            cls.from_raw(child, file_path, node)
            for child in raw_node.children
        ]

        return node


@dataclass
class QueryCapture:
    """A captured node from a query match.

    Attributes:
        name: Capture name from query
        node: Captured tree node
    """

    name: str
    node: TreeNode


@dataclass
class QueryMatch:
    """Result of a query match.

    Attributes:
        pattern_index: Index of matched pattern in query
        captures: Dictionary of capture name to captured node
    """

    pattern_index: int
    captures: dict[str, TreeNode] = field(default_factory=dict)

    def get(self, capture_name: str) -> TreeNode | None:
        """Get captured node by name."""
        return self.captures.get(capture_name)


class ParseTree:
    """Parsed syntax tree.

    Wrapper around tree-sitter Tree with additional utilities.

    Attributes:
        root: Root node of the tree
        source: Original source code
        file_path: Source file path
        errors: List of parse errors (ERROR nodes)
    """

    def __init__(
        self,
        root: TreeNode,
        source: str,
        file_path: str,
        raw_tree: Any = None,
    ):
        self.root = root
        self.source = source
        self.file_path = file_path
        self._raw = raw_tree
        self._errors: list[TreeNode] | None = None

    @property
    def errors(self) -> list[TreeNode]:
        """Get all error nodes in the tree."""
        if self._errors is None:
            self._errors = self.root.find_all("ERROR")
        return self._errors

    @property
    def has_errors(self) -> bool:
        """Check if tree has any parse errors."""
        return len(self.errors) > 0

    def text_for_node(self, node: TreeNode) -> str:
        """Get source text for a node.

        Args:
            node: Tree node

        Returns:
            Source text for the node's span
        """
        return self.source[node.span.start_byte:node.span.end_byte]

    def walk(self) -> Iterator[TreeNode]:
        """Walk the tree depth-first."""
        yield self.root
        yield from self.root.descendants()


class TreeSitterAdapter:
    """Generic tree-sitter wrapper for language-agnostic parsing.

    Provides a unified interface for parsing source code in any language
    supported by tree-sitter (165+ languages via tree-sitter-language-pack).

    Attributes:
        language: Language identifier (e.g., "python", "rust")

    Example:
        adapter = TreeSitterAdapter("python")
        tree = adapter.parse("def foo(): pass")

        # Access root node
        print(tree.root.type)  # "module"

        # Find all function definitions
        for func in tree.root.find_all("function_definition"):
            print(func.child_by_field("name").text)
    """

    # Supported languages with their tree-sitter names
    LANGUAGE_MAP = {
        "python": "python",
        "rust": "rust",
        "typescript": "typescript",
        "javascript": "javascript",
        "go": "go",
        "java": "java",
        "c": "c",
        "cpp": "cpp",
        "c#": "c_sharp",
        "csharp": "c_sharp",
        "ruby": "ruby",
        "scala": "scala",
        "kotlin": "kotlin",
        "swift": "swift",
        "haskell": "haskell",
        "elixir": "elixir",
        "erlang": "erlang",
    }

    def __init__(self, language: str):
        """Initialize adapter for a specific language.

        Args:
            language: Language identifier

        Raises:
            ValueError: If language is not supported
        """
        self.language = language.lower()
        self._parser = None
        self._ts_language = None
        self._query_cache: dict[str, Any] = {}

        # Validate language
        if self.language not in self.LANGUAGE_MAP:
            supported = ", ".join(sorted(self.LANGUAGE_MAP.keys()))
            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported: {supported}"
            )

    def _ensure_parser(self) -> None:
        """Lazy initialization of parser.

        Raises:
            ImportError: If tree-sitter or language pack not installed
        """
        if self._parser is not None:
            return

        try:
            import tree_sitter
            import tree_sitter_language_pack as tslp
        except ImportError as e:
            raise ImportError(
                "tree-sitter and tree-sitter-language-pack required. "
                "Install with: pip install tree-sitter tree-sitter-language-pack"
            ) from e

        # Get language from pack
        ts_name = self.LANGUAGE_MAP[self.language]
        try:
            self._ts_language = tslp.get_language(ts_name)
        except Exception:
            # Fallback for some language names
            self._ts_language = getattr(tslp, ts_name, None)
            if self._ts_language is None:
                raise ValueError(f"Failed to load tree-sitter grammar for {ts_name}")

        # Create parser
        self._parser = tree_sitter.Parser(self._ts_language)

    def parse(self, source: str, file_path: str = "<string>") -> ParseTree:
        """Parse source code into a syntax tree.

        Args:
            source: Source code as string
            file_path: File path for error reporting

        Returns:
            ParseTree with root node and utilities

        Example:
            tree = adapter.parse("def hello(): pass")
            assert tree.root.type == "module"
        """
        self._ensure_parser()

        # Parse source
        source_bytes = source.encode("utf-8")
        raw_tree = self._parser.parse(source_bytes)

        # Wrap root node
        root = TreeNode.from_raw(raw_tree.root_node, file_path)

        return ParseTree(
            root=root,
            source=source,
            file_path=file_path,
            raw_tree=raw_tree,
        )

    def parse_file(self, path: Path) -> ParseTree:
        """Parse a file.

        Args:
            path: Path to source file

        Returns:
            ParseTree for the file
        """
        source = path.read_text(encoding="utf-8")
        return self.parse(source, str(path))

    def query(self, tree: ParseTree, query_string: str) -> list[QueryMatch]:
        """Execute a tree-sitter query.

        Args:
            tree: ParseTree to query
            query_string: S-expression query pattern

        Returns:
            List of query matches

        Example:
            matches = adapter.query(tree, "(function_definition name: (identifier) @name)")
            for match in matches:
                print(match.captures["name"].text)
        """
        self._ensure_parser()

        try:
            import tree_sitter
        except ImportError:
            return []

        # Cache compiled queries
        if query_string not in self._query_cache:
            self._query_cache[query_string] = self._ts_language.query(query_string)

        query = self._query_cache[query_string]

        # Execute query
        matches = []
        for pattern_idx, captures in query.matches(tree._raw.root_node):
            match = QueryMatch(pattern_index=pattern_idx)
            for node, capture_name in captures:
                match.captures[capture_name] = TreeNode.from_raw(
                    node, tree.file_path
                )
            matches.append(match)

        return matches

    def find_nodes(
        self,
        tree: ParseTree,
        node_types: list[str],
    ) -> list[TreeNode]:
        """Find all nodes of given types.

        Args:
            tree: ParseTree to search
            node_types: List of node types to find

        Returns:
            List of matching nodes
        """
        results = []
        for node in tree.walk():
            if node.type in node_types:
                results.append(node)
        return results

    @classmethod
    def supported_languages(cls) -> list[str]:
        """Get list of supported languages."""
        return sorted(cls.LANGUAGE_MAP.keys())


# Convenience function for quick parsing
def parse(source: str, language: str, file_path: str = "<string>") -> ParseTree:
    """Quick parse function.

    Args:
        source: Source code
        language: Language identifier
        file_path: File path for error reporting

    Returns:
        ParseTree

    Example:
        tree = parse("def hello(): pass", "python")
    """
    adapter = TreeSitterAdapter(language)
    return adapter.parse(source, file_path)


# =============================================================================
# Generic AST (GAST) - Normalized tree-sitter output
# =============================================================================


@dataclass
class GASTNode:
    """Base node in the Generic AST.

    GAST normalizes tree-sitter's Concrete Syntax Trees into a
    language-agnostic structure suitable for IR generation.

    Attributes:
        kind: Node type from standard categories
        span: Source location
        children: Child nodes
        attributes: Kind-specific attributes
    """

    kind: str
    span: SourceSpan
    children: list[GASTNode] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)

    def get_attr(self, name: str, default: Any = None) -> Any:
        """Get attribute by name."""
        return self.attributes.get(name, default)

    def set_attr(self, name: str, value: Any) -> None:
        """Set attribute by name."""
        self.attributes[name] = value


@dataclass
class TypedGASTNode(GASTNode):
    """GAST node with semantic enrichment.

    Extended GAST node that includes type information from semantic
    analysis (e.g., jedi, pyright).

    Attributes:
        resolved_type: Type information from semantic analysis
        binding_ref: For identifiers, reference to binding
        definition_ref: For references, link to definition
    """

    resolved_type: Any | None = None
    binding_ref: str | None = None
    definition_ref: str | None = None


class GASTKind:
    """Standard GAST node kinds.

    Organized by category matching IR layers.
    """

    # Structural (Layer 4)
    MODULE = "module"
    IMPORT = "import"
    EXPORT = "export"
    DEFINITION = "definition"

    # Type (Layer 3)
    TYPE_DEF = "type_def"
    TYPE_PARAM = "type_param"
    TYPE_REF = "type_ref"
    TYPE_ALIAS = "type_alias"

    # Control Flow (Layer 2)
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    BLOCK = "block"
    BRANCH = "branch"
    LOOP = "loop"
    MATCH = "match"
    TRY = "try"

    # Data Flow (Layer 1)
    BINDING = "binding"
    ASSIGNMENT = "assignment"
    PARAMETER = "parameter"
    RETURN = "return"

    # Expression (Layer 0)
    CALL = "call"
    OPERATOR = "operator"
    LITERAL = "literal"
    IDENTIFIER = "identifier"
    LAMBDA = "lambda"
    MEMBER = "member"
    INDEX = "index"


# Type alias for node transformer functions
T = TypeVar("T")
NodeTransformer = Callable[[TreeNode], T | None]


class ASTNormalizer:
    """Base class for language-specific AST normalizers.

    Converts tree-sitter CST nodes to normalized GAST nodes.
    Subclasses implement language-specific normalization rules.

    Example:
        class PythonNormalizer(ASTNormalizer):
            def normalize_function(self, node: TreeNode) -> GASTNode:
                return GASTNode(
                    kind=GASTKind.FUNCTION,
                    span=node.span,
                    attributes={
                        "name": node.child_by_field("name").text,
                        "async": node.type == "async_function_definition",
                    },
                )
    """

    def __init__(self, language: str):
        self.language = language
        self._handlers: dict[str, NodeTransformer[GASTNode]] = {}

    def register_handler(
        self,
        node_type: str,
        handler: NodeTransformer[GASTNode],
    ) -> None:
        """Register a handler for a node type.

        Args:
            node_type: Tree-sitter node type
            handler: Function to convert node to GAST
        """
        self._handlers[node_type] = handler

    def normalize(self, tree: ParseTree) -> GASTNode:
        """Normalize a parse tree to GAST.

        Args:
            tree: ParseTree from tree-sitter

        Returns:
            Root GAST node
        """
        return self._normalize_node(tree.root)

    def _normalize_node(self, node: TreeNode) -> GASTNode:
        """Normalize a single node.

        Args:
            node: TreeNode to normalize

        Returns:
            Normalized GAST node
        """
        # Check for registered handler
        handler = self._handlers.get(node.type)
        if handler:
            result = handler(node)
            if result:
                return result

        # Default: create generic node
        gast = GASTNode(
            kind=node.type,
            span=node.span,
            attributes={"text": node.text},
        )

        # Recursively normalize children
        for child in node.named_children():
            gast.children.append(self._normalize_node(child))

        return gast
