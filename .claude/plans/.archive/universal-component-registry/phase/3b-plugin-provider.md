# Phase 3b: Plugin Provider

**ID:** `phase-3b`
**Dependencies:** phase-1 (complete)
**Status:** planned

## Objective

Create a `LocalPluginProvider` that discovers plugins via their `plugin.json` manifests and exposes them as `Component` objects. Reuses the existing `readPluginManifest()` from `lib/manifest.ts`.

## Success Criteria

- [ ] `LocalPluginProvider` discovers plugins in nested `context/plugins/` subdirectories
- [ ] Reuses `readPluginManifest(dir)` from `lib/manifest.ts` — no duplicate parsing
- [ ] Excludes `.template/` directory
- [ ] Maps `PluginManifest` fields to `Component` (name, version, description, author, tags/keywords)
- [ ] Search filters by query (substring on name+description+keywords)
- [ ] All tests pass

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Plugin provider | `.scripts/lib/component/provider-plugin.ts` | TypeScript |
| Plugin provider tests | `.scripts/test/component/provider-plugin.test.ts` | bun:test |

## Files

**Create:**
- `.scripts/lib/component/provider-plugin.ts`
- `.scripts/test/component/provider-plugin.test.ts`

## On-Disk Structure

```
context/plugins/
├── .template/                          # skip
│   └── .claude-plugin/plugin.json
├── frontend/
│   ├── swiftui-dev/
│   │   └── .claude-plugin/plugin.json  ← plugin
│   └── design-to-code/
│       └── .claude-plugin/plugin.json  ← plugin
├── releases/
│   └── homebrew-dev/
│       └── .claude-plugin/plugin.json  ← plugin
├── blog-workflow/
│   └── .claude-plugin/plugin.json      ← plugin
└── job-hunting/
    └── .claude-plugin/plugin.json      ← plugin
```

**Discovery pattern:** `glob("context/plugins/**/.claude-plugin/plugin.json")` excluding `.template/`.

**Manifest format** (already validated by `PluginManifest` Valibot schema in `lib/schemas.ts`):
```json
{
  "name": "blog-workflow",
  "version": "4.0.0",
  "description": "Multi-phase blog content creation...",
  "author": { "name": "Adam Smith", "email": "..." },
  "keywords": ["blog", "content", "writing"],
  "license": "MIT"
}
```

**Mapping to Component:**
| PluginManifest field | Component field |
|---------------------|-----------------|
| `name` | `name` |
| `description` | `description` |
| `version` | `version` |
| `author.name` | `author` |
| `keywords` | `tags` |
| `homepage` | `url` |
| (parent dir path) | `localPath` |
| `"context/plugins/..."` | `source` |

## Tasks

### Task 3b.1: Plugin Provider

- [ ] **Step 1: Write failing tests**

Create test fixtures with temp dirs containing `.claude-plugin/plugin.json` files. Tests:
1. **capabilities: declares plugin support for search, list, info**
2. **search: discovers plugins in nested dirs**
3. **search: excludes .template dir**
4. **search: filters by query on name+description+keywords**
5. **search: returns empty for non-plugin type**
6. **search: paginates results**
7. **list: returns all plugins**
8. **info: returns plugin detail by name**
9. **info: returns error for unknown plugin**
10. **plugin Component has correct shape** (version, author, tags from keywords, url from homepage)
11. **skips invalid plugin.json** (malformed JSON doesn't crash discovery)

- [ ] **Step 2: Run tests, verify fail**
- [ ] **Step 3: Implement**

Key: use `readPluginManifest(pluginDir)` from `lib/manifest.ts`. The provider's job is just discovery (find the dirs) + mapping (PluginManifest → Component).

- [ ] **Step 4: Run tests, verify pass**
- [ ] **Step 5: Commit**

## Acceptance Criteria

- [ ] Uses `readPluginManifest` from `lib/manifest.ts` — no duplicate manifest parsing
- [ ] Discovers plugins in arbitrarily nested subdirectories
- [ ] Read-only: no add/remove (plugins are scaffolded via `/scaffold-plugin`)
- [ ] At least 11 test cases
