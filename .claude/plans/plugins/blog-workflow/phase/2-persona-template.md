# Phase 2: Persona & Template Meta Commands

## Objective

Establish authorial voice control and reusable structural templates.

## Deliverables

### 1. Persona Skills

Create under `context/plugins/blog-workflow/skills/persona/`:

| Skill | Purpose |
|-------|---------|
| `draft.md` | Conversational persona creation → `personas/<slug>.md` |
| `plan.md` | Refine persona with examples and voice phrases |
| `review.md` | Test persona against sample content |

**Skill frontmatter pattern**:

```yaml
---
name: blog:persona:draft
description: Create a new authorial persona through voice discovery conversation
arguments:
  - name: name
    description: Short name/slug for the persona
    required: false
---
```

### 2. Template Skills

Create under `context/plugins/blog-workflow/skills/template/`:

| Skill | Purpose |
|-------|---------|
| `draft.md` | Create template → `<type>/<slug>.md` |
| `plan.md` | Refine with required/optional sections and guidance |
| `review.md` | Dry-run template against sample topic |

**Skill frontmatter pattern**:

```yaml
---
name: blog:template:draft
description: Create a new structural template for blog artifacts
arguments:
  - name: type
    description: Template type (outlines, research-plans, review-checklists, brainstorm-plans)
    required: true
  - name: name
    description: Template name/slug
    required: true
---
```

### 3. Persona Template

Create `context/plugins/blog-workflow/.templates/persona.md`:

```markdown
---
type: persona
name: "{{slug}}"
description: "{{one-line description}}"
created: "{{ISO 8601}}"
updated: "{{ISO 8601}}"
---

<!-- Template placeholders are filled by Claude during persona creation -->

## Voice

- {{voice characteristic 1}}
- {{voice characteristic 2}}
- {{voice characteristic 3}}

## Tone

- {{tone characteristic 1}}
- {{tone characteristic 2}}
- {{tone characteristic 3}}

## Expertise

- {{expertise indicator 1}}
- {{expertise indicator 2}}
- {{expertise indicator 3}}

## Voice Phrases

Characteristic expressions this persona uses:

- "{{phrase 1}}"
- "{{phrase 2}}"

## Avoid Phrases

Expressions that break this persona:

- "{{anti-phrase 1}}"
- "{{anti-phrase 2}}"

## Review Criteria

- {{question to evaluate voice consistency}}
- {{question to evaluate expertise authenticity}}
- {{question to evaluate tone appropriateness}}

## Examples

### Good

"{{example of writing that matches this persona}}"

### Bad

"{{example of writing that does NOT match this persona}}"
```

### 4. Persona Review Checklist

Create `context/plugins/blog-workflow/.templates/review-checklists/persona.md`:

```markdown
---
type: review-checklist
name: Persona Review
applies_to: persona
---

## Voice Clarity

- [ ] Voice characteristics are specific and actionable
- [ ] Voice examples demonstrate the style clearly
- [ ] Voice is distinct from other personas

## Tone Consistency

- [ ] Tone descriptors are clear
- [ ] Tone matches intended audience
- [ ] No contradictory tone elements

## Expertise Authenticity

- [ ] Expertise level is defined
- [ ] Expertise indicators are realistic
- [ ] Writing can credibly demonstrate expertise

## Examples Quality

- [ ] Good example clearly matches persona
- [ ] Bad example clearly violates persona
- [ ] Examples are distinct from each other

## Practical Usability

- [ ] Review criteria are testable
- [ ] Persona can be applied consistently
- [ ] No ambiguous guidance
```

### 5. Seed Persona: Practitioner

Create `context/plugins/blog-workflow/.templates/personas/practitioner.md`:

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

### 6. Seed Outline Templates

Copy 18 templates from `.claude/plans/plugins/blog-workflow/templates/` to `context/plugins/blog-workflow/.templates/outlines/`.

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

### 7. Seed Persona: Educator

Create `context/plugins/blog-workflow/.templates/personas/educator.md`:

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

### 8. Persona Inheritance Chain

Document how persona flows through the workflow:

**Levels**:

1. **Project level**: `index.md` frontmatter has `persona: <slug>`
2. **Artifact level**: Each artifact inherits from project unless overridden
3. **Post level**: Draft inherits from phase file → content plan → project

**Setting persona**:

