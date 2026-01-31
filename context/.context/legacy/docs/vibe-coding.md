# Vibe Coding

I wanted to take the time to develop a cadence for when to vibe code before I pitched in on the topic. Over the past 5 months moderating the [r/ClaudeAI](https://www.reddit.com/r/ClaudeAI) subreddit I have heard every kind of anecdote.

What is Vibe Coding

Vibe coding is a development tactic where you completely detach from the underlying code and focus entirely on the outcome of the code. Rather than concerning yourself with implementation details, syntax, or technical mechanics, you focus purely on the vibe of the result. Coined by Andrej Karpathy in February 2025 and recognized by Merriam-Webster Dictionary as a trending term by March 2025.

> "There's a new kind of coding I call 'vibe coding', where you fully give in to the vibes, embrace exponentials, and forget that the code even exists." — Andrej Karpathy

Over the past 5 months or so with Claude Code, I have personally observed you can achieve great success or great disaster with vibe coding.

I initially found success vibe coding Bash Scripts which I was inexperienced with. After vibe coding and reviewing dozens of scripts, orchestrators, and projects, and finding success when integrating vibe coded solutions into pipelines, I believe I have found a balance for when to vibe code.

### The scenarios when I personally do not Vibe Code

- **Novel functionality and feature discovery** - Vibe coding limits the scope of creativity and API discovery. In pursuit of solving problems, I often grok the whole docs and combine APIs to achieve novel functionality. Vibe coding in these scenarios would rob me of the knowledge necessary to create new bits of functionality through cross-pollination.
- **Non-repetitive/core modules within a system** - This is due to me needing to hold a well-known state of the system in my head to rapidly iterate. Vibe coding a whole module would mean introducing a black box as a node within my mental model of a system.
- **Design or aspects of a system which require human taste** - Vibe coded designs sadly suck and lack little differentiation, adding a human touch helps differentiate your products from the swath of slop.

### Scenarios where I am eager to Vibe Code

- **Bash scripts** like when customizing functionality such as Claude Code's StatusLine. The tight feedback loop and realtime updating makes this one of the best demonstrations of vibe coding, especially since I am a noob at Bash and Claude has extensive knowledge of the underlying APIs. Iterating on my own custom StatusLine is particularly fun with Claude Code version v1.0.88, due to the StatusLine updating every second.
  Note: There is a security risk when vibe coding in general, and this risk forced me to learn to read/debug Bash Scripts.
- **Products/functionality with no destructive potential** - If I am building something which is either a throwaway product or something which is static/offline/low-attack surface and does not interface with other systems, I am more willing to vibe code a solution.
- **Permutation-related tasks** - Firstly, I build up a sufficiently large example set for Claude to identify patterns in and reference when completing new tasks. I have found this tactic significantly limits his scope for failure. At the end of the task I would still manually review his work. Having a solid understanding of the acceptable output range, it is easy to see within the Git Diffs where Claude has gone awry.

### Essentials for Vibe Coding with Claude Code

- **`Plan mode` + `ultrathink`** - Always activate [Plan Mode](https://claudelog.com/mechanics/plan-mode/) (Shift + Tab) and be sure to type [Ultrathink](https://claudelog.com/faqs/what-is-ultrathink/) at the end of your prompt when submitting a request to Claude. The more you know about the aspects and edge cases or potential pitfalls of a feature, the more thorough you can be in this phase. You can request Claude to dump the plan to plan.md for easier review. I often perform multiple rounds of planning as I flag potential issues, edge cases, or pitfalls in the planned functionality or feature. I call these multiple rounds of planning [revving the engine](https://claudelog.com/mechanics/rev-the-engine/)
- To get the best results, you want to have broad knowledge of the domain so that you can steer Claude towards the APIs which can provide the functionality you desire most efficiently. If you are unable to articulate a mechanic, Claude may not know it is a logical solution to your issue, e.g. the concept of blend-modes in CSS.
- A form of version control needs to be set up to ensure that when vibe coding you can make tactical commits at key milestones. Not all progress needs to be an explicit commit, you can incrementally stage your progress. I often use this tactic when requesting Claude to perform a task where I feel there is a large room for hallucination or error. I incrementally stage my progress from an interface outside of Claude Code, e.g. VS Code, due to the potential risk that me requesting Claude to perform staging could lead to him becoming greedy, which could lead to him staging unverified progress [Poison Context Awareness](https://claudelog.com/mechanics/poison-context-awareness/).

Despite vibe coding having a bad rap in the community, I have managed to achieve success with it within specific tasks within specific domains and I consider it to be a useful tool within a developer's/business owner's toolbelt. I am looking forward to leveling up my vibe coding skillset!

#### Start Small

Begin vibe coding with throwaway projects and simple scripts to build confidence. Master the feedback loop with low-risk tasks before attempting production systems or complex architectures.

#### Git Discipline

Commit frequently when vibe coding. Small, tactical commits at key milestones allow you to recover quickly when Claude goes off track or introduces unexpected bugs.
