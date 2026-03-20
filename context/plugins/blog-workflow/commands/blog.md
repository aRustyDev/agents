---
name: blog
description: Blog workflow orchestrator — route to any phase (idea, research, content, post, publish, persona, template, series) with state-aware suggestions
argument-hint: <phase> <action> [args] | -h | (no args for status)
arguments:
  - name: phase
    description: "Workflow phase: idea, research, content, post, publish, persona, template, series"
    required: false
  - name: action
    description: "Phase action: draft, plan, review, refine, spec, brainstorm, pre-check, promote, validate, seo-review"
    required: false
---

# Blog Workflow Orchestrator

Single entry point for the entire blog workflow. Routes to phase-specific commands, detects project state, and suggests next steps.

## Routing

Parse `$ARGUMENTS` to determine the target command:

### If no arguments (bare `/blog`)

1. **Detect project state:**
   - Glob for `content/_projects/*/index.md`
   - If no projects exist: suggest `/blog init` then `/blog idea brainstorm "topic"`
   - If projects exist, find the most recently modified one
   - Read its `index.md` frontmatter for `status` field
   - Suggest the next logical step based on status:

   | Project Status | Next Step | Command |
   |---------------|-----------|---------|
   | `ideation` | Review or refine the idea | `/blog idea review <path>` |
   | `planning` | Create research spec | `/blog research spec draft <path>` |
   | `research` | Execute or review research | `/blog research draft <path>` |
   | `content-planning` | Draft or review content plan | `/blog content draft <path>` |
   | `post` | Create post spec or draft | `/blog post spec <path>` |
   | `publishing` | Run pre-check | `/blog publish pre-check <path>` |

2. **Show brief status summary:**

   ```
   Blog Workflow Status

   Active project: <slug> (status: <status>)
   Next step: /blog <phase> <action> <path>

   Tip: /blog -h for all commands
   ```

### If `-h` or `--help`

Show the full command reference:

```
Blog Workflow — /blog <phase> <action> [args]

Phases & Actions:
  idea        brainstorm <topic>     Start a new blog project
              review <path>          Evaluate idea against checklist
              refine <path> "note"   Update idea based on feedback
              draft-plan <path>      Create project plan from idea

  research    spec draft <path>      Create research plan
              spec plan <path>       Refine research methodology
              spec review <path>     Evaluate research plan
              draft <path>           Execute research
              plan <path>            Analyze findings
              review <path>          Compile final report
              refine <path> "note"   Update research artifact

  content     draft <path>           Create content brainstorm
              plan <path>            Decompose into phases
              review <path>          Evaluate content plan
              refine <path> "note"   Update content artifact

  post        spec <path>            Create post specification
              plan <path>            Create structural outline
              draft <path>           Write full post
              review <path>          Evaluate post artifact
              refine <path> "note"   Update post artifact

  publish     seo-review <path>      SEO optimization check
              pre-check <path>       Validate frontmatter & links
              promote <path>         Move to published directory
              validate <path>        Verify platform build

  persona     draft [name]           Create new persona
              plan <path>            Expand persona examples
              review <path>          Test persona consistency

  template    draft <type> <name>    Create new template
              plan <path>            Refine template
              review <path>          Dry-run template

  series      plan <topic>           Plan multi-part series

Shortcuts:
  i = idea    r = research    c = content    po = post
  pu = publish    pe = persona    t = template    s = series

Examples:
  /blog idea brainstorm "eBPF tracing tools"
  /blog r spec draft ./content/_projects/ebpf/plan.md
  /blog po draft ./content/_projects/ebpf/post/ch1/spec.md
  /blog pu pre-check ./content/_drafts/ebpf-tracing.md
  /blog                  (show project status + next step)
```

### If arguments provided

1. **Resolve shortcuts** in the first argument:

   | Shortcut | Phase |
   |----------|-------|
   | `i` | `idea` |
   | `r` | `research` |
   | `c` | `content` |
   | `po` | `post` |
   | `pu` | `publish` |
   | `pe` | `persona` |
   | `t` | `template` |
   | `s` | `series` |

2. **Build the command file path:**
   - `<phase>/<action>.md` for most commands
   - `research/spec/<action>.md` for research spec sub-phase
   - `series-plan.md` for the series phase

   Map table:

   | Input | Command File |
   |-------|-------------|
   | `idea brainstorm` | `idea/brainstorm.md` |
   | `idea review` | `idea/review.md` |
   | `idea refine` | `idea/refine.md` |
   | `idea draft-plan` | `idea/draft-plan.md` |
   | `research spec draft` | `research/spec/draft.md` |
   | `research spec plan` | `research/spec/plan.md` |
   | `research spec review` | `research/spec/review.md` |
   | `research draft` | `research/draft.md` |
   | `research plan` | `research/plan.md` |
   | `research refine` | `research/refine.md` |
   | `research review` | `research/review.md` |
   | `content draft` | `content/draft.md` |
   | `content plan` | `content/plan.md` |
   | `content refine` | `content/refine.md` |
   | `content review` | `content/review.md` |
   | `post spec` | `post/spec.md` |
   | `post plan` | `post/plan.md` |
   | `post draft` | `post/draft.md` |
   | `post refine` | `post/refine.md` |
   | `post review` | `post/review.md` |
   | `publish seo-review` | `publish/seo-review.md` |
   | `publish pre-check` | `publish/pre-check.md` |
   | `publish promote` | `publish/promote.md` |
   | `publish validate` | `publish/validate.md` |
   | `persona draft` | `persona/draft.md` |
   | `persona plan` | `persona/plan.md` |
   | `persona review` | `persona/review.md` |
   | `template draft` | `template/draft.md` |
   | `template plan` | `template/plan.md` |
   | `template review` | `template/review.md` |
   | `series plan` | `series-plan.md` |

3. **Read the target command file** from `${CLAUDE_PLUGIN_ROOT}/commands/<path>`

4. **Execute the command** with remaining arguments passed through.

### Error Handling

| Condition | Response |
|-----------|----------|
| Unknown phase | Show "Unknown phase '<phase>'. Run `/blog -h` for available phases." |
| Unknown action | Show "Unknown action '<action>' for phase '<phase>'. Available: <list actions>" |
| Missing required argument | Show the target command's argument-hint |
| Command file not found | Show "Command not found. Plugin may need reinstalling." |
