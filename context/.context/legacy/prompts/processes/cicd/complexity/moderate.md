# Complexity: Moderate

## Characteristics
- Multiple services or complex monolith
- Multiple environments (dev/staging/prod)
- Matrix builds
- Integration testing

## Applicable Patterns
- build-test-deploy
- blue-green
- feature-flags

## Standard Pipeline Structure
```yaml
stages:
  - build
  - test
  - integration
  - deploy-staging
  - deploy-production

includes:
  - Matrix strategies
  - Environment-specific configs
  - Approval gates
```

## Common Configurations

### GitHub Actions Example
```yaml
name: Moderate Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [api, frontend, worker]
        node-version: [16, 18]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
          cache-dependency-path: services/${{ matrix.service }}/package-lock.json
      
      - name: Build service
        working-directory: services/${{ matrix.service }}
        run: |
          npm ci
          npm run build
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.service }}-${{ matrix.node-version }}-dist
          path: services/${{ matrix.service }}/dist

  test:
    needs: build
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [api, frontend, worker]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run unit tests
        working-directory: services/${{ matrix.service }}
        run: |
          npm ci
          npm test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: services/${{ matrix.service }}/coverage/lcov.info
          flags: ${{ matrix.service }}

  integration-test:
    needs: test
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run integration tests
        run: |
          docker-compose -f docker-compose.test.yml up -d
          npm run test:integration
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test

  deploy-staging:
    needs: integration-test
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment"
          # Add actual deployment steps

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to production
        run: |
          echo "Deploying to production environment"
          # Add actual deployment steps
```

### GitLab CI Example
```yaml
stages:
  - build
  - test
  - integration
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: ""

.build_template:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE/$SERVICE:$CI_COMMIT_SHA services/$SERVICE
    - docker push $CI_REGISTRY_IMAGE/$SERVICE:$CI_COMMIT_SHA

build:api:
  extends: .build_template
  variables:
    SERVICE: api

build:frontend:
  extends: .build_template
  variables:
    SERVICE: frontend

build:worker:
  extends: .build_template
  variables:
    SERVICE: worker

test:unit:
  stage: test
  parallel:
    matrix:
      - SERVICE: [api, frontend, worker]
  script:
    - cd services/$SERVICE
    - npm ci
    - npm test -- --coverage
  coverage: '/Lines\s*:\s*(\d+\.\d+)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: services/$SERVICE/coverage/cobertura-coverage.xml

test:integration:
  stage: integration
  services:
    - postgres:14
    - redis:7
  variables:
    POSTGRES_DB: test
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
  script:
    - docker-compose -f docker-compose.test.yml up -d
    - npm run test:integration

deploy:staging:
  stage: deploy
  environment:
    name: staging
    url: https://staging.example.com
  script:
    - echo "Deploying to staging"
    # Add deployment script
  only:
    - develop

deploy:production:
  stage: deploy
  environment:
    name: production
    url: https://example.com
  script:
    - echo "Deploying to production"
    # Add deployment script
  only:
    - main
  when: manual
```

## Optimization Focus
- Parallel job execution
- Smart test selection
- Artifact sharing
- Container layer caching

## Environment Management
```yaml
environments:
  development:
    auto_deploy: true
    branch: develop
    
  staging:
    auto_deploy: true
    branch: develop
    approval: optional
    
  production:
    auto_deploy: false
    branch: main
    approval: required
```

## Best Practices
1. **Matrix Builds**
   - Test against multiple versions
   - Parallel service builds
   - Cross-platform testing

2. **Artifact Management**
   - Share build artifacts between jobs
   - Use artifact expiration
   - Compress large artifacts

3. **Environment Isolation**
   - Separate credentials per environment
   - Environment-specific configurations
   - Deployment gates and approvals

4. **Test Optimization**
   - Run tests in parallel
   - Implement test splitting
   - Cache test dependencies

## Common Patterns

### Blue-Green Deployment
```yaml
deploy:blue-green:
  script:
    - ./scripts/deploy-blue.sh
    - ./scripts/health-check.sh blue
    - ./scripts/switch-traffic.sh blue
    - ./scripts/cleanup-green.sh
  rollback:
    - ./scripts/switch-traffic.sh green
```

### Feature Flags
```yaml
deploy:with-features:
  script:
    - export FEATURE_FLAGS=$(./scripts/get-feature-flags.sh $ENVIRONMENT)
    - ./scripts/deploy.sh --features "$FEATURE_FLAGS"
```