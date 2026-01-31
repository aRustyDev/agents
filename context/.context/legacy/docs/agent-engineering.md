# Agent Engineering

We've evolved through three distinct eras of AI interaction: from Prompt Engineering (crafting perfect individual prompts) to Context Engineering (optimizing the context, what goes into it and what remains in it through CLAUDE.md files) and now to Agent Engineering (designing specialized, reusable, efficient AI agents). At each stage, our ability to share deliverables and grow as a community has expanded: from sharing individual prompts, to sharing comprehensive context configurations and tactics, to now sharing complete portable agent definitions that work across any project.

Custom agents represent this latest paradigm shift in Claude Code workflows from manual orchestration to automatic delegation, from project-specific solutions to portable specialist tools. This guide covers the essential foundations you need to understand before diving into advanced tactics.

Understanding the Agent Ecosystem

Comparison: Custom Agents vs. Sub-agents vs. Task Tools

| Aspect                | Custom Agents                     | Split Role Sub-agents      | Task/Agent Tools        |
| --------------------- | --------------------------------- | -------------------------- | ----------------------- |
| Token Efficiency      |                                   |                            |                         |
| Activation            | Automatic delegation              | Manual delegation          | Manual delegation       |
| Shared System Prompt  | No                                | Yes                        | Yes                     |
| Portability           | Highly portable (single .md file) | Impractical                | Impractical             |
| Configuration         | YAML frontmatter + system prompt  | Task description only      | Task description only   |
| System Prompt         | Custom system prompt access       | Inherits system prompt     | Inherits system prompt  |
| Custom Tool Selection | Yes                               | No                         | No                      |
| Claude.md Inheritance | Yes                               | Yes                        | Yes                     |
| Use Case              | Specialized repeatable tasks      | Multi-perspective analysis | Parallel task execution |

Custom agents deliver automatic activation, isolated contexts, and surgical tool selection, eliminating the token bloat and manual orchestration of previous approaches.

### Custom Agent Design

