# [Architecture Name]: [Key Innovation or Target]

**Target Length:** [3000-4500] words
**Type:** Computer Architecture Design
**Tone:** "We designed an architecture optimized for X, achieving Y through Z"

---

## Meta Requirements

### Computer Architecture Alignment Checklist

Architecture posts connect workload requirements to hardware organization. Your writing should:

- [ ] **Workload-driven design** — Every architectural choice motivated by workload characteristics
- [ ] **Quantitative reasoning** — Roofline analysis, bottleneck identification, Amdahl's law
- [ ] **Multi-level thinking** — ISA, microarchitecture, memory hierarchy, system integration
- [ ] **PPA tradeoff clarity** — Explicit about what you're trading for what
- [ ] **Scalability analysis** — How design choices affect scaling
- [ ] **Comparison rigor** — Fair baselines, normalized metrics, sensitivity analysis

**Architecture Voice Examples:**

- ✅ "Roofline analysis shows this workload is memory-bound at X ops/byte..."
- ✅ "We trade 2× area for 4× throughput by duplicating the [unit], justified by..."
- ✅ "The dataflow architecture eliminates 80% of register file accesses because..."
- ❌ "Our architecture is faster" (without workload context)
- ❌ "We added more compute units" (without bottleneck analysis)
- ❌ "Novel architecture for AI" (without specificity)

---

### Architecture Documentation Requirements

- [ ] Block diagram with data/control paths
- [ ] Memory hierarchy specification
- [ ] Execution model description
- [ ] Programming model
- [ ] Performance model/analysis
- [ ] Comparison to relevant alternatives

---

### Visual Requirements

| Visual Type | Purpose | When to Use |
|-------------|---------|-------------|
| Block diagram | Architecture overview | Always |
| Dataflow diagram | Data movement patterns | For dataflow/spatial architectures |
| Memory hierarchy | Cache/memory organization | For memory-intensive workloads |
| Pipeline diagram | Temporal execution | For pipelined designs |
| Roofline plot | Performance bounds | For performance analysis |
| Floorplan | Physical organization | For chip-level discussion |

---

## Post Structure

Follow the **Workload → Design Space → Architecture → Evaluation → Analysis** flow.

---

### Title

Use descriptive, specific titles:

- "[Name]: A [Adjective] Architecture for [Workload]"
- "Designing [Type] Accelerators for [Application]"
- "[Technique] in [Domain]: Architecture and Evaluation"
- "Beyond [Baseline]: [Innovation] for [Improvement]"

---

### Abstract (200-250 words)

- Target workload and its characteristics
- Key architectural innovation
- Design philosophy
- Headline performance results
- Comparison to state-of-art

---

### 1. Introduction (400-500 words)

#### 1.1 The Workload Challenge

- What computation are we accelerating?
- Why is it important?
- Why are general-purpose processors insufficient?

#### 1.2 Architectural Opportunity

- What workload characteristics enable specialization?
- What's the theoretical speedup potential?
- What makes this tractable?

#### 1.3 Key Insights

- 2-3 key observations driving the architecture
- Why these weren't exploited before

#### 1.4 Contributions

- Architectural innovations
- Implementation results
- Analytical contributions

---

### 2. Workload Analysis (500-600 words)

#### 2.1 Computational Patterns

**[FIGURE: Computation Graph / DAG]**

- Operations and their frequency
- Data dependencies
- Parallelism available (DLP, TLP, ILP)

#### 2.2 Data Movement Patterns

| Pattern | Frequency | Data Size | Locality |
|---------|-----------|-----------|----------|
| [Pattern 1] | X% | Y bytes | [High/Med/Low] |
| [Pattern 2] | X% | Y bytes | [High/Med/Low] |

- Memory access patterns
- Reuse opportunities
- Bandwidth requirements

#### 2.3 Roofline Analysis

**[FIGURE: Roofline Plot]**

