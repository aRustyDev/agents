# WASM Decision Report Style

Structured format for analyzing WebAssembly suitability in browser extensions.

## When to Use

Use this format when:
- Evaluating whether to add WASM to an extension
- Comparing WASM vs pure JavaScript implementation
- Documenting WASM integration decisions
- Reviewing existing WASM usage

## Format Template

```markdown
# WASM Suitability Analysis: [Feature/Component Name]

## Summary

| Aspect | Assessment |
|--------|------------|
| Recommendation | [Use WASM / Use JavaScript / Hybrid] |
| Confidence | [High / Medium / Low] |
| Priority | [Critical / Important / Nice-to-have] |

## Use Case

**Description**: [What the feature does]
**Performance requirement**: [Latency/throughput needs]
**Data size**: [Typical input/output sizes]

## Analysis

### Performance Comparison

| Metric | JavaScript | WASM | Improvement |
|--------|------------|------|-------------|
| Execution time | [X ms] | [Y ms] | [Z%] |
| Memory usage | [X MB] | [Y MB] | [Z%] |
| Startup time | [X ms] | [Y ms] | [Z%] |

### WASM Suitability Factors

| Factor | Score (1-5) | Notes |
|--------|-------------|-------|
| CPU-intensive computation | [1-5] | [Details] |
| Memory-efficient processing | [1-5] | [Details] |
| Existing Rust/C++ code | [1-5] | [Details] |
| Cryptographic operations | [1-5] | [Details] |
| Binary data processing | [1-5] | [Details] |

**Total Score**: [X/25] → [Strong/Moderate/Weak] WASM candidate

### JavaScript Preference Factors

| Factor | Score (1-5) | Notes |
|--------|-------------|-------|
| DOM manipulation | [1-5] | [Details] |
| Web API integration | [1-5] | [Details] |
| Simple logic | [1-5] | [Details] |
| Rapid iteration needed | [1-5] | [Details] |
| Team JavaScript expertise | [1-5] | [Details] |

**Total Score**: [X/25] → [Strong/Moderate/Weak] JavaScript candidate

## Cross-Browser Compatibility

| Browser | WASM Support | Notes |
|---------|--------------|-------|
| Chrome 88+ | ✓ Full | Service worker compatible |
| Firefox 109+ | ✓ Full | Event page compatible |
| Safari 15.4+ | ◐ Partial | No streaming from cross-origin |
| Edge 88+ | ✓ Full | Same as Chrome |

### Required Fallbacks

- [ ] Safari streaming fallback
- [ ] Older browser graceful degradation
- [ ] Feature detection implementation

## Memory Analysis

| Context | Limit | WASM Usage | Status |
|---------|-------|------------|--------|
| Service worker | 128MB | [X MB] | [✓ OK / ⚠ Close / ✗ Exceeds] |
| Content script | Tab memory | [X MB] | [✓ OK / ⚠ Close / ✗ Exceeds] |
| Popup | 128MB | [X MB] | [✓ OK / ⚠ Close / ✗ Exceeds] |

### Memory Mitigation

- [ ] Streaming processing for large data
- [ ] Explicit memory freeing
- [ ] Lazy loading strategy

## Bundle Size Impact

| Component | Size | Notes |
|-----------|------|-------|
| WASM binary | [X KB] | After optimization |
| JS bindings | [X KB] | wasm-bindgen output |
| Total impact | [X KB] | vs current bundle |
| % increase | [X%] | Acceptable / Concerning |

### Size Optimization Applied

- [ ] `opt-level = "s"` or `"z"`
- [ ] `lto = true`
- [ ] `wasm-opt` post-processing
- [ ] `wee_alloc` small allocator
- [ ] Dead code elimination

## Implementation Complexity

| Aspect | Effort | Notes |
|--------|--------|-------|
| Rust development | [Low/Med/High] | [Details] |
| Build pipeline | [Low/Med/High] | [Details] |
| Testing | [Low/Med/High] | [Details] |
| Debugging | [Low/Med/High] | [Details] |
| Maintenance | [Low/Med/High] | [Details] |

## Recommendation

### Decision: [Use WASM / Use JavaScript / Hybrid Approach]

**Rationale**:
[2-3 sentences explaining the decision based on the analysis above]

### If WASM Selected

**Implementation approach**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Risks and mitigations**:

| Risk | Mitigation |
|------|------------|
| [Risk 1] | [Mitigation] |
| [Risk 2] | [Mitigation] |

### If JavaScript Selected

**Optimization approaches**:
1. [Approach 1]
2. [Approach 2]

**When to reconsider WASM**:
- [Trigger 1]
- [Trigger 2]

## Appendix

### Benchmark Data

[Include actual benchmark results if available]

### References

- [Relevant documentation]
- [Similar implementations]
- [Performance studies]
```

## Quick Assessment

For quick decisions, use this abbreviated format:

```markdown
## WASM Quick Assessment: [Feature]

**Use case**: [One sentence]
**Data volume**: [Small/Medium/Large]
**Performance critical**: [Yes/No]
**Existing Rust code**: [Yes/No]

| Criterion | WASM | JS |
|-----------|:----:|:--:|
| CPU-bound | ✓ | |
| I/O-bound | | ✓ |
| DOM access | | ✓ |
| Crypto | ✓ | |
| Parsing | ✓ | |
| Simple logic | | ✓ |

**Verdict**: [WASM / JavaScript / Either]
**Confidence**: [High / Medium / Low]
```

## Decision Criteria Reference

### Strong WASM Indicators

- CPU-intensive: >10ms computation per operation
- Large data: >1MB processing at once
- Existing Rust/C++: Mature library available
- Cryptography: Security-sensitive operations
- Parsing: Complex binary formats

### Strong JavaScript Indicators

- DOM manipulation: Direct element interaction
- Simple logic: <1ms computation
- Web APIs: Heavy browser API usage
- Rapid changes: Frequent iteration expected
- Small data: <10KB typical operation

### Hybrid Approach Triggers

- Performance-critical core with DOM output
- Large codebase with hotspots
- Gradual migration path needed
