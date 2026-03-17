"""Data models for the IR schema.

This module defines Pydantic v2 models matching the ir-v1.json schema.
All models are designed for:
- Serialization to/from JSON
- Validation against the schema
- Type-safe manipulation in Python

The models follow the 5-layer architecture:
- Layer 4: Module, Import, Export, Definition
- Layer 3: TypeDef, TypeRef, TypeParam, TypeRelationship
- Layer 2: Function, Effect, ControlFlowGraph, Block, Terminator
- Layer 1: Binding, Lifetime, DataFlowNode, Transformation
- Layer 0: Expression, SourceSpan (optional)

Cross-cutting: SemanticAnnotation, GapMarker, PreservationStatus
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Enums
# =============================================================================


class GapType(str, Enum):
    """Types of semantic gaps that may occur during conversion.

    Attributes:
        IMPOSSIBLE: Cannot be converted (requires redesign)
        LOSSY: Information lost during conversion
        STRUCTURAL: Structural mismatch requiring transformation
        IDIOMATIC: Style difference (cosmetic)
        RUNTIME: Runtime behavior difference
        SEMANTIC: Meaning difference (subtle)
    """

    IMPOSSIBLE = "impossible"
    LOSSY = "lossy"
    STRUCTURAL = "structural"
    IDIOMATIC = "idiomatic"
    RUNTIME = "runtime"
    SEMANTIC = "semantic"


class Severity(str, Enum):
    """Severity levels for gaps and errors.

    Attributes:
        CRITICAL: Blocks conversion entirely
        HIGH: Significant manual work required
        MEDIUM: Automated with review
        LOW: Cosmetic or minor
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PreservationLevel(int, Enum):
    """Semantic preservation levels (0-3).

    Attributes:
        SYNTACTIC: Target code compiles/parses (level 0)
        SEMANTIC: Equivalent behavior for tested inputs (level 1)
        IDIOMATIC: Follows target language conventions (level 2)
        OPTIMIZED: Performance comparable to native (level 3)
    """

    SYNTACTIC = 0
    SEMANTIC = 1
    IDIOMATIC = 2
    OPTIMIZED = 3


class Visibility(str, Enum):
    """Visibility/access levels.

    Attributes:
        PUBLIC: Accessible from anywhere
        INTERNAL: Accessible within package/crate
        PRIVATE: Accessible only within module
        PROTECTED: Accessible within class hierarchy
        PACKAGE: Accessible within same package
    """

    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"
    PROTECTED = "protected"
    PACKAGE = "package"


class Mutability(str, Enum):
    """Mutability modes for bindings and parameters.

    Attributes:
        MUTABLE: Can be reassigned
        IMMUTABLE: Cannot be reassigned
        LINEAR: Must be used exactly once
        MOVE: Ownership transferred
    """

    MUTABLE = "mutable"
    IMMUTABLE = "immutable"
    LINEAR = "linear"
    MOVE = "move"


class LifetimeKind(str, Enum):
    """Lifetime kinds for ownership tracking.

    Attributes:
        STATIC: Lives for program duration
        SCOPED: Lives for a lexical scope
        OWNED: Ownership can be transferred
        BORROWED: Temporary reference
    """

    STATIC = "static"
    SCOPED = "scoped"
    OWNED = "owned"
    BORROWED = "borrowed"


class BorrowKind(str, Enum):
    """Borrow kinds for borrowed lifetimes.

    Attributes:
        SHARED: Multiple readers, no writers (&T)
        MUTABLE: Single reader/writer (&mut T)
        MOVE: Ownership transfer
    """

    SHARED = "shared"
    MUTABLE = "mutable"
    MOVE = "move"


class Variance(str, Enum):
    """Type parameter variance.

    Attributes:
        INVARIANT: No subtyping relationship
        COVARIANT: Same direction subtyping
        CONTRAVARIANT: Opposite direction subtyping
    """

    INVARIANT = "invariant"
    COVARIANT = "covariant"
    CONTRAVARIANT = "contravariant"


class TypeKind(str, Enum):
    """Kinds of type definitions.

    Attributes:
        STRUCT: Product type with named fields
        ENUM: Sum type with variants
        CLASS: Reference type with inheritance
        INTERFACE: Abstract type with method requirements
        ALIAS: Type synonym
        OPAQUE: Hidden internal structure
        PRIMITIVE: Built-in type
    """

    STRUCT = "struct"
    ENUM = "enum"
    CLASS = "class"
    INTERFACE = "interface"
    ALIAS = "alias"
    OPAQUE = "opaque"
    PRIMITIVE = "primitive"


