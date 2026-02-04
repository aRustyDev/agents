# Binary Format Documentation

This document specifies binary formats for IR serialization in a future universal extractor CLI.

**Version:** 1.0
**Generated:** 2026-02-04
**Task:** ai-f33.8

---

**IMPORTANT: DOCUMENTATION ONLY**

This document describes binary format specifications for a **future** universal extractor CLI. The formats documented here are **not implemented** in this project. This documentation ensures:

1. JSON/YAML schemas remain compatible with future binary representations
2. Architectural guidance exists for future implementers
3. Schema design decisions account for serialization constraints

---

## 1. Overview

### 1.1 Why Binary Formats Matter

A future extractor CLI will need efficient serialization for:

| Use Case | Primary Format | Rationale |
|----------|---------------|-----------|
| Human review and debugging | JSON/YAML | Readable, editable |
| Tool interoperability | Protobuf | Typed, versioned, cross-language |
| Compact transport | MessagePack | Smaller than JSON, schema-less |
| Streaming large codebases | Protobuf | Efficient incremental parsing |

### 1.2 Format Selection Guidelines

| Condition | Recommended Format |
|-----------|-------------------|
| IR output < 1 MB | JSON (human-readable) |
| IR output 1-100 MB | Protobuf (balanced) |
| IR output > 100 MB | Protobuf with streaming |
| Embedded/constrained environment | MessagePack |
| Ad-hoc tooling without schema | MessagePack |
| Cross-language tool integration | Protobuf |
| Debug and development | JSON |

### 1.3 Performance Characteristics

| Format | Relative Size | Encode Speed | Decode Speed | Schema Required |
|--------|--------------|--------------|--------------|-----------------|
| JSON | 1.0x (baseline) | 1.0x | 1.0x | No |
| Protobuf | 0.3-0.5x | 2-5x faster | 2-5x faster | Yes |
| MessagePack | 0.5-0.7x | 1.5-2x faster | 1.5-2x faster | No |

---

## 2. Protobuf Schema Specification

The following `.proto` definitions map directly to the YAML/JSON IR schemas.

### 2.1 Common Types

```protobuf
syntax = "proto3";

package ir.v1;

option go_package = "github.com/example/ir/v1";
option java_package = "com.example.ir.v1";

// Unique identifier for any IR node
message AnyId {
  string value = 1;  // e.g., "type:HashMap", "fn:process", "bind:data"
}

// Source location span
message SourceSpan {
  string file = 1;
  uint32 start_line = 2;
  uint32 start_col = 3;
  uint32 end_line = 4;
  uint32 end_col = 5;
}

// Visibility levels
enum Visibility {
  VISIBILITY_UNSPECIFIED = 0;
  VISIBILITY_PUBLIC = 1;
  VISIBILITY_PRIVATE = 2;
  VISIBILITY_PROTECTED = 3;
  VISIBILITY_INTERNAL = 4;
  VISIBILITY_PACKAGE = 5;
}

// Mutability modes
enum Mutability {
  MUTABILITY_UNSPECIFIED = 0;
  MUTABILITY_IMMUTABLE = 1;
  MUTABILITY_MUTABLE = 2;
  MUTABILITY_MOVE = 3;
  MUTABILITY_LINEAR = 4;
}

// Variance kinds
enum Variance {
  VARIANCE_UNSPECIFIED = 0;
  VARIANCE_INVARIANT = 1;
  VARIANCE_COVARIANT = 2;
  VARIANCE_CONTRAVARIANT = 3;
}
```

### 2.2 Layer 4: Structural IR

