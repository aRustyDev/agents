# [Device/System Name]: [Key Capability or Innovation]

**Target Length:** [2500-4000] words
**Type:** Photonics / Optical Engineering
**Tone:** "We designed optical [component], achieving [performance] through [technique]"

---

## Meta Requirements

### Photonics Alignment Checklist

Photonics posts bridge optics fundamentals with practical device/system design. Your writing should:

- [ ] **Physics grounding** — Connect to Maxwell's equations, waveguide theory, nonlinear optics
- [ ] **Fabrication awareness** — Process constraints, tolerances, yield considerations
- [ ] **System context** — Where this device fits in larger photonic/opto-electronic systems
- [ ] **Characterization rigor** — Measurement methodology, uncertainty quantification
- [ ] **Loss budgeting** — Insertion loss, coupling loss, propagation loss accounting
- [ ] **Wavelength/bandwidth specification** — Operating range, dispersion, spectral characteristics

**Photonics Voice Examples:**

- ✅ "The MZI achieves 30dB extinction ratio with 0.5dB insertion loss at 1550nm..."
- ✅ "Fabrication tolerance analysis shows the device maintains <1dB excess loss for ±10nm width variation..."
- ✅ "We couple to fiber with 2dB loss using an inverse taper, limited by mode mismatch..."
- ❌ "The device works" (without optical characterization)
- ❌ "Light goes through the waveguide" (without loss/mode analysis)
- ❌ "Obviously this is better than electronics" (without fair comparison)

---

### Photonics Documentation Requirements

- [ ] Device geometry with dimensions
- [ ] Material system and layer stack
- [ ] Simulation methodology (FDTD, BPM, EME)
- [ ] Fabrication process summary
- [ ] Characterization setup
- [ ] Loss budget breakdown

---

### Visual Requirements

| Visual Type | Purpose | When to Use |
|-------------|---------|-------------|
| Device schematic | Geometry and dimensions | Always |
| Mode profile | Field distribution | For waveguides, resonators |
| Transmission spectra | Spectral response | For filters, resonators |
| Eye diagram | Signal quality | For data transmission |
| Fabrication cross-section | Layer structure | For process discussion |
| Measurement setup | Characterization methodology | For experimental results |

---

## Post Structure

Follow the **Application → Design → Simulation → Fabrication → Characterization** flow.

---

### Title

Use technically precise titles:

- "[Device Type]: [Performance] at [Wavelength/Application]"
- "Designing [Component] for [Application]"
- "[Material] [Device] with [Key Achievement]"
- "High-[Metric] [Device] Using [Technique]"

---

### Abstract (150-200 words)

- Application context
- Device type and innovation
- Key performance metrics
- Fabrication platform
- Comparison to state-of-art

---

### 1. Introduction (300-400 words)

#### 1.1 Application Motivation

- What system-level need does this device address?
- Why photonics for this application?
- Performance requirements

#### 1.2 Device Concept

- What type of device?
- Operating principle
- Key innovation or approach

#### 1.3 Target Specifications

| Parameter | Target | Rationale |
|-----------|--------|-----------|
| Wavelength | X nm | [Why] |
| Bandwidth | X nm/GHz | [Why] |
| Insertion Loss | < X dB | [Why] |
| Extinction Ratio | > X dB | [Why] |
| Footprint | < X μm² | [Why] |

---

### 2. Background (400-500 words)

#### 2.1 Physics Fundamentals

- Relevant optical principles
- Wave propagation, interference, resonance as applicable
- Key equations

$$
n_{eff} = \frac{\beta}{k_0}
$$

#### 2.2 Material Platform

- Material system (SOI, SiN, InP, LiNbO₃, etc.)
- Relevant optical properties
- Fabrication platform characteristics

| Property | Value | Notes |
|----------|-------|-------|
| Refractive index | X @ λ nm | [Core/cladding] |
| Propagation loss | X dB/cm | [Typical for platform] |
| Waveguide dimensions | X × Y nm | [Single-mode condition] |

#### 2.3 Prior Art

- Existing device implementations
- Their limitations
- Gap your work addresses

---

### 3. Device Design (500-700 words)

#### 3.1 Geometry

**[FIGURE: Device Schematic with Dimensions]**

```text
Key dimensions:
- Waveguide width: X nm
- Waveguide height: Y nm
- Device length: Z μm
- [Other critical dimensions]
```

#### 3.2 Operating Principle

**[FIGURE: Operating Principle Illustration]**

- How the device achieves its function
- Key physical mechanisms
- Design parameters and their effects

#### 3.3 Design Optimization

| Parameter | Range Explored | Optimal | Sensitivity |
|-----------|---------------|---------|-------------|
| [Param 1] | X - Y | Z | [High/Med/Low] |
| [Param 2] | X - Y | Z | [High/Med/Low] |

- Optimization methodology
- Tradeoffs navigated

#### 3.4 Mode Analysis

**[FIGURE: Mode Profile]**

- Supported modes
- Effective indices
- Confinement factors
- Mode overlap considerations

---

### 4. Simulation (400-500 words)

#### 4.1 Simulation Methodology

| Tool/Method | Purpose | Accuracy |
|-------------|---------|----------|
| [FDTD/Lumerical] | [What simulated] | [Notes] |
| [BPM] | [What simulated] | [Notes] |
| [EME] | [What simulated] | [Notes] |

