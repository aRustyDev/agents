# Coverage Gap Analysis for convert-* Skills

**Task:** ai-p28.14
**Generated:** 2026-02-04
**Status:** Complete

## Executive Summary

This analysis examines the 49 existing convert-* skills to identify coverage gaps and prioritize future development. The current skill set provides **18.0% coverage** of Tier 1 language pairs, with significant clustering around Python as a source language and functional programming languages as targets.

---

## 1. Coverage Matrix

### 1.1 Tier 1 Languages (17 total)

Legend:
- Check: Skill exists
- X: No skill (gap)
- --: Same language (N/A)

| Source | c | clojure | cpp | elixir | elm | erlang | fsharp | golang | haskell | java | objc | python | roc | rust | scala | swift | typescript |
|--------|---|---------|-----|--------|-----|--------|--------|--------|---------|------|------|--------|-----|------|-------|-------|------------|
| **c** | -- | X | Check | X | X | X | X | X | X | X | X | X | X | Check | X | X | X |
| **clojure** | X | -- | X | Check | Check | Check | Check | X | Check | X | X | X | Check | X | Check | X | X |
| **cpp** | X | X | -- | X | X | X | X | X | X | X | X | X | X | Check | X | X | X |
| **elixir** | X | X | X | -- | Check | Check | Check | X | Check | X | X | X | Check | X | Check | X | X |
| **elm** | X | X | X | X | -- | Check | Check | X | Check | X | X | X | Check | X | Check | X | X |
| **erlang** | X | X | X | X | X | -- | Check | X | Check | X | X | X | Check | X | Check | X | X |
| **fsharp** | X | X | X | X | X | X | -- | X | Check | X | X | X | Check | X | Check | X | X |
| **golang** | X | X | X | X | X | X | X | -- | X | X | X | X | X | Check | X | X | X |
| **haskell** | X | X | X | X | X | X | X | X | -- | X | X | X | Check | X | Check | X | X |
| **java** | Check | X | Check | X | X | X | X | X | X | -- | X | X | X | Check | X | X | X |
| **objc** | X | X | X | X | X | X | X | X | X | X | -- | X | X | X | X | Check | X |
| **python** | X | Check | X | Check | Check | Check | Check | Check | Check | X | X | -- | Check | Check | Check | X | Check |
| **roc** | X | X | X | X | X | X | X | X | X | X | X | X | -- | X | Check | X | X |
| **rust** | X | X | X | X | X | X | X | X | X | X | X | X | X | -- | X | X | X |
| **scala** | X | X | X | X | X | X | X | X | X | X | X | X | X | X | -- | X | X |
| **swift** | X | X | X | X | X | X | X | X | X | X | X | X | X | X | X | -- | X |
| **typescript** | X | X | X | X | X | X | X | Check | X | X | X | X | X | Check | X | X | -- |

### 1.2 Visual Summary by Family

```
                          TARGET LANGUAGES
                   Dynamic     ML-FP        Systems       BEAM        Lisp    Managed  Apple
                   py  ts     sc  hs  ro  fs  elm   ru  c   c++ go   el  er    clj      ja    sw  ob
SOURCE  Dynamic    --  --
        python     --  Y      Y   Y   Y   Y   Y     Y   -   -   Y    Y   Y     Y        -     -   -
        typescript -   --     -   -   -   -   -     Y   -   -   Y    -   -     -        -     -   -

        ML-FP
        scala      -   -      --  -   -   -   -     -   -   -   -    -   -     -        -     -   -
        haskell    -   -      Y   --  Y   -   -     -   -   -   -    -   -     -        -     -   -
        roc        -   -      Y   -   --  -   -     -   -   -   -    -   -     -        -     -   -
        fsharp     -   -      Y   Y   Y   --  -     -   -   -   -    -   -     -        -     -   -
        elm        -   -      Y   Y   Y   Y   --    -   -   -   -    -   Y     -        -     -   -

        Systems
        rust       -   -      -   -   -   -   -     --  -   -   -    -   -     -        -     -   -
        c          -   -      -   -   -   -   -     Y   --  Y   -    -   -     -        -     -   -
        cpp        -   -      -   -   -   -   -     Y   -   --  -    -   -     -        -     -   -
        golang     -   -      -   -   -   -   -     Y   -   -   --   -   -     -        -     -   -

        BEAM
        elixir     -   -      Y   Y   Y   Y   Y     -   -   -   -    --  Y     -        -     -   -
        erlang     -   -      Y   Y   Y   Y   -     -   -   -   -    -   --    -        -     -   -

        Lisp
        clojure    -   -      Y   Y   Y   Y   Y     -   -   -   -    Y   Y     --       -     -   -

        Managed
        java       -   -      -   -   -   -   -     Y   Y   Y   -    -   -     -        --    -   -

        Apple
        swift      -   -      -   -   -   -   -     -   -   -   -    -   -     -        -     --  -
        objc       -   -      -   -   -   -   -     -   -   -   -    -   -     -        -     Y   --
```

