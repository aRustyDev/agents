## Structure Docs

- `PRD.md`
- `SPEC.md`
- `BRD.md`
- `SOW.md`
- `data-sheet.md`
- `spec-sheet.md`
- `PLAN.md`
- `phase/<n>-<title>.md`
- `book.toml`

## Workflow

1. Business/Mission Need
2. ConOps (operational view: how will it be used?)
3. BRD/MRD (why build it? business justification)
4. PRD/StRS (what features for which users?  "What value for whom?" )
5. System Requirements Specification (what must the system do technically?)
6. Split Requirements into Parallel Streams
  a). Software Requirements Specification. ("How must each subsystem work?")
  b). Hardware Requirements Specification. ("How must each subsystem work?")
  c). Interface Control Document. ("How must each subsystem work?")
7. Each requirements spec then drives its corresponding design document; These drive implementation (code, schematics, PCB layouts, mechanical designs).
  a). SDD for software. (answers "How will we build it?")
  b). HDD for hardware. (answers "How will we build it?")

## Patterns

- Use Frontmatter
  - all `references/*` contain
    - `audience` (internal engineering vs. external users vs. regulators vs. manufacturing partners)
    - `lifecycle` (Concept → Build → Produce → Deploy → Operate → Retire))
      - Concept, Requirements, Design, Implementation, Test, Production, Operations
    - `product:bool` (what we build)
    - `process:bool` (how we work)
    - `domain` (Business, Product, System, Software, Hardware, Interface, Test)
    - `artifact-type` (Specification, Description, Plan, Report, Record, Procedure, Request, Policy)
- Use one of; check rules/context for hints, ask user if unspecified or ambiguous
  - `BDD`: Behavior Driven Development
  - `TDD`: Test Driven Development
  - `FDD`: Feature Driven Development

## V-model for System Validation

> right side mirrors the left, with each verification level corresponding to a decomposition level:

| Left side (Decomposition) | Right side (Verification) |
|---|---|
| ConOps / Stakeholder Needs | Acceptance Testing / Operational Validation |
| System Requirements (SyRS) | System Testing (functional + non-functional) |
| Subsystem Architecture | Integration Testing (interface verification) |
| Component/Module Design | Unit/Component Testing |

## Requirements

Every requirement should trace forward to design elements and test cases, and backward to stakeholder needs. This is maintained through a **Requirements Traceability Matrix** (RTM) — mandatory in regulated industries, strongly recommended everywhere. Forward traceability ensures every requirement is implemented and tested; backward traceability ensures every deliverable traces to an original need and prevents scope creep.

**Derived requirements** deserve special attention: these are requirements that emerge from design decisions rather than flowing down from higher-level requirements. Choosing a specific communication protocol creates requirements for that protocol. Selecting an off-the-shelf component introduces that component's constraints. Derived requirements should be documented in the same specification as other requirements at that level but clearly marked as derived, because they can be changed without stakeholder approval and may become obsolete when design decisions change.