```protobuf
// Module definition (Layer 4)
message Module {
  string id = 1;
  string name = 2;
  repeated string path = 3;  // Namespace path
  Visibility visibility = 4;
  repeated Import imports = 5;
  repeated Export exports = 6;
  repeated Definition definitions = 7;
  ExtractionScope extraction_scope = 8;
  ModuleMetadata metadata = 9;
}

enum ExtractionScope {
  EXTRACTION_SCOPE_UNSPECIFIED = 0;
  EXTRACTION_SCOPE_FULL = 1;
  EXTRACTION_SCOPE_PARTIAL = 2;
}

message ModuleMetadata {
  string source_file = 1;
  string source_language = 2;
  string extraction_version = 3;
  ExtractionMode extraction_mode = 4;
}

enum ExtractionMode {
  EXTRACTION_MODE_UNSPECIFIED = 0;
  EXTRACTION_MODE_FULL_MODULE = 1;
  EXTRACTION_MODE_SINGLE_FUNCTION = 2;
  EXTRACTION_MODE_TYPE_ONLY = 3;
  EXTRACTION_MODE_SIGNATURE_ONLY = 4;
}

message Import {
  string id = 1;
  repeated string module_path = 2;
  repeated ImportedItem imported_items = 3;
  optional string alias = 4;
}

message ImportedItem {
  string name = 1;
  optional string alias = 2;
  bool is_wildcard = 3;
}

message Export {
  string id = 1;
  AnyId item = 2;
  optional string alias = 3;
  Visibility visibility = 4;
}

message Definition {
  DefinitionKind kind = 1;
  AnyId ref = 2;  // TypeId, FunctionId, ConstantId, or VariableId
}

enum DefinitionKind {
  DEFINITION_KIND_UNSPECIFIED = 0;
  DEFINITION_KIND_TYPE = 1;
  DEFINITION_KIND_FUNCTION = 2;
  DEFINITION_KIND_CONSTANT = 3;
  DEFINITION_KIND_VARIABLE = 4;
}
```

### 2.3 Layer 3: Type IR

```protobuf
// Type definition (Layer 3)
message TypeDef {
  string id = 1;
  string name = 2;
  TypeKind kind = 3;
  repeated TypeParam params = 4;
  repeated Constraint constraints = 5;
  TypeBody body = 6;
  Visibility visibility = 7;
  optional SourceSpan source_span = 8;
  optional string doc_comment = 9;
}

enum TypeKind {
  TYPE_KIND_UNSPECIFIED = 0;
  TYPE_KIND_STRUCT = 1;
  TYPE_KIND_ENUM = 2;
  TYPE_KIND_CLASS = 3;
  TYPE_KIND_INTERFACE = 4;
  TYPE_KIND_ALIAS = 5;
  TYPE_KIND_OPAQUE = 6;
  TYPE_KIND_PRIMITIVE = 7;
}

message TypeParam {
  string name = 1;
  Variance variance = 2;
  repeated TypeRef bounds = 3;
  optional TypeRef default_type = 4;
}

message TypeBody {
  // For struct/class
  repeated Field fields = 1;
  repeated string method_refs = 2;

  // For enum
  repeated Variant variants = 3;

  // For interface/trait
  repeated MethodSignature required_methods = 4;
  repeated string provided_method_refs = 5;

  // For alias
  optional TypeRef aliased_type = 6;
}

message Field {
  string name = 1;
  TypeRef type = 2;
  Visibility visibility = 3;
  Mutability mutability = 4;
  optional Expression default_value = 5;
}

message Variant {
  string name = 1;
  VariantKind kind = 2;
  repeated Field fields = 3;       // For struct variants
  repeated TypeRef types = 4;       // For tuple variants
  optional int64 discriminant = 5;
}

enum VariantKind {
  VARIANT_KIND_UNSPECIFIED = 0;
  VARIANT_KIND_UNIT = 1;
  VARIANT_KIND_TUPLE = 2;
  VARIANT_KIND_STRUCT = 3;
}

message TypeRef {
  TypeRefKind kind = 1;

  // For named types
  optional string type_id = 2;
  repeated TypeRef args = 3;

  // For function types
  repeated TypeRef params = 4;
  optional TypeRef return_type = 5;
  repeated Effect effects = 6;

  // For tuple types
  repeated TypeRef elements = 7;

  // For union/intersection types
  repeated TypeRef members = 8;
}

enum TypeRefKind {
  TYPE_REF_KIND_UNSPECIFIED = 0;
  TYPE_REF_KIND_NAMED = 1;
  TYPE_REF_KIND_GENERIC = 2;
  TYPE_REF_KIND_FUNCTION = 3;
  TYPE_REF_KIND_TUPLE = 4;
  TYPE_REF_KIND_UNION = 5;
  TYPE_REF_KIND_INTERSECTION = 6;
}

message TypeRelationship {
  string from_type = 1;
  string to_type = 2;
  RelationshipKind kind = 3;
}

enum RelationshipKind {
  RELATIONSHIP_KIND_UNSPECIFIED = 0;
  RELATIONSHIP_KIND_EXTENDS = 1;
  RELATIONSHIP_KIND_IMPLEMENTS = 2;
  RELATIONSHIP_KIND_SUBTYPE_OF = 3;
  RELATIONSHIP_KIND_CONVERTIBLE_TO = 4;
}

message Constraint {
  ConstraintKind kind = 1;
  string param = 2;
  optional TypeRef bound = 3;
  optional string associated_type = 4;
  optional TypeRef associated_bound = 5;
}

enum ConstraintKind {
  CONSTRAINT_KIND_UNSPECIFIED = 0;
  CONSTRAINT_KIND_TYPE_BOUND = 1;
  CONSTRAINT_KIND_WHERE_CLAUSE = 2;
  CONSTRAINT_KIND_ASSOCIATED_TYPE = 3;
}
```

