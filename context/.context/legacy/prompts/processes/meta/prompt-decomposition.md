# Process: Prompt Decomposition

## Purpose
Systematically break down complex prompts into modular, reusable components for better maintainability and reusability.

## Trigger
- Large monolithic prompts (>500 lines)
- Prompts with multiple responsibilities
- Repeated patterns across prompts
- Difficulty in maintenance or updates

## Process Steps

### 1. Initial Analysis
```bash
# Analyze prompt structure
analyze_prompt_structure() {
  local PROMPT_FILE="$1"
  
  # Count sections
  local SECTION_COUNT=$(grep -c "^##" "$PROMPT_FILE")
  
  # Measure complexity
  local LINE_COUNT=$(wc -l < "$PROMPT_FILE")
  local WORD_COUNT=$(wc -w < "$PROMPT_FILE")
  
  # Identify patterns
  local PATTERN_COUNT=$(grep -E "(MUST|ALWAYS|NEVER)" "$PROMPT_FILE" | wc -l)
  
  echo "Structure Analysis:"
  echo "- Sections: $SECTION_COUNT"
  echo "- Lines: $LINE_COUNT"
  echo "- Words: $WORD_COUNT"
  echo "- Directive patterns: $PATTERN_COUNT"
}
```

### 2. Identify Components
1. **Core Purpose**: What is the primary function?
2. **Responsibilities**: List all things the prompt does
3. **Dependencies**: What knowledge/context is required?
4. **Patterns**: Repeated structures or phrases

### 3. Decomposition Strategy
```yaml
decomposition_approach:
  by_responsibility:
    - Extract each major responsibility
    - Create focused modules
    - Link through references
    
  by_pattern:
    - Identify repeated patterns
    - Extract to shared modules
    - Parameterize variations
    
  by_knowledge:
    - Separate domain knowledge
    - Create knowledge modules
    - Reference from prompts
```

### 4. Module Creation
For each identified component:
1. Create appropriate module file
2. Extract relevant content
3. Add metadata and documentation
4. Update references in original

### 5. Integration
```yaml
integration_methods:
  composition:
    description: Combine modules at runtime
    example: Load process A + pattern B + knowledge C
    
  inheritance:
    description: Extend base modules
    example: Base prompt + specializations
    
  reference:
    description: Link to external modules
    example: "See process: xyz.md"
```

## Success Criteria
- Original functionality preserved
- Improved maintainability
- Increased reusability
- Clear module boundaries
- Documented dependencies

## Examples

### Before: Monolithic Prompt
```markdown
You are an AI assistant that helps with coding...
[500+ lines of mixed instructions]
```

### After: Modular Structure
```markdown
role: coding-assistant
processes:
  - code-review
  - debugging
knowledge:
  - programming-languages
  - best-practices
```

## Tools and Helpers
- `analyze_prompt_structure()` - Initial analysis
- `extract_components()` - Component extraction
- `create_module()` - Module generation
- `update_references()` - Reference updating

## Related Processes
- determine-prompt-reusability.md
- modularization-opportunities.md