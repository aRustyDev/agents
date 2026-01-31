---
module: ${PROCESS_NAME}Process
scope: ${SCOPE}
triggers: 
  - "${TRIGGER_PHRASE_1}"
  - "${TRIGGER_PHRASE_2}"
conflicts: []
dependencies: []
priority: ${PRIORITY}
process_type: ${PROCESS_TYPE}  # manual|automated|hybrid
estimated_time: ${TIME_ESTIMATE}
---

# ${PROCESS_NAME} Process

## Purpose
${PURPOSE_STATEMENT}

## When to Use
${WHEN_TO_USE}

## Prerequisites
- [ ] ${PREREQUISITE_1}
- [ ] ${PREREQUISITE_2}
- [ ] ${PREREQUISITE_3}

## Process Steps

### Step 1: ${STEP_1_NAME}
**Duration**: ${STEP_1_DURATION}  
**Responsible**: ${STEP_1_RESPONSIBLE}

${STEP_1_DESCRIPTION}

**Actions**:
1. ${STEP_1_ACTION_1}
2. ${STEP_1_ACTION_2}
3. ${STEP_1_ACTION_3}

**Deliverables**:
- ${STEP_1_DELIVERABLE_1}
- ${STEP_1_DELIVERABLE_2}

### Step 2: ${STEP_2_NAME}
**Duration**: ${STEP_2_DURATION}  
**Responsible**: ${STEP_2_RESPONSIBLE}

${STEP_2_DESCRIPTION}

**Actions**:
1. ${STEP_2_ACTION_1}
2. ${STEP_2_ACTION_2}

**Deliverables**:
- ${STEP_2_DELIVERABLE_1}

### Step 3: ${STEP_3_NAME}
[Continue pattern...]

## Decision Points

### Decision 1: ${DECISION_1_NAME}
**When**: ${DECISION_1_WHEN}  
**Criteria**: ${DECISION_1_CRITERIA}

**Options**:
- **Option A**: ${OPTION_A_DESCRIPTION}
  - Proceed to: ${OPTION_A_NEXT}
- **Option B**: ${OPTION_B_DESCRIPTION}
  - Proceed to: ${OPTION_B_NEXT}

## Quality Checks

### Check 1: ${CHECK_1_NAME}
- **What to verify**: ${CHECK_1_VERIFY}
- **Acceptance criteria**: ${CHECK_1_CRITERIA}
- **If failed**: ${CHECK_1_FAILURE_ACTION}

## Tools and Resources
- ${TOOL_1}
- ${TOOL_2}
- ${RESOURCE_1}

## Common Issues and Solutions

### Issue: ${ISSUE_1_NAME}
**Symptoms**: ${ISSUE_1_SYMPTOMS}  
**Solution**: ${ISSUE_1_SOLUTION}

### Issue: ${ISSUE_2_NAME}
**Symptoms**: ${ISSUE_2_SYMPTOMS}  
**Solution**: ${ISSUE_2_SOLUTION}

## Rollback Procedures
${ROLLBACK_STEPS}

## Metrics and KPIs
- ${METRIC_1}: ${METRIC_1_TARGET}
- ${METRIC_2}: ${METRIC_2_TARGET}

## Process Improvement
${IMPROVEMENT_NOTES}

## Related Processes
- [[${RELATED_PROCESS_1}]]
- [[${RELATED_PROCESS_2}]]

---

*This process follows Claude process standards.*