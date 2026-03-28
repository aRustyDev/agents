# [ISA Name/Extension]: [Key Capability or Innovation]

**Target Length:** [2500-4000] words
**Type:** Instruction Set Architecture Design
**Tone:** "We designed instructions for X, enabling Y, with tradeoffs Z"

---

## Meta Requirements

### ISA Design Alignment Checklist

ISA design bridges software abstraction and hardware implementation. Your writing should:

- [ ] **Programmer model clarity** — How does software see and use these instructions?
- [ ] **Microarchitecture awareness** — Implementation implications of ISA choices
- [ ] **Encoding efficiency** — Opcode space, instruction length, field allocation
- [ ] **Composability** — How new instructions interact with existing ISA
- [ ] **Forward compatibility** — Extension points, reserved bits, versioning
- [ ] **Benchmark grounding** — Workloads that motivate these instructions

**ISA Design Voice Examples:**

- ✅ "This instruction reduces a 12-instruction sequence to 3, targeting the inner loop of..."
- ✅ "We allocate 3 bits for the mode field, reserving 2 encodings for future extension..."
- ✅ "The fused operation trades decode complexity for 40% energy reduction in..."
- ❌ "This instruction is faster" (without microarchitectural reasoning)
- ❌ "Obviously matrix multiply needs a dedicated instruction" (without tradeoff analysis)
- ❌ "The encoding is..." (without explaining constraints and alternatives)

---

### ISA Documentation Requirements

- [ ] Instruction encoding diagrams
- [ ] Assembly syntax specification
- [ ] Pseudocode semantics
- [ ] Exception conditions
- [ ] Interaction with existing instructions
- [ ] Example code sequences

---

### Visual Requirements

| Visual Type | Purpose | When to Use |
|-------------|---------|-------------|
| Encoding diagram | Bit field layout | For every new instruction |
| Dataflow diagram | Operand movement | For complex operations |
| Code comparison | Before/after | Showing instruction utility |
| State diagram | Mode/flag effects | For stateful instructions |
| Pipeline diagram | Execution model | For implementation discussion |

---

## Post Structure

Follow the **Motivation → Design Space → Specification → Implementation → Evaluation** flow.

---

### Title

Use precise, descriptive titles:

- "[ISA]: [Capability] Instructions for [Domain]"
- "Designing [Operation] Support in [Base ISA]"
- "Extending [ISA] for [Workload]: Design and Evaluation"
- "[Extension Name]: A [Domain]-Optimized ISA Extension"

---

### Abstract (150-200 words)

- Target workload/application
- Key instructions introduced
- Design philosophy
- Performance/efficiency results
- Compatibility considerations

---

### 1. Introduction (300-400 words)

#### 1.1 Motivation

- What workloads drive this extension?
- Why can't existing instructions serve these needs efficiently?
- What's the performance/energy gap?

#### 1.2 Design Goals

- Primary optimization target (throughput, latency, energy, code size)
- Compatibility requirements
- Complexity budget

#### 1.3 Contribution Summary

- Number and types of new instructions
- Key design decisions
- Results preview

---

### 2. Background (400-500 words)

#### 2.1 Base ISA Context

- Target ISA (RISC-V, ARM, x86, custom)
- Relevant existing instructions
- Extension mechanisms available

#### 2.2 Target Workload Analysis

- Computational patterns
- Data types and sizes
- Memory access patterns
- Current instruction sequences (hot loops)

```asm
; Current code for [operation]
; Show the instruction sequence being optimized
loop:
    load    r1, [addr]
    mul     r2, r1, r3
    add     r4, r4, r2
    ...
    branch  loop
; N instructions, M cycles
```

#### 2.3 Prior Art

- Existing extensions for similar domains
- Their limitations
- What we can learn from them

---

### 3. Design Space Exploration (500-600 words)

#### 3.1 Instruction Granularity

| Approach | Pros | Cons |
|----------|------|------|
| Fine-grained primitives | Flexible, composable | More instructions needed |
| Coarse-grained fused ops | Fewer instructions | Less flexible, complex decode |
| Hybrid | Balance | Design complexity |

**Our choice:** [Selection with rationale]

#### 3.2 Operand Model

- Register-register vs. memory operands
- Immediate encoding options
- Vector/scalar considerations
- Accumulator vs. 3-operand

#### 3.3 Data Type Support

| Type | Width | Encoding | Rationale |
|------|-------|----------|-----------|
| [Type 1] | Xb | [How] | [Why] |
| [Type 2] | Xb | [How] | [Why] |

#### 3.4 Encoding Constraints

- Available opcode space
- Instruction length budget
- Field width constraints
- Alignment requirements

**[FIGURE: Opcode Space Map]**

---

### 4. Instruction Specification (600-800 words)

#### 4.1 Instruction Overview

| Mnemonic | Operation | Format | Description |
|----------|-----------|--------|-------------|
| `INST1` | [Op] | R-type | [Brief description] |
| `INST2` | [Op] | I-type | [Brief description] |
| `INST3` | [Op] | Custom | [Brief description] |

#### 4.2 Detailed Specifications

