# Logic Programming Family

> Languages based on formal logic where programs are logical statements and execution is inference.

## Overview

Logic programming represents computation as logical inference:

- **Declarative** - Describe what, not how
- **Unification** - Pattern matching + variable binding
- **Backtracking** - Automatic search through solution space
- **Relations** - Define relationships, query both directions
- **Database queries** - Natural for relational data

## Languages

| Language | Notes |
|----------|-------|
| Prolog | Original logic language, SLD resolution |
| Datalog | Restricted Prolog, database-focused |
| Mercury | Typed logic language with modes |
| miniKanren | Embedded logic DSL (in Scheme, Clojure, etc.) |

## Key Concepts

### Facts and Rules

```prolog
% Facts
parent(tom, bob).
parent(tom, liz).
parent(bob, ann).

% Rules
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.

% Queries
?- grandparent(tom, ann).  % true
?- grandparent(tom, Who).  % Who = ann
```

### Unification

```prolog
% Pattern matching + variable binding
append([], L, L).
append([H|T], L, [H|R]) :- append(T, L, R).

?- append([1,2], [3,4], X).  % X = [1,2,3,4]
?- append(X, [3,4], [1,2,3,4]).  % X = [1,2]
```

### Backtracking

```prolog
% Multiple solutions via backtracking
member(X, [X|_]).
member(X, [_|T]) :- member(X, T).

?- member(X, [1,2,3]).  % X = 1; X = 2; X = 3
```

## Conversion Considerations

### Converting FROM Logic

**What's hard:**

- Backtracking → explicit search/iteration
- Unification → pattern matching + equality
- Relations → functions (lose bidirectionality)
- Cut (!) → control flow restructuring

### Converting TO Logic

**What maps well:**

- Search problems
- Constraint satisfaction
- Database queries
- Rule-based systems

**What's awkward:**

- Imperative algorithms
- IO-heavy code
- Performance-critical code

## Sources

- [Learn Prolog Now!](https://www.learnprolognow.org/)
- [The Art of Prolog](https://mitpress.mit.edu/9780262691635/)
- [Datalog Educational System](https://www.des.sourceforge.io/)

## See Also

- [ML-FP](ml-fp.md) - Pattern matching similarity
- [Overview](overview.md) - Comparison matrices
