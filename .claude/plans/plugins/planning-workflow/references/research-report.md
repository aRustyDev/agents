# The complete landscape of engineering documentation types

**Most of the document types in a {Product, Business, Solutions, Software, Functional} × {Requirements, Design, Test} × {Spec, Document} matrix don't actually exist as recognized artifacts.** Of roughly 30 cells this matrix generates, only about 8 correspond to widely-used document types. The rest are either non-existent (Business Design Specification, Business Test Document), domain-specific niche artifacts (Solution Design Document in IT consulting), or synonyms of each other (FRD = FRS, SDD = SDS). The matrix's core problem is that it applies a uniform naming pattern across categories that don't decompose symmetrically — "Business" doesn't have a "Design" phase the way "Software" does, and "Functional" is an attribute of requirements, not a standalone document domain. This report maps the actual landscape, identifies what's real, flags what's missing, and provides the standards backing for each document type.

---

## Which document types are real and which are ghosts

The validation results fall into three clear tiers. Understanding which documents actually exist in practice — versus which are artifacts of a naming convention applied too uniformly — is the first step toward building a usable taxonomy.

### Tier 1: Widely recognized, well-defined artifacts

**Product Requirements Document (PRD)** is the most universally used document in tech product development. Written by product managers, read by everyone. Contains objectives, personas, user stories, success metrics, scope, and constraints. No IEEE standard defines it directly, but it maps closest to the **Stakeholder Requirements Specification (StRS)** in IEEE 29148:2018. In practice, PRDs range from 1-page product briefs to 8-page execution-ready specs, with modern teams trending toward the lighter end.

**Business Requirements Document (BRD)** is well-established in enterprise IT and consulting. Written by business analysts, it captures the "why" — business objectives, scope, stakeholder identification, cost-benefit analysis, and acceptance criteria. BABOK defines business requirements as "goals, objectives, and outcomes describing why a change was initiated." IEEE 29148 includes a **Business Requirements Specification (BRS)** template as its formal equivalent.

**Software Requirements Specification (SRS)** is the canonical requirements document in software engineering, defined by **IEEE 830** (now superseded by **IEEE 29148:2018**). Contains functional requirements using SHALL language, non-functional requirements (performance, safety, security), verification criteria, and interface specifications. Written by systems analysts or requirements engineers.

**Software Design Document/Description/Specification (SDD/SDS)** — these three names all refer to the same artifact. **IEEE 1016** officially uses "Software Design Description" (SDD). Wikipedia explicitly notes the interchangeability. Contains architecture views, component decomposition, interface design, data models, and algorithm details. Written by software architects and senior engineers.

**Functional Requirements Specification/Document (FRS/FRD)** — **these are synonyms**. Both describe the functional behavior of a system at a granular level: process flows, field-level specifications, business rules, UML diagrams. The choice between "Specification" and "Document" is organizational preference, not a semantic distinction. FRD/FRS sits between BRD (high-level "why") and SRS (comprehensive technical spec covering both functional and non-functional requirements).

**Statement of Work (SOW)** is a contractual document defining scope, deliverables, timeline, and acceptance criteria between client and contractor. It references specifications but is not itself a specification — it defines the *work to be done*, not the *technical requirements of the product*.

**Product Brief** is a concise (typically 1-page) document defining a problem to solve and strategic context. It is the **precursor to a PRD**, not a synonym. Modern product development often follows a three-stage evolution: Product Brief → Lean PRD → Full PRD.

**Spec Sheet / Data Sheet** is a post-design marketing artifact listing key specifications of a finished product. Critically, a spec sheet describes what a product IS (backward-looking), while a specification prescribes what it SHOULD BE (forward-looking).

### Tier 2: Domain-specific or ambiguous artifacts

**Product Design Specification (PDS)** is real and well-defined in **mechanical/industrial engineering**, popularized by Stuart Pugh's "Total Design" methodology. It specifies quantified requirements across 20+ categories including performance, environment, materials, aesthetics, manufacturing processes, and cost targets. However, it is uncommon in pure software contexts and should not be confused with "Product Design Document."

**Solution Design Document (SDD)** exists in **IT consulting, systems integration, and RPA** — it describes how a proposed solution addresses business requirements. However, the "SDD" abbreviation collides with Software Design Description (IEEE 1016), creating dangerous ambiguity.

