# [Project/Component]: [What You Built/Analyzed]

**Target Length:** [2000-3000] words
**Type:** Electrical Engineering / Hardware
**Tone:** "Here's the circuit/system, how it works, and what I learned"

---

## Meta Requirements

### Electrical Engineering Alignment Checklist

EE posts bridge theory and practical implementation. Your writing should:

- [ ] **Theory grounded** — Connect to fundamental principles (Ohm's law, KVL/KCL, signal theory)
- [ ] **Practical focus** — Real components, real constraints, real measurements
- [ ] **Safety conscious** — Highlight hazards, required precautions
- [ ] **Reproducible builds** — Bill of materials, schematics, PCB files if applicable
- [ ] **Test methodology** — How you verified the design works
- [ ] **Failure analysis** — What went wrong and why

**EE Voice Examples:**

- ✅ "The datasheet specifies X, but in practice I measured Y because..."
- ✅ "I chose this component because of its [parameter] characteristics..."
- ✅ "The simulation showed X, bench testing revealed Y..."
- ❌ "It just works" (without explaining why)
- ❌ "Trust the datasheet" (without validation)
- ❌ "I used this part because I had it lying around" (without analysis)

---

### Safety Section Requirements

- [ ] Voltage/current hazards identified
- [ ] Required safety equipment listed
- [ ] Safe handling procedures
- [ ] Failure mode considerations

---

### Documentation Requirements

- [ ] Complete schematic
- [ ] Bill of materials with part numbers
- [ ] PCB files or perfboard layout
- [ ] Firmware/code if applicable
- [ ] Test procedures

---

### Visual Requirements

| Visual Type | Purpose | When to Use |
|-------------|---------|-------------|
| Schematic | Circuit design | Always for circuit posts |
| PCB layout | Physical implementation | For PCB designs |
| Block diagram | System overview | Complex multi-stage systems |
| Oscilloscope captures | Signal analysis | When discussing waveforms |
| Photos | Build documentation | Assembly and debugging |
| Simulation plots | Design validation | Pre-build analysis |

---

## Post Structure

Follow the **Requirements → Design → Implementation → Testing → Results** flow.

---

### Title

Use descriptive, technical titles:

- "Designing a [Circuit Type]: [Key Specification]"
- "Building [Project]: From Schematic to PCB"
- "[Component] Driver Circuit: Design and Analysis"
- "Debugging [Issue] in [Circuit Type]"

---

### Abstract (100-150 words)

- What you built/analyzed
- Key specifications achieved
- Design approach
- Notable challenges or findings

---

### 1. Introduction (200-300 words)

#### 1.1 Project Overview

- What are you building?
- What problem does it solve?
- Target specifications

#### 1.2 Requirements

- Electrical specifications (voltage, current, frequency, etc.)
- Environmental constraints (temperature, size, power)
- Interface requirements
- Cost constraints

#### 1.3 Safety Considerations

**⚠️ SAFETY WARNING**
> [Identify any hazards: high voltage, high current, RF, etc.]
> [Required safety equipment]
> [Precautions for readers attempting to replicate]

---

### 2. Theory and Background (300-400 words)

#### 2.1 Fundamental Principles

- Relevant theory (amplifier classes, filter types, power conversion topology, etc.)
- Key equations

$$
V = IR \quad \text{(example equation formatting)}
$$

#### 2.2 Prior Art

- Existing solutions
- Reference designs
- Why a custom design was needed

#### 2.3 Design Approach

- Topology selection
- Why this approach over alternatives
- Key tradeoffs

---

### 3. Design (500-700 words)

#### 3.1 Block Diagram

```text
[ASCII block diagram or note for figure]
Input → Stage 1 → Stage 2 → Output
           ↓
        Feedback
```

**[FIGURE: System Block Diagram]**

#### 3.2 Circuit Design

**Stage 1: [Name/Function]**

- Component selection rationale
- Key calculations

```text
# Design calculation example
R = V / I = 5V / 10mA = 500Ω
# Selected 510Ω (standard value, +2%)
```

**[SCHEMATIC: Stage 1]**

**Stage 2: [Name/Function]**

- [Continue for each stage]

#### 3.3 Component Selection

| Component | Value | Part Number | Rationale |
|-----------|-------|-------------|-----------|
| R1 | 10kΩ | [Part #] | [Why this value/part] |
| C1 | 100nF | [Part #] | [Why this value/part] |
| U1 | [IC] | [Part #] | [Why this part] |

#### 3.4 Simulation

- Simulation tool used
- Key simulation results
- Predicted vs. specified performance

**[FIGURE: Simulation Results]**

---

### 4. Implementation (400-500 words)

#### 4.1 PCB Design (if applicable)

- Layer stackup
- Layout considerations
- Critical routing decisions

**[FIGURE: PCB Layout]**

#### 4.2 Bill of Materials

| Ref | Description | Part Number | Quantity | Source |
|-----|-------------|-------------|----------|--------|
| R1 | 10kΩ 1/4W 1% | [Part #] | 1 | [Supplier] |
| ... | ... | ... | ... | ... |

#### 4.3 Assembly Notes

- Build order recommendations
- Soldering considerations
- Common mistakes to avoid

**[PHOTO: Assembled Board]**

#### 4.4 Firmware/Software (if applicable)

```c
// Key code sections with comments
// Explain hardware-software interface
```

---

### 5. Testing and Measurement (400-500 words)

#### 5.1 Test Equipment

- Oscilloscope, DMM, signal generator, etc.
- Calibration notes if relevant

#### 5.2 Test Procedures

**Test 1: [What you're testing]**

- Setup
- Procedure
- Expected result

**Test 2: [Continue for each test]**

#### 5.3 Measurements

| Parameter | Specification | Simulated | Measured |
|-----------|--------------|-----------|----------|
| Gain | 20dB ± 1dB | 20.2dB | 19.8dB |
| Bandwidth | >1MHz | 1.2MHz | 1.1MHz |
| ... | ... | ... | ... |

**[FIGURE: Oscilloscope Capture]**

#### 5.4 Discrepancies

- Where measured differed from simulated
- Root cause analysis
- Corrections made

---

### 6. Results and Analysis (300-400 words)

#### 6.1 Performance Summary

- Specifications met or exceeded
- Specifications missed and by how much

#### 6.2 What Worked Well

- Design decisions that paid off
- Techniques to use again

#### 6.3 What Didn't Work

- Problems encountered
- Failures and debugging process
- Design mistakes

#### 6.4 Improvements for Rev 2

- What you'd change
- Optimizations identified
- Lessons to incorporate

---

### 7. Limitations (150-200 words)

**EXPLICIT LIMITATIONS — REQUIRED**

- Operating range restrictions
- Untested conditions
- Known issues not addressed
- Scaling limitations

---

### 8. Conclusion (100-150 words)

- Summary of what was achieved
- Key lessons learned
- Potential applications
- Future work

---

### Files and Resources

- Schematic (PDF and source files)
- PCB files (Gerbers, source)
- Bill of Materials (CSV/Excel)
- Firmware source code
- Datasheets for key components

---

### Appendix

- Detailed calculations
- Full schematics (if too large for main text)
- Additional oscilloscope captures
- Alternative approaches considered

---

## Writing Notes

### EE Post Guidelines

| Do | Don't |
|----|-------|
| Show calculations | Just state values |
| Include part numbers | Generic descriptions |
| Explain component choices | "I used what I had" |
| Compare sim to measured | Only show simulation |
| Document failures | Hide mistakes |
| Provide complete BOM | Incomplete parts list |

### Safety First

- Lead with hazards in relevant projects
- Include proper warnings
- Recommend appropriate PPE
- Consider reader skill level

### Reproducibility

- Complete enough for someone to replicate
- Note any custom parts or modifications
- Provide source files, not just PDFs
- Include purchasing links where helpful

### Theory Balance

- Enough theory to understand design choices
- Not a textbook—reference external resources for deep dives
- Connect theory to practical decisions

---

## Metadata

```yaml
---
title: "[Project]: [Key Achievement]"
date: YYYY-MM-DD
author: Adam Smith
tags:
  - electrical-engineering
  - [circuit-type]
  - [application]
type: hardware-project
specifications:
  voltage: [X]V
  current: [X]A
  frequency: [X]Hz
complexity: [beginner | intermediate | advanced]
safety_level: [low | medium | high]
status: draft
---
```
