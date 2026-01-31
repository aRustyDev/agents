# Skill Templates

Templates for creating new Claude Code skills following the naming convention and structure standards.

## Naming Convention

```
<category>-[<subcategory>-]<tool>-<focus>
```

### Focus Codes

| Focus | Code | Description | Audience |
|-------|------|-------------|----------|
| Operations | `ops` | Day-to-day operations, troubleshooting | SRE, Platform Engineers |
| Development | `dev` | Building, coding, implementing | Developers |
| Engineering | `eng` | Architecture, design patterns | Senior Engineers, Architects |
| Newcomer | `nub` | Learning-focused, onboarding | Beginners |
| Executive | `xec` | Strategy, high-level overview | Managers, CTOs |

### Categories

| Code | Category | Subcategories |
|------|----------|---------------|
| `ai` | AI/ML | train, infer, eval, finetune |
| `backend` | Backend | api, graphql, grpc, websocket |
| `cicd` | CI/CD | github, gitlab, jenkins, argocd |
| `cloud` | Cloud | aws, gcp, azure, cloudflare |
| `data` | Data | ingest, transform, quality, stream |
| `db` | Database | postgres, mongodb, redis, vector |
| `frontend` | Frontend | react, vue, svelte, css |
| `k8s` | Kubernetes | helm, gitops, security, networking |
| `lang` | Language | rust, python, go, typescript |
| `llm` | LLM | rag, prompts, agents, eval |
| `meta` | Meta | skills, plugins, mcp, hooks |
| `method` | Methodology | debugging, tdd, planning, review |
| `observability` | Observability | metrics, tracing, logging, alerts |
| `sci` | Scientific | stats, bio, quantum, viz |
| `security` | Security | scan, pentest, compliance, secrets |
| `workflow` | Workflow | n8n, temporal, airflow, make |

## Usage

```bash
# Create new skill from template
just create-skill <category>-<tool>-<focus>

# Examples
just create-skill lang-rust-cargo-dev
just create-skill cloud-aws-terraform-eng
just create-skill observability-metrics-prometheus-ops
```

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{SKILL_NAME}}` | Full skill name | `lang-rust-cargo-dev` |
| `{{CATEGORY}}` | Primary category | `lang` |
| `{{SUBCATEGORY}}` | Optional subcategory | `rust` |
| `{{TOOL}}` | Tool/technology | `cargo` |
| `{{FOCUS}}` | Focus level | `dev` |
| `{{TITLE}}` | Human-readable title | `Rust Cargo Development` |
| `{{SOURCE_REPO}}` | If imported, source repo | `hashintel/hash` |

## Directory Structure

```
<skill-name>/
├── SKILL.md              # Required: Main skill file
└── references/           # Optional: Reference materials
    ├── <topic>.md        # Topic-specific references
    └── <subtopic>/       # Nested for complex domains
        └── *.md
```

## Validation

```bash
# Validate skill structure and naming
just validate-skill components/skills/<skill-name>
```
