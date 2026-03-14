# [Circuit/Architecture Name]: [Key Innovation or Result]

**Target Length:** [2500-4000] words
**Type:** VLSI / Microelectronics Design
**Tone:** "We designed X, simulated Y, achieved Z"

---

## Meta Requirements

### VLSI Engineering Alignment Checklist

VLSI posts bridge architecture, circuit design, and physical implementation. Your writing should:

- [ ] **Multi-abstraction thinking** — Connect system-level to transistor-level decisions
- [ ] **PPA awareness** — Power, Performance, Area tradeoffs explicit throughout
- [ ] **Process-aware design** — Acknowledge technology node implications
- [ ] **Simulation rigor** — Clear methodology, corner coverage, Monte Carlo where appropriate
- [ ] **Physical design consideration** — Layout, routing, timing closure awareness
- [ ] **Reproducibility** — HDL snippets, tool flows, constraints shareable

**VLSI Voice Examples:**

- ✅ "At the 7nm node, leakage dominates, so we chose..."
- ✅ "Post-layout simulation showed 15% timing degradation due to routing congestion in..."
- ✅ "The architecture trades 20% area for 2x throughput by..."
- ❌ "The circuit works" (without PPA characterization)
- ❌ "Synthesis results show..." (without specifying constraints, corner)
- ❌ "Obviously this is better" (without quantitative comparison)

---

### Design Documentation Requirements

- [ ] RTL/schematic available (or described sufficiently)
- [ ] Synthesis constraints specified
- [ ] Target technology node stated
- [ ] PPA metrics with methodology
- [ ] Corner/PVT conditions for all measurements
- [ ] Comparison to prior art or baseline

---

### Visual Requirements

| Visual Type | Purpose | When to Use |
|-------------|---------|-------------|
| Block diagram | Architecture overview | Always for complex designs |
| Schematic | Circuit topology | For analog/custom digital |
| Timing diagram | Signal relationships | For sequential/pipelined designs |
| Layout screenshot | Physical implementation | For taped-out or physical designs |
| PPA charts | Performance comparison | For design space exploration |
| Waveforms | Simulation results | For verification/characterization |

---

## Post Structure

Follow the **Motivation → Architecture → Implementation → Characterization → Comparison** flow.

---

### Title

Use technically precise titles:

- "[Architecture]: A [Metric]-Optimized [Function] in [Node]"
- "Designing [X] for [Application]: [Key Result]"
- "[Technique] for [Problem]: [Improvement] Over [Baseline]"
- "A [Novel Aspect] [Circuit Type] Achieving [Metric]"

---

### Abstract (150-200 words)

- Problem/opportunity addressed
- Key architectural innovation
- Implementation technology
- Headline PPA results
- Comparison to state-of-art

---

### 1. Introduction (300-400 words)

#### 1.1 Motivation

- What application or problem drives this work?
- Why existing solutions are inadequate
- Target specifications

#### 1.2 Key Contributions

- Architectural innovation
- Circuit technique
- Design methodology
- Results achieved

#### 1.3 Scope

- Technology node
- Design abstraction level (RTL, gate, transistor)
- What's included/excluded

---

### 2. Background (400-500 words)

#### 2.1 Application Context

- System-level requirements
- Workload characteristics
- Interface constraints

#### 2.2 Prior Art

- Existing architectures/circuits
- Their limitations
- Gap your work addresses

#### 2.3 Technology Considerations

- Target process characteristics
- Relevant device parameters
- Design rules impacting architecture

---

### 3. Architecture (500-700 words)

#### 3.1 High-Level Architecture

**[FIGURE: Block Diagram]**

- Major functional blocks
- Data flow
- Control hierarchy

#### 3.2 Microarchitecture

**[FIGURE: Detailed Microarchitecture]**

- Pipeline stages (if applicable)
- Data path width and organization
- Memory hierarchy
- Control logic

#### 3.3 Key Design Decisions

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| [Decision 1] | A, B, C | B | [PPA reasoning] |
| [Decision 2] | X, Y | X | [Why] |

#### 3.4 Novelty

- What's new in this architecture
- Why it enables better PPA

---

### 4. Circuit Implementation (500-700 words)

#### 4.1 Critical Path Analysis

- Timing-critical components
- Optimization strategies

#### 4.2 Key Circuit Blocks

**[Block 1]: [Name]**

```verilog
// Key RTL or pseudocode
// Annotate design intent
module critical_block (
    input  logic [WIDTH-1:0] data_in,
    output logic [WIDTH-1:0] data_out
);
    // Implementation
endmodule
```

