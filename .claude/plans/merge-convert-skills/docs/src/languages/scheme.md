# Scheme

> Minimalist Lisp dialect emphasizing simplicity and first-class continuations.

## Overview

Scheme is a minimalist dialect of Lisp created by Guy Steele and Gerald Sussman in the 1970s. It emphasizes a small core with powerful abstractions, particularly first-class procedures and continuations. Scheme has been influential in programming language research and computer science education.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | LISP | Minimal Lisp-1 |
| Subtype | minimal-lisp | Small core, elegant |

## Key Characteristics

- **Minimalist design** - small core specification
- **Lisp-1** - unified namespace for functions and values
- **First-class continuations** (call/cc)
- **Tail call optimization** guaranteed by specification
- **Hygienic macros** (syntax-rules, syntax-case)
- **Lexical scoping** (unlike early Lisps)

## Standards

| Standard | Notes |
|----------|-------|
| R5RS | Classic, widely implemented |
| R6RS | Larger, modules, records |
| R7RS-small | Modern minimal |
| R7RS-large | Batteries-included (in progress) |

## Key Differences from Common Lisp

| Feature | Scheme | Common Lisp |
|---------|--------|-------------|
| Namespace | Lisp-1 | Lisp-2 |
| Size | Minimal | Large |
| Continuations | First-class | Limited |
| Tail calls | Guaranteed | Implementation-dependent |

## Conversion Notes

- call/cc → limited patterns (escape, coroutines)
- Hygienic macros → different macro systems
- Guaranteed TCO → explicit trampolining or loops
- Multiple implementations vary significantly

## Sources

- [R7RS Specification](https://small.r7rs.org/)
- [SICP](https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/6515/sicp.zip/index.html)
