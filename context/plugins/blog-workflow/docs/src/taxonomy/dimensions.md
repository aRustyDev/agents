# Post Dimensions

Beyond type, posts are characterized by several dimensions that affect their structure, voice, and lifecycle.

## Formality Spectrum

Formality affects structure, sourcing requirements, tone, and editing depth.

### Levels

| Level | Name | Description | Characteristics |
|-------|------|-------------|-----------------|
| 0 | Sketch | Internal only | Napkin notes, not published |
| 1 | Casual | Quick takes | Conversational tone, loose structure, "I think...", minimal citations |
| 2 | Structured | Most posts | Clear sections, some sourcing, professional but approachable |
| 3 | Formal | Whitepapers | Rigorous structure, citations expected, precise language |
| 4 | Academic | Research | Methodology section, peer-review ready, formal citations |

### Formality by Type

| Type | Typical Range | Notes |
|------|---------------|-------|
| Tutorial | 2-3 | Higher for advanced topics |
| Walk-through | 1-2 | Process-focused, less formal |
| Deep Dive | 2-3 | Industry formal, not academic |
| Research | 3-4 | Academic rigor required |
| Study Review | 2 | Reflective, structured |
| Review | 2 | Balanced assessment |
| Comparison | 2-3 | Criteria-driven |
| Problems | 2 | Structured diagnosis |
| Open Questions | 1-2 | Exploratory, casual |
| Planning | 2 | Clear goals, structured |
| Retrospective | 2 | Honest reflection |
| Updates | 1-2 | Progress diary |
| Opinions | 1-2 | Personal voice |
| Dev Blog | 2 | Practitioner wisdom |
| Announcement | 1-2 | Direct, clear |
| Reference | 1-2 | Utility-focused |
| ELI5 | 1-2 | Accessible |
| 5 Levels | 2-3 | Progressively formal |

### Frontmatter

```yaml
formality: 2  # Numeric value 1-4
# or
formality: structured  # Named value
```

Valid named values: `casual`, `structured`, `formal`, `academic`

---

## Complexity

Complexity describes the depth and technical level of the content.

### Factors

- **Subject complexity**: Library internals vs book review vs coffee preference
- **Prerequisite knowledge**: What the reader must already know
- **Depth of analysis**: Surface overview vs deep technical details

### Levels

| Level | Name | Example |
|-------|------|---------|
| 1 | Accessible | "Why I love my coffee routine" |
| 2 | Introductory | "What is Kubernetes?" |
| 3 | Intermediate | "Kubernetes networking explained" |
| 4 | Advanced | "Building a custom CNI plugin" |
| 5 | Expert | "Kernel bypass networking in K8s" |

### Frontmatter

```yaml
complexity: 3  # Numeric 1-5
# or
complexity: intermediate
```

---

## Temporality

Temporality describes when the post exists relative to the work it discusses.

### Categories

| Category | When Written | Relationship to Work |
|----------|--------------|---------------------|
| **Before** | Pre-work | Planning, Open Questions, Problems |
| **During** | Mid-work | Updates, Walk-through |
| **After** | Post-work | Review, Retrospective, Research, Study Review, Deep Dive, Comparison |
| **Atemporal** | Any time | Tutorial, Dev Blog, Opinions, ELI5, 5 Levels, Reference |
| **Point-in-time** | Specific moment | Announcement |

### Living Documents

Some posts are designed to be updated over time rather than remaining static snapshots.

```yaml
living: true
living-updated: 2026-03-16
```

See [Living Documents](#living-documents) for which types support this.

---

## Living Documents

Living documents are maintained over time rather than published once.

### Applicability by Type

| Type | Living Support | Notes |
|------|----------------|-------|
| Reference | Expected | Core purpose is staying current |
| Comparison | Expected | Products evolve |
| Tutorial | Available | APIs/tools change |
| Dev Blog | Available | Toolkits evolve |
| Review | Available | "Updated after 6 months" pattern |
| Open Questions | Available | Add answers as discovered |
| ELI5 | Available | Deepen understanding |
| 5 Levels | Available | Deepen understanding |
| Problems | Available | As diagnosis refines |
| Opinions | Rare | Original take has value |
| Deep Dive | Not applicable | Publish editions instead |
| Research | Not applicable | Snapshot; follow-up = new post |
| Study Review | Not applicable | Captures learning moment |
| Walk-through | Not applicable | Tied to specific time |
| Planning | Not applicable | Becomes Retrospective |
| Updates | Not applicable | Each entry is new |
| Announcement | Not applicable | Point-in-time |
| Retrospective | Not applicable | Reflection on completed work |

### Frontmatter

```yaml
living: true
living-updated: 2026-03-16  # ISO date of last content update
living-history:
  - date: 2026-03-16
    summary: "Added section on new API"
  - date: 2026-02-01
    summary: "Initial publication"
```

### Best Practices

1. **Changelog section**: Include visible update history for readers
2. **Date visibility**: Show both original publish and last update dates
3. **Major vs minor**: Document significant changes, not typo fixes
4. **Edition threshold**: If >50% changes, consider a new post instead

---

## Voice

Voice is derived from type and formality but can be explicitly noted.

### Voice Categories

| Voice | Description | Types |
|-------|-------------|-------|
| **Authoritative** | You know this well | Tutorial, Deep Dive |
| **Exploratory** | Learning alongside reader | Walk-through, Study Review |
| **Evaluative** | Balanced assessment | Review, Comparison |
| **Personal** | First-person perspective | Opinions, Dev Blog |
| **Academic** | Rigorous, formal | Research |
| **Speculative** | Thinking out loud | Open Questions |
| **Diagnostic** | Problem analysis | Problems |
| **Reflective** | Looking back | Retrospective, Study Review |
| **Pedagogical** | Teaching, patient | ELI5, 5 Levels, Tutorial |
| **Narrative** | Telling a story | Updates, Walk-through |
| **Declarative** | Clear announcement | Announcement |
| **Neutral** | Minimal opinion | Reference |

Voice is not typically set in frontmatter—it's implied by type and formality.

---

## Dimension Matrix

Posts exist in a multi-dimensional space:

```text
         Formality
            │
     4 ─────┼───── Academic
            │      Research
     3 ─────┼───── Formal
            │      Deep Dive, Comparison
     2 ─────┼───── Structured ← Most posts
            │      Tutorial, Review, Dev Blog
     1 ─────┼───── Casual
            │      Walk-through, Updates, Opinions
            │
            └──────────────────────────────────→ Complexity
                  1     2     3     4     5
              Simple  Intro  Mid  Adv  Expert
```

The third dimension (temporality) determines when in a project lifecycle the post fits.
