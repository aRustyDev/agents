# Sub-agent Tactics

Many folks on the [Claude AI subreddit](https://www.reddit.com/r/ClaudeAI/) have been asking:

> How do I utilise sub-agents to perform tasks?

### Understanding Task Types

There are different aspects you must take into account before utilising sub-agents. Firstly, whether the task is non-destructive or potentially destructive and the kinds of dependencies that exist within the task you are intending to action.

### Perfect Parallelizable Tasks

If you have a task where you want Claude to research 8 different MCPs and write up a report of their pros/cons and how they can be applicable to the goals defined in your vision.md. This is a perfect task for parallelisation because each Claude is working in isolation and does not interfere with the existing codebase or each other, they can provide all their finding to the main Claude agent or write individual findings files which can be read and consolidated by the main Claude agent.

This task being non-destructive and easily parallelisible is the kind of thing you should immediately jump to utilise sub-agents for.

### Developing an Itch for Parallelism

After performing multiple parallel tasks of this type you should begin to develop an itch for parallelism.

Another example is reviewing diffs prior to committing. I often utilise sub-agents to perform parallel, redundancy, security, factuality, time-complexity checks. After all, they run in parallel so it does not hurt to instantiate sub-agents. Prior to instantiating the sub-agents, I would enter Plan Mode to ensure the task is executed in a non-destructive way since the sub-agents could potentially attempt to make file changes.

### The Consolidation Strategy

My goal with this tactic is to consolidate the suggestions and then action on them from a single Claude model, often after clearing the context to allow him to start on his best foot.

Day by day, week by week I find myself learning to utilise sub-agents in more and more creative ways! Who knows what new mechanic next week will bring.

### How to Use Sub-agents

To answer the original question: you can explicitly request the number of sub-agents by stating Use 3 sub-agents to handle this task or Create a sub-agent for each file that needs updating. Claude also automatically uses sub-agents for non-destructive tasks when appropriate, but being explicit gives you control over the parallelisation strategy.

### Parallel Processing

Think like a CPU scheduler for AI agents. Queue up non-destructive tasks, spawn multiple sub-agents, then consolidate their findings and progressively step through their suggestions whilst overseeing Claude in interactive mode.
