# Tree-sitter KVConf TODO List

## Current Phase: Awaiting Phase 1 Implementation

### Phase 1: Foundation and Setup
- [ ] Create feature branch `feature/typed-values`
- [ ] Set up test infrastructure
- [ ] Create comprehensive test files for all supported formats
- [ ] Implement grammar refactoring foundation
- [ ] Generate baseline tests
- [ ] Complete Checkpoint 1.0 review

### Phase 2: String Types
- [ ] Implement double-quoted strings with interpolation
- [ ] Implement single-quoted strings (no interpolation)
- [ ] Update highlights.scm for string types
- [ ] Sync Zed extension with new node types
- [ ] Run performance benchmarks
- [ ] Complete Checkpoint 2.0 review

### Phase 3: Primitive Types
- [ ] Implement boolean value parsing (true/false)
- [ ] Implement integer value parsing
- [ ] Add error detection for invalid primitives
- [ ] Update highlights.scm and sync extension
- [ ] Complete Checkpoint 3.0 review

### Phase 4: Complex Types
- [ ] Implement URI/URL parsing (RFC 3986 compliant)
- [ ] Implement unquoted string catch-all
- [ ] Implement error node types
- [ ] Update highlights.scm and sync extension
- [ ] Complete Checkpoint 4.0 review

### Phase 5: Edge Cases and Polish
- [ ] Handle empty values
- [ ] Handle flexible spacing
- [ ] Handle special characters
- [ ] Optimize performance for large files
- [ ] Test against real-world configs
- [ ] Complete Checkpoint 5.0 review

### Phase 6: Future Enhancements (Deferred)
- [ ] Array support (optional, post-release)

### Phase 7: Documentation and Finalization
- [ ] Document all grammar rules
- [ ] Create visual diagrams
- [ ] Write Architecture Decision Records (ADRs)
- [ ] Complete integration testing in Zed
- [ ] Prepare release PR
- [ ] Complete Checkpoint 6.0 review

## Completed TODOs

### Phase 1 Preparation (Plan Development)
- [x] Create example content for each test file type
- [x] Add validation script to ensure all test files are valid
- [x] Add troubleshooting guide for common setup issues
- [x] Implement _spacing rule for flexible whitespace
- [x] Add automated regression test script
- [x] Implement test runner that validates parse trees
- [x] Add guide for writing effective corpus tests

### Phase 2 Preparation (Plan Development)
- [x] Implement _string_content to match non-special characters
- [x] Implement interpolation for ${VAR} syntax
- [x] Implement escape_sequence for \" \n etc
- [x] Add performance benchmark for string parsing
- [x] Add different colors for quote types
- [x] Create screenshot examples of expected highlighting

### Infrastructure
- [x] Update justfile with all required recipes
- [x] Split development plan into phases
- [x] Create project structure in .claude directory

## Decision Points

- [ ] Should .npmrc get its own dedicated extension or stay in kvconf?
- [ ] Should we support array syntax in initial release?
- [ ] What additional URI schemes should be supported beyond the common ones?

## Notes

- All checkpoints are MANDATORY - no skipping reviews
- Follow TDD approach - tests should fail first
- Commit after each passing test
- Performance target: < 100ms for 1000-line files