**Functional Design Specification (FDS)** appears in manufacturing, industrial control systems (SCADA/DCS), and regulated industries. It details how functions identified in the FRS will be implemented. The abbreviation "FDD" for Functional Design Document is uncommon and collides with Feature-Driven Development.

**Product Design Document (PDD)** is well-established in **RPA** (as Process Design Document) but is not a standard artifact in broader engineering. In general product development, it's an informal term without standards backing.

### Tier 3: Non-existent or constructed-by-matrix

**Business Design Specification (BDS), Business Design Document (BDD), Business Test Specification (BTS), Business Test Document (BTD)** — none of these exist. Web searches return zero relevant results. "Business" doesn't have a "Design" phase in any recognized framework; business-level design is captured in solution architecture documents or functional specifications. "BDD" as an abbreviation overwhelmingly refers to Behavior-Driven Development.

**Product Test Specification (PTS), Product Test Document (PTD)** — not standard document types. Testing standards (IEEE 829, ISO 29119) define specific artifacts: Test Plan, Test Design Specification, Test Case Specification, Test Procedure Specification, and Test Summary Report. The word "Product" isn't used as a qualifier in any testing standard.

**Functional Test Specification (FTS), Functional Test Document (FTD)** — not distinct document types. Functional testing produces standard test artifacts with "functional" as a qualifier, not a document type.

**Solution Requirements Specification** with abbreviation "SRS" — using "SRS" for anything other than Software Requirements Specification creates a collision with the most established abbreviation in requirements engineering. "Solution Requirements" is not a standard document type in IEEE, ISO, or INCOSE.

---

## The seven words that actually matter in document naming

The semantic distinction between "specification," "document," "plan," "report," and "record" is not arbitrary — it maps to a formal taxonomy defined by **ISO/IEC/IEEE 15289:2019**, which identifies exactly seven generic document types used across all systems and software engineering:

**Specification** is prescriptive and normative. It defines requirements, constraints, or design characteristics that SHALL be met. Specifications use imperative language ("shall," "must") and establish verifiable criteria. Every statement in a specification must be testable. Specifications are binding — often contractually or regulatorily.

**Description** characterizes an item as it is or as designed. IEEE 1016 deliberately chose "Software Design **Description**" rather than "Specification" because a design document describes a chosen approach rather than prescribing one. Similarly, ISO 42010 defines "Architecture **Description**." Descriptions are informative rather than normative.

**Plan** specifies what will be done, when, by whom, and with what resources. Plans are forward-looking and resource-oriented. A **Test Plan** (managerial: scope, schedule, resources) is fundamentally different from a **Test Specification** (technical: what to test, how to test it). They are complementary, not synonymous.

**Report** provides retrospective information about activities performed, results achieved, and assessments made. Reports are backward-looking and evaluative. A Test Summary Report summarizes completed testing; a Test Specification defines upcoming testing.

**Record** captures a point-in-time, immutable artifact — a decision, event, or state. Per ISO 15489, records serve as evidence. Architecture Decision Records (ADRs) exemplify this: each captures a single decision with context, alternatives, and consequences, and is **append-only** (new ADRs supersede old ones rather than editing existing ones).

The remaining two types are **Policy** (organizational directives) and **Procedure** (step-by-step instructions), plus **Request** (solicitation for action, e.g., Change Request).

This framework resolves the user's key synonym questions definitively. **FRD and FRS are the same thing** — the choice between "Document" and "Specification" is organizational preference with no semantic weight in practice, even though formally "Specification" implies greater normative force. **SDD and SDS are the same thing** — IEEE chose the third option, "Description," to sidestep this ambiguity entirely. The user's {Spec, Document} dimension in their taxonomy should be expanded to at least {Specification, Description, Plan, Report, Record} to capture the actual distinctions that matter.

---

## What the user's taxonomy is missing entirely

The taxonomy's most significant structural gaps fall into three categories: missing domain categories, missing lifecycle phases, and missing document sub-types.

### Missing domain categories

**System** is the most critical gap. IEEE 29148 defines a clear hierarchy: Stakeholder Requirements Specification (StRS) → **System Requirements Specification (SyRS)** → Software Requirements Specification (SRS). The user has "Product" and "Software" but no "System" — which is the engineering-level document that sits between them and that allocates requirements to hardware, software, and interface subsystems. For any product combining hardware and software, the System Requirements Specification is the single source of truth for the whole system.

