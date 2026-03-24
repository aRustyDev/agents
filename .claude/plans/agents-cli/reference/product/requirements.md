
1. Prioritize Structured Data in the tool

## Module Architecture

┌──────────────────┬────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────┐
│      Layer       │                            Modules                             │                     Purpose                      │
├──────────────────┼────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ CLI/Presentation │ cli.ts, find.ts, list.ts, remove.ts                            │ Interactive prompts, ANSI output, arg parsing    │
├──────────────────┼────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ Orchestration    │ add.ts (~900 lines, the big one), sync.ts, install.ts          │ Command logic, multi-step workflows              │
├──────────────────┼────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ Core Services    │ installer.ts, skills.ts, source-parser.ts, plugin-manifest.ts  │ Filesystem ops, SKILL.md discovery, URL parsing  │
├──────────────────┼────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ Infrastructure   │ git.ts, skill-lock.ts, local-lock.ts, telemetry.ts, providers/ │ Git clone, lock files, telemetry, HTTP providers │
└──────────────────┴────────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────┘

## Shell Completions

- Shell completions setup — @bomb.sh/tab is listed as a dep but no phase includes setting up the completion generation command (ai-tools complete zsh)

## Structured Data

### stderr

- contains clues about why a clone failed (auth failure, 404, private repo)
- source validation guard.


## Discovery (skills.ts, ...)

- marks repos as not_found/private/archived
- catalog.ts parseTodoLine, external-skills.ts manifest: @ means skill filter, no URL parsing
- Recursively finds SKILL.md files up to depth 5, parses YAML frontmatter via gray-matter, validates name+description. Also reads .claude-plugin/plugin.json manifests
for declared skill paths.
- remote Skills (catalog.ts TODO.yaml + registry.ts crawlers): availability checking, taxonomy, multi-source
- local Skills (commands/skill.ts listSkills()): lists dirs in context/skills/, no recursive SKILL.md scan

## Parsing 

### SKILL

- manifest.ts readSkillFrontmatter: gray-matter + Valibot validation

### (source-parser.ts)

Parses strings like owner/repo@skill-name, owner/repo/path, github.com/o/r/tree/branch/path, local paths, git URLs into a structured ParsedSource. You want to
extend this with explicit ref (branch/tag/hash) support — their @ syntax is overloaded (it means skill filter, not git ref).

## Installation Engine (installer.ts)

Two modes:
- Symlink: copy to .agents/skills/{name}/ (canonical), then symlink from each agent's dir
  - external-skills.ts refreshLinks + symlink.ts
  - passthrough symlinks with health auditing
- Copy: copy directly to each agent's dir (no canonical)
  - external-skills.ts syncSkill
  - copies skill directories, cleans artifacts

Supports project-scope ({cwd}) and global-scope (~). Universal agents (those reading .agents/skills/) skip symlinks.

## Lock Files (two separate files)

- Global (~/.agents/.skill-lock.json): tracks source origin, GitHub tree SHA for update checking, last-selected agents
- Local (skills-lock.json): project-scoped, committed to git, minimal format with computed SHA-256 content hashes
- external (external-skills.ts + sources.lock.json): upstream commit SHA + snapshot hash
- local (lockfile.ts + skills-lock.json schema): directory hash based staleness

## Update Detection (check/update in cli.ts)

Calls GitHub Trees API (/repos/{owner}/{repo}/git/trees/{branch}?recursive=1) to get folder SHAs, compares to stored hash. update re-invokes the CLI as a subprocess
with spawnSync.

## Search/Find (find.ts)

Hits https://skills.sh/api/search?q=...&limit=10 — hardcoded to 10 results. Returns {name, slug, source, installs}. Interactive mode has a custom fzf-style readline
prompt.
- search.ts (hybrid RRF), registry.ts (crawlers), meilisearch.ts
- smithery Uses FlexSearch for in-memory fuzzy search over MCP tools. Tree-grouped output using dot-prefix navigation (e.g. github.issues.list). This is client-side post-processing — the tools come from MCP tools/list calls.
- page param to SearchOptions (--page; pagination)


## Provider System (providers/)

Extensible via HostProvider interface. Only one implementation exists: RFC 8615 well-known URIs (fetches /.well-known/skills/index.json from any domain).

## Telemetry / o11y

## Git

- external-skills.ts (inline spawnSync)
- add, revert, rm, commit, grep, log, diff, ls-remote

## External APIs
- GitHub API (github.ts): Octokit with 3-tier auth
-

## Utility Functions

- Hashing (hash.ts): file, directory, deterministic cross-platform

## Schemas

- schemas.ts: All types Valibot-validated

## Content Analyzer