---

## 2. Statistics Summary

### 2.1 Overall Metrics

| Metric | Value |
|--------|-------|
| **Total existing skills** | 49 |
| **Tier 1 languages** | 17 |
| **Tier 1 possible pairs** | 272 (17 x 16) |
| **Tier 1 existing pairs** | 49 |
| **Tier 1 coverage** | 18.0% |
| **Missing Tier 1 pairs** | 223 |
| **Bidirectional pairs** | 0 |

### 2.2 Source Language Distribution

Languages used as SOURCE in existing skills:

| Language | Skills as Source | Percentage |
|----------|------------------|------------|
| python | 11 | 22.4% |
| clojure | 7 | 14.3% |
| elixir | 6 | 12.2% |
| elm | 5 | 10.2% |
| erlang | 4 | 8.2% |
| fsharp | 3 | 6.1% |
| java | 3 | 6.1% |
| c | 2 | 4.1% |
| haskell | 2 | 4.1% |
| typescript | 2 | 4.1% |
| cpp | 1 | 2.0% |
| golang | 1 | 2.0% |
| objc | 1 | 2.0% |
| roc | 1 | 2.0% |

**Not used as source (0 skills):** rust, scala, swift

### 2.3 Target Language Distribution

Languages used as TARGET in existing skills:

| Language | Skills as Target | Percentage |
|----------|------------------|------------|
| scala | 8 | 16.3% |
| roc | 7 | 14.3% |
| rust | 6 | 12.2% |
| haskell | 6 | 12.2% |
| fsharp | 5 | 10.2% |
| elm | 3 | 6.1% |
| erlang | 4 | 8.2% |
| elixir | 2 | 4.1% |
| golang | 2 | 4.1% |
| cpp | 2 | 4.1% |
| c | 1 | 2.0% |
| clojure | 1 | 2.0% |
| swift | 1 | 2.0% |
| typescript | 1 | 2.0% |

**Not used as target (0 skills):** java, objc, python

### 2.4 Family Coverage Analysis

| Source Family | Target Family | Skill Count | Potential |
|---------------|---------------|-------------|-----------|
| dynamic -> ml_fp | 10 | 20 | 50% |
| lisp -> ml_fp | 5 | 5 | 100% |
| beam -> ml_fp | 10 | 10 | 100% |
| ml_fp -> ml_fp | 9 | 20 | 45% |
| dynamic -> systems | 4 | 16 | 25% |
| systems -> systems | 4 | 12 | 33% |
| managed_oop -> systems | 3 | 4 | 75% |
| dynamic -> beam | 2 | 4 | 50% |
| lisp -> beam | 2 | 2 | 100% |
| dynamic -> lisp | 1 | 2 | 50% |
| apple -> apple | 1 | 2 | 50% |

---

## 3. Gap Analysis

### 3.1 Bidirectional Coverage

**Current state:** No bidirectional pairs exist.

All 49 skills are unidirectional. This means if `convert-python-scala` exists, there is no `convert-scala-python`.

