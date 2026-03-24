---
name: cicd-gitlab-components-dev
description: Develop reusable GitLab CI/CD components and templates. Use when creating CI/CD component libraries, building include templates, packaging components for the CI/CD Catalog, or designing organization-wide pipeline templates.
---

# GitLab CI/CD Components Development

Guide for developing reusable GitLab CI/CD components and templates that can be shared across projects and organizations.

## When to Use This Skill

- Creating reusable CI/CD component libraries
- Building include templates for shared pipelines
- Publishing to the GitLab CI/CD Catalog
- Designing organization-wide pipeline standards
- Packaging job templates and configurations
- Understanding component inputs, outputs, and specs

## Component Types

### CI/CD Components (Catalog)

Modern, versioned components with defined interfaces:

```yaml
# templates/build/template.yml
spec:
  inputs:
    stage:
      default: build
    image:
      default: node:20
    script:
      type: array

---
build-job:
  stage: $[[ inputs.stage ]]
  image: $[[ inputs.image ]]
  script: $[[ inputs.script ]]
  artifacts:
    paths:
      - dist/
```

### Include Templates

Traditional YAML templates for sharing:

```yaml
# templates/nodejs.yml
.nodejs-base:
  image: node:20
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/

.nodejs-test:
  extends: .nodejs-base
  script:
    - npm ci
    - npm test
```

## Component Structure

### Directory Layout

```
my-component/
├── templates/
│   ├── build/
│   │   └── template.yml     # Component definition
│   ├── test/
│   │   └── template.yml
│   └── deploy/
│       └── template.yml
├── README.md
└── .gitlab-ci.yml           # Tests for the components
```

### Component Specification

```yaml
# templates/my-job/template.yml
spec:
  inputs:
    # String input with default
    environment:
      description: 'Target environment'
      default: 'development'

    # Required string input
    app-name:
      description: 'Application name'

    # Boolean input
    run-tests:
      description: 'Whether to run tests'
      type: boolean
      default: true

    # Number input
    replicas:
      description: 'Number of replicas'
      type: number
      default: 1

    # Array input
    extra-args:
      description: 'Additional arguments'
      type: array
      default: []

---
# Component implementation
deploy-$[[ inputs.environment ]]:
  stage: deploy
  script:
    - echo "Deploying $[[ inputs.app-name ]] to $[[ inputs.environment ]]"
    - kubectl scale deployment/$[[ inputs.app-name ]] --replicas=$[[ inputs.replicas ]]
  rules:
    - if: $[[ inputs.run-tests ]]
      when: on_success
```

## Input Types

### String (Default)

```yaml
spec:
  inputs:
    version:
      description: 'Version to deploy'
      default: 'latest'
      options:              # Restrict to specific values
        - 'latest'
        - 'stable'
        - 'edge'
```

### Boolean

```yaml
spec:
  inputs:
    enable-cache:
      type: boolean
      default: true

---
job:
  cache:
    - if: $[[ inputs.enable-cache ]]
      paths:
        - node_modules/
```

### Number

```yaml
spec:
  inputs:
    timeout-minutes:
      type: number
      default: 30

---
job:
  timeout: $[[ inputs.timeout-minutes ]] minutes
```

### Array

```yaml
spec:
  inputs:
    services:
      type: array
      default:
        - postgres:15
        - redis:7

---
job:
  services: $[[ inputs.services ]]
```

## Using Components

### From CI/CD Catalog

```yaml
include:
  - component: gitlab.com/my-org/components/build@1.0.0
    inputs:
      image: node:20
      script:
        - npm run build
```

### From Project Repository

```yaml
include:
  - component: $CI_SERVER_HOST/$CI_PROJECT_PATH/templates/build@$CI_COMMIT_SHA
    inputs:
      stage: build
```

### Multiple Components

```yaml
include:
  - component: gitlab.com/org/components/lint@1.0
    inputs:
      config: .eslintrc.json

  - component: gitlab.com/org/components/test@1.0
    inputs:
      coverage: true

  - component: gitlab.com/org/components/deploy@1.0
    inputs:
      environment: production
```

## Template Patterns

### Hidden Jobs (Extends)

```yaml
# templates/base.yml
.base-job:
  image: alpine:latest
  before_script:
    - apk add --no-cache curl
  tags:
    - docker

.test-base:
  extends: .base-job
  stage: test
  coverage: '/Coverage: \d+\.\d+%/'

.deploy-base:
  extends: .base-job
  stage: deploy
  when: manual
```

### Parameterized Templates

```yaml
# templates/docker-build.yml
spec:
  inputs:
    dockerfile:
      default: Dockerfile
    context:
      default: '.'
    registry:
      default: $CI_REGISTRY
    image-name:
      default: $CI_PROJECT_PATH

---
docker-build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $[[ inputs.registry ]]
    - docker build -f $[[ inputs.dockerfile ]] -t $[[ inputs.registry ]]/$[[ inputs.image-name ]]:$CI_COMMIT_SHA $[[ inputs.context ]]
    - docker push $[[ inputs.registry ]]/$[[ inputs.image-name ]]:$CI_COMMIT_SHA
```

### Job Generator Pattern

