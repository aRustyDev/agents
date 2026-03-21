# AI coding agent component distribution: a fast-moving ecosystem converging on skills

The AI coding agent component ecosystem has rapidly standardized around the **SKILL.md format** (Agent Skills Specification at agentskills.io), with **over 20 CLI tools** now competing to distribute skills, commands, rules, and agents across 40+ coding agents. Vercel's `npx skills` CLI dominates with **547K weekly npm downloads** and support for 42 agents, but the landscape includes compelling alternatives like `openskills`, `prpm`, `@tanstack/intent`, and `agent-skills-cli` that each take fundamentally different architectural approaches. The ecosystem emerged explosively after Anthropic open-sourced the Agent Skills specification in December 2025, and has already split into two distribution paradigms: git-based (clone from repos) and npm-based (ship skills alongside library code). This report maps the full landscape, compares the major tools, documents component hierarchies across Claude Code, Cursor, and Windsurf, and analyzes whether "prompts" deserve first-class distributable status.

---

## 1. The CLI landscape: 20+ tools across four tiers

The tooling ecosystem has stratified into distinct tiers based on scope, adoption, and backing. The table below captures every significant tool discovered.

### Tier 1: Primary CLI tools

| Tool | npm Package | Weekly Downloads | Agents | Component Types | Source Types | Registry | Status |
|------|------------|-----------------|--------|----------------|-------------|----------|--------|
| **skills** (Vercel Labs) | `skills` v1.4.5 | **547,281** | 42 | Skills | GitHub, GitLab, git URL, local | skills.sh | ✅ Active (Mar 2026) |
| **openskills** | `openskills` v1.5.0 | 2,772 | ~6 named + "any AGENTS.md reader" | Skills (via AGENTS.md) | GitHub, git SSH, local | None | ✅ Active (Jan 2026) |
| **prpm** | `prpm` | — | Cursor, Claude Code, Windsurf, Copilot, Codex, Gemini, Kiro+ | Rules, commands, skills, agents, prompts, workflows | Own registry (7K+ packages) | prpm.dev | ✅ Active |
| **agent-skills-cli** | `agent-skills-cli` v1.1.7+ | — | 45 | Skills | GitHub, npm, private git, SkillsMP marketplace | SkillsMP (500K+ skills) | ✅ Active |
| **@tanstack/intent** | `@tanstack/intent` v0.0.14 | — | VS Code, Copilot, Codex, Cursor, Claude Code, Goose, Amp | Skills (npm-bundled) | node_modules | tanstack.com/intent/registry | ✅ Active (alpha, Mar 2026) |

### Tier 2: Specialized tools

| Tool | npm Package | Focus | Key Differentiator |
|------|------------|-------|-------------------|
| **@claude-collective/cli** | `@claude-collective/cli` | Claude Code | 80+ curated skill modules, "stacks" (bundled presets like `nextjs-fullstack`) |
| **skillpm** | `skillpm` | npm-based orchestration | Orchestrates npm + skills CLI + add-mcp; handles transitive dependencies |
| **skills-npm** (Anthony Fu) | `skills-npm` | npm-bundled skills | Scans node_modules for SKILL.md files, symlinks to agent dirs |
| **npm-agentskills** | `npm-agentskills` | Framework-agnostic | `agents.skills` field in package.json; has Nuxt module |
| **@omrikais/skill-manager** | `@omrikais/skill-manager` | Individual skill management | Fullscreen TUI, version rollback, usage analytics, MCP server exposure |
| **@tech-leads-club/agent-skills** | `@tech-leads-club/agent-skills` | Security-focused | Snyk Agent Scan on all skills, immutable integrity via lockfiles |

### Tier 3: Cursor/Windsurf-specific tools

| Tool | npm Package | Target | Notes |
|------|------------|--------|-------|
| **cursor-kit-cli** | `cursor-kit-cli` v1.6.0 | Cursor, Copilot, AntiGravity | Rules, commands, skills management |
| **cursor-directory** | `cursor-directory` | Cursor | Downloads rules from cursor.directory |
| **@mrzacsmith/cursor-rules** | `@mrzacsmith/cursor-rules` | Cursor | Interactive categorized rule installer |
| **@orbitant/cursor-rules** | `@orbitant/cursor-rules` | Cursor | Template-based rule/command generation |
| **rules-gen** | `rules-gen` | Cursor + Windsurf | Generates .mdc and .windsurfrules simultaneously |

