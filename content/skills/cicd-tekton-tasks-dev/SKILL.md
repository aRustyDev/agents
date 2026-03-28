---
name: cicd-tekton-tasks-dev
description: Develop custom Tekton Tasks and reusable pipeline components. Use when creating Tasks for Tekton Hub, building ClusterTasks, designing parameterized Task libraries, or packaging Tekton components for distribution.
---

# Tekton Tasks Development

Guide for developing custom, reusable Tekton Tasks - the fundamental building blocks of Tekton Pipelines.

## When to Use This Skill

- Creating custom Tekton Tasks
- Building reusable Task libraries
- Publishing Tasks to Tekton Hub
- Designing parameterized, flexible Tasks
- Creating ClusterTasks for organization-wide use
- Understanding Task structure, steps, and sidecars

## Task Structure

### Basic Task Definition

```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: my-task
  labels:
    app.kubernetes.io/version: "1.0.0"
  annotations:
    tekton.dev/categories: Build
    tekton.dev/tags: docker, build
    tekton.dev/displayName: "Build Docker Image"
    tekton.dev/platforms: "linux/amd64,linux/arm64"
spec:
  description: >-
    This task builds a Docker image from source code.

  params:
    - name: IMAGE
      description: Name of the image to build
      type: string

    - name: DOCKERFILE
      description: Path to Dockerfile
      type: string
      default: ./Dockerfile

  workspaces:
    - name: source
      description: Source code workspace

  results:
    - name: IMAGE_DIGEST
      description: Digest of the built image
    - name: IMAGE_URL
      description: URL of the built image

  steps:
    - name: build
      image: gcr.io/kaniko-project/executor:latest
      args:
        - --dockerfile=$(params.DOCKERFILE)
        - --destination=$(params.IMAGE)
        - --context=$(workspaces.source.path)
        - --digest-file=$(results.IMAGE_DIGEST.path)
      script: |
        #!/usr/bin/env sh
        echo -n "$(params.IMAGE)" > $(results.IMAGE_URL.path)
```

## Parameters

### Parameter Types

```yaml
spec:
  params:
    # String parameter (default type)
    - name: message
      description: Message to display
      type: string
      default: "Hello World"

    # Array parameter
    - name: extra-args
      description: Additional arguments
      type: array
      default:
        - "--verbose"
        - "--debug"

    # Object parameter
    - name: config
      description: Configuration object
      type: object
      properties:
        url:
          type: string
        timeout:
          type: string
      default:
        url: "https://api.example.com"
        timeout: "30s"
```

### Using Parameters

```yaml
steps:
  - name: run
    image: alpine
    script: |
      echo "Message: $(params.message)"

  # Array parameters in args
  - name: build
    image: node:20
    args:
      - "npm"
      - "run"
      - "build"
      - "$(params.extra-args[*])"  # Expands array

  # Object parameter access
  - name: call-api
    image: curlimages/curl
    script: |
      curl -X GET "$(params.config.url)" \
           --max-time "$(params.config.timeout)"
```

### Parameter Validation

```yaml
params:
  - name: environment
    description: Target environment
    type: string
    enum:
      - development
      - staging
      - production

  - name: replicas
    description: Number of replicas
    type: string
    default: "1"
    # Pattern validation (via webhook/policy)
```

## Steps

### Step Definition

```yaml
steps:
  - name: step-name
    image: alpine:3.19
    imagePullPolicy: IfNotPresent

    # Working directory
    workingDir: $(workspaces.source.path)

    # Command and args
    command: ["/bin/sh"]
    args: ["-c", "echo hello"]

    # Or use script (preferred)
    script: |
      #!/usr/bin/env bash
      set -euo pipefail
      echo "Running in $(pwd)"

    # Environment variables
    env:
      - name: MY_VAR
        value: "static-value"
      - name: PARAM_VAR
        value: $(params.my-param)
      - name: SECRET_VAR
        valueFrom:
          secretKeyRef:
            name: my-secret
            key: api-key

    # Resource limits
    resources:
      requests:
        memory: 256Mi
        cpu: 100m
      limits:
        memory: 512Mi
        cpu: 500m

    # Security context
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000

    # Timeout
    timeout: 10m
```

### Multi-Step Tasks

```yaml
steps:
  - name: fetch-dependencies
    image: node:20
    workingDir: $(workspaces.source.path)
    script: |
      npm ci

  - name: run-tests
    image: node:20
    workingDir: $(workspaces.source.path)
    script: |
      npm test

  - name: build
    image: node:20
    workingDir: $(workspaces.source.path)
    script: |
      npm run build
```

### Step Ordering

Steps execute sequentially in order defined. Use separate Tasks with `runAfter` in Pipelines for parallel execution.

## Workspaces

