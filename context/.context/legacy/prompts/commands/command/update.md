---
module: CommandUpdate  
scope: context
triggers: 
  - "/command update"
  - "update command"
  - "enhance command"
conflicts: []
dependencies:
  - _shared.md
  - process-detection.md
  - meta/slash-command-principles.md
priority: medium
---

# CommandUpdate - Enhance Existing Commands

## Purpose
Update and enhance existing slash commands while maintaining consistency and maximizing reusability.

## Overview
When you use `/project:command update`, I'll help you enhance an existing command following the slash command principles.

## Phase 1: Command Analysis 📊

1. **Identify the command**: "Which command would you like to update?"
2. **Read current implementation**: Load and analyze the existing command
3. **Understand current functionality**: Map what it currently does

### Analysis Checklist
- Current features and capabilities
- Existing process dependencies
- Known limitations or issues
- User feedback and requests
- Performance characteristics

## Phase 2: Enhancement Discovery 🔍

1. **Understand the need**: "What feature or change would you like to add?"
2. **Clarify requirements**:
   - Is this fixing a problem or adding new capability?
   - Who needs this enhancement?
   - What's the expected behavior?

### Enhancement Types
- **Bug Fixes**: Correcting existing functionality
- **Feature Additions**: New capabilities
- **Performance Improvements**: Speed or efficiency gains
- **Usability Enhancements**: Better user experience
- **Integration Updates**: New tool or API support

## Phase 3: Reusability Check ♻️

Following the slash command principles:

1. **Search for existing solutions**:
   ```
   !load processes/meta/determine-prompt-reusability.md
   ```
   - Can any existing process provide this feature?
   - Are there patterns we can compose?

2. **Evaluate extension options**:
   - **Unconditional**: If the feature benefits all users
   - **Conditional**: If it's context-specific

### Reusability Decision Tree
```
Does an existing process provide this feature?
├─ Yes → Can we use it as-is?
│   ├─ Yes → Document dependency
│   └─ No → Create conditional override
└─ No → Is this feature command-specific?
    ├─ Yes → Implement in command
    └─ No → Consider creating shared process
```

## Phase 4: Impact Analysis 📈

1. **Backward compatibility**: Will existing users be affected?
2. **Performance impact**: Does this add overhead?
3. **Dependency changes**: New requirements or tools?
4. **Documentation needs**: What needs updating?

### Compatibility Matrix
| Change Type | Risk Level | Mitigation Strategy |
|------------|------------|-------------------|
| New optional feature | Low | Add with default off |
| Modified behavior | Medium | Use feature flag |
| Breaking change | High | Major version bump |

## Phase 5: Implementation Plan 📝

1. **Minimal changes approach**: Modify only what's necessary
2. **Preserve existing patterns**: Maintain consistency
3. **Add proper gates**: For conditional features
4. **Update documentation**: Reflect all changes

### Implementation Checklist
- [ ] Identify files to modify
- [ ] Plan code changes
- [ ] Update tests
- [ ] Modify documentation
- [ ] Update version number
- [ ] Add changelog entry

## Phase 6: Update Execution 🛠️

I'll help you:
1. Add the new functionality
2. Update process dependencies
3. Document the enhancement
4. Ensure backward compatibility
5. Update version number

### Version Update Guidelines
- **Patch** (x.x.1): Bug fixes, documentation
- **Minor** (x.1.x): New features, backward compatible
- **Major** (1.x.x): Breaking changes

## Integration Points

This module works with:
- `process-detection.md` for finding reusable solutions
- `_shared.md` for update principles and patterns
- Original command file for modifications

## Best Practices

1. **Minimize disruption**: Keep changes focused
2. **Document thoroughly**: Explain what and why
3. **Test extensively**: Cover edge cases
4. **Communicate changes**: Update all affected docs

## Common Patterns

### Adding Optional Features
```yaml
# In command frontmatter
options:
  - name: --new-feature
    description: "Enable new functionality"
    default: false
    since: "1.2.0"
```

### Conditional Process Usage
```yaml
processes:
  - name: existing-process
    condition: "not options.custom-mode"
  - name: new-process
    condition: "options.custom-mode"
```

## Related Modules
- `init.md` - For creating new commands
- `review.md` - For analyzing update quality
- `process-detection.md` - For finding reusable components