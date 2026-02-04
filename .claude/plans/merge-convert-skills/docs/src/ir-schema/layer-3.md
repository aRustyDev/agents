# Layer 3: Type IR

**Version:** 1.0
**Generated:** 2026-02-04
**Task:** ai-f33.3

---

## 1. Overview

Layer 3 represents the type system of extracted code. It captures type definitions, generic parameters, type relationships (inheritance, implementation, subtyping), and type references used throughout the IR.

### 1.1 Role in the IR Architecture

```
Layer 4: Structural IR (modules, imports, exports)
         |
         v  contains definitions of
Layer 3: Type IR  <-- THIS LAYER
         |
         v  types referenced by
Layer 2: Control Flow IR (function signatures, return types)
         |
         v  types annotate
Layer 1: Data Flow IR (binding types, transformation types)
         |
         v  types of
Layer 0: Expression IR (expression types, literal types)
```

### 1.2 What Layer 3 Captures

| Construct | Description | Example |
|-----------|-------------|---------|
| Type definitions | ADTs, classes, interfaces, traits, aliases | `struct Point`, `interface Comparable` |
| Generic parameters | Type variables with bounds and variance | `<T: Clone>`, `<out T>` |
| Type constraints | Where clauses, bounds, requirements | `where T: Eq + Hash` |
| Type relationships | Inheritance, implementation, subtyping | `Dog extends Animal` |
| Type references | How types are used in signatures | `Vec<String>`, `Option<T>` |

### 1.3 What Layer 3 Does NOT Capture

- Function bodies (Layer 2)
- Variable bindings and lifetimes (Layer 1)
- Expression-level type information (Layer 0)
- Module organization (Layer 4)

---

## 2. Schema Elements

### 2.1 Type Definition (`type_def`)

The primary construct for defining types.

```yaml
type_def:
  id: TypeId                    # Unique identifier (e.g., "type:MyStruct")
  name: string                  # Type name as declared
  kind: TypeKind                # struct | enum | class | interface | alias | opaque | primitive
  params: TypeParam[]           # Generic type parameters
  constraints: Constraint[]     # Where clauses and bounds
  body: TypeBody                # Kind-specific body content
  visibility: Visibility        # public | internal | private | package
```

### 2.2 Type Parameter (`type_param`)

Represents generic/parametric type variables.

```yaml
type_param:
  name: string                  # Parameter name (e.g., "T", "Item")
  variance: Variance            # invariant | covariant | contravariant
  bounds: TypeRef[]             # Upper bounds / constraints
  default: TypeRef?             # Default type if any
```

### 2.3 Type Body (`type_body`)

Content varies by type kind. Only relevant fields are populated.

```yaml
type_body:
  # For struct/class
  fields: Field[]               # Data members
  methods: MethodRef[]          # Associated methods

  # For enum
  variants: Variant[]           # Enum variants (may have associated data)

  # For interface/trait
  required_methods: MethodSignature[]   # Methods implementors must provide
  provided_methods: MethodRef[]         # Default method implementations

  # For alias
  aliased_type: TypeRef         # The type being aliased
```

### 2.4 Type Reference (`type_ref`)

How types are referenced throughout the IR.

```yaml
type_ref:
  kind: TypeRefKind             # named | generic | function | tuple | union | intersection

  # For named types (concrete or generic instantiation)
  type_id: TypeId               # Reference to type definition
  args: TypeRef[]               # Generic arguments (e.g., String in Vec<String>)

  # For function types
  params: TypeRef[]             # Parameter types
  return_type: TypeRef          # Return type
  effects: Effect[]             # Associated effects (throws, async, etc.)

  # For tuple types
  elements: TypeRef[]           # Element types in order

  # For union/intersection types
  members: TypeRef[]            # Constituent types
```

### 2.5 Type Relationship (`type_relationship`)

Captures relationships between types.

```yaml
type_relationship:
  from_type: TypeId             # Source type
  to_type: TypeId               # Target type
  kind: RelationshipKind        # extends | implements | subtype_of | convertible_to
```

### 2.6 Supporting Types

