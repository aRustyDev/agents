---
description: Create an MDBook plugin (preprocessor or alt-backend) with full project setup
argument-hint: <plugin-name> [--type preprocessor|backend]
---

# Create MDBook Plugin

Create a new MDBook plugin project with complete scaffolding, documentation templates, and TDD setup.

## Arguments

- `$1` - Plugin name without `mdbook-` prefix (e.g., `json-table` becomes `mdbook-json-table`)
- `--type` - Plugin type: `preprocessor` (default) or `backend`

## Workflow

### Step 1: Validate Arguments

1. Parse plugin name from `$1`
2. Validate name format (lowercase, hyphenated)
3. Determine plugin type from `--type` flag (default: `preprocessor`)
4. Full name will be `mdbook-<plugin-name>`

### Step 2: Ensure Required Skills Available

Before proceeding, verify the appropriate skill is available:

**For preprocessor plugins:**
1. Check if `mdbook-plugin-preprocessor` skill exists in:
   - `.claude/skills/mdbook-plugin-preprocessor/SKILL.md`
   - `~/repos/configs/ai/components/skills/mdbook-plugin-preprocessor/SKILL.md`
2. If not found, read the skill from the ai config repo

**For alt-backend plugins:**
1. Check if `mdbook-plugin-alt-backend` skill exists in:
   - `.claude/skills/mdbook-plugin-alt-backend/SKILL.md`
   - `~/repos/configs/ai/components/skills/mdbook-plugin-alt-backend/SKILL.md`
2. If not found, create a minimal placeholder skill:

```markdown
---
name: mdbook-plugin-alt-backend
description: Developing custom MDBook alternative backend plugins. Use when asked to 'create mdbook backend', 'build mdbook renderer', or 'develop alt-backend'.
---

# MDBook Alt-Backend Plugin Development

## Overview

Guide for developing MDBook alternative backend (renderer) plugins.

**This skill covers:**
- Backend trait implementation
- Output format handling
- Configuration in `book.toml`

**Note:** This is a placeholder. See MDBook docs for full backend development guide:
https://rust-lang.github.io/mdBook/for_developers/backends.html
```

### Step 3: Invoke the Appropriate Skill

Read and apply the skill content to guide development:

1. Use the Skill tool or read the SKILL.md file directly
2. Follow the skill's workflow for the selected plugin type

### Step 4: Gather Plugin Requirements

Use AskUserQuestion to collect:

1. **Problem Statement**: What content transformation or rendering is needed?
2. **Input Syntax**: What will users write in their markdown?
3. **Output Format**: What should be generated?
4. **Supported Renderers** (preprocessor): html, pdf, epub, etc.
5. **Output Format** (backend): Custom format details

### Step 5: Check for Existing Plugins

Before creating, search for existing solutions:

```bash
# Search GitHub
gh search repos mdbook-<keyword> --limit 20

# Search crates.io
cargo search mdbook-<keyword>
```

Present findings to user. If suitable plugin exists, offer to adopt instead.

### Step 6: Create GitHub Repository

**Confirm with user before creating the repo.**

```bash
gh repo create arustydev/mdbook-<plugin-name> \
  --public \
  --description "MDBook <type> for <description>" \
  --clone

cd mdbook-<plugin-name>
cargo init --name mdbook-<plugin-name>
```

### Step 7: Set Up Project Structure

Follow the skill's project structure template.

For **preprocessor**:
```
mdbook-<name>/
├── Cargo.toml
├── src/
│   ├── main.rs
│   └── lib.rs
├── tests/
│   ├── integration.rs
│   └── fixtures/
├── docs/
│   └── adr/
└── .github/workflows/ci.yml
```

For **backend**:
```
mdbook-<name>/
├── Cargo.toml
├── src/
│   ├── main.rs
│   └── lib.rs
├── templates/          # Output templates
├── tests/
└── .github/workflows/ci.yml
```

### Step 8: Generate Documentation

Create documentation following skill templates:

1. **ADR** (Architecture Decision Record)
2. **Data Flow Diagram** (Mermaid)
3. **User Stories**
4. **README.md** with installation and usage

### Step 9: Implement with TDD

Follow skill's TDD workflow:

1. Write failing tests first
2. Implement minimal code to pass
3. Refactor and iterate
4. Run `cargo test`, `cargo clippy`, `cargo fmt`

### Step 10: Report Summary

```
## Plugin Created

| Field | Value |
|-------|-------|
| Name | `mdbook-<plugin-name>` |
| Type | <preprocessor|backend> |
| Repo | https://github.com/arustydev/mdbook-<plugin-name> |

**Next steps:**
1. Complete implementation following TDD workflow
2. Test with sample book
3. Publish to crates.io when ready
```

## Examples

### Create a preprocessor
```
/create-mdbook-plugin json-table
```
Creates `mdbook-json-table` preprocessor plugin.

### Create an alt-backend
```
/create-mdbook-plugin wiki-js --type backend
```
Creates `mdbook-wiki-js` backend plugin.

## Notes

- Plugin names should be descriptive and follow `mdbook-<name>` convention
- Preprocessors modify content before rendering
- Backends render content to alternative formats
- Both types use stdin/stdout JSON communication with mdbook
- See MDBook developer docs: https://rust-lang.github.io/mdBook/for_developers/
