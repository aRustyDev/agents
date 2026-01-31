---
name: role
description: Manage expert roles - activate, compose, and consult different personas
author: Claude
version: 1.0.0
---

# Command: /role

Manage expert roles for different contexts and expertise areas.

## Usage
```
/role <subcommand> [arguments] [options]
```

## Subcommands
- `activate` - Switch to a specific role
- `compose` - Create custom role by combining existing ones
- `list` - Show available roles
- `current` - Display current active role
- `consult` - Consult another role without switching
- `cache` - Manage role cache

## Subcommand: activate

Switch to a specific expert role.

### Usage
```
/role activate <role-name> [--context <context>]
```

### Options
- `--context` - Provide context for contextual capability loading

### Examples
```
/role activate senior-dev
/role activate ml-engineer --context "model optimization"
```

### Workflow
1. Load role definition
2. Check cache for performance
3. Load core identity
4. Load required capabilities
5. Load contextual capabilities based on context
6. Configure behaviors
7. Report activation status

## Subcommand: compose

Create a custom role by combining existing roles and capabilities.

### Usage
```
/role compose [--name <name>] [--interactive] [--quick]
```

### Options
- `--name` - Name for the custom role
- `--interactive` - Interactive wizard mode (default)
- `--quick` - Quick composition with CLI arguments

### Interactive Mode Workflow

1. **Base Role Selection**
   ```
   Select a base role to start from:
   1) senior-dev - Experienced developer with architectural focus
   2) junior-dev - Learning-focused early-career developer
   3) security-engineer - Security-first mindset
   4) ml-engineer - Data-driven ML practitioner
   5) None - Start from scratch
   ```

2. **Capability Addition**
   ```
   Would you like to add capabilities from other roles? (y/n)
   
   Available capabilities:
   - From security-engineer:
     □ vulnerability-assessment
     □ secure-architecture
     □ incident-response
   - From ml-engineer:
     □ data-analysis
     □ model-development
   
   Select capabilities to add (space to toggle, enter to confirm)
   ```

3. **Knowledge Integration**
   ```
   Select knowledge domains to include:
   □ software-engineering
   □ design-patterns
   □ security-fundamentals
   □ ml-algorithms
   □ distributed-systems
   ```

4. **Behavioral Customization**
   ```
   Customize behavior settings:
   
   Communication style:
   1) Mentoring (patient, educational)
   2) Direct (concise, to-the-point)
   3) Analytical (data-driven, detailed)
   
   Technical level:
   1) Adaptive (adjusts to audience)
   2) Expert (assumes deep knowledge)
   3) Beginner-friendly (explains everything)
   ```

5. **Review and Save**
   ```
   Review your custom role:
   
   Name: fullstack-security-dev
   Base: senior-dev
   Additional Capabilities:
   - vulnerability-assessment (from security-engineer)
   - secure-architecture (from security-engineer)
   Knowledge Domains:
   - software-engineering
   - security-fundamentals
   Behavior: Mentoring style, Adaptive level
   
   Save this role? (y/n)
   ```

### Quick Mode
```bash
/role compose --quick \
  --name "devops-security" \
  --base "senior-dev" \
  --add-capabilities "security-engineer:incident-response,ml-engineer:monitoring" \
  --knowledge "distributed-systems,security-fundamentals"
```

### Composition Rules

1. **Capability Merging**
   - No duplicate capabilities
   - Dependencies automatically included
   - Conflicts resolved by priority

2. **Knowledge Integration**
   - Union of all knowledge domains
   - Latest versions used
   - Circular dependencies prevented

3. **Behavior Resolution**
   - Base role behaviors as default
   - Explicit overrides take precedence
   - Consultation lists combined

### Output
Creates a new role file in `.claude/roles/custom/{name}.yaml`

## Subcommand: list

Show available roles with descriptions.

### Usage
```
/role list [--verbose] [--category <category>]
```

