# Conversion Difficulty Matrix

Single source of truth for language pair conversion difficulty ratings.

> **Referenced by:**
> - `create-lang-conversion-skill.md` (Step 3.5)
> - `meta-convert-dev/SKILL.md`
> - `meta-convert-guide/SKILL.md`

---

## Rating Framework

### Factors (0-2 points each)

| Factor | Easy (+0) | Medium (+1) | Hard (+2) |
|--------|-----------|-------------|-----------|
| **Type System** | Both static or both dynamic | Mixed static/dynamic | Opposite philosophies (e.g., gradual→strict) |
| **Paradigm** | Same paradigm | Related paradigms | Opposite paradigms (OOP↔Pure FP) |
| **Memory Model** | Both GC or both manual | Different GC strategies | GC ↔ Ownership/Manual |
| **Concurrency** | Same model | Related models | Fundamentally different (Actors↔Threads) |
| **Platform** | Same runtime | Related runtimes | Different platforms (JVM↔Native) |

### Difficulty Levels

| Total Score | Level | Expected Skill Size | Focus Areas |
|-------------|-------|---------------------|-------------|
| 0-2 | **Easy** | 200-400 lines | Idiom differences, library mapping |
| 3-5 | **Medium** | 400-800 lines | Type translation, paradigm shifts |
| 6-8 | **Hard** | 800-1200 lines | Memory model, concurrency, architecture |
| 9-10 | **Expert** | 1200+ lines | Complete paradigm shift, all factors differ |

---

## Language Characteristics

| Language | Type | Paradigm | Memory | Concurrency | Platform |
|----------|------|----------|--------|-------------|----------|
| C | Static | Imperative | Manual | Threads | Native |
| C++ | Static | Multi (OOP) | Manual/RAII | Threads | Native |
| Clojure | Dynamic | Functional | GC | STM/Agents | JVM |
| Elixir | Dynamic | Functional | GC | Actors | BEAM |
| Elm | Static | Pure FP | GC | TEA/Messages | JS |
| Erlang | Dynamic | Functional | GC | Actors | BEAM |
| F# | Static | Functional | GC | Async | .NET |
| Go | Static | Imperative | GC | CSP | Native |
| Haskell | Static | Pure FP | GC | STM/Async | Native |
| Java | Static | OOP | GC | Threads | JVM |
| Obj-C | Static | OOP | ARC | GCD | Apple |
| Python | Dynamic | Multi | GC | Async/Threads | Interpreted |
| Roc | Static | Pure FP | GC | Effects | Native |
| Rust | Static | Multi | Ownership | Async/Threads | Native |
| Scala | Static | Multi (FP/OOP) | GC | Actors/Async | JVM |
| Swift | Static | Multi | ARC | GCD/Async | Apple |
| TypeScript | Static | Multi | GC | Promises | JS |

---

## Complete Difficulty Ratings

### Functional Language Family

Languages: Clojure, Elixir, Elm, Erlang, F#, Haskell, Roc, Scala

