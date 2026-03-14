# [System/Algorithm Name]: [Key Innovation or Result]

**Target Length:** [2500-4000] words
**Type:** Neuromorphic Computing
**Tone:** "We designed brain-inspired [system], achieving [efficiency/capability] through [mechanism]"

---

## Meta Requirements

### Neuromorphic Alignment Checklist

Neuromorphic posts bridge neuroscience inspiration with computational implementation. Your writing should:

- [ ] **Biological grounding** — Clear about what neuroscience inspires vs. what's engineering abstraction
- [ ] **Computational model clarity** — Neuron model, learning rule, network topology explicit
- [ ] **Event-driven thinking** — Exploit temporal sparsity, asynchronous computation
- [ ] **Energy-aware design** — Power/energy metrics central, not afterthought
- [ ] **Learning mechanism specification** — How the system adapts (if applicable)
- [ ] **Comparison honesty** — Fair comparison to conventional approaches with appropriate metrics

**Neuromorphic Voice Examples:**

- ✅ "The LIF neuron model captures spike timing with 3 state variables, trading biological fidelity for..."
- ✅ "At 5% average spike rate, energy scales as O(spikes) not O(timesteps), yielding..."
- ✅ "STDP-inspired learning achieves 92% accuracy with 100× less training energy because..."
- ❌ "This is how the brain works" (overclaiming biological validity)
- ❌ "Obviously neuromorphic is more efficient" (without workload-specific analysis)
- ❌ "We use spiking neurons" (without specifying model, encoding, learning)

---

### Neuromorphic Documentation Requirements

- [ ] Neuron model equations
- [ ] Synapse/learning rule specification
- [ ] Network topology
- [ ] Encoding scheme (rate, temporal, population)
- [ ] Hardware/simulation platform
- [ ] Energy measurement methodology

---

### Visual Requirements

| Visual Type | Purpose | When to Use |
|-------------|---------|-------------|
| Network architecture | Topology overview | Always |
| Neuron model diagram | State variables and dynamics | For novel neuron models |
| Spike raster plot | Temporal activity | For spiking networks |
| Learning rule visualization | Weight update dynamics | For learning discussion |
| Energy breakdown | Power distribution | For efficiency claims |
| Accuracy vs. efficiency plot | Pareto analysis | For comparisons |

---

## Post Structure

Follow the **Inspiration → Model → Implementation → Learning → Evaluation** flow.

---

### Title

Use descriptive, specific titles:

- "[Model/System]: [Capability] with [Efficiency Metric]"
- "Neuromorphic [Application]: [Approach] for [Result]"
- "[Learning Rule] on [Hardware]: [Achievement]"
- "Event-Driven [Computation]: [Improvement] Over [Baseline]"

---

### Abstract (150-200 words)

- Application or computational challenge
- Neuromorphic approach and key innovations
- Implementation platform
- Efficiency and accuracy results
- Comparison to conventional approaches

---

### 1. Introduction (350-450 words)

#### 1.1 The Efficiency Challenge

- What computational problem are you addressing?
- Why are conventional approaches inefficient?
- What makes this suitable for neuromorphic?

#### 1.2 Biological Inspiration

- What neuroscience principle inspires this work?
- How faithful is the abstraction?
- What's preserved, what's simplified?

#### 1.3 Approach Overview

- Neuron model
- Learning mechanism (if any)
- Target platform

#### 1.4 Contributions

- Novel model or algorithm
- Implementation advances
- Evaluation methodology
- Efficiency results

---

### 2. Background (400-500 words)

#### 2.1 Neuroscience Foundations

- Relevant biological mechanisms
- What's known about the neural computation
- How this is abstracted for engineering

**[FIGURE: Biological vs. Engineered Abstraction]**

#### 2.2 Computational Models

**Neuron Models Landscape:**