- Mesh/grid resolution
- Boundary conditions
- Material models used

#### 4.2 Simulation Results

**[FIGURE: Simulated Transmission/Response]**

| Metric | Simulated | Target | Notes |
|--------|-----------|--------|-------|
| Insertion loss | X dB | < Y dB | [Met/Margin] |
| Extinction ratio | X dB | > Y dB | [Met/Margin] |
| Bandwidth | X nm | > Y nm | [Met/Margin] |

#### 4.3 Tolerance Analysis

**[FIGURE: Tolerance Sensitivity]**

- Width variation: ±X nm → Y dB variation
- Height variation: ±X nm → Y dB variation
- Refractive index variation: ±X → Y dB variation

#### 4.4 Simulation vs. Expected Fabrication

- Anticipated fabrication deviations
- Predicted performance with realistic tolerances

---

### 5. Fabrication (350-450 words)

#### 5.1 Fabrication Process

**[FIGURE: Process Flow / Cross-section]**

| Step | Process | Parameters |
|------|---------|------------|
| 1 | [Lithography] | [Details] |
| 2 | [Etching] | [Details] |
| 3 | [Deposition] | [Details] |

#### 5.2 Critical Process Steps

- Most challenging fabrication aspects
- How they're controlled
- Yield considerations

#### 5.3 Fabricated Device

**[FIGURE: SEM/Microscope Images]**

- Measured dimensions vs. design
- Observed defects or deviations
- Yield statistics (if available)

---

### 6. Characterization (500-600 words)

#### 6.1 Measurement Setup

**[FIGURE: Experimental Setup]**

- Light source (laser, ASE, tunable)
- Coupling method (grating, edge, fiber array)
- Detection (photodetector, OSA, power meter)
- Calibration procedure

#### 6.2 Loss Budget

| Loss Source | Value | Method |
|-------------|-------|--------|
| Fiber coupling (input) | X dB | [How measured] |
| Fiber coupling (output) | X dB | [How measured] |
| Propagation loss | X dB | [How measured] |
| Device insertion loss | X dB | [How measured] |
| **Total** | **X dB** | |

#### 6.3 Device Performance

**[FIGURE: Measured Transmission Spectra]**

| Metric | Measured | Simulated | Target |
|--------|----------|-----------|--------|
| Insertion loss | X dB | Y dB | < Z dB |
| Extinction ratio | X dB | Y dB | > Z dB |
| Bandwidth | X nm | Y nm | > Z nm |
| Center wavelength | X nm | Y nm | Z ± W nm |

#### 6.4 Statistical Analysis

- Device-to-device variation
- Wafer-level uniformity
- Yield

#### 6.5 Simulation vs. Measurement

**[FIGURE: Sim vs. Measured Comparison]**

- Where simulation matches
- Where it deviates and why
- Model improvements for future work

---

### 7. System Integration (300-400 words)

*(If applicable)*

#### 7.1 Packaging

- Fiber attachment
- Thermal management
- Electrical connections (if active)

#### 7.2 System Performance

- Device in system context
- System-level metrics
- Integration challenges

#### 7.3 Opto-Electronic Interface

*(For hybrid systems)*

- Driver/receiver electronics
- Bandwidth matching
- Power consumption

---

### 8. Discussion (300-400 words)

#### 8.1 Performance Analysis

- What limits current performance?
- How does this compare to state-of-art?

#### 8.2 Scaling and Integration

- How does this scale?
- Integration density considerations
- Thermal crosstalk

#### 8.3 Applications

- Where this device is applicable
- System-level value proposition

---

### 9. Limitations (200-250 words)

**EXPLICIT LIMITATIONS — REQUIRED**

- Wavelength/bandwidth limitations
- Temperature sensitivity
- Power handling limits
- Fabrication platform constraints
- Characterization limitations

---

### 10. Future Work (150-200 words)

- Performance improvements
- New applications
- Integration paths
- Alternative designs

---

### 11. Conclusion (100-150 words)

- Key achievement
- Performance summary
- Significance

---

### References

- Foundational photonics papers
- Prior device implementations
- Fabrication/material references
- Measurement methodology

---

### Appendix

- Detailed fabrication recipe
- Full simulation parameters
- Extended measurement data
- Device design files

---

## Writing Notes

### Photonics Post Guidelines

| Do | Don't |
|----|-------|
| Specify wavelength always | Assume reader knows wavelength |
| Include loss budget | Report only device loss |
| Show sim vs. measured | Only show simulation |
| Explain fabrication constraints | Ignore process limitations |
| Quantify tolerances | Assume perfect fabrication |
| Include mode profiles | Skip field distributions |

### Units and Conventions

- Loss in dB (not linear)
- Wavelength in nm (or μm for mid-IR)
- Dimensions in nm/μm as appropriate
- Bandwidth: nm for wavelength, GHz for frequency

### Figures

- Always include scale bars
- Label wavelengths on spectra
- Show simulation and measurement on same plot when comparing
- Mode profiles need axis labels and colorbar

---

## Metadata

```yaml
---
title: "[Device]: [Achievement]"
date: YYYY-MM-DD
author: Adam Smith
tags:
  - photonics
  - [device-type]
  - [application]
type: photonics-design
wavelength: [X] nm
platform: [SOI | SiN | InP | LiNbO3 | other]
status: [simulation | fabricated | characterized]
---
```
