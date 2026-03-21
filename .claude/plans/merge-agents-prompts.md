# Merge Plan: agents and prompts into ai

## Overview

Merge `arustydev/agents` and `arustydev/prompts` repositories into `arustydev/agents`.

## Analysis Summary

### arustydev/agents
- **Status**: Already fully merged into `legacy/agents/`
- **Action**: Only `README.md` is missing - minor update
- **Note**: The ai repo actually has MORE agents than the source repo

### arustydev/prompts
- **Status**: NOT merged - this is the primary work
- **Content**: Sophisticated prompt engineering system with:
  - Commands (`/audit`, `/plan`, `/report`, etc.)
  - Processes (CI/CD, auditing, code-review, testing, etc.)
  - Templates (issues, reports, documentation)
  - Roles (developer levels, security engineer, ML engineer)
  - Guides (tool usage guides)
  - Core patterns (error handling, validation, process integration)
  - Hooks (validation scripts)
  - Schemas (role definitions, knowledge modules)

### arustydev/agents (cicd vs configs)
- Both paths point to identical content (only .git differs)
- Use `configs/agents` as the canonical source

---

## Merge Mapping

| Source (prompts/.claude/) | Target (ai/) | Notes |
|---------------------------|--------------|-------|
| `commands/` | `legacy/prompts/commands/` | Slash commands |
| `processes/` | `legacy/prompts/processes/` | Workflow processes |
| `templates/` | `legacy/prompts/templates/` | Issue/report templates |
| `roles/` | `legacy/prompts/roles/` | Role definitions |
| `guides/` | `legacy/prompts/guides/` | Tool guides |
| `core/` | `legacy/prompts/core/` | Core patterns & principles |
| `hooks/` | `legacy/prompts/hooks/` | Validation scripts |
| `schemas/` | `legacy/prompts/schemas/` | YAML schemas |
| `patterns/` | `legacy/prompts/patterns/` | Development patterns |
| `config/` | `legacy/prompts/config/` | Configuration files |
| `references/` | `legacy/prompts/references/` | Quick references |
| `knowledge/` | `legacy/prompts/knowledge/` | Knowledge bases |
| `automation/` | `legacy/prompts/automation/` | Automation scripts |
| `tests/` | `legacy/prompts/tests/` | Test files |
| `validators/` | `legacy/prompts/validators/` | Validation scripts |
| `workflows/` | `legacy/prompts/workflows/` | Workflow definitions |
| `standards/` | `legacy/prompts/standards/` | Standards docs |
| `meta/` | `legacy/prompts/meta/` | Meta documentation |
| `docs/` | `legacy/prompts/docs/` | Documentation |
| `examples/` | `legacy/prompts/examples/` | Examples |
| `helpers/` | `legacy/prompts/helpers/` | Helper scripts |
| `archive/` | `legacy/prompts/archive/` | Archived content |
| `archives/` | `legacy/prompts/archives/` | More archives |
| `metrics/` | `legacy/prompts/metrics/` | Metrics data |

| Source (prompts/) | Target (ai/) | Notes |
|-------------------|--------------|-------|
| Root `*.md` files | `legacy/prompts/docs/architecture/` | Architecture docs |
| Root `*.sh` scripts | `legacy/prompts/scripts/` | Shell scripts |
| Root `*.py` scripts | `legacy/prompts/scripts/` | Python scripts |
| `analysis/` | `legacy/prompts/docs/analysis/` | Analysis reports |
| `scripts/` | `legacy/prompts/scripts/` | Script files |
| `engine/` | `legacy/prompts/engine/` | Engine code |

| Source (agents/) | Target (ai/) | Notes |
|------------------|--------------|-------|
| `README.md` | `legacy/agents/README.md` | Only missing file |

---

## Implementation Plan

### Phase 1: Prepare (PR #1)
**Branch**: `feat/merge-prepare`

1. Create directory structure in `legacy/prompts/`
2. Add `.gitkeep` files
3. Update README.md to document the merge

### Phase 2: Merge Core Prompts Content (PR #2)
**Branch**: `feat/merge-prompts-core`

1. Copy `commands/` → `legacy/prompts/commands/`
2. Copy `processes/` → `legacy/prompts/processes/`
3. Copy `core/` → `legacy/prompts/core/`
4. Copy `patterns/` → `legacy/prompts/patterns/`

### Phase 3: Merge Templates & Roles (PR #3)
**Branch**: `feat/merge-prompts-templates`

1. Copy `templates/` → `legacy/prompts/templates/`
2. Copy `roles/` → `legacy/prompts/roles/`
3. Copy `schemas/` → `legacy/prompts/schemas/`

### Phase 4: Merge Guides & Knowledge (PR #4)
**Branch**: `feat/merge-prompts-guides`

1. Copy `guides/` → `legacy/prompts/guides/`
2. Copy `knowledge/` → `legacy/prompts/knowledge/`
3. Copy `references/` → `legacy/prompts/references/`

### Phase 5: Merge Supporting Files (PR #5)
**Branch**: `feat/merge-prompts-support`

1. Copy `hooks/` → `legacy/prompts/hooks/`
2. Copy `validators/` → `legacy/prompts/validators/`
3. Copy `automation/` → `legacy/prompts/automation/`
4. Copy `tests/` → `legacy/prompts/tests/`
5. Copy `helpers/` → `legacy/prompts/helpers/`

