---
name: cicd-gitlab-cicd-dev
description: Develop and troubleshoot GitLab CI/CD pipelines. Use when creating pipelines, debugging job failures, understanding GitLab-specific features like DAG, rules, and includes, or optimizing pipeline performance.
---

# GitLab CI/CD Development

Guide for developing, debugging, and optimizing GitLab CI/CD pipelines.

## When to Use This Skill

- Creating new GitLab CI/CD pipelines
- Debugging job failures from pipeline logs
- Understanding GitLab-specific pipeline features
- Optimizing pipeline performance and costs
- Configuring runners and environments
- Working with includes, extends, and templates

## Pipeline Structure

### File Location

Pipelines are defined in `.gitlab-ci.yml` at the repository root.

### Basic Structure

```yaml
stages:
  - build
  - test
  - deploy

variables:
  NODE_VERSION: "20"

build:
  stage: build
  image: node:${NODE_VERSION}
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/

test:
  stage: test
  image: node:${NODE_VERSION}
  script:
    - npm ci
    - npm test

deploy:
  stage: deploy
  script:
    - ./deploy.sh
  only:
    - main
```

## Key Concepts

### Stages

Stages define the order of job execution. Jobs in the same stage run in parallel.

```yaml
stages:
  - build
  - test
  - deploy
  - cleanup
```

### Jobs

Jobs are the basic unit of execution:

```yaml
job-name:
  stage: test
  image: ruby:3.2
  before_script:
    - bundle install
  script:
    - bundle exec rspec
  after_script:
    - echo "Cleanup"
  artifacts:
    paths:
      - coverage/
    expire_in: 1 week
```

### Variables

```yaml
# Global variables
variables:
  DATABASE_URL: "postgres://localhost/test"
  RAILS_ENV: test

# Job-level variables
test:
  variables:
    COVERAGE: "true"
  script:
    - echo $COVERAGE
```

### Predefined Variables

```yaml
script:
  - echo "Project: $CI_PROJECT_NAME"
  - echo "Branch: $CI_COMMIT_REF_NAME"
  - echo "Commit: $CI_COMMIT_SHA"
  - echo "Pipeline: $CI_PIPELINE_ID"
  - echo "Job: $CI_JOB_ID"
  - echo "Runner: $CI_RUNNER_ID"
  - echo "Environment: $CI_ENVIRONMENT_NAME"
```

## Common CI Patterns

### Matrix Builds (Parallel)

```yaml
test:
  stage: test
  parallel:
    matrix:
      - RUBY_VERSION: ["3.1", "3.2", "3.3"]
        DATABASE: ["postgres", "mysql"]
  image: ruby:$RUBY_VERSION
  script:
    - echo "Testing Ruby $RUBY_VERSION with $DATABASE"
```

### Rules (Conditional Execution)

```yaml
deploy:
  stage: deploy
  script:
    - ./deploy.sh
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: on_success
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      when: manual
    - when: never
```

### DAG (Directed Acyclic Graph)

Use `needs` for faster pipelines by skipping stage ordering:

```yaml
stages:
  - build
  - test
  - deploy

build-frontend:
  stage: build
  script: npm run build:frontend

build-backend:
  stage: build
  script: npm run build:backend

test-frontend:
  stage: test
  needs: [build-frontend]  # Runs as soon as build-frontend completes
  script: npm run test:frontend

test-backend:
  stage: test
  needs: [build-backend]
  script: npm run test:backend

deploy:
  stage: deploy
  needs: [test-frontend, test-backend]
  script: ./deploy.sh
```

### Caching

```yaml
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - node_modules/
    - .npm/

# Or per-job cache
test:
  cache:
    key:
      files:
        - package-lock.json
    paths:
      - node_modules/
  script:
    - npm ci --cache .npm
    - npm test
```

### Artifacts

```yaml
build:
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
    exclude:
      - dist/**/*.map
    expire_in: 1 day
    reports:
      junit: test-results.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura.xml
```

## Includes and Templates

### Include External Files

```yaml
include:
  # Local file
  - local: '/templates/.gitlab-ci-template.yml'

  # From another project
  - project: 'my-group/ci-templates'
    ref: main
    file: '/templates/nodejs.yml'

  # Remote URL
  - remote: 'https://example.com/templates/ci.yml'

  # GitLab templates
  - template: Auto-DevOps.gitlab-ci.yml
```

### Extends (Inheritance)

```yaml
.test-template:
  image: node:20
  before_script:
    - npm ci
  cache:
    paths:
      - node_modules/

unit-test:
  extends: .test-template
  script:
    - npm run test:unit

integration-test:
  extends: .test-template
  script:
    - npm run test:integration
```