class TypeRefKind(str, Enum):
    """Kinds of type references.

    Attributes:
        NAMED: Reference to a concrete or generic type
        GENERIC: Unbound type parameter
        FUNCTION: Function/callable type
        TUPLE: Fixed-size heterogeneous collection
        UNION: Discriminated union (sum type)
        INTERSECTION: Types satisfying multiple interfaces
        REFERENCE: Reference/pointer type
    """

    NAMED = "named"
    GENERIC = "generic"
    FUNCTION = "function"
    TUPLE = "tuple"
    UNION = "union"
    INTERSECTION = "intersection"
    REFERENCE = "reference"


class EffectKind(str, Enum):
    """Kinds of computational effects.

    Attributes:
        PURE: No side effects
        THROWS: May raise exception
        ASYNC: Asynchronous operation
        UNSAFE: Bypasses safety guarantees
        IO: Input/output operations
        SUSPENDS: May suspend execution
        ALLOCATES: Heap allocation
        CAPTURES: Captures environment
    """

    PURE = "pure"
    THROWS = "throws"
    ASYNC = "async"
    UNSAFE = "unsafe"
    IO = "io"
    SUSPENDS = "suspends"
    ALLOCATES = "allocates"
    CAPTURES = "captures"


class TerminatorKind(str, Enum):
    """Kinds of block terminators.

    Attributes:
        RETURN: Exit function with value
        BRANCH: Conditional branch
        SWITCH: Multi-way branch
        LOOP: Loop construct
        TRY: Exception handling
        UNREACHABLE: Code that should never execute
    """

    RETURN = "return"
    BRANCH = "branch"
    SWITCH = "switch"
    LOOP = "loop"
    TRY = "try"
    UNREACHABLE = "unreachable"


class ExpressionKind(str, Enum):
    """Kinds of expressions (Layer 0).

    Attributes:
        LITERAL: Constant value
        IDENTIFIER: Variable reference
        CALL: Function invocation
        OPERATOR: Binary/unary operation
        LAMBDA: Anonymous function
        MEMBER_ACCESS: Field access
        INDEX: Array indexing
        CAST: Type conversion
        CONDITIONAL: Ternary expression
        TUPLE: Tuple construction
        ARRAY: Array literal
        OBJECT: Object literal
        AWAIT: Async await
        THROW: Throw/raise
    """

    LITERAL = "literal"
    IDENTIFIER = "identifier"
    CALL = "call"
    OPERATOR = "operator"
    LAMBDA = "lambda"
    MEMBER_ACCESS = "member_access"
    INDEX = "index"
    CAST = "cast"
    CONDITIONAL = "conditional"
    TUPLE = "tuple"
    ARRAY = "array"
    OBJECT = "object"
    AWAIT = "await"
    THROW = "throw"


class AnnotationSource(str, Enum):
    """Source of semantic annotations.

    Attributes:
        EXPLICIT: Declared in source code
        INFERRED: Determined by static analysis
        DEFAULT: Applied as language default
        TEST_SUITE: Derived from test execution
        HUMAN: Manually specified by user
    """

    EXPLICIT = "explicit"
    INFERRED = "inferred"
    DEFAULT = "default"
    TEST_SUITE = "test_suite"
    HUMAN = "human"


class AutomationLevel(str, Enum):
    """Level of automation possible for gap resolution.

    Attributes:
        NONE: Requires human decision
        PARTIAL: Can suggest, human confirms
        FULL: Fully automated
    """

    NONE = "none"
    PARTIAL = "partial"
    FULL = "full"


class ExtractionMode(str, Enum):
    """Mode of extraction.

    Attributes:
        FULL_MODULE: Complete codebase conversion
        SINGLE_FUNCTION: Function-level extraction
        TYPE_ONLY: Interface/type extraction
        SIGNATURE_ONLY: API surface extraction
    """

    FULL_MODULE = "full_module"
    SINGLE_FUNCTION = "single_function"
    TYPE_ONLY = "type_only"
    SIGNATURE_ONLY = "signature_only"


# =============================================================================
# Error Codes
# =============================================================================


