# Ultrathink

In case you have not heard you can adjust the degree to which Claude utilises test-time compute. Adding ultrathink within your prompt indicates to Claude that he should give it his all thinking wise.

### Ultrathink & Plan Mode

I personally get outstanding results using ultrathink + Plan Mode with Claude Sonnet 4.5. This combination is especially useful when you don't want to reach for Claude 4 Opus. I have found it can often bridge the intelligence gap for complex tasks, and when that's not sufficient, I opt to rev the model by performing multiple critiqued rounds of ultrathink + Plan Mode.

### Revving the Engine

Revving the engine means instructing Claude to create a plan in Plan Mode, then systematically critiquing that plan for missing edge cases, redundant aspects, and ordering inefficiencies. This iterative process pushes the model through multiple thinking cycles to reach higher performance.

### The Ultimate Stack

If you are struggling to get the performance from ultrathink + Sonnet + Plan Mode + revving you can throw sub-agents into the mix. Requesting Claude to use split role sub-agents to analyse task or plan where each sub-agent has a different role which influences its suggestions towards the plan.

This tactic is token efficient thanks to utilising Sonnet and is scalable regarding to how many sub-agents/roles are utilised and the degree of thinking applied.

### Why Ultrathink Before Opus

ultrathink is a must utilise mechanic which ideally should be used in combinations with the other available mechanics prior to reaching for a superior model like Opus.

Why? Because otherwise you are learning to be unnecessarily reliant on a model which is 5X more expensive without delivering 5X more value.

### The Complete Stack

- **Base**: ultrathink for enhanced thinking.
- **Planning**: Plan Mode for structured approach.
- **Iteration**: revving for multiple critique rounds.
- **Perspectives**: split role sub-agents for diverse analysis.
- **Hybrid Intelligence**: Opus Plan Mode for automatic Opus planning with Sonnet execution.

### Compute Optimization

The above mechanics reveal the hidden potential in systematic mechanic stacking. By combining ultrathink, Plan Mode, revving, and split role sub-agents, you unlock intelligence amplification that transforms how complex problems get solved.
