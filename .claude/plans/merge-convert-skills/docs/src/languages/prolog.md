# Prolog

> Logic programming language based on formal logic and automated reasoning.

## Overview

Prolog (Programming in Logic) is a logic programming language developed in 1972 by Alain Colmerauer. Programs consist of facts and rules that define relationships, and the Prolog engine uses unification and backtracking to find solutions. It's used in AI, natural language processing, expert systems, and symbolic computation.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Logic | Declarative, relational |
| Subtype | horn-clause | Based on first-order logic |

## Key Characteristics

- **Declarative programming** - specify what, not how
- **Unification** - pattern matching on steroids
- **Backtracking** - automatic search through solution space
- **Logic variables** - variables bind during execution
- **Cut (!)** - control backtracking
- **Definite clause grammars** (DCG) for parsing

## Programming Model

```prolog
% Facts
parent(tom, mary).
parent(mary, ann).

% Rules
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).

% Query
?- grandparent(tom, ann).
% true
```

## Implementations

| Implementation | Notes |
|----------------|-------|
| SWI-Prolog | Most popular, extensive libraries |
| GNU Prolog | Native compilation |
| SICStus | Commercial, high-performance |
| Scryer | Modern Rust implementation |

## Conversion Notes

- Backtracking → generators or search algorithms
- Unification → pattern matching (limited)
- Logic variables → explicit state threading
- Cut → explicit control flow
- DCGs → parser combinators
- Fundamentally different paradigm - often requires redesign

## Sources

- [SWI-Prolog Documentation](https://www.swi-prolog.org/pldoc/)
- [ISO Prolog Standard](https://www.iso.org/standard/21413.html)
- [Learn Prolog Now](http://www.learnprolognow.org/)
