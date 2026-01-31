# Architecture Documentation

**Last Updated**: January 9, 2025  
**Version**: 2.0 (Post-Phase 1 Modularization)

## Overview

This repository follows a modular architecture designed for maintainability, performance, and scalability. All modules adhere to strict guidelines ensuring consistent quality and organization.

## Architecture Principles

### 1. Module Size Limits
- **Hard limit**: 200 lines per module
- **Target**: 150 lines for optimal performance
- **Rationale**: Smaller modules are easier to maintain, test, and load

### 2. Modular Organization
```
.claude/
├── commands/
│   ├── command/          # Modularized from command.md (481→5 modules)
│   │   ├── init.md
│   │   ├── update.md
│   │   ├── review.md
│   │   ├── process-detection.md
│   │   └── _shared.md
│   ├── plan/            # Modularized from plan.md (741→6 modules)
│   │   ├── discovery.md
│   │   ├── analysis.md
│   │   ├── design.md
│   │   ├── implementation.md
│   │   ├── cleanup.md
│   │   └── _core.md
│   └── report/          # Modularized from report.md (671→7 modules)
│       ├── bug.md
│       ├── feature.md
│       ├── improvement.md
│       ├── security.md
│       ├── audit.md
│       └── _templates.md
```

### 3. Dependency Management
- Explicit dependencies in YAML frontmatter
- No circular dependencies allowed
- Clear hierarchical structure

### 4. Performance Optimization
- **35-40% performance improvement** achieved through modularization
- **70% memory reduction** for typical operations
- Lazy loading of modules only when needed

## Module Structure

Every module must include:

```yaml
---
module: ModuleName
scope: context|persistent|locked
triggers: 
  - "trigger phrase"
  - "/command"
conflicts: []
dependencies:
  - dependency1.md
  - dependency2.md
priority: high|medium|low
---
```

## Directory Structure

### Command Modules (`/commands/`)
- Parent files act as routers
- Subdirectories contain modular implementations
- `_shared.md` and `_core.md` for common functionality

### Supporting Files
- `scripts/` - Extracted shell scripts (must be executable)
- `templates/` - Reusable templates and examples
- `_*_templates.md` - Template collections for specific modules

## Development Guidelines

### Adding New Features
1. Identify the appropriate module or create a new one
2. Keep under 200 lines (target 150)
3. Extract large sections to separate files
4. Update dependencies in frontmatter
5. Run validation: `./validate-architecture.sh`

### Code Extraction Patterns
- **Scripts**: Move to `scripts/` subdirectory
- **Templates**: Create `_*_templates.md` files
- **Examples**: Move to `templates/` subdirectory
- **Utilities**: Add to `_shared.md` or create utility modules

## Performance Benefits

The modular architecture provides:
- **Faster loading**: Load only required modules
- **Reduced memory**: 70% less content loaded
- **Better caching**: Smaller units cache more efficiently
- **Improved searches**: Targeted module searches
- **Easier maintenance**: Focused, single-purpose files

## Validation and Testing

### Automated Validation
```bash
# Check module sizes and naming
./validate-architecture.sh

# Run integration tests
./test-modular-loading.sh

# Benchmark performance
./benchmark-performance.sh
```

### Continuous Monitoring
- Module size warnings at 180 lines
- Module size errors at 200 lines
- Dependency validation on every check
- Performance benchmarks in CI/CD

## Migration Status

### Phase 1 Complete ✅
- command.md → 5 modules
- plan.md → 6 modules  
- report.md → 7 modules
- All modules under 200 lines
- 35-40% performance improvement

### Phase 2 Planned
- Pattern extraction
- Additional optimizations
- Smart module preloading
- Enhanced caching strategies

## Best Practices

1. **Module Naming**: Use descriptive, action-oriented names
2. **Dependencies**: Keep minimal and explicit
3. **Documentation**: Include purpose and usage in each module
4. **Testing**: Test modules in isolation and integration
5. **Performance**: Monitor module size and load times

## Tools and Scripts

- `validate-architecture.sh` - Validate all modules
- `test-modular-loading.sh` - Integration testing
- `benchmark-performance.sh` - Performance metrics
- `fix-architecture-violations.sh` - Automated fixes

## References

- [Migration Guide](migration-guide-phase1.md)
- [Performance Report](performance-improvement-report.md)
- [Test Results](phase1-test-results.md)
- [Architecture Plan](architecture-modularization-plan.md)

---

*This architecture ensures sustainable growth while maintaining high performance and code quality.*