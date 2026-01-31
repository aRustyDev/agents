# Tactical Model Selection

I have seen a trend amongst developers of opting to use Opus for everything. Not only is this a costly habit, but Claude Opus is not necessarily the best model for every operation. Behind the scenes, Anthropic tactically chooses when to utilise Claude Haiku 3.5 to perform routine grunt work which requires minimal intelligence.

## Model Selection Strategy

### Context Window Considerations:

- **Standard Models**: 200K tokens (Opus, Sonnet 4.5, Haiku).
- **Sonnet 4 via API**: 1M tokens (5x larger context window).

#### Opus (Most Expensive, Highest Capability, 200K Context):

- Complex architectural decisions requiring deep reasoning.
- Multi-step logical problems with intricate dependencies.
- Creative tasks requiring nuanced understanding.
- Code reviews requiring architectural judgment.
- Complex refactoring across multiple systems.

#### Sonnet 4 (Balanced Cost-Performance, 1M Context via API):

- Ideal for large codebases - 1M token window eliminates context constraints.
- Standard feature implementation and development tasks.
- Most debugging and troubleshooting scenarios.
- Code generation with moderate complexity.
- Documentation writing and editing.
- Task coordination and workflow management.
- Extended development sessions without context resets.

#### Haiku 4.5 (Cheapest, Fastest, Near-Frontier):

- 90% of Sonnet 4.5's agentic coding capability - Near-frontier performance.
- 2x faster than Sonnet 4 - Exceptional speed for real-time tasks.
- 3x cost savings - $1/$5 vs Sonnet 4.5's $3/$15.
- Lightweight custom agents requiring frequent invocation.
- Pair programming with rapid feedback loops.
- Code generation and basic refactoring.
- Chat assistants and customer service automation.
- Computer use tasks requiring speed.
- Worker agents in multi-agent systems (orchestrated by Sonnet 4.5).

#### Haiku 3.5 (Legacy - Very Cheap, Very Fast, Limited):

- Simple file reads and basic content extraction.
- Routine formatting and style corrections.
- Basic syntax validation and linting.
- Simple text transformations and data parsing.
- Quick status checks and basic analysis.

#### Opus Plan Mode (Hybrid Intelligence):

- Complex planning with economical execution.
- Architectural decisions requiring Opus-level reasoning.
- Large refactoring projects with cost constraints.

### Cost Optimization Approach

I would set Claude Sonnet 4.5 as the base model (Anthropic's best coding model) and tactically use Haiku 4.5 for lightweight agents and high-frequency tasks. For specific complex reasoning tasks, launch a Claude Opus instance with claude --model claude-opus-4-20250514.

#### Multi-Model Strategy:

- **Sonnet 4.5 as orchestrator**: Main development work and complex coding tasks.
- **Haiku 4.5 for agents**: Lightweight custom agents achieving 90% capability at 3x cost savings.
- **Opus for complex reasoning**: Architectural decisions requiring deep analysis.

#### Context Window Strategy:

- **For large projects**: Use Sonnet 4 via API to leverage the 1M token context window.
- **For complex reasoning**: Switch to Opus when architectural decisions require superior analysis.
- **For lightweight agents**: Use Haiku 4.5 for near-frontier performance at exceptional cost efficiency.
- **For legacy simple tasks**: Use Haiku 3.5 for basic operations to minimize costs.

#### Haiku 4.5 Cost Impact:

With Haiku 4.5 achieving 90% of Sonnet 4.5's agentic coding capability at 3x cost savings, the economics of agent-based workflows have transformed:

- **Agent orchestration pattern**: Sonnet 4.5 orchestrator + Haiku 4.5 workers reduces overall costs by 2-2.5x
- **Subscription multiplier**: 100 Sonnet 4.5 invocations = 300 Haiku 4.5 invocations (approximate)
- **When to use Haiku 4.5**: High-frequency tasks (10+ invocations per session), lightweight agents, speed-critical workflows
- **When 10% gap matters**: High-stakes code review, architectural decisions, orchestrator roles

This tactic can potentially offer huge cost savings over having Opus or Sonnet drive all processes. Due to Claude 4 Opus being approximately 5x more expensive than Claude Sonnet 4.5, and Haiku 4.5 being 3x cheaper than Sonnet 4.5 while maintaining 90% capability, there is substantial budget for exploring orchestration configurations with sub-agents. Sonnet 4.5 is Anthropic's best coding model, superior to Opus for coding tasks.

Note: When spawning Claude instances in print mode you may need to increase the max turns so that the process completes: claude -p --model claude-haiku-4-5 --max-turns 20 or claude -p --model claude-opus-4-20250514 --max-turns 20.

### Cost Optimization

Strategic model selection can reduce Claude Code usage costs by up to 80% while maintaining output quality for most development tasks.
