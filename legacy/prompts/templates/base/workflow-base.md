---
module: ${WORKFLOW_NAME}Workflow
scope: ${SCOPE}
triggers: 
  - "${TRIGGER_1}"
  - "${TRIGGER_2}"
conflicts: []
dependencies: []
priority: ${PRIORITY}
workflow_type: ${WORKFLOW_TYPE}  # linear|branching|iterative
automation_level: ${AUTOMATION_LEVEL}  # manual|partial|full
---

# ${WORKFLOW_NAME} Workflow

## Purpose
${PURPOSE_DESCRIPTION}

## Overview
${WORKFLOW_OVERVIEW}

## Entry Criteria
- [ ] ${ENTRY_CRITERION_1}
- [ ] ${ENTRY_CRITERION_2}
- [ ] ${ENTRY_CRITERION_3}

## Exit Criteria
- [ ] ${EXIT_CRITERION_1}
- [ ] ${EXIT_CRITERION_2}
- [ ] ${EXIT_CRITERION_3}

## Workflow Diagram
```mermaid
graph TD
    A[${START_NODE}] --> B{${DECISION_NODE_1}}
    B -->|${CONDITION_1}| C[${ACTION_NODE_1}]
    B -->|${CONDITION_2}| D[${ACTION_NODE_2}]
    C --> E[${MERGE_NODE}]
    D --> E
    E --> F{${DECISION_NODE_2}}
    F -->|${CONDITION_3}| G[${END_NODE}]
    F -->|${CONDITION_4}| H[${LOOP_BACK_NODE}]
    H --> B
```

## Phases

### Phase 1: ${PHASE_1_NAME}
**Duration**: ${PHASE_1_DURATION}  
**Objective**: ${PHASE_1_OBJECTIVE}

#### Activities
1. ${PHASE_1_ACTIVITY_1}
2. ${PHASE_1_ACTIVITY_2}
3. ${PHASE_1_ACTIVITY_3}

#### Deliverables
- ${PHASE_1_DELIVERABLE_1}
- ${PHASE_1_DELIVERABLE_2}

#### Gates
- [ ] ${PHASE_1_GATE_1}
- [ ] ${PHASE_1_GATE_2}

### Phase 2: ${PHASE_2_NAME}
[Continue pattern...]

## Roles and Responsibilities

### ${ROLE_1_NAME}
- ${ROLE_1_RESPONSIBILITY_1}
- ${ROLE_1_RESPONSIBILITY_2}

### ${ROLE_2_NAME}
- ${ROLE_2_RESPONSIBILITY_1}
- ${ROLE_2_RESPONSIBILITY_2}

## Handoffs

### Handoff 1: ${HANDOFF_1_NAME}
**From**: ${HANDOFF_1_FROM}  
**To**: ${HANDOFF_1_TO}  
**Artifacts**: ${HANDOFF_1_ARTIFACTS}  
**Criteria**: ${HANDOFF_1_CRITERIA}

## Automation Points
${AUTOMATION_OPPORTUNITIES}

## Exception Handling

### Exception: ${EXCEPTION_1_NAME}
**Trigger**: ${EXCEPTION_1_TRIGGER}  
**Handler**: ${EXCEPTION_1_HANDLER}  
**Recovery**: ${EXCEPTION_1_RECOVERY}

## Monitoring and Metrics

### Key Metrics
- ${METRIC_1_NAME}: ${METRIC_1_DESCRIPTION}
- ${METRIC_2_NAME}: ${METRIC_2_DESCRIPTION}

### Health Indicators
- ${INDICATOR_1}
- ${INDICATOR_2}

### Alerts
- ${ALERT_1_CONDITION}: ${ALERT_1_ACTION}
- ${ALERT_2_CONDITION}: ${ALERT_2_ACTION}

## Optimization Opportunities
${OPTIMIZATION_NOTES}

## Integration Points
- ${INTEGRATION_1}
- ${INTEGRATION_2}

## Related Workflows
- [[${RELATED_WORKFLOW_1}]]
- [[${RELATED_WORKFLOW_2}]]

---

*This workflow follows Claude workflow standards.*