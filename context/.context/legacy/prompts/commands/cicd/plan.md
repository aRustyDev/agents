---
name: cicd-plan
description: Create detailed CI/CD implementation plan based on patterns and requirements
author: Claude
version: 1.0.0
---

# Command: /cicd plan

Create a detailed implementation plan for CI/CD based on selected patterns and project requirements.

## Usage
```
/cicd plan <pattern> [options]
```

## Patterns
- `basic` - Simple build-test-deploy pipeline
- `gitops` - GitOps-based deployment
- `microservices` - Multi-service architecture
- `monorepo` - Monorepo with multiple projects
- `progressive` - Progressive delivery (canary/blue-green)
- `serverless` - Serverless application deployment
- `ml` - Machine learning pipeline

## Options
- `--platform` - Target platform (github/gitlab)
- `--cloud` - Cloud provider (aws/azure/gcp)
- `--complexity` - Override detected complexity
- `--timeline` - Implementation timeline (days)
- `--team-size` - Team size for capacity planning

## Workflow

### Phase 1: Context Loading
1. **Load Context from CICDController**
   - Retrieve assessment results
   - Load detected configuration
   - Apply pattern selection

2. **Pattern Validation**
   - Verify pattern compatibility
   - Check prerequisites
   - Identify dependencies

### Phase 2: Requirements Gathering
3. **Technical Requirements**
   - Build requirements
   - Test strategies
   - Deployment targets
   - Integration needs

4. **Operational Requirements**
   - Team structure
   - Approval processes
   - Compliance needs
   - SLA requirements

### Phase 3: Plan Generation
5. **Create Implementation Phases**
   - Foundation setup
   - Core pipeline implementation
   - Integration configuration
   - Testing and validation
   - Rollout strategy

6. **Generate Configurations**
   - Pipeline definitions
   - Infrastructure as Code
   - Security policies
   - Monitoring setup

### Phase 4: Risk Assessment
7. **Identify Risks**
   - Technical risks
   - Operational risks
   - Timeline risks
   - Resource risks

8. **Mitigation Strategies**
   - Risk prevention
   - Contingency plans
   - Rollback procedures

### Phase 5: Documentation
9. **Generate Plan Document**
   - Use template: CICD_PLAN.md
   - Include all configurations
   - Add visual diagrams
   - Create task breakdown

## Plan Components

### 1. Architecture Design
```yaml
# Example GitOps Architecture
components:
  source_control:
    - Application repository
    - Configuration repository
    - Secrets repository
  
  ci_pipeline:
    - Build stage
    - Test stage
    - Security scan
    - Container build
    - Registry push
  
  cd_pipeline:
    - GitOps operator
    - Sync mechanism
    - Rollback capability
    - Multi-environment
```

### 2. Implementation Timeline
```
Week 1-2: Foundation
- Set up repositories
- Configure CI/CD platform
- Establish conventions

Week 3-4: Core Pipeline
- Implement build process
- Add testing stages
- Configure artifacts

Week 5-6: Deployment
- Set up environments
- Implement deployment
- Add monitoring

Week 7-8: Optimization
- Performance tuning
- Security hardening
- Documentation
```

### 3. Task Breakdown
```markdown
## Foundation Tasks
- [ ] Create CI/CD repository structure
- [ ] Set up service accounts and permissions
- [ ] Configure secrets management
- [ ] Install required tools and operators

## Pipeline Tasks
- [ ] Create pipeline configuration
- [ ] Implement build stages
- [ ] Add test automation
- [ ] Configure quality gates
```

## Example Usage

### GitOps Plan for Kubernetes
```
/cicd plan gitops --platform github --cloud aws
```

### Microservices Plan
```
/cicd plan microservices --complexity complex --team-size 10
```

### Quick Basic Pipeline
```
/cicd plan basic --timeline 7
```

## Plan Customization

### Pattern Combinations
Plans can combine multiple patterns:
```
/cicd plan gitops+progressive --platform gitlab
```

### Custom Requirements
Include specific requirements:
```
/cicd plan monorepo --requirements "compliance=sox,regions=multi"
```

## Deliverables

### 1. Implementation Plan Document
- Executive summary
- Technical architecture
- Step-by-step guide
- Timeline and milestones

### 2. Configuration Files
- Pipeline definitions
- IaC templates
- Policy configurations
- Example implementations

### 3. Validation Criteria
- Success metrics
- Test scenarios
- Acceptance criteria
- Performance baselines

### 4. Training Materials
- Team onboarding guide
- Troubleshooting guide
- Best practices document
- Runbook templates

## Success Metrics

### Implementation KPIs
- **Setup Time**: Target vs actual
- **Pipeline Success Rate**: >95%
- **Deployment Frequency**: Improvement %
- **Lead Time**: Reduction target
- **Quality Metrics**: Test coverage, security score

### Adoption Metrics
- Team onboarding time
- Self-service capability
- Incident reduction
- Developer satisfaction

## Next Steps

After planning:
1. Review plan with stakeholders
2. Get approval for implementation
3. Use `/cicd implement` to execute
4. Monitor with `/cicd monitor`