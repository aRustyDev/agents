---
name: cicd-tekton-pipelines-dev
description: Develop and troubleshoot Tekton Pipelines on Kubernetes. Use when creating cloud-native CI/CD pipelines, debugging TaskRuns and PipelineRuns, understanding Tekton CRDs, or building reusable Tasks and Pipelines.
---

# Tekton Pipelines Development

Guide for developing, debugging, and optimizing Tekton Pipelines - the Kubernetes-native CI/CD framework.

## When to Use This Skill

- Creating Kubernetes-native CI/CD pipelines
- Debugging TaskRuns and PipelineRuns
- Building reusable Tasks for Tekton Hub
- Understanding Tekton CRDs and architecture
- Integrating with Tekton Triggers for GitOps
- Optimizing pipeline performance on Kubernetes

## Core Concepts

### Tekton Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Tekton Components                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Task ─────────► TaskRun                                   │
│     │                │                                       │
│     ├── Steps        ├── Pod (one per TaskRun)              │
│     ├── Params       ├── Containers (one per Step)          │
│     ├── Workspaces   └── Status                             │
│     └── Results                                              │
│                                                              │
│   Pipeline ─────► PipelineRun                               │
│     │                │                                       │
│     ├── Tasks        ├── TaskRuns (one per Task)            │
│     ├── Params       ├── PVCs (for Workspaces)              │
│     ├── Workspaces   └── Status                             │
│     └── Results                                              │
│                                                              │
│   Trigger ─────► EventListener ─────► PipelineRun           │
│     │                                                        │
│     ├── TriggerBinding (extract data)                       │
│     └── TriggerTemplate (create resources)                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Custom Resource Definitions (CRDs)

| CRD | Purpose |
|-----|---------|
| `Task` | Reusable unit of work (collection of steps) |
| `TaskRun` | Execution instance of a Task |
| `Pipeline` | Ordered collection of Tasks |
| `PipelineRun` | Execution instance of a Pipeline |
| `TriggerTemplate` | Template for creating PipelineRuns |
| `TriggerBinding` | Extracts data from events |
| `EventListener` | Listens for incoming events |

## Task Definition

### Basic Task

```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: build-push
spec:
  params:
    - name: image
      type: string
      description: Image name to build
    - name: dockerfile
      type: string
      default: ./Dockerfile

  workspaces:
    - name: source
      description: Source code workspace

  results:
    - name: image-digest
      description: Digest of the built image

  steps:
    - name: build
      image: gcr.io/kaniko-project/executor:latest
      args:
        - --dockerfile=$(params.dockerfile)
        - --destination=$(params.image)
        - --context=$(workspaces.source.path)
        - --digest-file=$(results.image-digest.path)
```

### Step Configuration

```yaml
steps:
  - name: run-tests
    image: node:20
    workingDir: $(workspaces.source.path)
    script: |
      #!/usr/bin/env bash
      set -ex
      npm ci
      npm test
    env:
      - name: NODE_ENV
        value: test
      - name: SECRET_KEY
        valueFrom:
          secretKeyRef:
            name: my-secret
            key: api-key
    resources:
      requests:
        memory: 512Mi
        cpu: 250m
      limits:
        memory: 1Gi
        cpu: 500m
```

### Sidecars

```yaml
spec:
  steps:
    - name: test
      image: node:20
      script: |
        npm test
  sidecars:
    - name: postgres
      image: postgres:15
      env:
        - name: POSTGRES_PASSWORD
          value: test
      readinessProbe:
        exec:
          command: ["pg_isready", "-U", "postgres"]
```

## Pipeline Definition

### Basic Pipeline

```yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: ci-pipeline
spec:
  params:
    - name: repo-url
      type: string
    - name: image-name
      type: string

  workspaces:
    - name: shared-workspace
    - name: docker-credentials

  tasks:
    - name: fetch-source
      taskRef:
        name: git-clone
      workspaces:
        - name: output
          workspace: shared-workspace
      params:
        - name: url
          value: $(params.repo-url)

    - name: run-tests
      taskRef:
        name: npm-test
      runAfter:
        - fetch-source
      workspaces:
        - name: source
          workspace: shared-workspace

    - name: build-push
      taskRef:
        name: kaniko
      runAfter:
        - run-tests
      workspaces:
        - name: source
          workspace: shared-workspace
        - name: dockerconfig
          workspace: docker-credentials
      params:
        - name: IMAGE
          value: $(params.image-name)
```

### Parallel Tasks

