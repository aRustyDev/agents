# ir-extract-scala

Scala source code extractor for the IR extraction/synthesis pipeline.

## Overview

This package extracts structured IR from Scala source code with special handling for:

- **Higher-kinded types**: F[_] and variance annotations
- **Implicits/Givens**: Type class instances and context parameters
- **Case classes**: Product types with automatic methods
- **Sealed traits**: Sum types for pattern matching
- **Variance**: Covariant (+T) and contravariant (-T)

## Installation

```bash
pip install ir-extract-scala
```

## Usage

### CLI

```bash
# Extract IR from Scala file
ir-extract-scala src/main/scala/Example.scala

# Output as JSON
ir-extract-scala Example.scala -f json -o ir-output.json
```

### API

```python
from ir_extract_scala import ScalaExtractor
from ir_core.base import ExtractConfig

source = '''
trait Functor[F[_]] {
  def map[A, B](fa: F[A])(f: A => B): F[B]
}

case class User(name: String, age: Int)

object UserFunctor extends Functor[Option] {
  def map[A, B](fa: Option[A])(f: A => B): Option[B] = fa.map(f)
}
'''

extractor = ScalaExtractor()
config = ExtractConfig()
ir = extractor.extract(source, "Example.scala", config)

# Access extracted data
for type_def in ir.types:
    print(f"Type: {type_def.name}")
```

## Extracted Patterns

### Higher-Kinded Types

```scala
trait Functor[F[_]] {
  def map[A, B](fa: F[A])(f: A => B): F[B]
}
```

IR representation:
```yaml
type_def:
  name: Functor
  kind: interface
  type_params:
    - name: F
      kind: higher_kinded
      arity: 1
```

### Variance Annotations

```scala
trait Producer[+T] {  // Covariant
  def produce: T
}

trait Consumer[-T] {  // Contravariant
  def consume(t: T): Unit
}
```

### Implicit Parameters

```scala
def sort[T](list: List[T])(implicit ord: Ordering[T]): List[T]
```

Captured as:
```yaml
function:
  name: sort
  implicit_params:
    - name: ord
      type: Ordering[T]
```

### Given Instances (Scala 3)

```scala
given Ordering[Int] with
  def compare(x: Int, y: Int): Int = x - y
```

### Case Classes

```scala
case class Point(x: Int, y: Int)
```

Extracted as struct with automatic equals, hashCode, copy, etc.

## Semantic Annotations

| ID | Pattern | Description |
|----|---------|-------------|
| SC-001 | Higher-kinded type | F[_] type parameter |
| SC-002 | Variance | +T or -T annotation |
| SC-003 | Implicit params | Implicit/using parameters |
| SC-004 | Given instance | Type class instance |
| SC-005 | Case class | Product type |

## Gap Detection

| ID | Description | Severity |
|----|-------------|----------|
| SC-010 | Higher-kinded type (limited support) | High |
| SC-011 | Variance annotation | Medium |
| SC-012 | Implicit parameters | Medium |
| SC-013 | Given instances | Medium |
| SC-014 | Self types | Medium |
| SC-015 | Context bounds | Medium |

## Development

```bash
pip install -e ".[dev]"
pytest
mypy ir_extract_scala
```

## License

MIT
