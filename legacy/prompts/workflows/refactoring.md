---
name: Refactoring Workflow
module_type: workflow
scope: context
priority: medium
triggers: ["refactor", "improve code", "technical debt", "code smell", "cleanup", "restructure", "optimize code"]
dependencies: ["processes/version-control/workspace-setup.md", "processes/code-review/codebase-analysis.md", "processes/testing/safety-net-creation.md", "patterns/development/tdd-pattern.md", "processes/version-control/commit-standards.md"]
conflicts: []
version: 1.0.0
---

# Refactoring Workflow

## Purpose
Improve code structure, readability, and maintainability without changing external behavior. This workflow ensures safe, incremental improvements while maintaining system stability.

## Trigger
- Code smell identified
- Performance bottleneck found
- Maintenance difficulty reported
- Technical debt sprint
- Pre-feature cleanup needed

## Workflow Steps

### 1. Process: WorkspaceSetup
**Purpose**: Create dedicated refactoring environment
**Focus**: Clean workspace for structural changes
**Output**: Working branch for refactoring

**Customization**:
- Branch naming: `refactor/${scope}-${description}`
- Always branch from develop/main
- Consider feature flags for large refactors

### 2. Process: RefactoringScopeAnalysis
**Purpose**: Define clear boundaries for refactoring
**Focus**: What to change and what to preserve

**Steps**:
1. **Identify refactoring targets**
   - Specific files/modules
   - Code patterns to address
   - Performance bottlenecks
   - Maintenance pain points

2. **Define success criteria**
   - Measurable improvements
   - Code quality metrics
   - Performance targets
   - Maintainability goals

3. **Assess risk and impact**
   ```
   What systems depend on this code?
   ├─ Internal only → Lower risk
   ├─ Public API → Need compatibility
   ├─ Critical path → Extra caution
   └─ Legacy integration → Document thoroughly
   ```

4. **Set boundaries**
   - What's in scope
   - What's explicitly out
   - Migration strategy if needed
   - Rollback plan

### 3. Process: SafetyNetCreation
**Purpose**: Establish comprehensive test coverage before changes
**Focus**: Behavioral verification

**Actions**:
1. **Measure current coverage**
   ```bash
   # Run coverage analysis
   coverage run -m pytest
   coverage report --include="${target_files}"
   ```

2. **Add characterization tests**
   - Test current behavior exactly
   - Cover edge cases
   - Document assumptions
   - Include integration tests

3. **Performance baselines**
   - Benchmark current performance
   - Set acceptable thresholds
   - Create performance tests

4. **Create snapshot tests**
   - API response snapshots
   - Database state captures
   - Output comparisons

**Critical**: No refactoring until safety net is complete

### 4. Decision Point: Coverage Adequacy
```
Is test coverage sufficient?
├─ > 90% with edge cases → Proceed
├─ 70-90% → Add critical path tests
├─ < 70% → Expand safety net
└─ Untestable code → Refactor for testability first
```

### 5. Process: RefactorPlanning
**Purpose**: Design the refactoring approach
**Focus**: Incremental, safe transformations

**Strategies**:
1. **Identify refactoring patterns**
   - Extract method/class
   - Inline variable/method
   - Replace conditionals
   - Introduce parameter object
   - Replace inheritance with composition

2. **Order transformations**
   - Start with lowest risk
   - Build on each success
   - Keep commits atomic
   - Maintain green tests

3. **Plan checkpoints**
   - After each major step
   - Performance validation
   - Integration verification
   - Rollback points

### 6. Process: IncrementalRefactoring
**Purpose**: Execute refactoring in small, safe steps
**Focus**: Continuous validation

**For each refactoring step**:
1. **Make single change**
   ```
   Refactoring type:
   ├─ Extract → Create new, redirect, remove old
   ├─ Inline → Copy logic, replace calls, remove
   ├─ Rename → Update all references atomically
   └─ Restructure → Move incrementally
   ```

2. **Validate immediately**
   - Run all tests
   - Check performance
   - Verify behavior unchanged
   - Lint and format

3. **Commit atomically**
   ```
   refactor(${scope}): ${specific_change}
   
   - Extract ${method} from ${class}
   - No behavioral changes
   - All tests passing
   ```

### 7. Decision Point: Behavior Preserved
```
Do all tests still pass?
├─ Yes → Continue to next step
├─ No, expected → Fix and retest
├─ No, unexpected → Revert and investigate
└─ Performance degraded → Optimize or revert
```

