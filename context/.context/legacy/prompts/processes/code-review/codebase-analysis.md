---
name: Codebase Review Process
module_type: process
scope: context
priority: high
triggers: ["review codebase", "analyze code", "before planning", "understand project", "explore codebase"]
dependencies: ["processes/issue-tracking/issue-management.md"]
conflicts: []
version: 1.0.0
---

# Codebase Review Process

## Purpose
Systematically analyze a codebase before planning any implementation to understand structure, patterns, dependencies, and risks. This ensures informed decisions and pattern-consistent implementations.

## Trigger
Execute BEFORE planning any:
- New feature implementation
- Bug fix
- Refactoring task
- Architecture changes

## Prerequisites
- Access to project repository
- Understanding of the requested change
- List of potentially affected areas

## Process Steps

### 1. Initial Context Gathering
```
1.1 Identify the scope of the requested change
1.2 List keywords related to the change:
    - Component names
    - Function names
    - Business concepts
    - Technical terms
1.3 Determine which parts of the codebase might be affected
1.4 Create initial hypothesis about implementation areas
```

### 2. Project Structure Analysis
```bash
# Review directory structure
${version_control} ls-tree -r HEAD --name-only | head -50

# Identify key directories
find . -type d -name "src" -o -name "lib" -o -name "test" | head -20

# Check technology stack
ls -la | grep -E "(package.json|requirements.txt|go.mod|Gemfile|pom.xml)"
```

Key areas to identify:
- Source code locations (src/, lib/, app/)
- Test directories (test/, spec/, __tests__/)
- Configuration files (config/, .*)
- Documentation (docs/, README*)
- CI/CD configurations

### 3. Architecture Discovery

#### Identify Patterns
- **MVC**: controllers/, models/, views/
- **Clean Architecture**: domain/, infrastructure/, application/
- **Microservices**: Separate service directories
- **Layered**: presentation/, business/, data/

#### Map Components
```bash
# Find entry points
find . -name "main.*" -o -name "index.*" -o -name "app.*"

# Locate core business logic
grep -r "class.*Service" --include="*.js" --include="*.py" --include="*.java"

# Identify API boundaries
find . -type f -name "*controller*" -o -name "*handler*" -o -name "*route*"
```

### 4. Code Pattern Analysis

#### Naming Conventions
```bash
# Check casing patterns
grep -r "function \w\+" --include="*.js" | head -10
grep -r "class \w\+" --include="*.py" | head -10
```

#### Common Patterns to Identify
1. **Error Handling**
   - Try-catch patterns
   - Error types used
   - Logging approaches

2. **State Management**
   - Global state locations
   - State update patterns
   - Immutability practices

3. **Authentication/Authorization**
   - Middleware locations
   - Permission checking
   - Session management

### 5. Dependency Analysis
```bash
# Check package files
cat package.json | jq '.dependencies'
cat requirements.txt
cat go.mod | grep -v indirect

# Look for security issues
npm audit --production
pip check
```

Categorize:
- Core framework dependencies
- Utility libraries
- Development dependencies
- Security-related packages

### 6. Test Infrastructure Review

#### Locate Tests
```bash
# Find test files
find . -name "*test*" -o -name "*spec*" | grep -E "\.(js|py|go|java)$"

# Check test framework
grep -E "(jest|mocha|pytest|junit|testing)" package.json requirements.txt go.mod
```

#### Assess Quality
- Test naming conventions
- Coverage reports location
- Mock/stub strategies
- Test data management

### 7. Related Feature Analysis

Search for similar implementations:
```bash
# Search by feature keywords
grep -r "${feature_keyword}" --include="*.${extension}" | head -20

# Find similar patterns
grep -r "${pattern}" --include="*.${extension}" -B 2 -A 2
```

Document:
- Code structure used
- Design patterns applied
- Reusable components
- Integration methods

### 8. Risk Assessment

#### High-Risk Areas
- **Security**: Auth, encryption, input validation
- **Business Critical**: Payments, core algorithms
- **Performance**: Database queries, API endpoints
- **Data Integrity**: Validation, transactions

#### Technical Debt Indicators
```bash
# Find TODOs and FIXMEs
grep -r "TODO\|FIXME\|HACK\|XXX" --include="*.${extension}"

# Check for deprecated usage
grep -r "@deprecated\|DEPRECATED" --include="*.${extension}"
```