- `blog:idea:brainstorm` checks for persona and prompts if not set (already implemented in Phase 1)
- Selected persona stored in `index.md` frontmatter
- Subsequent commands read from `index.md` automatically

**Changing persona mid-project**:

- Edit `index.md` frontmatter `persona:` field directly
- Or use `--persona <slug>` flag on any skill to override
- Future artifacts use new persona
- Existing artifacts retain original persona (immutable history)

**Integration with Phase 1**:

Phase 1's `brainstorm.md` already has persona awareness (step 2). Phase 2 provides:

- The personas to select from (`.templates/personas/`)
- Skills to create new personas (`blog:persona:draft`)
- Skills to test personas (`blog:persona:review`)

No changes to Phase 1 skills are required.

## Skill Behaviors

### persona/draft.md

**Input**: Conversational dialogue about voice, tone, expertise

**Output**: `.templates/personas/<slug>.md`

**Logic**:

1. If no name provided, prompt for persona name/slug
2. Engage user in voice discovery conversation:
   - "How do you want to sound? Formal, casual, technical?"
   - "What's your relationship with the reader?"
   - "What expertise are you demonstrating?"
3. Extract voice, tone, expertise characteristics
4. Generate persona file from `.templates/persona.md`
5. Prompt for examples (good/bad writing samples)
6. Generate voice phrases and avoid phrases
7. Run self-review against `.templates/review-checklists/persona.md`

**Example output**:

```text
Created persona: .templates/personas/skeptical-engineer.md

Voice: Direct, questioning, evidence-based
Tone: Constructively critical, curious
Expertise: Senior engineer evaluating trade-offs

Self-review: passed

Next: Run `blog:persona:review .templates/personas/skeptical-engineer.md` to test
```

### persona/plan.md

**Input**: Existing persona draft path

**Output**: Refined persona with expanded content

**Logic**:

1. Load existing persona draft
2. Generate 3-5 additional good/bad examples
3. Expand review criteria with specific testable questions
4. Add more voice phrases (5-10 characteristic expressions)
5. Add more avoid phrases (5-10 expressions to never use)
6. Update `updated` timestamp

**Example output**:

```text
Refined persona: .templates/personas/skeptical-engineer.md

Added:
- 4 new example pairs (good/bad)
- 6 voice phrases
- 5 avoid phrases
- 3 specific review questions

Next: Run `blog:persona:review` to validate refinements
```

### persona/review.md

**Input**: Persona path

**Output**: Evaluation with sample content generation

**Logic**:

1. Load persona
2. Load `.templates/review-checklists/persona.md`
3. Evaluate each checklist criterion
4. Generate sample paragraph in persona voice
5. Generate sample paragraph violating persona
6. Ask user to identify which matches (validation test)
7. Report consistency score

**Example output**:

```text
## Persona Review: skeptical-engineer

### Voice Clarity
- [x] Voice characteristics are specific — pass
- [x] Voice examples demonstrate style — pass
- [x] Voice is distinct from others — pass

### Sample Generation Test

**Sample A:**
"I've tested this approach in three production systems, and while the
benchmarks look good, I'm still not convinced about the failure modes..."

**Sample B:**
"This revolutionary paradigm shift will transform how we think about
distributed systems architecture going forward..."

Which matches the persona? [A/B]: A ✓

Review: passed (9/9 criteria)
```

### template/draft.md

**Input**: Template type + name/slug

**Output**: `.templates/<type>/<slug>.md`

**Logic**:

1. Validate type is one of: outlines, research-plans, review-checklists, brainstorm-plans
2. Generate template structure appropriate for type
3. Add frontmatter with type, name, applies_to fields
4. Mark sections as required vs optional
5. Add placeholder guidance for each section

**Example output**:

```text
Created template: .templates/outlines/case-study.outline.md

Type: outlines
Sections: 7 (5 required, 2 optional)

Next: Run `blog:template:plan` to refine with examples
```

### template/plan.md

**Input**: Existing template draft path

**Output**: Refined template with detailed guidance

**Logic**:

1. Load existing template draft
2. Add word count guidance per section
3. Add example content snippets for each section
4. Add "common mistakes" notes
5. Add "good examples" for complex sections
6. Mark dependencies between sections
7. Update `updated` timestamp

**Example output**:

```text
Refined template: .templates/outlines/case-study.outline.md

Added:
- Word count targets (total: 2500-3500)
- Example snippets for 4 sections
- 3 common mistake warnings
- Section dependency notes

Next: Run `blog:template:review` to dry-run against sample topic
```