### Workspace Types

```yaml
spec:
  workspaces:
    # Required workspace
    - name: source
      description: Source code
      mountPath: /workspace/source

    # Optional workspace
    - name: cache
      description: Build cache
      optional: true
      mountPath: /workspace/cache

    # Read-only workspace
    - name: config
      description: Configuration files
      readOnly: true
```

### Using Workspaces

```yaml
steps:
  - name: build
    image: node:20
    script: |
      cd $(workspaces.source.path)
      npm ci
      npm run build

      # Use optional workspace if available
      if [ -d "$(workspaces.cache.path)" ]; then
        cp -r node_modules $(workspaces.cache.path)/
      fi
```

## Results

### Defining Results

```yaml
spec:
  results:
    - name: digest
      description: Image digest
      type: string

    - name: urls
      description: List of URLs
      type: array

    - name: metadata
      description: Build metadata
      type: object
      properties:
        version:
          type: string
        timestamp:
          type: string
```

### Writing Results

```yaml
steps:
  - name: build
    image: alpine
    script: |
      # String result
      echo -n "sha256:abc123" > $(results.digest.path)

      # Array result (JSON)
      echo '["http://url1", "http://url2"]' > $(results.urls.path)

      # Object result (JSON)
      cat > $(results.metadata.path) << EOF
      {
        "version": "1.0.0",
        "timestamp": "$(date -Iseconds)"
      }
      EOF
```

### Result Size Limits

Results are limited to 4KB. For larger data, use workspaces or external storage.

## Sidecars

### Database Sidecar

```yaml
spec:
  sidecars:
    - name: postgres
      image: postgres:15
      env:
        - name: POSTGRES_DB
          value: testdb
        - name: POSTGRES_USER
          value: test
        - name: POSTGRES_PASSWORD
          value: test
      readinessProbe:
        exec:
          command: ["pg_isready", "-U", "postgres"]
        initialDelaySeconds: 5
        periodSeconds: 2

  steps:
    - name: test
      image: node:20
      env:
        - name: DATABASE_URL
          value: postgres://test:test@localhost:5432/testdb
      script: |
        npm test
```

### Service Mesh Sidecar

```yaml
sidecars:
  - name: nginx
    image: nginx:alpine
    ports:
      - containerPort: 8080
    volumeMounts:
      - name: config
        mountPath: /etc/nginx/conf.d

  volumes:
    - name: config
      configMap:
        name: nginx-config
```

## Volume Mounts

### EmptyDir Volumes

```yaml
spec:
  stepTemplate:
    volumeMounts:
      - name: temp
        mountPath: /tmp/shared

  volumes:
    - name: temp
      emptyDir: {}

  steps:
    - name: generate
      image: alpine
      script: |
        echo "data" > /tmp/shared/file.txt

    - name: consume
      image: alpine
      script: |
        cat /tmp/shared/file.txt
```

### Secret Volumes

```yaml
spec:
  volumes:
    - name: docker-config
      secret:
        secretName: docker-credentials

  steps:
    - name: push
      image: gcr.io/kaniko-project/executor
      volumeMounts:
        - name: docker-config
          mountPath: /kaniko/.docker
```

## StepTemplate

Apply common configuration to all steps:

```yaml
spec:
  stepTemplate:
    image: node:20
    workingDir: $(workspaces.source.path)
    env:
      - name: NODE_ENV
        value: production
    resources:
      requests:
        memory: 256Mi

  steps:
    - name: install
      script: npm ci

    - name: build
      script: npm run build

    - name: test
      script: npm test
```

## ClusterTasks

Organization-wide reusable Tasks:

```yaml
apiVersion: tekton.dev/v1beta1
kind: ClusterTask
metadata:
  name: organization-build
spec:
  params:
    - name: image
      type: string
  steps:
    - name: build
      image: gcr.io/kaniko-project/executor
      args:
        - --destination=$(params.image)
```

Note: ClusterTasks are deprecated in favor of remote resolution.

## Task Bundles

Package Tasks as OCI artifacts:

```bash
# Bundle a Task
tkn bundle push docker.io/myorg/my-task:v1 \
  -f my-task.yaml

# Use in TaskRun
apiVersion: tekton.dev/v1
kind: TaskRun
metadata:
  name: my-run
spec:
  taskRef:
    resolver: bundles
    params:
      - name: bundle
        value: docker.io/myorg/my-task:v1
      - name: name
        value: my-task
```

## Testing Tasks

### TaskRun for Testing

```yaml
apiVersion: tekton.dev/v1
kind: TaskRun
metadata:
  generateName: test-my-task-
spec:
  taskRef:
    name: my-task
  params:
    - name: IMAGE
      value: test-image:latest
  workspaces:
    - name: source
      emptyDir: {}
```

