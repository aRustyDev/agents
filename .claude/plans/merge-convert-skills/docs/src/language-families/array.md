# Array Programming Family

> Languages where operations implicitly apply to entire arrays, emphasizing concise notation.

## Overview

Array languages feature:

- **Implicit iteration** - Operations apply element-wise
- **Rank polymorphism** - Functions work on any dimension
- **Concise notation** - Dense symbolic syntax
- **Mathematical focus** - Linear algebra, data analysis
- **Interactive** - REPL-driven exploration

## Languages

| Language | Notes |
|----------|-------|
| APL | Original (1966), special character set |
| J | ASCII APL descendant, tacit programming |
| K | Terse, finance-focused |
| BQN | Modern APL, first-class functions |
| NumPy | Python array library (inspired by APL) |

## Key Concepts

### Implicit Iteration

```apl
⍝ APL: add arrays element-wise
1 2 3 + 4 5 6    ⍝ → 5 7 9

⍝ Scalar extends to array
10 + 1 2 3       ⍝ → 11 12 13

⍝ Reduce with function
+/ 1 2 3 4 5     ⍝ → 15 (sum)
```

```j
NB. J equivalent
1 2 3 + 4 5 6    NB. 5 7 9
+/ 1 2 3 4 5     NB. 15
```

### Rank Polymorphism

```apl
⍝ Same function works on different ranks
2 × 3            ⍝ Scalar × Scalar → 6
2 × 1 2 3        ⍝ Scalar × Vector → 2 4 6
(2 2⍴1 2 3 4) × 2 ⍝ Matrix × Scalar → 2×2 matrix
```

### Tacit (Point-Free) Style

```j
NB. J: Define function without mentioning arguments
average =: +/ % #    NB. sum divided by count
average 1 2 3 4 5    NB. 3
```

## Conversion Considerations

### Converting FROM Array

**What's hard:**

- Implicit iteration → explicit loops
- Rank polymorphism → overloads or generics
- Tacit style → explicit arguments
- Dense notation → verbose equivalent

### Converting TO Array

**What maps well:**

- Numerical algorithms
- Data transformations
- Matrix operations

**What's awkward:**

- Object-oriented code
- Control flow-heavy code
- String manipulation

## Modern Relevance

Array concepts appear in:

- **NumPy/PyTorch** - Broadcasting
- **R** - Vectorized operations
- **MATLAB** - Matrix operations
- **Julia** - Broadcasting with `.`

```python
# NumPy broadcasting (APL-inspired)
import numpy as np
a = np.array([1, 2, 3])
b = np.array([[1], [2], [3]])
a + b  # 3×3 result via broadcasting
```

## Sources

- [APL Wiki](https://aplwiki.com/)
- [J Documentation](https://www.jsoftware.com/help/learning/contents.htm)
- [BQN Documentation](https://mlochbaum.github.io/BQN/)
- [A History of APL](https://www.jsoftware.com/papers/APL.htm)

## See Also

- [ML-FP](ml-fp.md) - Functional composition
- [Overview](overview.md) - Comparison matrices