### 9. Documentation Review

Check for:
```bash
# README files
find . -name "README*" -type f

# API documentation
find . -name "*.md" -path "*/docs/*" -o -path "*/documentation/*"

# Inline documentation
grep -r "\/\*\*\|'''\|\"\"\"" --include="*.${extension}" | wc -l
```

### 10. Create Review Summary

## Review Summary Template

```markdown
### Codebase Review Summary

#### Project Overview
- **Structure**: [monorepo/standard/microservices]
- **Stack**: [languages and frameworks]
- **Architecture**: [patterns identified]
- **Test Coverage**: [general assessment]

#### Relevant Context for [Task Name]
- **Affected Areas**:
  - [Component/Module 1]: [why relevant]
  - [Component/Module 2]: [why relevant]

- **Similar Implementations**:
  - [Feature]: [location] - [approach used]
  - [Feature]: [location] - [approach used]

- **Key Patterns to Follow**:
  - [Pattern]: [example usage]
  - [Pattern]: [example usage]

#### Dependencies & Constraints
- **Must Use**: [required dependencies/patterns]
- **Must Avoid**: [deprecated patterns/anti-patterns]
- **External Dependencies**: [relevant packages]

#### Risk Analysis
- **High Risk Areas**:
  - [Area]: [risk type] - [mitigation strategy]
- **Technical Debt**:
  - [Debt item]: [impact] - [recommendation]
- **Test Coverage**:
  - [Area]: [coverage status]

#### Recommendations
1. [Specific approach for the task]
2. [Components to reuse]
3. [Patterns to follow]
4. [Risks to mitigate]

#### Questions for Clarification
- [Question about requirements]
- [Question about constraints]
- [Question about preferences]
```

## Conditional Execution

### For Feature Implementation
**FOCUS ON**:
- Architecture Discovery (DETAILED)
- Code Pattern Analysis (DETAILED)
- Related Feature Analysis (CRITICAL)

**LIGHTER ON**:
- Dependency Analysis (QUICK CHECK)

### For Bug Fix
**FOCUS ON**:
- Related Feature Analysis (CRITICAL)
- Risk Assessment (DETAILED)
- Test Infrastructure (DETAILED)

**LIGHTER ON**:
- Architecture Discovery (BASIC)

### For Refactoring
**FOCUS ON**:
- Code Pattern Analysis (CRITICAL)
- Test Infrastructure (CRITICAL)
- Risk Assessment (DETAILED)
- Dependency Analysis (DETAILED)

## Integration Points
- Feeds into: Process: FeaturePlanning
- Feeds into: Process: TaskBreakdown
- May trigger: Process: RiskMitigation
- Updates: Issue tracker with findings

## Time Guidelines
- **Minimal Review** (tiny fixes): 2-3 minutes
- **Standard Review** (typical changes): 5-10 minutes
- **Deep Review** (major changes): 15-20 minutes

## Best Practices

### DO
- ✅ Always review before planning
- ✅ Use findings to inform approach
- ✅ Document questions immediately
- ✅ Focus review based on task type
- ✅ Update if scope changes

### DON'T
- ❌ Skip review for "simple" changes
- ❌ Make assumptions about patterns
- ❌ Ignore test infrastructure
- ❌ Review without clear scope
- ❌ Spend too long on exhaustive analysis

## Common Commands Reference

### Language-Specific Searches
```bash
# JavaScript/TypeScript
find . -name "*.js" -o -name "*.ts" | xargs grep -l "className"

# Python
find . -name "*.py" | xargs grep -l "class.*:"

# Go
find . -name "*.go" | xargs grep -l "type.*struct"

# Java
find . -name "*.java" | xargs grep -l "public class"
```

### Quick Analysis Commands
```bash
# Count lines of code by language
find . -name "*.${ext}" -exec wc -l {} + | tail -1

# Find largest files
find . -name "*.${ext}" -exec wc -l {} + | sort -rn | head -10

# Recent changes in area
${version_control} log --oneline -n 20 -- path/to/area
```

---
*A thorough codebase review prevents surprises and ensures pattern-consistent implementation.*