# Complexity: Simple

## Characteristics
- Single service/application
- Linear build → test → deploy
- Single environment
- Basic dependencies

## Applicable Patterns
- build-test-deploy

## Standard Pipeline Structure
```yaml
stages:
  - build
  - test
  - deploy

build:
  - Install dependencies
  - Compile/build artifacts
  
test:
  - Run unit tests
  - Basic linting

deploy:
  - Deploy to single environment
```

## Common Configurations

### GitHub Actions Example
```yaml
name: Simple Pipeline
on: [push, pull_request]

jobs:
  build-test-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup runtime
        uses: actions/setup-node@v4  # or setup-python, etc.
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
      
      - name: Test
        run: npm test
      
      - name: Deploy
        if: github.ref == 'refs/heads/main'
        run: npm run deploy
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
```

### GitLab CI Example
```yaml
stages:
  - build
  - test
  - deploy

variables:
  NODE_VERSION: "18"

.node_template:
  image: node:${NODE_VERSION}
  cache:
    paths:
      - node_modules/

build:
  extends: .node_template
  stage: build
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/

test:
  extends: .node_template
  stage: test
  script:
    - npm test

deploy:
  extends: .node_template
  stage: deploy
  script:
    - npm run deploy
  only:
    - main
```

## Optimization Focus
- Build caching
- Dependency caching
- Parallel test execution

## Best Practices
1. **Cache Dependencies**
   - NPM: Cache node_modules or use npm ci
   - Python: Cache pip packages
   - Maven/Gradle: Cache ~/.m2 or ~/.gradle

2. **Fail Fast**
   - Run fastest checks first (linting before tests)
   - Use lightweight images
   - Minimize checkout depth when possible

3. **Security**
   - Never commit secrets
   - Use platform secret management
   - Scan dependencies for vulnerabilities

## Common Issues
1. **Slow Builds**
   - Solution: Implement caching
   - Use specific language versions
   - Optimize Docker layers if using containers

2. **Flaky Tests**
   - Solution: Add retry logic
   - Ensure test isolation
   - Mock external dependencies

3. **Deploy Failures**
   - Solution: Add health checks
   - Implement rollback strategy
   - Use deployment gates