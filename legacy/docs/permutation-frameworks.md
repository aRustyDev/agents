# Permutation Frameworks

A permutation framework is when you build an array of similar features with shared function signatures by hand (for example, 10+ features), then design a CLAUDE.md that lets Claude generate subsequent variations reliably. Instead of coding each feature manually, you create an array of patterns which covers a broad range of possibilities whilst also guiding Claude on aspects which must not be changed.

After confirming that Claude is reliable, I began to wonder how far could this scale? How could you push a product to the limits and extract as much value as possible whilst working within the limitations of the kind of tasks that can be autonomously completed and evaluated.

### Understanding Claude's Strengths

The first thing I had to acknowledge is what works and what does not work.

Claude Code appears to be incredibly good at completing tasks where it has decent inherent knowledge or where you provide it with sufficient context including examples of what to do and what not to do.

I have observed that the more strict examples, steps, files to edit and not edit you can provide, the less adherence variance you have on a task. But the issue then becomes that this kind of setup is tedious to do for tasks which are bespoke and one-off.

### From One-Off Tasks to Systematic Permutations

This is why you should identify how and where to implement permutations of functionality within your product and offer them to the market as valuable add-ons.

This requires you to design a system or permutation framework which Claude can work within, allowing you to create example permutations of functionality that follow similar patterns but provide different kinds of value to end users. See [Tool Maker](https://claudelog.com/tool-maker/) as an example permutation CLAUDE.md.

### Building Your Framework Foundation

At [CommandStick](https://www.commandstick.com/) for our upcoming Android app, we have units of functionality which are accessed by a novel HCI (human computer interface). After you have completed 10 or so differing units of functionality within a permutation framework, it can be further fleshed out to allow for defining a wide range of functionality. After fleshing out your permutation framework scope, you can then begin experimenting to get an agent to generate functionality within the confines of your permutation framework.

### Iterative Framework Refinement

Initially, Claude will struggle and fail frequently. However, as you refine your CLAUDE.md to provide clearer guidance for implementing permutations, the adherence and reward gradually improves.

Once Claude began successfully implementing functionality, I repeated the process ~90 times while adjusting various aspects of my CLAUDE.md to understand what affects instruction adherence and what affects the degree of code variance.

I would not say it is necessary to run 90 tests but it is paramount to have a solid idea of the degree of variance amongst the generated code within a permutation framework, otherwise you are creating permutations of slop.

I then explored creating a system for reviewing the permutations which are frivolously generated, so my job goes from implementation to live review at scale! This iterative process builds both your Claude Code expertise and a reliable system for generating permutations.

#### Mechanic Benefits:

- **Scalable value creation**: Transform one framework into multiple valuable feature variations instead of building individual features.
- **Reduced variance through constraints**: Well-defined permutation frameworks limit Claude's creative variance while maintaining useful output diversity.
- **Implementation to review workflow**: Shift from manual coding to reviewing and orchestrating AI-generated permutations at scale.
- **Expertise compounding**: Each iteration improves both your Claude Code skills and framework reliability.

### Systematic Scaling

Permutation frameworks transform development from linear to exponential scaling. Your role shifts from implementation to orchestration, reviewing Ai-generated feature permutations rather than building each feature manually.