### Options
- `--verbose` - Show detailed information
- `--category` - Filter by category (base, custom, all)

### Example Output
```
Available Roles:

Base Roles:
- senior-dev (v1.0.0) - Experienced developer with architectural focus
- junior-dev (v1.0.0) - Learning-focused early-career developer
- security-engineer (v1.0.0) - Security-first mindset
- ml-engineer (v1.0.0) - Data-driven ML practitioner

Custom Roles:
- fullstack-security (v1.0.0) - Full-stack dev with security expertise
- devops-ml (v1.0.0) - DevOps engineer with ML deployment skills

Use '/role activate <name>' to switch roles
```

## Subcommand: current

Display information about the currently active role.

### Usage
```
/role current [--capabilities] [--knowledge]
```

### Options
- `--capabilities` - List loaded capabilities
- `--knowledge` - List loaded knowledge domains

### Example Output
```
Current Role: senior-dev
Version: 1.0.0
Active for: 15 minutes

Core Identity:
- Mindset: Systems thinking with focus on maintainability
- Communication: Patient mentor, explains complex concepts simply
- Decision: Data-driven with long-term impact focus

Loaded Capabilities:
✓ system-design (required)
✓ code-review (required)
✓ mentoring (contextual - triggered by "explain")

Can Consult: security-engineer, ml-engineer, architect
```

## Subcommand: consult

Consult another role without switching context.

### Usage
```
/role consult <role-name> "<question>"
```

### Examples
```
/role consult security-engineer "What are the security implications of this API design?"
/role consult ml-engineer "What's the best way to handle this data preprocessing?"
```

### Workflow
1. Save current role context
2. Load minimal consultant role
3. Process consultation question
4. Return response
5. Restore original role context

### Consultation Protocol
- Lightweight loading (core + relevant modules only)
- Question-specific context
- Preserves main role state
- Fast context switching (<100ms)

## Subcommand: cache

Manage the role caching system.

### Usage
```
/role cache <action> [options]
```

### Actions
- `status` - Show cache statistics
- `clear` - Clear role cache
- `warm` - Pre-cache specific roles
- `optimize` - Run cache optimization

### Examples
```
/role cache status
/role cache warm senior-dev security-engineer
/role cache optimize
```

### Cache Status Output
```
Role Cache Status:
Total Size: 12.5 MB
Hit Rate: 94%
Cached Roles: 8/12

Most Used:
1. senior-dev (45 loads, last: 2 min ago)
2. security-engineer (23 loads, last: 1 hour ago)
3. ml-engineer (18 loads, last: 3 hours ago)

Performance:
- Avg cached load: 47ms
- Avg fresh load: 512ms
- Speed improvement: 10.9x
```

## Performance Considerations

### Cache Strategy
- Frequently used roles kept in memory
- LRU eviction for space management
- Predictive pre-loading based on patterns

### Load Optimization
- Lazy loading for contextual capabilities
- Parallel loading where possible
- Incremental updates for version changes

## Integration with Other Commands

### Auto-activation
Some commands may suggest or auto-activate appropriate roles:
```
/assess security  # Suggests: "Would you like to activate security-engineer role?"
/review code      # Suggests: "Would you like to activate senior-dev role?"
```

### Role-Aware Commands
Commands can check current role and adjust behavior:
```python
current_role = get_current_role()
if current_role.has_capability('security-assessment'):
    # Enhanced security checks available
```

## Best Practices

1. **Choose Appropriate Roles**
   - Match role to task
   - Use specialized roles for domain tasks
   - Compose custom roles for unique needs

2. **Leverage Consultation**
   - Don't switch for quick questions
   - Use consultation for cross-domain insights
   - Maintain context with primary role

3. **Optimize Performance**
   - Pre-cache frequently used roles
   - Use role warmup at session start
   - Monitor cache hit rates

4. **Custom Role Management**
   - Name roles descriptively
   - Document custom role purposes
   - Regularly review and update