| Model | Biological Fidelity | Computational Cost | Use Case |
|-------|--------------------|--------------------|----------|
| Rate-based | Low | Low | Dense computation |
| LIF | Medium | Medium | General spiking |
| Izhikevich | High | Medium | Biological realism |
| Hodgkin-Huxley | Very High | High | Detailed neuroscience |

#### 2.3 Prior Neuromorphic Systems

- Existing hardware/algorithms
- Their capabilities and limitations
- Gap your work addresses

---

### 3. Computational Model (500-700 words)

#### 3.1 Neuron Model

**[FIGURE: Neuron State Diagram]**

**Membrane Dynamics:**
$$
\tau_m \frac{dV}{dt} = -(V - V_{rest}) + R \cdot I_{syn}
$$

**Spike Generation:**
$$
\text{if } V > V_{th}: \text{emit spike, } V \leftarrow V_{reset}
$$

**State Variables:**

| Variable | Meaning | Dynamics |
|----------|---------|----------|
| V | Membrane potential | [Equation] |
| I_syn | Synaptic current | [Equation] |
| [Other] | [Meaning] | [Equation] |

#### 3.2 Synapse Model

**[FIGURE: Synapse Dynamics]**

- Weight representation (fixed, plastic)
- Synaptic dynamics (instantaneous, exponential, alpha)
- Delay modeling

#### 3.3 Network Topology

**[FIGURE: Network Architecture]**

- Layer structure
- Connectivity pattern (all-to-all, sparse, structured)
- Recurrence (feedforward, recurrent, reservoir)

```text
Network specification:
- Input layer: X neurons
- Hidden layer 1: Y neurons, [connectivity]
- Hidden layer 2: Z neurons, [connectivity]
- Output layer: W neurons
- Total synapses: N
```

#### 3.4 Information Encoding

| Encoding Scheme | Description | Advantages | Disadvantages |
|-----------------|-------------|------------|---------------|
| Rate coding | Spike count → value | Robust | Slow, less efficient |
| Temporal coding | Spike timing → value | Fast, efficient | Noise sensitive |
| Population coding | Ensemble activity | Redundancy | More neurons |

**Our choice:** [Selection with rationale]

---

### 4. Learning Mechanism (400-500 words)

*(If applicable — skip for inference-only systems)*

#### 4.1 Learning Rule

**[FIGURE: Learning Rule Visualization]**

**STDP-based / Gradient-based / Other:**
$$
\Delta w = f(\text{pre}, \text{post}, \ldots)
$$

- Biological inspiration
- Mathematical formulation
- Computational requirements

#### 4.2 Training Procedure

- Online vs. offline
- Supervised vs. unsupervised
- Error signal / reward signal
- Convergence properties

#### 4.3 Hardware Compatibility

- On-chip vs. off-chip learning
- Memory requirements
- Precision requirements

---

### 5. Implementation (400-500 words)

#### 5.1 Platform

**Hardware Implementation:**

| Platform | Neuron Model | Learning | Power | Notes |
|----------|--------------|----------|-------|-------|
| Intel Loihi | LIF variants | STDP, custom | ~1W | [Notes] |
| IBM TrueNorth | LIF | Off-chip | ~70mW | [Notes] |
| SpiNNaker | Flexible | Flexible | ~1W/chip | [Notes] |
| Custom ASIC | [Model] | [Rule] | [Power] | [Notes] |
| GPU simulation | Any | Any | ~200W | Baseline |

**Our platform:** [Selection with rationale]

#### 5.2 Implementation Details

- Neuron mapping
- Synapse storage
- Spike routing
- Timing/synchronization

#### 5.3 Optimization Techniques

- Quantization
- Pruning/sparsity
- Approximations
- Their impact on accuracy/efficiency

---

### 6. Evaluation (500-700 words)

#### 6.1 Methodology

**Benchmarks:**