- Design choices and tradeoffs
- Why this implementation

**[Block 2]: [Continue for critical blocks]**

#### 4.3 Power Optimization

- Clock gating strategy
- Power domains (if applicable)
- Leakage mitigation

#### 4.4 Physical Design Considerations

- Floorplanning approach
- Critical routing
- Timing closure strategy

**[FIGURE: Floorplan or Layout]**

---

### 5. Verification (300-400 words)

#### 5.1 Functional Verification

- Testbench architecture
- Coverage metrics
- Corner cases tested

#### 5.2 Timing Verification

- STA methodology
- Corners analyzed
- Margin achieved

#### 5.3 Power Verification

- Simulation methodology
- Workload characterization
- Switching activity assumptions

---

### 6. Results (500-600 words)

#### 6.1 Implementation Summary

| Parameter | Value |
|-----------|-------|
| Technology | [Node] |
| Frequency | [X] GHz |
| Area | [X] mm² / [X] gates |
| Power | [X] mW @ [conditions] |
| Voltage | [X] V |

#### 6.2 Performance Characterization

**[FIGURE: Performance vs. Configuration]**

- Throughput analysis
- Latency breakdown
- Bottleneck identification

#### 6.3 Power Breakdown

**[FIGURE: Power Breakdown Pie Chart]**

| Component | Power (mW) | % Total |
|-----------|------------|---------|
| Datapath | X | X% |
| Control | X | X% |
| Memory | X | X% |
| Clock | X | X% |

#### 6.4 Area Breakdown

| Component | Area (μm²) | % Total |
|-----------|------------|---------|
| [Component 1] | X | X% |
| [Component 2] | X | X% |

#### 6.5 PVT Variation

| Corner | Frequency | Power |
|--------|-----------|-------|
| TT | X GHz | X mW |
| SS | X GHz | X mW |
| FF | X GHz | X mW |

---

### 7. Comparison (300-400 words)

#### 7.1 Comparison Methodology

- Normalization approach
- Fair comparison considerations
- Metric selection rationale

#### 7.2 State-of-Art Comparison

| Work | Tech | Freq | Power | Area | Efficiency |
|------|------|------|-------|------|------------|
| [Prior 1] | Xnm | X GHz | X mW | X mm² | X ops/mW |
| [Prior 2] | Xnm | X GHz | X mW | X mm² | X ops/mW |
| **This work** | Xnm | X GHz | X mW | X mm² | X ops/mW |

#### 7.3 Analysis

- Where this work excels
- Where it falls short
- Apples-to-apples considerations

---

### 8. Limitations (200-250 words)

**EXPLICIT LIMITATIONS — REQUIRED**

#### 8.1 Scope Limitations

- Simulation vs. silicon
- Technology portability unknown
- Workload coverage

#### 8.2 Methodology Limitations

- Tool limitations
- Model accuracy
- Verification coverage gaps

#### 8.3 Scalability Questions

- Scaling to larger designs
- Technology scaling implications

---

### 9. Future Work (150-200 words)

- Silicon implementation path
- Architecture extensions
- Technology migration
- Application expansion

---

### 10. Conclusion (100-150 words)

- Key contribution restated
- Headline results
- Significance

---

### References

- Prior art citations
- Tool documentation
- Technology references

---

### Appendix

- Complete RTL (or link to repository)
- Full synthesis reports
- Extended simulation results
- Constraint files

---

## Writing Notes

### VLSI Post Guidelines

| Do | Don't |
|----|-------|
| Specify technology node | Use vague "advanced node" |
| Report all PPA metrics | Cherry-pick favorable metrics |
| State simulation conditions | Assume reader knows corners |
| Compare fairly | Compare different nodes without normalization |
| Show area/power breakdown | Report only totals |
| Acknowledge limitations | Claim superiority without caveats |

### Abstraction Navigation

- Start at system level for context
- Dive to relevant detail level
- Surface back to implications
- Don't lose reader in either direction

### Tool Transparency

- Name synthesis/P&R tools and versions
- Specify constraint assumptions
- Note any tool-specific optimizations

---

## Metadata

```yaml
---
title: "[Design]: [Key Result]"
date: YYYY-MM-DD
author: Adam Smith
tags:
  - vlsi
  - [circuit-type]
  - [application]
type: vlsi-design
technology_node: [X]nm
design_type: [rtl | gate | transistor | full-custom]
metrics:
  frequency: [X] GHz
  power: [X] mW
  area: [X] mm²
status: draft
---
```
