# Consolidated Pattern Analysis

## Overview

This document consolidates all pattern findings from Phases 0-10 into a unified classification system for the IR-based code conversion pipeline.

## Pattern Categories

### 1. Universal Patterns (Core IR)

These patterns exist in essentially all programming languages and form the foundation of the IR.

| Pattern | IR Construct | Description |
|---------|--------------|-------------|
| Function Definition | `FunctionDef` | Named callable with parameters and return |
| Variable Binding | `BindingDef` | Name-value association |
| Type Alias | `TypeDef.alias` | Named type reference |
| Conditional | `IfExpression` | If-then-else branching |
| Loop | `LoopConstruct` | Iteration (for/while/loop) |
| Sequence | `Block` | Ordered statement execution |
| Binary Operation | `BinaryOp` | Arithmetic, logical, comparison |
| Unary Operation | `UnaryOp` | Negation, increment, etc. |
| Function Call | `CallExpression` | Apply function to arguments |
| Record/Struct | `TypeDef.struct` | Named field collection |
| Array/List | `TypeDef.array` | Ordered element collection |
| String | `TypeDef.string` | Text data |
| Integer | `TypeDef.integer` | Numeric data |
| Boolean | `TypeDef.boolean` | True/false value |

### 2. Family Patterns (Extensions)

These patterns are shared within language families and require IR extensions.

#### ML/FP Family (Haskell, OCaml, F#, Scala, Roc, Elm)

| Pattern | IR Construct | Fallback |
|---------|--------------|----------|
| Pattern Matching | `MatchExpression` | switch/if-else chain |
| Algebraic Data Types | `TypeDef.adt` | class hierarchy + sealed |
| Higher-Kinded Types | `TypeDef.hkt` | monomorphize, type erasure |
| Type Classes | `TypeClassDef` | interfaces + manual resolution |
| Currying | `CurriedFunction` | wrapper functions |
| Immutability Default | `ImmutabilityAnnotation` | const/readonly modifiers |
| Expression-Oriented | `ExpressionBlock` | statement-with-return |
| Option Type | `TypeDef.option` | nullable + null checks |
| Result Type | `TypeDef.result` | exceptions or error codes |
| Monadic Composition | `MonadChain` | explicit callbacks/promises |
| Effects System | `EffectAnnotation` | IO type or side effect tracking |

#### Systems Family (Rust, C, C++, Zig)

| Pattern | IR Construct | Fallback |
|---------|--------------|----------|
| Ownership | `OwnershipAnnotation` | GC or manual memory |
| Borrowing | `BorrowAnnotation` | reference passing |
| Lifetimes | `LifetimeAnnotation` | N/A (GC handles) |
| Move Semantics | `MoveSemantics` | copy semantics |
| Zero-Cost Abstraction | `InlineHint` | standard abstraction |
| Unsafe Blocks | `UnsafeBlock` | remove marker (trust runtime) |
| Const Generics | `ConstGeneric` | runtime parameters |
| Trait Objects | `TraitObjectDef` | interface + vtable |

#### BEAM Family (Erlang, Elixir, Gleam)

| Pattern | IR Construct | Fallback |
|---------|--------------|----------|
| Actor Processes | `ActorDef` | threads + message queues |
| Message Passing | `SendReceive` | async/await or channels |
| Pattern Matching | `MatchExpression` | switch/if-else chain |
| Supervision Trees | `SupervisionTree` | try/catch + restart logic |
| Hot Code Loading | `HotSwapAnnotation` | restart required |
| Binary Pattern Match | `BinaryMatch` | manual byte parsing |
| List Comprehensions | `ListComprehension` | map/filter chains |

#### Lisp Family (Clojure, Common Lisp, Scheme, Racket)

| Pattern | IR Construct | Fallback |
|---------|--------------|----------|
| Homoiconicity | `QuotedExpression` | manual AST construction |
| Macros | `MacroDef` | code generation or functions |
| S-Expressions | `SExpression` | standard AST |
| Dynamic Typing | `DynamicType` | any/object type |
| Persistent Data | `PersistentCollection` | immutable copies |
| Multi-Methods | `MultiMethodDef` | visitor pattern |

#### Managed OOP Family (Java, C#, Kotlin)

| Pattern | IR Construct | Fallback |
|---------|--------------|----------|
| Classes | `ClassDef` | direct mapping |
| Interfaces | `InterfaceDef` | direct mapping |
| Inheritance | `InheritanceRelation` | composition fallback |
| Generics | `GenericTypeDef` | type erasure or reification |
| Annotations | `AnnotationDef` | decorators or attributes |
| Properties | `PropertyDef` | getter/setter methods |
| Nullable Types | `NullableType` | Option or union |

#### Dynamic Family (Python, Ruby, JavaScript, PHP)

| Pattern | IR Construct | Fallback |
|---------|--------------|----------|
| Duck Typing | `DuckType` | interfaces + type hints |
| Dynamic Properties | `DynamicProperty` | dictionary/map |
| Decorators | `DecoratorDef` | wrapper functions |
| Metaclasses | `MetaclassDef` | factory pattern |
| First-Class Functions | `FirstClassFunction` | direct mapping |
| Mixins | `MixinDef` | multiple inheritance or composition |

### 3. Language-Specific Patterns

These are unique to specific languages and require special handling.

#### Rust-Specific