```yaml
spec:
  tasks:
    - name: fetch-source
      taskRef:
        name: git-clone

    # These run in parallel after fetch-source
    - name: lint
      taskRef:
        name: npm-lint
      runAfter:
        - fetch-source

    - name: unit-test
      taskRef:
        name: npm-test
      runAfter:
        - fetch-source

    - name: security-scan
      taskRef:
        name: trivy-scan
      runAfter:
        - fetch-source

    # This waits for all three
    - name: build
      taskRef:
        name: build-push
      runAfter:
        - lint
        - unit-test
        - security-scan
```

### Conditional Execution (when)

```yaml
tasks:
  - name: deploy-staging
    when:
      - input: $(params.environment)
        operator: in
        values: ["staging", "all"]
    taskRef:
      name: kubectl-deploy
    params:
      - name: namespace
        value: staging

  - name: deploy-production
    when:
      - input: $(params.environment)
        operator: in
        values: ["production"]
      - input: $(tasks.run-tests.results.passed)
        operator: in
        values: ["true"]
    taskRef:
      name: kubectl-deploy
    params:
      - name: namespace
        value: production
```

### Matrix (Fan-out)

```yaml
tasks:
  - name: test-matrix
    taskRef:
      name: npm-test
    matrix:
      params:
        - name: node-version
          value:
            - "18"
            - "20"
            - "22"
        - name: os
          value:
            - "linux"
            - "darwin"
```

## Running Pipelines

### TaskRun

```yaml
apiVersion: tekton.dev/v1
kind: TaskRun
metadata:
  generateName: build-push-run-
spec:
  taskRef:
    name: build-push
  params:
    - name: image
      value: gcr.io/myproject/myapp:latest
  workspaces:
    - name: source
      persistentVolumeClaim:
        claimName: source-pvc
```

### PipelineRun

```yaml
apiVersion: tekton.dev/v1
kind: PipelineRun
metadata:
  generateName: ci-pipeline-run-
spec:
  pipelineRef:
    name: ci-pipeline
  params:
    - name: repo-url
      value: https://github.com/org/repo
    - name: image-name
      value: gcr.io/myproject/myapp:v1
  workspaces:
    - name: shared-workspace
      volumeClaimTemplate:
        spec:
          accessModes:
            - ReadWriteOnce
          resources:
            requests:
              storage: 1Gi
    - name: docker-credentials
      secret:
        secretName: docker-credentials
```

### Using tkn CLI

```bash
# Start a PipelineRun
tkn pipeline start ci-pipeline \
  -p repo-url=https://github.com/org/repo \
  -p image-name=gcr.io/myproject/myapp:v1 \
  -w name=shared-workspace,claimName=my-pvc \
  --showlog

# Start a TaskRun
tkn task start build-push \
  -p image=myimage:latest \
  -w name=source,claimName=source-pvc \
  --showlog

# List runs
tkn pipelinerun list
tkn taskrun list

# View logs
tkn pipelinerun logs ci-pipeline-run-xyz -f
tkn taskrun logs build-push-run-abc -f

# Describe run
tkn pipelinerun describe ci-pipeline-run-xyz
```

## Tekton Triggers

### EventListener

```yaml
apiVersion: triggers.tekton.dev/v1beta1
kind: EventListener
metadata:
  name: github-listener
spec:
  serviceAccountName: tekton-triggers-sa
  triggers:
    - name: github-push
      interceptors:
        - ref:
            name: github
          params:
            - name: secretRef
              value:
                secretName: github-secret
                secretKey: secret
            - name: eventTypes
              value: ["push"]
      bindings:
        - ref: github-push-binding
      template:
        ref: ci-pipeline-template
```

### TriggerBinding

```yaml
apiVersion: triggers.tekton.dev/v1beta1
kind: TriggerBinding
metadata:
  name: github-push-binding
spec:
  params:
    - name: repo-url
      value: $(body.repository.clone_url)
    - name: revision
      value: $(body.head_commit.id)
    - name: branch
      value: $(body.ref)
```

### TriggerTemplate

```yaml
apiVersion: triggers.tekton.dev/v1beta1
kind: TriggerTemplate
metadata:
  name: ci-pipeline-template
spec:
  params:
    - name: repo-url
    - name: revision
    - name: branch

  resourcetemplates:
    - apiVersion: tekton.dev/v1
      kind: PipelineRun
      metadata:
        generateName: ci-pipeline-run-
      spec:
        pipelineRef:
          name: ci-pipeline
        params:
          - name: repo-url
            value: $(tt.params.repo-url)
          - name: revision
            value: $(tt.params.revision)
        workspaces:
          - name: shared-workspace
            volumeClaimTemplate:
              spec:
                accessModes:
                  - ReadWriteOnce
                resources:
                  requests:
                    storage: 1Gi
```