```yaml
field:
  name: string
  type: TypeRef
  visibility: Visibility
  mutability: mutable | immutable | readonly
  default_value: Expression?    # Optional default (references Layer 0)

variant:
  name: string
  kind: unit | tuple | struct   # Variant shape
  fields: Field[]               # For struct variants
  types: TypeRef[]              # For tuple variants
  discriminant: int?            # Explicit discriminant value

method_signature:
  name: string
  params: Param[]
  return_type: TypeRef
  type_params: TypeParam[]
  effects: Effect[]

constraint:
  kind: type_bound | where_clause | associated_type
  param: string                 # Which type param this constrains
  bound: TypeRef?               # The bound type
  associated_type: string?      # For associated type constraints
  associated_bound: TypeRef?

visibility:
  kind: public | internal | private | package
  scope: ModuleId?              # For package-scoped visibility
```

---

## 3. Type Kinds

### 3.1 `struct`

Product types with named fields. No inheritance.

**Applicable languages:** Rust, Go, C, Swift, Kotlin (`data class`)

**Body fields used:** `fields`, `methods`

```yaml
# Rust struct
type_def:
  id: "type:Point"
  name: "Point"
  kind: struct
  params: []
  body:
    fields:
      - { name: "x", type: { kind: named, type_id: "type:f64" }, visibility: public }
      - { name: "y", type: { kind: named, type_id: "type:f64" }, visibility: public }
    methods: ["fn:Point::new", "fn:Point::distance"]
```

### 3.2 `enum`

Sum types with variants. May have associated data (ADTs).

**Applicable languages:** Rust, Swift, Haskell, TypeScript, Java (sealed)

**Body fields used:** `variants`

```yaml
# Rust enum (ADT)
type_def:
  id: "type:Option"
  name: "Option"
  kind: enum
  params:
    - { name: "T", variance: covariant, bounds: [] }
  body:
    variants:
      - { name: "Some", kind: tuple, types: [{ kind: named, type_id: "type:T" }] }
      - { name: "None", kind: unit }
```

### 3.3 `class`

Reference types with inheritance and methods.

**Applicable languages:** Java, C#, Python, TypeScript, Kotlin

**Body fields used:** `fields`, `methods`

```yaml
# Java class
type_def:
  id: "type:ArrayList"
  name: "ArrayList"
  kind: class
  params:
    - { name: "E", variance: invariant, bounds: [] }
  body:
    fields:
      - { name: "elementData", type: { kind: named, type_id: "type:Object[]" }, visibility: private }
      - { name: "size", type: { kind: named, type_id: "type:int" }, visibility: private }
    methods: ["fn:ArrayList::add", "fn:ArrayList::get", "fn:ArrayList::size"]
```

### 3.4 `interface`

Abstract types defining method requirements.

**Applicable languages:** Java, C#, TypeScript, Go, Kotlin

**Body fields used:** `required_methods`, `provided_methods`

```yaml
# TypeScript interface
type_def:
  id: "type:Comparable"
  name: "Comparable"
  kind: interface
  params:
    - { name: "T", variance: contravariant, bounds: [] }
  body:
    required_methods:
      - name: "compareTo"
        params: [{ name: "other", type: { kind: named, type_id: "type:T" } }]
        return_type: { kind: named, type_id: "type:number" }
        effects: []
    provided_methods: []
```

### 3.5 `alias`

Type synonyms and newtype wrappers.

**Applicable languages:** TypeScript, Haskell, Rust, Swift, Go

**Body fields used:** `aliased_type`

```yaml
# TypeScript type alias
type_def:
  id: "type:UserId"
  name: "UserId"
  kind: alias
  params: []
  body:
    aliased_type: { kind: named, type_id: "type:string" }
```

### 3.6 `opaque`

Types whose internal structure is hidden from consumers.

**Applicable languages:** Rust (via module privacy), ML languages, Swift

**Body fields used:** None exposed (internal structure private)

```yaml
# Opaque type (implementation hidden)
type_def:
  id: "type:FileHandle"
  name: "FileHandle"
  kind: opaque
  params: []
  body: {}  # Internal structure not exposed
```

### 3.7 `primitive`

Built-in types provided by the language.

**Body fields used:** None (no user-defined structure)

```yaml
# Primitive type
type_def:
  id: "type:i32"
  name: "i32"
  kind: primitive
  params: []
  body: {}
```

---

## 4. Variance

Variance describes how subtyping relationships between generic types relate to subtyping relationships between their type arguments.

### 4.1 Variance Kinds

