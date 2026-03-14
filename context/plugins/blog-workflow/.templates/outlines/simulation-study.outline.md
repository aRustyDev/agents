# [Study Subject]: [Key Finding or Comparison]

**Target Length:** [2500-3500] words
**Type:** Simulation Study / Computational Experiment
**Tone:** "We simulated X under conditions Y, finding Z"

---

## Meta Requirements

### Simulation Study Alignment Checklist

Simulation studies derive insights through computational experiments. Your writing should:

- [ ] **Methodology transparency** — Simulator, parameters, assumptions fully specified
- [ ] **Validity discussion** — How well does simulation represent reality?
- [ ] **Statistical rigor** — Multiple runs, confidence intervals, significance testing
- [ ] **Parameter sensitivity** — How robust are conclusions to parameter choices?
- [ ] **Reproducibility** — Sufficient detail for replication
- [ ] **Scope clarity** — What questions can/cannot be answered by this simulation

**Simulation Study Voice Examples:**

- ✅ "We simulated 1000 configurations, varying [parameters] across [ranges]..."
- ✅ "Results are robust to ±20% variation in [parameter], but sensitive to [other parameter]..."
- ✅ "The simulation assumes [X], which may not hold in [conditions]..."
- ❌ "The simulation proves [X]" (simulations don't prove, they suggest)
- ❌ "We ran the experiment" (clarify it's simulation, not physical)
- ❌ "Results show [X]" (without statistical context)

---

### Simulation Documentation Requirements

- [ ] Simulator name and version
- [ ] Full parameter specification
- [ ] Random seed handling
- [ ] Number of runs per configuration
- [ ] Statistical analysis methods
- [ ] Code/configuration availability

---

### Visual Requirements

| Visual Type | Purpose | When to Use |
|-------------|---------|-------------|
| Parameter sweep plots | Show trends | For exploring parameter space |
| Comparison bar charts | Compare configurations | For discrete comparisons |
| Heatmaps | 2D parameter interaction | For interaction effects |
| Box plots | Show distribution | When variance matters |
| Pareto plots | Multi-objective tradeoffs | For design space exploration |
| Convergence plots | Simulation validity | For iterative simulations |

---

## Post Structure

Follow the **Question → Methodology → Results → Analysis → Implications** flow.

---

### Title

Use descriptive, specific titles:

- "[Subject] Performance: A Simulation Study of [Variables]"
- "Comparing [A] vs. [B]: Simulation Analysis of [Metric]"
- "Design Space Exploration of [System]: [Key Finding]"
- "How [Parameter] Affects [Outcome]: A Computational Study"

---

### Abstract (150-200 words)

- Research question or hypothesis
- Simulation approach and scope
- Key findings (quantified)
- Sensitivity/robustness summary
- Implications and limitations

---

### 1. Introduction (300-400 words)

#### 1.1 Research Question

- What specific question are we investigating?
- Why does this question matter?
- Why simulation (vs. analytical, experimental)?

#### 1.2 Hypothesis

- What do we expect to find?
- Why do we expect this?

```text
HYPOTHESIS: [Clear, testable statement]
```

#### 1.3 Scope

- What parameters/configurations explored
- What's explicitly out of scope
- Target audience for findings

---

### 2. Background (300-400 words)

#### 2.1 Domain Context

- System being simulated
- Key behaviors and parameters
- Why these are interesting to study

#### 2.2 Prior Work

- Previous simulation studies
- Analytical results
- Experimental data (if exists)
- Gap this study fills

#### 2.3 Why This Study

- What makes this study different or necessary
- New parameter space, new metrics, new comparisons

---

### 3. Simulation Methodology (500-700 words)

#### 3.1 Simulator Description

| Aspect | Specification |
|--------|---------------|
| Simulator | [Name, version, citation] |
| Model fidelity | [Cycle-accurate, functional, behavioral] |
| Abstraction level | [RTL, architecture, system] |
| Validation status | [Against what] |

- What the simulator models
- What it abstracts or ignores
- Known limitations

#### 3.2 System Configuration

**Baseline Configuration:**

```text
[Full parameter specification]
Parameter A: value
Parameter B: value
...
```

**[FIGURE: System Model Diagram]**

#### 3.3 Parameter Space

| Parameter | Baseline | Range Explored | Rationale |
|-----------|----------|---------------|-----------|
| [Param 1] | X | X₁ - X₂ | [Why this range] |
| [Param 2] | Y | Y₁ - Y₂ | [Why this range] |
| [Param 3] | Z | Z₁ - Z₂ | [Why this range] |

Total configurations: [N]

#### 3.4 Workloads/Inputs

| Workload | Description | Characteristics | Why Included |
|----------|-------------|-----------------|--------------|
| [WL 1] | [What it is] | [Key properties] | [Relevance] |
| [WL 2] | [What it is] | [Key properties] | [Relevance] |

#### 3.5 Metrics

| Metric | Definition | Unit | Why Important |
|--------|------------|------|---------------|
| [Metric 1] | [Precise definition] | [Unit] | [Relevance] |
| [Metric 2] | [Precise definition] | [Unit] | [Relevance] |

#### 3.6 Statistical Methodology

- Runs per configuration: [N]
- Random seed handling: [Strategy]
- Statistical tests: [Which tests, significance level]
- Confidence interval method: [Method]

```python
# Example: Statistical analysis code
def compute_confidence_interval(data, confidence=0.95):
    # [Implementation]
    pass
```

---

### 4. Results (600-800 words)

#### 4.1 Primary Results

**[FIGURE: Main Result Plot]**

| Configuration | Metric 1 | Metric 2 | Metric 3 |
|---------------|----------|----------|----------|
| Baseline | X ± σ | Y ± σ | Z ± σ |
| Config A | X ± σ | Y ± σ | Z ± σ |
| Config B | X ± σ | Y ± σ | Z ± σ |

Key observations:

- [Observation 1 with quantification]
- [Observation 2 with quantification]
- [Observation 3 with quantification]

#### 4.2 Parameter Sensitivity

**[FIGURE: Sensitivity Analysis Plots]**

**Parameter 1 sensitivity:**

- Range: X₁ to X₂
- Effect on Metric 1: [Relationship, magnitude]
- Significance: [p-value or CI]

**Parameter 2 sensitivity:**

- [Continue for each parameter]

#### 4.3 Interaction Effects

**[FIGURE: Interaction Heatmap]**

- [Parameter A × Parameter B] interaction: [Description]
- Implications for design: [What this means]

#### 4.4 Workload Variation

| Workload | Config A vs. Baseline | Config B vs. Baseline |
|----------|----------------------|----------------------|
| [WL 1] | +X% | +Y% |
| [WL 2] | +X% | +Y% |
| Variance | [How much variation] | [How much variation] |

---

### 5. Analysis (400-500 words)

#### 5.1 Hypothesis Evaluation

- Hypothesis: [Restate]
- Supported / Partially Supported / Refuted
- Key evidence

#### 5.2 Explaining the Results

- Why did we observe [finding 1]?
- Why did we observe [finding 2]?
- What mechanisms explain the results?

#### 5.3 Unexpected Findings

- What surprised us?
- Possible explanations
- Further investigation needed

#### 5.4 Design Implications

- What should designers do based on these results?
- When to use [configuration A] vs. [configuration B]
- Recommended parameter ranges

---

### 6. Validity and Robustness (300-400 words)

#### 6.1 Simulation Validity

**Internal validity:**

- Is the simulation self-consistent?
- Convergence verification
- Sanity checks

**External validity:**

- How well does this represent real systems?
- Validation against experimental data (if available)
- Known model limitations

#### 6.2 Robustness Analysis

| Assumption/Parameter | Tested Range | Results Robust? | Notes |
|---------------------|--------------|-----------------|-------|
| [Assumption 1] | [Range] | Yes/Partial/No | [Details] |
| [Assumption 2] | [Range] | Yes/Partial/No | [Details] |

#### 6.3 Threats to Validity

- Selection bias in workloads
- Parameter range limitations
- Simulator fidelity gaps
- Statistical power concerns

---

### 7. Limitations (200-250 words)

**EXPLICIT LIMITATIONS — REQUIRED**

#### 7.1 Simulation Limitations

- What the simulator doesn't model
- Fidelity limitations
- Abstraction effects

#### 7.2 Study Scope Limitations

- Parameter space not fully explored
- Workloads not representative of all use cases
- Configurations not tested

#### 7.3 Statistical Limitations

- Sample sizes
- Multiple comparison concerns
- Generalization bounds

---

### 8. Reproducibility (150-200 words)

#### 8.1 Code and Data Availability

```text
Repository: [URL]
Simulator: [Name, version, URL]
Scripts: [Description]
Data: [Availability]
```

#### 8.2 Reproduction Instructions

1. Install [simulator]
2. Clone [repository]
3. Run [command]
4. Results in [location]

---

### 9. Open Questions (150-200 words)

- What questions does this study raise?
- What would we study next?
- What would change our conclusions?

---

### 10. Conclusion (100-150 words)

- Key findings restated
- Implications for the field
- Confidence level in conclusions

---

### References

- Simulator documentation
- Prior simulation studies
- Analytical work
- Experimental validation sources

---

### Appendix

- Full parameter tables
- Extended results
- All statistical outputs
- Additional sensitivity analyses

---

## Writing Notes

### Simulation Study Guidelines

| Do | Don't |
|----|-------|
| Specify all parameters | Omit "obvious" defaults |
| Report confidence intervals | Report only point estimates |
| Discuss validity explicitly | Assume reader trusts simulation |
| Show sensitivity analysis | Present single-point results |
| Make data/code available | Keep reproduction details private |
| Distinguish simulation from reality | Say "proves" or "demonstrates" |

### Statistical Rigor

- Always report variance/confidence intervals
- Multiple runs are mandatory, not optional
- State significance thresholds before seeing results
- Be wary of multiple comparison effects
- Effect size matters, not just significance

### Reproducibility Checklist

- [ ] Simulator version pinned
- [ ] All parameters listed
- [ ] Random seeds documented
- [ ] Code available
- [ ] Data available
- [ ] Instructions tested

---

## Metadata

```yaml
---
title: "[Study Subject]: [Key Finding]"
date: YYYY-MM-DD
author: Adam Smith
tags:
  - simulation-study
  - [domain]
  - [technique]
type: simulation-study
simulator: [name]
configurations_tested: [N]
runs_per_config: [N]
code_available: [yes/no, URL]
data_available: [yes/no, URL]
status: draft
---
```
