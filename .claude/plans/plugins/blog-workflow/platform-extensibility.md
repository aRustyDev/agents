# Platform Extensibility Refactoring Plan

## Objective

Refactor blog-workflow plugin to make Astro/AstroPaper-specific instructions a progressively disclosed skill, enabling platform extensibility for Hugo, Next.js MDX, and other blog platforms.

## Current State

| Metric | Value |
|--------|-------|
| Total plugin files | 138 |
| Platform-agnostic | ~85% |
| Astro-specific | ~15% |
| Platform skills | 0 |

### Astro-Specific Content Identified

| File | Content | Severity |
|------|---------|----------|
| `rules/blog-frontmatter.md` | AstroPaper field names, schema | High |
| `commands/publish/validate.md` | `astro build`, `dist/` output | High |
| `commands/publish/promote.md` | `src/data/blog/` target path | High |
| `commands/publish/pre-check.md` | AstroPaper schema validation | High |
| `commands/post/draft.md` | "AstroPaper-compatible frontmatter" | Medium |
| `commands/init.md` | `src/data/blog/` in hook paths | Medium |
| `docs/src/workflow/publishing.md` | `src/data/blog/`, `astro build` | Medium |

---

## Target Architecture

### Directory Structure

```
context/plugins/blog-workflow/
├── skills/
│   └── platforms/
│       ├── _interface.md              # Platform interface contract
│       └── astro/
│           ├── SKILL.md               # Minimal trigger + core mapping
│           └── reference/
│               ├── frontmatter.md     # Full AstroPaper schema
│               ├── publishing.md      # Build/deploy details
│               └── paths.md           # Directory conventions
├── rules/
│   └── blog-frontmatter.md            # Generic, references platform
├── commands/
│   └── publish/
│       ├── validate.md                # Uses {{platform.*}} variables
│       ├── promote.md                 # Uses {{platform.*}} variables
│       └── pre-check.md               # Uses {{platform.*}} variables
└── ...
```

### Platform Interface Contract

Each platform skill must provide:

```yaml
# Platform interface (_interface.md)
platform:
  name: string              # "astro", "hugo", "nextjs-mdx"
  display_name: string      # "Astro/AstroPaper"

  paths:
    published: string       # Where posts go (e.g., "src/data/blog/")
    build_output: string    # Build output (e.g., "dist/")

  frontmatter:
    date_field: string      # "pubDatetime" or "date"
    updated_field: string   # "modDatetime" or "lastmod"
    image_field: string     # "ogImage" or "image"
    canonical_field: string # "canonicalURL" or "canonical"

  commands:
    build: string           # "astro build"
    dev: string             # "astro dev"

  detection:
    files: string[]         # ["astro.config.mjs", "astro.config.ts"]
```

---

## Implementation Phases

### Phase 1: Create Platform Interface & Astro Skill

**Goal**: Extract Astro-specific knowledge into a skill without changing core plugin behavior.

**Tasks**:

1. Create `skills/platforms/_interface.md` defining the platform contract
2. Create `skills/platforms/astro/SKILL.md` with:
   - Detection triggers
   - Core frontmatter mapping table
   - Links to reference files
3. Create `skills/platforms/astro/reference/frontmatter.md`:
   - Full AstroPaper schema
   - Field validation rules
   - Common mistakes table
4. Create `skills/platforms/astro/reference/publishing.md`:
   - Build commands
   - Dev server usage
   - Rollback procedures
5. Create `skills/platforms/astro/reference/paths.md`:
   - Directory conventions
   - Content collections structure

**Acceptance**:
- Astro skill exists with progressive disclosure
- No changes to core plugin yet
- Skill can be manually loaded and provides correct information

---

### Phase 2: Abstract Core Plugin Commands

**Goal**: Make publish commands platform-agnostic using variable substitution.

**Tasks**:

1. Update `commands/publish/promote.md`:
   - Replace `src/data/blog/` with `{{platform.paths.published}}`
   - Add "Requires: Active platform skill" section
   - Document platform detection behavior

2. Update `commands/publish/validate.md`:
   - Replace `astro build` with `{{platform.commands.build}}`
   - Replace `astro dev` with `{{platform.commands.dev}}`
   - Replace `dist/` with `{{platform.paths.build_output}}`

3. Update `commands/publish/pre-check.md`:
   - Replace AstroPaper field names with `{{platform.frontmatter.*}}`
   - Reference platform skill for schema details

4. Update `commands/post/draft.md`:
   - Remove "AstroPaper-compatible" wording
   - Reference platform skill for frontmatter generation