### 2.4 Layer 2: Control Flow IR

```protobuf
// Function definition (Layer 2)
message Function {
  string id = 1;
  string name = 2;
  repeated Param params = 3;
  TypeRef return_type = 4;
  repeated TypeParam type_params = 5;
  repeated Effect effects = 6;
  optional ControlFlowGraph body = 7;
  Visibility visibility = 8;
  optional Receiver receiver = 9;
  optional SourceSpan source_span = 10;
  optional string doc_comment = 11;
  repeated SemanticAnnotation annotations = 12;
}

message Param {
  string name = 1;
  TypeRef type = 2;
  optional Expression default_value = 3;
  Mutability mutability = 4;
  bool variadic = 5;
}

message Receiver {
  TypeRef type = 1;
  Mutability mutability = 2;
  optional string name = 3;
}

message Effect {
  EffectKind kind = 1;
  optional TypeRef type = 2;
  AnnotationSource source = 3;
  optional float confidence = 4;
}

enum EffectKind {
  EFFECT_KIND_UNSPECIFIED = 0;
  EFFECT_KIND_PURE = 1;
  EFFECT_KIND_THROWS = 2;
  EFFECT_KIND_ASYNC = 3;
  EFFECT_KIND_UNSAFE = 4;
  EFFECT_KIND_IO = 5;
  EFFECT_KIND_SUSPENDS = 6;
  EFFECT_KIND_ALLOCATES = 7;
  EFFECT_KIND_CAPTURES = 8;
}

message ControlFlowGraph {
  string entry = 1;
  repeated Block blocks = 2;
  optional string exit = 3;
}

message Block {
  string id = 1;
  repeated Statement statements = 2;
  Terminator terminator = 3;
  optional uint32 loop_depth = 4;
  optional string exception_handler = 5;
}

message Statement {
  StatementKind kind = 1;

  // For assign
  optional string target = 2;
  optional Expression value = 3;

  // For call
  optional Expression callee = 4;
  repeated Expression arguments = 5;
}

enum StatementKind {
  STATEMENT_KIND_UNSPECIFIED = 0;
  STATEMENT_KIND_ASSIGN = 1;
  STATEMENT_KIND_CALL = 2;
  STATEMENT_KIND_ALLOC = 3;
  STATEMENT_KIND_DEALLOC = 4;
  STATEMENT_KIND_NOOP = 5;
}

message Terminator {
  TerminatorKind kind = 1;

  // For return
  optional Expression return_value = 2;

  // For branch
  optional Expression condition = 3;
  optional string then_block = 4;
  optional string else_block = 5;

  // For switch
  optional Expression scrutinee = 6;
  repeated SwitchArm arms = 7;
  optional string default_block = 8;

  // For loop
  optional string body_block = 9;
  optional string continue_target = 10;
  optional string break_target = 11;

  // For try
  optional string try_block = 12;
  repeated CatchBlock catch_blocks = 13;
  optional string finally_block = 14;

  // For unreachable
  optional string reason = 15;
}

enum TerminatorKind {
  TERMINATOR_KIND_UNSPECIFIED = 0;
  TERMINATOR_KIND_RETURN = 1;
  TERMINATOR_KIND_BRANCH = 2;
  TERMINATOR_KIND_SWITCH = 3;
  TERMINATOR_KIND_LOOP = 4;
  TERMINATOR_KIND_TRY = 5;
  TERMINATOR_KIND_UNREACHABLE = 6;
}

message SwitchArm {
  Pattern pattern = 1;
  optional Expression guard = 2;
  string target = 3;
}

message CatchBlock {
  TypeRef exception_type = 1;
  optional string binding = 2;
  string handler_block = 3;
}

message Pattern {
  PatternKind kind = 1;
  optional string variant_name = 2;
  optional string type_name = 3;
  repeated string bindings = 4;
  optional Expression literal_value = 5;
}

enum PatternKind {
  PATTERN_KIND_UNSPECIFIED = 0;
  PATTERN_KIND_WILDCARD = 1;
  PATTERN_KIND_LITERAL = 2;
  PATTERN_KIND_VARIANT = 3;
  PATTERN_KIND_CONSTRUCTOR = 4;
  PATTERN_KIND_BINDING = 5;
}

message MethodSignature {
  string name = 1;
  repeated Param params = 2;
  TypeRef return_type = 3;
  repeated TypeParam type_params = 4;
  repeated Effect effects = 5;
}
```

