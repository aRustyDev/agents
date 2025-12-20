# Pattern: Iterative Refinement

## Purpose
Progressively improve analysis quality through multiple focused passes, each building on previous insights to achieve comprehensive understanding.

## Context
Use this pattern when:
- Complex problems require multiple perspectives
- Initial analysis reveals new questions
- Quality improvements are needed incrementally
- Time allows for multiple iterations

## Pattern Structure

### 1. Iteration Planning

#### 1.1 Iteration Goals
```yaml
iteration_structure:
  iteration_1_discovery:
    goal: Understand the landscape
    focus: Breadth over depth
    output: Initial findings and questions
    
  iteration_2_investigation:
    goal: Answer key questions
    focus: Targeted deep dives
    output: Detailed findings
    
  iteration_3_refinement:
    goal: Polish and validate
    focus: Quality and completeness
    output: Final recommendations
    
  iteration_n_optimization:
    goal: Continuous improvement
    focus: Emerging issues
    output: Ongoing enhancements
```

#### 1.2 Iteration Timebox
```yaml
time_allocation:
  fixed_time:
    - Equal duration per iteration
    - Forced progression
    - Prevents analysis paralysis
    
  variable_time:
    - Based on findings
    - Flexible depth
    - Risk of overrun
    
  hybrid_approach:
    - Core iterations fixed
    - Optional iterations flexible
    - Balance of structure and adaptability
```

### 2. Progressive Refinement Techniques

#### 2.1 Layered Analysis
```yaml
analysis_layers:
  surface_layer:
    - Obvious issues
    - Quick wins
    - Basic metrics
    
  structural_layer:
    - Organization problems
    - Design flaws
    - Integration issues
    
  semantic_layer:
    - Meaning and intent
    - Conceptual gaps
    - Purpose alignment
    
  quality_layer:
    - Performance issues
    - Optimization opportunities
    - Excellence gaps
```

#### 2.2 Focus Narrowing
```yaml
focus_progression:
  iteration_1:
    scope: Entire repository
    depth: Shallow
    findings: 50+ issues
    
  iteration_2:
    scope: Problem areas
    depth: Medium
    findings: 20 key issues
    
  iteration_3:
    scope: Critical issues
    depth: Deep
    findings: 5-10 root causes
```

### 3. Feedback Integration

#### 3.1 Learning Loop
```yaml
learning_loop:
  capture:
    - What worked well
    - What was missed
    - What surprised us
    
  analyze:
    - Why did we miss it
    - How can we improve
    - What patterns emerge
    
  adjust:
    - Update checklist
    - Refine process
    - Add new techniques
    
  apply:
    - Use in next iteration
    - Document changes
    - Share learnings
```

#### 3.2 Stakeholder Feedback
```yaml
feedback_integration:
  after_each_iteration:
    - Share preliminary findings
    - Gather reactions
    - Adjust focus
    
  feedback_types:
    - Priority adjustments
    - Additional context
    - Validation/correction
    - New concerns
    
  incorporation:
    - Document feedback
    - Adjust next iteration
    - Track changes
```

### 4. Quality Enhancement

#### 4.1 Refinement Checklist
```yaml
quality_checklist:
  clarity:
    - [ ] Clear problem statement
    - [ ] Unambiguous findings
    - [ ] Specific examples
    - [ ] Actionable recommendations
    
  completeness:
    - [ ] All areas covered
    - [ ] Questions answered
    - [ ] Evidence provided
    - [ ] Edge cases considered
    
  correctness:
    - [ ] Facts verified
    - [ ] Logic sound
    - [ ] Assumptions stated
    - [ ] Conclusions justified
    
  consistency:
    - [ ] Terminology uniform
    - [ ] Format standardized
    - [ ] Tone appropriate
    - [ ] Level consistent
```

#### 4.2 Enhancement Techniques
```yaml
enhancement_methods:
  clarification:
    - Add examples
    - Simplify language
    - Define terms
    - Visualize concepts
    
  expansion:
    - Add detail
    - Provide context
    - Include alternatives
    - Explore implications
    
  validation:
    - Cross-check facts
    - Test assumptions
    - Verify references
    - Confirm with experts
```

### 5. Iteration Patterns

#### 5.1 Spiral Model
```yaml
spiral_iteration:
  characteristics:
    - Each pass covers same ground
    - Deeper investigation each time
    - Builds on previous knowledge
    - Expanding understanding
    
  advantages:
    - Comprehensive coverage
    - Progressive depth
    - Early broad insights
    
  when_to_use:
    - Unknown problem space
    - Complex dependencies
    - Learning while analyzing
```

#### 5.2 Focused Iteration
```yaml
focused_iteration:
  characteristics:
    - Each pass examines different aspect
    - Specialized analysis
    - Minimal overlap
    - Targeted outcomes
    
  advantages:
    - Efficient time use
    - Deep expertise per area
    - Clear boundaries
    
  when_to_use:
    - Well-understood domain
    - Specific concerns
    - Limited time
```

#### 5.3 Adaptive Iteration
```yaml
adaptive_iteration:
  characteristics:
    - Direction based on findings
    - Flexible focus
    - Responsive to discoveries
    - Emergent path
    
  advantages:
    - Follows important leads
    - Maximizes value
    - Addresses real issues
    
  when_to_use:
    - Exploratory analysis
    - Unknown problems
    - Research mode
```

## Implementation Example

### Three-Iteration Repository Analysis
```bash
# Iteration 1: Discovery (2 hours)
echo "=== Iteration 1: Discovery ==="
# Broad survey
find . -type f | wc -l
find . -size +50k
grep -r "TODO\|FIXME" . | wc -l
# Document initial findings

# Iteration 2: Investigation (4 hours)
echo "=== Iteration 2: Investigation ==="
# Deep dive on issues from iteration 1
# Analyze large files
# Investigate TODO patterns
# Check specific problem areas

# Iteration 3: Refinement (2 hours)
echo "=== Iteration 3: Refinement ==="
# Validate findings
# Prioritize issues
# Polish recommendations
# Create action plan
```

## Success Indicators

### Iteration Quality Metrics
```yaml
quality_indicators:
  convergence:
    - Fewer new issues each iteration
    - Clearer understanding
    - Stabilizing recommendations
    
  depth:
    - More specific findings
    - Root causes identified
    - Nuanced understanding
    
  actionability:
    - Clear next steps
    - Prioritized items
    - Feasible improvements
```

### Stopping Criteria
```yaml
when_to_stop:
  objective_met:
    - All questions answered
    - Required depth achieved
    - Stakeholders satisfied
    
  diminishing_returns:
    - Few new findings
    - Minor improvements only
    - Time better spent elsewhere
    
  resource_limits:
    - Time exhausted
    - Budget consumed
    - Team unavailable
```

## Common Pitfalls

### Iteration Traps
- Endless refinement without shipping
- Losing sight of goals
- Over-polishing low-priority items
- Skipping synthesis between iterations

### Mitigation Strategies
- Set clear iteration goals
- Timebox strictly
- Regular stakeholder check-ins
- Focus on highest value items

## Related Patterns
- systematic-review.md
- deep-exploration.md
- continuous-improvement.md