# External Skills Analysis

**Generated:** 2025-12-25
**Source:** `external.yaml` manifest
**Total Skills Cataloged:** ~200
**Registries Identified:** 27

---

## Executive Summary

This analysis examines skills across 27 skill registries, categorized into 30+ functional areas. The ecosystem shows strong coverage in:
- **Enterprise development patterns** (wshobson/agents)
- **Scientific computing** (K-Dense-AI + davila7)
- **Methodology/debugging** (obra/superpowers)

Notable gaps exist in:
- Mobile development
- Game development
- IoT/embedded systems
- Desktop application patterns

---

## Category Analysis

### 1. Official Anthropic Skills

| Source | Skills | Quality | Notes |
|--------|--------|---------|-------|
| anthropics/skills | 11 | High | Canonical reference implementations |
| anthropics/claude-code | 8 | High | Plugin development focused |
| anthropics/claude-cookbooks | 3 | High | Finance and brand examples |
| anthropics/claude-plugins-official | 2 | High | Production patterns |

**Recommendation:** Import all. These are authoritative and well-maintained.

**Already Imported:**
- `skill-creator` → `claude-skill-dev` (with version tracking)

**Priority Imports:**
1. `mcp-builder` - Critical for MCP server development
2. `webapp-testing` - Testing patterns
3. `frontend-design` - Overlaps with claude-code version, compare first

---

### 2. Methodology & Debugging

| Source | Style | Strength |
|--------|-------|----------|
| obra/superpowers | Systematic, academic | Deep debugging methodology |
| wshobson/agents | Practical patterns | Enterprise-oriented |

**Overlap Analysis:**
- `systematic-debugging` (obra) vs `debugging-strategies` (wshobson)
  - obra: More theoretical, covers bisection, hypothesis testing
  - wshobson: More practical, CI/CD integration focused
  - **Recommendation:** Import both - complementary approaches

**Unique Value:**
- `root-cause-tracing` - Unique systematic approach
- `testing-anti-patterns` - Valuable for code review
- `defense-in-depth` - Security methodology

**Priority Imports:**
1. `systematic-debugging`
2. `root-cause-tracing`
3. `brainstorming`

---

### 3. Context Engineering

| Source | Coverage | Notes |
|--------|----------|-------|
| muratcankoylan/Agent-Skills-for-Context-Engineering | Complete | 8 skills covering full lifecycle |

**Unique Category:** No overlap with other registries.

**Skills:**
- `context-fundamentals` - Foundation
- `context-optimization` - Performance
- `context-compression` - Token efficiency
- `context-degradation` - Graceful handling
- `memory-systems` - Persistence patterns
- `tool-design` - Tool integration
- `evaluation` / `advanced-evaluation` - Quality assessment

**Recommendation:** High priority import for meta-skill development.

---

### 4. Scientific Computing

**Two major sources with different focus:**

| Source | Focus | Skill Count |
|--------|-------|-------------|
| K-Dense-AI | Tools & Libraries | 17 |
| davila7 | Research Workflow | 16 |

**Complementary Coverage:**

| Area | K-Dense-AI | davila7 |
|------|------------|---------|
| Data Analysis | polars, dask | exploratory-data-analysis |
| Statistics | statsmodels, pymc | - |
| Visualization | matplotlib, seaborn | plotly |
| Research | market-research-reports | literature-review, peer-review |
| Bio/Medical | neuropixels, histolab | anndata |
| Quantum | - | qiskit, pennylane, qutip |

**Overlap:**
- Both have visualization skills (different libraries)
- Both have research workflow skills

**Priority Imports:**
1. K-Dense-AI: `polars`, `pymc`, `matplotlib`
2. davila7: `literature-review`, `peer-review`, `qiskit`

---

### 5. Backend Development

**Primary Source:** wshobson/agents (8 skills)

**Coverage:**
- API design
- Microservices
- Event sourcing (CQRS, saga, projections)
- Workflow orchestration

**Quality:** Enterprise-grade patterns

**Priority Imports:**
1. `api-design-principles`
2. `microservices-patterns`
3. `cqrs-implementation`

---

### 6. Data Engineering

**Source:** wshobson/agents (4 skills)

**Coverage:**
- Airflow DAGs
- dbt transformations
- Spark optimization
- Data quality

