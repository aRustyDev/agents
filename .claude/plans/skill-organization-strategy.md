# Skill Organization Strategy

**Created:** 2025-12-25
**Status:** Draft
**Purpose:** Define naming conventions, taxonomy, and merge strategy for external skills

---

## Naming Convention

### Pattern
```
<category>-[<subcategory>-]<tool>-<focus>
```

### Examples
| Full Name | Category | Subcategory | Tool | Focus |
|-----------|----------|-------------|------|-------|
| `cicd-github-actions-dev` | cicd | - | github-actions | dev |
| `cicd-github-actions-ops` | cicd | - | github-actions | ops |
| `data-ingest-weaviate-ops` | data | ingest | weaviate | ops |
| `cloud-aws-terraform-eng` | cloud | aws | terraform | eng |
| `lang-rust-cargo-dev` | lang | rust | cargo | dev |
| `llm-rag-langchain-dev` | llm | rag | langchain | dev |
| `observability-metrics-prometheus-ops` | observability | metrics | prometheus | ops |

---

## Focus Taxonomy

| Focus | Code | Description | Target Audience |
|-------|------|-------------|-----------------|
| Operations | `ops` | Day-to-day operations, troubleshooting, maintenance | SRE, Platform Engineers, Admins |
| Development | `dev` | Building, coding, implementing features | Developers, Contributors |
| Engineering | `eng` | Architecture, design patterns, optimization | Senior Engineers, Architects |
| Newcomer | `nub` | Learning-focused, tutorials, onboarding | New users, Beginners |
| Executive | `xec` | Strategy, cost analysis, high-level overview | Managers, CTOs, Decision-makers |

### Focus Overlap Rules
- A skill can only have ONE focus
- If content serves multiple focuses, split into separate skills
- Reference files can be shared across focus variants

---

## Category Taxonomy

### Primary Categories (16)

| Category | Code | Description | Subcategories |
|----------|------|-------------|---------------|
| AI/ML | `ai` | Machine learning, models, training | train, infer, eval, finetune |
| Backend | `backend` | Server-side development | api, graphql, grpc, websocket |
| CI/CD | `cicd` | Continuous integration/deployment | github, gitlab, jenkins, argocd |
| Cloud | `cloud` | Cloud infrastructure | aws, gcp, azure, cloudflare |
| Data | `data` | Data engineering & processing | ingest, transform, quality, stream |
| Database | `db` | Database operations | postgres, mongodb, redis, vector |
| Frontend | `frontend` | Client-side development | react, vue, svelte, css |
| Kubernetes | `k8s` | Container orchestration | helm, gitops, security, networking |
| Language | `lang` | Language-specific patterns | rust, python, go, typescript, elixir |
| LLM | `llm` | LLM applications | rag, prompts, agents, eval |
| Meta | `meta` | Skill/agent development | skills, plugins, mcp, hooks |
| Methodology | `method` | Development methodologies | debugging, tdd, planning, review |
| Observability | `observability` | Monitoring & logging | metrics, tracing, logging, alerts |
| Scientific | `sci` | Scientific computing | stats, bio, quantum, viz |
| Security | `security` | Security practices | scan, pentest, compliance, secrets |
| Workflow | `workflow` | Automation tools | n8n, temporal, airflow, make |

### Subcategory Examples

