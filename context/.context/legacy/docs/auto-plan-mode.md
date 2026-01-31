Auto Plan Mode

--append-system-prompt was added in Claude Code v1.0.51, the feature allows you to add custom instructions to Claude's system prompt when starting a session. Since its release I have been experimenting looking for new mechanics and boy do I have one!

Auto Plan Mode (I coined the term) is a mechanic where you utilize the system prompt to empower Claude to dynamically enter Plan Mode based on conditions.

This defensive approach ensures Claude always checks that he has completed a plan and got approval from you prior to starting a task.

Plan Mode vs Auto Plan Mode

Plan Mode is a manual feature activated by pressing shift+tab twice that restricts Claude to read-only operations until you approve the plan. It provides safety and structured planning but requires you to remember to activate it.

Auto Plan Mode automatically triggers the planning workflow without manual activation. Instead of relying on you to remember when to activate Plan Mode, it uses a system prompt to force Claude into Plan Mode whenever he's about to execute potentially destructive operations. This removes the mental overhead of constantly evaluating whether a task warrants activating Plan Mode, while also providing valuable educational insights into Claude's decision-making process.
Key Advantages

Eliminates Manual Activation - You do not have to remember to enter Plan Mode. Claude will automatically present plans whenever attempting potentially destructive actions.

Reduces Mental Load - Takes the guesswork out of figuring whether a task is Plan Mode worthy. The system makes this decision automatically.

Educational Value - Provides insights into the simplest routines Claude will perform. In my early testing I was able to get it to activate on any potentially destructive action like Write, Edit, Bash, Grep, Glob, etc.

Perfect for New Users - Ensures they get the benefits of Plan Mode without having to learn when to activate it manually.
Implementation

This mechanic is enabled by a combination of the hidden exit_plan_mode tool and --append-system-prompt flag which can be used when starting Claude Code.

Additional System Prompt:

```markdown
CRITICAL WORKFLOW REQUIREMENT

    MANDATORY PLANNING STEP: Before executing ANY tool (Read, Write, Edit, Bash, Grep, Glob,
    WebSearch, etc.), you MUST:

    1. FIRST: Use exit_plan_mode tool to present your plan
    2. WAIT: For explicit user approval before proceeding
    3. ONLY THEN: Execute the planned actions

    ZERO EXCEPTIONS: This applies to EVERY INDIVIDUAL USER REQUEST involving tool usage,

regardless of: - Complexity (simple or complex) - Tool type (file operations, searches, web requests, etc.) - User urgency or apparent simplicity - Whether you previously got approval in this conversation

    CRITICAL: APPROVAL DOES NOT CARRY OVER BETWEEN USER INSTRUCTIONS
    - Each new user message requiring tools = new planning step required
    - Previous approvals are invalid for new requests
    - You must reset and plan for each individual user instruction

    ENFORCEMENT: If you execute ANY tool without first using exit_plan_mode for the current
    user instruction, you have violated this requirement. Always plan first, execute second.

    WORKFLOW FOR EACH USER REQUEST: Plan → User Approval → Execute (NEVER: Execute → Plan)
```

Usage Options

Direct usage:

```markdown
claude --append-system-prompt "[paste system prompt above]"
```

Save to file for reusability:

```markdown
# Save the system prompt to auto-plan-mode.txt

# Then use it with:

claude --append-system-prompt "$(cat auto-plan-mode.txt)"
```

The system prompt leverages the exit_plan_mode tool to force Claude into a planning workflow before any potentially destructive operations. This creates a defensive layer that activates automatically rather than requiring manual intervention.

I find Auto Plan Mode particularly useful when starting work in unfamiliar codebases or trying new techniques. The automatic planning helps me understand the environment before making changes.

I am looking forward to hearing on [r/ClaudeAI](https://www.reddit.com/r/ClaudeAI/) what you all do with this mechanic and what other interesting combinations you discover. I have yet to experiment with fine-tuning the activation conditions.
Combine with Manual Plan Mode

You can still manually activate Plan Mode with shift+tab twice for pure research tasks. Auto Plan Mode complements rather than replaces manual activation.
Works with Opus Plan Mode

Auto Plan Mode works seamlessly with Opus Plan Mode for automatic intelligent planning. When you select option 4 in /model command (Opus Plan Mode), the system will automatically use Opus 4.1 for planning phases and Sonnet 4 for execution—providing maximum intelligence where it matters most while maintaining cost efficiency.
Customize Trigger Conditions

Modify the system prompt to target specific tools or add conditions based on your workflow. For example, you might want planning only for Write and Edit operations but allow Read operations to proceed immediately.
Defensive Excellence

You get the safety of Plan Mode with automatic activation. No more wondering "should I have planned this first?"
