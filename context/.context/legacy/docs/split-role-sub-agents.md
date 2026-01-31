# Split Role Sub-Agents

A fascinating mechanic the [Reddit community](https://www.reddit.com/r/ClaudeAI/) brought to my attention is the ability to designate different roles to sub-agents.

### The Role Foundation

Anthropic have [openly discussed](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts) providing Claude with a Role which helps get him in the zone for the task at hand, for example:

> Your role is as a seasoned security expert which specialises in pen testing.

Multiple members of the community have created sophisticated tools for orchestrating sub-agent roles. [SuperClaude](https://claudelog.com/claude-code-mcps/super-claude/) provides 9 cognitive personas (architect, frontend, backend, security, analyzer, qa, performance, refactorer, mentor) that can be applied as universal flags to any command. [Claudia](https://claudelog.com/claude-code-mcps/claudia/) offers custom AI agents with tailored system prompts through a GUI interface for coordinating different agent roles.

### Native Implementation

However, I am old school and love exploring a tool's raw mechanics without third-party dependencies. So I experimented with asking Claude to Utilise multiple sub-agents to validate this code from multiple perspectives.

### Sub-Agent Coordination Strategy:

- **Setup Phase** - Ensure Claude is in [Plan Mode](https://claudelog.com/mechanics/plan-mode/) and that [ultrathink](https://claudelog.com/mechanics/ultrathink/) is instantiated.
- **Role Suggestion** - Claude automatically suggests various relevant roles applicable to the task.
- **Perspective Selection** - Select the kind of perspectives you want the task reviewed from.
- **Parallel Analysis** - Sub-agents complete their review using their specialized approaches.
- **Consolidation** - Findings are consolidated and presented by Claude.

Perspective Selection Examples:

After multiple successful attempts it becomes second nature to suggest quirky perspectives for Claude to analyse tasks/problems from different perspectives.

#### Code Review Tasks:

```
Create sub-agents and analyse the problem from the following perspectives:
factual, senior engineer, security expert, consistency reviewer, redundancy checker
```

#### User Experience Tasks:

```
Create sub-agents and analyse the problem from a:
creative, nooby user, designer, marketing, seo perspective
```

#### Documentation Tasks:

```
Create sub-agents to review this documentation from the following perspectives:
technical accuracy, beginner accessibility, SEO optimization, content clarity
```

Interestingly enough each perspective naturally gravitates toward different tools based on their role and problem-solving approach. This creates a more comprehensive analysis as different agents instinctively choose the most relevant combination of tools for their domain of expertise.

#### Performance & Cost Optimization:

This mechanic delivers exceptional value by maximizing Claude Sonnet 4.5's capabilities through strategic orchestration. Rather than reaching for the 5x more expensive Opus model, split role sub-agents combined with [ultrathink](https://claudelog.com/mechanics/ultrathink/) unlock sophisticated analysis at Sonnet pricing. The parallel nature of [Task](https://claudelog.com/mechanics/task-agent-tools/) execution means multiple expert roles can analyze the same problem simultaneously, creating multiple insights that would be difficult to achieve through single-role analysis (due to previous roles and context influencing the context window).

#### Beyond Coding Applications

This mechanic applies beyond coding! I have used noob, seo, engineer, vibe coder, non-coder perspectives to get additional opinions on aspects of ClaudeLog and it all happens in parallel safely within [Plan Mode](https://claudelog.com/mechanics/plan-mode/).

The beauty of split role sub-agents lies in their scalability - you can adapt the perspective combinations to any domain or problem type. Start with the fundamental technical perspectives, then experiment with creative combinations as you discover what insights each role type reveals. [A.B.E](https://claudelog.com/mechanics/always-be-experimenting/) (Always be experimenting)

### Multi-Perspective Analysis

The power of split role sub-agents lies in their ability to surface insights you neither a single Claude instance could surface alone. Each perspective uses different tools and approaches, creating a comprehensive analysis that dramatically improves decision quality.

### Pushing the Limit

Utilise Claude Sonnet 4.5 + [Plan Mode](https://claudelog.com/mechanics/plan-mode/) + ultrathink + role sub-agents to extract the maximum performance from the Claude Sonnet 4.5 model, prior to reaching for the 5x more expensive and often overkill Claude 4 Opus model.
