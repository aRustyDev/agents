# Extend and Contribute Strategy

When an official or community Helm chart exists, you have options for how to proceed. This guide helps you decide when and how to extend existing charts while maintaining compatibility for contribution.

---

## When to Extend vs Create Independent

### Decision Matrix

| Scenario | Recommendation |
|----------|----------------|
| Official chart meets all needs | **Use as-is** - Don't reinvent |
| Official chart missing 1-2 features | **Extend** - Add features, contribute back |
| Official chart has different architecture | **Create Independent** - Your patterns may not fit |
| Official chart abandoned (>1yr no updates) | **Fork and Adopt** or **Create Independent** |
| Multiple community charts exist | **Compare** - Pick best to extend or create fresh |
| Chart is behind paywall/enterprise | **Create Independent** - Open-source alternative |

### Extension Suitability Checklist

Before extending, verify compatibility:

- [ ] Chart uses similar values structure you can maintain
- [ ] Chart's architecture aligns with your deployment model
- [ ] Maintainers are responsive (check recent issues/PRs)
- [ ] License permits modification and redistribution
- [ ] Your improvements would benefit the community

If 3+ items are unchecked, consider creating an independent chart.

---

## Fork vs Copy-Local Decision

When you decide to extend, choose your development approach:

### Decision Tree

```
Is chart in its own repository?
├─ Yes → Is repository small/focused?
│   ├─ Yes → FORK the repository
│   └─ No (large monorepo) → COPY locally
└─ No (chart in app's main repo) →
    Is monorepo manageable?
    ├─ Yes → FORK monorepo, work in charts/ dir
    └─ No → COPY locally
```

### Comparison

| Factor | Fork Repository | Copy Locally |
|--------|-----------------|--------------|
| **Best for** | Dedicated chart repos | Monorepos, learning |
| **Contribution path** | Direct PRs | Manual diff/patch |
| **Git history** | Preserved | Fresh start |
| **Upstream sync** | Easy (`git fetch upstream`) | Manual |
| **CI/CD** | May inherit or conflict | Your setup |
| **Complexity** | Two remotes | Single repo |
| **Independence** | Must coordinate | Can diverge freely |

### When to Fork

- Chart has its own repository
- You plan to contribute within weeks
- You want to stay synchronized with upstream
- Maintainers are active and welcoming

### When to Copy Locally

- Chart is in a large monorepo
- You need to iterate quickly first
- You may diverge significantly
- Contribution timeline is uncertain

### Hybrid Approach

For maximum flexibility:
1. **Copy locally** for rapid development
2. When improvements are stable:
   - Clone upstream temporarily
   - Apply your changes as commits
   - Create PR upstream
3. Continue local development for project-specific needs

---

## Compatibility Checklist

When extending a chart, maintain compatibility for easier upstream contribution:

### Values Schema

- [ ] Keep existing value names and paths
- [ ] Add new values, don't rename existing ones
- [ ] Preserve default values (or improve them)
- [ ] Document any breaking changes

### Templates

- [ ] Follow existing template patterns
- [ ] Use same helper function names
- [ ] Maintain label structure
- [ ] Keep resource naming conventions

### Dependencies

- [ ] Use same dependency repositories (e.g., Bitnami)
- [ ] Keep compatible version ranges
- [ ] Document any version changes

### Documentation

- [ ] Update README with new features
- [ ] Add examples for new configuration
- [ ] Note differences from upstream

---

## Contribution Workflow

### Step 1: Review Upstream

Before making changes:
```bash
# Clone/fork upstream
git clone https://github.com/<org>/charts.git
cd charts/<chart-name>

# Understand their patterns
cat values.yaml | head -50      # Values structure
ls templates/                    # Template organization
cat Chart.yaml                   # Dependencies, annotations
```

### Step 2: Identify Improvements

Common improvements to add:

| Feature | Benefit | Complexity |
|---------|---------|------------|
| HorizontalPodAutoscaler (HPA) | Auto-scaling | Low |
| PodDisruptionBudget (PDB) | Availability | Low |
| Startup probe | Slow-starting apps | Low |
| kubeVersion constraint | Compatibility checking | Low |
| Enhanced securityContext | Security hardening | Medium |
| Additional persistence options | Flexibility | Medium |
| Multi-port service | Complex apps | Medium |
| ServiceMonitor (Prometheus) | Observability | Medium |

### Step 3: Implement with Compatibility

Follow upstream conventions:
- Match their indentation and formatting
- Use their comment style
- Keep their values structure
- Add, don't replace

### Step 4: Document Differences

In your README or PR description:
```markdown
## Differences from Official Chart

### Added Features
- HorizontalPodAutoscaler support (`autoscaling.enabled`)
- PodDisruptionBudget support (`pdb.enabled`)
- Startup probe configuration (`startupProbe.*`)

### Changed Defaults
- None (all defaults preserved)

### Breaking Changes
- None
```

### Step 5: Prepare Contribution

**For direct PR:**
```bash
# Create feature branch in fork
git checkout -b feat/add-hpa-support

# Make changes, commit with conventional commit
git commit -m "feat: add HorizontalPodAutoscaler support"

# Push and create PR
git push origin feat/add-hpa-support
gh pr create --title "feat: add HPA support" --body "..."
```

**For copied chart (manual contribution):**
```bash
# Create diff of your changes
diff -r upstream-chart/ local-chart/ > improvements.patch

# Or create PR from scratch
git clone upstream-repo
cd upstream-repo/charts/<name>
# Apply changes manually, commit, PR
```

### Step 6: Communicate with Maintainers

Before large contributions:
1. Open an issue describing your planned improvements
2. Ask if they're interested and if approach aligns
3. Reference the issue in your PR

---

## Common Pitfalls

### Don't

- Rename existing values (breaks existing users)
- Remove features to "simplify"
- Change default behavior without documentation
- Skip testing with their CI configuration
- Force your conventions over theirs

### Do

- Add features as opt-in (disabled by default)
- Preserve backward compatibility
- Test with minimal values (defaults work)
- Follow their PR template and guidelines
- Be patient with review process

---

## Related References

- `research-strategy.md` - Finding existing charts
- `chart-complexity.md` - Classifying chart difficulty
- `planning-phase-workflow.md` - Structuring development