### 8. Process: RefactorValidation
**Purpose**: Ensure refactoring achieved goals
**Focus**: Measurable improvements

**Validations**:
1. **Code quality metrics**
   - Cyclomatic complexity
   - Code duplication
   - Coupling metrics
   - Cohesion measures

2. **Performance comparison**
   - Benchmark against baseline
   - Memory usage
   - Response times
   - Resource utilization

3. **Maintainability assessment**
   - Easier to understand?
   - Simpler to modify?
   - Better testability?
   - Clearer structure?

### 9. Process: DocumentationUpdate
**Purpose**: Reflect structural changes in docs
**Focus**: Architecture and design docs

**Updates needed**:
- Architecture diagrams
- API documentation
- Design decisions
- Migration guides
- Code comments

### 10. Process: TeamKnowledgeTransfer
**Purpose**: Share refactoring learnings
**Focus**: Team improvement

**Activities**:
1. **Document patterns found**
   - What was problematic
   - Why it occurred
   - How to prevent

2. **Share techniques used**
   - Effective refactorings
   - Testing strategies
   - Tools that helped

3. **Update team standards**
   - New patterns to follow
   - Anti-patterns to avoid
   - Tooling improvements

### 11. Process: WorkspaceCleanup
**Purpose**: Prepare for integration
**Focus**: Clean history and documentation
**Output**: Ready for review

### 12. Process: SubmitWork
**Purpose**: Present refactoring for review
**Focus**: Clear value communication

**PR Template**:
```markdown
## Refactoring: ${description}

### Motivation
${why_refactoring_needed}

### Approach
${refactoring_strategy_used}

### Changes Made
- ${structural_change_1}
- ${structural_change_2}

### Improvements
- **Complexity**: ${before} → ${after}
- **Performance**: ${metrics}
- **Maintainability**: ${specific_improvements}

### Testing
- [ ] All existing tests pass
- [ ] New tests added for coverage
- [ ] Performance benchmarks verified
- [ ] No behavior changes confirmed

### Review Notes
- Pay attention to: ${specific_areas}
- Validates approach for: ${future_refactorings}
```

## Success Criteria
- [ ] All tests remain green
- [ ] Performance maintained or improved
- [ ] Code metrics improved
- [ ] No functional changes
- [ ] Team understands changes

## Integration Points
### Required Processes
- SafetyNetCreation (test coverage)
- CodebaseAnalysis (understanding)
- CommitStandards (clear history)
- CodeQualityReview (validation)

### Optional Processes
- PerformanceProfiling (for optimization)
- ArchitectureReview (for large changes)
- SecurityAudit (if touching sensitive code)

### May Trigger
- Documentation updates
- Team training sessions
- Tooling improvements
- Further refactorings

## Variations

### Performance Refactoring
When optimizing for speed:
1. Profile first
2. Identify bottlenecks
3. Benchmark baseline
4. Apply optimizations
5. Verify improvements

### Testability Refactoring
When improving test coverage:
1. Identify untestable code
2. Extract dependencies
3. Introduce interfaces
4. Add test seams
5. Write comprehensive tests

### API Compatibility Refactoring
When maintaining public interfaces:
1. Create adapter layer
2. Deprecate old interface
3. Refactor implementation
4. Maintain both temporarily
5. Remove after grace period

## Anti-Patterns

### Big Bang Refactoring
❌ Rewrite everything at once
✅ Small, incremental changes

### Refactoring Without Tests
❌ "I'll be careful"
✅ Comprehensive safety net first

### Feature Creep
❌ Add new features while refactoring
✅ Separate refactoring from features

### Perfectionism
❌ Make it perfect in one go
✅ Iterative improvements

## Best Practices

### DO
- ✅ One refactoring at a time
- ✅ Keep tests green always
- ✅ Commit frequently
- ✅ Measure improvements
- ✅ Share learnings

### DON'T
- ❌ Change behavior
- ❌ Skip tests
- ❌ Refactor without purpose
- ❌ Mix with features
- ❌ Ignore performance

## Metrics
- Code coverage before/after
- Complexity reduction
- Performance impact
- Time to implement changes
- Defect rate post-refactor

---
*Refactoring is about making the code better for developers while keeping it exactly the same for users.*