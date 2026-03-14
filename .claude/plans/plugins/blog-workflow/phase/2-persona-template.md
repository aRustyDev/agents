# Phase 2: Persona & Template Meta Commands

## Objective

Establish authorial voice control and reusable structural templates.

## Deliverables

### 1. Persona Commands

Create under `.claude/commands/blog/persona/`:

| Command | Purpose |
|---------|---------|
| `draft.md` | Conversational persona creation → `personas/<slug>.md` |
| `plan.md` | Refine persona with examples and guidelines |
| `review.md` | Test persona against sample content |

### 2. Template Commands

Create under `.claude/commands/blog/template/`:

| Command | Purpose |
|---------|---------|
| `draft.md` | Create template → `<type>/<slug>.md` |
| `plan.md` | Refine with required/optional sections |
| `review.md` | Dry-run template against sample topic |

### 3. Seed Persona

Create `content/_templates/personas/practitioner.md`:

```yaml
---
type: persona
name: practitioner
description: Experienced engineer sharing practical knowledge
---

## Voice
- Conversational, direct
- Uses "I" and "you"
- Shares opinions with justification

## Tone
- Confident but not arrogant
- Pragmatic over theoretical
- Acknowledges trade-offs

## Expertise
- Writes from hands-on experience
- Includes "I've seen this fail when..."
- References real scenarios

## Review Criteria
- Does this sound like someone who's done the work?
- Are opinions backed by experience?
- Is jargon explained or avoided?

## Examples

### Good
"I spent a week debugging this before realizing the problem was simpler than I thought."

### Bad
"It is recommended that developers consider the implications of this architectural decision."
```

### 4. Seed Outline Templates

Copy 18 templates from `/.claude/plans/plugins/blog-workflow/templates/` to `content/_templates/outlines/`.

**File naming**: Templates are copied with their original `.outline.md` suffix preserved. The suffix indicates the template type and distinguishes outline templates from other markdown files.

Source files:

- `tutorial.outline.md`
- `dev-blog.outline.md`
- `debug-error.outline.md`
- `staff-eng.outline.md`
- `principal-eng.outline.md`
- `research-eng.outline.md`
- `computer-arch.outline.md`
- `isa-design.outline.md`
- `vlsi-eng.outline.md`
- `elec-eng.outline.md`
- `photonics.outline.md`
- `neuromorphic.outline.md`
- `novel-computing.outline.md`
- `conference-paper-blog.outline.md`
- `literature-review.outline.md`
- `simulation-study.outline.md`
- `thesis-blog.outline.md`
- `reverse-eng.outline.md`

**Usage**: Reference templates by slug in artifact frontmatter: `template: tutorial` (matches `tutorial.outline.md`).

### 5. Second Seed Persona

Create `content/_templates/personas/educator.md`:

```yaml
---
type: persona
name: educator
description: Patient teacher explaining complex topics clearly
---

## Voice
- Clear, structured explanations
- Uses analogies and examples
- Builds from fundamentals

## Tone
- Patient and encouraging
- Assumes intelligence, not knowledge
- Celebrates "aha" moments

## Expertise
- Anticipates common misconceptions
- Provides multiple explanations
- Links to prerequisites

## Review Criteria
- Would a beginner understand this?
- Are steps numbered and clear?
- Are technical terms defined on first use?

## Examples

### Good
"Think of it like a restaurant kitchen. The chef (your CPU) follows recipes (code), but needs ingredients from the pantry (memory). The waiter (I/O) brings requests from customers..."

### Bad
"The system utilizes a multi-threaded approach to optimize throughput via asynchronous I/O operations."
```

### 6. Persona Verification Integration

Update Phase 1 commands to add persona verification:

- `brainstorm.md` — add persona check/prompt at start (step 2)
- `draft-plan.md` — inherit persona from idea
- Store selected persona in artifact and project frontmatter

**Integration Logic**:

```text
1. Check if project has persona in index.md
2. If set: display "Using persona: <name> — <description>. Continue? (yes/no/change)"
3. If not set: list available personas, prompt selection
4. Store in artifact frontmatter AND project index.md
```

## Command Behaviors

### persona/draft.md

**Input**: Conversational dialogue about voice, tone, expertise

**Output**: `content/_templates/personas/<slug>.md`

**Logic**:

1. Engage user in voice discovery conversation
2. Extract voice, tone, expertise characteristics
3. Generate persona file with required sections
4. Prompt for examples (good/bad)

### persona/review.md

**Input**: Persona path

**Output**: Evaluation against sample content

**Logic**:

1. Load persona
2. Generate sample paragraph in persona voice
3. Evaluate against review criteria
4. Report consistency

### template/draft.md

**Input**: Template type + purpose

**Output**: `content/_templates/<type>/<slug>.md`

**Logic**:

1. Determine type (outlines, research-plans, review-checklists, brainstorm-plans)
2. Generate template structure
3. Mark required vs optional sections

### template/review.md

**Input**: Template path + sample topic

**Output**: Dry-run validation

**Logic**:

1. Load template
2. Apply to sample topic
3. Verify all sections make sense
4. Report gaps or awkward fits

## Tasks

- [ ] Create `.claude/commands/blog/persona/` directory
- [ ] Write `persona/draft.md` command
- [ ] Write `persona/plan.md` command
- [ ] Write `persona/review.md` command
- [ ] Create `.claude/commands/blog/template/` directory
- [ ] Write `template/draft.md` command
- [ ] Write `template/plan.md` command
- [ ] Write `template/review.md` command
- [ ] Create seed persona: `practitioner.md`
- [ ] Create seed persona: `educator.md`
- [ ] Copy 18 outline templates to `content/_templates/outlines/`
- [ ] Update `idea/brainstorm.md` to add persona verification (step 2)
- [ ] Update `idea/draft-plan.md` to inherit persona
- [ ] Test persona creation flow
- [ ] Test persona verification in brainstorm

## Acceptance Tests

- [ ] `/blog/persona/draft` creates persona at `content/_templates/personas/<slug>.md`
- [ ] Persona has required sections: Voice, Tone, Expertise, Review Criteria, Examples
- [ ] `/blog/persona/review <path>` evaluates persona against sample
- [ ] `/blog/template/draft` creates template at `content/_templates/<type>/<slug>.md`
- [ ] `/blog/template/review` dry-runs template against sample topic
- [ ] After Phase 2, `/blog/idea/brainstorm` prompts for persona selection
- [ ] Seeded `practitioner.md` has valid frontmatter with `type: persona`
- [ ] Seeded `educator.md` has valid frontmatter with `type: persona`
- [ ] Seeded outline templates can be referenced by slug in artifact frontmatter
- [ ] All 18 outline templates exist in `content/_templates/outlines/`
- [ ] Persona selection is stored in both artifact and project frontmatter
- [ ] Subsequent commands in same project inherit persona without re-prompting

## Dependencies

- Phase 0 (Foundation)
- Phase 1 (Ideation) — for persona verification integration

## Estimated Effort

2-3 hours
