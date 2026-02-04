# Fortran

> High-performance language for scientific computing and numerical analysis.

## Overview

Fortran (Formula Translation) is a compiled programming language developed at IBM in the 1950s, making it one of the oldest high-level languages still in active use. It dominates high-performance computing (HPC), scientific simulations, weather modeling, and computational physics.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Procedural | Imperative, array-oriented |
| Subtype | scientific | HPC, numerical computing |

## Key Characteristics

- **First-class array operations** with built-in vectorization
- **Column-major array storage** (unlike C's row-major)
- **Highly optimized compilers** for numerical performance
- **Coarray Fortran** for parallel computing (Fortran 2008+)
- **Legacy compatibility** spanning 70+ years of code

## Version Notes

| Version | Key Features |
|---------|--------------|
| FORTRAN 77 | Fixed-form, structured programming |
| Fortran 90 | Free-form, modules, derived types |
| Fortran 2003 | OOP, interoperability with C |
| Fortran 2018 | Enhanced parallelism, IEEE arithmetic |

## Conversion Notes

- Array indexing starts at 1 (not 0)
- Column-major to row-major array conversion
- COMMON blocks → modules or explicit parameters
- Implicit typing must be made explicit
- Numerical precision requirements critical

## Sources

- [Fortran-lang](https://fortran-lang.org/)
- [Modern Fortran](https://www.manning.com/books/modern-fortran)
