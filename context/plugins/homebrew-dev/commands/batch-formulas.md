---
description: Research and generate multiple Homebrew formulas in parallel from a list of packages
argument-hint: <package-list-or-file> [--tap path/to/tap] [--validate]
allowed-tools: Read, Write, Glob, Grep, Bash(curl:*), Bash(shasum:*), Bash(just:*), Bash(git:*), Bash(gh:*), Bash(brew:*), Bash(npm:*), Bash(ls:*), Bash(mkdir:*), Bash(cat:*), WebFetch, WebSearch, Task, AskUserQuestion
---

# Batch Generate Homebrew Formulas

Research multiple packages and generate Homebrew formulas for all of them, using parallel sub-agents for research and SHA256 computation.

## Arguments

- `$1` - Comma-separated list of repo URLs/names, OR path to a file with one package per line (required)
- `--tap` - Path to the tap's `Formula/` directory (optional, default: `Formula/`)
- `--validate` - Run `/validate-formula` on each generated formula after rendering (optional)

## Workflow

### Step 1: Parse Package List

1. If `$1` is a file path (ends in `.txt`, `.json`, or `.yaml`), read it:
   - `.txt`: one package per line (blank lines and `#` comments ignored)
   - `.json`: array of strings or array of objects with `name`/`url` fields
   - `.yaml`: same structure as JSON
2. If `$1` is a comma-separated string, split on commas and trim whitespace
3. Report the count: "Found N packages to process"

### Step 2: Parallel Research

For each package, launch a Task sub-agent to:

1. Resolve the repository (same as `/add-formula` Step 1-2)
2. Fetch latest release tag and tarball URL
3. Compute SHA256 of the tarball: `curl -sL <url> | shasum -a 256`
4. Detect language/build system
5. Analyze dependencies from build files
6. Return a structured JSON result

Use parallel Task agents — up to 4 concurrent — to speed up research.

### Step 3: Review Research Results

Present a summary table to the user:

```
| # | Package | Version | Language | Deps | Status |
|---|---------|---------|----------|------|--------|
| 1 | ripgrep | 14.1.0  | rust     | 2    | Ready  |
| 2 | fd      | 10.2.0  | rust     | 1    | Ready  |
| 3 | my-tool | —       | go       | 0    | HEAD-only |
```

Ask the user to confirm before rendering, or remove packages from the batch.

### Step 4: Generate JSON and Render

1. Build a single JSON object with all formulas in the `formulas` array
2. Write to a temp file
3. Run: `cd <skill-dir> && just template-formula "$(cat <temp-file>)"`
4. Split the rendered output into individual formula files (split on `class ... < Formula`)

### Step 5: Write Formula Files

1. Create the output directory if needed: `mkdir -p <tap>/Formula/`
2. Write each formula to `<tap>/Formula/<name>.rb`
3. Report files created

### Step 6: Optional Validation

If `--validate` was passed, run `/validate-formula` on each generated file and collect results.

### Step 7: Final Report

```
## Batch Formula Generation Complete

| Formula | File | Validation |
|---------|------|------------|
| ripgrep | Formula/ripgrep.rb | PASS |
| fd      | Formula/fd.rb | PASS |
| my-tool | Formula/my-tool.rb | WARN (2) |

Next steps:
- Review each formula for accuracy
- `brew install --build-from-source Formula/<name>.rb`
- Commit and push to your tap
```

## Examples

```
/batch-formulas ripgrep,fd,bat,eza,delta
/batch-formulas packages.txt --tap homebrew-tap --validate
/batch-formulas tools.json --validate
```

## Notes

- SHA256 computation requires network access to download tarballs
- Large batches (10+) may take a while due to tarball downloads
- Each formula is rendered independently — one failure won't block others
- The skill's template pipeline must be set up first (`cd <skill-dir> && just deps`)
