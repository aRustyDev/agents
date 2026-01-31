# High-Level Plan: <Chart-Name>

Planning date: <date>
Based on research: `.claude/plans/<chart>-chart/research-summary.md`

---

## Chart Metadata

| Property | Value |
|----------|-------|
| Chart Name | `<chart-name>` |
| Chart Type | application / library |
| Complexity | Simple / Standard / Complex / Operator |
| CI Handling | Full lint+install / Lint-only (exclude from install) |
| Extending Existing | Yes / No |
| Upstream Chart | <url or N/A> |

---

## Target Features

### MVP (Phase 1) - Required

- [ ] Chart.yaml with metadata and ArtifactHub annotations
- [ ] Deployment with container configuration
- [ ] Service (ClusterIP)
- [ ] ConfigMap for non-sensitive configuration
- [ ] Secret for sensitive configuration
- [ ] ServiceAccount (optional, configurable)
- [ ] NOTES.txt with access instructions
- [ ] README.md with basic documentation
- [ ] values.yaml with helm-docs comments

### Phase 2 - Health Probes

- [ ] Liveness probe configuration
- [ ] Readiness probe configuration
- [ ] Startup probe configuration (if slow-starting)

### Phase 3 - Resource Configuration

- [ ] Resource requests (CPU, memory)
- [ ] Resource limits (CPU, memory)

### Phase 4 - Security

- [ ] SecurityContext (runAsNonRoot, readOnlyRootFilesystem)
- [ ] PodSecurityContext (fsGroup, runAsUser)
- [ ] ServiceAccount with configurable options

### Phase 5+ - Optional Enhancements

- [ ] Ingress with TLS support
- [ ] PersistentVolumeClaim for data storage
- [ ] HorizontalPodAutoscaler
- [ ] PodDisruptionBudget
- [ ] ServiceMonitor (Prometheus)
- [ ] NetworkPolicy

---

## Dependencies

### Subcharts

| Subchart | Repository | Condition | Required |
|----------|------------|-----------|----------|
| postgresql | bitnami | `postgresql.enabled` | Yes / No |
| redis | bitnami | `redis.enabled` | No |

### External Services (Not Subcharts)

| Service | Configuration | Required |
|---------|---------------|----------|
| <service> | `externalDatabase.*` | Yes / No |

### CI Exclusions

If chart requires external services not provided by subcharts:
- Add to `ct-install.yaml` excluded-charts list
- Document in README

---

## Values Structure

```yaml
# Image configuration
image:
  repository: <org>/<image>
  tag: ""  # Defaults to appVersion
  pullPolicy: IfNotPresent

# Replica configuration
replicaCount: 1

# Service configuration
service:
  type: ClusterIP
  port: <port>

# Ingress (optional)
ingress:
  enabled: false
  className: ""
  hosts: []
  tls: []

# Resources
resources: {}
  # requests:
  #   cpu: 100m
  #   memory: 128Mi
  # limits:
  #   cpu: 500m
  #   memory: 512Mi

# Autoscaling (optional)
autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

# Pod Disruption Budget (optional)
pdb:
  enabled: false
  minAvailable: 1

# Application-specific configuration
<appName>:
  <config-section>
```

---

## Template Structure

| Template | Purpose | Conditional |
|----------|---------|-------------|
| `deployment.yaml` | Main workload | No |
| `service.yaml` | ClusterIP service | No |
| `configmap.yaml` | Non-sensitive config | If has config |
| `secret.yaml` | Sensitive config | If has secrets |
| `serviceaccount.yaml` | Service account | `serviceAccount.create` |
| `ingress.yaml` | External access | `ingress.enabled` |
| `hpa.yaml` | Autoscaling | `autoscaling.enabled` |
| `pdb.yaml` | Disruption budget | `pdb.enabled` |
| `pvc.yaml` | Persistent storage | `persistence.enabled` |

---

## Phase Summary

| Phase | Component | Branch Suffix | SemVer | Priority |
|-------|-----------|---------------|--------|----------|
| 1 | MVP | `-mvp` | 0.1.0 | Required |
| 2 | Probes | `-probes` | 0.1.1 | High |
| 3 | Resources | `-resources` | 0.1.2 | High |
| 4 | Security | `-security` | 0.1.3 | High |
| 5 | Ingress | `-ingress` | 0.2.0 | Medium |
| 6 | Persistence | `-persistence` | 0.3.0 | Medium |
| 7 | HPA | `-hpa` | 0.4.0 | Low |
| 8 | PDB | `-pdb` | 0.4.1 | Low |
| 9 | Monitoring | `-monitoring` | 0.5.0 | Low |

---

## Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| <risk1> | High/Medium/Low | <mitigation1> |
| <risk2> | High/Medium/Low | <mitigation2> |

---

## Open Questions

1. <question1>?
2. <question2>?

---

## Approval

- [ ] High-level plan reviewed
- [ ] Phase structure approved
- [ ] Values structure approved
- [ ] Ready to proceed with Phase 1

Approved by: <name/timestamp>
