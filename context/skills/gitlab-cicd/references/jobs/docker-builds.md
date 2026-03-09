---
name: docker-builds
description: Docker-in-Docker, Kaniko, Buildah, multi-stage builds, and CI_REGISTRY integration
---

# Docker Builds

> **Scope:** Docker-in-Docker, Kaniko, Buildah, multi-stage builds, and CI_REGISTRY integration
> **GitLab version:** 10.0+
> **Source cards:** NEW-11
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Building Docker/OCI images in GitLab CI
- Choosing between DinD, Kaniko, and Buildah for container builds
- Configuring GitLab Container Registry integration
- Optimizing build times with layer caching and multi-stage builds

## Key Concepts

### Build Methods

| Method | Privileged? | Daemon? | Best For |
|---|---|---|---|
| **Docker-in-Docker (DinD)** | Yes | Yes (sidecar) | Full Docker API, docker-compose |
| **Kaniko** | No | No | Shared/restricted runners, rootless builds |
| **Buildah** | No | No | OCI images, rootless, Podman-compatible |
| **Docker socket bind** | No* | Host daemon | Fast, uses host Docker (security risk) |

*Socket bind shares the host Docker daemon — containers aren't isolated.

### GitLab Container Registry

| Variable | Value |
|---|---|
| `CI_REGISTRY` | Registry URL (e.g., `registry.gitlab.com`) |
| `CI_REGISTRY_IMAGE` | Full image path: `registry.gitlab.com/group/project` |
| `CI_REGISTRY_USER` | `gitlab-ci-token` |
| `CI_REGISTRY_PASSWORD` | `$CI_JOB_TOKEN` |

### Multi-Stage Build Caching

Use `--cache-from` to reuse layers from previously pushed images:

```bash
docker pull $CI_REGISTRY_IMAGE:latest || true
docker build --cache-from $CI_REGISTRY_IMAGE:latest \
  --tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA \
  --tag $CI_REGISTRY_IMAGE:latest .
docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
docker push $CI_REGISTRY_IMAGE:latest
```

## Examples

### Docker-in-Docker

```yaml
build-image:
  stage: build
  image: docker:24-dind
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

### Kaniko (Rootless)

```yaml
build-image:
  stage: build
  image:
    name: gcr.io/kaniko-project/executor:v1.23.0-debug
    entrypoint: [""]
  script:
    - /kaniko/executor
      --context $CI_PROJECT_DIR
      --dockerfile $CI_PROJECT_DIR/Dockerfile
      --destination $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
      --cache=true
      --cache-repo=$CI_REGISTRY_IMAGE/cache
```

### Buildah (OCI-Native)

```yaml
build-image:
  stage: build
  image: quay.io/buildah/stable:latest
  variables:
    STORAGE_DRIVER: vfs
  script:
    - buildah bud -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - buildah login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - buildah push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

## Common Patterns

- **Kaniko for shared runners** — no privileged mode required
- **Multi-stage builds** with `--cache-from` for layer reuse
- **`CI_REGISTRY_IMAGE`** for automatic image naming
- **Tag with `$CI_COMMIT_SHA`** for immutable references + `latest` for convenience
- **DinD with TLS** (`DOCKER_TLS_CERTDIR: "/certs"`) — required for secure DinD

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| DinD on shared runners without review | Security risk — privileged containers | Use Kaniko or dedicated runners |
| No build cache strategy | Rebuilds everything each time | Use `--cache-from` or Kaniko `--cache=true` |
| Docker socket bind in shared env | Host Docker shared, container escape risk | Use DinD with TLS or Kaniko |
| Large base images (1GB+) | Slow pull, wasted minutes | Use `-slim` or `-alpine` variants |
| Not logging into registry | Push fails silently | `docker login` in `before_script` |

## Practitioner Pain Points

1. **DinD requires `privileged: true`** — most shared runners don't allow this. Kaniko is the standard workaround.
2. **Layer caching with Kaniko** — use `--cache=true --cache-repo=` to push/pull cache layers to registry.
3. **`DOCKER_TLS_CERTDIR`** — DinD requires TLS since Docker 20.10+. Set to `"/certs"` or `""` (insecure).
<!-- TODO: Expand with deeper research on Buildah rootless patterns and multi-arch builds -->

## Related Topics

- [../runner/executors.md](../runner/executors.md) — Docker executor configuration
- [../runner/security.md](../runner/security.md) — Privileged mode and `allowed_images`
- [../pipelines/security.md](../pipelines/security.md) — Image pinning and supply chain

## Sources

- [Docker builds in CI](https://docs.gitlab.com/ci/docker/using_docker_build/)
- [Kaniko](https://docs.gitlab.com/ci/docker/using_kaniko/)
- [Container Registry](https://docs.gitlab.com/user/packages/container_registry/)

