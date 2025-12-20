---
name: Module Loader
module_type: core
scope: persistent
priority: critical
triggers: []
dependencies: ["core/principles.md", "manifest.md"]
conflicts: []
version: 1.0.0
---

# Module Loader

## Purpose
This module implements the logic for loading, unloading, and managing modules in Claude's memory. It enforces loading rules, manages conflicts, and ensures system stability.

## Module Loading Process

### 1. Load Request Handling
When a module load is requested (automatic or manual):

```
LoadRequest ’ Validation ’ ConflictCheck ’ DependencyResolution ’ Load ’ Verify
```

#### Validation Steps
1. Check module exists at specified path
2. Validate YAML frontmatter structure
3. Verify required fields present
4. Check module type is recognized
5. Validate scope and priority values

#### Conflict Resolution
1. Check manifest for conflicting modules
2. If conflict exists:
   - If comparison mode: Allow both temporarily
   - If normal mode: Prompt user for resolution
   - If one is locked: Locked module wins
3. Document conflict resolution

#### Dependency Loading
1. Parse module dependencies
2. Check circular dependencies
3. Load dependencies recursively
4. Track dependency chain

### 2. Context-Based Auto-Loading

The loader monitors conversation for context triggers:

```python
def check_context_triggers(message):
    for context in manifest.contexts:
        if any(keyword in message.lower() for keyword in context.keywords):
            load_modules(context.loads, scope=context.scope)
```

Priority for auto-loading:
1. Explicit user commands
2. Context triggers with highest priority
3. Context triggers by keyword match count
4. Default auto-load modules

### 3. Memory Management

#### Module Tracking
Each loaded module maintains:
- Load timestamp
- Last access time
- Access count
- Load source (auto/manual/dependency)
- Lock status

#### Unloading Rules
Modules are unloaded when:
1. Explicit unload command (unless locked)
2. Temporary module lifetime expires
3. Context switch makes module irrelevant
4. Memory limit reached (lowest priority first)
5. Conflicting module takes precedence

Never unload:
- Locked modules
- Critical priority modules
- Active dependencies
- Modules in current use

### 4. Module Commands Implementation

#### !load <module>
```
1. Parse module path (support partial matching)
2. Validate module exists
3. Check current load status
4. Execute load process
5. Report success/failure
```

#### !unload <module>
```
1. Check if module is locked
2. Check if module is critical
3. Check for dependent modules
4. Execute unload if allowed
5. Clean up resources
```

#### !list-modules
```
Format: [scope] priority | module-name | status | loaded-at
Example:
[persistent] critical | core/principles.md | active | start
[context] high | processes/testing/tdd.md | active | 5 min ago
[temporary] low | guides/tools/grep.md | expires-in-2 | 1 min ago
```

#### !compare <module1> <module2>
```
1. Temporarily override conflict rules
2. Load both modules
3. Create comparison view
4. Prompt for selection
5. Unload non-selected module
```

#### !lock/!unlock <module>
```
1. Verify module is loaded
2. Update lock status
3. Persist lock state
4. Prevent/allow future unloading
```

### 5. Reinforcement Protocol

Every N interactions (configurable):
```
1. Silent health check:
   - Verify critical modules loaded
   - Check for memory leaks
   - Validate module states
   
2. Context evaluation:
   - Analyze recent conversation
   - Determine if context shifted
   - Suggest module adjustments if needed
   
3. Cleanup:
   - Unload expired temporary modules
   - Reset access counters
   - Log statistics
```

### 6. Error Handling

#### Module Load Failures
- File not found ’ Suggest similar modules
- Invalid format ’ Report validation errors
- Dependency missing ’ Attempt to load dependencies
- Conflict detected ’ Prompt for resolution

#### System Errors
- Memory limit ’ Unload lowest priority modules
- Circular dependency ’ Reject load, report cycle
- Corrupted module ’ Quarantine and alert

### 7. Module State Persistence

Between conversations:
- Save list of manually loaded modules
- Preserve lock states
- Remember user preferences
- Track usage patterns

## Integration Points

### With Manifest
- Read module registry
- Update load statistics
- Check conflict rules
- Verify triggers

### With Principles
- Enforce ALWAYS/NEVER rules
- Validate module compliance
- Prevent principle violations

### With Other Modules
- Manage dependencies
- Handle integration points
- Coordinate shared resources

## Performance Optimization

### Caching
- Cache parsed module metadata
- Store compiled trigger patterns
- Remember conflict resolutions

### Lazy Loading
- Load module content only when accessed
- Parse frontmatter separately from content
- Defer dependency resolution when possible

## Monitoring & Metrics

Track and report:
- Module load frequency
- Conflict occurrence rate
- Average module lifetime
- Memory usage patterns
- Command usage statistics

These metrics inform:
- Default module selection
- Trigger optimization
- Memory limit adjustments
- System improvements

---
*The loader ensures reliable, efficient module management while maintaining system stability and user control.*