

## Agents
- plan-analyzer: determines if the plan is fully refined or not; triggers plan-decomposer or plan-refiner
- plan-decomposer: breaks down a plan into smaller subtasks
- plan-refiner: refines a plan by adding more details, supporting context, quality gates, and feedback loops
- operator: plays the role of a 'product operator/user' for supporting Stakeholder Conversations
- business-analyst: plays the role of a 'business analyst' for analyzing the business context and providing insights for the plan
- stakeholder-conversation: facilitates conversations with stakeholders to gather feedback and insights

## Skills
- behaviour-driven-development-planning: Supports creating plans based on behavior-driven development principles
- component-design: Supports component/module design; its a broader context for component/module design
- feature-driven-development-planning: Supports creating plans based on test-driven development principles
- hardware-planning: Supports creating plans for hardware development
- plan-refinement: Provides robust support for plan refinement, ensuring that plans are well-structured, efficient, and aligned with business goals
- plan-reviewing: Provides robust support for plan review, ensuring that plans are well-structured, efficient, and aligned with business goals
- requirements-planning:
- requirements-standards:
- security-planning: Provides support for including security considerations in plans, and directing how to find targeted security related information for security planning.
- software-planning:
- sop-development: Provides robust support for creating standard operating procedures (SOPs), Engineering-handbooks, and QSMs ensuring consistency and efficiency in operations.
- subsystem-architecture:
- system-planning:
- test-driven-development-planning: Supports creating plans based on test-driven development principles
- validation-planning:

```
.claude/plans/<plan>/
├── docs/
│   ├── records/                          # adrs, constraints, requirements, etc
│   │   ├── xxxx-<adr-title>.md
│   │   ├── xxxx-<constraint-title>.md
│   │   ├── xxxx-<requirement-title>.md
│   │   ├── PRD.md
│   │   ├── BRD.md
│   │   └── SOW.md
│   ├── reports/                          # 
│   │   ├── data-sheet.md
│   │   └── spec-sheet.md
│   ├── sops/                             # Procedures, Engineering-Handbook entries, etc
│   ├── policy/                           # Policy documents
│   ├── requests/                         # 
│   ├── plan/                             # 
│   │   └── phase/                        # 
│   │       └── <n>-<title>.md
│   ├── specs/                            # 
│   ├── PRD.md                            # index file for ./records/xxxx-<requirement-title>.md
│   ├── ROADMAP.md                        #
│   ├── SPEC.md                           # index file for ./specs/*
│   └── PLAN.md                           # index file for ./plan/phase/*
├── references/
│   ├── research-report.md
│   └── life-cycle-planning.md
├── ROADMAP.md                            # symlink to ./docs/ROADMAP.md
├── SPEC.md                               # symlink to ./docs/SPEC.md
├── PRD.md                                # symlink to ./docs/PRD.md
├── README.md                             # Description of the plan
└── book.toml                             # Config for ./docs/ mdbook
```