- Operational intensity
- Compute vs. memory bound regions
- Target operating point

```text
Arithmetic Intensity = [X] ops/byte
Peak Compute = [Y] ops/sec
Required Bandwidth = [Z] bytes/sec
```

#### 2.4 Bottleneck Identification

- Where does time go on baseline architecture?
- What limits performance?
- What's the headroom?

---

### 3. Design Space Exploration (500-700 words)

#### 3.1 Architectural Alternatives

| Approach | Strengths | Weaknesses | When Appropriate |
|----------|-----------|------------|------------------|
| Temporal (CPU-like) | Flexible, programmable | Low efficiency | General workloads |
| Spatial (Systolic) | High efficiency | Fixed dataflow | Regular patterns |
| Dataflow | Explicit parallelism | Complex control | Irregular graphs |
| CGRA | Reconfigurable | Mapping overhead | Medium regularity |

#### 3.2 Key Design Decisions

**Decision 1: Execution Model**

- Options: [A, B, C]
- Our choice: [X]
- Rationale: [Why]

**Decision 2: Memory Architecture**

- Options: [A, B, C]
- Our choice: [X]
- Rationale: [Why]

**Decision 3: Interconnect Topology**

- Options: [A, B, C]
- Our choice: [X]
- Rationale: [Why]

#### 3.3 Design Philosophy

- What we're optimizing for (throughput, latency, efficiency, flexibility)
- What we're explicitly not optimizing
- The fundamental tradeoff we're making

---

### 4. Architecture Description (700-900 words)

#### 4.1 High-Level Organization

**[FIGURE: Architecture Block Diagram]**

- Major components and their roles
- Data paths
- Control hierarchy

#### 4.2 Compute Units

**[FIGURE: Compute Unit Detail]**

- Processing element design
- Datapath width
- Supported operations
- Local storage

```text
Compute Unit Specifications:
- [N] processing elements
- [M]-bit datapath
- [K] operations per cycle
- [L] KB local storage
```

#### 4.3 Memory Hierarchy

**[FIGURE: Memory Hierarchy]**

| Level | Size | Bandwidth | Latency | Purpose |
|-------|------|-----------|---------|---------|
| Registers | X KB | Y GB/s | Z cycles | [Purpose] |
| L1/Local | X KB | Y GB/s | Z cycles | [Purpose] |
| L2/Shared | X MB | Y GB/s | Z cycles | [Purpose] |
| DRAM | X GB | Y GB/s | Z cycles | [Purpose] |

- Banking and access patterns
- Coherence (if any)
- Prefetching strategy

#### 4.4 Interconnect

- Topology (mesh, ring, tree, crossbar)
- Bandwidth and latency
- Routing policy

#### 4.5 Control Architecture

- Instruction fetch/decode (if applicable)
- Synchronization mechanisms
- Exception handling

#### 4.6 System Integration

- Host interface
- Memory interface (HBM, DDR, etc.)
- I/O considerations

---

### 5. Execution Model (400-500 words)

#### 5.1 Programming Model

- How does software express computation?
- What's exposed to the programmer?
- What's handled by hardware/runtime?

```python
# Pseudocode showing programming model
# How workloads are mapped to architecture
```

#### 5.2 Mapping Strategy

- How workloads map to hardware
- Tiling and scheduling
- Resource allocation

**[FIGURE: Workload Mapping Example]**

#### 5.3 Dataflow and Synchronization

- Execution ordering
- Data dependencies
- Synchronization primitives

---

### 6. Implementation (400-500 words)

#### 6.1 RTL Implementation

- Design methodology
- Key implementation challenges
- Critical paths

#### 6.2 Physical Design

| Parameter | Value |
|-----------|-------|
| Technology | [Node] |
| Frequency | [X] GHz |
| Area | [X] mm² |
| Power | [X] W |
| Transistors | [X] B |

#### 6.3 Floorplan

**[FIGURE: Chip Floorplan]**