**Gap:** Missing streaming patterns (Kafka, Flink)

**Priority Imports:**
1. `airflow-dag-patterns`
2. `dbt-transformation-patterns`

---

### 7. Cloud Infrastructure

**Source:** wshobson/agents (6 skills)

**Coverage:**
- Terraform modules
- Multi-cloud architecture
- Cost optimization
- Service mesh (Linkerd, mTLS)

**Priority Imports:**
1. `terraform-module-library`
2. `cost-optimization`
3. `service-mesh-observability`

---

### 8. Kubernetes

**Source:** wshobson/agents (4 skills)

**Coverage:**
- Helm charts
- GitOps
- Security policies
- Manifest generation

**Priority Imports:**
1. `helm-chart-scaffolding`
2. `gitops-workflow`
3. `k8s-security-policies`

---

### 9. CI/CD

**Multiple Sources:**

| Source | Focus |
|--------|-------|
| wshobson/agents | Templates & patterns |
| Local skills | GitHub Actions operations |

**Overlap with Local:**
- `cicd-github-actions-ops` - Already covers review/debugging
- `cicd-github-actions-dev` - Already covers development

wshobson's `github-actions-templates` may add value for:
- Different template patterns
- Cross-platform comparison (GitLab CI)

**Priority Imports:**
1. `gitlab-ci-patterns` (no local equivalent)
2. `deployment-pipeline-design`
3. `secrets-management`

---

### 10. LLM Development

**Source:** wshobson/agents (8 skills)

**Comprehensive Coverage:**
- RAG implementation
- Embeddings & vectors
- Search (similarity, hybrid)
- Prompt engineering
- Evaluation
- LangChain architecture

**Priority Imports:**
1. `rag-implementation`
2. `prompt-engineering-patterns`
3. `llm-evaluation`

---

### 11. Observability

**Source:** wshobson/agents (4 skills)

**Coverage:**
- Prometheus
- Grafana dashboards
- Distributed tracing
- SLO implementation

**Priority Imports:**
1. `prometheus-configuration`
2. `grafana-dashboards`
3. `slo-implementation`

---

### 12. Security

**Multiple Sources:**

| Source | Focus |
|--------|-------|
| wshobson/agents | SAST, threat modeling |
| davila7 | Role-based (senior-security, senior-secops) |
| obra/superpowers | defense-in-depth methodology |

**Priority Imports:**
1. `sast-configuration`
2. `threat-mitigation-mapping`
3. `defense-in-depth` (from methodology)

---

### 13. Language-Specific

#### Python
**Source:** wshobson/agents (5 skills)
- Testing, performance, async, packaging, uv

**Priority:** `uv-package-manager` (modern tooling)

#### JavaScript/TypeScript
**Source:** wshobson/agents (3 skills)
- Advanced types, Node.js backend, testing

**Priority:** `typescript-advanced-types`

#### Rust
**Sources:** hashintel/hash (6), facet-rs/facet (4)
- Error handling, cargo, documentation, profiling, benchmarking

**Priority:** `handling-rust-errors`, `profiling`, `benchmarking`

#### Systems
**Source:** wshobson/agents (2 skills)
- Memory safety, Go concurrency

---

### 14. Database

**Multiple Sources:**

| Source | Skills | Focus |
|--------|--------|-------|
| wshobson/agents | 1 | PostgreSQL |
| davila7 | 1 | Schema design |
| jeremylongshore | 4 | Tooling (diff, index, performance, health) |

**Best Coverage:** jeremylongshore for operational tooling

**Priority Imports:**
1. `database-index-advisor`
2. `query-performance-analyzer`
3. `postgres-schema-design`

---

### 15. N8N Automation

**Source:** czlonkowski/n8n-skills (7 skills)

**Unique Category:** Complete n8n workflow coverage
- Expressions, patterns, validation, configuration
- JavaScript/Python code nodes
- MCP integration

**Recommendation:** Import all if using n8n

---

### 16. Causal Analysis

**Source:** pymc-labs/CausalPy (5 skills)

**Unique Category:** Statistical causal inference
- Dataset loading
- Experiment design
- Placebo analysis
- Marimo notebooks

**Recommendation:** Import for statistical/scientific work

---

### 17. Crash Analysis & Forensics