### Tier 4: Marketplaces with CLI components

**Smithery** (smithery.ai) hosts **100K+ skills** with CLI installation via `npx @smithery/cli skill add`. **Tessl** (tessl.io) operates as a full prompt/context registry with semantic versioning and 10K+ library documentation "tiles." **skills.sh** (Vercel) serves as the public leaderboard for the `skills` CLI. **SkillsMP** aggregates 500K+ skills from GitHub. **SkillHub** (skillhub.club) offers 7K+ AI-evaluated skills with quality scoring.

Two distribution paradigms have emerged. **Git-based tools** (skills, openskills) clone SKILL.md files directly from GitHub repositories. **npm-based tools** (@tanstack/intent, skills-npm, npm-agentskills, skillpm) ship skills inside npm packages alongside library source code, enabling version-pinned distribution through existing dependency management. The npm approach — pioneered by TanStack and Anthony Fu — represents a significant architectural shift where library authors bundle agent skills as first-class package artifacts.

---

## 2. Skills CLI comparison: three tools, two survivors

A critical discovery: **`npx add-skill` is deprecated**. The npm package `add-skill` v2.0.0 is now a thin stub that displays a deprecation warning and redirects to `npx skills add`. Both originated from Vercel Labs. This leaves two active primary tools worth comparing in depth.

### Feature comparison matrix

| Feature | `npx skills` (Vercel Labs) | `npx openskills` (numman-ali) | `npx add-skill` |
|---------|---------------------------|------------------------------|-----------------|
| **Status** | ✅ Actively maintained | ✅ Active | ❌ **Deprecated** → redirects to skills |
| **Backing** | Vercel Labs | Independent | Vercel Labs |
| **npm downloads** | 547,281/week | 2,772/week | 3,520/week (stub) |
| **GitHub stars** | 7,500 | 8,800 | N/A |
| **Agents supported** | **42** | ~6 named + universal | 4 (historical) |
| **Architecture** | Direct symlink/copy to agent-specific directories | AGENTS.md generation + runtime `read` command | Direct file placement |
| **CLI commands** | add, remove, list, find, check, update, init | install, sync, list, read, update, manage, remove | N/A |
| **GitHub repos** | ✅ (shorthand, full URL) | ✅ | ✅ |
| **GitLab** | ✅ | ❌ | ✅ |
| **Private repos** | ✅ (SSH/HTTPS) | ✅ (SSH) | Unknown |
| **Local paths** | ✅ | ✅ | ✅ |
| **npm packages** | ❌ (use skills-npm companion) | ❌ | ❌ |
| **Registry/discovery** | **skills.sh** + `skills find` | None | None |
| **CI/CD mode** | ✅ (`-y`, `--all`, `--agent`) | ✅ (`-y`) | N/A |
| **Update management** | ✅ check + update | ✅ update | ❌ |
| **Skill scaffolding** | ✅ `skills init` | Manual | ❌ |
| **Plugin manifests** | ✅ (.claude-plugin/marketplace.json) | ❌ | ❌ |
| **Progressive disclosure** | Agent-native | ✅ Explicit via XML + `read` | Agent-native |
| **Telemetry** | ✅ (anonymous, disableable) | None | None |
| **License** | MIT | Apache 2.0 | MIT |

The architectural difference is fundamental. **`npx skills` places files directly** into each agent's configuration directory via symlinks, letting each agent handle discovery natively. **`npx openskills` generates an AGENTS.md file** containing `<available_skills>` XML that any agent can parse, with skill content loaded on-demand via `npx openskills read <name>`. The openskills approach is more universal in theory — any tool that reads AGENTS.md gets skill awareness — but the skills CLI's direct placement is simpler and more reliable across the 42 agents it explicitly supports.

The SKILL.md fields both tools read are minimal: `name` (required, lowercase with hyphens) and `description` (required). The skills CLI additionally supports `metadata.internal` for hiding skills from discovery. Neither tool handles explicit inter-skill dependencies — composition happens through prompt instructions telling the agent to invoke other skills.

