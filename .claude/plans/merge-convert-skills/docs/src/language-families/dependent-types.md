# Dependent Types Family

> Type systems where types can depend on values, enabling proofs and precise specifications.

## Overview

Dependent types blur the line between types and values:

- **Types from values** - Type `Vec n Int` depends on value `n`
- **Proof carrying code** - Types encode invariants
- **Program extraction** - Generate programs from proofs
- **Total functions** - All functions must terminate

## Base Family

This is a **feature family** extending [ML-FP](ml-fp.md) with value-dependent types.

## Languages

| Language | Focus | Notes |
|----------|-------|-------|
| Idris | Practical programming | Dependent types for real programs |
| Agda | Proof assistant | Cubical type theory support |
| Coq | Theorem proving | Extraction to OCaml/Haskell |
| Lean | Math formalization | Mathlib library |
| F* | Verified code | Extraction to F#/OCaml/C |

## Key Concepts

### Dependent Types

```idris
-- Type depends on value n
data Vect : Nat -> Type -> Type where
  Nil  : Vect 0 a
  (::) : a -> Vect n a -> Vect (S n) a

-- Type-safe head (impossible on empty)
head : Vect (S n) a -> a
head (x :: _) = x

-- Concatenation with length proof
(++) : Vect n a -> Vect m a -> Vect (n + m) a
```

### Proofs as Types

```idris
-- Prove that list reverse is its own inverse
reverseInvolutive : (xs : List a) -> reverse (reverse xs) = xs
```

### Refinement Types

```fstar
// F* refinement type
type nat = x:int{x >= 0}

// Function that only accepts positive
val sqrt : x:nat{x > 0} -> nat
```

## Conversion Considerations

### Converting FROM Dependent Types

**What's preserved:**

- Runtime code (proofs erased)
- Basic algorithms

**What's lost:**

- Compile-time guarantees
- Length-indexed types → runtime checks
- Proofs → documentation

### Converting TO Dependent Types

**Requirements:**

- All functions must be total
- Must prove termination
- Types must be precise

**Not practical for:**

- Most production code
- Partial functions
- IO-heavy code

## Sources

- [Idris Documentation](https://idris2.readthedocs.io/)
- [Agda Documentation](https://agda.readthedocs.io/)
- [Software Foundations](https://softwarefoundations.cis.upenn.edu/)

## See Also

- [ML-FP](ml-fp.md) - Base family
- [Overview](overview.md) - Comparison matrices