| Pattern | ID | Description | Conversion Strategy |
|---------|----|--------------|--------------------|
| Ownership System | RS-001 | Linear types | GC or manual management |
| Lifetimes | RS-002 | Reference validity | N/A in GC languages |
| Trait Bounds | RS-003 | Generic constraints | Interface constraints |
| `?` Operator | RS-004 | Error propagation | try/catch or Result chain |
| Pattern Guards | RS-005 | Match with conditions | if-else within cases |
| Derive Macros | RS-006 | Auto-impl traits | manual implementation |

#### TypeScript-Specific

| Pattern | ID | Description | Conversion Strategy |
|---------|----|--------------|--------------------|
| Union Types | TS-001 | A | B syntax | ADT or sealed class |
| Type Guards | TS-002 | Runtime narrowing | instanceof/switch |
| Mapped Types | TS-003 | Type transformations | manual type def |
| Template Literals | TS-004 | String types | string validation |
| Declaration Files | TS-005 | .d.ts definitions | interface definitions |

#### Go-Specific

| Pattern | ID | Description | Conversion Strategy |
|---------|----|--------------|--------------------|
| Goroutines | GO-001 | Green threads | async/await or threads |
| Channels | GO-002 | CSP communication | queues or async streams |
| Defer | GO-003 | Deferred execution | try/finally or RAII |
| Multiple Returns | GO-004 | Error handling | Result type or exceptions |
| Interface Satisfaction | GO-005 | Implicit interfaces | explicit implements |

#### Scala-Specific

| Pattern | ID | Description | Conversion Strategy |
|---------|----|--------------|--------------------|
| Higher-Kinded Types | SC-001 | F[_] syntax | monomorphize |
| Variance Annotations | SC-002 | +T/-T | manual verification |
| Implicit Parameters | SC-003 | Context injection | explicit parameters |
| Given/Using | SC-004 | Type class instances | interface instances |
| For Comprehensions | SC-005 | Monadic syntax | flatMap chains |

#### Roc-Specific

| Pattern | ID | Description | Conversion Strategy |
|---------|----|--------------|--------------------|
| Platform Effects | ROC-001 | Task types | IO monad or async |
| Backpassing | ROC-002 | `<-` syntax | callbacks or async/await |
| Opaque Types | ROC-003 | Encapsulated types | newtype pattern |
| Tag Unions | ROC-004 | Structural ADTs | sealed classes |
| Abilities | ROC-005 | Type classes | interfaces + impl |

#### Python-Specific

| Pattern | ID | Description | Conversion Strategy |
|---------|----|--------------|--------------------|
| Decorators | PY-001 | Function wrappers | annotations or wrappers |
| Context Managers | PY-002 | with statement | try/finally or RAII |
| Generators | PY-003 | yield syntax | iterators or streams |
| Metaclasses | PY-004 | Class factories | factory pattern |
| Multiple Inheritance | PY-005 | MRO | composition or interfaces |

## Pattern Conversion Matrix

### Cross-Family Pattern Availability

| Pattern | ML/FP | Systems | BEAM | Lisp | OOP | Dynamic |
|---------|-------|---------|------|------|-----|---------|
| Pattern Matching | ✅ | ✅ (Rust) | ✅ | ✅ | ⚠️ | ⚠️ |
| ADTs | ✅ | ✅ (Rust) | ✅ | ✅ | ⚠️ | ❌ |
| Higher-Kinded Types | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Ownership | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Actors | ⚠️ | ❌ | ✅ | ⚠️ | ⚠️ | ⚠️ |
| Macros | ⚠️ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Generics | ✅ | ✅ | ⚠️ | ✅ | ✅ | ⚠️ |
| Type Classes | ✅ | ✅ (Rust) | ⚠️ | ✅ | ⚠️ | ❌ |
| Effects | ✅ | ❌ | ✅ | ⚠️ | ❌ | ❌ |
| Null Safety | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ❌ |

Legend: ✅ Native support, ⚠️ Partial/library, ❌ Not available

## Semantic Preservation Levels

When converting between languages, target these levels in order:

1. **Equivalent**: Same observable behavior in all cases
2. **Behavioral**: Same behavior for common cases, may differ in edge cases
3. **Approximate**: Similar behavior, documented differences
4. **Manual**: Requires human intervention to decide approach

## Gap Severity Classification

Based on Phase 3 analysis, gaps are classified by severity:

| Severity | Count | Description | Action |
|----------|-------|-------------|--------|
| Critical | 12 | Semantic loss without manual intervention | Block conversion, require human decision |
| High | 28 | Significant idiom change | Warn, suggest alternatives |
| Medium | 45 | Pattern translation needed | Auto-convert with annotation |
| Low | 67 | Minor syntax differences | Auto-convert silently |
| Info | 150+ | Documentation only | Log for reference |

## Recommendations

### IR Design Implications

1. **Core IR must be minimal** - Only truly universal patterns in base IR
2. **Extensions must be composable** - Enable/disable per source/target pair
3. **Annotations preserve context** - Source patterns annotated for synthesis
4. **Gaps are first-class** - Gap detection built into extraction
5. **Human decisions tracked** - Decision points marked for review

### Skill Architecture Implications

1. **Single analysis skill** - One skill for extraction regardless of source
2. **Single synthesis skill** - One skill for code generation regardless of target
3. **Idiomatic skills per language** - Language-specific best practices
4. **Pattern library** - Reusable conversion patterns

### Tool Integration

1. **Extractors** - Per-language IR extraction (Python, Rust, TS, Go, Scala, Roc done)
2. **Synthesizers** - Per-language code generation (same languages done)
3. **Validators** - IR validation and round-trip testing
4. **Gap Detector** - Cross-language gap identification