**Verdict**: `npx skills` is the clear choice for most use cases given its **200x larger adoption**, Vercel backing, comprehensive agent support, and built-in discovery via skills.sh. `npx openskills` remains interesting for teams that prioritize the AGENTS.md-based universal approach or need the progressive disclosure mechanism for context-constrained environments.

---

## 3. Component hierarchy across ecosystems

### Claude Code: the deepest component model

Claude Code has the most mature and granular hierarchy of any AI coding agent. Components layer from always-on context through user-invoked commands to autonomous agent delegation:

**CLAUDE.md** sits at the foundation — persistent project instructions loaded at every session start. It functions as a memory card containing conventions, stack details, and architecture decisions. User-level (`~/.claude/CLAUDE.md`) applies globally; project-level applies per repo.

**Rules** (`.claude/rules/*.md`) provide modular, path-scoped instructions. Each rule file can target specific aspects like API conventions or testing standards. Rules are more granular than CLAUDE.md but both form the "static instruction" layer.

**Skills** (`.claude/skills/*/SKILL.md`) are the recommended primary component type. Each skill is a directory containing SKILL.md (YAML frontmatter + markdown), optional `scripts/`, `references/`, and `assets/` subdirectories. Skills create slash commands and can be auto-invoked by Claude based on description matching. Frontmatter supports `allowed-tools`, `disable-model-invocation`, `user-invocable`, `context`, `agent`, and `hooks`. Claude Code's legacy `.claude/commands/*.md` format has been merged into skills — both create slash commands, but skills support additional features.

**Agents** (`.claude/agents/*.md`) define sub-agents with their own context windows, tool access, and system prompts. The critical distinction: an agent file's content is a **system prompt, not a user prompt** — the most common misconception. Agents get separate context windows, preventing context pollution. Tool access can be whitelisted or inherited from the parent thread.

**Hooks** provide the most comprehensive lifecycle system among all agents: **15 events** (SessionStart, PreToolUse, PostToolUse, Stop, SubagentStop, UserPromptSubmit, and more) with **four handler types** (command, prompt, agent, HTTP). Prompt hooks evaluate with Haiku for lightweight checks; agent hooks spawn full sub-agents for deep verification. PreToolUse hooks can deterministically block actions — unique to Claude Code.

**Configuration precedence** flows: System/Enterprise → User (`~/.claude/`) → Project (`.claude/`) → Local (`.claude/settings.local.json`).

### Cursor: rapid catch-up with marketplace advantage

Cursor has evolved dramatically, adding skills, subagents, hooks, and a plugin marketplace between October 2025 and February 2026.

**Rules** use `.cursor/rules/*.mdc` files with four activation types: Always (every prompt), Auto Attached (glob-matched), Agent Requested (description-only until needed), and Manual (@-mention). The legacy `.cursorrules` file is deprecated but still supported.

**AGENTS.md** is natively supported — the open, vendor-neutral format stewarded by the Agentic AI Foundation under the Linux Foundation. This gives Cursor immediate interoperability with OpenAI Codex, Amp, Jules (Google), and Factory.

**Skills** (added January 2026 in Cursor 2.4) follow the SKILL.md standard with slash command invocation and auto-discovery. **Subagents** (also Cursor 2.4) run in parallel with independent context windows and configurable tool access.

**Plugins** (February 2026) represent Cursor's strongest differentiation: the top-level packaging unit that bundles skills, subagents, MCP servers, hooks, and rules. The **Cursor Marketplace** (cursor.com/marketplace) launched with partners including Amplitude, AWS, Figma, Linear, Stripe, Cloudflare, and Vercel. This is the most developed distribution channel in the ecosystem.

### Windsurf: pragmatic layering with unique memories

Windsurf centers on Cascade with a practical component set. **Rules** live in `.windsurf/rules/*.md` with four activation modes (always_on, model_decision, glob, manual) and three scopes (system/enterprise, global, workspace). **AGENTS.md** is natively supported with automatic scoping — root-level is always-on, subdirectory AGENTS.md auto-scopes to that directory.

