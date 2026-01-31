# GitLab CI Basics

## Core Concepts

### Pipelines
- Defined in `.gitlab-ci.yml`
- Top-level component containing stages and jobs
- Triggered by commits, MRs, schedules, or API

### Stages
- Groups of jobs that run in parallel
- Define the order of execution
- Default stages: build, test, deploy

### Jobs
- Individual tasks that run scripts
- Belong to a stage
- Can have dependencies and artifacts

### Runners
- Agents that execute jobs
- Shared, group, or project-specific
- Can have tags for job assignment

### Artifacts
- Files passed between jobs
- Can be downloaded from UI
- Have expiration times

### Variables
- CI/CD variables at different scopes
- Protected and masked options
- File type variables available

## Syntax Reference

### Basic Pipeline Structure
```yaml
# Define stages
stages:
  - build
  - test
  - deploy

# Global variables
variables:
  GLOBAL_VAR: "value"

# Default configuration
default:
  image: node:18
  before_script:
    - npm ci --cache .npm --prefer-offline
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - .npm/

# Job definition
build:
  stage: build
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
```

### Job Configuration
```yaml
test:unit:
  stage: test
  image: node:18
  services:
    - postgres:14
  variables:
    POSTGRES_DB: test
    POSTGRES_PASSWORD: secret
  before_script:
    - npm ci
  script:
    - npm test
  after_script:
    - echo "Tests completed"
  coverage: '/Coverage: \d+\.\d+%/'
  retry:
    max: 2
    when:
      - runner_system_failure
      - stuck_or_timeout_failure
  timeout: 30 minutes
  tags:
    - docker
    - linux
```

### Rules and Conditions
```yaml
deploy:
  stage: deploy
  script:
    - ./deploy.sh
  rules:
    # Deploy on main branch
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: on_success
    # Deploy on tags
    - if: $CI_COMMIT_TAG
      when: on_success
    # Manual deploy for other branches
    - if: $CI_COMMIT_BRANCH
      when: manual
    # Don't run on merge requests
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      when: never
```

### Parallel Jobs
```yaml
# Parallel matrix
test:
  stage: test
  parallel:
    matrix:
      - OS: linux
        ARCH: [amd64, arm64]
      - OS: windows
        ARCH: amd64
  script:
    - echo "Testing on $OS-$ARCH"

# Simple parallel
test:load:
  stage: test
  parallel: 5
  script:
    - echo "Running load test $CI_NODE_INDEX/$CI_NODE_TOTAL"
```

### Dependencies and Artifacts
```yaml
build:frontend:
  stage: build
  script:
    - npm run build
  artifacts:
    name: "frontend-$CI_COMMIT_REF_NAME"
    paths:
      - dist/
    expire_in: 1 week

test:frontend:
  stage: test
  dependencies:
    - build:frontend
  script:
    - npm test

deploy:frontend:
  stage: deploy
  needs:
    - job: build:frontend
      artifacts: true
    - job: test:frontend
      artifacts: false
  script:
    - ./deploy.sh dist/
```

### Environments
```yaml
deploy:staging:
  stage: deploy
  script:
    - ./deploy.sh staging
  environment:
    name: staging
    url: https://staging.example.com
    on_stop: stop:staging
  only:
    - develop

stop:staging:
  stage: deploy
  script:
    - ./stop.sh staging
  environment:
    name: staging
    action: stop
  when: manual
  only:
    - develop
```

### Includes and Templates
```yaml
include:
  # Local file
  - local: .gitlab/ci/build.yml
  # Template from GitLab
  - template: Security/SAST.gitlab-ci.yml
  # Remote file
  - remote: https://example.com/ci-config.yml
  # Another project
  - project: my-group/my-project
    ref: main
    file: .gitlab-ci.yml

# Extend jobs
.test_template:
  stage: test
  before_script:
    - echo "Setup test environment"
  after_script:
    - echo "Cleanup"

test:unit:
  extends: .test_template
  script:
    - npm test
```

## Best Practices

### 1. Pipeline Efficiency
```yaml
# Use DAG for faster pipelines
stages:
  - build
  - test
  - deploy

build:app:
  stage: build
  script: build app

build:docs:
  stage: build
  script: build docs

test:app:
  stage: test
  needs: ["build:app"]
  script: test app

test:docs:
  stage: test
  needs: ["build:docs"]
  script: test docs

deploy:all:
  stage: deploy
  needs: ["test:app", "test:docs"]
  script: deploy all
```