| Variance | Notation | Rule | Usage |
|----------|----------|------|-------|
| **Covariant** | `+T`, `out T` | If `A <: B`, then `F<A> <: F<B>` | Read-only positions (return types, getters) |
| **Contravariant** | `-T`, `in T` | If `A <: B`, then `F<B> <: F<A>` | Write-only positions (parameter types) |
| **Invariant** | `T` | `F<A>` unrelated to `F<B>` | Read-write positions (mutable containers) |

### 4.2 Variance Examples

**Covariant example (Kotlin):**

```kotlin
// List is covariant in T (out T)
interface List<out T> {
    fun get(index: Int): T  // T in return position only
}

// If Dog <: Animal, then List<Dog> <: List<Animal>
fun printAnimals(animals: List<Animal>) { ... }
val dogs: List<Dog> = listOf(Dog())
printAnimals(dogs)  // OK: List<Dog> is subtype of List<Animal>
```

```yaml
type_def:
  id: "type:List"
  name: "List"
  kind: interface
  params:
    - name: "T"
      variance: covariant  # out T
      bounds: []
```

**Contravariant example (Kotlin):**

```kotlin
// Comparable is contravariant in T (in T)
interface Comparable<in T> {
    fun compareTo(other: T): Int  // T in parameter position only
}

// If Dog <: Animal, then Comparable<Animal> <: Comparable<Dog>
fun sortDogs(comparator: Comparable<Dog>) { ... }
val animalComparator: Comparable<Animal> = ...
sortDogs(animalComparator)  // OK: Comparable<Animal> is subtype of Comparable<Dog>
```

```yaml
type_def:
  id: "type:Comparable"
  name: "Comparable"
  kind: interface
  params:
    - name: "T"
      variance: contravariant  # in T
      bounds: []
```

**Invariant example (Java):**

```java
// Array is invariant in Java (both read and write)
String[] strings = new String[1];
Object[] objects = strings;  // Compiles (unsound!)
objects[0] = 42;  // ArrayStoreException at runtime
```

```yaml
# Java arrays are invariant in the type system (but unsound at runtime)
type_def:
  id: "type:Array"
  name: "Array"
  kind: class
  params:
    - name: "T"
      variance: invariant  # Both read and write
      bounds: []
```

### 4.3 Variance in IR

The IR captures declared variance. For languages without explicit variance:

| Language | Variance Declaration | IR Handling |
|----------|---------------------|-------------|
| Kotlin | Explicit (`in`/`out`) | Direct mapping |
| Scala | Explicit (`+`/`-`) | Direct mapping |
| TypeScript | Explicit (`in`/`out`) as of 4.7 | Direct mapping |
| Java | Wildcards only | Infer from usage |
| Rust | Implicit | Infer from PhantomData |
| Go | None (no generics until 1.18, invariant since) | Default invariant |

---

## 5. Type Reference Kinds

### 5.1 `named`

Reference to a concrete or generic type by ID.

```yaml
# Simple named type
type_ref:
  kind: named
  type_id: "type:String"
  args: []

# Generic instantiation
type_ref:
  kind: named
  type_id: "type:Vec"
  args:
    - { kind: named, type_id: "type:i32", args: [] }
```

### 5.2 `generic`

Unbound type parameter reference within a generic definition.

```yaml
# Reference to type parameter T within a generic function
type_ref:
  kind: generic
  type_id: "type_param:T"  # References a type_param, not a type_def
  args: []
```

### 5.3 `function`

Function/callable types.

```yaml
# (Int, Int) -> Int
type_ref:
  kind: function
  params:
    - { kind: named, type_id: "type:Int" }
    - { kind: named, type_id: "type:Int" }
  return_type: { kind: named, type_id: "type:Int" }
  effects: []

# async (String) -> Result<Data, Error>
type_ref:
  kind: function
  params:
    - { kind: named, type_id: "type:String" }
  return_type:
    kind: named
    type_id: "type:Result"
    args:
      - { kind: named, type_id: "type:Data" }
      - { kind: named, type_id: "type:Error" }
  effects:
    - { kind: async }
```

### 5.4 `tuple`

Fixed-size heterogeneous collections.

```yaml
# (Int, String, Bool)
type_ref:
  kind: tuple
  elements:
    - { kind: named, type_id: "type:Int" }
    - { kind: named, type_id: "type:String" }
    - { kind: named, type_id: "type:Bool" }
```