### 2.5 Layer 1: Data Flow IR

```protobuf
// Variable binding (Layer 1)
message Binding {
  string id = 1;
  string name = 2;
  TypeRef type = 3;
  Mutability mutability = 4;
  Lifetime lifetime = 5;
  optional Expression value = 6;
  string scope = 7;
}

message Lifetime {
  LifetimeKind kind = 1;
  optional string scope = 2;
  BorrowKind borrow_kind = 3;
}

enum LifetimeKind {
  LIFETIME_KIND_UNSPECIFIED = 0;
  LIFETIME_KIND_STATIC = 1;
  LIFETIME_KIND_SCOPED = 2;
  LIFETIME_KIND_OWNED = 3;
  LIFETIME_KIND_BORROWED = 4;
}

enum BorrowKind {
  BORROW_KIND_UNSPECIFIED = 0;
  BORROW_KIND_SHARED = 1;
  BORROW_KIND_MUTABLE = 2;
  BORROW_KIND_MOVE = 3;
}

message DataFlowNode {
  string id = 1;
  DataFlowNodeKind kind = 2;
  Expression expression = 3;
  repeated string inputs = 4;
  repeated string outputs = 5;
  repeated Effect effects = 6;
}

enum DataFlowNodeKind {
  DATA_FLOW_NODE_KIND_UNSPECIFIED = 0;
  DATA_FLOW_NODE_KIND_SOURCE = 1;
  DATA_FLOW_NODE_KIND_TRANSFORM = 2;
  DATA_FLOW_NODE_KIND_SINK = 3;
}

message Transformation {
  TransformationKind kind = 1;
  TypeRef input_type = 2;
  TypeRef output_type = 3;
  oneof function {
    string function_ref = 4;
    Lambda lambda = 5;
  }
}

enum TransformationKind {
  TRANSFORMATION_KIND_UNSPECIFIED = 0;
  TRANSFORMATION_KIND_MAP = 1;
  TRANSFORMATION_KIND_FILTER = 2;
  TRANSFORMATION_KIND_FOLD = 3;
  TRANSFORMATION_KIND_FLAT_MAP = 4;
  TRANSFORMATION_KIND_COLLECT = 5;
}

message Lambda {
  repeated Param params = 1;
  oneof body {
    Expression expression = 2;
    ControlFlowGraph cfg = 3;
  }
  repeated Capture captures = 4;
}

message Capture {
  string binding_id = 1;
  Mutability mutability = 2;
}
```

### 2.6 Layer 0: Expression IR