class ExtractionErrorCode(str, Enum):
    """Error codes for extraction failures (E001-E005).

    Attributes:
        E001: Parse error - syntax error in source
        E002: Unsupported syntax - valid but unsupported
        E003: Type inference failed - cannot determine type
        E004: Cross-file reference - unresolved import
        E005: Metaprogramming - dynamic code generation
    """

    E001 = "E001"
    E002 = "E002"
    E003 = "E003"
    E004 = "E004"
    E005 = "E005"


class SynthesisErrorCode(str, Enum):
    """Error codes for synthesis failures (S001-S005).

    Attributes:
        S001: Invalid IR - schema validation failed
        S002: Unsupported construct - IR construct not supported
        S003: Type mapping failed - cannot map type to target
        S004: Missing dependency - required import not available
        S005: Code generation failed - synthesis error
    """

    S001 = "S001"
    S002 = "S002"
    S003 = "S003"
    S004 = "S004"
    S005 = "S005"


class ValidationErrorCode(str, Enum):
    """Error codes for validation failures (V001-V004).

    Attributes:
        V001: Schema mismatch - IR doesn't match schema
        V002: Cross-reference error - invalid reference
        V003: Consistency error - layers inconsistent
        V004: Preservation violation - preservation level not met
    """

    V001 = "V001"
    V002 = "V002"
    V003 = "V003"
    V004 = "V004"


# =============================================================================
# Base Models
# =============================================================================


