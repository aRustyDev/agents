# Platform Testing Scenarios

Verification scenarios for platform skill integration. Run these after `/blog/init` or when adding a new platform skill.

## 1. Fresh Initialization

### Astro Auto-Detection

**Precondition:** Project has `astro.config.mjs` or `astro.config.ts` in root.

```text
/blog/init
```

**Expected:**

- Platform detected as `astro`
- `.blog-workflow.yaml` created with `platform: astro`
- Platform skill loaded from `skills/platforms/astro/SKILL.md`
- All directories created under `content/`
- Templates copied to `content/_templates/`

**Verify:**

- [ ] `.blog-workflow.yaml` exists and contains `platform: astro`
- [ ] `content/_projects/`, `content/_drafts/`, `content/_templates/` exist
- [ ] Templates copied (34 total)

### Explicit Platform

```text
/blog/init --platform astro
```

**Expected:** Same as auto-detection, but skips file checks.

### No Platform Detected

**Precondition:** No platform indicator files in project root.

```text
/blog/init
```

**Expected:** User prompted to specify platform manually.

## 2. Full Workflow (Idea → Publish)

### End-to-End with Astro

1. `/blog/init --platform astro` — Initialize
2. `/blog/idea/brainstorm "Test topic"` — Generate ideas
3. `/blog/post/draft content/_projects/test/` — Draft post
   - **Verify:** Frontmatter uses `pubDatetime` (not `date`)
   - **Verify:** `draft: true` set
4. `/blog/publish/pre-check content/_drafts/test-post.md` — Validate
   - **Verify:** Checks against platform schema from skill
5. `/blog/publish/promote content/_drafts/test-post.md` — Promote
   - **Verify:** Copies to `src/data/blog/` (from `platform.paths.published`)
   - **Verify:** Sets `draft: false`, adds `modDatetime`
6. `/blog/publish/validate src/data/blog/test-post.md` — Build check
   - **Verify:** Runs `astro build` (from `platform.commands.build`)

## 3. Frontmatter Validation

### Platform-Specific Field Names

**Verify the Astro platform skill provides correct field mappings:**

| Generic Concept | Astro Field | Source |
|-----------------|-------------|--------|
| Publication date | `pubDatetime` | `platform.frontmatter.date_field` |
| Last modified | `modDatetime` | `platform.frontmatter.updated_field` |
| Social image | `ogImage` | `platform.frontmatter.image_field` |
| Canonical URL | `canonicalURL` | `platform.frontmatter.canonical_field` |

### Draft Command Output

When `/blog/post/draft` generates frontmatter:

- [ ] Uses `pubDatetime` (not generic `date`)
- [ ] Uses `modDatetime` (not generic `updated`)
- [ ] Includes `ogImage` field (not generic `image`)

## 4. Build Validation

### Platform Commands

**Verify commands from skill frontmatter:**

| Command | Expected Value | Used By |
|---------|----------------|---------|
| `platform.commands.build` | `astro build` | `/blog/publish/validate` |
| `platform.commands.dev` | `astro dev` | `/blog/publish/validate --dev` |

### Build Output Path

- [ ] `/blog/publish/validate` checks `dist/` (from `platform.paths.build_output`)

## 5. Progressive Disclosure

### Default Load

When `/blog/init` runs:

- [ ] `skills/platforms/astro/SKILL.md` loaded (< 200 lines)
- [ ] Reference files NOT loaded automatically

### On-Demand Load

When commands need deeper context:

- [ ] `reference/frontmatter.md` loaded only during frontmatter validation
- [ ] `reference/publishing.md` loaded only during publish commands
- [ ] `reference/paths.md` loaded only when path resolution needed

## 6. Error Paths

| Scenario | Expected Behavior |
|----------|-------------------|
| No `.blog-workflow.yaml` exists | Commands show error: "No platform configured. Run `/blog/init`" |
| Invalid platform name in config | Error: "Unknown platform. Available: astro" |
| Platform skill file missing | Error: "Platform skill not found at `skills/platforms/<name>/SKILL.md`" |
| Multiple platforms detected | User prompted to choose |