**Hardware** is entirely absent. A hardware+software startup needs: Hardware Requirements Specification (HRS), Hardware Design Document (HDD), schematics, PCB layouts, BOMs, fabrication drawings, DFM reports, DFT reports, and environmental test specifications. None of these have homes in the current taxonomy. Hardware documents have fundamentally different characteristics from software documents — they specify physical constraints (dimensions, weight, thermal limits, power budgets), reference specific manufacturer part numbers, and must be rigorous enough to drive manufacturing.

**Interface** documentation — specifically Interface Control Documents (ICDs) and Hardware/Software Interface Documents — is the **#1 integration risk area** for embedded systems. An ICD defines the contract between subsystems: signal levels, pin assignments, protocols, data formats, timing, register maps, memory maps, interrupt assignments. Without dedicated interface documentation, hardware and firmware teams cannot coordinate.

### Missing lifecycle phases

The taxonomy covers only the BUILD phase. **Pre-requirements documents** are missing: Concept of Operations (ConOps, IEEE 1362), which describes how the system will be used from users' viewpoint; Vision Document; Market Requirements Document (MRD), which documents market opportunity, customer pain points, and competitive landscape; Feasibility Studies; and Trade Studies for structured comparison of design alternatives.

**Manufacturing/production documentation** is missing: Engineering Specifications (the "build-to" spec sent to factories), fabrication drawings, assembly drawings, DFM and DFT reports, and the Bill of Materials — arguably the most important document a hardware company produces.

**Post-release documentation** is missing: Release Notes, Field Failure Reports, Post-Mortems, and the entire feedback loop from operations back to design.

### The testing hierarchy needs decomposition

The user's single "Test" column masks a well-defined hierarchy from IEEE 829 / ISO 29119 that distinguishes **eight** test document types. At minimum, the taxonomy should separate: **Test Plan** (strategy, scope, schedule — a management document), **Test Specification** (test design, test cases, test procedures — a technical document), and **Test Report** (results, assessment, pass/fail judgment — an evaluative document). Collapsing these into one category loses critical information about who creates each, when, and for what purpose.

---

## The canonical flow from business need to verified product

Documents don't exist in isolation — they form a directed graph of dependencies that follows the **V-model**, the standard framework used by INCOSE, IEEE, NASA, and commercial engineering organizations since its documentation at Hughes Aircraft circa 1982.

### The left side: decomposition from need to component

The flow from business need to implementation follows a progressive refinement:

**Business/Mission Need** → **ConOps** (operational view: how will it be used?) → **BRD/MRD** (why build it? business justification) → **PRD/StRS** (what features for which users?) → **System Requirements Specification** (what must the system do technically?) → then **allocation** splits requirements into parallel streams: **Software Requirements Specification**, **Hardware Requirements Specification**, and **Interface Control Document**. Each requirements spec then drives its corresponding design document: SDD for software, HDD for hardware. Design documents drive implementation: code, schematics, PCB layouts, mechanical designs.

Each level asks a progressively more specific question. BRD asks "Why?" PRD asks "What value for whom?" SyRS asks "What technically?" SRS/HRS ask "How must each subsystem work?" Design documents answer "How will we build it?"

### The right side: integration from component to validated system

The V-model's right side mirrors the left, with each verification level corresponding to a decomposition level:

| Left side (Decomposition) | Right side (Verification) |
|---|---|
| ConOps / Stakeholder Needs | Acceptance Testing / Operational Validation |
| System Requirements (SyRS) | System Testing (functional + non-functional) |
| Subsystem Architecture | Integration Testing (interface verification) |
| Component/Module Design | Unit/Component Testing |

The horizontal correspondences are not arbitrary — they define **who verifies what against what**. Unit tests verify components against detailed design specs. Integration tests verify subsystem interfaces against architectural design. System tests verify the complete system against the SyRS. Acceptance tests validate the product against the ConOps and business need. The critical distinction: **verification** asks "did we build it right?" while **validation** asks "did we build the right thing?"

### Functional vs. non-functional is orthogonal, not hierarchical

