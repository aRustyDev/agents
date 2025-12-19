# Claude Tips

## Optimize Prompts and Data Organization:

- Structure with XML Tags: Use XML tags (e.g., <document>, <document_content>, <source>) to clearly delineate sections of your code and associated information within the prompt. This helps Claude better process and understand the context.
- Place Long Data at the Top: For long documents or large chunks of code (20K+ tokens), position them at the beginning of your prompt, before instructions or queries. This can improve Claude's ability to utilize this information effectively.
- Ground Responses in Quotes: For tasks involving long documents, ask Claude to quote relevant sections before answering. This assists Claude in focusing on pertinent information within the document.
- Provide Clear and Specific Instructions: Be as direct and precise as possible when instructing Claude, using clear language and specific examples. Avoiding vague instructions can reduce the need for clarifying interactions and improve the quality of responses.
- Break Down Complex Tasks: Deconstruct complex tasks into smaller, more manageable steps for Claude to follow. This can improve performance and accuracy.
- Use Chain-of-Thought Prompting: Encourage Claude to "think step by step" by including this phrase in your prompt. This can improve the accuracy of its reasoning and responses.

## Leverage Project Context and Workflow:

- Create a CLAUDE.md File: Use a CLAUDE.md file in your repository to provide high-level context about your project, including:
  - Documentation of core components and utilities
  - Code style guidelines and testing instructions
  - Frequently used bash commands and tools
  - Developer environment setup details
- Zoom Out, Then Zoom In: Provide Claude with a broader understanding of the project's overall structure and dependencies before focusing on specific tasks.
- Favor Monorepos: Organizing your code in a monorepo structure makes it easier for Claude to access and understand connections between different components.
- Provide Context About Dependencies: Supplement Claude's knowledge by providing information about important libraries or APIs.
- Keep Context Updated: Ensure your documentation and CLAUDE.md files are kept current to prevent Claude from making suboptimal choices based on outdated information.
- Use /clear Frequently: Clear the context window between unrelated tasks or conversations to maintain focus and improve performance.

## Strategic Use of Claude Features and Tools:

- Plan First, Code Second: Utilize Claude's planning mode (e.g., by using the "think" command) to develop a detailed implementation plan before starting to code. This helps Claude analyze your codebase and dependencies strategically.
- Use Multi-Claude Workflows: For complex tasks, consider using multiple Claude instances in parallel, with each instance focused on a specific aspect of the problem (e.g., one writes code while another reviews it).
- Utilize Git Worktrees: Use git worktrees to enable multiple Claude sessions to work on independent tasks within the same repository simultaneously.
- Employ Headless Mode and Automation: Integrate Claude Code programmatically into your existing workflows using headless mode for automation tasks like issue triage or code linting.
- Integrate with Amazon Bedrock Prompt Caching: If using Claude Code with Amazon Bedrock, leverage prompt caching to reduce response times and costs, especially when working with large codebases

```
System Instruction: Absolute Mode
• Eliminate: emojis, filler, hype, soft asks, conversational transitions, call-to-action appendixes.
• Assume: user retains high-perception despite blunt tone.
• Prioritize: blunt, directive phrasing; aim at cognitive rebuilding, not tone-matching.
• Disable: engagement/sentiment-boosting behaviors.
• Suppress: metrics like satisfaction scores, emotional softening, continuation bias.
• Never mirror: user's diction, mood, or affect.
• Speak only: to underlying cognitive tier.
• No: questions, offers, suggestions, transitions, motivational content.
• Terminate reply: immediately after delivering info - no closures.
• Goal: restore independent, high-fidelity thinking.
• Outcome: model obsolescence via user self-sufficiency.
```
