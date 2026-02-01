## Adding Language Support — Meta-Checklist

### Tier 1: Dedicated Toolchain Language (Full Support — 9 Artifacts)

Languages with their own build tool that Homebrew formulas call directly.

- [ ] **Schema definition** — Add `install-<lang>` def in `scripts/formula.schema.ts`
- [ ] **Schema allOf dispatch** — Add `if/then` block in `formula.allOf` array
- [ ] **Schema enum entry** — Add `"<lang>"` to `language.enum`
- [ ] **Mustache partial** — Create `reference/templates/langs/<lang>.mustache`
- [ ] **Main template dispatch** — Add `{{#is_<lang>}}{{> langs/<lang>}}{{/is_<lang>}}` block in `main.mustache`
- [ ] **Reference doc** — Create `reference/langs/<lang>.md` following the pattern in `go.md`
- [ ] **Example formula** — Create `reference/templates/formulas/<lang>.rb` (pipeline-generated output)
- [ ] **Test fixture** — Create `test/data/<lang>-standard.json` with valid formula JSON
- [ ] **Test case** — Create `test/cases/test-<lang>-renders.sh` asserting key patterns

**Reference doc structure:**

1. Research table (What / Where to Look / Command)
2. Quick check sequence (bash commands)
3. Dependencies block
4. Install block pattern
5. JSON schema fields table
6. Mustache partial note
7. Common issues
8. Reference link to example formula

### Tier 2: Build-System Mapping Language (3 Artifacts)

Languages that use an existing build system (cmake, autotools, make, etc.) rather than a language-specific tool.

- [ ] **Reference doc** — Create `reference/langs/<lang>.md` explaining which `language` value to use, plus language-specific dependency and pattern notes
- [ ] **Test fixture** — Create `test/data/<lang>-standard.json` using the mapped `language` value with language-specific deps/patterns
- [ ] **Test case** — Create `test/cases/test-<lang>-renders.sh` verifying language-specific output

**Reference doc structure:**

1. Mapping note: "Use `language: <mapped>` — <lang> projects typically use <build-system>"
2. Research table (language-specific indicators)
3. Dependencies block (language-specific deps like `gcc`, `gfortran`)
4. Install block pattern (same as mapped language but with language-specific notes)
5. Common patterns and variations
6. Common issues

### Tier 3: Minimal Homebrew Presence Language (3 Artifacts)

Languages rarely packaged as Homebrew formulas; reference doc explains the recommended approach.

- [ ] **Reference doc** — Create `reference/langs/<lang>.md` with recommended `language` value and rationale
- [ ] **Test fixture** — Create `test/data/<lang>-standard.json` demonstrating the recommended approach
- [ ] **Test case** — Create `test/cases/test-<lang>-renders.sh` verifying the approach works

**Reference doc structure:**

1. Overview: why this language is rarely a formula
2. Recommended `language` value and rationale
3. Example patterns from real formulas
4. Common issues and workarounds

### Helper Changes (When Needed)

- **`build_system_is_*` flags** — For languages with `build_system` sub-selectors (Java, Haskell, OCaml), add flag preprocessing in `scripts/formula.helper.ts` so mustache can conditionally render build system variants
