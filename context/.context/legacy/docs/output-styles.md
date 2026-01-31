# Output Styles

Over the months of using Claude Code daily, I have observed a clear trend: Anthropic progressively removing constraints and empowering us to shape Claude Code into the perfect tool for our varied tasks. We started with basic CLAUDE.md customization and simple [sub-agents](https://claudelog.com/mechanics/sub-agents/). Then came --append-system-prompt, letting us adjust Claude's behavior while keeping the software engineering focus. Most recently, we gained fully customizable sub-agents with isolated system prompts, custom tool selection, and separate context windows.

Anthropic has been on a roll, dropping more and more mechanics in Claude Code week over week. However, a major foundational constraint has been that the delegating agent was always steered at a system level to be an assistant for software development. With the release of Output Styles, the delegating agent can be customized in the same manner as the customizable sub-agents.

Interestingly enough, this unlocks the possibility for Claude Code being Claude Anything, since the system prompt is no longer steering the base model towards code.

This is new ground so I am fascinated to explore having a specialised delegating agent, to match and control my [Custom Agents](https://claudelog.com/mechanics/custom-agents/).

### Untapped Potential

Unlike other Claude Code mechanics that augment or delegate from the base software engineering behavior, Output Styles completely replace the core personality while preserving all the powerful capabilities that make Claude Code exceptional.

**What stays**: CLAUDE.md project context system, complete tool ecosystem, sub-agent/Custom Agent delegation, MCP integrations, context management, automation workflows, file system operations, project continuity.

**What changes**: System prompt personality, domain assumptions, task prioritization, interaction patterns, response formatting.

By removing software engineering assumptions at the system prompt level, each domain gets a cleaner, more focused experience. No [context pollution](https://claudelog.com/mechanics/poison-context-awareness/) from irrelevant expertise areas means better performance in their specific domains. The tool adapts its reasoning patterns to match domain-appropriate thinking rather than forcing domain experts to work within software engineering paradigms.

Crucially, it will communicate with you using the language, density, and verbosity appropriate for its role.

### How This Differs from Other Mechanics

Understanding Output Styles requires seeing how they fundamentally differ from Claude Code's other customization approaches:

#### vs CLAUDE.md

    CLAUDE.md: Creates an instruction adherence hierarchy that adds project context, workflows, and process definitions within the existing software engineering framework.
    Output Styles: Completely replaces the software engineering system prompt with domain-specific behavioral instructions, removing coding assumptions entirely.

#### vs --append-system-prompt

    --append-system-prompt: Augments Claude's existing software engineering behavior with specialized focus areas (security, performance, database expertise) while maintaining core helpful coding assistant nature.
    Output Styles: Removes software engineering assumptions entirely and substitutes completely different domain expertise and interaction patterns.

#### vs Custom Agents

    Custom Agents: Create specialized assistants with isolated contexts, custom system prompts, and tool selection that automatically activate for specific tasks while the main agent remains software-focused.
    Output Styles: Transforms the main delegating agent personality and domain assumptions rather than creating separate specialists.

#### vs Sub-agents

    Sub-agents: Enable manual orchestration using the [Task tool](https://claudelog.com/mechanics/task-agent-tools/) for parallel processing and multi-perspective analysis while inheriting the main software engineering system prompt.
    Output Styles: Changes the fundamental assumptions about what types of tasks are appropriate and how to approach them from the ground up.

### Cross-Domain Applications

This is where the Claude Anything vision becomes reality. Output Styles unlock Claude Code's capabilities for entirely new domains:

- **Content Strategy** - Create brand-specific content specialists that speak only in your brand's voice and maintain brand values throughout all interactions. Analyze markdown files, reorganize documentation structure, and optimize for audience engagement while helping you think from your brand's perspective. Train team members to adopt consistent brand thinking patterns and responses to similar problems.
- **Research Analysis** - Process academic papers with consistent structure and formatting, always collating and citing sources verbatim without interpretation. Organize findings systematically across files while maintaining research project tracking with full file system integration for reliable, unbiased information delivery.
- **Business Analysis** - Create domain-specific analysts tailored to your exact field, such as law-oriented specialists that use the precise level of specificity needed to ensure unambiguous communication. Examine data files, generate reports, and track project metrics with industry-appropriate terminology and standards.
- **Design Systems** - Experiment with SVG specialists who are trained to make incremental changes to vector graphics with deep knowledge of design standards and SVG specifications. Audit component libraries, analyze usage patterns, and maintain consistency documentation with complete file manipulation capabilities.

Each domain gets Claude Code's full toolset adapted to their specific thinking patterns and needs.

I am looking forward to seeing the new cross-domain pollination possibilities and exploring what the community develops at [r/ClaudeAI](https://www.reddit.com/r/ClaudeAI/).

### Domain Transformation

Start with one focused output style for your primary domain. Test how it changes Claude's reasoning patterns and communication style before creating multiple specialists.

### Platform Evolution

Output Styles transform Claude Code from software engineering tool to universal intelligent platform. The same powerful capabilities, adapted to any domain's specific needs and thinking patterns.
