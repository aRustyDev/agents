# Tight Feedback Loops

Tight feedback loops enable Claude to reliably build modular functionality.

    How tight is tight?

Claude writes a bash script, executes it, and if it fails, Claude iterates based on the error output until it works as requested with no compilation step, no framework setup, no build process, just write, execute, iterate.

This setup creates the tightest agentic debug loop I have observed, thanks to the result appearing immediately in the same terminal where Claude is working, giving him all the necessary data to act autonomously. Bash's lightweight nature means zero startup time, no runtime overhead, and instant feedback without layers of abstraction.

Currently, I am primarily using this setup to build data visualisation tools and experimental orchestration frameworks. Today is day zero, and I believe we have not scratched the surface of what this setup is capable of.

Tips for working with Claude and autonomously generated scripts:

- Instruct Claude to document any unusual behavior, edge cases, or implementation quirks encountered during script creation. This creates invaluable context for future modifications and debugging sessions.
- Keep scripts focused and modular to fit comfortably within Claude's context window.
- Design the overall system architecture yourself, then delegate individual script components to Claude. The clearer you define and specify the expected input & output signatures the better.
- Instruct Claude to create a guide document for using the bash script (like a CLAUDE.md file). As he tests the script with your prompts, have him iteratively update the guide document based on any issues discovered during actual usage.

I can imagine a future where dozens of scripts work together seamlessly, with Claude autonomously generating ephemeral problem solving scripts on demand during task execution. The ephemeral scripts could even be created by one sub-agent and used by another sub-agent, creating a dynamic ecosystem of autonomous tool generation and consumption where solutions emerge organically.

### Ephemeral Scripts

The future of development might involve Claude autonomously generating temporary problem-solving scripts during task execution, creating a dynamic ecosystem of tool generation and consumption.
