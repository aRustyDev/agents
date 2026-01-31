# Complexity: Complex

## Characteristics
- Microservices architecture
- Dynamic pipeline generation
- Multiple deployment targets
- Advanced testing strategies
- Service dependencies

## Applicable Patterns
- gitops
- progressive-delivery
- canary
- blue-green

## Pipeline Features
- Dynamic job generation
- Conditional workflows
- Cross-service testing
- Dependency management
- Advanced caching strategies

## Common Configurations

### GitHub Actions - Microservices
```yaml
name: Complex Microservices Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      services: ${{ steps.detect.outputs.services }}
      matrix: ${{ steps.detect.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Detect changed services
        id: detect
        run: |
          SERVICES=$(git diff --name-only ${{ github.event.before }} ${{ github.sha }} | \
            grep -E '^services/' | \
            cut -d/ -f2 | \
            sort -u | \
            jq -R . | jq -sc .)
          echo "services=$SERVICES" >> $GITHUB_OUTPUT
          echo "matrix={\"service\":$SERVICES}" >> $GITHUB_OUTPUT

  build:
    needs: detect-changes
    if: needs.detect-changes.outputs.services != '[]'
    runs-on: ubuntu-latest
    strategy:
      matrix: ${{ fromJson(needs.detect-changes.outputs.matrix) }}
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: services/${{ matrix.service }}
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ github.repository }}/${{ matrix.service }}:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ github.repository }}/${{ matrix.service }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64

  dependency-test:
    needs: build
    runs-on: ubuntu-latest
    strategy:
      matrix:
        test-suite: [api-gateway, service-mesh, data-pipeline]
    steps:
      - uses: actions/checkout@v4
      
      - name: Run dependency tests
        run: |
          docker-compose -f tests/${{ matrix.test-suite }}/docker-compose.yml up -d
          ./tests/${{ matrix.test-suite }}/run-tests.sh
          
  performance-test:
    needs: dependency-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run load tests
        run: |
          docker run --rm \
            -v $PWD/tests/load:/scripts \
            grafana/k6 run /scripts/load-test.js

  deploy-preview:
    needs: [build, dependency-test]
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy preview environment
        id: deploy-preview
        run: |
          PREVIEW_URL=$(./scripts/deploy-preview.sh ${{ github.event.number }})
          echo "url=$PREVIEW_URL" >> $GITHUB_OUTPUT
      
      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🚀 Preview environment deployed: ${{ steps.deploy-preview.outputs.url }}'
            })

  canary-deploy:
    needs: [build, dependency-test, performance-test]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy canary
        run: |
          ./scripts/deploy-canary.sh 10  # 10% traffic
          
      - name: Monitor canary
        run: |
          ./scripts/monitor-canary.sh --duration 30m --error-threshold 1
          
      - name: Promote or rollback
        run: |
          if ./scripts/check-canary-health.sh; then
            ./scripts/promote-canary.sh
          else
            ./scripts/rollback-canary.sh
          fi
```

### GitLab CI - Dynamic Pipelines
```yaml
stages:
  - analyze
  - generate
  - build
  - test
  - deploy

variables:
  DOCKER_BUILDKIT: 1
  BUILDKIT_INLINE_CACHE: 1

analyze:changes:
  stage: analyze
  image: alpine:latest
  script:
    - apk add --no-cache git jq
    - |
      CHANGED_SERVICES=$(git diff --name-only $CI_COMMIT_BEFORE_SHA $CI_COMMIT_SHA | \
        grep -E '^services/' | \
        cut -d/ -f2 | \
        sort -u)
      echo "$CHANGED_SERVICES" > changed_services.txt
    - |
      cat > pipeline-config.yml <<EOF
      include:
        - local: .gitlab/ci/base.yml
      
      stages:
        - build
        - test
        - deploy
      
      EOF
      
      for service in $CHANGED_SERVICES; do
        cat >> pipeline-config.yml <<EOF
      build:$service:
        extends: .build_template
        variables:
          SERVICE: $service
      
      test:$service:
        extends: .test_template
        variables:
          SERVICE: $service
        needs: ["build:$service"]
      
      EOF
      done
  artifacts:
    paths:
      - pipeline-config.yml
      - changed_services.txt

generate:pipeline:
  stage: generate
  needs: ["analyze:changes"]
  trigger:
    include:
      - artifact: pipeline-config.yml
        job: analyze:changes
    strategy: depend

# Base templates in .gitlab/ci/base.yml
.build_template:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE/$SERVICE:$CI_COMMIT_SHA services/$SERVICE
    - docker push $CI_REGISTRY_IMAGE/$SERVICE:$CI_COMMIT_SHA
  retry:
    max: 2
    when:
      - runner_system_failure
      - stuck_or_timeout_failure

.test_template:
  stage: test
  script:
    - docker run --rm $CI_REGISTRY_IMAGE/$SERVICE:$CI_COMMIT_SHA test

# Service mesh testing
test:service-mesh:
  stage: test
  needs: ["analyze:changes"]
  services:
    - name: consul:latest
      alias: consul
    - name: envoyproxy/envoy:latest
      alias: envoy
  script:
    - ./scripts/test-service-mesh.sh
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# Progressive delivery
deploy:canary:
  stage: deploy
  image: fluxcd/flux-cli:latest
  script:
    - flux reconcile source git flux-system
    - |
      for service in $(cat changed_services.txt); do
        kubectl set image deployment/$service \
          $service=$CI_REGISTRY_IMAGE/$service:$CI_COMMIT_SHA \
          -n production
        kubectl rollout status deployment/$service -n production
      done
  environment:
    name: production
    url: https://api.example.com
  only:
    - main
```

## Optimization Focus
- Pipeline parallelization
- Selective service building
- Distributed caching
- Resource pooling

## Advanced Patterns

### GitOps Integration
```yaml
gitops:sync:
  script:
    - |
      # Update manifests
      for service in $CHANGED_SERVICES; do
        yq eval ".spec.template.spec.containers[0].image = \"$REGISTRY/$service:$TAG\"" \
          -i manifests/$service/deployment.yaml
      done
    - |
      # Commit and push
      git config user.email "ci@example.com"
      git config user.name "CI Bot"
      git add manifests/
      git commit -m "Update services: $CHANGED_SERVICES"
      git push origin main
```

### Service Dependency Management
```yaml
dependency:graph:
  script:
    - |
      # Generate dependency graph
      ./scripts/analyze-dependencies.sh > dependencies.json
      
      # Order services by dependencies
      ORDERED_SERVICES=$(jq -r '.services | sort_by(.dependencies | length)' dependencies.json)
      
      # Deploy in dependency order
      echo "$ORDERED_SERVICES" | jq -r '.[].name' | while read service; do
        ./scripts/deploy-service.sh $service
        ./scripts/wait-for-healthy.sh $service
      done
```

### Multi-Region Deployment
```yaml
deploy:multi-region:
  parallel:
    matrix:
      - REGION: [us-east-1, eu-west-1, ap-southeast-1]
  script:
    - ./scripts/deploy-region.sh $REGION
    - ./scripts/verify-region.sh $REGION
```

## Best Practices

1. **Change Detection**
   - Build only what changed
   - Smart dependency resolution
   - Incremental testing

2. **Caching Strategy**
   - Distributed cache for builds
   - Layer caching for Docker
   - Dependency caching per service

3. **Testing Strategy**
   - Service isolation tests
   - Contract testing
   - Chaos engineering
   - Performance benchmarking

4. **Deployment Strategy**
   - Progressive rollouts
   - Automated rollbacks
   - Health monitoring
   - Traffic management