| Pair | Type | Paradigm | Memory | Concurrency | Platform | **Total** | **Level** |
|------|------|----------|--------|-------------|----------|-----------|-----------|
| clojure-elixir | +1 | +0 | +0 | +1 | +2 | **4** | Medium |
| clojure-elm | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| clojure-erlang | +1 | +0 | +0 | +1 | +2 | **4** | Medium |
| clojure-fsharp | +1 | +0 | +0 | +1 | +2 | **4** | Medium |
| clojure-haskell | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| clojure-roc | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| clojure-scala | +0 | +0 | +0 | +1 | +0 | **1** | Easy |
| elixir-clojure | +1 | +0 | +0 | +1 | +2 | **4** | Medium |
| elixir-elm | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| elixir-erlang | +0 | +0 | +0 | +0 | +0 | **0** | Easy |
| elixir-fsharp | +1 | +0 | +0 | +1 | +2 | **4** | Medium |
| elixir-haskell | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| elixir-roc | +1 | +1 | +0 | +2 | +2 | **6** | Hard |
| elixir-scala | +1 | +0 | +0 | +1 | +2 | **4** | Medium |
| elm-clojure | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| elm-elixir | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| elm-erlang | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| elm-fsharp | +0 | +0 | +0 | +1 | +2 | **3** | Medium |
| elm-haskell | +0 | +0 | +0 | +1 | +2 | **3** | Medium |
| elm-roc | +0 | +0 | +0 | +0 | +2 | **2** | Easy |
| elm-scala | +0 | +1 | +0 | +1 | +2 | **4** | Medium |
| erlang-clojure | +1 | +0 | +0 | +1 | +2 | **4** | Medium |
| erlang-elixir | +0 | +0 | +0 | +0 | +0 | **0** | Easy |
| erlang-elm | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| erlang-fsharp | +1 | +0 | +0 | +1 | +2 | **4** | Medium |
| erlang-haskell | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| erlang-roc | +1 | +1 | +0 | +2 | +2 | **6** | Hard |
| erlang-scala | +1 | +0 | +0 | +1 | +2 | **4** | Medium |
| fsharp-clojure | +1 | +0 | +0 | +1 | +2 | **4** | Medium |
| fsharp-elixir | +1 | +0 | +0 | +1 | +2 | **4** | Medium |
| fsharp-elm | +0 | +0 | +0 | +1 | +2 | **3** | Medium |
| fsharp-erlang | +1 | +0 | +0 | +1 | +2 | **4** | Medium |
| fsharp-haskell | +0 | +0 | +0 | +1 | +2 | **3** | Medium |
| fsharp-roc | +0 | +0 | +0 | +1 | +2 | **3** | Medium |
| fsharp-scala | +0 | +0 | +0 | +1 | +2 | **3** | Medium |
| haskell-clojure | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| haskell-elixir | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| haskell-elm | +0 | +0 | +0 | +1 | +2 | **3** | Medium |
| haskell-erlang | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| haskell-fsharp | +0 | +0 | +0 | +1 | +2 | **3** | Medium |
| haskell-roc | +0 | +0 | +0 | +1 | +0 | **1** | Easy |
| haskell-scala | +0 | +1 | +0 | +1 | +2 | **4** | Medium |
| roc-clojure | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| roc-elixir | +1 | +1 | +0 | +2 | +2 | **6** | Hard |
| roc-elm | +0 | +0 | +0 | +0 | +2 | **2** | Easy |
| roc-erlang | +1 | +1 | +0 | +2 | +2 | **6** | Hard |
| roc-fsharp | +0 | +0 | +0 | +1 | +2 | **3** | Medium |
| roc-haskell | +0 | +0 | +0 | +1 | +0 | **1** | Easy |
| roc-scala | +0 | +1 | +0 | +1 | +2 | **4** | Medium |
| scala-clojure | +0 | +0 | +0 | +1 | +0 | **1** | Easy |
| scala-elixir | +1 | +0 | +0 | +1 | +2 | **4** | Medium |
| scala-elm | +0 | +1 | +0 | +1 | +2 | **4** | Medium |
| scala-erlang | +1 | +0 | +0 | +1 | +2 | **4** | Medium |
| scala-fsharp | +0 | +0 | +0 | +1 | +2 | **3** | Medium |
| scala-haskell | +0 | +1 | +0 | +1 | +2 | **4** | Medium |
| scala-roc | +0 | +1 | +0 | +1 | +2 | **4** | Medium |

### Python Conversions

| Pair | Type | Paradigm | Memory | Concurrency | Platform | **Total** | **Level** |
|------|------|----------|--------|-------------|----------|-----------|-----------|
| python-clojure | +0 | +1 | +0 | +1 | +2 | **4** | Medium |
| python-elixir | +0 | +1 | +0 | +2 | +2 | **5** | Medium |
| python-elm | +1 | +2 | +0 | +1 | +2 | **6** | Hard |
| python-erlang | +0 | +1 | +0 | +2 | +2 | **5** | Medium |
| python-fsharp | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| python-golang | +1 | +0 | +0 | +1 | +2 | **4** | Medium |
| python-haskell | +1 | +2 | +0 | +1 | +2 | **6** | Hard |
| python-roc | +1 | +2 | +0 | +1 | +2 | **6** | Hard |
| python-rust | +1 | +1 | +2 | +1 | +2 | **7** | Hard |
| python-scala | +1 | +1 | +0 | +1 | +2 | **5** | Medium |
| python-typescript | +0 | +0 | +0 | +0 | +1 | **1** | Easy |

### TypeScript Conversions