```yaml
ai:
  - train      # Training models
  - infer      # Inference/serving
  - eval       # Evaluation & benchmarks
  - finetune   # Fine-tuning
  - safety     # AI safety & alignment

cicd:
  - github     # GitHub Actions
  - gitlab     # GitLab CI
  - jenkins    # Jenkins
  - argocd     # ArgoCD
  - tekton     # Tekton

cloud:
  - aws        # Amazon Web Services
  - gcp        # Google Cloud Platform
  - azure      # Microsoft Azure
  - cloudflare # Cloudflare
  - terraform  # Multi-cloud IaC

data:
  - ingest     # Data ingestion
  - transform  # Transformations (dbt, spark)
  - quality    # Data quality
  - stream     # Streaming (kafka, flink)
  - lake       # Data lakehouse

db:
  - postgres   # PostgreSQL
  - mongodb    # MongoDB
  - redis      # Redis
  - vector     # Vector databases
  - graph      # Graph databases

k8s:
  - helm       # Helm charts
  - gitops     # GitOps (flux, argocd)
  - security   # Pod security, policies
  - networking # Service mesh, ingress
  - operators  # Operator development

lang:
  - rust       # Rust
  - python     # Python
  - go         # Go
  - typescript # TypeScript
  - elixir     # Elixir
  - lean       # Lean4

llm:
  - rag        # Retrieval-augmented generation
  - prompts    # Prompt engineering
  - agents     # Agent development
  - eval       # LLM evaluation
  - embeddings # Embeddings & vectors

observability:
  - metrics    # Prometheus, metrics
  - tracing    # Distributed tracing
  - logging    # Log aggregation
  - alerts     # Alerting rules

security:
  - scan       # SAST, DAST scanning
  - pentest    # Penetration testing
  - compliance # GDPR, SOC2, ISO
  - secrets    # Secrets management
  - forensics  # Digital forensics
```

---

## Skill Structure Standard

### Directory Layout
```
<skill-name>/
├── SKILL.md              # Required: Main skill file
└── references/           # Optional: Reference materials
    ├── <topic>.md        # Topic-specific references
    └── <subtopic>/       # Nested for complex domains
        └── *.md
```

### SKILL.md Template
```markdown
---
name: <category>-[<subcategory>-]<tool>-<focus>
description: <Clear description of what this skill does and when to use it>
created: YYYY-MM-DDTHH:MM
updated: YYYY-MM-DDTHH:MM
tags: [<category>, <subcategory>, <tool>, <focus>]
source: <original-repo> # If imported/merged
---

# <Title>

<One-line description>

## Overview

<What this skill covers and does NOT cover>

**This skill covers:**
- ...

**This skill does NOT cover:**
- ...

## Quick Reference

<Tables, diagrams for fast lookup>

## Workflow: <Primary Use Case>

### Step 1: ...
### Step 2: ...
...

## Common Patterns

<Code examples for frequent tasks>

## Troubleshooting

<Common issues and solutions>

## See Also

- [references/<topic>.md](references/<topic>.md) - <description>
- `<related-skill>` skill - <relationship>
```

---

## Skill Analysis & Selection Criteria

### Evaluation Matrix

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Uniqueness | 30% | Does it fill a gap? Avoid duplicates |
| Quality | 25% | Well-structured, accurate, comprehensive |
| Maintainability | 20% | Active source? Clear ownership? |
| Focus Fit | 15% | Matches a defined focus level |
| Token Efficiency | 10% | Concise, uses references effectively |

### Selection Decision Tree

```
1. Does skill fill an identified gap?
   └─ NO → Skip (unless significantly higher quality than existing)
   └─ YES → Continue

2. Is there overlap with existing skill?
   └─ YES → Evaluate merge vs replace
      ├─ If external is clearly better → Replace
      ├─ If internal is better → Skip external
      └─ If complementary → Merge (combine best parts)
   └─ NO → Continue

3. Does skill fit naming convention?
   └─ NO → Rename to convention before import
   └─ YES → Continue

4. Is skill well-structured?
   └─ NO → Restructure during import
   └─ YES → Import as-is (with naming adjustment)
```

---

## Merge Strategy

### Merge Types

| Type | When | Process |
|------|------|---------|
| **Direct Import** | No overlap, fits convention | Rename, import, version track |
| **Replace** | External significantly better | Archive old, import new |
| **Enhance** | External has valuable additions | Add new sections/references |
| **Combine** | Multiple sources cover different aspects | Create new unified skill |
| **Split** | External covers multiple focuses | Create focus-specific variants |

### Merge Process

1. **Identify candidates** from external manifest
2. **Map to naming convention** (category, subcategory, tool, focus)
3. **Check for overlaps** with existing skills
4. **Evaluate quality** using criteria matrix
5. **Determine merge type** based on overlap and quality
6. **Execute merge** with version tracking
7. **Update manifest** with source attribution

