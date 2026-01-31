---
module: PlanImplementation  
scope: context
triggers: 
  - "plan execution"
  - "github integration"
  - "preview approval"
conflicts: []
dependencies:
  - design.md
  - _core.md
  - scripts/execute_plan.sh
  - scripts/error_handling.sh
priority: high
---

# PlanImplementation - Preview, Approval & Execution

## Purpose
Handle the preview, approval, and execution phases of the planning process, including GitHub integration.

## Overview
This module manages the final phases where users review the generated plan and execute it to create GitHub resources.

## Phase 6: Preview & Approval

### Step 1: Generate Preview Report

Create comprehensive preview showing what will be created.

**Implementation**: Preview generation is integrated into the execution flow.

Preview includes:
- Project count and names
- Milestone count with due dates
- Issue count by priority
- Label summary
- Sample issues for review

### Step 2: Display Sample Issues

Show a few example issues for user review to ensure quality before execution.

### Step 3: Approval Prompt

Present clear options for user action:
1. Execute - Create all items in GitHub
2. Preview files - See generated JSON files  
3. Edit - Modify the plan
4. Cancel - Exit without creating anything

### Step 4: Handle User Choice

#### Option 1: Execute
Proceed to Phase 7 execution

#### Option Handling

- **Option 1 (Execute)**: Proceed to execution phase
- **Option 2 (Preview)**: Display JSON files for inspection
- **Option 3 (Edit)**: Allow plan modifications
- **Option 4 (Cancel)**: Clean up and exit safely

## Phase 7: Execution & Tracking

### Step 1: Pre-execution Checks

Validate environment and permissions before execution.

**Implementation**: See `scripts/execute_plan.sh` - `pre_execution_checks()` function

Checks performed:
- GitHub CLI authentication
- Git repository presence
- Repository access permissions

### Step 2: Execute Plan

Execute the plan using the dedicated execution script.

**Implementation**: See `scripts/execute_plan.sh`

Execution order:
1. Create labels
2. Create milestones
3. Create issues (with milestone mapping)
4. Create project board

### Step 3: Track Progress

Progress tracking is built into the execution functions with real-time updates.

#### Create Milestones
```bash
echo "🎯 Creating milestones..."
milestone_map="{}"
index=1
for milestone in $(jq -r '.[] | @base64' milestones.json); do
    _jq() {
        echo ${milestone} | base64 --decode | jq -r ${1}
    }
    
    title=$(_jq '.title')
    description=$(_jq '.description')
    due_on=$(_jq '.due_on')
    
    number=$(gh api repos/:owner/:repo/milestones \
        --method POST \
        --field title="$title" \
        --field description="$description" \
        --field due_on="$due_on" \
        --jq '.number')
    
    milestone_map=$(echo $milestone_map | jq ". + {\"$index\": $number}")
    echo "  ✅ Created milestone: $title (#$number)"
    ((index++))
done
```

#### Create Issues

Issues are created with proper milestone mapping and label assignment.

**Implementation**: See `scripts/execute_plan.sh` - `create_issues()` function

### Step 4: Post-execution

After successful execution:
- Save execution summary to session directory
- Display creation counts
- Provide GitHub links for viewing created items
- Archive session for future reference

## Error Recovery

Handle common errors gracefully:
- Network failures: Retry with exponential backoff
- Rate limiting: Pause and resume
- Duplicate items: Skip and continue
- Partial completion: Save state for resume

## Integration

This module:
- Receives scripts from `design.md`
- Uses utilities from `_core.md`
- Integrates with GitHub via CLI

## Best Practices

1. **Always preview first**: Let users review before execution
2. **Provide escape routes**: Allow cancellation at any point
3. **Track progress**: Show what's being created
4. **Handle errors gracefully**: Don't leave partial state
5. **Save everything**: Keep records of what was created