- Component placement
- Power delivery
- Thermal considerations

---

### 7. Evaluation (600-800 words)

#### 7.1 Methodology

**Simulation/Implementation:**

- Cycle-accurate simulation OR silicon measurements
- RTL simulation OR analytical model
- Tool flow

**Benchmarks:**

| Benchmark | Description | Size | Why Included |
|-----------|-------------|------|--------------|
| [Bench 1] | [What it does] | [Size] | [Relevance] |
| [Bench 2] | [What it does] | [Size] | [Relevance] |

**Baselines:**

- [Baseline 1]: Description
- [Baseline 2]: Description

#### 7.2 Performance Results

**[FIGURE: Performance Comparison Chart]**

| Benchmark | Baseline | This Work | Speedup |
|-----------|----------|-----------|---------|
| [Bench 1] | X ms | Y ms | Z× |
| [Bench 2] | X ms | Y ms | Z× |
| Geomean | — | — | Z× |

#### 7.3 Efficiency Results

**[FIGURE: Efficiency Comparison]**

| Metric | Baseline | This Work | Improvement |
|--------|----------|-----------|-------------|
| Perf/Watt | X | Y | Z× |
| Perf/mm² | X | Y | Z× |
| Perf/$ | X | Y | Z× |

#### 7.4 Sensitivity Analysis

**[FIGURE: Sensitivity Plots]**

- Sensitivity to memory bandwidth
- Sensitivity to compute scaling
- Sensitivity to workload characteristics

#### 7.5 Breakdown Analysis

**[FIGURE: Execution Time Breakdown]**

- Where does time go?
- What's the new bottleneck?
- Remaining optimization opportunities

---

### 8. Discussion (300-400 words)

#### 8.1 When This Architecture Excels

- Workload characteristics that favor this design
- Sweet spots

#### 8.2 When It Doesn't

- Workloads that don't benefit
- Architectural mismatches

#### 8.3 Comparison to Related Work

- How does this compare to [Alternative 1]?
- How does this compare to [Alternative 2]?
- What's genuinely new?

---

### 9. Limitations (200-300 words)

**EXPLICIT LIMITATIONS — REQUIRED**

#### 9.1 Scope Limitations

- Workloads not evaluated
- System-level effects not modeled

#### 9.2 Methodology Limitations

- Simulation vs. silicon gap
- Model accuracy

#### 9.3 Scalability Limitations

- How design choices affect scaling
- Technology dependencies

---

### 10. Future Directions (150-200 words)

- Next-generation improvements
- Scaling strategies
- New workload targets

---

### 11. Conclusion (100-150 words)

- Key contribution
- Headline results
- Significance

---

### References

- Related architectures
- Workload characterization studies
- Design methodology papers

---

### Appendix

- Detailed microarchitecture
- Full benchmark results
- Analytical models

---

## Writing Notes

### Architecture Post Guidelines

| Do | Don't |
|----|-------|
| Start with workload analysis | Start with architecture description |
| Quantify bottlenecks | Make vague claims |
| Show roofline/bounds | Ignore theoretical limits |
| Compare fairly (normalize PPA) | Cherry-pick metrics |
| Explain what you trade away | Claim all-around better |
| Sensitivity analysis | Single-point comparisons |

### Quantitative Rigor

- Every claim should have a number
- Show your analysis methodology
- Include confidence/error bounds
- Sensitivity analysis is essential

### Balancing Depth and Breadth

- Full architecture for overview
- Deep dive on key innovations
- Reference appendix for completeness
- Don't get lost in details

---

## Metadata

```yaml
---
title: "[Architecture]: [Innovation]"
date: YYYY-MM-DD
author: Adam Smith
tags:
  - computer-architecture
  - [domain]
  - [technique]
type: architecture-design
target_workload: [workload]
architecture_style: [spatial | temporal | dataflow | cgra | hybrid]
evaluation: [simulation | silicon | analytical]
status: draft
---
```