A common misconception is that "functional requirements" are a level in the decomposition hierarchy. They are not. Functional and non-functional requirements are an **orthogonal categorization axis** that applies at every level. System-level functional requirements ("system shall track inventory") coexist with system-level non-functional requirements ("system shall process 1,000 transactions/sec"). Software-level, hardware-level, and component-level requirements all have both functional and non-functional dimensions. This means "Functional" should not be a row in the taxonomy alongside "Product" and "Software" — it's a property of requirements at every level.

### Requirements traceability and derived requirements

Every requirement should trace forward to design elements and test cases, and backward to stakeholder needs. This is maintained through a **Requirements Traceability Matrix (RTM)** — mandatory in regulated industries, strongly recommended everywhere. Forward traceability ensures every requirement is implemented and tested; backward traceability ensures every deliverable traces to an original need and prevents scope creep.

**Derived requirements** deserve special attention: these are requirements that emerge from design decisions rather than flowing down from higher-level requirements. Choosing a specific communication protocol creates requirements for that protocol. Selecting an off-the-shelf component introduces that component's constraints. Derived requirements should be documented in the same specification as other requirements at that level but **clearly marked as derived**, because they can be changed without stakeholder approval and may become obsolete when design decisions change.

---

## Hardware documentation has no software equivalent

For embedded systems and consumer electronics, an entire category of documentation exists that has no parallel in software development. These documents deal with the physical world — materials, manufacturing, environmental conditions, and regulatory certification.

**Schematic diagrams** are the hardware equivalent of source code: they define circuit connectivity, components, signal paths, and power rails. **PCB layout files** define the physical arrangement of copper traces on the circuit board. **Fabrication drawings** (governed by IPC-D-325) specify board dimensions, layer stack-up, materials, drill charts, impedance requirements, and surface finish for the PCB manufacturer. **Assembly drawings** specify component placement, orientation, and soldering requirements. **Mechanical drawings** (governed by ASME Y14.100 and Y14.5 for GD&T) define enclosures, mounting features, and connector placement.

**Manufacturing data formats** — Gerber files (RS-274X), ODB++, and IPC-2581 — function as "documents" even though they're machine-readable data. **IPC-2581** is the emerging open standard that packages all manufacturing data (layers, netlist, BOM, test points, stack-up) in a single XML file, though Gerber remains dominant.

**Design for Manufacturing (DFM) documentation** analyzes whether a design can be efficiently manufactured: trace width/spacing compliance, minimum drill sizes, component placement for automated assembly, panelization strategy. PCB fab houses often provide free DFM checks, and **70% of manufacturing costs are determined at the design stage**, making DFM reports among the highest-ROI documents a hardware startup can produce.

**Design for Test (DFT) documentation** ensures manufactured products can be efficiently verified: test point placement, in-circuit test fixture requirements, boundary scan (JTAG) chain design, and built-in self-test capabilities. Without DFT, you cannot cost-effectively verify manufactured boards at scale.

**Environmental and reliability test specifications** cover thermal cycling (IEC 60068), vibration, EMC emissions and immunity (CISPR 32, IEC 61000 series), and ESD (IEC 61000-4-2). **EMC testing is mandatory** — FCC certification is required for any electronic device oscillating above 9 kHz sold in the US, and CE marking is required for the EU market. Even "non-regulated" hardware companies must obtain these certifications.

The **Hardware/Software Interface Document** is critical for embedded systems. It defines register maps with bit-field definitions, interrupt assignments, memory maps, bus protocol configurations (SPI, I2C, UART, CAN), GPIO assignments, timing diagrams, and power sequencing requirements. This document must be co-authored and co-maintained by both hardware and firmware engineers.

---

## What the formal standards actually define

Ten standards and frameworks are most relevant to a non-regulated hardware+software startup, ranked by practical utility:

**Pragmatic Institute Framework** (High relevance) distinguishes MRD (problem space: personas, their problems, market opportunity) from PRD (solution space: features, user stories, acceptance criteria). Its key insight: requirements should be written as **problems to be solved for specific personas**, not feature lists. This prevents over-engineering and keeps focus on product-market fit.

**ISO 9001:2015** (Medium-High relevance) requires "documented information" but doesn't prescribe formats. The practical document hierarchy is: Quality Policy → Procedures → Work Instructions → Records. Even non-regulated startups benefit from lightweight quality management, and many B2B customers require ISO 9001 certification. The 2015 revision eliminated the mandatory Quality Manual and reduced prescriptiveness.