- download, parse, lint, grade, deduplicate skills (requires network + subagent dispatch)
  - Metadata:
    - wordCount, sectionCount, fileCount, headingTree
    - mdq -o json, wc -w, find | wc -l
  - Links:
    - internalLinks[], externalLinks[], brokenLinks[]
    - mdq -o json links object
  - Keywords:
    - Extract from heading text + frontmatter description + first paragraph
    - keywords[]
  - Complexity:
    - complexity: simple|moderate|complex
    - Simple heuristic: wordCount < 500 = simple, 500-2000 = moderate, > 2000 = complex. Also: number of sections, nesting depth, code block count
  - ProgressiveDisclosure:
    - Check for patterns: collapsible <details> blocks, "Overview" before "Advanced", layered sections (basic→intermediate→advanced), conditional loading hints
    - progressiveDisclosure: boolean, techniques[]
  - BestPractices:
    - Frontmatter has name + description, description is actionable (tells agent WHEN to use), has examples section, uses allowed-tools, no hardcoded paths
    - bestPractices: { score: 0-5, violations[] }
  - Security:
    - Check for: hardcoded secrets/tokens, eval() usage in code blocks, unrestricted Bash(*) in allowed-tools, external URLs fetched without validation, prompt injection patterns
    - security: { score: 0-5, concerns[] }
  - Availability:
    - curl -sI https://github.com/<owner>/<repo> — check HTTP status
    - available|archived|private|not_found|error
  - ForkDetection:
    - Compare SKILL.md content hash against other entries with same skill name
    - contentHash, possibleForkOf: <owner/repo>
  - GradingRubric:
```asciidoc
┌───────┬─────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Grade │ Score Range │                                                                     Criteria                                                                     │
├───────┼─────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ A     │ 9-10        │ Frontmatter complete, description is actionable trigger, progressive disclosure used, examples present, security clean, well-structured sections │
├───────┼─────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ B     │ 7-8         │ Frontmatter complete, description adequate, has examples, minor best-practice gaps                                                               │
├───────┼─────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ C     │ 5-6         │ Frontmatter present but description vague, few examples, flat structure                                                                          │
├───────┼─────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ D     │ 3-4         │ Missing frontmatter fields, no examples, unclear purpose                                                                                         │
├───────┼─────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ F     │ 0-2         │ Broken/empty, missing SKILL.md, or security concerns                                                                                             │
└───────┴─────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
- identifying/scaling/grading complexity
- identifying use of progressive disclosure techniques
- checking skills for adherence to best practices
- checking skills for security considerations (Do we know WHAT/HOW to check these?)
- gather skill metadata (word count, section count, file count)
- inventory the links in the skills (internal files and external links)
- build a keyword index for each skill
- determining Content quality analysis
- Grading or scoring

Final score = weighted average:

- Best Practices: 30%
- Content Quality (word count + structure): 25%
- Security: 20%
- Progressive Disclosure: 15%
- Metadata Completeness: 10%

## Taxonomy Engine

- categorize 9K+ unique skill names into a category/subcategory hierarchy

## Interfaces

### Web GUI
### Machine
### TUI
### CLI

prompts (fzf-style search, multiselect agent picker)

## Namespaces

- Org/user scoping for multi-tenant publishing
- A namespace = an org/user scope. It's stored as a single string in settings.json. All resources (connections, servers, skills) are namespaced. Resolution: settings.json → first from API → auto-create. For a private registry, this maps to tenancy or team scoping.


## Components

### MCP Servers

- Remote connections to hosted MCP servers (self-hosted registry/gateway)

#### Publish

> The publish flow is tightly coupled to Smithery's workerd infrastructure. For a self-hosted gateway, you'd need: manifest spec + multipart upload endpoint + deployment status polling. The abstract pattern is sound but the implementation would be entirely custom.

This is a deploy-to-hosted-infrastructure flow, not a registry metadata push:

1. Authenticate (API key)
2. Build the MCP server with esbuild (target: Cloudflare Workers/workerd for shttp, or Node CJS for stdio)
3. Read manifest.json from build output
4. Multipart POST the JS bundle + sourcemap + manifest to /servers/:name/releases
5. Poll for deployment status (PENDING → SUCCESS/FAILURE)
6. On success: returns the live MCP URL (https://server.smithery.ai/:namespace/:server/mcp)

For your self-hosted gateway: The abstract logic is: build → package → upload to registry → poll for health. The Smithery-specific parts (workerd, shttp transport) are implementation details. What you'd want is the manifest format and upload/polling pattern.

build + upload + poll pattern (adapted for self-hosted)

### MCP Clients

- Client mode (--client): writes to 19 known client config files (Claude Desktop JSON, Cursor mcp.json, VS Code settings, etc.) with transport-specific config (stdio/http-oauth/http-proxy)
- What we'd extract: The client-config-io.ts module (read/write 19 client config formats) and the clients.ts registry (paths per OS, transport capabilities). This is the most valuable reusable logic.

## Diagramming

- Output context diagram map