```protobuf
// Expression (Layer 0)
message Expression {
  ExpressionKind kind = 1;
  optional TypeRef type = 2;
  optional SourceSpan span = 3;

  // For literal
  optional LiteralKind literal_kind = 4;
  optional bytes literal_value = 5;  // Serialized literal

  // For identifier
  optional string binding_ref = 6;

  // For call
  optional Expression callee = 7;
  repeated Argument arguments = 8;

  // For operator
  optional string operator = 9;
  repeated Expression operands = 10;

  // For field access
  optional Expression object = 11;
  optional string field = 12;

  // For lambda (references Layer 1)
  optional Lambda lambda = 13;
}

enum ExpressionKind {
  EXPRESSION_KIND_UNSPECIFIED = 0;
  EXPRESSION_KIND_LITERAL = 1;
  EXPRESSION_KIND_IDENTIFIER = 2;
  EXPRESSION_KIND_CALL = 3;
  EXPRESSION_KIND_OPERATOR = 4;
  EXPRESSION_KIND_FIELD_ACCESS = 5;
  EXPRESSION_KIND_LAMBDA = 6;
  EXPRESSION_KIND_CONSTRUCT = 7;
  EXPRESSION_KIND_AWAIT = 8;
  EXPRESSION_KIND_THROW = 9;
  EXPRESSION_KIND_BORROW = 10;
}

enum LiteralKind {
  LITERAL_KIND_UNSPECIFIED = 0;
  LITERAL_KIND_INT = 1;
  LITERAL_KIND_FLOAT = 2;
  LITERAL_KIND_STRING = 3;
  LITERAL_KIND_BOOL = 4;
  LITERAL_KIND_NULL = 5;
  LITERAL_KIND_CHAR = 6;
  LITERAL_KIND_BYTES = 7;
}

message Argument {
  optional string name = 1;  // For named arguments
  Expression value = 2;
}
```

### 2.7 Cross-Cutting Concerns

```protobuf
// Semantic annotation
message SemanticAnnotation {
  string id = 1;
  AnyId target = 2;
  string kind = 3;  // e.g., "inferred_type", "ownership_hint"
  bytes value = 4;  // JSON-encoded annotation value
  float confidence = 5;
  AnnotationSource source = 6;
  repeated string evidence = 7;
  int64 created_at = 8;  // Unix timestamp
  string created_by = 9;
}

enum AnnotationSource {
  ANNOTATION_SOURCE_UNSPECIFIED = 0;
  ANNOTATION_SOURCE_EXPLICIT = 1;
  ANNOTATION_SOURCE_INFERRED = 2;
  ANNOTATION_SOURCE_DEFAULT = 3;
  ANNOTATION_SOURCE_TEST_SUITE = 4;
  ANNOTATION_SOURCE_HUMAN = 5;
}

// Gap marker
message GapMarker {
  string id = 1;
  AnyId location = 2;
  GapType gap_type = 3;
  optional string gap_pattern_id = 4;  // e.g., "TS-001"
  Severity severity = 5;
  string description = 6;
  string source_concept = 7;
  optional string target_concept = 8;
  repeated string suggested_mitigations = 9;
  optional string decision_point_id = 10;
  uint32 preservation_level = 11;  // 0-3
  AutomationLevel automation_level = 12;
  repeated uint32 affected_layers = 13;
}

enum GapType {
  GAP_TYPE_UNSPECIFIED = 0;
  GAP_TYPE_IMPOSSIBLE = 1;
  GAP_TYPE_LOSSY = 2;
  GAP_TYPE_STRUCTURAL = 3;
  GAP_TYPE_IDIOMATIC = 4;
  GAP_TYPE_RUNTIME = 5;
  GAP_TYPE_SEMANTIC = 6;
}

enum Severity {
  SEVERITY_UNSPECIFIED = 0;
  SEVERITY_CRITICAL = 1;
  SEVERITY_HIGH = 2;
  SEVERITY_MEDIUM = 3;
  SEVERITY_LOW = 4;
}

enum AutomationLevel {
  AUTOMATION_LEVEL_UNSPECIFIED = 0;
  AUTOMATION_LEVEL_NONE = 1;
  AUTOMATION_LEVEL_PARTIAL = 2;
  AUTOMATION_LEVEL_FULL = 3;
}

// Preservation status
message PreservationStatus {
  string id = 1;
  AnyId unit_id = 2;
  uint32 current_level = 3;       // 0-3
  uint32 max_achievable_level = 4; // 0-3
  repeated string blocking_gaps = 5;
  LevelEvidence level_evidence = 6;
  repeated string progression_notes = 7;
}

message LevelEvidence {
  bool level_0_achieved = 1;
  optional int64 level_0_verified_at = 2;
  optional string level_0_verifier = 3;

  bool level_1_achieved = 4;
  optional float test_coverage = 5;
  optional uint32 passing_tests = 6;
  optional uint32 total_tests = 7;

  bool level_2_achieved = 8;
  optional uint32 lint_warnings = 9;
  optional float style_score = 10;

  bool level_3_achieved = 11;
  optional float benchmark_ratio = 12;
  optional float memory_ratio = 13;
}

// Asymmetry metadata
message AsymmetryInfo {
  string id = 1;
  optional AnyId unit_id = 2;
  string source_family = 3;
  string target_family = 4;
  uint32 direction_difficulty = 5;  // 1-5
  uint32 reverse_difficulty = 6;     // 1-5
  float asymmetry_ratio = 7;
  bool preserved_in_reverse = 8;
  repeated AsymmetryDetail key_asymmetries = 9;
  optional string notes = 10;
}

message AsymmetryDetail {
  string concept = 1;
  string forward_action = 2;
  string reverse_action = 3;
  InformationFlow information_flow = 4;
}

enum InformationFlow {
  INFORMATION_FLOW_UNSPECIFIED = 0;
  INFORMATION_FLOW_GAINS = 1;
  INFORMATION_FLOW_LOSES = 2;
  INFORMATION_FLOW_PRESERVES = 3;
}
```