class IRBaseModel(BaseModel):
    """Base model for all IR constructs."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=False,
        validate_assignment=True,
        use_enum_values=True,
    )


# =============================================================================
# Source Location (Layer 0)
# =============================================================================


class SourceSpan(IRBaseModel):
    """Source location span for precise error reporting.

    Attributes:
        file: File path (relative to project root)
        start_line: 1-indexed starting line
        start_col: 0-indexed starting column (bytes)
        end_line: 1-indexed ending line
        end_col: 0-indexed ending column (exclusive)
    """

    file: str
    start_line: Annotated[int, Field(ge=1)]
    start_col: Annotated[int, Field(ge=0)]
    end_line: Annotated[int, Field(ge=1)]
    end_col: Annotated[int, Field(ge=0)]

    def contains(self, other: SourceSpan) -> bool:
        """Check if this span fully contains another span."""
        if self.file != other.file:
            return False
        if self.start_line > other.start_line:
            return False
        if self.end_line < other.end_line:
            return False
        if self.start_line == other.start_line and self.start_col > other.start_col:
            return False
        if self.end_line == other.end_line and self.end_col < other.end_col:
            return False
        return True


# =============================================================================
# Type References (Layer 3)
# =============================================================================


class TypeRef(IRBaseModel):
    """Reference to a type.

    This is a discriminated union based on the 'kind' field.
    Different fields are populated depending on the kind.

    Attributes:
        kind: Type reference kind
        type_id: For named/generic types, the type ID
        args: Generic type arguments
        params: For function types, parameter types
        return_type: For function types, return type
        effects: For function types, associated effects
        elements: For tuple types, element types
        members: For union/intersection types, member types
        mutable: For reference types, mutability
        lifetime_name: For reference types, lifetime name
    """

    kind: TypeRefKind
    type_id: str | None = None
    args: list[TypeRef] = Field(default_factory=list)
    params: list[TypeRef] = Field(default_factory=list)
    return_type: TypeRef | None = None
    effects: list[Effect] = Field(default_factory=list)
    elements: list[TypeRef] = Field(default_factory=list)
    members: list[TypeRef] = Field(default_factory=list)
    mutable: bool = False
    lifetime_name: str | None = None


class TypeParam(IRBaseModel):
    """Generic type parameter.

    Attributes:
        name: Parameter name (e.g., "T", "Item")
        variance: Variance annotation
        bounds: Upper bounds/constraints
        default: Default type if any
    """

    name: str
    variance: Variance = Variance.INVARIANT
    bounds: list[TypeRef] = Field(default_factory=list)
    default: TypeRef | None = None


class Constraint(IRBaseModel):
    """Type constraint (where clause).

    Attributes:
        kind: Constraint kind
        param: Which type param this constrains
        bound: The bound type
        associated_type: For associated type constraints
        associated_bound: Bound for associated type
    """

    kind: Literal["type_bound", "where_clause", "associated_type"]
    param: str
    bound: TypeRef | None = None
    associated_type: str | None = None
    associated_bound: TypeRef | None = None


class Field_(IRBaseModel):
    """Field in a struct/class type.

    Note: Named Field_ to avoid conflict with pydantic.Field
    """

    name: str
    type: TypeRef
    visibility: Visibility = Visibility.PRIVATE
    mutability: Mutability = Mutability.MUTABLE
    default_value: Any | None = None


class Variant(IRBaseModel):
    """Enum variant.

    Attributes:
        name: Variant name
        kind: Variant shape
        fields: For struct variants
        types: For tuple variants
        discriminant: Explicit discriminant value
    """

    name: str
    kind: Literal["unit", "tuple", "struct"] = "unit"
    fields: list[Field_] = Field(default_factory=list)
    types: list[TypeRef] = Field(default_factory=list)
    discriminant: int | None = None


class TypeBody(IRBaseModel):
    """Type body content (varies by kind)."""

    fields: list[Field_] = Field(default_factory=list)
    methods: list[str] = Field(default_factory=list)
    variants: list[Variant] = Field(default_factory=list)
    required_methods: list[MethodSignature] = Field(default_factory=list)
    provided_methods: list[str] = Field(default_factory=list)
    aliased_type: TypeRef | None = None


class MethodSignature(IRBaseModel):
    """Method signature for interfaces/traits."""

    name: str
    params: list[Param] = Field(default_factory=list)
    return_type: TypeRef
    type_params: list[TypeParam] = Field(default_factory=list)
    effects: list[Effect] = Field(default_factory=list)


class TypeDef(IRBaseModel):
    """Type definition (Layer 3).

    Represents struct, enum, class, interface, alias, opaque, or primitive types.

    Attributes:
        id: Unique identifier (e.g., "type:MyStruct")
        name: Type name as declared
        kind: Type kind
        params: Generic type parameters
        constraints: Where clauses and bounds
        body: Type body content
        visibility: Type visibility
        span: Source location (optional)
        annotations: Semantic annotations
    """

    id: str
    name: str
    kind: TypeKind
    params: list[TypeParam] = Field(default_factory=list)
    constraints: list[Constraint] = Field(default_factory=list)
    body: TypeBody = Field(default_factory=TypeBody)
    visibility: Visibility = Visibility.PUBLIC
    span: SourceSpan | None = None
    annotations: list[SemanticAnnotation] = Field(default_factory=list)


class TypeRelationship(IRBaseModel):
    """Relationship between types.

    Attributes:
        from_type: Source type ID
        to_type: Target type ID
        kind: Relationship kind
    """

    from_type: str
    to_type: str
    kind: Literal["extends", "implements", "subtype_of", "convertible_to"]


# =============================================================================
# Effects (Layer 2)
# =============================================================================


class Effect(IRBaseModel):
    """Computational effect annotation.

    Attributes:
        kind: Effect kind
        type: Associated type for typed effects
        source: How the effect was determined
        confidence: Confidence for inferred effects
    """

    kind: EffectKind
    type: TypeRef | None = None
    source: AnnotationSource = AnnotationSource.EXPLICIT
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0


# =============================================================================
# Parameters and Functions (Layer 2)
# =============================================================================


class Param(IRBaseModel):
    """Function parameter.

    Attributes:
        name: Parameter name
        type: Parameter type
        default: Default value expression
        mutability: Parameter mutability
        variadic: Whether this is a variadic parameter
        annotations: Semantic annotations
    """

    name: str
    type: TypeRef
    default: Expression | None = None
    mutability: Mutability = Mutability.IMMUTABLE
    variadic: bool = False
    annotations: list[SemanticAnnotation] = Field(default_factory=list)


class Receiver(IRBaseModel):
    """Method receiver (self/this).

    Attributes:
        type: Receiver type
        mutability: Receiver mutability
        name: Receiver name (usually "self" or "this")
    """

    type: TypeRef
    mutability: Mutability = Mutability.IMMUTABLE
    name: str = "self"


# =============================================================================
# Control Flow (Layer 2)
# =============================================================================


class Statement(IRBaseModel):
    """Statement in a basic block.

    Attributes:
        kind: Statement kind
        target: For assign, target binding ID
        value: For assign, value expression
        callee: For call, callee expression
        arguments: For call, arguments
    """

    kind: Literal["assign", "call", "alloc", "dealloc", "noop"]
    target: str | None = None
    value: Expression | None = None
    callee: Expression | None = None
    arguments: list[Expression] = Field(default_factory=list)


class SwitchArm(IRBaseModel):
    """Arm of a switch/match terminator."""

    pattern: dict[str, Any]
    guard: Expression | None = None
    target: str


class CatchBlock(IRBaseModel):
    """Catch block in try terminator."""

    exception_type: TypeRef
    binding: str | None = None
    handler_block: str


class Terminator(IRBaseModel):
    """Block terminator.

    Attributes:
        kind: Terminator kind
        value: For return, return value
        condition: For branch, condition expression
        then_block: For branch, then target
        else_block: For branch, else target
        scrutinee: For switch, value being matched
        arms: For switch, match arms
        default_block: For switch, default target
        body: For loop, body block
        continue_target: For loop, continue target
        break_target: For loop, break target
        try_block: For try, try body
        catch_blocks: For try, catch handlers
        finally_block: For try, finally block
        reason: For unreachable, explanation
    """

    kind: TerminatorKind
    value: Expression | None = None
    condition: Expression | None = None
    then_block: str | None = None
    else_block: str | None = None
    scrutinee: Expression | None = None
    arms: list[SwitchArm] = Field(default_factory=list)
    default_block: str | None = None
    body: str | None = None
    continue_target: str | None = None
    break_target: str | None = None
    try_block: str | None = None
    catch_blocks: list[CatchBlock] = Field(default_factory=list)
    finally_block: str | None = None
    reason: str | None = None


class Block(IRBaseModel):
    """Basic block in control flow graph.

    Attributes:
        id: Block identifier
        statements: Statements in the block
        terminator: Block terminator
        loop_depth: Nesting depth in loops
        exception_handler: Handler block ID if in try
    """

    id: str
    statements: list[Statement] = Field(default_factory=list)
    terminator: Terminator
    loop_depth: int = 0
    exception_handler: str | None = None


class ControlFlowGraph(IRBaseModel):
    """Control flow graph for function bodies.

    Attributes:
        entry: Entry block ID
        blocks: All blocks in the CFG
        exit: Exit block ID (may be None for multiple exits)
    """

    entry: str
    blocks: list[Block] = Field(default_factory=list)
    exit: str | None = None


class Function(IRBaseModel):
    """Function definition (Layer 2).

    Attributes:
        id: Unique identifier
        name: Function name
        params: Parameters
        return_type: Return type
        type_params: Generic type parameters
        effects: Effect annotations
        body: Control flow graph (None for declarations)
        visibility: Access level
        receiver: Method receiver (for methods)
        span: Source location
        annotations: Semantic annotations
        doc_comment: Documentation string
    """

    id: str
    name: str
    params: list[Param] = Field(default_factory=list)
    return_type: TypeRef
    type_params: list[TypeParam] = Field(default_factory=list)
    effects: list[Effect] = Field(default_factory=list)
    body: ControlFlowGraph | None = None
    visibility: Visibility = Visibility.PUBLIC
    receiver: Receiver | None = None
    span: SourceSpan | None = None
    annotations: list[SemanticAnnotation] = Field(default_factory=list)
    doc_comment: str | None = None


# =============================================================================
# Data Flow (Layer 1)
# =============================================================================


class Lifetime(IRBaseModel):
    """Lifetime for ownership tracking.

    Attributes:
        kind: Lifetime kind
        scope: For scoped lifetimes, scope ID
        borrow_kind: For borrowed lifetimes
        name: Named lifetime (e.g., 'a)
    """

    kind: LifetimeKind
    scope: str | None = None
    borrow_kind: BorrowKind | None = None
    name: str | None = None


class Capture(IRBaseModel):
    """Closure capture.

    Attributes:
        binding_id: Original binding ID
        capture_kind: How the variable is captured
        captured_type: Type as captured (may differ from original)
    """

    binding_id: str
    capture_kind: Literal["by_value", "by_reference", "by_mut_ref", "by_move"]
    captured_type: TypeRef | None = None


class Binding(IRBaseModel):
    """Variable binding (Layer 1).

    Attributes:
        id: Unique identifier
        name: Variable name
        type: Type reference
        mutability: Binding mutability
        lifetime: Ownership/borrowing info
        value: Initial value expression
        scope: Enclosing scope ID
        captures: For closures, captured variables
        annotations: Semantic annotations
    """

    id: str
    name: str
    type: TypeRef
    mutability: Mutability = Mutability.IMMUTABLE
    lifetime: Lifetime = Field(default_factory=lambda: Lifetime(kind=LifetimeKind.SCOPED))
    value: Expression | None = None
    scope: str | None = None
    captures: list[Capture] = Field(default_factory=list)
    annotations: list[SemanticAnnotation] = Field(default_factory=list)


class DataFlowNode(IRBaseModel):
    """Node in data flow graph.

    Attributes:
        id: Node identifier
        kind: Node kind (source, transform, sink)
        expression: Associated expression
        inputs: Input node IDs
        outputs: Output node IDs
        effects: Effects at this node
    """

    id: str
    kind: Literal["source", "transform", "sink"]
    expression: Expression | None = None
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    effects: list[Effect] = Field(default_factory=list)


class Transformation(IRBaseModel):
    """Functional transformation (map, filter, fold, etc.).

    Attributes:
        kind: Transformation kind
        input_type: Input type
        output_type: Output type
        function: Transformation function
    """

    kind: Literal["map", "filter", "fold", "flat_map", "collect"]
    input_type: TypeRef
    output_type: TypeRef
    function: str | None = None  # Function reference or lambda


# =============================================================================
# Expressions (Layer 0)
# =============================================================================


class Expression(IRBaseModel):
    """Expression (Layer 0 - optional).

    This is the finest-grained representation, used for detailed AST analysis.
    Not always populated - depends on extraction configuration.

    Attributes:
        id: Expression identifier
        kind: Expression kind
        type: Resolved type
        span: Source location

        # Kind-specific fields
        literal_kind: For literals
        literal_value: For literals
        binding_ref: For identifiers
        name: For identifiers
        callee: For calls
        arguments: For calls
        operator: For operators
        operands: For operators
        params: For lambdas
        body: For lambdas
        captures: For lambdas
        object: For member access
        member: For member access
        collection: For index
        index: For index
        target_type: For cast
        condition: For conditional
        then_expr: For conditional
        else_expr: For conditional
        elements: For tuple/array
        fields: For object literals
        operand: For unary ops
    """

    id: str
    kind: ExpressionKind
    type: TypeRef | None = None
    span: SourceSpan | None = None

    # Literal
    literal_kind: str | None = None
    literal_value: Any | None = None

    # Identifier
    binding_ref: str | None = None
    name: str | None = None

    # Call
    callee: Expression | None = None
    arguments: list[Argument] = Field(default_factory=list)
    type_arguments: list[TypeRef] = Field(default_factory=list)

    # Operator
    operator: str | None = None
    operator_kind: str | None = None
    operands: list[Expression] = Field(default_factory=list)

    # Lambda
    params: list[Param] = Field(default_factory=list)
    body: Expression | ControlFlowGraph | None = None
    captures: list[Capture] = Field(default_factory=list)
    is_async: bool = False
    is_generator: bool = False

    # Member access
    object: Expression | None = None
    member: str | None = None

    # Index
    collection: Expression | None = None
    index: Expression | None = None

    # Cast
    target_type: TypeRef | None = None

    # Conditional
    condition: Expression | None = None
    then_expr: Expression | None = None
    else_expr: Expression | None = None

    # Tuple/Array
    elements: list[Expression] = Field(default_factory=list)

    # Object literal
    fields: list[ObjectField] = Field(default_factory=list)

    # Unary (await, throw)
    operand: Expression | None = None


class Argument(IRBaseModel):
    """Function argument."""

    name: str | None = None
    value: Expression
    spread: bool = False


class ObjectField(IRBaseModel):
    """Object literal field."""

    name: str
    value: Expression
    shorthand: bool = False


# =============================================================================
# Module Structure (Layer 4)
# =============================================================================


class ImportedItem(IRBaseModel):
    """Item imported from a module.

    Attributes:
        name: Original name in source module
        alias: Local alias if renamed
        kind: Type of imported item
    """

    name: str
    alias: str | None = None
    kind: Literal["type", "function", "constant", "variable", "module", "wildcard"]


class Import(IRBaseModel):
    """Import declaration.

    Attributes:
        id: Import identifier
        module_path: Path to imported module
        imported_items: Specific items or wildcard
        alias: Module alias
        is_reexport: Whether this import is re-exported
    """

    id: str
    module_path: list[str]
    imported_items: list[ImportedItem] = Field(default_factory=list)
    alias: str | None = None
    is_reexport: bool = False


class DefinitionRef(IRBaseModel):
    """Reference to a definition."""

    module_id: str
    definition_id: str


class Export(IRBaseModel):
    """Export declaration.

    Attributes:
        id: Export identifier
        item: Reference to exported definition
        alias: Public name if different
        visibility: Export visibility
        documentation: Public documentation
    """

    id: str
    item: DefinitionRef
    alias: str | None = None
    visibility: Visibility = Visibility.PUBLIC
    documentation: str | None = None


class Attribute(IRBaseModel):
    """Decorator/annotation attribute."""

    name: str
    arguments: list[Any] = Field(default_factory=list)
    target: str | None = None


class Definition(IRBaseModel):
    """Definition in a module.

    Attributes:
        id: Definition identifier
        kind: Definition kind
        ref: Reference to the actual definition
        visibility: Item visibility
        attributes: Decorators/annotations
    """

    id: str
    kind: Literal["type", "function", "constant", "variable"]
    ref: str
    visibility: Visibility = Visibility.PUBLIC
    attributes: list[Attribute] = Field(default_factory=list)


class ModuleMetadata(IRBaseModel):
    """Module extraction metadata.

    Attributes:
        source_file: Original file path
        source_language: Language identifier
        extraction_version: IR version used
        extraction_mode: How the module was extracted
        source_hash: SHA-256 of source file
        extraction_timestamp: When extraction occurred
        documentation: Module-level documentation
    """

    source_file: str
    source_language: str
    extraction_version: str = "ir-v1.0"
    extraction_mode: ExtractionMode = ExtractionMode.FULL_MODULE
    source_hash: str | None = None
    extraction_timestamp: datetime | None = None
    documentation: str | None = None


class Module(IRBaseModel):
    """Module definition (Layer 4).

    This is the top-level container for a code unit.

    Attributes:
        id: Unique identifier
        name: Module name
        path: Namespace path
        visibility: Module visibility
        imports: Dependencies
        exports: Exposed items
        definitions: Types, functions, constants
        submodules: Nested modules
        extraction_scope: Full or partial
        metadata: Extraction metadata
    """

    id: str
    name: str
    path: list[str] = Field(default_factory=list)
    visibility: Visibility = Visibility.PUBLIC
    imports: list[Import] = Field(default_factory=list)
    exports: list[Export] = Field(default_factory=list)
    definitions: list[Definition] = Field(default_factory=list)
    submodules: list[str] = Field(default_factory=list)
    extraction_scope: Literal["full", "partial"] = "full"
    metadata: ModuleMetadata


# =============================================================================
# Cross-Cutting Concerns
# =============================================================================


class SemanticAnnotation(IRBaseModel):
    """Semantic annotation for conversion metadata.

    Integrates the 54 gap patterns from Phase 3.

    Attributes:
        id: Annotation identifier
        target: ID of annotated node
        kind: Annotation kind (e.g., "inferred_type", "ownership_hint")
        value: Kind-specific payload
        confidence: For inferred annotations (0.0-1.0)
        source: How annotation was determined
        evidence: Supporting evidence
        created_at: When annotation was created
        created_by: Tool or human identifier
    """

    id: str
    target: str
    kind: str
    value: dict[str, Any] = Field(default_factory=dict)
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0
    source: AnnotationSource = AnnotationSource.INFERRED
    evidence: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    created_by: str | None = None


class GapMarker(IRBaseModel):
    """Marker for semantic gaps during conversion.

    Flags issues that may require human intervention or result in imperfect
    conversion.

    Attributes:
        id: Gap marker identifier
        location: Node where gap occurs
        gap_type: Category of gap
        gap_pattern_id: Reference to pattern (e.g., "TS-001")
        severity: Gap severity
        description: Human-readable description
        source_concept: What exists in source
        target_concept: Equivalent in target (if any)
        suggested_mitigations: Possible solutions
        decision_point_id: Link to human decision if needed
        preservation_level: Max achievable level with this gap
        automation_level: How much can be automated
        affected_layers: Which IR layers are affected
    """

    id: str
    location: str
    gap_type: GapType
    gap_pattern_id: str | None = None
    severity: Severity
    description: str
    source_concept: str
    target_concept: str | None = None
    suggested_mitigations: list[str] = Field(default_factory=list)
    decision_point_id: str | None = None
    preservation_level: PreservationLevel = PreservationLevel.SEMANTIC
    automation_level: AutomationLevel = AutomationLevel.PARTIAL
    affected_layers: list[int] = Field(default_factory=list)


class LevelEvidence(IRBaseModel):
    """Evidence for a specific preservation level."""

    achieved: bool = False
    verified_at: datetime | None = None
    verifier: str | None = None
    test_coverage: float | None = None
    passing_tests: int | None = None
    total_tests: int | None = None
    lint_warnings: int | None = None
    style_score: float | None = None
    benchmark_ratio: float | None = None
    memory_ratio: float | None = None


class PreservationStatus(IRBaseModel):
    """Preservation level tracking for an IR unit.

    Attributes:
        id: Status identifier
        unit_id: IR unit being tracked
        current_level: Currently achieved level
        max_achievable_level: Highest possible given gaps
        blocking_gaps: Gap IDs preventing higher level
        level_evidence: Evidence for each level
        progression_notes: Notes on how to improve
    """

    id: str
    unit_id: str
    current_level: PreservationLevel
    max_achievable_level: PreservationLevel
    blocking_gaps: list[str] = Field(default_factory=list)
    level_evidence: dict[int, LevelEvidence] = Field(default_factory=dict)
    progression_notes: list[str] = Field(default_factory=list)


# =============================================================================
# Complete IR Version
# =============================================================================


class IRVersion(IRBaseModel):
    """Complete IR representation for a code unit.

    This is the top-level container that holds all layers and cross-cutting
    concerns for a single extraction.

    Attributes:
        version: IR schema version
        module: Layer 4 - Module structure
        types: Layer 3 - Type definitions
        type_relationships: Layer 3 - Type relationships
        functions: Layer 2 - Function definitions
        bindings: Layer 1 - Variable bindings
        data_flow_nodes: Layer 1 - Data flow graph
        expressions: Layer 0 - Expression details (optional)
        annotations: Cross-cutting - Semantic annotations
        gaps: Cross-cutting - Gap markers
        preservation: Cross-cutting - Preservation status
    """

    version: str = "ir-v1.0"
    module: Module
    types: list[TypeDef] = Field(default_factory=list)
    type_relationships: list[TypeRelationship] = Field(default_factory=list)
    functions: list[Function] = Field(default_factory=list)
    bindings: list[Binding] = Field(default_factory=list)
    data_flow_nodes: list[DataFlowNode] = Field(default_factory=list)
    expressions: list[Expression] = Field(default_factory=list)
    annotations: list[SemanticAnnotation] = Field(default_factory=list)
    gaps: list[GapMarker] = Field(default_factory=list)
    preservation: PreservationStatus | None = None

    def content_hash(self) -> str:
        """Compute SHA-256 content hash of the IR.

        Uses canonical JSON serialization for deterministic hashing.
        See ADR-008 for hashing specification.

        Returns:
            Hex-encoded SHA-256 hash string
        """
        # Serialize to canonical JSON
        content = self.model_dump(mode="json", exclude_none=True)
        canonical = json.dumps(content, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# =============================================================================
# Errors
# =============================================================================


class ExtractionError(Exception):
    """Error during IR extraction.

    Attributes:
        code: Error code (E001-E005)
        message: Error description
        location: Source location where error occurred
        recovery: Recovery action taken
    """

    def __init__(
        self,
        code: ExtractionErrorCode,
        message: str,
        location: SourceSpan | None = None,
        recovery: str | None = None,
    ):
        self.code = code
        self.location = location
        self.recovery = recovery
        super().__init__(f"[{code.value}] {message}")


class SynthesisError(Exception):
    """Error during code synthesis.

    Attributes:
        code: Error code (S001-S005)
        message: Error description
        ir_location: IR element that caused the error
    """

    def __init__(
        self,
        code: SynthesisErrorCode,
        message: str,
        ir_location: str | None = None,
    ):
        self.code = code
        self.ir_location = ir_location
        super().__init__(f"[{code.value}] {message}")


class ValidationError(Exception):
    """Error during IR validation.

    Attributes:
        code: Error code (V001-V004)
        message: Error description
        path: JSON path to invalid element
        expected: Expected value/type
        actual: Actual value/type
    """

    def __init__(
        self,
        code: ValidationErrorCode,
        message: str,
        path: str | None = None,
        expected: str | None = None,
        actual: str | None = None,
    ):
        self.code = code
        self.path = path
        self.expected = expected
        self.actual = actual
        super().__init__(f"[{code.value}] {message}")