### template/review.md

**Input**: Template path + sample topic

**Output**: Dry-run validation with filled template

**Logic**:

1. Load template
2. Apply to sample topic (fill all sections with example content)
3. Verify all sections make sense for the topic
4. Check section flow and transitions
5. Report gaps or awkward fits
6. Suggest template improvements

**Example output**:

```text
## Template Dry-Run: case-study.outline.md
Topic: "Migrating from Monolith to Microservices at Scale"

### Section Fit Analysis
- [x] Problem Statement — good fit
- [x] Context & Constraints — good fit
- [~] Technical Approach — warn: may need sub-sections for phased migration
- [x] Results & Metrics — good fit
- [x] Lessons Learned — good fit

### Suggestions
1. Consider adding "Rollback Strategy" as optional section
2. "Technical Approach" may benefit from timeline sub-structure

Dry-run: passed with 1 suggestion
```

## Tasks

### Skills

- [x] Create `context/plugins/blog-workflow/skills/persona/` directory
- [x] Write `skills/persona/draft.md` with skill frontmatter
- [x] Write `skills/persona/plan.md` with skill frontmatter
- [x] Write `skills/persona/review.md` with skill frontmatter
- [x] Create `context/plugins/blog-workflow/skills/template/` directory
- [x] Write `skills/template/draft.md` with skill frontmatter
- [x] Write `skills/template/plan.md` with skill frontmatter
- [x] Write `skills/template/review.md` with skill frontmatter

### Templates

- [x] Create `.templates/persona.md` artifact template
- [x] Create `.templates/review-checklists/persona.md`
- [x] Create seed persona: `.templates/personas/practitioner.md`
- [x] Create seed persona: `.templates/personas/educator.md`
- [x] Copy 18 outline templates to `.templates/outlines/`

### Plugin Updates

- [x] Update `plugin.json` with new skills
- [x] Update `marketplace.json` version

### Testing

- [ ] Test persona creation flow (draft → plan → review)
- [ ] Test template creation flow (draft → plan → review)
- [ ] Test persona selection works with existing brainstorm skill
- [ ] Test outline template can be referenced in artifact frontmatter

## Acceptance Tests

### Persona Skills

- [ ] `blog:persona:draft` creates persona at `.templates/personas/<slug>.md`
- [ ] Persona follows `.templates/persona.md` structure
- [ ] Persona has required sections: Voice, Tone, Expertise, Voice Phrases, Avoid Phrases, Review Criteria, Examples
- [ ] `blog:persona:plan` adds examples and expands phrases
- [ ] `blog:persona:review` generates sample content for validation
- [ ] `blog:persona:review` runs checklist from `.templates/review-checklists/persona.md`

### Template Skills

- [ ] `blog:template:draft outlines my-template` creates `.templates/outlines/my-template.outline.md`
- [ ] `blog:template:draft research-plans my-plan` creates `.templates/research-plans/my-plan.md`
- [ ] Template has valid frontmatter (type, name, applies_to)
- [ ] `blog:template:plan` adds word counts and examples
- [ ] `blog:template:review` dry-runs template against sample topic

### Seed Content

- [ ] `practitioner.md` has valid frontmatter with `type: persona`
- [ ] `educator.md` has valid frontmatter with `type: persona`
- [ ] All 18 outline templates exist in `.templates/outlines/`
- [ ] Outline templates have valid frontmatter (type, name, applies_to, content_type)

### Integration

- [ ] `blog:idea:brainstorm` finds personas in `.templates/personas/`
- [ ] Persona selection is stored in project `index.md` frontmatter
- [ ] Subsequent skills in same project inherit persona without re-prompting
- [ ] `--persona <slug>` flag overrides project persona for single invocation
- [ ] Outline templates can be referenced by slug: `template: tutorial`

## Dependencies

- Phase 0 (Foundation) — base templates and rules
- Phase 1 (Ideation) — brainstorm.md has persona awareness that uses personas from this phase
- Source outline templates exist at `.claude/plans/plugins/blog-workflow/templates/` (18 files)

## Estimated Effort

3-4 hours

- Persona skills (3 files): 1.5 hours
- Template skills (3 files): 1 hour
- Persona/checklist templates (3 files): 30 min
- Seed personas (2 files): 15 min
- Copy 18 outline templates: 15 min
- Testing all workflows: 30 min