Windsurf uniquely features **auto-generated Memories** — Cascade captures context during conversations and stores it locally for future retrieval (no credits consumed). **Workflows** (`.windsurf/workflows/*.md`) handle repeatable multi-step tasks as manual-only slash commands. **Skills** and **Hooks** are more recent additions, with hooks being less mature than Claude Code's system.

### Cross-agent comparison

| Component | Claude Code | Cursor | Windsurf |
|-----------|------------|--------|----------|
| Project instructions | CLAUDE.md | AGENTS.md + .cursor/rules | AGENTS.md + .windsurf/rules |
| Rules | .claude/rules/*.md | .cursor/rules/*.mdc (4 types) | .windsurf/rules/*.md (4 modes) |
| Skills | .claude/skills/*/SKILL.md ✅ | SKILL.md ✅ (Jan 2026) | Skills ✅ (newer) |
| Commands | Merged into skills | .cursor/commands/*.md | Workflows |
| Sub-agents | .claude/agents/*.md ✅ | Custom subagents ✅ | N/A |
| Hooks | **15 events, 4 handler types** | ~6 events, command handlers | Basic hooks |
| Plugins | Community plugins | **Marketplace** (Feb 2026) | Plugin store |
| Memories | /memory → MEMORY.md | Chat-generated | **Auto-generated** by Cascade |
| AGENTS.md | ❌ Not supported | ✅ Native | ✅ Native |

A striking irony: **Claude Code does not support AGENTS.md** despite Anthropic having helped develop the Agent Skills standard. A GitHub issue requesting AGENTS.md support (#31005) has accumulated **3,000+ upvotes** and 224 comments with zero Anthropic response after seven months. Claude Code also does not support the `.agents/skills/` path that the standard it helped create recommends, forcing tools to use `.claude/skills/` instead.

### Composition: no formal dependency graph yet

No ecosystem supports formal skill-to-skill dependencies. Composition happens through prompt instructions — a skill's markdown body can tell the agent to invoke other skills or spawn sub-agents. Cursor's plugin system comes closest to formal bundling by packaging skills + subagents + MCP + hooks + rules together. The `agent-skills-cli` has a `compose` command and `skillpm` handles transitive npm dependencies, but these are community-driven workarounds rather than spec-level features.

---

## 4. Prompts should remain inside skills, not become a separate component

The ecosystem uses "prompt" to mean many different things — system prompts, user rules, slash commands, reusable templates, skills, and context bundles. After examining the landscape, the recommendation is clear: **prompts should not become a separate first-class distributable type**. The skill format already subsumes them.

VS Code makes the taxonomy most explicit, distinguishing three tiers: **`.prompt.md`** (lightweight single-task prompts), **SKILL.md** (directory-based capabilities with scripts), and **`.agent.md`** (persistent personas with tool restrictions). This is the clearest acknowledgment that different prompt weights exist, but even VS Code bundles them under the skills umbrella for distribution.

Commands are literally prompts with slash triggers — the Claude Code documentation confirms that "the entire content of the markdown file is added as a user message." Rules (CLAUDE.md, .cursorrules, .windsurfrules) are "headless prompts" with no trigger, always injected into context. Skills are prompts with supporting infrastructure (scripts, references, assets). All are distributable through existing mechanisms.

Rather than creating a new component type, the better path is recognizing **sub-types within skills** via metadata: `type: command | guideline | template | workflow`. A single SKILL.md file with no scripts directory is already effectively a distributable prompt. The Agent Skills spec supports this lightweight case with zero overhead.

**Tessl** (tessl.io) provides the most sophisticated model for prompt distribution today: versioned "tiles" that can contain skills, rules, documentation, and prompts together as a single installable package with semantic versioning and evaluation frameworks. This demonstrates that the distribution unit should be a **bundle** (tile/plugin), not a raw prompt file.

The gap is not a missing "prompt" type but rather **better tooling for distributing passive context layers** — rules, guidelines, and documentation that complement active commands/skills. Tools like `prpm` (which already handles rules, commands, skills, agents, and prompts across IDEs with 7K+ packages) and Tessl are filling this gap.

---

## 5. Gaps with no distribution mechanism

Several component types lack standardized distribution:

- **Hooks**: No tool distributes hook configurations. Claude Code's 15-event hook system and Cursor's growing hook support have no packaging or sharing mechanism. This is the largest gap — hooks are powerful but entirely manual to configure.
- **MCP server configurations**: While `skillpm` and `add-mcp` handle some MCP wiring, there's no standardized way to distribute `.mcp.json` configurations as part of a skill. Cursor's plugin marketplace bundles MCP servers inside plugins, pointing toward a solution.
- **Agent definitions**: Claude Code's `.claude/agents/*.md` sub-agent definitions have no dedicated distribution tool. They can be included inside skills but aren't independently discoverable or installable.
- **Cross-agent rules**: While skills have a universal format (SKILL.md), rules do not. Claude Code uses `.claude/rules/*.md`, Cursor uses `.cursor/rules/*.mdc`, and Windsurf uses `.windsurf/rules/*.md` — each with different frontmatter schemas. No tool translates between them.
- **Memories**: Windsurf auto-generates memories, Claude Code has `/memory`, but there's no way to share or distribute learned memories across team members or projects.
- **Skill dependency graphs**: No spec-level mechanism exists for declaring that skill A requires skill B. All composition is ad-hoc via prompt instructions.

---

## 6. What to adopt versus what to build

### Adopt immediately

**`npx skills` (Vercel Labs)** is the clear default for skill distribution. With 547K weekly downloads, 42 agent support, the skills.sh registry, and Vercel backing, it is the npm of the agent skills world. Its symlink-based approach is reliable and its `find`, `check`, and `update` commands provide complete lifecycle management.

**The SKILL.md / Agent Skills specification** (agentskills.io) should be the format for any distributable component. Adopted by Anthropic, OpenAI, Microsoft, Google, and 30+ agents, it has achieved critical mass. Building on any other format is a losing bet.

**Cursor's plugin marketplace** model is worth watching closely for organizations wanting to distribute bundled component sets (skills + hooks + MCP + rules). It's the only ecosystem with a formal plugin packaging and discovery channel backed by a major vendor.

### Consider adopting

**`@tanstack/intent`** represents the future for library maintainers. Shipping skills inside npm packages — version-pinned, updated via `npm update`, with staleness detection — solves the version mismatch problem that git-based tools don't address. It's alpha-stage but architecturally sound.

**`prpm`** (prpm.dev) is worth evaluating for teams needing cross-format support beyond just skills — it handles Cursor rules, Claude agents, slash commands, Windsurf rules, and prompts with 7K+ packages in its registry.

**`openskills`** remains valuable for the AGENTS.md-based universal loading pattern, particularly for teams working across many agents that support AGENTS.md (which notably excludes Claude Code).

### Build (or contribute to)

**Hook distribution** is the clearest build opportunity. No tool packages or shares hook configurations. A `hooks.json` spec that can be installed alongside skills would fill the largest gap in the ecosystem.

**Cross-agent rule translation** is needed. A tool that reads `.cursor/rules/*.mdc` and generates `.claude/rules/*.md` and `.windsurf/rules/*.md` (or vice versa) would solve a real pain point for multi-agent teams.

**Skill dependency resolution** at the spec level would mature the ecosystem significantly. The current approach of embedding composition instructions in prompt text is fragile. Contributing a `dependencies` field to the Agent Skills specification — similar to npm's `package.json` — would be a high-impact contribution.

**AGENTS.md support for Claude Code** remains the community's most-requested feature. Until Anthropic acts, workarounds like symlinks (`ln -s AGENTS.md CLAUDE.md`) or tools that auto-generate CLAUDE.md from AGENTS.md represent a niche but needed build opportunity.

## Conclusion

The AI coding agent component ecosystem has moved from fragmented experimentation to rapid standardization in roughly four months. The Agent Skills spec has won the format war. Vercel's `skills` CLI has won the distribution war (for now). But significant gaps remain in hook distribution, cross-agent rule portability, and dependency resolution. The most important architectural insight is that **skills have become the universal container** — not just for commands and capabilities but for any distributable prompt-like component. Organizations should standardize on SKILL.md, adopt `npx skills` for distribution, and focus build efforts on the hook and composition gaps that no existing tool addresses.
