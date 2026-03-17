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

## Docs

- **Product Requirements Document (PRD)** is the most universally used document in tech product development. Written by product managers, read by everyone. Contains objectives, personas, user stories, success metrics, scope, and constraints. No IEEE standard defines it directly, but it maps closest to the **Stakeholder Requirements Specification (StRS)** in IEEE 29148:2018. In practice, PRDs range from 1-page product briefs to 8-page execution-ready specs, with modern teams trending toward the lighter end.
- **Business Requirements Document (BRD)** is well-established in enterprise IT and consulting. Written by business analysts, it captures the "why" — business objectives, scope, stakeholder identification, cost-benefit analysis, and acceptance criteria. BABOK defines business requirements as "goals, objectives, and outcomes describing why a change was initiated." IEEE 29148 includes a **Business Requirements Specification (BRS)** template as its formal equivalent.
  - Captures what the business needs from the system in business terms—created with stakeholders
  - captures the business needs and ensures alignment with business goals
  - BRD is written by the business to highlight their need/issues. They add the current situation, how is it a problem, and what a "solution" could improve. They also put metrics to track results. This is used by product to challenge business and prioritize project. 
- **Software Requirements Specification (SRS)** is the canonical requirements document in software engineering, defined by **IEEE 830** (now superseded by **IEEE 29148:2018**). Contains functional requirements using SHALL language, non-functional requirements (performance, safety, security), verification criteria, and interface specifications. Written by systems analysts or requirements engineers.
- **Software Design Document/Description/Specification (SDD/SDS)** — these three names all refer to the same artifact. **IEEE 1016** officially uses "Software Design Description" (SDD). Wikipedia explicitly notes the interchangeability. Contains architecture views, component decomposition, interface design, data models, and algorithm details. Written by software architects and senior engineers.
- **Functional Requirements Specification/Document (FRS/FRD)** — **these are synonyms**. Both describe the functional behavior of a system at a granular level: process flows, field-level specifications, business rules, UML diagrams. The choice between "Specification" and "Document" is organizational preference, not a semantic distinction. FRD/FRS sits between BRD (high-level "why") and SRS (comprehensive technical spec covering both functional and non-functional requirements).
  - Aliases:
      - SPEC
      - Technical Specification
  - Focus: Technical implementation, architecture, and data flow.
  - Data models
      - schemas (DB, json, etc)
  - API contracts
  - system interaction
  - specific functionalities
  - security
  - error handling
  - system architecture
- Product Design Specification (PDS)
  - Focus: Purpose, user problems, business goals, and high-level functionality
  - Problem statement
  - User stories
  - features
  - KPIs
  - high-level scope
  - success metrics
  - wireframes
- **Product Design Specification (PDS)** is real and well-defined in **mechanical/industrial engineering**, popularized by Stuart Pugh's "Total Design" methodology. It specifies quantified requirements across 20+ categories including performance, environment, materials, aesthetics, manufacturing processes, and cost targets. However, it is uncommon in pure software contexts and should not be confused with "Product Design Document."
- Testing standards (IEEE 829, ISO 29119) define specific artifacts: Test Plan, Test Design Specification, Test Case Specification, Test Procedure Specification, and Test Summary Report
- **Statement of Work (SOW)** is a contractual document defining scope, deliverables, timeline, and acceptance criteria between client and contractor. It references specifications but is not itself a specification — it defines the *work to be done*, not the *technical requirements of the product*.
- **Product Brief** is a concise (typically 1-page) document defining a problem to solve and strategic context. It is the **precursor to a PRD**, not a synonym. Modern product development often follows a three-stage evolution: Product Brief → Lean PRD → Full PRD.
- **Spec Sheet / Data Sheet** is a post-design marketing artifact listing key specifications of a finished product. Critically, a spec sheet describes what a product IS (backward-looking), while a specification prescribes what it SHOULD BE (forward-looking).

## Domains
- System: the engineering-level document that sits between them and that allocates requirements to hardware, software, and interface subsystems.
  - IEEE 29148 defines a clear hierarchy:
    - Stakeholder Requirements Specification (StRS) → System Requirements Specification (SyRS) → Software Requirements Specification (SRS). 
  - The user has "Product" and "Software" but no "System" — which is
  - System Requirements Specification is the single source of truth for the whole system, For any product combining hardware and software.
- Business
- Product
- Software
- Hardware: specify physical constraints (dimensions, weight, thermal limits, power budgets), reference specific manufacturer part numbers, and must be rigorous enough to drive manufacturing.
  - Hardware Requirements Specification (HRS)
  - Hardware Design Document (HDD)
  - schematics
  - PCB layouts
  - BOMs
  - fabrication drawings
  - DFM reports
  - DFT reports
  - environmental test specifications.