| Task | Dataset | Metrics | Why Included |
|------|---------|---------|--------------|
| [Task 1] | [Dataset] | [Metrics] | [Relevance] |
| [Task 2] | [Dataset] | [Metrics] | [Relevance] |

**Baselines:**

- Conventional DNN (GPU)
- Other neuromorphic approaches
- Theoretical bounds

**Energy Measurement:**

- Methodology for power/energy measurement
- What's included (compute, memory, I/O)

#### 6.2 Accuracy Results

**[FIGURE: Accuracy Comparison]**

| Task | Conventional | This Work | Gap |
|------|--------------|-----------|-----|
| [Task 1] | X% | Y% | Z% |
| [Task 2] | X% | Y% | Z% |

#### 6.3 Efficiency Results

**[FIGURE: Energy Efficiency Comparison]**

| Metric | Conventional | This Work | Improvement |
|--------|--------------|-----------|-------------|
| Energy/inference | X mJ | Y μJ | Z× |
| Throughput | X inf/s | Y inf/s | Z× |
| Energy-delay product | X | Y | Z× |

#### 6.4 Sparsity Analysis

**[FIGURE: Spike Raster / Activity Analysis]**

- Average spike rate
- How sparsity translates to efficiency
- Activity distribution

#### 6.5 Scaling Analysis

- How efficiency scales with network size
- Break-even points with conventional
- Limiting factors

---

### 7. Discussion (300-400 words)

#### 7.1 When Neuromorphic Wins

- Task characteristics that favor this approach
- Efficiency crossover points
- Application sweet spots

#### 7.2 When It Doesn't

- Tasks where conventional is better
- Overheads that hurt small-scale
- Training challenges

#### 7.3 Biological Fidelity vs. Engineering

- What we preserved and why
- What we discarded and why
- Implications for neuroscience claims

---

### 8. Limitations (200-300 words)

**EXPLICIT LIMITATIONS — REQUIRED**

#### 8.1 Model Limitations

- Biological abstractions made
- Computational approximations
- Precision limitations

#### 8.2 Evaluation Limitations

- Benchmark representativeness
- Energy measurement caveats
- System-level costs not included

#### 8.3 Scaling Limitations

- Network size constraints
- Training scalability
- Hardware limitations

---

### 9. Future Directions (150-200 words)

- More complex tasks
- Hardware improvements
- Learning algorithm advances
- Biological inspiration extensions

---

### 10. Conclusion (100-150 words)

- Key contribution
- Efficiency achievement
- Broader implications

---

### References

- Neuroscience foundations
- Neuromorphic hardware
- Learning algorithms
- Benchmark sources

---

### Appendix

- Full neuron model parameters
- Training hyperparameters
- Extended benchmark results
- Hardware specifications

---

## Writing Notes

### Neuromorphic Post Guidelines

| Do | Don't |
|----|-------|
| Specify neuron model precisely | Vaguely say "spiking" |
| Report energy, not just power | Ignore temporal factors |
| Compare to appropriate baselines | Only compare to other neuromorphic |
| Acknowledge biological simplifications | Overclaim brain similarity |
| Show activity/sparsity metrics | Ignore spike statistics |
| Explain encoding scheme | Assume reader knows |

### Energy Measurement

- Specify what's included
- Report per-inference AND throughput
- Compare at same accuracy where possible
- Include system overhead if claiming system efficiency

### Biological Claims

- Be precise about what's bio-inspired vs. bio-realistic
- Cite neuroscience sources for inspiration
- Acknowledge simplifications explicitly
- Avoid "like the brain" without qualification

---

## Metadata

```yaml
---
title: "[System]: [Achievement]"
date: YYYY-MM-DD
author: Adam Smith
tags:
  - neuromorphic
  - [neuron-model]
  - [application]
type: neuromorphic-computing
neuron_model: [LIF | Izhikevich | rate | other]
learning_rule: [STDP | backprop | none | other]
platform: [Loihi | TrueNorth | simulation | custom]
status: draft
---
```