**Impact:** Users converting in the "reverse" direction must manually adapt patterns, or use the meta-convert methodology.

### 3.2 High-Value Missing Pairs (Tier 1 <-> Tier 1)

Priority 1: **Same-family gaps** (highest value, lowest implementation effort)

| Missing Pair | Family | Notes |
|--------------|--------|-------|
| scala -> haskell | ml_fp | Reverse of haskell -> scala |
| scala -> roc | ml_fp | Reverse of roc -> scala |
| scala -> fsharp | ml_fp | Reverse of fsharp -> scala |
| scala -> elm | ml_fp | Reverse of elm -> scala |
| haskell -> fsharp | ml_fp | Within ML-FP family |
| haskell -> elm | ml_fp | Within ML-FP family |
| roc -> haskell | ml_fp | Reverse of haskell -> roc |
| roc -> fsharp | ml_fp | Reverse of fsharp -> roc |
| roc -> elm | ml_fp | Within ML-FP family |
| fsharp -> elm | ml_fp | Within ML-FP family |
| elm -> fsharp | ml_fp | Reverse of fsharp -> elm exists? No |
| rust -> c | systems | Reverse of c -> rust |
| rust -> cpp | systems | Reverse of cpp -> rust |
| rust -> golang | systems | Reverse of golang -> rust |
| cpp -> c | systems | Reverse of c -> cpp |
| c -> golang | systems | Within systems family |
| golang -> c | systems | Within systems family |
| golang -> cpp | systems | Within systems family |
| elixir -> erlang | beam | Exists! |
| erlang -> elixir | beam | Reverse needed |
| swift -> objc | apple | Reverse of objc -> swift |

Priority 2: **High-traffic cross-family gaps**

| Missing Pair | Src Family | Tgt Family | Rationale |
|--------------|------------|------------|-----------|
| typescript -> scala | dynamic | ml_fp | Web to FP migration |
| typescript -> haskell | dynamic | ml_fp | Web to FP migration |
| typescript -> python | dynamic | dynamic | JS ecosystem to Python |
| python -> java | dynamic | managed_oop | Enterprise migration |
| python -> swift | dynamic | apple | Mobile development |
| scala -> python | ml_fp | dynamic | Data science access |
| haskell -> python | ml_fp | dynamic | Prototype/scripting |
| rust -> python | systems | dynamic | Python extensions |
| rust -> typescript | systems | dynamic | WASM interop |
| java -> scala | managed_oop | ml_fp | JVM FP migration |
| java -> python | managed_oop | dynamic | Enterprise to data science |
| java -> typescript | managed_oop | dynamic | Backend to fullstack |
| kotlin -> java | managed_oop | managed_oop | Interop (Tier 2) |
| gleam -> elixir | beam | beam | BEAM typed/untyped (Tier 2) |

### 3.3 Coverage by Language Family

**Well-covered directions:**
- Python -> (anything): 11 skills cover most Tier 1 targets
- (FP languages) -> Scala: Scala is the most common target
- BEAM family -> ML-FP family: Strong coverage
- Lisp -> ML-FP family: Complete coverage

**Poorly-covered directions:**
- (anything) -> Python: No skills (Python is never a target)
- (anything) -> Java: No skills (Java is never a target)
- Rust as source: No skills (Rust is only a target)
- Scala as source: No skills (Scala is only a target)
- Swift as source: No skills (Swift is only a target)

### 3.4 Zero-Coverage Languages

These Tier 1 languages have NO outgoing skills:
- **rust** (0 as source, 6 as target)
- **scala** (0 as source, 8 as target)
- **swift** (0 as source, 1 as target)

These Tier 1 languages have NO incoming skills:
- **python** (11 as source, 0 as target)
- **java** (3 as source, 0 as target)
- **objc** (1 as source, 0 as target)

---

## 4. Recommendations

### 4.1 Immediate Priorities (P0)

Create reverse skills for the most-used targets to enable bidirectional conversion:

