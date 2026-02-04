# Bidirectional Merge Analysis

Analysis of bidirectional convert-* skill pairs and merge recommendations.

## Summary

- **Initial state**: 78 convert-* skills
- **Bidirectional pairs identified**: 29 pairs (58 skills)
- **After merge**: 49 skills
- **Reduction**: 37%

## Methodology

Used semantic embeddings (nomic-embed-text) to compute cosine similarity between skill centroids. Pairs with similarity > 0.85 were flagged as potential bidirectional candidates.

## Bidirectional Pairs

| Keep | Delete | Similarity |
|------|--------|------------|
| convert-c-cpp | convert-cpp-c | 0.987 |
| convert-python-clojure | convert-clojure-python | 0.973 |
| convert-csharp-fsharp | convert-fsharp-csharp | 0.971 |
| convert-erlang-elixir | convert-elixir-erlang | 0.968 |
| convert-java-kotlin | convert-kotlin-java | 0.966 |
| convert-haskell-elm | convert-elm-haskell | 0.960 |
| convert-java-scala | convert-scala-java | 0.958 |
| convert-python-elm | convert-elm-python | 0.954 |
| convert-python-erlang | convert-erlang-python | 0.952 |
| convert-golang-rust | convert-rust-golang | 0.951 |
| convert-python-elixir | convert-elixir-python | 0.950 |
| convert-python-haskell | convert-haskell-python | 0.948 |
| convert-objc-swift | convert-swift-objc | 0.945 |
| convert-cpp-rust | convert-rust-cpp | 0.942 |
| convert-javascript-typescript | convert-typescript-javascript | 0.940 |
| convert-python-ocaml | convert-ocaml-python | 0.938 |
| convert-python-fsharp | convert-fsharp-python | 0.936 |
| convert-c-rust | convert-rust-c | 0.932 |
| convert-python-typescript | convert-typescript-python | 0.928 |
| convert-python-roc | convert-roc-python | 0.925 |
| convert-python-rust | convert-rust-python | 0.922 |
| convert-python-scala | convert-scala-python | 0.918 |
| convert-python-golang | convert-golang-python | 0.915 |
| convert-python-gleam | convert-gleam-python | 0.912 |
| convert-python-java | convert-java-python | 0.908 |
| convert-python-swift | convert-swift-python | 0.905 |
| convert-python-kotlin | convert-kotlin-python | 0.902 |
| convert-python-cpp | convert-cpp-python | 0.898 |
| convert-python-c | convert-c-python | 0.885 |

## Merge Strategy

For each pair:

1. Keep the skill with the more common source language (Python preferred)
2. Update skill metadata to indicate bidirectional capability
3. Ensure content covers both directions
4. Delete the reverse skill

## Results

See [Post-Merge State](post-merge-state.md) for analysis of the 49 remaining skills.
