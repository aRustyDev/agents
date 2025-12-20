# Pattern: Systematic Review

## Purpose
Provide a structured, repeatable approach to reviewing repositories or complex systems, ensuring comprehensive coverage and consistent quality.

## Context
Use this pattern when you need to:
- Audit a repository comprehensively
- Review code or documentation systematically  
- Ensure nothing is missed in analysis
- Maintain consistency across reviews

## Pattern Structure

### 1. Establish Baseline

#### 1.1 Initial Inventory
```yaml
baseline_establishment:
  capture:
    - current_state: Document what exists now
    - metrics: Quantify measurable aspects
    - structure: Map organization and relationships
    
  document:
    - file_counts: By type and location
    - size_metrics: Lines, bytes, complexity
    - dependency_graph: Component relationships
    - quality_baseline: Current scores
```

#### 1.2 Success Criteria
```yaml
define_success:
  objectives:
    - what_good_looks_like: Clear target state
    - measurable_goals: Specific metrics
    - quality_standards: Minimum requirements
    
  constraints:
    - time_available: Review deadline
    - resources: People and tools
    - scope_boundaries: What's in/out
```

### 2. Three-Round Review Method

#### Round 1: Breadth-First Survey
```yaml
round_1_survey:
  purpose: Get the big picture
  
  activities:
    - walk_through: Navigate entire structure
    - categorize: Group similar items
    - flag_obvious: Mark clear issues
    - note_patterns: Identify recurring themes
    
  outputs:
    - structure_map: Visual/textual overview
    - initial_findings: Obvious problems
    - areas_of_concern: Need deeper review
    
  time_allocation: 25% of total
```

#### Round 2: Deep Dive Analysis
```yaml
round_2_analysis:
  purpose: Detailed investigation of concerns
  
  activities:
    - examine_flagged: Deep dive on Round 1 findings
    - trace_dependencies: Follow connections
    - verify_assumptions: Test hypotheses
    - measure_quality: Apply quality metrics
    
  techniques:
    - follow_the_thread: Trace issues to root
    - compare_contrast: Look for inconsistencies
    - boundary_testing: Check edge cases
    
  outputs:
    - detailed_findings: Specific issues
    - root_causes: Why problems exist
    - impact_assessment: Severity and scope
    
  time_allocation: 50% of total
```

#### Round 3: Synthesis and Validation
```yaml
round_3_synthesis:
  purpose: Consolidate and verify findings
  
  activities:
    - cross_reference: Validate findings
    - prioritize: Rank by impact
    - find_solutions: Identify fixes
    - create_roadmap: Plan improvements
    
  validation:
    - peer_review: Second opinion
    - spot_checks: Verify samples
    - assumption_testing: Challenge conclusions
    
  outputs:
    - final_report: Consolidated findings
    - action_plan: Prioritized fixes
    - recommendations: Strategic advice
    
  time_allocation: 25% of total
```

### 3. Perspective Shifting

#### 3.1 Multiple Viewpoints
```yaml
perspective_rotation:
  user_perspective:
    focus: Usability and accessibility
    questions:
      - Is it easy to find what I need?
      - Are instructions clear?
      - Do examples help understanding?
      
  maintainer_perspective:
    focus: Maintainability and evolution
    questions:
      - How hard is it to update?
      - Are dependencies clear?
      - Is technical debt manageable?
      
  architect_perspective:
    focus: Structure and design
    questions:
      - Is the organization logical?
      - Are patterns consistent?
      - Does it scale well?
```

#### 3.2 Time-Based Views
```yaml
temporal_analysis:
  historical_view:
    - How did we get here?
    - What decisions were made?
    - What problems were solved?
    
  current_view:
    - What works well now?
    - What causes friction?
    - Where are the pain points?
    
  future_view:
    - What will break first?
    - Where will growth stress appear?
    - What needs future-proofing?
```

### 4. Evidence Gathering

#### 4.1 Documentation Requirements
```yaml
evidence_standards:
  for_each_finding:
    - specific_example: File:line reference
    - impact_description: Who/what affected
    - frequency: How often occurs
    - severity: Critical/High/Medium/Low
    
  supporting_data:
    - metrics: Quantifiable measurements
    - patterns: Multiple instances
    - alternatives: Other approaches
```

#### 4.2 Evidence Chain
```yaml
evidence_chain:
  observation:
    what: Initial finding
    where: Specific location
    
  analysis:
    why: Root cause
    how: Mechanism of issue
    
  impact:
    who: Affected users
    when: Occurrence conditions
    
  solution:
    fix: Proposed remedy
    effort: Implementation cost
```

### 5. Review Checklist

#### 5.1 Completeness Checks
```yaml
completeness_checklist:
  coverage:
    - [ ] All directories visited
    - [ ] All file types examined
    - [ ] All connections traced
    - [ ] All assumptions tested
    
  quality:
    - [ ] Documentation complete
    - [ ] Examples provided
    - [ ] Tests adequate
    - [ ] Performance acceptable
    
  consistency:
    - [ ] Naming conventions
    - [ ] Structure patterns
    - [ ] Style guidelines
    - [ ] Integration patterns
```

#### 5.2 Quality Gates
```yaml
quality_gates:
  must_have:
    - No broken references
    - No security vulnerabilities
    - Core functionality works
    - Documentation exists
    
  should_have:
    - Good test coverage
    - Performance optimization
    - Error handling
    - Logging/monitoring
    
  nice_to_have:
    - Advanced features
    - Extra documentation
    - Performance tuning
    - Aesthetic improvements
```

## Implementation Example

### Repository Audit Application
```bash
# Round 1: Survey
echo "=== Round 1: Breadth-First Survey ==="
find . -type f -name "*.md" | wc -l  # Count files
du -sh .                              # Check size
tree -d -L 2                         # View structure

# Round 2: Deep Dive  
echo "=== Round 2: Deep Dive Analysis ==="
# Check specific concerns from Round 1
grep -r "TODO" . | wc -l             # Count TODOs
find . -size +100k                   # Large files
# ... detailed checks ...

# Round 3: Synthesis
echo "=== Round 3: Synthesis ==="
# Consolidate findings
# Prioritize issues
# Generate report
```

## Variations

### Quick Review (1-2 hours)
- Single pass instead of three rounds
- Focus on critical issues only
- High-level recommendations

### Deep Review (Multiple days)
- Extended Round 2 analysis
- Multiple perspective reviews
- Detailed remediation planning

### Continuous Review
- Automated Round 1 surveys
- Triggered deep dives
- Rolling synthesis updates

## Success Indicators
- Comprehensive coverage achieved
- All critical issues identified
- Clear action plan produced
- Stakeholder agreement on findings

## Common Pitfalls
- Analysis paralysis in Round 2
- Missing forest for trees
- Insufficient evidence gathering
- Unclear prioritization

## Related Patterns
- deep-exploration.md
- iterative-refinement.md
- root-cause-analysis.md