1. **scala -> python** - Reverse the most common conversion path
2. **rust -> python** - Enable Python extension patterns
3. **haskell -> python** - Complete the FP <-> dynamic bridge
4. **scala -> typescript** - Enable web targeting from FP

### 4.2 High Priority (P1)

Complete intra-family coverage:

1. **Systems family completion:**
   - rust -> c, rust -> cpp, rust -> golang
   - cpp -> c, c -> golang, golang -> cpp

2. **ML-FP family completion:**
   - scala -> haskell, scala -> fsharp, scala -> elm
   - haskell -> fsharp, haskell -> elm
   - roc -> haskell, roc -> fsharp

3. **BEAM family completion:**
   - erlang -> elixir (reverse exists)

4. **Apple family completion:**
   - swift -> objc (reverse exists)

### 4.3 Medium Priority (P2)

High-value cross-family pairs:

1. **Enterprise migration paths:**
   - java -> scala, java -> python, java -> typescript
   - python -> java

2. **Modern web paths:**
   - typescript -> scala, typescript -> haskell, typescript -> rust

3. **Mobile paths:**
   - python -> swift, swift -> kotlin (Tier 2)

### 4.4 Patterns for IR Sharing

The following groups can share common IR transformation patterns:

**Group 1: ML-FP Mutual Conversion**
- Languages: scala, haskell, fsharp, elm, roc
- Pattern: All have ADTs, pattern matching, immutability
- Recommendation: Build bidirectional IR for all 20 combinations

**Group 2: Systems Mutual Conversion**
- Languages: rust, c, cpp, golang, zig
- Pattern: Manual memory or GC, pointers/references, low-level control
- Recommendation: Share memory model IR, pointer semantics

**Group 3: BEAM Mutual Conversion**
- Languages: elixir, erlang, gleam
- Pattern: Actor model, supervision, hot code reload
- Recommendation: Share OTP pattern IR

**Group 4: Dynamic <-> Typed Bridge**
- Languages: python <-> typescript, python <-> scala
- Pattern: Type annotation to type enforcement
- Recommendation: Share gradual typing IR patterns

### 4.5 Tier 2 Expansion Recommendations

When Tier 1 coverage reaches 50%, consider:

1. **javascript** - Critical for web ecosystem (currently absent)
2. **kotlin** - Android/JVM alternative to Java
3. **gleam** - Typed BEAM alternative
4. **ruby** - Rails ecosystem
5. **zig** - Systems programming alternative

---

## 5. Data Sources

This analysis was generated from:

| Source | Location |
|--------|----------|
| Existing skills | `/context/skills/convert-*` (49 directories) |
| Language tiers | `/data/language-tiers.yaml` |
| Gap analysis | `/data/gap-analysis.json` |
| Pattern data | `/data/patterns.db` |

---

## 6. Appendix: Complete Gap List

### 6.1 Missing Tier 1 Pairs (223 total)

<details>
<summary>Click to expand full list</summary>

**From c (14 missing):**
- c -> clojure, c -> elixir, c -> elm, c -> erlang, c -> fsharp
- c -> golang, c -> haskell, c -> java, c -> objc, c -> python
- c -> roc, c -> scala, c -> swift, c -> typescript

**From clojure (10 missing):**
- clojure -> c, clojure -> cpp, clojure -> golang, clojure -> java
- clojure -> objc, clojure -> python, clojure -> rust, clojure -> swift
- clojure -> typescript

**From cpp (15 missing):**
- cpp -> c, cpp -> clojure, cpp -> elixir, cpp -> elm, cpp -> erlang
- cpp -> fsharp, cpp -> golang, cpp -> haskell, cpp -> java, cpp -> objc
- cpp -> python, cpp -> roc, cpp -> scala, cpp -> swift, cpp -> typescript

**From elixir (10 missing):**
- elixir -> c, elixir -> clojure, elixir -> cpp, elixir -> golang
- elixir -> java, elixir -> objc, elixir -> python, elixir -> rust
- elixir -> swift, elixir -> typescript

