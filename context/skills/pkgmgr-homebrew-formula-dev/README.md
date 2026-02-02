# pkgmgr-homebrew-formula-dev

A skill for creating, validating, and maintaining Homebrew formulas. It provides a JSON-to-Ruby pipeline backed by JSON Schema validation and Mustache templating, with support for 24 language/build-system types.

## How It Works

```
JSON input → AJV schema validation → helper preprocessing → Mustache rendering → Ruby formula
```

1. Author a JSON file describing the formula (name, version, URL, language, dependencies, etc.)
2. Run `just template-formula <path-to-json>` to validate and render a `.rb` formula
3. The schema enforces correct structure per language; the Mustache templates emit idiomatic Homebrew Ruby DSL

## Quick Start

```bash
just deps                                          # install Node + Homebrew deps
just template-formula test/data/go-standard.json   # render a Go formula
just test                                          # run all test cases
```

## Supported Languages

### Tier 1 — Dedicated Toolchain (full schema + template + tests)

Go, Rust, Python, Node.js, Java, Swift, Elixir, Haskell, Kotlin, Scala, Erlang, OCaml, Nim, Dart, Gleam, Roc, Julia, .NET, Zig, CMake, Autotools, Meson, Make, Custom

### Tier 2 — Build-System Mapping (reference doc + tests)

C, C++, Fortran, Objective-C, R, Scheme, Groovy — each maps to an existing Tier 1 build system.

### Tier 3 — Minimal Homebrew Presence (reference doc + tests)

Lua, PHP, Ruby, Perl, Clojure, TypeScript, JavaScript — guidance on recommended approach.

## Directory Layout

```
scripts/
  formula.schema.ts    JSON Schema (draft-2020-12) with per-language install defs
  formula.helper.ts    Preprocessing: PascalCase, license rendering, flag expansion

reference/
  templates/
    main.mustache      Top-level formula template
    langs/*.mustache    Language-specific install block partials
    formulas/*.rb      Static reference examples (not used by pipeline)
  langs/*.md           Per-language research and pattern guides
  checklists/          Procedural checklists (add-language, local-validation)
  faq/                 Common formula authoring questions
  security/            Signing and attestation guidance
  testing/             Test block patterns

test/
  data/*.json          Test fixtures (one per language/scenario)
  cases/test-*.sh      Shell-based test cases
```

## Adding a New Language

See `reference/checklists/add-language.md` for the tiered procedure (9 artifacts for Tier 1, 3 for Tier 2/3).

## Key Files

| File | Purpose |
|------|---------|
| `SKILL.md` | AI-facing skill definition with full research/authoring workflow |
| `justfile` | Pipeline commands: `deps`, `template-formula`, `test` |
| `scripts/formula.schema.ts` | Canonical schema — all validation rules live here |
| `reference/templates/main.mustache` | Formula structure and language dispatch |