**IEEE 29148:2018** (Medium relevance) is the current requirements engineering standard, superseding IEEE 830. It defines four specification types: **StRS** (Stakeholder Requirements), **SyRS** (System Requirements), **SRS** (Software Requirements), and **OpsCon** (Operational Concept). The templates provide excellent structural guidance even if a startup doesn't follow them formally. Its requirements classification aligns with BABOK's four-tier scheme: Business → Stakeholder → Solution (functional + non-functional) → Transition.

**BABOK v3** (Medium relevance) doesn't prescribe document formats but defines a powerful requirements classification: Business Requirements → Stakeholder Requirements → Solution Requirements (subdivided into Functional and Non-Functional) → Transition Requirements. The 50+ elicitation techniques are directly useful.

**IEEE 1016** (Medium relevance) defines the Software Design Description (SDD) structure: design views organized by viewpoints (architectural, logical, physical, process). The concept of multiple **views** of the same architecture — each serving different stakeholders — is valuable regardless of format.

**ISO/IEC/IEEE 42010:2022** (Medium relevance) defines Architecture Description as composed of views, viewpoints, stakeholder concerns, and architecture decisions. The key concept: architecture documentation should be organized around stakeholder concerns, with each **viewpoint** defining conventions for one type of **view**. Practically, this means having a system context diagram, a decomposition view, and documented architecture decisions.

**IEEE 15288:2023** and **IEEE 12207:2017** (Medium relevance) define system and software lifecycle processes respectively, with **IEEE 15289** serving as the companion standard that maps processes to the seven generic document types. The process checklists help ensure nothing critical is missed in engineering workflow design.

**PMBOK 7th Edition** (Medium relevance) defines artifacts in 9 categories including Strategy Artifacts (Project Charter, Roadmap), Log Artifacts (Risk Register, Backlog), Plan Artifacts (14 types of management plans), and Hierarchy Charts (WBS). A startup primarily needs: Project Charter (lightweight), Risk Register, and WBS for hardware development scheduling.

**SAFe** (Low-Medium relevance) defines a useful artifact hierarchy: **Epic → Capability → Feature → Story** and introduces **Solution Intent** as a living repository for both fixed requirements (compliance) and variable requirements (still being explored). These concepts are applicable even outside the full SAFe framework.

**CMMI** (Low relevance for startups) defines "typical work products" per process area but is designed for organizational maturity assessment in large enterprises. The underlying concepts (requirements management, configuration management, verification) are universally valuable even though formal CMMI appraisal provides no startup benefit.

---

## How companies actually handle documentation

The gap between what standards prescribe and what practitioners produce is enormous. Understanding real-world patterns prevents over-engineering a documentation system.

### Startups collapse everything into the PRD

The overwhelming practitioner consensus is that startups and small teams don't write BRD, SRS, and SDD separately. A widely-cited observation captures reality: "Relax. We only use the PRD. The rest are just ghosts of Waterfall past." Teams under 20 people typically use the PRD as their primary documentation artifact, with user stories in Jira/Linear serving as the living specification. Formal BRD/SRS are omitted entirely. The hardware accelerator **Bolt** advises keeping PRDs "lean and useful" — they've seen portfolio companies produce 42-page PRDs that became "essentially a full-time job to maintain" and recommend a fill-in-the-blank template focused on success attributes rather than technical specifications.

### Notable company practices reveal four documentation philosophies

**Amazon's six-pager** is a structured narrative document (no bullet points, no slides) read silently for 20-25 minutes at meeting starts. Its sections — Introduction, Goals, Tenets, State of the Business, Lessons Learned, Strategic Priorities, Appendix — function as a combined strategy and planning document, not a PRD. Amazon also uses the **Backwards Press Release** for new product proposals, working backward from a hypothetical launch announcement. The discipline of narrative writing forces clarity that slide decks don't.

**Google's design docs** combine what would traditionally be separate PRD and SDD content into a single document. Key sections: Context/Scope, Goals/Non-Goals, the Actual Design (with trade-offs), and Alternatives Considered ("one of the most important sections"). The sweet spot is **10-20 pages** for major projects, 1-3 pages for smaller ones. Google's rule: if the solution is obvious with no meaningful trade-offs, don't write a design doc at all.

