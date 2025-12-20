---
name: Feature Development Workflow
module_type: workflow
scope: context
priority: high
triggers: ["new feature", "implement", "add functionality", "create component", "feature request"]
dependencies: 
  - "processes/version-control/workspace-setup.md"
  - "processes/code-review/codebase-analysis.md"
  - "processes/issue-tracking/feature-planning.md"
  - "patterns/development/tdd-pattern.md"
  - "processes/testing/tdd.md"
  - "processes/code-review/quality-review.md"
  - "processes/version-control/workspace-cleanup.md"
  - "processes/version-control/submit-work.md"
conflicts: []
version: 1.0.0
---

# Feature Development Workflow

## Purpose
Orchestrate the complete process of implementing a new feature from initial request through deployment-ready code. This workflow ensures consistent, high-quality feature development following established patterns.

## Trigger
- New feature request from user
- Feature ticket assigned
- Enhancement to existing functionality
- User story created

## Pattern
Uses `${active_pattern}` from configuration (default: TestDrivenDevelopment)

## Workflow Steps

### 1. Process: WorkspaceSetup
**Purpose**: Initialize clean, tracked workspace

**Actions**:
- Verify repository context
- Create feature branch: `feature/${issue_number}-${brief_description}`
- Check pre-commit configuration
- Initialize issue tracking
- Push branch to remote

**Output**: Clean workspace on dedicated branch

### 2. Process: CodebaseReview (Feature Focus)
**Purpose**: Understand existing code and patterns

**Focus Areas**:
- Architecture patterns (DETAILED)
- Code conventions (DETAILED)
- Similar features (CRITICAL)
- Integration points

**Output**: Review summary with implementation insights

### 3. Process: FeaturePlanning
**Purpose**: Create detailed implementation plan

**Actions**:
- State understanding of requirements
- Identify ambiguities and ask questions
- Design technical approach
- Break down into atomic tasks
- Define test scenarios
- Assess risks and dependencies

**Decision Point**:
```
Should this be tracked as a Project or Milestone?
├─ Multi-week effort → Create GitHub Project
├─ Multiple subtasks → Create Milestone
└─ Single issue scope → Track in issue only
```

**Output**: Approved implementation plan with task breakdown

### 4. Process: DevelopmentExecution → ${active_pattern}
**Purpose**: Implement feature using chosen pattern

**Default**: TestDrivenDevelopment
- Red-green-refactor cycles
- Atomic commits after each cycle
- Continuous pushing to remote
- Issue updates after each cycle

**Alternative Patterns** (if overridden):
- CoverageDrivenDevelopment
- BehaviorDrivenDevelopment

**Implementation Loop**:
```
WHILE tasks_remaining:
    - Select next atomic task
    - Execute development pattern
    - Commit and push changes
    - Update issue tracking
    - Monitor CI/CD status
```

### 5. Process: CodeQualityReview
**Purpose**: Ensure code meets standards

**Checks**:
- Automated (linting, formatting, types)
- Pattern compliance
- Security review
- Performance assessment
- Documentation completeness

**Output**: Quality checklist and improvements

### 6. Process: WorkspaceCleanup
**Purpose**: Prepare for merge

**Actions**:
- Ensure all work committed and pushed
- Update documentation if needed
- Final issue update with summary
- Self-review all changes

**Output**: Clean, documented branch ready for review

### 7. Process: SubmitWork
**Purpose**: Create pull request for review

**Actions**:
- Create PR with template
- Link to issue(s)
- Add reviewers
- Monitor CI/CD
- Respond to feedback

**Output**: Pull request ready for team review

## Decision Points

### 1. Complexity Assessment (Step 3)
```
Feature Complexity Assessment:
├─ Effort > 1 week → Create GitHub Project
├─ Subtasks > 10 → Create Milestone
├─ Subtasks 5-10 → Consider Milestone
└─ Subtasks < 5 → Use issue tracking only
```

### 2. Pattern Override (Step 4)
```
Development Pattern Selection:
├─ Exploration needed → Consider CDD
├─ Behavior specs exist → Consider BDD
├─ Complex behaviors → Consider BDD
└─ Default → Continue with TDD
```

