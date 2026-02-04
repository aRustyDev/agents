# Post-Merge State Analysis

Analysis of the 49 convert-* skills remaining after bidirectional merge.

## Summary

- **Total skills**: 49
- **Unidirectional**: 20
- **Bidirectional**: 29

## Source Language Distribution

| Language | Count | Skills |
|----------|-------|--------|
| Python | 11 | Universal source for most target languages |
| C | 2 | convert-c-cpp, convert-c-rust |
| Java | 2 | convert-java-kotlin, convert-java-scala |
| C# | 1 | convert-csharp-fsharp |
| Erlang | 1 | convert-erlang-elixir |
| Haskell | 1 | convert-haskell-elm |
| Go | 1 | convert-golang-rust |
| C++ | 1 | convert-cpp-rust |
| JS | 1 | convert-javascript-typescript |
| Obj-C | 1 | convert-objc-swift |

## Target Language Distribution

| Language | As Target | Skills |
|----------|-----------|--------|
| Rust | 6 | Popular target for systems/ML-FP |
| Roc | 6 | Emerging ML-FP target |
| Scala | 8 | Universal JVM target |
| Clojure | 3 | LISP target |
| Erlang | 3 | BEAM target |
| Elixir | 3 | BEAM target |
| Gleam | 2 | Emerging BEAM target |

## Language Families Represented

### ML-FP Family
- Haskell, Elm, OCaml, F#, Roc, Scala

### BEAM Family
- Erlang, Elixir, Gleam

### Systems Family
- C, C++, Rust, Go, Zig

### Managed OOP Family
- Java, Kotlin, C#

### Dynamic Family
- Python, JavaScript/TypeScript, Ruby

### Apple Family
- Objective-C, Swift

## Coverage Gaps Identified

### Missing Conversion Directions
- No rust→anything (Rust only as target)
- No scala→anything (Scala only as target)
- No roc→anything (Roc only as target)

### Missing Language Pairs
- No Ruby conversions
- No PHP conversions
- Limited cross-family coverage

## Target Similarity Analysis

Languages with high target similarity (can share synthesis templates):

| Target | Avg Similarity | Notes |
|--------|----------------|-------|
| Clojure | 0.852 | Consistent LISP target |
| Erlang | 0.839 | Consistent BEAM target |
| Scala | 0.822 | Consistent JVM target |
| Rust | 0.798 | More variance due to ownership |

## Cross-Family Conversion Coverage

| From Family | To Family | Count |
|-------------|-----------|-------|
| Dynamic | ML-FP | 8 |
| Dynamic | Systems | 5 |
| Dynamic | BEAM | 3 |
| Dynamic | Managed | 2 |
| Systems | Systems | 4 |
| ML-FP | ML-FP | 3 |
| Managed | ML-FP | 2 |
| BEAM | BEAM | 1 |

## Recommendations

1. **IR Design**: Focus on Dynamic → ML-FP conversions (most common)
2. **Template Sharing**: Group targets by similarity for synthesis templates
3. **Future Skills**: Add rust→python, scala→python for round-trip support
4. **Family Coverage**: Expand BEAM and Systems family coverage
