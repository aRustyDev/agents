# Decomposing Research Questions

When and how to break broad research questions into focused sub-questions, each suitable for its own search matrix.

## Table of Contents

- [When to Decompose](#when-to-decompose)
- [Decomposition Strategies](#decomposition-strategies)
- [Decomposition Process](#decomposition-process)
- [Anti-Patterns](#anti-patterns)

---

## When to Decompose

Decompose when a single matrix cannot adequately cover the research question. Signals:

**Decompose when:**
- The question spans multiple unrelated domains (e.g., "How do CRDTs work and what are their tax implications?")
- Answering it would require more than 3 tiers of 4+ queries each
- The question contains "and" joining distinct sub-topics with different engine needs
- Different parts of the question need different research types (e.g., one part is a survey, another is verification)
- The expected results for different parts would be graded on entirely different criteria

**Do NOT decompose when:**
- The question is broad but within a single domain (a survey matrix handles this)
- The sub-topics share engines and operators (grouping is more efficient)
- Decomposition would produce sub-questions too narrow to have meaningful search results
- The user explicitly asked for a single broad matrix (respect the intent)
- The breadth IS the point (e.g., "Give me a landscape overview of...")

**Key principle:** Prefer multiple focused matrices over one sprawling matrix, but do not over-split. Each sub-question must be independently useful and searchable.

---

## Decomposition Strategies

### By Facet

Split the question into its constituent facets, where each facet is a distinct aspect of the topic.

**When to use:** The question asks about multiple aspects of the same subject.

**Example:**
- Original: "What is the state of WebAssembly for server-side applications — performance, ecosystem, and production adoption?"
- Sub-questions:
  1. "What is the runtime performance of WebAssembly compared to native code on the server?"
  2. "What server-side WebAssembly frameworks, runtimes, and tools exist?"
  3. "Which companies are using WebAssembly in production server workloads?"

**Why this works:** Each facet uses different engines (benchmarks vs registries vs case studies) and has different grading criteria.

### By Domain

Split the question when it crosses domain boundaries that require different engine categories.

**When to use:** Different parts of the question live in different search ecosystems.

**Example:**
- Original: "How should we implement real-time collaboration, and what are the HIPAA implications?"
- Sub-questions:
  1. "What libraries and patterns exist for real-time collaborative editing?" (tech domain)
  2. "What are the HIPAA compliance requirements for real-time data synchronization in healthcare?" (regulatory domain)

**Why this works:** The tech question uses code platforms and package registries; the regulatory question uses FDA, PubMed, and legal databases. Mixing them in one matrix wastes queries.

### By Depth

Split when the question has both a surface-level and deep-level component.

**When to use:** The user needs both a broad overview and deep analysis, but at different levels.

**Example:**
- Original: "What ORMs exist for TypeScript and how does Prisma handle migrations internally?"
- Sub-questions:
  1. "What ORM options exist for TypeScript?" (survey)
  2. "How does Prisma's migration engine work internally?" (deep-dive)

**Why this works:** The survey needs breadth (many engines, broad queries); the deep-dive needs precision (Prisma docs, GitHub source code, specific technical content). Different matrix shapes.

### By Time Horizon

Split when the question asks about both historical and current/future states.

**When to use:** The question spans time periods that require different search strategies.

**Example:**
- Original: "How has the container orchestration landscape evolved and where is it headed?"
- Sub-questions:
  1. "What was the container orchestration landscape in 2018-2022?" (historical)
  2. "What are the current and emerging container orchestration platforms in 2024-2025?" (current)

**Why this works:** Historical questions benefit from `before:` date operators and may rely on archived content. Current questions use `after:` operators and prioritize recency.

### By Jurisdiction

Split when the question spans regulatory or legal jurisdictions that have different governing bodies, terminology, and source databases.

**When to use:** The question asks about regulations, compliance, or legal frameworks across multiple countries or governing bodies (e.g., US federal + EU + state-level).

**Example:**
- Original: "Does our AI insurance tool need regulatory approval?"
- Sub-questions:
  1. "Does the FDA regulate AI software used in insurance claim processing?" (US federal — FDA)
  2. "What SEC disclosure obligations apply to AI in insurance?" (US federal — SEC)
  3. "How does the EU AI Act classify AI systems used in insurance?" (EU — EC/EIOPA)
  4. "What state-level AI insurance regulations exist?" (US state — NAIC, Colorado AI Act)

**Why this works:** Each jurisdiction has different authoritative sources (FDA.gov vs EUR-Lex vs state DOI sites), different terminology ("SaMD" vs "high-risk AI system" vs "algorithmic discrimination"), and different engine strategies (EDGAR for SEC filings vs EU legislative portals). A single matrix cannot efficiently target all of these — the operator sets and acceptance criteria are too different.

**Execution note:** Jurisdiction sub-questions are usually independent and can run in parallel. The synthesis step is where jurisdictional findings get combined into a unified compliance picture.

---

## Decomposition Process

### Step 1: Identify the Core Intent

Before splitting, make sure you understand what the user actually wants. A question that sounds broad might have a narrow intent.

Ask: "If I could only give the user one thing, what would it be?" That is the primary matrix. Everything else is secondary.

### Step 2: Propose Sub-Questions

Generate candidate sub-questions. For each candidate, check:
- Is it independently searchable? (Can you write a matrix for it on its own?)
- Does it need different engines than the other sub-questions?
- Would it be graded on different criteria?
- Does it produce results that are useful without the other sub-questions?

If a candidate fails these checks, it should stay merged with another sub-question.

### Step 3: Present to the User

**Always present the decomposition to the user before proceeding.** Do not silently split a question. Example format:

> This question covers multiple distinct areas. I recommend splitting into [N] matrices:
>
> 1. "[Sub-question 1]" -- [brief rationale]
> 2. "[Sub-question 2]" -- [brief rationale]
> 3. "[Sub-question 3]" -- [brief rationale]
>
> Should I proceed with this split, adjust the sub-questions, or keep it as a single matrix?

### Step 4: Prioritize

If the user approves, ask which sub-question to tackle first (or state a recommended order). Typically:
- Start with the broadest sub-question (survey/landscape) to establish context
- Follow with focused sub-questions (deep-dive/verification) that build on the landscape
- End with comparative sub-questions that synthesize findings

### Step 5: Build Independent Matrices

Each sub-question gets its own complete matrix with its own tiers, engines, operators, and grading criteria. Sub-question matrices are independent: each can be executed, graded, and reported on without reference to the others.

---

## Anti-Patterns

### Over-Splitting

**Problem:** Decomposing into too many sub-questions, each too narrow to produce meaningful results.

**Symptoms:**
- Sub-questions that can be answered with a single query
- Sub-questions that all use the same engines and operators
- More than 5 sub-questions from a single original question

**Fix:** Merge sub-questions that share engines, operators, and grading criteria. A good matrix can have 3-4 queries per tier; not every query needs its own matrix.

### Under-Splitting

**Problem:** Keeping a question as a single matrix when it clearly spans multiple domains.

**Symptoms:**
- Tier 1 uses academic databases; Tier 2 uses package registries; Tier 3 uses regulatory databases (these are not "fallbacks" — they are different research threads)
- Acceptance criteria differ fundamentally between tiers
- Results from different tiers cannot be meaningfully compared or combined

**Fix:** If different tiers are serving different sub-questions, they should be separate matrices.

### Silent Decomposition

**Problem:** The agent decomposes the question without telling the user.

**Symptoms:**
- Multiple matrices appear without the user approving the split
- The user's original question is not addressed as-stated
- Sub-questions introduce scope the user did not ask for

**Fix:** Always present the decomposition to the user and wait for confirmation. This is a hard rule, not a suggestion.

### Decomposing Surveys

**Problem:** Splitting a deliberately broad question into narrow sub-questions when the user wanted a landscape overview.

**Symptoms:**
- The user asked "What options exist for X?" and received 5 narrow sub-matrices instead of one survey matrix
- The breadth of the original question was the point, not a problem

**Fix:** Recognize when breadth is intentional. Survey-type research questions should stay as single matrices with broad queries. The tiers handle depth (narrow to broad), not the decomposition.

### Losing the Thread

**Problem:** Sub-questions drift from the original research question.

**Symptoms:**
- Sub-questions introduce topics the user did not ask about
- The sum of the sub-questions does not equal the original question
- Results from all sub-questions combined still leave the original question unanswered

**Fix:** After generating sub-questions, verify: "If I answer all of these, does the original question get answered?" If not, revise the sub-questions.