### 2.8 Top-Level IR Container

```protobuf
// Complete IR document
message IRDocument {
  string version = 1;  // e.g., "ir-v1.0"
  int64 extracted_at = 2;
  string content_hash = 3;  // SHA-256

  repeated Module modules = 4;
  repeated TypeDef types = 5;
  repeated TypeRelationship type_relationships = 6;
  repeated Function functions = 7;
  repeated Binding bindings = 8;

  repeated SemanticAnnotation annotations = 9;
  repeated GapMarker gap_markers = 10;
  repeated PreservationStatus preservation_statuses = 11;
  repeated AsymmetryInfo asymmetry_infos = 12;
}
```

---

## 3. Usage Guidelines

### 3.1 When to Use Protobuf vs JSON

**Use JSON when:**
- Output is for human review
- Debugging extraction issues
- Small codebases (< 1 MB IR output)
- Ad-hoc scripting and tooling
- Integration with tools lacking Protobuf support

**Use Protobuf when:**
- Processing large codebases
- Cross-language tool integration
- Performance-critical pipelines
- Streaming or incremental processing
- Long-term storage with version compatibility

### 3.2 File Size Thresholds

| IR Output Size | Recommended Format | Rationale |
|---------------|-------------------|-----------|
| < 100 KB | JSON | Negligible overhead |
| 100 KB - 1 MB | JSON or Protobuf | User preference |
| 1 MB - 10 MB | Protobuf | 3-5x size reduction |
| 10 MB - 100 MB | Protobuf + compression | Essential for efficiency |
| > 100 MB | Protobuf + streaming | Memory efficiency |

### 3.3 Streaming Scenarios

For very large codebases, Protobuf supports streaming via:

1. **Delimited messages**: Length-prefixed message sequences
2. **File-per-module**: One `.pb` file per module
3. **Incremental processing**: Process modules without loading entire IR

```protobuf
// Streaming wrapper
message IRChunk {
  uint32 sequence = 1;
  bool is_last = 2;
  oneof content {
    Module module = 3;
    TypeDef type = 4;
    Function function = 5;
  }
}
```

---

## 4. MessagePack Considerations

### 4.1 When MessagePack is Preferred

MessagePack is useful when:

- **Protobuf overhead is excessive**: Very small messages where schema metadata dominates
- **Embedded environments**: Limited code generation support
- **Schema-less flexibility**: Rapid prototyping without schema updates
- **JSON compatibility**: Need to convert to/from JSON easily

### 4.2 MessagePack Trade-offs

| Aspect | Protobuf | MessagePack |
|--------|----------|-------------|
| Size | Smallest | Slightly larger |
| Schema | Required | Optional |
| Validation | Built-in | Manual |
| Cross-language | Excellent | Excellent |
| Streaming | Native | Manual |
| Evolution | Field numbers | Key names |

### 4.3 MessagePack Schema Mapping

MessagePack uses the same structure as JSON but with binary encoding:

```python
# Example MessagePack serialization (Python)
import msgpack

ir_unit = {
    "id": "type:Point",
    "name": "Point",
    "kind": "struct",
    "params": [],
    "body": {
        "fields": [
            {"name": "x", "type": {"kind": "named", "type_id": "type:f64"}},
            {"name": "y", "type": {"kind": "named", "type_id": "type:f64"}}
        ]
    }
}

# Serialize
packed = msgpack.packb(ir_unit)

# Deserialize
unpacked = msgpack.unpackb(packed)
```

