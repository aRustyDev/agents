# Migration Strategies

Decision framework for choosing between incremental and full rewrite approaches.

## Strategy Comparison

| Strategy | When to Use | Risk Level | Timeline |
|----------|-------------|------------|----------|
| **Full Rewrite** | Small codebase, greenfield opportunity | High | Faster start, uncertain end |
| **Incremental** | Production system, risk-averse | Low | Slower start, predictable end |
| **Strangler Fig** | Large monolith, gradual replacement | Medium | Moderate timeline |
| **Parallel Run** | Critical systems, correctness required | Low | Longer (2x development) |

---

## Full Rewrite

### When to Choose

- Codebase < 10,000 lines
- No active users depending on current system
- Technical debt makes incremental changes costly
- Target language offers significant advantages
- Team has capacity for focused rewrite sprint

### Risks

- "Second system effect" - tendency to over-engineer
- Feature parity gaps discovered late
- Timeline estimation is difficult
- Team burnout on long rewrites

### Process

```
1. Document all features and behaviors (exhaustively)
2. Create comprehensive test suite for original
3. Implement core functionality first
4. Port tests to target language
5. Achieve feature parity
6. Parallel testing phase
7. Cutover
```

---

## Incremental Migration

### When to Choose

- Production system with active users
- Large codebase (> 50,000 lines)
- Cannot afford downtime or feature freeze
- Team needs to learn target language gradually
- Business requires continuous feature delivery

### Patterns

#### 1. Module-by-Module

```
Original System          Target System
┌─────────────────┐     ┌─────────────────┐
│ Module A (src)  │ ──► │ Module A (tgt)  │
├─────────────────┤     ├─────────────────┤
│ Module B (src)  │     │ Module B (src)  │ ← Still original
├─────────────────┤     ├─────────────────┤
│ Module C (src)  │     │ Module C (src)  │ ← Still original
└─────────────────┘     └─────────────────┘
```

#### 2. Layer-by-Layer

```
┌─────────────────┐     ┌─────────────────┐
│   UI Layer      │     │   UI Layer      │ ← Convert last
├─────────────────┤     ├─────────────────┤
│ Business Logic  │ ──► │ Business Logic  │ ← Convert second
├─────────────────┤     ├─────────────────┤
│   Data Layer    │     │   Data Layer    │ ← Convert first
└─────────────────┘     └─────────────────┘
```

#### 3. Feature-by-Feature

Convert one feature end-to-end, including all layers:

```
Feature A: [UI] → [Logic] → [Data]  ← Fully converted
Feature B: [UI] → [Logic] → [Data]  ← Still original
Feature C: [UI] → [Logic] → [Data]  ← Still original
```

### Interop Requirements

For incremental migration, you need a bridge between languages:

| Source → Target | Interop Options |
|-----------------|-----------------|
| TypeScript → Rust | WASM, NAPI, HTTP API |
| Python → Rust | PyO3, CFFI, HTTP API |
| Go → Rust | CGO + C ABI, gRPC, HTTP API |
| TypeScript → Python | HTTP API, message queue |
| TypeScript → Go | HTTP API, gRPC |

---

## Strangler Fig Pattern

Named after strangler fig trees that grow around host trees.

### When to Choose

- Large monolithic system
- Need to replace without disruption
- Can route traffic between old and new
- System has clear request/response boundaries

### Process

```
                    ┌──────────────────┐
                    │    Router/Proxy   │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │ New Service │  │ Old Monolith│  │ Old Monolith│
    │  (Target)   │  │  Feature B  │  │  Feature C  │
    └─────────────┘  └─────────────┘  └─────────────┘

1. Start with edge features
2. Route traffic to new implementation
3. Gradually expand coverage
4. Decommission old code as features migrate
```

### Success Criteria

- [ ] Clear routing layer in place
- [ ] Feature flags for traffic splitting
- [ ] Monitoring on both implementations
- [ ] Rollback capability

---

## Parallel Run

### When to Choose

- Financial systems, correctness-critical
- Need mathematical proof of equivalence
- Regulatory requirements for validation
- Cannot afford any regression

### Process

```
┌─────────────────┐
│     Input       │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│ Old   │ │ New   │
│System │ │System │
└───┬───┘ └───┬───┘
    │         │
    └────┬────┘
         ▼
┌─────────────────┐
│   Comparator    │ ← Detect differences
└─────────────────┘
```

### Comparison Strategies

1. **Shadow mode**: New system processes but results are discarded
2. **Diff mode**: Both results stored and compared offline
3. **Canary mode**: Small percentage of traffic uses new result
4. **Full parallel**: Both run, old result used, new result logged

---

## Decision Matrix

| Factor | Full Rewrite | Incremental | Strangler Fig | Parallel |
|--------|--------------|-------------|---------------|----------|
| Codebase size | Small | Any | Large | Any |
| Risk tolerance | High | Low | Medium | Very Low |
| Feature freeze OK? | Yes | No | No | No |
| Interop complexity | None | High | Medium | Low |
| Team size | Small | Any | Medium+ | Large |
| Timeline certainty | Low | High | Medium | High |

---

## Anti-Patterns

### 1. The "Big Bang"
Attempting to rewrite everything at once without incremental delivery.

### 2. Scope Creep
Adding features during migration instead of achieving parity first.

### 3. No Rollback Plan
Migrating without ability to revert to original system.

### 4. Skipping Tests
Migrating without comprehensive test coverage of original behavior.

### 5. Ignoring Interop Costs
Underestimating the complexity of running two systems simultaneously.

---

## Related

- `meta-convert-dev` - Core conversion patterns
- `convert-*` skills - Language-specific migrations