**Source:** gadievron/raptor (7 skills)

**Unique Categories:**
- **Crash Analysis:** rr debugger, gcov, function tracing
- **OSS Forensics:** GitHub wayback, evidence kit, commit recovery

**Recommendation:** Import for debugging and security research

---

### 18. Development Roles

**Source:** davila7/claude-code-templates (9 skills)

**"Senior" role-based skills:**
- architect, backend, fullstack, devops
- security, secops, qa
- ml-engineer, prompt-engineer

**Assessment:** Role-based prompting. Value depends on use case.

**Priority:** `senior-architect`, `senior-prompt-engineer`

---

### 19. Business & Marketing

**Source:** davila7/claude-code-templates (10 skills)

**Coverage:**
- Content creation
- Marketing strategy
- Product management
- SEO

**Priority:** `product-manager-toolkit`, `cto-advisor`

---

### 20. Compliance

**Multiple Sources:**

| Source | Focus |
|--------|-------|
| davila7 | GDPR, ISO27001, ISMS, quality |
| wshobson/agents | GDPR data handling, HR contracts |

**Overlap:** GDPR covered by both

**Priority Imports:**
1. `gdpr-dsgvo-expert` (davila7 - more comprehensive)
2. `information-security-manager-iso27001`
3. `isms-audit-expert`

---

### 21. Creative & Design

**Source:** davila7/claude-code-templates (4 skills)

**Coverage:**
- UX research/design
- UI design systems
- Accessibility auditing
- Marketing campaigns

**Priority:** `ux-researcher-designer`, `accessibility-auditor`

---

## Duplicate Detection

### High Overlap (Choose One)

| Category | Skills | Recommendation |
|----------|--------|----------------|
| Skill Creation | anthropics skill-creator, pytorch skill-writer, openai codex skill-creator | Use anthropics (official) |
| Frontend Design | anthropics/skills, anthropics/claude-code, claude-plugins-official | Compare and merge |
| Debugging | obra systematic-debugging, wshobson debugging-strategies | Import both (complementary) |
| GDPR | davila7 gdpr-dsgvo-expert, wshobson gdpr-data-handling | davila7 more comprehensive |

### Complementary (Import Both)

| Topic | Source A | Source B |
|-------|----------|----------|
| Visualization | K-Dense-AI matplotlib/seaborn | davila7 plotly |
| Research | K-Dense-AI market-research | davila7 literature-review |
| Security | wshobson SAST | obra defense-in-depth |

---

## Gap Analysis

### Missing Categories

| Category | Status | Notes |
|----------|--------|-------|
| Mobile Development | Missing | No iOS/Android skills |
| Game Development | Missing | No Unity/Unreal skills |
| IoT/Embedded | Missing | No Arduino/Raspberry Pi |
| Desktop Apps | Missing | No Electron/Tauri skills |
| GraphQL | Partial | Only mentioned in API design |
| WebSockets | Missing | Real-time patterns |
| ML Ops | Partial | Missing MLflow, model serving |

### Underrepresented Areas

| Category | Current | Gap |
|----------|---------|-----|
| Testing | E2E, unit | Integration testing patterns |
| Frontend | Design focus | State management patterns |
| DevOps | CI/CD | Incident response |
| Data | Batch processing | Stream processing |

---

## Import Priority Matrix

### Tier 1: Import Immediately

| Skill | Source | Reason |
|-------|--------|--------|
| mcp-builder | anthropics/skills | MCP development critical |
| systematic-debugging | obra/superpowers | Debugging methodology |
| root-cause-tracing | obra/superpowers | Unique systematic approach |
| context-fundamentals | muratcankoylan | Meta-skill development |
| rag-implementation | wshobson/agents | LLM patterns |
| prometheus-configuration | wshobson/agents | Observability |

### Tier 2: Import Soon

| Skill | Source | Reason |
|-------|--------|--------|
| terraform-module-library | wshobson/agents | IaC patterns |
| helm-chart-scaffolding | wshobson/agents | K8s deployment |
| polars | K-Dense-AI | Modern data analysis |
| handling-rust-errors | hashintel/hash | Rust development |
| uv-package-manager | wshobson/agents | Modern Python tooling |

### Tier 3: Import As Needed