---

## Priority Import List

Based on gap analysis and quality assessment:

### Tier 1: Critical (Import immediately)

| External Skill | Target Name | Source | Reason |
|----------------|-------------|--------|--------|
| mcp-builder | meta-mcp-builder-dev | anthropics/skills | MCP development |
| systematic-debugging | method-debugging-systematic-eng | obra/superpowers | Unique methodology |
| rag-implementation | llm-rag-patterns-dev | wshobson/agents | LLM patterns |
| terraform-module-library | cloud-terraform-modules-eng | wshobson/agents | IaC patterns |
| prometheus-configuration | observability-metrics-prometheus-ops | wshobson/agents | Monitoring |
| context-fundamentals | meta-context-engineering-dev | muratcankoylan | Meta-skill |

### Tier 2: High Priority

| External Skill | Target Name | Source | Reason |
|----------------|-------------|--------|--------|
| helm-chart-scaffolding | k8s-helm-charts-dev | wshobson/agents | K8s deployment |
| polars | data-analysis-polars-dev | K-Dense-AI | Modern dataframes |
| handling-rust-errors | lang-rust-errors-dev | hashintel/hash | Rust patterns |
| playwright-skill | frontend-testing-playwright-dev | lackeyjb | E2E testing |
| elixir-architect | lang-elixir-patterns-eng | maxim-ist | Fills language gap |

### Tier 3: As Needed

| Category | Skills to Import |
|----------|------------------|
| Scientific | qiskit, pymc, literature-review |
| AI Research | mechanistic-interpretability, safety-alignment |
| Lean4 | lean4-theorem-proving |
| Security | ffuf-web-fuzzing, sigma-threat-hunting |

---

## Implementation Plan

### Phase 1: Foundation
1. Create skill template in `components/skills/.templates/`
2. Add justfile recipe: `create-skill <name>`
3. Add validation script for naming/structure

### Phase 2: Priority Imports
1. Import Tier 1 skills (6 skills)
2. Rename to convention
3. Restructure if needed
4. Track versions in `.versions/`

### Phase 3: Bulk Processing
1. Create import automation for categories
2. Process Tier 2 skills
3. Create merged skills where needed

### Phase 4: Maintenance
1. Weekly check for updates (`just check-external-updates`)
2. Monthly quality review
3. Prune unused skills

---

## Justfile Recipes (Proposed)

```just
# Create new skill from template
[group('skills')]
create-skill name:
    @scripts/create-skill.py "{{ name }}"

# Validate skill naming and structure
[group('skills')]
validate-skill path:
    @scripts/validate-skill.py "{{ path }}"

# Bulk rename skills to convention
[group('skills')]
normalize-skill-names:
    @scripts/normalize-skills.py

# Import and restructure external skill
[group('skills')]
import-and-normalize repo skill target:
    just import-skill "{{ repo }}" "{{ skill }}" "{{ target }}"
    just validate-skill "components/skills/{{ target }}"
```

---

## Appendix: Full Category Mapping from External Manifest

| External Category | Maps To | Subcategory |
|-------------------|---------|-------------|
| anthropic-official | meta | skills |
| claude-code-plugin-dev | meta | plugins |
| methodology | method | - |
| context-engineering | meta | context |
| scientific | sci | - |
| backend-patterns | backend | - |
| data-engineering | data | - |
| cloud-infrastructure | cloud | - |
| kubernetes | k8s | - |
| cicd | cicd | - |
| llm-development | llm | - |
| observability | observability | - |
| security | security | - |
| python | lang | python |
| javascript-typescript | lang | typescript |
| rust | lang | rust |
| n8n | workflow | n8n |
| causal-analysis | sci | causal |
| crash-analysis | security | forensics |
| development-roles | meta | personas |
| business-marketing | meta | business |
| compliance | security | compliance |
| creative-design | frontend | design |
| ai-research | ai | research |
| elixir | lang | elixir |
| lean4 | lang | lean |
