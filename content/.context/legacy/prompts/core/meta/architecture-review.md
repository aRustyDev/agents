---
module: ArchitectureReview
scope: context
triggers: ["review architecture", "system health", "module audit", "check system"]
conflicts: []
dependencies: ["module-validation", "module-creation-guide"]
priority: high
---

# Architecture Review Process

## Purpose
Perform comprehensive analysis of the entire modular system to ensure coherence, identify inefficiencies, and maintain system health as it grows and evolves.

## Review Triggers
Conduct architecture review when:
- Adding significant new functionality
- Quarterly as preventive maintenance
- Performance degradation is noticed
- Module conflicts increase
- System becomes difficult to understand
- Before major refactoring efforts

## Review Dimensions

### 1. System Coherence
How well do all modules work together as a unified system?

### 2. Complexity Management
Is the system becoming too complex or maintaining appropriate simplicity?

### 3. Performance Efficiency
Are modules loading/unloading efficiently? Is memory usage optimized?

### 4. Maintainability
Can new modules be easily added? Are existing modules easy to update?

### 5. User Experience
Is the system intuitive to use? Are the right modules loading at the right times?

## Architecture Review Process

### Phase 1: System Inventory
```
1.1 Catalog all modules:
    - Count modules by type
    - Map directory structure
    - List all unique triggers
    - Document scope distribution

1.2 Analyze module statistics:
    - Average module size
    - Dependency depth
    - Conflict frequency
    - Trigger overlap

1.3 Create system snapshot:
    - Total modules: X
    - Total triggers: Y
    - Dependency chains: Z
    - Known conflicts: N
```

### Phase 2: Structural Analysis
```
2.1 Dependency analysis:
    - Create dependency graph
    - Identify dependency clusters
    - Find circular dependencies
    - Assess coupling levels

2.2 Scope distribution:
    - Count modules per scope
    - Verify scope appropriateness
    - Check scope rule violations
    - Identify scope migration needs

2.3 Trigger analysis:
    - Find overlapping triggers
    - Identify trigger gaps
    - Assess trigger specificity
    - Check trigger effectiveness

2.4 Conflict mapping:
    - Document all conflicts
    - Verify conflict necessity
    - Find hidden conflicts
    - Assess conflict resolution
```

### Phase 3: Behavioral Analysis
```
3.1 Loading patterns:
    - Track common load sequences
    - Identify rarely loaded modules
    - Find always-loaded context modules
    - Measure load/unload frequency

3.2 Usage patterns:
    - Which modules used together
    - Common workflow paths
    - Unused module detection
    - Over-specified modules

3.3 Performance metrics:
    - Module load times
    - Memory usage per module
    - Context switch overhead
    - System responsiveness

3.4 Error patterns:
    - Failed module loads
    - Unhandled edge cases
    - Recovery failures
    - User confusion points
```

### Phase 4: Content Quality Review
```
4.1 Documentation completeness:
    - All modules have clear purpose
    - Examples are practical
    - Steps are actionable
    - References are valid

4.2 Consistency check:
    - Naming conventions followed
    - Formatting standardized
    - Cross-references uniform
    - Terminology consistent

4.3 Coverage analysis:
    - Identify functionality gaps
    - Find redundant modules
    - Assess feature completeness
    - Check edge case handling

4.4 Maintenance burden:
    - Complex modules identified
    - Update frequency tracked
    - Technical debt assessed
    - Refactoring needs listed
```

### Phase 5: System Health Assessment
```
5.1 Calculate health metrics:
    - Module cohesion score
    - System coupling index
    - Complexity rating
    - Maintainability score

5.2 Identify problem areas:
    - Bottleneck modules
    - Fragile connections
    - Over-engineered sections
    - Under-specified areas

5.3 Assess evolution readiness:
    - Extensibility rating
    - Modification difficulty
    - New developer onboarding
    - System documentation

5.4 Risk evaluation:
    - Single points of failure
    - Critical dependencies
    - Security concerns
    - Performance limits
```

## Review Artifacts

