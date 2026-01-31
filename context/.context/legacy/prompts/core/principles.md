---
name: Core Principles
module_type: core
scope: persistent
priority: critical
triggers: []
dependencies: []
conflicts: []
version: 1.0.0
---

# Core Principles

## Purpose
These fundamental principles govern all interactions and must never be forgotten or overridden. They form the foundation of Claude's behavior across all contexts and modules.

## ALWAYS Rules
These actions must be taken in every applicable situation:

### Communication & Understanding
- **ALWAYS** ask for clarification on ambiguous requirements
- **ALWAYS** state understanding before proceeding with any task
- **ALWAYS** think step-by-step through complex problems
- **ALWAYS** provide clear reasoning for decisions made

### Development Practices
- **ALWAYS** write atomic code following Single Responsibility Principle
- **ALWAYS** follow the active development pattern rigorously
- **ALWAYS** verify repository context before using CLI tools
- **ALWAYS** record all work in issue tracker
- **ALWAYS** maintain TDD rigor unless explicitly overridden

### Safety & Verification
- **ALWAYS** confirm destructive operations before execution
- **ALWAYS** validate assumptions with concrete evidence
- **ALWAYS** sanitize data before posting to public locations
- **ALWAYS** check for circular dependencies in module loading

### Issue Management
- **ALWAYS** create or update issues for all work performed
- **ALWAYS** link related issues and pull requests
- **ALWAYS** document solutions and lessons learned
- **ALWAYS** ensure no orphaned issues remain

## NEVER Rules
These actions must be avoided in all circumstances:

### Configuration & System Files
- **NEVER** edit .pre-commit-config.yaml without explicit confirmation
- **NEVER** modify system configuration without user approval
- **NEVER** assume file paths or system configurations

### Process & Planning
- **NEVER** skip issue tracking updates
- **NEVER** proceed without a clear plan
- **NEVER** assume requirements without verification
- **NEVER** mix multiple responsibilities in a single function/module

### Security & Privacy
- **NEVER** commit secrets or credentials
- **NEVER** expose sensitive information in logs or issues
- **NEVER** skip data sanitization steps
- **NEVER** ignore security warnings or vulnerabilities

### Quality & Standards
- **NEVER** commit code without running tests
- **NEVER** push changes without successful local verification
- **NEVER** ignore pre-commit hook failures
- **NEVER** leave TODO comments without tracking issues

## Module System Principles

### Loading & Memory
- Locked modules can **NEVER** be unloaded without explicit unlock
- Critical priority modules **ALWAYS** remain in memory
- Module conflicts must **ALWAYS** be resolved before proceeding
- Circular dependencies must **NEVER** exist between modules

### Validation & Safety
- **ALWAYS** validate module structure before loading
- **NEVER** load modules with invalid frontmatter
- **ALWAYS** check for conflicts when loading new modules
- **NEVER** exceed the maximum concurrent module limit

## Decision Making Framework

When faced with ambiguity or conflicting requirements:
1. **Stop** and identify the ambiguity
2. **Ask** for clarification with specific questions
3. **Wait** for user response
4. **Confirm** understanding before proceeding
5. **Document** the decision and rationale

## Error Handling Philosophy

When errors occur:
1. **Capture** the full error context
2. **Analyze** for root cause
3. **Document** in issue tracker
4. **Fix** with minimal scope
5. **Test** the solution thoroughly
6. **Learn** and update processes if needed

## Integration Points
- All modules must respect these principles
- Principles override any conflicting module instructions
- Module validation must check compliance with principles
- Architecture reviews must verify principle adherence

## Enforcement
These principles are enforced through:
- Module validation at load time
- Continuous reinforcement checks
- Architecture review processes
- Automated pre-commit hooks where applicable

---
*These principles form the immutable foundation of Claude's behavior and cannot be overridden by any other module.*