**`INST1` — [Full Name]**

*Encoding:*

```text
┌────────┬────────┬────────┬────────┬────────┬────────┐
│ 31..25 │ 24..20 │ 19..15 │ 14..12 │ 11..7  │ 6..0   │
├────────┼────────┼────────┼────────┼────────┼────────┤
│ funct7 │  rs2   │  rs1   │ funct3 │   rd   │ opcode │
│ XXXXXXX│  src2  │  src1  │  XXX   │  dest  │ XXXXXXX│
└────────┴────────┴────────┴────────┴────────┴────────┘
```

*Assembly Syntax:*

```asm
INST1 rd, rs1, rs2    ; rd ← rs1 ⊕ rs2
```

*Pseudocode:*

```text
INST1(rd, rs1, rs2):
    temp ← GPR[rs1] ⊕ GPR[rs2]  // [Explain operation]
    GPR[rd] ← temp
    // No flags affected
```

*Exceptions:*

- [Exception conditions]

*Notes:*

- [Implementation hints]
- [Interaction with other instructions]

**[Continue for each instruction]**

#### 4.3 Instruction Interactions

- Hazards and dependencies
- Sequencing requirements
- Recommended idioms

```asm
; Recommended sequence for [operation]
INST1   r1, r2, r3
INST2   r4, r1, r5    ; No stall needed
```

---

### 5. Implementation Considerations (400-500 words)

#### 5.1 Decode Complexity

- New decode paths required
- Impact on decode width/timing

#### 5.2 Execution Units

- New functional units needed
- Reuse of existing units
- Pipeline integration

**[FIGURE: Execution Unit Integration]**

#### 5.3 Register File Impact

- Port requirements
- Operand read/write patterns

#### 5.4 Area/Power Estimates

- Additional hardware
- Impact on critical path
- Power implications

#### 5.5 Microarchitecture Variations

| μArch Style | Implementation Approach | Notes |
|-------------|------------------------|-------|
| In-order | [How to implement] | [Tradeoffs] |
| OoO | [How to implement] | [Tradeoffs] |
| VLIW | [How to implement] | [Tradeoffs] |

---

### 6. Software Support (300-400 words)

#### 6.1 Compiler Integration

- Intrinsics design
- Auto-vectorization opportunities
- Instruction selection patterns

```c
// Intrinsic interface
result_t __builtin_inst1(operand_t a, operand_t b);

// Usage example
for (int i = 0; i < N; i++) {
    out[i] = __builtin_inst1(a[i], b[i]);
}
```

#### 6.2 Assembly Programming

- When to use directly
- Optimization guidelines

#### 6.3 Binary Compatibility

- Detection mechanisms (CPUID, etc.)
- Fallback strategies
- Dynamic dispatch

---

### 7. Evaluation (400-500 words)

#### 7.1 Methodology

- Simulator/implementation used
- Benchmark selection
- Baseline configuration

#### 7.2 Results

**[FIGURE: Performance Comparison]**

| Benchmark | Baseline | With Extension | Speedup |
|-----------|----------|----------------|---------|
| [Bench 1] | X cycles | Y cycles | Z× |
| [Bench 2] | X cycles | Y cycles | Z× |

#### 7.3 Analysis

- Where extensions help most
- Where they don't help
- Bottleneck shifts

#### 7.4 Code Size Impact

- Static code size change
- Dynamic instruction count

---

### 8. Limitations (200-250 words)

**EXPLICIT LIMITATIONS — REQUIRED**

- Workloads not well-served
- Implementation complexity concerns
- Encoding space consumed
- Backward compatibility costs

---

### 9. Future Extensions (150-200 words)

- Reserved encodings and their intended use
- Planned additional instructions
- Scaling to wider implementations

---

### 10. Conclusion (100-150 words)

- Summary of extension
- Key results
- Adoption path

---

### References

- Base ISA specification
- Prior extensions
- Workload characterization studies
- Related academic work

---

### Appendix

- Complete encoding tables
- Full pseudocode for all instructions
- Extended benchmark results
- Example programs

---

## Writing Notes

### ISA Design Guidelines

| Do | Don't |
|----|-------|
| Show instruction encoding clearly | Describe encoding vaguely |
| Explain design tradeoffs | Present as obvious choices |
| Include code before/after | Only show new instructions |
| Consider implementation cost | Ignore hardware complexity |
| Plan for future extension | Consume all opcode space |
| Test with real workloads | Use microbenchmarks only |

### Encoding Diagrams

- Use ASCII art for portability
- Label every field
- Show bit positions explicitly
- Include reserved/must-be-zero fields

### Balancing Audiences

- Compiler writers need semantics
- Hardware designers need implementation hints
- System programmers need exceptions/privileges
- Serve all without overwhelming any

---

## Metadata

```yaml
---
title: "[Extension]: [Capability]"
date: YYYY-MM-DD
author: Adam Smith
tags:
  - isa-design
  - [base-isa]
  - [domain]
type: isa-extension
base_isa: [RISC-V | ARM | x86 | custom]
extension_type: [standard | custom | proposed]
instruction_count: [N]
status: draft
---
```