5. Update `commands/init.md`:
   - Add `--platform <name>` argument
   - Generate platform-specific hooks
   - Default to platform detection

**Acceptance**:
- Commands use platform variables
- Existing Astro users see no behavior change
- Commands fail gracefully without platform skill

---

### Phase 3: Abstract Rules and Documentation

**Goal**: Make rules and docs platform-agnostic.

**Tasks**:

1. Update `rules/blog-frontmatter.md`:
   - Make schema generic (use plugin field names)
   - Add "Platform Mapping" section referencing skill
   - Keep validation rules generic

2. Update `docs/src/reference/frontmatter.md`:
   - Document plugin's generic schema
   - Add "Platform-Specific" section with links

3. Update `docs/src/workflow/publishing.md`:
   - Use generic paths/commands
   - Add "Platform Requirements" section

4. Create `docs/src/platforms/index.md`:
   - Overview of platform support
   - How to add new platforms
   - Platform detection logic

**Acceptance**:
- Rules reference platform skills
- Documentation is platform-neutral
- Clear extension guide exists

---

### Phase 4: Platform Detection & Initialization

**Goal**: Auto-detect platform and configure workflow accordingly.

**Tasks**:

1. Add detection logic to `/blog/init`:
   - Check for `astro.config.mjs` → Astro
   - Check for `hugo.toml` / `config.toml` with hugo → Hugo
   - Check for `next.config.js` + MDX config → Next.js MDX
   - Prompt if ambiguous

2. Store platform choice in project:
   - Add `platform: astro` to project `index.md` frontmatter
   - Or create `.blog-workflow.yaml` config file

3. Load platform skill automatically:
   - When entering blog workflow context
   - Based on project config or detection

4. Update plugin.json:
   - Add `platformSkills` array
   - Define skill dependencies

**Acceptance**:
- New projects auto-detect platform
- Platform skill loads automatically
- Manual override available

---

### Phase 5: Validation & Testing

**Goal**: Ensure refactoring doesn't break existing workflows.

**Tasks**:

1. Create test scenarios:
   - Fresh init with Astro detection
   - Full workflow: idea → publish
   - Frontmatter validation
   - Build validation

2. Test platform skill progressive disclosure:
   - SKILL.md loads by default
   - Reference files load on demand
   - Token budget stays reasonable

3. Document migration for existing users:
   - What changes (if anything)
   - How to verify setup

**Acceptance**:
- All existing workflows work
- No regression in Astro support
- Clear upgrade path documented

---

## Files to Create

| File | Purpose |
|------|---------|
| `skills/platforms/_interface.md` | Platform contract definition |
| `skills/platforms/astro/SKILL.md` | Astro platform skill |
| `skills/platforms/astro/reference/frontmatter.md` | AstroPaper schema |
| `skills/platforms/astro/reference/publishing.md` | Build/deploy |
| `skills/platforms/astro/reference/paths.md` | Directory structure |
| `docs/src/platforms/index.md` | Platform support overview |

## Files to Modify

| File | Changes |
|------|---------|
| `rules/blog-frontmatter.md` | Make generic, add platform reference |
| `commands/publish/validate.md` | Use platform variables |
| `commands/publish/promote.md` | Use platform variables |
| `commands/publish/pre-check.md` | Use platform variables |
| `commands/post/draft.md` | Remove AstroPaper wording |
| `commands/init.md` | Add platform detection/selection |
| `docs/src/workflow/publishing.md` | Make generic |
| `docs/src/reference/frontmatter.md` | Add platform section |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing Astro workflows | Medium | High | Phase 5 testing, maintain backward compat |
| Variable substitution complexity | Low | Medium | Keep syntax simple, document clearly |
| Platform detection false positives | Low | Low | Allow manual override |
| Skill loading overhead | Low | Low | Progressive disclosure minimizes tokens |

---

## Future Platforms

After Astro skill is complete, same pattern for:

1. **Hugo** - Different frontmatter, `hugo build`, `public/` output
2. **Next.js MDX** - Different structure, `npm run build`, `.next/` output
3. **Gatsby** - Similar to Next.js
4. **Jekyll** - Ruby-based, `_posts/` convention

Each platform skill follows the interface contract, making addition straightforward.

---

## Success Criteria

1. ✅ Astro-specific content extracted to platform skill
2. ✅ Core plugin commands work with platform variables
3. ✅ Progressive disclosure reduces default token usage
4. ✅ Platform detection works automatically
5. ✅ Clear path to add new platforms
6. ✅ No regression for existing Astro users
