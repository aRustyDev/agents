---
module: PlanAnalysis  
scope: context
triggers: 
  - "task analysis"
  - "mvp planning"
  - "task breakdown"
conflicts: []
dependencies:
  - discovery.md
  - _core.md
priority: high
---

# PlanAnalysis - Task Analysis & MVP Planning

## Purpose
Analyze gathered requirements and break them down into actionable tasks with MVP focus.

## Overview
This module takes the requirements from the discovery phase and transforms them into a structured task breakdown suitable for implementation.

## Phase 3: Task Analysis & MVP Planning

Once the user confirms the plan is complete:

### Step 1: Review All Gathered Information
- Load requirements from discovery phase
- Validate completeness
- Identify any gaps or contradictions
- Create working notes for analysis

### Step 2: Think Step-by-Step About Implementation

Analyze each major area:

#### Core Functionality
- What are the absolute must-haves for MVP?
- What can be deferred to later versions?
- What are the critical user journeys?
- What constitutes "working" for each feature?

#### Infrastructure Requirements
- Development environment setup
- Database schema and setup
- API structure and endpoints
- Authentication/authorization needs
- Hosting and deployment infrastructure

#### Testing Requirements
- Unit test coverage expectations
- Integration test scenarios
- End-to-end test cases
- Performance benchmarks
- Security testing needs

#### Documentation Needs
- API documentation
- User documentation
- Developer onboarding guide
- Architecture decision records
- Deployment procedures

#### Deployment Considerations
- CI/CD pipeline setup
- Environment configurations
- Monitoring and logging
- Backup and recovery
- Scaling considerations

### Step 3: Identify All Tasks for MVP

Create comprehensive task breakdown:

#### Task Structure
```yaml
task:
  title: "Clear, actionable task title"
  description: |
    Detailed description including:
    - Context and background
    - Specific requirements
    - Technical considerations
  effort: "S|M|L|XL"
  priority: "p0|p1|p2|p3"
  dependencies: ["task-1", "task-2"]
  acceptance_criteria:
    - "Specific measurable outcome 1"
    - "Specific measurable outcome 2"
  labels: ["component", "type", "effort"]
```

#### Effort Estimation Guidelines
- **S (Small)**: < 4 hours
  - Simple changes
  - Documentation updates
  - Configuration changes
  
- **M (Medium)**: 4-16 hours
  - Single feature implementation
  - Moderate refactoring
  - Integration work
  
- **L (Large)**: 16-40 hours
  - Complex feature development
  - Major refactoring
  - New service creation
  
- **XL (Extra Large)**: > 40 hours
  - Architecture changes
  - Multiple integrated features
  - Major infrastructure work

#### Priority Guidelines
- **p0 (Critical)**: Blocks everything, must be done immediately
- **p1 (High)**: Core MVP functionality, needed soon
- **p2 (Medium)**: Important but not blocking
- **p3 (Low)**: Nice to have, can be deferred

### Task Categorization

Group tasks by:

#### By Component
- Frontend tasks
- Backend tasks
- Database tasks
- Infrastructure tasks
- Documentation tasks

#### By Feature Area
- User authentication
- Core business logic
- API development
- UI/UX implementation
- Testing infrastructure

#### By Implementation Phase
- Setup and configuration
- Core development
- Integration
- Testing and validation
- Deployment preparation

### Dependencies Mapping

Create dependency graph:
```
Setup Tasks
  ├── Development Environment
  ├── Database Schema
  └── CI/CD Pipeline
      │
      ▼
Core Features
  ├── User Model
  ├── Authentication
  └── Basic API
      │
      ▼
Advanced Features
  ├── Feature A (depends on User Model)
  └── Feature B (depends on Basic API)
```

### MVP Definition

Clearly define:
- **In Scope**: What must be in MVP
- **Out of Scope**: What is deferred
- **Success Criteria**: How we know MVP is complete

## Output

Creates analysis artifacts:
- `$SESSION_DIR/task-breakdown.yaml` - All tasks with metadata
- `$SESSION_DIR/dependencies.md` - Task dependency graph
- `$SESSION_DIR/mvp-scope.md` - Clear MVP definition

## Integration

This module:
- Receives data from `discovery.md`
- Provides structured tasks to `design.md`
- Uses utilities from `_core.md`

## Best Practices

1. **Be comprehensive**: Every requirement needs a task
2. **Be realistic**: Accurate effort estimates
3. **Be clear**: Unambiguous task descriptions
4. **Think dependencies**: Identify blockers early
5. **Focus on MVP**: Defer non-essential features