| Pair | Type | Paradigm | Memory | Concurrency | Platform | **Total** | **Level** |
|------|------|----------|--------|-------------|----------|-----------|-----------|
| typescript-golang | +0 | +1 | +0 | +1 | +2 | **4** | Medium |
| typescript-python | +0 | +0 | +0 | +0 | +1 | **1** | Easy |
| typescript-rust | +0 | +1 | +2 | +1 | +2 | **6** | Hard |

### Systems Language Conversions

| Pair | Type | Paradigm | Memory | Concurrency | Platform | **Total** | **Level** |
|------|------|----------|--------|-------------|----------|-----------|-----------|
| c-cpp | +0 | +0 | +0 | +0 | +0 | **0** | Easy |
| c-rust | +0 | +1 | +1 | +1 | +0 | **3** | Medium |
| cpp-rust | +0 | +0 | +1 | +0 | +0 | **1** | Easy |
| golang-rust | +0 | +0 | +2 | +1 | +0 | **3** | Medium |
| java-c | +0 | +1 | +2 | +1 | +2 | **6** | Hard |
| java-cpp | +0 | +0 | +2 | +0 | +2 | **4** | Medium |
| java-rust | +0 | +1 | +2 | +1 | +2 | **6** | Hard |

### Platform-Specific

| Pair | Type | Paradigm | Memory | Concurrency | Platform | **Total** | **Level** |
|------|------|----------|--------|-------------|----------|-----------|-----------|
| objc-swift | +0 | +0 | +0 | +0 | +0 | **0** | Easy |

---

## Summary by Difficulty Level

### Easy (0-2 points) - 10 pairs

| Pair | Score | Notes |
|------|-------|-------|
| c-cpp | 0 | Same family |
| elixir-erlang | 0 | Same platform (BEAM) |
| erlang-elixir | 0 | Same platform (BEAM) |
| objc-swift | 0 | Same platform (Apple) |
| clojure-scala | 1 | Same platform (JVM) |
| cpp-rust | 1 | Similar memory models |
| haskell-roc | 1 | Similar pure FP |
| python-typescript | 1 | Similar multi-paradigm |
| roc-haskell | 1 | Similar pure FP |
| scala-clojure | 1 | Same platform (JVM) |
| typescript-python | 1 | Similar multi-paradigm |
| elm-roc | 2 | Both pure FP |
| roc-elm | 2 | Both pure FP |

### Medium (3-5 points) - 47 pairs

Most functional↔functional conversions fall here. Key challenges:
- Platform differences (JVM↔BEAM↔.NET↔Native)
- Concurrency model translation (Actors↔STM↔Async)
- Type system differences (static↔dynamic)

### Hard (6-8 points) - 18 pairs

| Pair | Score | Key Challenges |
|------|-------|----------------|
| python-rust | 7 | GC→Ownership, dynamic→static |
| python-elm | 6 | Multi→Pure FP, architecture shift |
| python-haskell | 6 | Multi→Pure FP, type system |
| python-roc | 6 | Multi→Pure FP, platform |
| typescript-rust | 6 | GC→Ownership, platform |
| java-c | 6 | GC→Manual, platform |
| java-rust | 6 | GC→Ownership, platform |
| elixir-roc | 6 | Actors→Effects, BEAM→Native |
| erlang-roc | 6 | Actors→Effects, BEAM→Native |
| roc-elixir | 6 | Effects→Actors, Native→BEAM |
| roc-erlang | 6 | Effects→Actors, Native→BEAM |

### Expert (9-10 points) - 0 pairs

No current pairs reach expert level. Would require:
- Dynamic OOP → Static Pure FP with ownership
- Example: Python → a hypothetical pure FP + ownership language

---

## Usage

### In create-lang-conversion-skill.md

```markdown
> **See:** [meta-convert-guide/reference/difficulty-matrix.md](../skills/meta-convert-guide/reference/difficulty-matrix.md) for pre-calculated difficulty ratings.
```

### In Skill SKILL.md

```markdown
## Difficulty Assessment

**Rating:** Hard (6/10)

See [difficulty-matrix.md](../../meta-convert-guide/reference/difficulty-matrix.md) for methodology.
```

### Updating This Matrix

When adding a new conversion skill:
1. Calculate score using the Rating Framework above
2. Add entry to the appropriate section
3. Update summary tables if needed
