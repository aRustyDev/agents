# Ada

> Safety-critical programming language for high-integrity and real-time systems.

## Overview

Ada is a structured, statically typed programming language designed for the US Department of Defense in the late 1970s. Named after Ada Lovelace, it emphasizes safety, reliability, and maintainability for mission-critical systems in aerospace, defense, transportation, and medical devices.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Procedural | Structured, safety-focused |
| Subtype | safety-critical | High-integrity systems |

## Key Characteristics

- **Strong static typing** with explicit range constraints
- **Built-in concurrency** (tasks, protected objects)
- **Exception handling** with propagation
- **Contract-based programming** (pre/post conditions, invariants)
- **SPARK subset** for formal verification

## Version Notes

| Version | Key Features |
|---------|--------------|
| Ada 83 | Original standard |
| Ada 95 | OOP, protected types, child packages |
| Ada 2005 | Interfaces, containers |
| Ada 2012 | Contracts, iterators, expressions |
| Ada 2022 | Parallel blocks, lightweight parallelism |

## Conversion Notes

- Task types → threads or actors
- Protected types → synchronized/concurrent structures
- Package specifications → interfaces/headers
- Subtypes with constraints → refinement types or validation
- Pragma directives → compiler-specific annotations

## Sources

- [Ada Reference Manual](http://www.ada-auth.org/standards/rm12_w_tc1/html/RM-TOC.html)
- [Learn Ada](https://learn.adacore.com/)
