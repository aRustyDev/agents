# Phase 10: Scala Extractor & Synthesizer

Implement Scala language support for the IR extraction/synthesis pipeline.

## Goal

Build Scala extractor and synthesizer, focusing on Scala's unique combination of OOP and FP, higher-kinded types, and implicits/given system.

## Dependencies

- **Phase 5**: Python MVP
- **Phase 7**: TypeScript tooling (type system complexity)
- **Phase 9**: Roc tooling (FP patterns)

### Scala-Specific IR Requirements

From `docs/src/ir-schema/layer-3.md` (Type IR):
- Higher-kinded types (F[_])
- Variance annotations (+T, -T)
- Implicit parameters / given instances
- Type classes via traits

From `docs/src/ir-schema/cross-cutting.md`:
- Annotation kinds: `TS-003` (HKT→No HKT), `TS-007` (Variance handling)

## Deliverables

- [ ] Scala extractor handling HKT and implicits
- [ ] Scala synthesizer with idiomatic patterns
- [ ] Cross-language tests
- [ ] 25+ Scala-specific test cases
- [ ] Validation report

---

## Scala-Specific Challenges

### Higher-Kinded Types

```scala
// HKT example: Functor
trait Functor[F[_]] {
  def map[A, B](fa: F[A])(f: A => B): F[B]
}

object ListFunctor extends Functor[List] {
  def map[A, B](fa: List[A])(f: A => B): List[B] = fa.map(f)
}
```

**IR Representation**:

```yaml
type_def:
  name: Functor
  kind: trait
  type_params:
    - name: F
      kind: higher_kinded  # F[_]
      arity: 1
  methods:
    - name: map
      type_params: [A, B]
      params:
        - name: fa
          type: "F[A]"
        - name: f
          type: "A => B"
      returns: "F[B]"
  annotations:
    - kind: TS-003
      value: { hkt_arity: 1 }
```

### Implicits / Givens (Scala 3)

```scala
// Scala 3 given/using
trait Ord[T]:
  def compare(a: T, b: T): Int

given Ord[Int] with
  def compare(a: Int, b: Int): Int = a - b

def sort[T](list: List[T])(using ord: Ord[T]): List[T] =
  list.sortWith((a, b) => ord.compare(a, b) < 0)
```

**IR Representation**:

```yaml
function:
  name: sort
  type_params: [T]
  params:
    - name: list
      type: "List[T]"
  context_params:  # using/implicit
    - name: ord
      type: "Ord[T]"
      resolution: implicit
  annotations:
    - kind: implicit_resolution
      value: { strategy: typeclass }
```

### Variance

```scala
trait Producer[+T] {  // Covariant
  def produce: T
}

trait Consumer[-T] {  // Contravariant
  def consume(t: T): Unit
}

trait Processor[T] {  // Invariant
  def process(t: T): T
}
```

**IR Representation**:

```yaml
type_def:
  name: Producer
  type_params:
    - name: T
      variance: covariant  # +T
  annotations:
    - kind: TS-007
      value: { variance: covariant }
```

---

## Tasks

### 10.1 Scala Extractor Implementation

**Implementation Approach**:
- **Primary**: Scalameta for AST parsing
- **Semantics**: Metals LSP for type information
- **Alternative**: Scala 3 TASTy reader for compiled artifacts

```scala
// tools/ir-extract/scala/Extract.scala
import scala.meta._

object ScalaExtractor {
  def extract(source: String): IR = {
    val tree = source.parse[Source].get

    val types = extractTypes(tree)
    val functions = extractFunctions(tree)
    val implicits = extractImplicits(tree)

    IR(types, functions, implicits)
  }
}
```

**Deliverable**: `tools/ir-extract/scala/`

---

### 10.2 Scala Synthesizer Implementation

**Key Patterns**:
- Case classes for data
- Trait + object for type classes
- For-comprehensions for monadic code
- Pattern matching with guards
- Given/using for context

```python
def gen_trait(self, trait_def: TypeDef) -> str:
    variance_prefix = {
        "covariant": "+",
        "contravariant": "-",
        "invariant": ""
    }

    type_params = ", ".join(
        f"{variance_prefix.get(p.variance, '')}{p.name}"
        for p in trait_def.type_params
    )

    return f"trait {trait_def.name}[{type_params}]"
```

**Deliverable**: `tools/ir-synthesize/scala/`

---

### 10.3 Cross-Language Testing

**Key Conversions**:

| Direction | Challenge |
|-----------|-----------|
| Scala → Python | HKT → Protocol + dispatch |
| Scala → TypeScript | Implicits → explicit params |
| Scala → Rust | HKT → trait objects or monomorphization |
| Python → Scala | Add type annotations |

---

### 10.4-10.6 Test Suite, Report, Review

**Test Categories**:

```
tests/fixtures/scala/
├── types/
│   ├── case_classes.scala
│   ├── sealed_traits.scala
│   ├── higher_kinded.scala
│   └── variance.scala
├── implicits/
│   ├── type_classes.scala
│   ├── given_using.scala
│   └── context_bounds.scala
├── control/
│   ├── for_comprehensions.scala
│   ├── pattern_matching.scala
│   └── partial_functions.scala
└── oop_fp/
    ├── traits_objects.scala
    └── case_class_methods.scala
```

---

## Success Criteria

- [ ] Scala extractor working (20+ fixtures)
- [ ] Scala synthesizer producing compilable code
- [ ] HKT captured in IR (even if lossy for some targets)
- [ ] Implicits/givens tracked
- [ ] Variance annotations preserved
- [ ] 25+ test cases passing

## Effort Estimate

8-12 days (complex type system)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| HKT conversion lossy | High | Medium | Document as gap, use workarounds |
| Implicits hard to track | Medium | High | Focus on explicit given syntax |
| Scala 2 vs 3 differences | Medium | Medium | Target Scala 3 only |

## Output Files

| File | Description |
|------|-------------|
| `tools/ir-extract/scala/` | Scala extractor |
| `tools/ir-synthesize/scala/` | Scala synthesizer |
| `tests/fixtures/scala/` | Test fixtures |
| `analysis/phase10-validation-report.md` | Results |