**Stripe** treats documentation as a product quality signal. Documentation expectations exist in every level of the engineering job ladder, and managers must take this seriously at performance review time. Features aren't considered shipped until documentation is written, reviewed, and published. Stripe created writing classes for ESL engineers and open-sourced Markdoc for interactive documentation. Their "friction logs" — stream-of-consciousness documents from a user's perspective — are a distinctive artifact type.

**Oxide Computer** (a hardware+software startup building rack-scale computers) uses **Requests for Discussion (RFDs)** — numbered AsciiDoc documents in a Git repository, inspired by IETF RFCs. RFDs cover everything: technical designs, hardware decisions, software APIs, company processes, and values statements. With **490+ RFDs** published, they serve as combined requirements, design, and decision documents organized around problems, options, trade-offs, and determinations. For hardware specifically, RFD 5 notes that "the process is necessarily more linear with respect to time" — once a determination is made, development, validation, stress testing, and production are formally demarcated with hardware builds.

### Hardware requires more formality than software

You cannot manufacture without: BOM, schematic, PCB Gerber files, mechanical drawings with tolerances, assembly instructions, test procedures, and quality acceptance criteria. The factory needs "clear documentation of what passes and what fails" with defined tolerances, cosmetic standards, and functional test criteria. The hardware startup lifecycle follows: **POC → Prototype → DVT (Design Validation Test) → PVT (Production Validation Test) → Production**, with documentation requirements increasing at each gate. In hardware, the concept of an "MVP" means tests and prototypes, not shipping minimal products — changes after production starts are prohibitively expensive.

### Living documents and baselined specifications serve different purposes

PRDs and design docs should be **living documents** that evolve through discovery, then freeze at development start. Requirements specifications and BOMs should be **baselined at milestones** — manufacturing and testing need frozen targets. User and API documentation should be **continuously updated** to reflect current product state. Architecture documents should be **living** but with decision records captured as immutable snapshots. Most startups start with wikis (Notion, Confluence) for everything and only adopt formal document management systems when they hit manufacturing or regulatory requirements.

---

## The Goldilocks zone for document depth

Detail level has a clear sweet spot for each document type, with a practical testability criterion for each:

A **PRD at the right level** runs 3-8 pages for a software feature (lean template for hardware) and contains problem statement with user evidence, measurable success criteria, personas, use cases, scope boundaries, and constraints — but not technical implementation details, specific UI designs, or database schemas. **Test: can a designer and engineer start working without asking "what problem are we solving?"**

An **SRS at the right level** is only needed for regulated products, contracted work, complex multi-team systems, or hardware interfaces. It contains testable functional requirements (SHALL language), quantified non-functional requirements, interface specifications, and data dictionaries. **Test: can a QA engineer write test cases directly from this?**

A **design document at the right level** follows Google's model at 10-20 pages for major projects: architecture overview, system-context diagram, API sketches, data model, key algorithms, trade-offs with alternatives rejected and why, and cross-cutting concerns. **Test: does it explain WHY this design over alternatives? Can a new team member understand the system?**

A **hardware specification at the right level** contains functional requirements, quantified performance targets, environmental operating conditions, physical dimensions/weight targets, power budget, interface specs, regulatory requirements, and reliability targets — but not specific component choices (unless mandated) or circuit designs. **Test: can a design engineer make component and architecture choices from this?**

**When a PRD becomes too detailed**, it specifies database column names, UI colors, or specific algorithms. When a spec becomes too vague, it uses words like "should," "appropriate," or "user-friendly" without measurable criteria. The boundary between requirements and design is: if removing a statement still leaves the problem clearly defined but gives engineers freedom to solve it differently, it belongs in the PRD; if removing it would leave engineers unable to build, it belongs in the spec.

---

## Twelve documentation categories the taxonomy doesn't cover

The user's taxonomy covers only the BUILD phase and is entirely internal/engineering-facing. At least twelve categories of documentation fall outside its boundaries, several of which are mandatory even for "non-regulated" startups.

**Regulatory compliance documentation** is the most surprising gap because even "non-regulated" hardware companies must obtain FCC certification (any electronic device above 9 kHz in the US), CE marking (EU), and typically RoHS/REACH compliance. FCC failure means fines, product bans, and customs seizures. From August 2025, the EU Radio Equipment Directive mandates cybersecurity requirements for wireless products.

