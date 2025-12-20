---
module: PlanDiscovery  
scope: context
triggers: 
  - "/plan init"
  - "/plan feature"
  - "/plan fix"
  - "/plan refactor"
  - "project planning"
conflicts: []
dependencies:
  - _core.md
priority: high
---

# PlanDiscovery - Requirements Gathering Phase

## Purpose
Initial setup and comprehensive requirements gathering for project planning.

## Overview
This module handles the discovery phase of planning, including setup, initialization, and iterative information gathering. It's used by init, feature, fix, and refactor subcommands.

## Phase 1: Setup & Initialization

1. **Detect subcommand**: Check if user specified init/feature/fix/refactor
2. **Create session directory**:
   ```bash
   SESSION_ID=$(date +%Y%m%d_%H%M%S)
   SESSION_DIR=".plan/sessions/$SESSION_ID"
   mkdir -p "$SESSION_DIR"
   echo "📁 Created session: $SESSION_DIR"
   ```

3. **Check for resume**: Look for existing sessions if user wants to continue
   ```bash
   if [ -d ".plan/sessions" ] && [ "$(ls -A .plan/sessions)" ]; then
     echo "Found existing sessions. Would you like to resume? (y/n)"
     # List sessions with creation times
   fi
   ```

## Phase 2: Iterative Information Gathering

**CRITICAL**: This is the most important phase. You must be thorough and persistent in gathering information.

### High-Level Questions

Start with understanding the big picture:
- What is the purpose/goal of this [project/feature/fix/refactor]?
- What problem does it solve?
- Who are the intended users?
- What does success look like?

### Specific Details Gathering

Keep asking until comprehensive:

#### Problem & Solution
- Current problem state (with examples)
- Desired solution state (with examples)
- Specific features/capabilities needed

#### Technical Requirements
- Performance needs (speed sensitive?)
- Size constraints (needs to be lightweight?)
- Platform compatibility (specific OS? browser?)
- Dependencies (external libraries? APIs?)
- Security requirements

#### Integration & Ecosystem
- Existing codebase integration
- API compatibility needs
- Database requirements
- Third-party service integration

#### Constraints & Limitations
- Timeline constraints
- Resource limitations
- Technical debt considerations
- Backward compatibility needs

### Information Storage

Save all gathered information incrementally:
```bash
# After each answer, save to session
echo "Q: $QUESTION" >> "$SESSION_DIR/requirements.md"
echo "A: $ANSWER" >> "$SESSION_DIR/requirements.md"
echo "" >> "$SESSION_DIR/requirements.md"
```

## Subcommand-Specific Discovery

### For `init` - New Project
Additional discovery questions:
- Project type (web app, CLI tool, library, etc.)
- Technology stack preferences
- Team size and roles
- Development methodology (agile, waterfall, etc.)
- CI/CD requirements

### For `feature` - Feature Development
Additional discovery questions:
- How does this fit into existing functionality?
- Are there similar features to reference?
- What are the acceptance criteria?
- Any UI/UX considerations?
- Performance benchmarks?

### For `fix` - Bug Fixes
Additional discovery questions:
- How to reproduce the bug?
- When did it start occurring?
- What's the expected vs actual behavior?
- Impact severity and scope?
- Any workarounds currently in use?

### For `refactor` - Code Refactoring
Additional discovery questions:
- What specific code needs refactoring?
- What are the current pain points?
- Performance goals?
- Maintainability improvements needed?
- Risk assessment for the refactor?

## Discovery Completion Criteria

Before moving to analysis phase, ensure:
- [ ] Clear problem statement documented
- [ ] Success criteria defined
- [ ] All technical requirements gathered
- [ ] Constraints and limitations identified
- [ ] Stakeholders and users identified
- [ ] Integration points mapped

## Output

Creates `$SESSION_DIR/requirements.md` containing:
- Timestamp and session ID
- Subcommand type
- All Q&A pairs
- Summary of key requirements
- Ready for analysis phase

## Integration

This module provides data for:
- `analysis.md` - Task breakdown and MVP planning
- `design.md` - Technical design decisions
- `_core.md` - Session management utilities

## Best Practices

1. **Be persistent**: Keep asking clarifying questions
2. **Document everything**: Every detail matters
3. **Validate understanding**: Summarize and confirm
4. **Think ahead**: Consider future phases' needs
5. **Stay organized**: Use consistent formatting