---

## 5. Cross-Language Compatibility

### 5.1 Generated Code Patterns

**Python:**
```python
# Using protobuf generated code
from ir.v1 import ir_pb2

type_def = ir_pb2.TypeDef()
type_def.id = "type:Point"
type_def.name = "Point"
type_def.kind = ir_pb2.TYPE_KIND_STRUCT

# Serialize
data = type_def.SerializeToString()

# Deserialize
loaded = ir_pb2.TypeDef()
loaded.ParseFromString(data)
```

**Rust:**
```rust
// Using prost
use ir::v1::{TypeDef, TypeKind};

let type_def = TypeDef {
    id: "type:Point".to_string(),
    name: "Point".to_string(),
    kind: TypeKind::Struct as i32,
    ..Default::default()
};

// Serialize
let bytes = type_def.encode_to_vec();

// Deserialize
let loaded = TypeDef::decode(&bytes[..]).unwrap();
```

**Go:**
```go
// Using protoc-gen-go
import pb "example.com/ir/v1"

typeDef := &pb.TypeDef{
    Id:   "type:Point",
    Name: "Point",
    Kind: pb.TypeKind_TYPE_KIND_STRUCT,
}

// Serialize
data, _ := proto.Marshal(typeDef)

// Deserialize
loaded := &pb.TypeDef{}
proto.Unmarshal(data, loaded)
```

**TypeScript:**
```typescript
// Using protobuf.js
import { TypeDef, TypeKind } from './ir/v1/ir_pb';

const typeDef = new TypeDef();
typeDef.setId('type:Point');
typeDef.setName('Point');
typeDef.setKind(TypeKind.TYPE_KIND_STRUCT);

// Serialize
const bytes = typeDef.serializeBinary();

// Deserialize
const loaded = TypeDef.deserializeBinary(bytes);
```

### 5.2 Common Pitfalls

| Pitfall | Description | Mitigation |
|---------|-------------|------------|
| Default values | Protobuf3 omits default values | Use explicit presence (`optional`) for meaningful defaults |
| Enum zero values | Zero value must be UNSPECIFIED | Never rely on enum zero for meaningful state |
| Repeated fields | Empty list vs missing | Always check `len()` not truthiness |
| Oneof fields | Only one can be set | Check `HasField()` before accessing |
| String encoding | Always UTF-8 | Validate inputs, use bytes for binary |

### 5.3 Platform-Specific Notes

**Python:**
- Use `protobuf>=4.0` for better performance
- Consider `betterproto` for more Pythonic API

**Rust:**
- `prost` is recommended over `protobuf` crate
- Use `bytes` crate for zero-copy deserialization

**Go:**
- Use `protoc-gen-go` v1.28+ for better generated code
- Consider `vtprotobuf` for high-performance scenarios

**TypeScript:**
- `protobuf.js` for Node.js
- `google-protobuf` for browser compatibility
- Consider `ts-proto` for TypeScript-first experience

---

## 6. Schema Evolution Rules

### 6.1 Backward Compatibility

To maintain backward compatibility when evolving the schema:

**Safe changes (backward compatible):**
- Add new optional fields
- Add new enum values (not at position 0)
- Add new message types
- Add new oneof options
- Rename fields (field numbers preserved)

**Breaking changes (avoid):**
- Remove or renumber existing fields
- Change field types
- Change enum value numbers
- Remove enum values
- Change oneof to regular field

### 6.2 Reserved Field Numbers

Reserve field numbers for deprecated fields to prevent reuse:

```protobuf
message TypeDef {
  reserved 100, 101, 102;  // Deprecated: old_field_1, old_field_2
  reserved "old_field_name";

  string id = 1;
  // ... current fields
}
```

### 6.3 Deprecation Strategy

1. **Mark deprecated**: Add comment, keep field
2. **Stop writing**: New code ignores field
3. **Reserve number**: After migration period, reserve the field number
4. **Remove from schema**: Only in major version bump

```protobuf
message Module {
  string id = 1;
  string name = 2;

  // DEPRECATED: Use extraction_scope instead (v1.1)
  bool is_partial = 3 [deprecated = true];

  ExtractionScope extraction_scope = 8;
}
```

