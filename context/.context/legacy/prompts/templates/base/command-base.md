---
module: ${COMMAND_NAME}Command
scope: persistent
triggers: 
  - "/${COMMAND_NAME}"
  - "${COMMAND_NAME} command"
conflicts: []
dependencies: []
priority: high
command_type: ${COMMAND_TYPE}  # simple|complex|interactive
---

# Command: /${COMMAND_NAME}

${COMMAND_DESCRIPTION}

## Usage
```
/${COMMAND_NAME} ${USAGE_PATTERN}
```

## Arguments
${ARGUMENTS_LIST}

## Options
${OPTIONS_LIST}

## Subcommands
${SUBCOMMANDS_LIST}

## Examples

### Basic Usage
```bash
/${COMMAND_NAME} ${BASIC_EXAMPLE}
```
${BASIC_EXAMPLE_DESCRIPTION}

### Advanced Usage
```bash
/${COMMAND_NAME} ${ADVANCED_EXAMPLE}
```
${ADVANCED_EXAMPLE_DESCRIPTION}

## Workflow

1. **Initialization**
   ${INIT_STEPS}

2. **Validation**
   ${VALIDATION_STEPS}

3. **Execution**
   ${EXECUTION_STEPS}

4. **Output**
   ${OUTPUT_FORMAT}

## Error Handling

### Common Errors
${ERROR_LIST}

### Error Recovery
${RECOVERY_STEPS}

## Integration

### With Other Commands
${COMMAND_INTEGRATION}

### Automation
${AUTOMATION_EXAMPLES}

## Configuration

### Default Settings
```yaml
${DEFAULT_CONFIG}
```

### Customization
${CUSTOMIZATION_GUIDE}

## Performance Considerations
${PERFORMANCE_NOTES}

## Security Considerations
${SECURITY_NOTES}

## Related Commands
${RELATED_COMMANDS}

---

*Command implementation follows Claude command standards.*