### 5.5 `union`

Discriminated unions (sum types expressed as type-level unions).

```yaml
# string | number | null (TypeScript)
type_ref:
  kind: union
  members:
    - { kind: named, type_id: "type:string" }
    - { kind: named, type_id: "type:number" }
    - { kind: named, type_id: "type:null" }
```

### 5.6 `intersection`

Types that satisfy multiple interfaces simultaneously.

```yaml
# A & B (TypeScript)
type_ref:
  kind: intersection
  members:
    - { kind: named, type_id: "type:A" }
    - { kind: named, type_id: "type:B" }
```

---

## 6. Language Examples

### 6.1 Rust: Struct with Generics and Lifetime

```rust
pub struct HashMap<K, V, S = RandomState>
where
    K: Eq + Hash,
{
    table: RawTable<(K, V)>,
    hash_builder: S,
}
```

```yaml
type_def:
  id: "type:HashMap"
  name: "HashMap"
  kind: struct
  visibility: public
  params:
    - name: "K"
      variance: invariant
      bounds:
        - { kind: named, type_id: "type:Eq" }
        - { kind: named, type_id: "type:Hash" }
      default: null
    - name: "V"
      variance: invariant
      bounds: []
      default: null
    - name: "S"
      variance: invariant
      bounds: []
      default: { kind: named, type_id: "type:RandomState" }
  constraints:
    - kind: type_bound
      param: "K"
      bound: { kind: named, type_id: "type:Eq" }
    - kind: type_bound
      param: "K"
      bound: { kind: named, type_id: "type:Hash" }
  body:
    fields:
      - name: "table"
        type:
          kind: named
          type_id: "type:RawTable"
          args:
            - kind: tuple
              elements:
                - { kind: generic, type_id: "type_param:K" }
                - { kind: generic, type_id: "type_param:V" }
        visibility: private
      - name: "hash_builder"
        type: { kind: generic, type_id: "type_param:S" }
        visibility: private
    methods: []
```

### 6.2 TypeScript: Interface with Union Types

```typescript
interface ApiResponse<T> {
  status: 'success' | 'error';
  data?: T;
  error?: string;
  timestamp: number;
}

type UserOrAdmin = User | Admin;
```

```yaml
type_def:
  id: "type:ApiResponse"
  name: "ApiResponse"
  kind: interface
  params:
    - name: "T"
      variance: covariant
      bounds: []
  body:
    required_methods: []
    provided_methods: []
    # Interface fields represented as required_methods (getters)
  # Note: TypeScript interface fields are modeled as property signatures

---
# Separate type alias
type_def:
  id: "type:UserOrAdmin"
  name: "UserOrAdmin"
  kind: alias
  params: []
  body:
    aliased_type:
      kind: union
      members:
        - { kind: named, type_id: "type:User" }
        - { kind: named, type_id: "type:Admin" }
```

### 6.3 Haskell: Algebraic Data Type

```haskell
data Tree a = Leaf a
            | Branch (Tree a) (Tree a)
            deriving (Eq, Show, Functor)
```

```yaml
type_def:
  id: "type:Tree"
  name: "Tree"
  kind: enum  # ADT represented as enum
  params:
    - name: "a"
      variance: covariant  # Functor implies covariance
      bounds: []
  constraints: []
  body:
    variants:
      - name: "Leaf"
        kind: tuple
        types:
          - { kind: generic, type_id: "type_param:a" }
      - name: "Branch"
        kind: tuple
        types:
          - kind: named
            type_id: "type:Tree"
            args: [{ kind: generic, type_id: "type_param:a" }]
          - kind: named
            type_id: "type:Tree"
            args: [{ kind: generic, type_id: "type_param:a" }]

# Derived instances create type relationships
type_relationship:
  from_type: "type:Tree"
  to_type: "type:Eq"
  kind: implements

type_relationship:
  from_type: "type:Tree"
  to_type: "type:Show"
  kind: implements

type_relationship:
  from_type: "type:Tree"
  to_type: "type:Functor"
  kind: implements
```

### 6.4 Java: Class Hierarchy with Bounded Generics