### Architecture Report Template
```markdown
# Modular System Architecture Review
Date: [timestamp]
Reviewer: [name/role]

## Executive Summary
- Overall Health: [Good|Fair|Needs Attention]
- Key Findings: [2-3 major discoveries]
- Recommended Actions: [Priority changes]

## System Overview
### Metrics
- Total Modules: X
- Active Dependencies: Y
- Known Conflicts: Z
- Average Module Size: N lines

### Module Distribution
| Type | Count | Percentage |
|------|-------|------------|
| Processes | X | Y% |
| Workflows | X | Y% |
| Patterns | X | Y% |
| Guides | X | Y% |

## Health Indicators
### Strengths
1. [What's working well]
2. [Positive patterns observed]

### Concerns
1. [Issue]: [Impact] - [Recommendation]
2. [Issue]: [Impact] - [Recommendation]

## Dependency Analysis
[Visualization or description of dependency graph]

### Critical Paths
- [Most important dependency chains]

### Circular Dependencies
- [Any found, with resolution plan]

## Performance Analysis
- Average Load Time: Xms
- Memory Footprint: YMB
- Context Switch Time: Zms

## Recommendations
### Immediate Actions
1. [High-priority fixes]

### Short-term Improvements
1. [1-month timeline items]

### Long-term Evolution
1. [Architectural changes needed]

## Module-Specific Issues
[Detailed findings per module]
```

### Dependency Visualization
Create a visual map showing:
- Module relationships
- Dependency direction
- Conflict zones
- Isolated modules

### Complexity Heatmap
Identify areas of high complexity:
- Deep dependency chains
- High trigger density
- Frequent conflicts
- Large modules

## Review Findings Patterns

### Common Anti-patterns to Identify

#### 1. The God Module
A module that does too much and everything depends on it.
- **Signs**: Many dependencies, large size, mixed responsibilities
- **Fix**: Split into focused modules

#### 2. Circular Dependency Web
Modules that all depend on each other in a cycle.
- **Signs**: A→B→C→A dependency pattern
- **Fix**: Extract shared functionality

#### 3. Trigger Overlap Confusion
Multiple modules responding to similar triggers.
- **Signs**: User says "test" and 5 modules load
- **Fix**: More specific triggers or consolidated modules

#### 4. Scope Creep
Temporary modules being used as persistent.
- **Signs**: Tool guides always loaded
- **Fix**: Correct scope assignment

#### 5. Documentation Drift
Module behavior doesn't match documentation.
- **Signs**: Users confused, features don't work as described
- **Fix**: Regular documentation updates

## Improvement Strategies

### Refactoring Priorities
Based on review findings, prioritize:

1. **Break up large modules**
   - If module > 500 lines
   - If module has > 5 responsibilities
   - If module is hard to understand

2. **Consolidate related modules**
   - If triggers overlap significantly
   - If modules always load together
   - If separation adds no value

3. **Clarify module boundaries**
   - If responsibilities unclear
   - If modules duplicate functionality
   - If users load wrong modules

4. **Optimize loading patterns**
   - If modules load unnecessarily
   - If context switches are slow
   - If memory usage is high

### System Evolution Planning

#### Short-term (1 month)
- Fix critical bugs and conflicts
- Update outdated documentation
- Resolve circular dependencies

#### Medium-term (3 months)
- Refactor problem modules
- Implement performance improvements
- Add missing functionality

#### Long-term (6+ months)
- Architectural improvements
- New module categories
- Advanced features

## Review Automation

### Automated Checks
Create scripts to regularly check:
```bash
# Module count growth
!count-modules --trend

# Dependency complexity
!analyze-dependencies --depth

# Trigger overlap
!check-triggers --conflicts

# Performance metrics
!measure-performance --modules
```

### Health Dashboard
Track key metrics over time:
- Module count trends
- Dependency depth average
- Conflict frequency
- Load time patterns

### Alert Thresholds
Set alerts when:
- Circular dependencies detected
- Module size exceeds limit
- Load time degrades
- Conflicts increase

## Best Practices for Ongoing Health

### Regular Maintenance
- Weekly: Quick validation of new modules
- Monthly: Check for unused modules
- Quarterly: Full architecture review
- Yearly: Major refactoring planning

### Documentation Hygiene
- Update module docs with behavior
- Keep examples current
- Remove deprecated content
- Add lessons learned

### Performance Monitoring
- Track module load times
- Monitor memory usage
- Measure user satisfaction
- Optimize hot paths

### Community Feedback
- Gather user experiences
- Track common questions
- Note confusion points
- Implement improvements

## Review Checklist

Before completing architecture review:
- [ ] All modules inventoried
- [ ] Dependencies mapped
- [ ] Conflicts documented
- [ ] Performance measured
- [ ] Anti-patterns identified
- [ ] Improvements prioritized
- [ ] Report generated
- [ ] Action items assigned
- [ ] Timeline established
- [ ] Success metrics defined

Remember: Architecture review is not about perfection—it's about maintaining a healthy, evolving system that serves its users effectively while remaining maintainable and extensible.