- Interface
  - Interface Control Documents (ICDs)
    - defines the contract between subsystems: signal levels, pin assignments, protocols, data formats, timing, register maps, memory maps, interrupt assignments. 
    - Without dedicated interface documentation, hardware and firmware teams cannot coordinate.
  - Hardware/Software Interface Documents
- Test (See IEEE 829 / ISO 29119)
  - Test Plan (strategy, scope, schedule — a management document)
  - Test Specification (test design, test cases, test procedures — a technical document)
  - Test Report (results, assessment, pass/fail judgment — an evaluative document).


## Lifecycle Phases
- Pre-requirements Phase
  - Concept of Operations (ConOps, IEEE 1362), which describes how the system will be used from users' viewpoint
  - Vision Document
  - Market Requirements Document: documents market opportunity, customer pain points, and competitive landscape;
  - Feasibility Studies: structured comparison of design alternatives
  - Trade Studies: structured comparison of design alternatives
- Build Phase
- Manufacturing/production
  - Engineering Specifications (the "build-to" spec sent to factories)
    - fabrication drawings
    - assembly drawings
    - DFM and DFT reports
    - Bill of Materials
- Post-release
  - Release Notes
  - Field Failure Reports
  - Post-Mortems
  - feedback loop from operations back to design

## Special Document Types (Words)
- Specification: prescriptive and normative.
    - implies greater normative force than 'document'
    - It defines requirements, constraints, or design characteristics that SHALL be met. 
    - Specifications use imperative language ("shall," "must") and establish verifiable criteria. 
    - Every statement in a specification must be testable.
    - Specifications are binding — often contractually or regulatorily.
- Plan: specifies what will be done, when, by whom, and with what resources. 
    - Plans are forward-looking and resource-oriented. 
    - A Test Plan (managerial: scope, schedule, resources) is fundamentally different from a Test Specification (technical: what to test, how to test it). They are complementary, not synonymous
- Report: provides retrospective information about activities performed, results achieved, and assessments made. 
    - Backward-looking and evaluative. 
    - A Test Summary Report summarizes completed testing
    - A Test Specification defines upcoming testing.
- Description: characterizes an item as it is or as designed. 
    - IEEE 1016 deliberately chose "Software Design Description" rather than "Specification" because a design document describes a chosen approach rather than prescribing one. Similarly, ISO 42010 defines "Architecture Description." Descriptions are informative rather than normative.
- Record: captures a point-in-time, immutable artifact — a decision, event, or state. 
    - Per ISO 15489, records serve as evidence. 
    - Architecture Decision Records (ADRs) exemplify this: each captures a single decision with context, alternatives, and consequences, and is append-only (new ADRs supersede old ones rather than editing existing ones).
- Policy (organizational directives)
- Procedure (step-by-step instructions)
- Request (solicitation for action, e.g., Change Request).


## Goals 

### Re: Above Docs
- Format: Specify overall structure
- Content: Clarify the expected contents
- Detail: level of detail


## Unclear
- User Story: Does this go in one of the Above Docs or is it seperate?
- Statement of Work (SOW): Does this go in one of the Above Docs or is it seperate?
    - sets the overall project framework.
    - High-level contract outlining project scope, timeline, deliverables, and cost—owned by the implementation partner
- Epics is just to clean up our Jira by categorising the stories by project or subproject
- **Stories**
- Bodies of Knowledge relevant to the above docs (e.g., BABOK, CMMI)

## Workflow
1. PRD is completed first
2. PRD is decomposed and refined
3. SPEC is generated based on PRD & .claude/rules/spec/*
4. SPEC is decomposed and refined
5. SPEC is transformed into project scoped `.claude/rules/spec/*`
6. The PRD is summarized into Epic tickets
7. Deep Planning workflow for each Epic ticket added as Task
    - Research Planning Round 1 (General Exploration)
    - Research
    - Research Planning Round 2 (Informed Exploration)
    - Research
    - Research Planning Round 3 (Targeted Deep Dives)
    - Deep-Research on Scoped Target Topics
    - Update PRDs/SPECs
    - Determine if Further Research needed
8. Create ROADMAP for project using SPECs/Epics
9. Create Tasks for Epics using ROADMAP
    - add technical details directly into tasks
    - reference technical design documents in tasks

## Tools
- Open Spec
- Spec Kit
    - Constitution: defines the non-negotiable, high-level rules and guiding principles for a project
- BMAD
- SPEC Framework