### Reference (YAML Anchors)

```yaml
.default-rules: &default-rules
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

test:
  <<: *default-rules
  script: npm test

lint:
  <<: *default-rules
  script: npm run lint
```

## Debugging CI Failures

### View Pipeline Logs

1. Navigate to CI/CD > Pipelines
2. Click on the pipeline
3. Click on the failed job
4. Review job log output

### Debug Mode

```yaml
test:
  script:
    - npm test
  variables:
    CI_DEBUG_TRACE: "true"  # Verbose logging
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Job stuck pending | No available runners | Check runner status and tags |
| Cache not working | Key mismatch or expired | Verify cache key and paths |
| Artifacts missing | Not passed between stages | Add artifacts and dependencies |
| Rules not matching | Incorrect conditions | Use `CI_DEBUG_TRACE` to debug |
| Image pull failed | Registry auth or network | Check image name and credentials |

### Lint Pipeline Locally

```bash
# Using GitLab CI Lint API
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --data-urlencode "content=$(cat .gitlab-ci.yml)" \
  "https://gitlab.example.com/api/v4/projects/$PROJECT_ID/ci/lint"

# Using gitlab-ci-local
npm install -g gitlab-ci-local
gitlab-ci-local --list
gitlab-ci-local test
```

## Runner Configuration

### Runner Types

| Type | Best For |
|------|----------|
| Shared runners | Small projects, standard builds |
| Group runners | Team-specific configuration |
| Project runners | Custom requirements, security |

### Runner Tags

```yaml
deploy:
  tags:
    - docker
    - linux
    - production
  script:
    - ./deploy.sh
```

### Docker Executor

```yaml
test:
  image: python:3.11
  services:
    - postgres:15
    - redis:7
  variables:
    POSTGRES_DB: test
    POSTGRES_USER: runner
    POSTGRES_PASSWORD: ""
  script:
    - pytest
```

## Environment and Secrets

### Protected Variables

Configure in Settings > CI/CD > Variables:
- Mark as "Protected" for protected branches only
- Mark as "Masked" to hide in logs

```yaml
deploy:
  script:
    - echo $DEPLOY_TOKEN  # Masked in logs
  only:
    - main  # Protected variable only available here
```

### Environments

```yaml
deploy-staging:
  stage: deploy
  environment:
    name: staging
    url: https://staging.example.com
  script:
    - ./deploy.sh staging

deploy-production:
  stage: deploy
  environment:
    name: production
    url: https://example.com
  when: manual
  script:
    - ./deploy.sh production
```

## Performance Optimization

### Interruptible Jobs

Cancel running jobs when new commits push:

```yaml
test:
  interruptible: true
  script:
    - npm test
```

### Resource Groups

Prevent concurrent deploys:

```yaml
deploy:
  resource_group: production
  script:
    - ./deploy.sh
```

### Workflow Rules

Skip pipelines for certain conditions:

```yaml
workflow:
  rules:
    - if: $CI_COMMIT_MESSAGE =~ /\[skip ci\]/
      when: never
    - if: $CI_PIPELINE_SOURCE == "push"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

### Pipeline Efficiency

```yaml
# Use needs for DAG
# Use rules to skip unnecessary jobs
# Cache aggressively
# Use slim images
# Parallelize where possible

test:
  parallel: 4  # Split tests across 4 jobs
  script:
    - npm run test -- --shard=$CI_NODE_INDEX/$CI_NODE_TOTAL
```

## Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.35.1
    hooks:
      - id: yamllint
        files: \.gitlab-ci\.yml$
        args: [-c, .yamllint.yml]
```

## Debugging Checklist

- [ ] Check `.gitlab-ci.yml` syntax with CI Lint
- [ ] Verify runner is available and has correct tags
- [ ] Check job rules/conditions are matching
- [ ] Review variable values (use debug trace)
- [ ] Verify artifacts are being passed correctly
- [ ] Check cache is being used effectively
- [ ] Review image availability and credentials
- [ ] Check for resource_group conflicts

## References

- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [.gitlab-ci.yml Reference](https://docs.gitlab.com/ee/ci/yaml/)
- [Predefined Variables](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html)
- [CI/CD Examples](https://docs.gitlab.com/ee/ci/examples/)
- [Pipeline Architecture](https://docs.gitlab.com/ee/ci/pipelines/pipeline_architectures.html)
- [Runner Documentation](https://docs.gitlab.com/runner/)
- [gitlab-ci-local](https://github.com/firecow/gitlab-ci-local) - Run pipelines locally