### 6.4 Version Negotiation

Include version information in all serialized data:

```protobuf
message IRDocument {
  string schema_version = 1;  // "ir-v1.0", "ir-v1.1", etc.
  // ... rest of document
}
```

Readers should:
1. Parse `schema_version` first
2. Handle unknown fields gracefully
3. Warn on unknown enum values
4. Fail on incompatible major versions

---

## 7. JSON to Protobuf Mapping

### 7.1 Field Mapping Rules

| JSON/YAML | Protobuf | Notes |
|-----------|----------|-------|
| `string` | `string` | Direct mapping |
| `number` (int) | `int32`, `int64` | Choose based on range |
| `number` (float) | `float`, `double` | `double` preferred |
| `boolean` | `bool` | Direct mapping |
| `null` | absent field | Use `optional` in proto3 |
| `array` | `repeated` | Preserves order |
| `object` | `message` | Nested definition |

### 7.2 Handling Optional Fields

JSON optional fields map to `optional` in proto3:

```yaml
# YAML/JSON
binding:
  name: "data"
  type: { kind: named, type_id: "type:String" }
  default: null  # Optional, may be absent
```

```protobuf
message Binding {
  string name = 1;
  TypeRef type = 2;
  optional Expression default_value = 3;  // Present only when set
}
```

### 7.3 Enum Mappings

JSON enum strings map to Protobuf enum values:

```yaml
# YAML/JSON
visibility: "public"
```

```protobuf
enum Visibility {
  VISIBILITY_UNSPECIFIED = 0;
  VISIBILITY_PUBLIC = 1;  // Maps to "public"
  VISIBILITY_PRIVATE = 2; // Maps to "private"
  // ...
}
```

Conversion functions:

```python
def visibility_to_proto(json_value: str) -> int:
    mapping = {
        "public": 1,
        "private": 2,
        "protected": 3,
        "internal": 4,
        "package": 5,
    }
    return mapping.get(json_value, 0)  # 0 = UNSPECIFIED

def visibility_from_proto(proto_value: int) -> str:
    mapping = {
        1: "public",
        2: "private",
        3: "protected",
        4: "internal",
        5: "package",
    }
    return mapping.get(proto_value, "unspecified")
```

### 7.4 Nested Message Patterns

Deeply nested JSON maps to nested messages:

```yaml
# YAML/JSON
function:
  return_type:
    kind: named
    type_id: "type:Result"
    args:
      - kind: named
        type_id: "type:User"
      - kind: named
        type_id: "type:Error"
```

```protobuf
// Maps to nested TypeRef messages
message Function {
  TypeRef return_type = 4;
}

message TypeRef {
  TypeRefKind kind = 1;
  string type_id = 2;
  repeated TypeRef args = 3;
}
```

---

## 8. Summary

### 8.1 Format Selection Matrix

| Criterion | JSON | Protobuf | MessagePack |
|-----------|------|----------|-------------|
| Human readable | Yes | No | No |
| Size efficiency | Low | High | Medium |
| Parse speed | Medium | High | High |
| Schema required | No | Yes | No |
| Cross-language | Yes | Yes | Yes |
| Streaming | No | Yes | Manual |
| Schema evolution | Flexible | Strict | Flexible |

### 8.2 Recommended Defaults

For the future extractor CLI:

1. **Primary output**: JSON for development, Protobuf for production
2. **Streaming**: Protobuf with delimited messages
3. **Embedded use**: MessagePack
4. **Long-term storage**: Protobuf with version headers

### 8.3 Implementation Priority

When implementing the extractor CLI:

1. JSON first (enables rapid iteration)
2. Protobuf second (production optimization)
3. MessagePack optional (specific use cases only)

---

## 9. Cross-References

| Document | Relationship |
|----------|--------------|
| `overview.md` | IR architecture context |
| `layer-{0-4}.md` | YAML schema definitions |
| `cross-cutting.md` | Annotation and gap marker schemas |
| `../analysis/gap-patterns.md` | Gap pattern IDs referenced in markers |

---

*Generated for Phase 4: IR Schema Design (ai-f33.8)*
*DOCUMENTATION ONLY - Binary formats not implemented in this project*