```java
public abstract class AbstractCollection<E> implements Collection<E> {
    public abstract Iterator<E> iterator();
    public abstract int size();

    public boolean isEmpty() {
        return size() == 0;
    }
}

public class ArrayList<E> extends AbstractCollection<E>
    implements List<E>, RandomAccess, Cloneable {
    // ...
}
```

```yaml
type_def:
  id: "type:AbstractCollection"
  name: "AbstractCollection"
  kind: class
  visibility: public
  params:
    - name: "E"
      variance: invariant
      bounds: []
  body:
    fields: []
    methods: ["fn:AbstractCollection::iterator", "fn:AbstractCollection::size", "fn:AbstractCollection::isEmpty"]

type_relationship:
  from_type: "type:AbstractCollection"
  to_type: "type:Collection"
  kind: implements

---
type_def:
  id: "type:ArrayList"
  name: "ArrayList"
  kind: class
  visibility: public
  params:
    - name: "E"
      variance: invariant
      bounds: []
  body:
    fields:
      - name: "elementData"
        type: { kind: named, type_id: "type:Object[]" }
        visibility: private
      - name: "size"
        type: { kind: named, type_id: "type:int" }
        visibility: private
    methods: []

type_relationship:
  from_type: "type:ArrayList"
  to_type: "type:AbstractCollection"
  kind: extends

type_relationship:
  from_type: "type:ArrayList"
  to_type: "type:List"
  kind: implements

type_relationship:
  from_type: "type:ArrayList"
  to_type: "type:RandomAccess"
  kind: implements

type_relationship:
  from_type: "type:ArrayList"
  to_type: "type:Cloneable"
  kind: implements
```

---

## 7. Higher-Kinded Types (HKT)

Higher-kinded types (types parameterized over type constructors) are challenging to represent uniformly. The IR captures HKT patterns with semantic loss annotations.

### 7.1 The HKT Challenge

```haskell
-- Functor takes a type constructor (* -> *)
class Functor f where
    fmap :: (a -> b) -> f a -> f b
```

In languages without HKT support, this cannot be directly expressed.

### 7.2 IR Representation (Lossy)

```yaml
type_def:
  id: "type:Functor"
  name: "Functor"
  kind: interface
  params:
    - name: "F"
      variance: invariant
      bounds: []
      # Note: F is a type constructor, not a concrete type
  body:
    required_methods:
      - name: "fmap"
        type_params:
          - { name: "A", variance: invariant, bounds: [] }
          - { name: "B", variance: invariant, bounds: [] }
        params:
          - name: "f"
            type:
              kind: function
              params: [{ kind: generic, type_id: "type_param:A" }]
              return_type: { kind: generic, type_id: "type_param:B" }
          - name: "fa"
            type:
              kind: named
              type_id: "type_param:F"  # F<A> - type constructor application
              args: [{ kind: generic, type_id: "type_param:A" }]
        return_type:
          kind: named
          type_id: "type_param:F"  # F<B>
          args: [{ kind: generic, type_id: "type_param:B" }]

# Gap marker for HKT
gap_marker:
  id: "gap:functor_hkt"
  location: "type:Functor"
  gap_type: structural
  gap_pattern_id: "TS-003"  # HKT to non-HKT
  severity: high
  description: "Higher-kinded type cannot be directly expressed in target"
  source_concept: "type constructor parameter"
  target_concept: "generic type parameter"
  suggested_mitigations:
    - "Use defunctionalization pattern"
    - "Create concrete instances (FunctorList, FunctorOption)"
    - "Use type class simulation with associated types"
  preservation_level: 1
```

### 7.3 Target Language Workarounds

| Target | Strategy | Preservation Level |
|--------|----------|-------------------|
| Rust | Associated types + GATs | Level 2 |
| TypeScript | Module augmentation | Level 1 |
| Java | Witness types | Level 1 |
| Go | Code generation | Level 1 |

---

## 8. Type Relationships

### 8.1 Relationship Kinds

| Kind | Meaning | Example |
|------|---------|---------|
| `extends` | Class inheritance | `class Dog extends Animal` |
| `implements` | Interface implementation | `class ArrayList implements List` |
| `subtype_of` | Structural subtyping | TypeScript structural compatibility |
| `convertible_to` | Explicit conversion exists | `i32` convertible to `i64` |

### 8.2 Relationship Semantics

**`extends`** (nominal inheritance):
- Single inheritance in Java/C#, multiple in C++/Python
- Implies `subtype_of` in most languages
- Carries implementation (fields, methods)

