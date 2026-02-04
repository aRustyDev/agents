# COBOL

> Business-oriented programming language for enterprise and financial applications.

## Overview

COBOL (Common Business-Oriented Language) is a compiled, English-like programming language designed for business applications, first released in 1959. It remains critical in banking, insurance, and government systems, processing an estimated 95% of ATM transactions and 80% of in-person transactions globally.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Procedural | Structured, imperative |
| Subtype | business | Business/financial focus |

## Key Characteristics

- **Verbose English-like syntax** for readability by non-programmers
- **Fixed-point decimal arithmetic** for precise financial calculations
- **Record-oriented data structures** matching business documents
- **Division-based program structure** (Identification, Environment, Data, Procedure)
- **Massive legacy codebase** (estimated 220 billion lines in production)

## Conversion Notes

- Decimal precision must be preserved in target languages
- File/record handling maps to streams or structured data
- PERFORM loops → for/while loops
- COPYBOOK includes → modules/imports
- Batch processing patterns common

## Sources

- [IBM COBOL Documentation](https://www.ibm.com/docs/en/cobol-zos)
- [GnuCOBOL](https://gnucobol.sourceforge.io/)