| Category | Skills |
|----------|--------|
| Scientific | qiskit, pymc, literature-review |
| Business | product-manager-toolkit, cto-advisor |
| Compliance | gdpr-dsgvo-expert, iso27001 |
| N8N | Full suite if using n8n |
| Causal | Full suite for statistical work |

---

## Registry Quality Assessment

| Registry | Quality | Maintenance | Recommended |
|----------|---------|-------------|-------------|
| anthropics/* | Excellent | Active | Yes |
| obra/superpowers | Excellent | Active | Yes |
| wshobson/agents | Good | Active | Yes |
| K-Dense-AI | Good | Active | Yes |
| davila7 | Moderate | Active | Selective |
| muratcankoylan | Good | Unknown | Yes |
| jeremylongshore | Good | Unknown | Selective |
| hashintel/hash | Good | Active | Yes (Rust) |
| facet-rs/facet | Good | Active | Yes (Rust) |
| czlonkowski/n8n | Good | Active | Yes (n8n users) |
| pymc-labs | Excellent | Active | Yes (scientific) |
| gadievron/raptor | Good | Unknown | Yes (forensics) |

---

## Phase 4: Additional Registries Discovered

GitHub search uncovered significant additional registries not in the original manifest. Search metrics:
- **SKILL.md files found:** 1,224
- **Repos with claude-code topic:** 274
- **Repos matching "claude skills":** 1,447

### Major Curated Lists (Awesome Lists)

| Registry | Stars | Notes |
|----------|-------|-------|
| ComposioHQ/awesome-claude-skills | 10,823 | Largest curated list |
| travisvn/awesome-claude-skills | 3,695 | Well-maintained |
| BehiSecc/awesome-claude-skills | 3,312 | Security focus |
| VoltAgent/awesome-claude-skills | 1,618 | Agent-focused |
| mrgoonie/claudekit-skills | 988 | Toolkit approach |
| simonw/claude-skills | 895 | /mnt/skills contents |

**Recommendation:** Cross-reference these curated lists to identify high-quality skills not yet cataloged.

### Gap-Filling Discoveries

Skills that address gaps identified in the Gap Analysis:

| Gap | Registry | Stars | Notes |
|-----|----------|-------|-------|
| IoT/Embedded | BrownFineSecurity/iothackbot | 450 | IoT pentesting skills |
| Game Dev | *(none found)* | - | Gap remains |
| Mobile Dev | *(none found)* | - | Gap remains |
| Desktop Apps | *(none found)* | - | Gap remains |

### Specialized Skills

| Registry | Stars | Focus |
|----------|-------|-------|
| SawyerHood/dev-browser | 1,487 | Browser automation |
| lackeyjb/playwright-skill | 1,015 | Playwright E2E testing |
| zechenzhangAGI/AI-research-SKILLs | 417 | AI research workflows |
| maxim-ist/elixir-architect | 73 | Elixir development |
| cameronfreer/lean4-skills | 58 | Theorem proving (Lean4) |

### New Language Coverage

| Language | Registry | Notes |
|----------|----------|-------|
| Elixir | maxim-ist/elixir-architect | Fills language gap |
| Lean4 | cameronfreer/lean4-skills | Formal verification |

### Registry Assessment Update

| Registry | Quality | Stars | Recommended |
|----------|---------|-------|-------------|
| ComposioHQ/awesome-claude-skills | High | 10,823 | Yes (meta-registry) |
| SawyerHood/dev-browser | Good | 1,487 | Yes (browser automation) |
| lackeyjb/playwright-skill | Good | 1,015 | Yes (testing) |
| BrownFineSecurity/iothackbot | Good | 450 | Yes (fills IoT gap) |
| zechenzhangAGI/AI-research-SKILLs | Good | 417 | Yes (AI research) |

---

## Next Steps

1. ~~**Phase 4:** Search for additional registries covering gaps~~ ✓ Complete
2. **Import from curated lists:** Parse awesome-claude-skills repos for additional skills
3. **Create import automation:** Justfile recipes for skill import
4. **Version tracking:** Extend .anthropic-version pattern to other sources
5. **Quality validation:** Script to verify SKILL.md format compliance
6. **Deduplication:** Create merged skills for overlapping areas
7. **Address remaining gaps:** Mobile, Game Dev, Desktop Apps still missing