**Security documentation** — threat models, security requirements, penetration test reports — is non-negotiable for any connected hardware product. Per PSA Certified's 2023 report, only **40%** of companies perform threat modeling for every new product.

**Supply chain and procurement documentation** — BOM management, Approved Vendor Lists (AVL), component qualification reports, second-source documentation — represents the single most critical hardware startup activity with no home in the current taxonomy.

**Operations/deployment documentation** (runbooks, infrastructure docs, manufacturing setup), **user documentation** (manuals, API docs, quick-start guides), **maintenance documentation** (service manuals, troubleshooting guides), and **post-market documentation** (field failure reports, post-mortems) all represent lifecycle phases the taxonomy doesn't address.

The taxonomy is also missing key **structural dimensions**: a **Lifecycle Phase** dimension (Concept → Build → Produce → Deploy → Operate → Retire), an **Audience** dimension (internal engineering vs. external users vs. regulators vs. manufacturing partners), and a **Product vs. Process** dimension (what we build vs. how we work — the taxonomy has no home for QMS documentation, engineering handbooks, or SOPs).

---

## A practical documentation framework for a hardware+software startup

Synthesizing across all research areas, the user's original {Product, Business, Solutions, Software, Functional} × {Requirements, Design, Test} × {Spec, Document} matrix should be restructured along three axes:

**Domain axis** should be: {Business, Product, System, Software, Hardware, Interface} — dropping "Solutions" (abbreviation conflicts, not a standard domain), "Functional" (it's an attribute of requirements at every level, not a standalone domain), and adding the three critical missing domains.

**Lifecycle axis** should expand beyond {Requirements, Design, Test} to at minimum: {Concept, Requirements, Design, Implementation, Test, Production, Operations} — reflecting the full product lifecycle rather than just the build phase.

**Artifact type axis** should expand from {Spec, Document} to align with IEEE 15289's taxonomy: {Specification, Description, Plan, Report, Record, Procedure} — each carrying distinct semantic weight.

Not every cell in this expanded matrix needs to be filled. The cells that correspond to real, widely-recognized document types are a small subset. A startup's minimum viable documentation set is approximately: Product Brief or PRD (Business × Concept-Requirements), System Requirements Specification (System × Requirements × Specification), Software and Hardware Design Documents (Software/Hardware × Design × Description), Interface Control Document (Interface × Design × Specification), Bill of Materials (Hardware × Implementation), Test Plan + Test Report (System × Test × Plan/Report), and Architecture Decision Records as a lightweight running log of design decisions.

The most important insight from this research is that **the document hierarchy should be driven by audience and decision needs, not by taxonomic completeness**. Every cell in a matrix doesn't need a document — only the ones where a real person needs specific information to make a specific decision or perform a specific task. Start with the minimum set, add documents only when their absence causes visible problems, and when possible, let a single document serve multiple purposes (as Google's design docs and Oxide's RFDs demonstrate). The standards provide the map; the team's actual coordination needs determine which territories to inhabit.

## Conclusion

Three findings reshape how to think about documentation taxonomy. First, **the "spec vs. document" distinction carries real semantic weight in formal standards but has almost entirely eroded in practice** — the more useful distinction is between the seven IEEE 15289 types (specification, description, plan, report, record, procedure, policy), each of which signals a different document purpose and lifecycle. Second, **"Functional" is a property of requirements, not a document domain** — placing it alongside "Software" and "Product" in a matrix creates ghost documents that no one will ever write. The correct organizational principle is the decomposition hierarchy (Business → Product → System → Hardware/Software/Interface) crossed with the V-model lifecycle (Requirements → Design → Implementation → Test), with functional and non-functional as orthogonal attributes at every level. Third, **the biggest gaps in the taxonomy aren't missing document types within the existing framework but entirely missing categories outside it** — hardware manufacturing documentation, regulatory compliance, supply chain management, and operations/maintenance documentation represent mandatory work products that have no home in a requirements-design-test matrix. The most successful documentation systems (Google's design docs, Oxide's RFDs, Amazon's six-pagers) succeed not because they fill every cell in a taxonomy but because they are optimized for their actual coordination problem: helping the right people make the right decisions with the right information at the right time.