**From elm (11 missing):**
- elm -> c, elm -> clojure, elm -> cpp, elm -> elixir, elm -> golang
- elm -> java, elm -> objc, elm -> python, elm -> rust, elm -> swift
- elm -> typescript

**From erlang (11 missing):**
- erlang -> c, erlang -> clojure, erlang -> cpp, erlang -> elixir
- erlang -> elm, erlang -> golang, erlang -> java, erlang -> objc
- erlang -> python, erlang -> rust, erlang -> swift, erlang -> typescript

**From fsharp (11 missing):**
- fsharp -> c, fsharp -> clojure, fsharp -> cpp, fsharp -> elixir
- fsharp -> elm, fsharp -> erlang, fsharp -> golang, fsharp -> java
- fsharp -> objc, fsharp -> python, fsharp -> rust, fsharp -> swift
- fsharp -> typescript

**From golang (15 missing):**
- golang -> c, golang -> clojure, golang -> cpp, golang -> elixir
- golang -> elm, golang -> erlang, golang -> fsharp, golang -> haskell
- golang -> java, golang -> objc, golang -> python, golang -> roc
- golang -> scala, golang -> swift, golang -> typescript

**From haskell (13 missing):**
- haskell -> c, haskell -> clojure, haskell -> cpp, haskell -> elixir
- haskell -> elm, haskell -> erlang, haskell -> fsharp, haskell -> golang
- haskell -> java, haskell -> objc, haskell -> python, haskell -> rust
- haskell -> swift, haskell -> typescript

**From java (13 missing):**
- java -> clojure, java -> elixir, java -> elm, java -> erlang
- java -> fsharp, java -> golang, java -> haskell, java -> objc
- java -> python, java -> roc, java -> scala, java -> swift
- java -> typescript

**From objc (15 missing):**
- objc -> c, objc -> clojure, objc -> cpp, objc -> elixir, objc -> elm
- objc -> erlang, objc -> fsharp, objc -> golang, objc -> haskell
- objc -> java, objc -> python, objc -> roc, objc -> rust, objc -> scala
- objc -> typescript

**From python (5 missing):**
- python -> c, python -> cpp, python -> java, python -> objc
- python -> swift

**From roc (15 missing):**
- roc -> c, roc -> clojure, roc -> cpp, roc -> elixir, roc -> elm
- roc -> erlang, roc -> fsharp, roc -> golang, roc -> haskell
- roc -> java, roc -> objc, roc -> python, roc -> rust, roc -> swift
- roc -> typescript

**From rust (16 missing):**
- rust -> c, rust -> clojure, rust -> cpp, rust -> elixir, rust -> elm
- rust -> erlang, rust -> fsharp, rust -> golang, rust -> haskell
- rust -> java, rust -> objc, rust -> python, rust -> roc, rust -> scala
- rust -> swift, rust -> typescript

**From scala (16 missing):**
- scala -> c, scala -> clojure, scala -> cpp, scala -> elixir, scala -> elm
- scala -> erlang, scala -> fsharp, scala -> golang, scala -> haskell
- scala -> java, scala -> objc, scala -> python, scala -> roc, scala -> rust
- scala -> swift, scala -> typescript

**From swift (16 missing):**
- swift -> c, swift -> clojure, swift -> cpp, swift -> elixir, swift -> elm
- swift -> erlang, swift -> fsharp, swift -> golang, swift -> haskell
- swift -> java, swift -> objc, swift -> python, swift -> roc, swift -> rust
- swift -> scala, swift -> typescript

**From typescript (14 missing):**
- typescript -> c, typescript -> clojure, typescript -> cpp, typescript -> elixir
- typescript -> elm, typescript -> erlang, typescript -> fsharp, typescript -> haskell
- typescript -> java, typescript -> objc, typescript -> python, typescript -> roc
- typescript -> scala, typescript -> swift

</details>

---

*Generated by coverage gap analysis task ai-p28.14*