### Local Testing with tkn

```bash
# Start a TaskRun
tkn task start my-task \
  -p IMAGE=test:latest \
  -w name=source,emptyDir="" \
  --showlog

# View logs
tkn taskrun logs my-task-run-xyz -f

# Describe run
tkn taskrun describe my-task-run-xyz
```

## Tekton Hub Publication

### Catalog Structure

```
catalog/
└── task/
    └── my-task/
        ├── 0.1/
        │   ├── my-task.yaml
        │   └── README.md
        └── 0.2/
            ├── my-task.yaml
            └── README.md
```

### Required Annotations

```yaml
metadata:
  annotations:
    tekton.dev/pipelines.minVersion: "0.50.0"
    tekton.dev/categories: Build
    tekton.dev/tags: docker, build
    tekton.dev/displayName: "My Task"
    tekton.dev/platforms: "linux/amd64,linux/arm64"
```

### README Template

```markdown
# My Task

This task does X.

## Parameters

| Name | Description | Default |
|------|-------------|---------|
| IMAGE | Image to build | - |
| DOCKERFILE | Dockerfile path | ./Dockerfile |

## Workspaces

| Name | Description |
|------|-------------|
| source | Source code |

## Results

| Name | Description |
|------|-------------|
| IMAGE_DIGEST | Built image digest |

## Usage

\`\`\`yaml
- name: build
  taskRef:
    name: my-task
  params:
    - name: IMAGE
      value: myimage:latest
  workspaces:
    - name: source
      workspace: shared-workspace
\`\`\`

## Example TaskRun

\`\`\`yaml
apiVersion: tekton.dev/v1
kind: TaskRun
metadata:
  name: my-task-run
spec:
  taskRef:
    name: my-task
  params:
    - name: IMAGE
      value: myimage:latest
  workspaces:
    - name: source
      persistentVolumeClaim:
        claimName: source-pvc
\`\`\`
```

## Advanced Patterns

### Conditional Execution in Steps

```yaml
steps:
  - name: maybe-deploy
    image: alpine
    script: |
      if [ "$(params.DEPLOY)" = "true" ]; then
        echo "Deploying..."
        # deployment commands
      else
        echo "Skipping deployment"
      fi
```

### Retry Logic

```yaml
steps:
  - name: flaky-operation
    image: alpine
    script: |
      MAX_RETRIES=3
      RETRY_COUNT=0

      until [ $RETRY_COUNT -ge $MAX_RETRIES ]; do
        if curl -f https://api.example.com/health; then
          exit 0
        fi
        RETRY_COUNT=$((RETRY_COUNT+1))
        sleep $((RETRY_COUNT * 5))
      done

      exit 1
```

### Dynamic Script Generation

```yaml
steps:
  - name: generate-script
    image: alpine
    script: |
      cat > /workspace/run.sh << 'EOF'
      #!/bin/sh
      $(params.CUSTOM_SCRIPT)
      EOF
      chmod +x /workspace/run.sh

  - name: execute
    image: alpine
    script: |
      /workspace/run.sh
```

## Debugging

### Debug Step

```yaml
steps:
  - name: debug
    image: busybox
    script: |
      echo "=== Workspace contents ==="
      ls -la $(workspaces.source.path)

      echo "=== Environment ==="
      env | sort

      echo "=== Parameters ==="
      echo "IMAGE: $(params.IMAGE)"
```

### Interactive Debugging

```yaml
# Add a sleep step for debugging
steps:
  - name: debug-pause
    image: busybox
    script: |
      echo "Pausing for debugging..."
      sleep 3600
```

```bash
# Exec into the pod
kubectl exec -it my-taskrun-pod-xyz -c step-debug-pause -- /bin/sh
```

## Debugging Checklist

- [ ] Verify Task YAML syntax with `kubectl apply --dry-run=client`
- [ ] Check all required params have values or defaults
- [ ] Verify workspace paths are correct
- [ ] Check step images are accessible
- [ ] Validate result paths match declarations
- [ ] Test with minimal TaskRun first
- [ ] Check resource limits aren't too restrictive
- [ ] Verify secrets and configmaps exist

## References

- [Tekton Tasks Documentation](https://tekton.dev/docs/pipelines/tasks/)
- [Task Parameters](https://tekton.dev/docs/pipelines/tasks/#specifying-parameters)
- [Workspaces](https://tekton.dev/docs/pipelines/workspaces/)
- [Results](https://tekton.dev/docs/pipelines/tasks/#emitting-results)
- [Tekton Hub](https://hub.tekton.dev/)
- [Tekton Catalog](https://github.com/tektoncd/catalog)
- [Task Bundles](https://tekton.dev/docs/pipelines/pipelines/#tekton-bundles)