**`implements`** (interface conformance):
- Multiple implementation allowed
- No field inheritance
- May be nominal (Java) or structural (Go)

**`subtype_of`** (subtype relation):
- May be structural (TypeScript, Go interfaces)
- May be nominal (Java class hierarchy)
- Captures the actual subtyping lattice

**`convertible_to`** (conversion):
- Explicit conversion operators
- Rust `From`/`Into` traits
- Not implicit subtyping

### 8.3 Relationship Example

```yaml
# Full type hierarchy for an animal system
type_relationship:
  from_type: "type:Dog"
  to_type: "type:Animal"
  kind: extends

type_relationship:
  from_type: "type:Dog"
  to_type: "type:Comparable"
  kind: implements

type_relationship:
  from_type: "type:Dog"
  to_type: "type:Animal"
  kind: subtype_of  # Implied by extends

type_relationship:
  from_type: "type:String"
  to_type: "type:str"
  kind: convertible_to  # Rust String -> &str
```

---

## 9. Cross-Layer References

### 9.1 Layer 4 (Structural) to Layer 3

Modules contain type definitions:

```yaml
# Layer 4
module:
  id: "mod:collections"
  definitions:
    - kind: type
      ref: "type:HashMap"    # References Layer 3
    - kind: type
      ref: "type:Vec"
    - kind: function
      ref: "fn:sort"         # References Layer 2
```

### 9.2 Layer 2 (Control Flow) Using Layer 3

Function signatures reference types:

```yaml
# Layer 2
function:
  id: "fn:process_items"
  params:
    - name: "items"
      type:                           # TypeRef from Layer 3
        kind: named
        type_id: "type:Vec"
        args:
          - kind: generic
            type_id: "type_param:T"
  return_type:
    kind: named
    type_id: "type:Result"
    args:
      - kind: named
        type_id: "type:ProcessedData"
      - kind: named
        type_id: "type:Error"
```

### 9.3 Layer 1 (Data Flow) Using Layer 3

Bindings have types:

```yaml
# Layer 1
binding:
  id: "bind:user_map"
  name: "user_map"
  type:                               # TypeRef from Layer 3
    kind: named
    type_id: "type:HashMap"
    args:
      - { kind: named, type_id: "type:UserId" }
      - { kind: named, type_id: "type:User" }
  mutability: mutable
```

---

## 10. Annotations and Gap Markers

### 10.1 Type-Related Annotations

```yaml
# Inferred nullability
semantic_annotation:
  target: "type:UserData"
  kind: nullability
  value:
    nullable_fields: ["email", "phone"]
    non_null_fields: ["id", "name"]
  confidence: 0.95
  source: inferred

# Variance annotation (for languages without explicit variance)
semantic_annotation:
  target: "type:Producer"
  kind: variance_annotation
  value:
    param: "T"
    inferred_variance: covariant
    evidence: ["only appears in return position"]
  confidence: 0.85
  source: inferred
```

### 10.2 Common Type System Gap Patterns

| Pattern ID | Description | Gap Type |
|------------|-------------|----------|
| TS-001 | Dynamic to static typing | lossy |
| TS-002 | Nullable to non-nullable | structural |
| TS-003 | HKT to non-HKT | structural |
| TS-009 | Type erasure boundaries | lossy |
| TS-014 | Variance handling | structural |

---

## 11. Quick Reference

### Type Definition Template

```yaml
type_def:
  id: "type:{name}"
  name: "{name}"
  kind: struct | enum | class | interface | alias | opaque | primitive
  params:
    - name: "{param_name}"
      variance: invariant | covariant | contravariant
      bounds: [TypeRef...]
      default: TypeRef?
  constraints:
    - kind: type_bound | where_clause | associated_type
      param: "{param_name}"
      bound: TypeRef
  body:
    # Varies by kind
  visibility: public | internal | private | package
```

### Type Reference Template

```yaml
type_ref:
  kind: named | generic | function | tuple | union | intersection
  # Fields depend on kind
```

### Type Relationship Template

```yaml
type_relationship:
  from_type: TypeId
  to_type: TypeId
  kind: extends | implements | subtype_of | convertible_to
```

---

*Generated for Phase 4: IR Schema Design (ai-f33)*
