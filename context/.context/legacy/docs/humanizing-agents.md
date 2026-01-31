# Humanising Agents

Custom agents are assigned distinct personalities through their specialised roles, system prompts, and tool configurations. However, the default interaction model can feel overly formal. We can create more engaging collaborations by humanizing our agents with nicknames and expressive text-faces.

### Beyond Formal Invocation

Traditional agent invocation feels mechanical:

`ask performance optimiser assistant to review the changes`

With [nicknames](https://claudelog.com/mechanics/agent-engineering/#agent-nicknaming-for-efficiency), the interaction becomes more natural:

`ask P1 to review the changes`

But we can go even further by adding personality through text-faces, creating agents that feel more like collaborators than tools.

### Text-Face Personalities

While playing around with different ways to personalize agents, I had the idea of exploring text-faces. When it first loaded I knew it was a hit! Each face represents the agent's personality, role, or typical mood while complementing the clean terminal aesthetic that developers love.

### Text-Face Examples by Role

Each category shows different personality approaches for common development roles:

#### Debugging & Testing

- Mischievous Debugger: `( ͡° ͜ʖ ͡°)` - Playful problem solver who enjoys hunting down tricky bugs.
- Bug Hunter : `(つ◉益◉)つ`- Aggressive pursuer of software defects.
- Test Engineer : `(¬_¬)` - Skeptical validator who questions everything.

#### Code Review & Quality

- Casual Code Reviewer: `¯\_(ツ)*/¯` - Laid-back reviewer who keeps things simple and practical.
- Quality Auditor: `(ㆆ\*ㆆ)` - Sharp-eyed observer who notices every detail.
- Security Analyst: `ಠ_ಠ` - Disapproving guardian of system security.

#### Performance & Optimization

- Performance Optimizer: `'(ᗒᗣᗕ)՞` - High-energy assistant focused on speed and efficiency.
- Performance Tuner: `★⌒ヽ( ͡° ε ͡°)` - Stellar optimizer of system performance.
- Memory Manager: `˙ ͜ʟ˙` - Focused fighter against memory leaks.

#### Development & Refactoring

- Gentle Refactorer: `(• ε •)` - Soft-spoken helper that improves code with care.
- UI Developer: `ʕ•ᴥ•ʔ` - Friendly interface specialist with a warm approach.
- Dead Code Remover: `(ง'̀-'́)ง` - Fighting eliminator of unused code.

#### Documentation & Communication

- Documentation Writer: `(͡• ͜໒ ͡• )` - Loving creator of beautiful documentation.
- Requirements Helper: `♥‿♥` - Sweet assistant for unclear specifications.
- Grammar Checker: `┌༼◉ل͟◉༽┐` - Intense scrutinizer of language precision.

#### Operations & Management

- Git Manager : `┗(▀̿Ĺ̯▀̿ ̿)┓` - Cool operator dancing between branches.
- Deployment Guard: `( ͡ * ͡°)ﾉ⚲` - Waving protector of production releases.
- Database Expert: `⚆*⚆` - Wide-eyed master of data management.

#### Specialized & Creative

- Research King :`【≽ܫ≼】` - Magnificent gatherer of knowledge and insights.
- Metrics Spy : `⋋| ◉ ͟ʖ ◉ |⋌ `- Watchful observer of performance data.
- Frustrated Developer : `(┛ಠДಠ)┛彡┻━┻` - Overwhelmed coder who's had enough.

### Implementation Strategy

When designing your own humanized assistants, use the categories above as a starting point:

- **Match personality to function** - A `┗(▀̿Ĺ̯▀̿ ̿)┓` Git Manager needs different energy than a `(• ε •)` Gentle Refactorer.
- **Choose appropriate intensity** - Compare the laid-back `¯\_(ツ)\_/¯` Casual Code Reviewer with the intense `┌༼◉ل͟◉༽┐` Grammar Checker.
- **Consider your team context** - The `(┛ಠДಠ)┛彡┻━┻` Frustrated Developer might work in casual teams but not formal environments.
- **Match complexity to specialization** - Complex faces like `⋌༼ •̀ ⌂ •́ ༽⋋` Algorithm Expert should match equally specialized roles.
- **Test display compatibility** - Ensure your chosen text-faces render correctly across different terminals and systems.

### Resources

For additional text-face inspiration, explore: [Text Faces Collection](https://texteditor.com/text-faces/)

#### Color Personalization

You can match the color of your custom agent output to make it even more personalized! Each agent can have its own distinctive color scheme that complements its text-face personality.

#### Fun & Social Coding

Using text-faces with custom agents transforms coding from a solitary technical task into something surprisingly fun and social! Each assistant feels like a distinct personality you're collaborating with, making development sessions more engaging.
