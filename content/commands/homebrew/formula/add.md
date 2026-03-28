---
description: Research a package and generate a Homebrew formula via the template pipeline
argument-hint: <repo-url-or-name> [--language go|rust|python|zig|cmake|autotools|meson] [--head-only]
allowed-tools: Read, Write, Glob, Grep, Bash(curl:*), Bash(shasum:*), Bash(just:*), Bash(git:*), Bash(gh:*), Bash(brew:*), Bash(npm:*), Bash(ls:*), Bash(mkdir:*), Bash(cat:*), WebFetch, WebSearch, Task, AskUserQuestion
---

# Add Homebrew Formula

Research a package repository and generate a complete Homebrew formula using the `pkgmgr-homebrew-formula-dev` skill's JSON Schema → Mustache template pipeline.

## Arguments

- `$1` - Repository URL or package name (required). Examples: `https://github.com/owner/repo`, `owner/repo`, `my-tool`
- `--language` - Build system language (optional, auto-detected if omitted): `go`, `rust`, `python`, `zig`, `cmake`, `autotools`, `meson`
- `--head-only` - Generate a HEAD-only formula with no stable URL/SHA256

## Workflow

### Step 1: Resolve Repository

1. If `$1` is a full URL, extract owner/repo
2. If `$1` is `owner/repo`, construct `https://github.com/owner/repo`
3. If `$1` is just a name, search GitHub: `gh search repos "$1" --limit 5` and ask the user to pick
4. Verify the repo exists: `gh repo view <owner/repo> --json name,description,url,licenseInfo,primaryLanguage`

### Step 2: Detect Language and Build System

1. If `--language` was provided, use it
2. Otherwise, inspect the repo:
   - `go.mod` → go
   - `Cargo.toml` → rust
   - `setup.py` / `pyproject.toml` → python
   - `build.zig` → zig
   - `CMakeLists.txt` → cmake
   - `configure.ac` / `Makefile.am` → autotools
   - `meson.build` → meson
3. If ambiguous, ask the user

### Step 3: Fetch Release Info

1. Get latest release: `gh release view --repo <owner/repo> --json tagName,tarballUrl,name`
2. If `--head-only` or no releases exist, skip to Step 4 with head-only config
3. Compute SHA256: `curl -sL <tarball-url> | shasum -a 256`
4. Extract version from tag (strip leading `v`)

### Step 4: Analyze Dependencies

1. Read the repo's build files to identify:
   - Build dependencies (compilers, build tools)
   - Runtime dependencies (shared libraries, interpreters)
   - `uses_from_macos` candidates (zlib, curl, libxml2, etc.)
2. Check if the package produces a service (daemon) or CLI tool
3. Look for completions (bash, zsh, fish) in the source

### Step 5: Build JSON Input

Construct a JSON object conforming to the skill's `formula.schema.ts`:

```json
{
  "formulas": [{
    "name": "<kebab-case-name>",
    "desc": "<description from repo>",
    "homepage": "<repo-url>",
    "url": "<tarball-url>",
    "sha256": "<computed-sha256>",
    "license": "<SPDX-identifier>",
    "language": "<detected-language>",
    "livecheck": { "url": ":stable", "strategy": ":github_latest" },
    "dependencies": [...],
    "uses_from_macos": [...],
    "install": { ... },
    "test": { "command": "...", "expected_output": "..." }
  }]
}
```

Read the schema at `content/skills/pkgmgr-homebrew-formula-dev/scripts/formula.schema.ts` to ensure all fields are valid.

### Step 6: Render Formula

1. Locate the skill directory: `content/skills/pkgmgr-homebrew-formula-dev`
2. Ensure dependencies are installed: `cd <skill-dir> && npm ls mustache ajv 2>/dev/null || npm install`
3. Write the JSON to a temp file
4. Run: `cd <skill-dir> && just template-formula "$(cat <temp-file>)"`
5. Capture the rendered Ruby output

### Step 7: Write and Report

1. Determine output path — ask the user or default to `Formula/<name>.rb`
2. Write the rendered formula to the output path
3. Show the user the generated formula
4. Suggest next steps:
   - `/validate-formula <path>` to run brew audit/style
   - `brew install --build-from-source <path>` to test locally

## Examples

```text
/add-formula https://github.com/BurntSushi/ripgrep
/add-formula sharkdp/bat --language rust
/add-formula my-internal-tool --head-only
```

## Notes

- The formula schema supports: go, rust, python, zig, cmake, autotools, meson
- For Python formulas, resources (pip dependencies) must be listed manually or extracted from `requirements.txt`
- HEAD-only formulas skip URL/SHA256 and use `head "https://github.com/..."` instead
- Always verify the generated formula with `/validate-formula` before committing