### 3. Risk Mitigation (Step 3)
```
Risk Assessment:
├─ High security risk → Add security review
├─ Performance critical → Add benchmarks
├─ Breaking changes → Add migration plan
└─ Low risk → Standard process
```

## Integration Points

### Required Processes
1. WorkspaceSetup (initialization)
2. CodebaseReview (analysis)
3. FeaturePlanning (planning)
4. DevelopmentExecution (implementation)
5. CodeQualityReview (quality)
6. WorkspaceCleanup (finalization)
7. SubmitWork (submission)

### Optional Processes
- RiskMitigation (if high risks)
- PerformanceOptimization (if needed)
- SecurityAudit (if sensitive)
- SpikeResearch (if unknowns)

### May Trigger
- Workflow: BugFix (if bugs found)
- Workflow: Refactoring (if debt identified)
- Process: ArchitectureReview (if structural changes)

## Success Criteria
- [ ] All requirements implemented
- [ ] Comprehensive test coverage
- [ ] No regression in existing features
- [ ] Documentation updated
- [ ] Code review approved
- [ ] CI/CD passing
- [ ] Stakeholder acceptance

## Time Estimates
- **Small Feature** (1-2 days): Standard workflow
- **Medium Feature** (3-5 days): Workflow + milestone
- **Large Feature** (1-2 weeks): Workflow + project
- **Epic Feature** (2+ weeks): Phased approach

## Workflow Variations

### Spike/Prototype Variation
For exploratory features:
1. Abbreviated planning
2. Use CDD for learning
3. Focus on key unknowns
4. Document findings
5. Plan real implementation

### Emergency Feature Variation
For urgent features:
1. Minimal codebase review
2. Focus on critical path
3. Accept technical debt
4. Extensive post-review
5. Schedule follow-up

### Large Feature Variation
For multi-week features:
1. Extended planning phase
2. Create GitHub Project
3. Weekly stakeholder syncs
4. Phased implementation
5. Incremental releases

## Common Pitfalls

### Planning Phase
- ❌ Analysis paralysis
- ❌ Skipping codebase review
- ❌ Vague task breakdown
- ✅ Timebox planning (2-4 hours max)

### Development Phase
- ❌ Feature creep
- ❌ Skipping tests
- ❌ Large commits
- ✅ Stay focused on plan

### Submission Phase
- ❌ Rushed PR description
- ❌ Missing issue links
- ❌ Ignored CI failures
- ✅ Thorough self-review

## Best Practices

### Communication
- ✅ Daily progress updates
- ✅ Ask questions early
- ✅ Document decisions
- ✅ Share blockers immediately

### Technical Excellence
- ✅ Follow existing patterns
- ✅ Write tests first
- ✅ Keep changes focused
- ✅ Refactor continuously

### Process Discipline
- ✅ Update issues regularly
- ✅ Commit atomically
- ✅ Push frequently
- ✅ Review own work

## Example Execution

```
User: "Add export functionality for user data"

1. WorkspaceSetup
   ✓ Branch: feature/456-user-export
   ✓ Issue #456 created

2. CodebaseReview
   ✓ Found existing CSV export in reports module
   ✓ Identified user data access patterns
   ✓ Located similar batch operations

3. FeaturePlanning
   ✓ 8 tasks identified → Creating milestone
   ✓ Reusing CSV service
   ✓ Adding progress tracking
   ✓ Plan approved

4. Development (TDD)
   ✓ Task 1: User data collector service
   ✓ Task 2: Export format handlers
   → Task 3: Progress tracking (current)
   ⏳ Tasks 4-8: Pending

5. Progress: 25% complete, all tests passing
```

## Troubleshooting

### Blocked on Requirements
1. Document specific questions
2. Create spike task if needed
3. Make documented assumptions
4. Get stakeholder clarification

### Technical Challenges
1. Research similar solutions
2. Consult team/documentation
3. Consider alternatives
4. Document decision rationale

### Time Pressure
1. Identify MVP scope
2. Negotiate requirements
3. Plan phased delivery
4. Track technical debt

---
*This workflow ensures features are developed systematically with quality, tracking, and clear communication throughout.*