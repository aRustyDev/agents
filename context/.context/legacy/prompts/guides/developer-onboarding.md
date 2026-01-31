# Developer Onboarding Guide
## Welcome to the Claude Module System

**Version**: 1.0.0  
**Last Updated**: January 9, 2025

---

## 🎯 Quick Start (15 minutes)

### Step 1: Install Pre-commit Hooks (2 minutes)
```bash
# Install pre-commit
pip install pre-commit

# Install hooks in your repository
pre-commit install

# Run hooks manually (optional)
pre-commit run --all-files
```

### Step 2: Understand the Structure (5 minutes)
```
.claude/
├── commands/        # Slash commands (/help, /plan, etc.)
├── processes/       # Repeatable processes
├── workflows/       # Multi-step workflows
├── patterns/        # Design patterns
├── roles/          # Expert roles
├── standards/      # Quality standards
├── tests/          # Test framework
├── hooks/          # Pre-commit hooks
├── automation/     # Automation scripts
└── guides/         # Documentation
```

### Step 3: Create Your First Module (8 minutes)
```bash
# Use the template engine
python3 .claude/templates/template-engine.py create command-base my-command.md \
  --var COMMAND_NAME=analyze \
  --var COMMAND_DESCRIPTION="Analyze code for patterns" \
  --var SCOPE=context \
  --var PRIORITY=medium

# Or use interactive mode
python3 .claude/templates/template-engine.py create command-base my-command.md -i
```

---

## 📚 Core Concepts

### Module System Philosophy
The Claude module system is designed around these principles:
1. **Modularity**: Everything is a module with clear boundaries
2. **Consistency**: All modules follow the same standards
3. **Quality**: Automated checks prevent common issues
4. **Discoverability**: Easy to find and understand modules
5. **Maintainability**: Easy to update and improve

### Module Types

#### 1. Commands (`/commands/`)
Interactive commands that users can invoke
- Start with `/`
- Can have subcommands
- Return results to user

#### 2. Processes (`/processes/`)
Step-by-step procedures for common tasks
- Repeatable
- Clear prerequisites
- Defined outcomes

#### 3. Workflows (`/workflows/`)
Complex multi-phase operations
- Multiple decision points
- Role assignments
- Progress tracking

#### 4. Patterns (`/patterns/`)
Reusable solutions to common problems
- Problem-solution format
- Implementation guides
- Known uses

#### 5. Roles (`/roles/`)
Expert personas with specific capabilities
- Specialized knowledge
- Behavioral traits
- Consultation abilities

---

## 🛠️ Development Workflow

### 1. Planning Phase
Before creating a module:
- [ ] Check if similar module exists
- [ ] Determine appropriate module type
- [ ] Identify dependencies
- [ ] Plan module scope (< 200 lines)

### 2. Creation Phase
```bash
# Option 1: From template
python3 .claude/templates/template-engine.py create [template] [output]

# Option 2: From scratch (follow standards)
cp .claude/standards/module-definition-of-done.md my-checklist.md
```

### 3. Development Phase
Follow the Definition of Done:
- ✅ Valid YAML frontmatter
- ✅ Clear purpose statement
- ✅ Complete documentation
- ✅ Test scenarios included
- ✅ No circular dependencies
- ✅ Module size < 200 lines

### 4. Testing Phase
```bash
# Run module tests
.claude/tests/test-runner.sh

# Test specific module
python3 .claude/tests/module-tests/validation-tests.py my-module.md

# Check dependencies
python3 .claude/validators/dependency-depth-validator.py --visualize
```

### 5. Pre-commit Phase
Pre-commit hooks automatically check:
- Empty files
- Module size
- Naming conventions
- Dependencies
- Security issues
- YAML/Markdown syntax

### 6. Review Phase
Before committing:
- [ ] Run all tests
- [ ] Check module size
- [ ] Validate dependencies
- [ ] Review with checklist

---

## 🔧 Tools and Utilities

### Template Engine
```bash
# List available templates
python3 .claude/templates/template-engine.py list

# Show template variables
python3 .claude/templates/template-engine.py show command-base

# Create with specific variables
python3 .claude/templates/template-engine.py create process-base my-process.md \
  --var PROCESS_NAME=CodeReview \
  --var SCOPE=persistent
```

### Validators

#### Module Size Validator
```bash
# Check all modules
python3 .claude/validators/module-size-validator.py

# Get splitting suggestions
python3 .claude/validators/module-size-validator.py --suggest-split large-module.md

# Custom threshold
python3 .claude/validators/module-size-validator.py --max-lines 150
```

#### Dependency Validator
```bash
# Check dependency depth
python3 .claude/validators/dependency-depth-validator.py

# Visualize dependencies
python3 .claude/validators/dependency-depth-validator.py --visualize

# Get refactoring suggestions
python3 .claude/validators/dependency-depth-validator.py --suggest ModuleName
```