## Debugging

### View Logs

```bash
# PipelineRun logs
tkn pipelinerun logs <pipelinerun-name> -f

# TaskRun logs
tkn taskrun logs <taskrun-name> -f

# Specific task in pipeline
tkn pipelinerun logs <pipelinerun-name> -f --task=<task-name>

# Using kubectl
kubectl logs -l tekton.dev/pipelineRun=<pipelinerun-name> -c step-<step-name>
```

### Describe Resources

```bash
tkn pipelinerun describe <name>
tkn taskrun describe <name>

kubectl describe pipelinerun <name>
kubectl describe taskrun <name>
kubectl describe pod <taskrun-pod>
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Pod pending | No PVC or node resources | Check PVC binding and node capacity |
| Step fails | Script error or missing deps | Check step logs and image |
| Workspace empty | PVC not mounted correctly | Verify workspace binding |
| Timeout | Task exceeds timeout | Increase timeout in spec |
| Permission denied | RBAC issues | Check ServiceAccount permissions |

### Debug Step

Add a debug step to inspect workspace:

```yaml
steps:
  - name: debug
    image: busybox
    script: |
      echo "=== Workspace contents ==="
      ls -la $(workspaces.source.path)
      echo "=== Environment ==="
      env | sort
```

## Workspaces

### Types

```yaml
workspaces:
  # PersistentVolumeClaim
  - name: source
    persistentVolumeClaim:
      claimName: my-pvc

  # VolumeClaimTemplate (created per-run)
  - name: source
    volumeClaimTemplate:
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 1Gi

  # Secret
  - name: credentials
    secret:
      secretName: docker-credentials

  # ConfigMap
  - name: config
    configMap:
      name: my-config

  # EmptyDir (ephemeral)
  - name: temp
    emptyDir: {}
```

## Results and Parameters

### Passing Results Between Tasks

```yaml
# Task that produces result
spec:
  results:
    - name: image-digest
      description: The image digest

  steps:
    - name: build
      script: |
        echo -n "sha256:abc123" > $(results.image-digest.path)

# Pipeline consuming result
tasks:
  - name: build
    taskRef:
      name: build-image

  - name: deploy
    taskRef:
      name: deploy
    params:
      - name: digest
        value: $(tasks.build.results.image-digest)
```

## Tekton Hub Tasks

Use pre-built tasks from Tekton Hub:

```bash
# Install a task
tkn hub install task git-clone

# Search for tasks
tkn hub search build
```

Common Hub Tasks:

| Task | Purpose |
|------|---------|
| `git-clone` | Clone git repository |
| `kaniko` | Build container images |
| `buildah` | Build OCI images |
| `trivy-scanner` | Security scanning |
| `kubectl-actions` | Kubernetes deployments |
| `helm-upgrade` | Helm deployments |

## Performance Optimization

### Resource Requests

```yaml
steps:
  - name: build
    resources:
      requests:
        memory: 512Mi
        cpu: 250m
      limits:
        memory: 1Gi
        cpu: 1
```

### Workspace Caching

Use a shared PVC for caching:

```yaml
workspaces:
  - name: cache
    persistentVolumeClaim:
      claimName: build-cache-pvc
```

### Parallel Tasks

Design pipelines with parallel paths where possible.

### Timeout Configuration

```yaml
spec:
  timeouts:
    pipeline: 1h
    tasks: 30m
    finally: 15m
```

## Debugging Checklist

- [ ] Check PipelineRun/TaskRun status with `tkn describe`
- [ ] View pod logs with `kubectl logs`
- [ ] Verify workspace PVCs are bound
- [ ] Check RBAC permissions for ServiceAccount
- [ ] Verify image pull secrets if using private registries
- [ ] Check resource limits aren't too restrictive
- [ ] Verify parameters are passed correctly
- [ ] Check results paths are correct

## References

- [Tekton Documentation](https://tekton.dev/docs/)
- [Tekton Pipelines](https://tekton.dev/docs/pipelines/)
- [Tekton Triggers](https://tekton.dev/docs/triggers/)
- [Tekton Hub](https://hub.tekton.dev/)
- [tkn CLI Reference](https://tekton.dev/docs/cli/)
- [Tekton Catalog](https://github.com/tektoncd/catalog)
- [Getting Started Guide](https://tekton.dev/docs/getting-started/)
