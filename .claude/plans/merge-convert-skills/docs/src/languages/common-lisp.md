# Common Lisp

> Multi-paradigm Lisp dialect with powerful object system and condition handling.

## Overview

Common Lisp is a standardized dialect of Lisp, defined by ANSI in 1994, unifying earlier dialects like MacLisp, Interlisp, and Zetalisp. It's a dynamic, multi-paradigm language known for its powerful macro system, interactive development, and the Common Lisp Object System (CLOS).

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | LISP | Code as data, macros |
| Subtype | classic-lisp | Full-featured Lisp-2 |

## Key Characteristics

- **Homoiconicity** - code represented as data structures
- **Powerful macro system** for language extension
- **CLOS** - multiple inheritance, multiple dispatch, MOP
- **Condition system** - restartable exceptions
- **Dynamic typing** with optional declarations
- **Lisp-2** - separate namespaces for functions and values

## Key Differences from Clojure

| Feature | Common Lisp | Clojure |
|---------|-------------|---------|
| Namespace | Lisp-2 (separate) | Lisp-1 (unified) |
| Mutability | Default mutable | Default immutable |
| Object System | CLOS | Protocols, records |
| Platform | Native, various | JVM, JS |

## Conversion Notes

- Lisp-2 → Lisp-1 requires careful function/value distinction
- CLOS → protocols or interfaces
- Condition system → try/catch with custom handling
- defmacro → target macro system or code generation
- Dynamic variables → explicit state passing or refs

## Sources

- [Common Lisp HyperSpec](http://www.lispworks.com/documentation/HyperSpec/)
- [Practical Common Lisp](https://gigamonkeys.com/book/)