### Phase 6: Merge Docs & Scripts (PR #6)
**Branch**: `feat/merge-prompts-docs`

1. Copy root `*.md` files → `legacy/prompts/docs/architecture/`
2. Copy root `*.sh` and `*.py` scripts → `legacy/prompts/scripts/`
3. Copy `analysis/` → `legacy/prompts/docs/analysis/`
4. Copy `scripts/` → `legacy/prompts/scripts/`
5. Copy remaining directories

### Phase 7: Merge Agents README (PR #7)
**Branch**: `feat/merge-agents-readme`

1. Copy `README.md` → `legacy/agents/README.md`

### Phase 8: Cleanup & Archive
**Branch**: `feat/merge-cleanup`

1. Update ai repo README with merge notes
2. Create migration guide for users

---

## Post-Merge Actions

### Phase 9: Archive arustydev/prompts

1. **Update README.md** with deprecation notice:
   ```markdown
   # ⚠️ DEPRECATED - This repository has been archived

   This repository has been merged into [arustydev/agents](https://github.com/arustydev/agents).

   ## New Location

   All content from this repository now lives at:
   - `arustydev/agents/legacy/prompts/`

   ## Migration

   If you were using this repository, update your references:
   ```bash
   # Old
   git clone https://github.com/arustydev/prompts.git

   # New
   git clone https://github.com/arustydev/agents.git
   cd ai/legacy/prompts
   ```

   ## Why?

   This repository was consolidated into `arustydev/agents` to:
   - Centralize AI-related configuration and tooling
   - Simplify maintenance across fewer repositories
   - Enable better cross-referencing between agents, prompts, and skills

   ---
   *Archived on: YYYY-MM-DD*
   ```

2. **Update GitHub repo description**:
   ```bash
   gh repo edit arustydev/prompts \
     --description "⚠️ ARCHIVED - Merged into arustydev/agents. See legacy/prompts/"
   ```

3. **Archive the repository**:
   ```bash
   gh repo archive arustydev/prompts --yes
   ```

### Phase 10: Archive arustydev/agents

1. **Update README.md** with deprecation notice:
   ```markdown
   # ⚠️ DEPRECATED - This repository has been archived

   This repository has been merged into [arustydev/agents](https://github.com/arustydev/agents).

   ## New Location

   All content from this repository now lives at:
   - `arustydev/agents/legacy/agents/`

   ## Migration

   If you were using this repository, update your references:
   ```bash
   # Old
   git clone https://github.com/arustydev/agents.git

   # New
   git clone https://github.com/arustydev/agents.git
   cd ai/legacy/agents
   ```

   ## Why?

   This repository was consolidated into `arustydev/agents` to:
   - Centralize AI-related configuration and tooling
   - Simplify maintenance across fewer repositories
   - Enable better cross-referencing between agents, prompts, and skills

   ---
   *Archived on: YYYY-MM-DD*
   ```

2. **Update GitHub repo description**:
   ```bash
   gh repo edit arustydev/agents \
     --description "⚠️ ARCHIVED - Merged into arustydev/agents. See legacy/agents/"
   ```

3. **Archive the repository**:
   ```bash
   gh repo archive arustydev/agents --yes
   ```

### Phase 11: Cleanup

1. **Delete local clones** (optional):
   - `/Users/arustydev/repos/configs/cicd/prompts`
   - `/Users/arustydev/repos/configs/cicd/agents`
   - `/Users/arustydev/repos/configs/agents` (keep one for reference)

2. **Update any references**:
   - Search for imports/references to old repos
   - Update dotfiles if they reference these repos

3. **Verify archives are accessible**:
   ```bash
   # Archived repos remain readable but not writable
   gh repo view arustydev/prompts --json isArchived
   gh repo view arustydev/agents --json isArchived
   ```

---

## Checklist

### Merge Phases (PRs to arustydev/agents)
- [ ] Phase 1: Prepare directory structure
- [ ] Phase 2: Merge core prompts content
- [ ] Phase 3: Merge templates & roles
- [ ] Phase 4: Merge guides & knowledge
- [ ] Phase 5: Merge supporting files
- [ ] Phase 6: Merge docs & scripts
- [ ] Phase 7: Merge agents README
- [ ] Phase 8: Cleanup & archive (ai repo)

### Archive Phases (Source repos)
- [ ] Phase 9: Archive arustydev/prompts
  - [ ] Update README.md with deprecation notice
  - [ ] Update repo description
  - [ ] Archive repository
- [ ] Phase 10: Archive arustydev/agents
  - [ ] Update README.md with deprecation notice
  - [ ] Update repo description
  - [ ] Archive repository
- [ ] Phase 11: Final cleanup
  - [ ] Delete local clones (optional)
  - [ ] Update external references
  - [ ] Verify archives are accessible

---

## Notes

- All merges go to `legacy/` because the content is from older repos
- After merge, valuable content can be promoted to `components/` via `/promote-skill` or similar
- Keeping prompts in their own subdirectory (`legacy/prompts/`) maintains organization
- No content conflicts expected as prompts content is new to ai repo