I believe one of the most important aspects when designing custom agents is to carefully engineer how many tokens your custom agent needs to initialize. Optimizing this serves multiple purposes: to improve initialization speed, reduce cost, maintain [peak performance](https://claudelog.com/mechanics/context-window-depletion/), and enable efficient chaining.

Each custom agent invocation carries a variable initialization cost based on tool count and configuration complexity. Design decisions should account for this:

Performance Analysis by Tool Count (Anecdotal experiment):

| Tool Count | Token Usage | Relative Initialization Time | Claude.md Empty |
| ---------- | ----------- | ---------------------------- | --------------- |
| 0          | 640         | 2.6s                         | true            |
| 1          | 2.6k        | 3.9s                         | false           |
| 2          | 2.9k        | 4.3s                         | false           |
| 3          | 3.2k        | 6.0s                         | false           |
| 4          | 3.4k        | 6.1s                         | false           |
| 5          | 3.9k        | 5.1s                         | false           |
| 6          | 4.1k        | 7.0s                         | false           |
| 7          | 5.0k        | 6.9s                         | false           |
| 8          | 7.1k        | 5.6s                         | false           |
| 9          | 7.5k        | 5.1s                         | false           |
| 10         | 7.9k        | 6.2s                         | false           |
| 15+        | 13.9k - 25k | 6.4s                         | false           |

> Note: The 0 tool experiment was conducted with a completely empty Claude.md and thus reflects the best case scenario. Experiments for 1-15+ tools were conducted with a non-empty Claude.md. Token cost and initialization time were affected by the specific tools which were added.

#### Agent Weight Classifications:

- **Lightweight agents**: Under 3k tokens - Low initialization cost.
- **Medium-weight agents**: 10-15k tokens - Moderate initialization cost.
- **Heavy agents**: 25k+ tokens - High initialization cost.

**Subscription and Model Optimization**: A lightweight, performant custom agent will be used and experimented with more than a heavyweight custom agent due to subscription constraints. They are by far the most composable and effortless to use. We should strive to make our custom agents as performant and composable as possible.

**Model Selection Strategy**: With the introduction of the model parameter in v1.0.64, you can now specify which model each agent should use (sonnet, opus, haiku). Claude Haiku 4.5 (released October 2025) has transformed agent engineering economics by delivering 90% of Sonnet 4.5's agentic coding performance at 2x the speed and 3x cost savings ($1/$5 vs $3/$15).

#### Access Haiku 4.5:

- **Command line**: --model claude-haiku-4-5
- **Agent configuration**: model: haiku in YAML frontmatter

#### Proven Pairings (Based on Haiku 4.5 Performance):

- **Haiku 4.5 + Lightweight Agent**: Achieves 90% of Sonnet 4.5's agentic performance with 2x speed and 3x cost savings - ideal for frequent-use agents requiring near-frontier capabilities at minimal cost.
- **Sonnet 4.5 + Medium Agent**: Balanced approach for moderate complexity tasks requiring maximum reasoning capability.
- **Opus 4 + Heavy Agent**: Complex analysis requiring deepest reasoning and context understanding.

#### Advanced Experimentation Patterns (Emerging Best Practices):

- **Haiku 4.5 + Medium Agent**: Given 90% agentic performance, Haiku 4.5 can handle medium-weight agents efficiently - experiment with expanding this boundary.
- **Opus 4 + Lightweight Agent**: May unlock surprising depth in specialized reasoning tasks - unproven but worth testing.
- **Model Rotation**: Same agent with different models for A/B testing to quantify the 10% capability gap in your specific use case.
- **Dynamic Model Selection**: Start with Haiku 4.5, escalate to Sonnet 4.5 if validation fails - emerging pattern for cost optimization.

**Community Knowledge** (October 2025 onwards): Haiku 4.5's release established concrete performance baselines, reducing some uncertainty. However, optimal model-agent pairings remain highly context-dependent. Continue benchmarking and sharing discoveries - what works for one use case may revolutionize another.

**Agent Chainability Impact**: The complexity of a custom agent significantly affects its chainability due to startup time and token usage. Heavy custom agents (25k+ tokens) create bottlenecks in multi-agent workflows, while lightweight custom agents (under 3k tokens) enable fluid orchestration. As future Agent Engineers, we must optimize both individual custom agent metrics and their composability:

- **Individual Optimization**: Minimize tool count while preserving capability.
- **Composition Strategy**: Balance specialized high-cost custom agents with efficient ones (Similar to the [big.LITTLE](https://en.wikipedia.org/wiki/ARM_big.LITTLE) concept from CPU design).
- **Workflow Design**: Consider cumulative token costs when chaining multiple custom agents.
- **Performance Monitoring**: Track custom agent efficiency metrics across different use cases.

#### Proven Multi-Agent Orchestration Pattern:

The Haiku 4.5 release validated a specific orchestration architecture that maximizes efficiency:

    Sonnet 4.5 as orchestrator: Handles complex task decomposition, coordination, and quality validation.
    Haiku 4.5 as worker agents: Executes specialized subtasks with 90% of Sonnet 4.5's capability at 3x cost savings.
    Cost efficiency: This pattern reduces overall token costs by 2-2.5x while maintaining 85-95% overall quality.
    Speed advantage: Parallel Haiku 4.5 workers operating at 2x speed create significant throughput gains.

#### Example orchestration workflow:

- Sonnet 4.5 analyzes requirements and creates execution plan
- Sonnet 4.5 delegates discrete tasks to multiple Haiku 4.5 agents in parallel
- Haiku 4.5 workers execute at 2x speed with 90% capability
- Sonnet 4.5 validates outputs and integrates results

### Cost-Benefit Analysis for Model Selection

Understanding the economics of agent model selection is critical for sustainable agent engineering. Haiku 4.5's release provides concrete data for cost-benefit analysis:

Token Cost Comparison (per 1M tokens):

| Model      | Input | Output | Total Cost\* | Performance       | Cost Efficiency                        |
| ---------- | ----- | ------ | ------------ | ----------------- | -------------------------------------- |
| Haiku 4.5  | $1    | $5     | ~$3.00       | 90%               | agentic Baseline                       |
| Sonnet 4.5 | $3    | $15    | ~$9.00       | 100%              | agentic 3x more expensive for 11% gain |
| Opus 4     | $15   | $75    | ~$45.00      | Maximum reasoning | 15x more expensive                     |

\*Assumes typical 50% input / 50% output ratio

Break-Even Analysis for Lightweight Agents:

For lightweight agents (under 3k tokens initialization):

- Haiku 4.5: 3k tokens ≈ $0.009 per invocation at $3/M blended rate
- Sonnet 4.5: 3k tokens ≈ $0.027 per invocation at $9/M blended rate
- Savings: 3x cost reduction per invocation

When the 10% capability gap matters:

- High-stakes code review requiring maximum safety validation
- Complex architectural decisions with significant downstream impact
- Tasks where quality degradation cascades through multi-agent workflows
- Orchestrator roles coordinating multiple sub-agents

When the 10% gap is acceptable:

- Frequent-use agents (invoked 10+ times per session)
- Pair programming assistance and code generation
- Chat interfaces and customer service responses
- Computer use tasks requiring speed over perfection
- Worker agents in multi-agent systems (Sonnet 4.5 orchestrator validates)

Subscription Constraint Strategy:

For users on Claude Code Pro subscription limits, strategic model selection dramatically extends usage:

- 100 Sonnet 4.5 invocations = 300 Haiku 4.5 invocations (approximate token equivalent)
- This 3x multiplier effect makes Haiku 4.5 agents substantially more composable
- Design agent collections with Haiku 4.5 as default, Sonnet 4.5 for validation

### When to Use Custom Agents

Custom agents excel in the same scenarios as [split role sub-agents](https://claudelog.com/mechanics/split-role-sub-agents/), but with enhanced portability and automatic activation:

#### Specialized Domain Tasks

- **Code Review** - Security, performance, maintainability analysis.
- **Research Tasks** - API documentation, library comparison, best practices.
- **Quality Assurance** - Testing strategies, edge case identification.
- **Documentation ** - Technical writing, SEO optimization, accessibility.
- **Design Analysis** - UX review, layout assessment, design consistency.
- **Content Quality** - Legibility expert, grammar expert, brand voice expert.

#### Portable Workflows

Unlike sub-agents tied to specific projects, custom agents can be refined once and utilized across multiple projects, making them ideal for:

- Cross-project standards enforcement.
- Team workflow standardization.
- Personal expertise amplification.
- Community knowledge sharing.

### Essential Features

#### No CLAUDE.md Inheritance

Major Advantage: Unlike traditional sub-agents, custom agents are designed to not automatically inherit the project's CLAUDE.md configuration. This prevents context pollution and ensures consistent behavior across projects. You can verify this with a [sanity check](https://claudelog.com/mechanics/sanity-check/).

#### Coloring Your Custom Agent

Custom agents can be visually distinguished through terminal color formatting in their indicator, making it easier to track which agent is responding during complex workflows. This helps maintain clarity when multiple agents are active or when reviewing conversation history.

#### Agent Nicknaming for Efficiency

Configure short nicknames for frequently used agents:

- **UX agent** (A1) - Quick UX analysis.
- **Security agent** (S1) - Rapid security review.
- **Performance agent** (P1) - Performance optimization.

Example configuration with nickname:

```markdown
---
name: UX Agent (A1)
description: UX specialist for user experience analysis. Use this agent when evaluating interfaces and user workflows.
tools: Read, Grep, Glob
---

You are a UX specialist focused on user experience analysis and interface evaluation.

When invoked:

1. Analyze user interface elements and workflows
2. Identify usability issues and improvement opportunities
3. Provide actionable UX recommendations
4. Consider accessibility and user journey optimization
```

Calling the agent with nickname:

```markdown
ask agent a1 to review the navigation menu UX
```

or:

```markdown
ask a1 to review the navigation menu UX
```

#### Advanced Nickname Workflows

The ability to provide nicknames to custom agents helps to improve manual invocation and opens up possibilities like calling custom agents via nicknames A1, P2, C1.

```markdown
ask A1, P2, C1 to review the changes
```

#### Configuring Automatic Delegation

Custom agents are automatically utilized by the delegating agent based on the task description within your prompt, the description field within your custom agent configuration, the current context and available tools.

When crafting your custom agents you will need to evaluate Claude's reliability at invoking your custom agent. If you need to improve the reliability, explore updating your agent's name, description or system prompt. Configuring your custom agent to be promptly utilized by Claude is a form of Tool SEO.

Anthropic has mentioned that to encourage proactive custom agent use we should include terms like use PROACTIVELY or MUST BE USED in the description fields of our custom agents. This functions similarly to how you would use such terms to get good adherence out of Claude by correctly formatting your Claude.md.

### Design Considerations

#### Getting Started Strategy

##### Token-First Design:

- Create focused, single-purpose agents initially.
- Start with lightweight agents (minimal or no tools) for maximum composability.
- Carefully engineer how many tokens your custom agent needs to initialize.
- Prioritize efficiency over capability for frequent-use agents.

##### Configuration Best Practices:

- Use clear, specific descriptions for reliable auto-activation.
- Grant only necessary tools initially, expand as needed.
- Choose appropriate models: Start with Haiku 4.5 for most agents (90% agentic capability), use Sonnet 4.5 for orchestration and maximum quality validation.
- Test agent reliability before expanding.
- Include examples in system prompts for better pattern recognition.
- Test agents in isolation before deploying in workflows.
- Design for chainability and multi-agent piping.
- Match model to agent weight: Haiku 4.5 now handles lightweight AND many medium-weight agents efficiently - only escalate to Sonnet 4.5 when the 10% capability gap impacts outcomes.
- Frequently test agents and share them with others to help validate effectiveness.

#### Model Selection Strategy

The model parameter opens unexplored possibilities in agent engineering. This is frontier territory - approach with experimental curiosity rather than rigid rules.

##### Performance Capabilities (Based on Haiku 4.5 Data):

- Haiku 4.5 agents: Near-frontier agentic coding (90% of Sonnet 4.5), pair programming, code generation, chat assistants, customer service, computer use tasks - significantly more capable than previous assumptions. Best for frequent-use agents where 2x speed and 3x cost savings justify 10% capability tradeoff.
- Sonnet 4.5 agents: Maximum agentic performance, complex orchestration, deep reasoning, quality validation - ideal for orchestrator roles and tasks requiring frontier capabilities.
- Opus 4 agents: Deepest reasoning for research, complex analysis, and tasks requiring maximum context understanding and nuanced decision-making.

##### Cost-Benefit Decision Framework:

- Choose Haiku 4.5 when: Frequency of use is high, 90% capability is sufficient, speed matters, subscription costs are constrained.
- Choose Sonnet 4.5 when: Maximum capability required, orchestrating multi-agent workflows, quality validation critical.
- Choose Opus 4 when: Deepest reasoning needed, complex research tasks, maximum context comprehension essential.

##### Experimental Discovery Framework:

- **Challenge assumptions**: Test whether "simple" tasks benefit from opus intelligence.
- **Reverse expectations**: Try Haiku on complex agents to find efficiency breakthroughs.
- **Benchmark systematically**: Measure actual performance vs. theoretical predictions.

##### Discovery-Oriented Lifecycle:

- **Start with conventional pairing**: Establish baseline performance.
- **Cross-experiment**: Test unconventional model/agent combinations.
- **Measure everything**: Token usage, token cost, speed, quality, user satisfaction.
- **Share breakthrough discoveries**: Contribute findings to expand collective knowledge.
- **Iterate based on real data**: Let empirical results guide optimization, not assumptions.

**Community Collaboration**: The agent engineering community should actively share benchmarking results and surprising discoveries. What works for one use case might revolutionize another.

#### Getting Started

Start with one simple, focused custom agent that solves a specific problem you encounter regularly. Test its effectiveness and refine its description based on how reliably Claude invokes it automatically.

#### Experimental Approach

While efficiency matters, don't let optimization assumptions limit discovery. A heavy agent with Haiku might surprise you with efficient performance, or a "simple" agent with opus might unlock unexpected capabilities.

#### Foundation First

Master the fundamentals of custom agents before diving into complex chaining. A solid understanding of these foundations will enable more effective chaining and increased usage frequency.