### Test Runner
```bash
# Run all tests
.claude/tests/test-runner.sh

# Run with custom directory
CLAUDE_DIR=/path/to/claude .claude/tests/test-runner.sh

# View latest report
cat .claude/tests/results/summary_*.md | tail -1
```

---

## 📋 Common Tasks

### Adding a New Command
1. Create command file:
   ```bash
   python3 .claude/templates/template-engine.py create command-base \
     .claude/commands/mycommand.md -i
   ```

2. Implement command logic
3. Add test scenarios
4. Test the command
5. Update help documentation

### Creating a Process
1. Identify process steps
2. Create process file:
   ```bash
   python3 .claude/templates/template-engine.py create process-base \
     .claude/processes/category/myprocess.md
   ```
3. Define prerequisites
4. Document each step
5. Add decision points
6. Include rollback procedures

### Fixing Module Issues

#### Module Too Large
```bash
# Get splitting suggestions
python3 .claude/validators/module-size-validator.py --suggest-split module.md

# Common solutions:
# 1. Extract examples to separate file
# 2. Split by functionality
# 3. Create submodules
```

#### Circular Dependencies
```bash
# Visualize to understand the cycle
python3 .claude/validators/dependency-depth-validator.py --visualize

# Common solutions:
# 1. Extract shared functionality
# 2. Use interfaces
# 3. Restructure dependencies
```

#### Missing Dependencies
```bash
# Find what's missing
.claude/hooks/validate-dependencies.sh module.md

# Solutions:
# 1. Create missing module
# 2. Update dependency reference
# 3. Remove unnecessary dependency
```

---

## 🚨 Troubleshooting

### Pre-commit Hook Failures

#### "Empty files detected"
- Add content to the file or remove it
- Minimum size is 10 bytes

#### "Module name not PascalCase"
- Update module name in frontmatter
- Example: `module: MyModule` not `module: my-module`

#### "Dependency not found"
- Check dependency name spelling
- Ensure dependency file exists
- Use correct module name (not filename)

### Test Failures

#### "YAML frontmatter invalid"
- Check for proper `---` delimiters
- Validate YAML syntax
- Ensure all required fields present

#### "Module size exceeded"
- Split the module
- Move examples elsewhere
- Extract common patterns

### Common Mistakes

1. **Using `_meta.md` instead of `.meta.md`**
   - Always use dot prefix

2. **Spaces in filenames**
   - Use hyphens instead: `my-module.md`

3. **Forgetting frontmatter**
   - All modules need YAML frontmatter

4. **Wrong scope values**
   - Must be: persistent, context, or temporary

5. **Deep dependency chains**
   - Keep depth ≤ 3 levels

---

## 🎓 Best Practices

### Module Design
1. **Single Responsibility**: Each module does one thing well
2. **Clear Naming**: Module name describes its purpose
3. **Complete Documentation**: Anyone can understand and use it
4. **Testable**: Include test scenarios
5. **Maintainable**: Easy to update

### Dependency Management
1. **Minimize Dependencies**: Only what's necessary
2. **Avoid Circular References**: Use interfaces if needed
3. **Document Dependencies**: Explain why each is needed
4. **Version Compatibility**: Note any version requirements

### Documentation Standards
1. **Purpose First**: Start with why the module exists
2. **Examples Required**: Show, don't just tell
3. **Error Handling**: Document failure modes
4. **Integration Guide**: How it works with other modules

### Testing Philosophy
1. **Test Early**: During development, not after
2. **Test Scenarios**: Real-world usage examples
3. **Edge Cases**: Document known limitations
4. **Automated Checks**: Let tools catch simple errors

---

## 🚀 Advanced Topics

### Custom Validators
Create your own validators:
```python
# .claude/validators/custom-validator.py
class CustomValidator:
    def validate(self, module_path):
        # Your validation logic
        pass
```

### Automation Integration
```yaml
# .github/workflows/claude-checks.yml
name: Claude Module Checks
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: |
          pip install pre-commit pyyaml
          pre-commit run --all-files
          .claude/tests/test-runner.sh
```

### Performance Optimization
1. **Module Loading**: Keep modules focused
2. **Dependency Resolution**: Minimize depth
3. **Caching**: Use for frequently accessed modules
4. **Lazy Loading**: Load only when needed

---

## 📚 Additional Resources

### Internal Documentation
- [Module Definition of Done](.claude/standards/module-definition-of-done.md)
- [Testing Guide](.claude/tests/test-runner.md)
- [Template Guide](.claude/templates/template-engine.py)

### Command Reference
- `/help` - Get help with Claude
- `/audit` - Run repository audit
- `/test` - Run module tests
- `/validate` - Validate specific module

### Getting Help
1. Check this guide first
2. Run module validation for specific errors
3. Review audit reports for patterns
4. Ask team members
5. Submit issue for tool problems

---

## 🎉 Welcome to the Team!

You're now ready to create high-quality modules for Claude. Remember:
- Quality over quantity
- When in doubt, validate
- Follow the standards
- Ask questions
- Continuous improvement

Happy module development! 🚀