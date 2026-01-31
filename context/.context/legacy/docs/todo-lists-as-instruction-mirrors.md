# Todo Lists as Instruction Mirrors

The Todo list tool is my second favourite Claude Code tool, second only to the Task/Agent tool. The Todo list tool serves a purpose beyond just tracking progress, it reveals how Claude interprets your instructions.

I often benchmark my instructions against Claude's todos, particularly for step by step processes I am aspiring for a mirror like reflection. When his todos mirror my intentions, I know my instructions are grokked. When his todos diverge, it flags an area for potential improvement in my communication.

### Todo List Divergence

- **Out of Order**: Instructions specify step A then B, but Claude's todos list B then A.
- **Missing Todo Item**: Instructions mention running tests, but Claude's todo list omits this step entirely.
- **Extra Todo Item**: Claude adds "backup existing files" when instructions never mentioned this.
- **Wrong Granularity**: Instructions say "update documentation" but Claude creates separate todos for each individual file.
- **Misinterpreted Step**: Instructions say "review changes" but Claude lists "commit changes" instead.

### Real-Time Steering

Claude's todo list communicates the effects of real-time steering of Claude's goals. You can steer future todo items as Claude reviews your prompts mid-task and uses them to update his planning.

Consider a basic example of changing an element's colour. Properly utilising the todo list allows for clearer steering of future todos as you can see exactly what he plans to do.

### Before Steering:

- Fix the navigation menu alignment
- Update the footer text
- Add new contact form validation
- Change the button background color to blue
- Update documentation

### Mid-task Steering:

`Actually make it green instead`

### After Steering:

- Fix the navigation menu alignment
- Update the footer text
- Add new contact form validation
- Change the button background color to green
- Update documentation

Experiment

Try encouraging Claude to be granular with his todos. Instead of "style the navbar," get Claude to reveal specific adjustments: "change height from 60px to 80px," "reduce padding-top from 16px to 12px," "adjust background from #ffffff to rgba(255,255,255,0.95)." This transparency exposes Claude's design decisions before he makes them, letting you approve or redirect his aesthetic choices.
