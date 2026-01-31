### Key Elements of AI Instructions

- **Clear objective**: State the goal of the automated task upfront—what should the AI accomplish?
- **Defined workflow**: Outline the steps in your workflow the AI should take to achieve the objective
- **Tool usage**: Specify which tools the AI should use and how to use them
- **Response format**: Describe the desired output format, including structure, style, and content
- **Context and examples**: Provide context and examples to guide the AI and clarify expectations
- **Error handling**: Consider potential errors or edge cases and provide instructions for how to handle them
- **Iteration and follow-up**: Include instructions for how the AI should respond to user feedback or requests for further action

- **Role definition**: What is the AI agent’s identity or purpose?
  - "You are a developer who is very security-aware and avoids weaknesses in the code"
- **Brand voice and tone guidelines**: Clear dos and don'ts (with examples).
- **Target audience context**: Who the AI is interacting with, along with their expectations.
- **Task boundaries and scope**: What it can and cannot do.
- **Response style preferences**: Length, formatting, formality, etc.
- **Fallback/escalation protocols**: When and how to defer to humans or redirect.
- **Success criteria**: What a “good” output looks like for that use case.

### Best practices for rules files

- focus on crafting instructions that are clear, concise, and actionable
- tailor rules to their relevant scope, such as a particular programming language
- break down complex guidelines into smaller, atomic, and composable rules
- keep the overall rules concise; under 500 lines
- mention "secure" or specific CWEs to avoid
  - ("Generate secure Python code that prevents top security weaknesses listed in CWE for the following")
