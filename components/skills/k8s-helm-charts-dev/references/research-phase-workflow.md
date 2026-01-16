# Research Phase Workflow

Structured approach for investigating an application before creating its Helm chart.

---

## Overview

```
Initial Research → Create Plan → Review+Refine → Approve → Implement → Document
```

Use this workflow for:
- Complex/Operator charts
- Extending existing charts
- Applications with unclear documentation
- Multi-service dependencies

Skip to **Fast Path** for Simple/Standard charts with clear requirements.

---

## Step 1: Initial Research (5-10 minutes)

Quick exploration to understand scope and complexity.

### Goals

- Determine if official chart exists
- Assess chart complexity
- Identify obvious blockers

### Actions

```bash
# Check for existing charts
gh search repos "<project> helm" --owner <org>
curl -s "https://artifacthub.io/api/v1/packages/search?ts_query_web=<project>&kind=0" | jq '.packages[].name'

# Quick documentation scan
# Try: /docs/deployment, /docs/docker, /docs/kubernetes
```

### Outputs

- Chart exists? (Yes/No/Abandoned)
- Complexity estimate (Simple/Standard/Complex/Operator)
- Key documentation URLs
- Initial blockers or concerns

### Decision Point

| Finding | Action |
|---------|--------|
| Simple chart, clear docs | **Fast Path** - Skip to implementation |
| Official chart exists | See `extend-contribute-strategy.md` |
| Complex/unclear | **Continue** to Step 2 |

---

## Step 2: Create Research Plan

Structure your investigation before diving in.

### Research Plan Template

```markdown
## Research Plan: <Application> Helm Chart

### Objectives
- [ ] Identify container image and configuration
- [ ] Document all required ports
- [ ] Find health check endpoints
- [ ] Determine resource requirements
- [ ] List external dependencies

### Information Needed
- [ ] Docker image (registry, repository, tag pattern)
- [ ] Exposed ports (main, admin, metrics, debug)
- [ ] Environment variables (required vs optional)
- [ ] Health endpoints (liveness, readiness, startup)
- [ ] Resource recommendations (CPU, memory)
- [ ] External services (database, search, cache, messaging)
- [ ] Persistence requirements (volumes, data directories)
- [ ] Configuration format (env vars, config file, both)

### Sources to Investigate
1. Official documentation: <url>
2. Docker Hub / container registry: <url>
3. GitHub repository: <url>
4. Existing Helm charts: <url>
5. docker-compose examples: <url>

### Fallback Strategies
If primary sources fail:
1. Inspect Dockerfile directly
2. Run container with --help
3. Search GitHub for deployment examples
4. Check community forums/Discord

### Expected Outputs
- Completed research summary (see template)
- Chart complexity classification
- Dependency list
- Blockers/risks identified

### Estimated Time
- Research: <X> minutes
- Documentation: <X> minutes
```

---

## Step 3: Review and Refine

Self-review before seeking approval.

### Review Checklist

- [ ] All information categories addressed
- [ ] Fallback strategies defined for each source
- [ ] Time estimate is realistic
- [ ] No obvious gaps in investigation plan
- [ ] Sources are accessible (not paywalled, not requiring auth)

### Refinement Questions

1. Are there sources I haven't considered?
2. Is the scope appropriate (not too broad, not too narrow)?
3. Have I accounted for documentation failures?
4. What's my exit criteria if I can't find information?

---

## Step 4: Get Approval (Optional Gate)

When to seek user approval:

| Scenario | Approval Recommended |
|----------|---------------------|
| Complex application (3+ dependencies) | Yes |
| Unclear requirements from user | Yes |
| Multiple valid approaches identified | Yes |
| Time estimate > 30 minutes | Yes |
| Simple application, clear path | No - proceed |
| User explicitly said "just do it" | No - proceed |

### Approval Request Format

```markdown
## Research Plan Ready for Review

**Application**: <name>
**Complexity**: <Simple/Standard/Complex/Operator>
**Estimated Time**: <X> minutes

### Key Sources
1. <url1> - for <purpose>
2. <url2> - for <purpose>

### Potential Blockers
- <blocker1>
- <blocker2>

### Questions/Decisions Needed
- <question1>?
- <question2>?

Proceed with research?
```

---

## Step 5: Implement Research Plan

Execute the plan systematically.

### Execution Order

1. **Existing charts first** - Don't reinvent
2. **Official documentation** - Primary source
3. **GitHub repository** - Dockerfile, docker-compose
4. **Container inspection** - Direct evidence
5. **Community examples** - Validation

### During Research

- Take notes in structured format (see template)
- Note confidence level for each finding
- Document source URLs for reference
- Flag contradictions between sources

### If Blocked

| Blocker | Resolution |
|---------|------------|
| Docs require JavaScript | Use GitHub/Docker Hub |
| Paywall/login required | Check for OSS alternative, ask user |
| Conflicting information | Prefer docker-compose > docs |
| No information available | Note as unknown, proceed conservatively |

---

## Step 6: Document Findings

Use the research summary template to capture results.

### Location

Save research summary to:
```
.claude/plans/<chart-name>-chart/research-summary.md
```

### Template Reference

See `assets/templates/research-summary.md` for full template.

### Key Sections

1. **Image Details** - Registry, repository, tag
2. **Ports** - All exposed ports with purpose
3. **Health Endpoints** - Liveness, readiness, startup
4. **Environment Variables** - Required vs optional
5. **Dependencies** - External services needed
6. **Resources** - CPU/memory recommendations
7. **Confidence Levels** - What's certain vs assumed
8. **Open Questions** - What still needs clarification

---

## Fast Path (Simple Charts)

For Simple/Standard charts with clear documentation:

1. **Quick Research** (5 min)
   - Find container image
   - Note main port
   - Check for obvious dependencies

2. **Create Directly**
   - Use chart templates from skill
   - Apply values from quick research

3. **Validate and PR**
   - helm lint + template
   - Create PR with findings in description

Skip: Research plan, approval gate, detailed documentation

---

## Related References

- `research-strategy.md` - Finding existing charts, gathering details
- `planning-phase-workflow.md` - Next phase after research
- `assets/templates/research-summary.md` - Documentation template