### 2. Caching Strategy
```yaml
# Global cache
cache:
  key:
    files:
      - package-lock.json
  paths:
    - node_modules/
  policy: pull-push

# Job-specific cache
build:
  cache:
    key: "$CI_JOB_NAME-$CI_COMMIT_REF_SLUG"
    paths:
      - .npm/
    policy: pull-push

test:
  cache:
    key: "$CI_JOB_NAME-$CI_COMMIT_REF_SLUG"
    paths:
      - .npm/
    policy: pull
```

### 3. Security Best Practices
```yaml
# Use protected variables
deploy:
  script:
    - deploy --token $DEPLOY_TOKEN
  only:
    - main
  # Requires protected branch and variables

# Mask sensitive output
test:
  script:
    - export TOKEN=$(get-token)
    - echo "TOKEN=$TOKEN" | sed 's/=.*/=****/'
    
# Use file type variables for sensitive data
deploy:secure:
  script:
    - deploy --key-file $SSH_PRIVATE_KEY
  # SSH_PRIVATE_KEY is a file type variable
```

### 4. Reusable Components
```yaml
# Hidden job as template
.deploy:
  image: alpine:latest
  variables:
    GIT_STRATEGY: none
  before_script:
    - apk add --no-cache curl
  script:
    - curl -X POST $DEPLOY_WEBHOOK

# YAML anchors
.node_modules_cache: &node_modules_cache
  key:
    files:
      - package-lock.json
  paths:
    - node_modules/

build:
  cache:
    <<: *node_modules_cache
    policy: pull-push

test:
  cache:
    <<: *node_modules_cache
    policy: pull
```

## Advanced Features

### Dynamic Pipelines
```yaml
generate:pipeline:
  stage: .pre
  script:
    - |
      cat > generated-pipeline.yml <<EOF
      test:dynamic:
        script:
          - echo "Dynamic job"
      EOF
  artifacts:
    paths:
      - generated-pipeline.yml

child:pipeline:
  stage: test
  trigger:
    include:
      - artifact: generated-pipeline.yml
        job: generate:pipeline
```

### Multi-Project Pipelines
```yaml
trigger:downstream:
  stage: deploy
  trigger:
    project: my-group/my-deployment-project
    branch: main
    strategy: depend
```

### Merge Request Pipelines
```yaml
# Only run on merge requests
test:mr:
  script:
    - npm test
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

# Different behavior for MRs
deploy:review:
  script:
    - deploy --env review-$CI_MERGE_REQUEST_IID
  environment:
    name: review/$CI_MERGE_REQUEST_IID
    url: https://$CI_MERGE_REQUEST_IID.review.example.com
    on_stop: stop:review
  rules:
    - if: $CI_MERGE_REQUEST_ID
```

### Resource Groups
```yaml
deploy:production:
  script: deploy
  resource_group: production
  # Ensures only one deployment at a time
```

## Pipeline Optimization

### 1. Fail Fast
```yaml
test:lint:
  stage: .pre
  script:
    - npm run lint
  # Fails pipeline early if linting fails

test:unit:
  stage: test
  script:
    - npm test
  interruptible: true
  # Can be cancelled if newer pipeline starts
```

### 2. Smart Test Selection
```yaml
test:changes:
  script:
    - |
      CHANGED_FILES=$(git diff --name-only $CI_COMMIT_BEFORE_SHA $CI_COMMIT_SHA)
      if echo "$CHANGED_FILES" | grep -q "^frontend/"; then
        npm run test:frontend
      fi
      if echo "$CHANGED_FILES" | grep -q "^backend/"; then
        npm run test:backend
      fi
  rules:
    - if: $CI_PIPELINE_SOURCE == "push"
```

### 3. Pipeline Schedules
```yaml
nightly:tests:
  script:
    - npm run test:extensive
  only:
    - schedules
  variables:
    TEST_SUITE: "full"
```

## Debugging

### Enable Debug Output
```yaml
debug:job:
  variables:
    CI_DEBUG_TRACE: "true"
  script:
    - echo "Debug mode enabled"
```

### Troubleshooting Commands
```yaml
debug:info:
  script:
    - echo "Project: $CI_PROJECT_NAME"
    - echo "Branch: $CI_COMMIT_BRANCH"
    - echo "Pipeline: $CI_PIPELINE_ID"
    - echo "Job: $CI_JOB_ID"
    - env | grep CI_
```

### Common Issues

1. **Job Not Running**
   - Check rules/only/except conditions
   - Verify runner tags match
   - Check if runner is available

2. **Artifacts Not Found**
   - Check job dependencies
   - Verify artifact paths
   - Check expiration time

3. **Variable Not Available**
   - Check variable scope
   - Verify protected branch settings
   - Check masked variable regex

4. **Pipeline Timeout**
   - Adjust job/pipeline timeout
   - Optimize long-running scripts
   - Consider splitting into multiple jobs