```yaml
spec:
  inputs:
    environments:
      type: array
      default:
        - staging
        - production

---
# Generates multiple jobs from array
.deploy-template:
  stage: deploy
  script:
    - ./deploy.sh $ENVIRONMENT

deploy-staging:
  extends: .deploy-template
  variables:
    ENVIRONMENT: staging
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

deploy-production:
  extends: .deploy-template
  variables:
    ENVIRONMENT: production
  when: manual
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

## CI/CD Catalog Publishing

### Project Configuration

```yaml
# .gitlab-ci.yml in component project
stages:
  - test
  - release

test-components:
  stage: test
  script:
    - gitlab-ci-local --list  # Validate components

create-release:
  stage: release
  script:
    - echo "Creating release"
  release:
    tag_name: $CI_COMMIT_TAG
    description: 'Release $CI_COMMIT_TAG'
  rules:
    - if: $CI_COMMIT_TAG
```

### Catalog Metadata

```yaml
# In project settings or .gitlab/ci-component.yml
---
name: My CI/CD Components
description: Reusable components for CI/CD
icon: 🚀
categories:
  - Build
  - Test
  - Deploy
```

### Versioning

```bash
# Semantic versioning for components
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
```

## Include Patterns

### Local Includes

```yaml
include:
  - local: '/templates/base.yml'
  - local: '/templates/nodejs.yml'
```

### Project Includes

```yaml
include:
  - project: 'my-group/ci-templates'
    ref: v1.0.0
    file:
      - '/templates/nodejs.yml'
      - '/templates/docker.yml'
```

### Remote Includes

```yaml
include:
  - remote: 'https://example.com/ci/templates/standard.yml'
```

### Template Includes

```yaml
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Code-Quality.gitlab-ci.yml
```

## Testing Components

### Component Validation

```yaml
# .gitlab-ci.yml
test:component-syntax:
  stage: test
  script:
    - |
      for template in templates/*/template.yml; do
        echo "Validating $template"
        yq eval '.' "$template" > /dev/null
      done
```

### Integration Testing

```yaml
test:component-integration:
  stage: test
  trigger:
    include:
      - component: $CI_SERVER_FQDN/$CI_PROJECT_PATH/templates/build@$CI_COMMIT_SHA
        inputs:
          script:
            - echo "Test passed"
```

### Local Testing

```bash
# Install gitlab-ci-local
npm install -g gitlab-ci-local

# Test pipeline with components
gitlab-ci-local --list
gitlab-ci-local test
```

## Advanced Patterns

### Conditional Component Content

```yaml
spec:
  inputs:
    enable-sast:
      type: boolean
      default: false

---
build:
  stage: build
  script:
    - npm run build

# Only included when enable-sast is true
sast-scan:
  rules:
    - if: $[[ inputs.enable-sast ]]
  stage: test
  script:
    - npm audit
```

### Composition of Components

```yaml
# meta-component that combines others
spec:
  inputs:
    nodejs-version:
      default: '20'
    run-security:
      type: boolean
      default: true

---
include:
  - component: gitlab.com/org/components/nodejs-setup@1.0
    inputs:
      version: $[[ inputs.nodejs-version ]]

  - component: gitlab.com/org/components/security-scan@1.0
    rules:
      - if: $[[ inputs.run-security ]]
```

### Dynamic Child Pipelines

```yaml
spec:
  inputs:
    services:
      type: array

---
generate-pipeline:
  stage: build
  script:
    - |
      cat > child-pipeline.yml << EOF
      stages:
        - deploy
      EOF
      for service in $[[ inputs.services | join(" ") ]]; do
        cat >> child-pipeline.yml << EOF
      deploy-$service:
        stage: deploy
        script:
          - ./deploy.sh $service
      EOF
      done
  artifacts:
    paths:
      - child-pipeline.yml

trigger-deploy:
  stage: deploy
  trigger:
    include:
      - artifact: child-pipeline.yml
        job: generate-pipeline
```

## Documentation

### Component README

```markdown
# Component Name

Brief description of what this component does.

## Usage

\`\`\`yaml
include:
  - component: gitlab.com/org/my-component@1.0.0
    inputs:
      param1: value1
\`\`\`

## Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `param1` | string | `default` | What it does |
| `enable-x` | boolean | `true` | Whether to enable X |

## Examples

### Basic Usage

\`\`\`yaml
include:
  - component: gitlab.com/org/my-component@1.0.0
\`\`\`

### Advanced Usage

\`\`\`yaml
include:
  - component: gitlab.com/org/my-component@1.0.0
    inputs:
      param1: custom-value
      enable-x: false
\`\`\`

## Outputs

This component creates the following jobs:
- `build`: Builds the application
- `test`: Runs tests
```

## Debugging Checklist

- [ ] Verify component spec syntax (inputs, types, defaults)
- [ ] Check `$[[ ]]` interpolation syntax (not `${{ }}`)
- [ ] Ensure inputs are passed correctly when including
- [ ] Validate YAML structure with linter
- [ ] Test component locally with gitlab-ci-local
- [ ] Verify version tags exist for referenced components
- [ ] Check project visibility allows component access

## References

- [GitLab CI/CD Components](https://docs.gitlab.com/ee/ci/components/)
- [CI/CD Catalog](https://docs.gitlab.com/ee/ci/components/#cicd-catalog)
- [Component Inputs](https://docs.gitlab.com/ee/ci/components/#define-inputs)
- [Include Keyword](https://docs.gitlab.com/ee/ci/yaml/#include)
- [Extends Keyword](https://docs.gitlab.com/ee/ci/yaml/#extends)
- [gitlab-ci-local](https://github.com/firecow/gitlab-ci-local)
