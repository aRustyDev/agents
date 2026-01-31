# Complexity: Enterprise

## Characteristics
- Monorepo with multiple services
- Multi-region deployments
- Compliance requirements
- Complex approval chains
- Cost tracking requirements

## Applicable Patterns
- All patterns applicable
- Custom hybrid patterns

## Additional Requirements
- Audit logging
- Change management
- Security scanning at multiple stages
- Cost allocation
- Performance monitoring

## Enterprise Pipeline Architecture

### GitHub Actions - Enterprise Monorepo
```yaml
name: Enterprise CI/CD Pipeline
on:
  push:
    branches: [main, release/*, hotfix/*]
  pull_request:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options: [dev, staging, prod-us, prod-eu, prod-apac]

env:
  COMPLIANCE_LEVEL: sox
  COST_CENTER: engineering
  CHANGE_TICKET_REQUIRED: true

jobs:
  # Governance and Compliance
  compliance-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check change ticket
        if: github.ref == 'refs/heads/main'
        run: |
          ./scripts/verify-change-ticket.sh ${{ github.event.head_commit.message }}
      
      - name: Audit log
        run: |
          ./scripts/audit-log.sh \
            --action "pipeline_start" \
            --user "${{ github.actor }}" \
            --ref "${{ github.ref }}" \
            --compliance "${{ env.COMPLIANCE_LEVEL }}"

  # Cost Analysis
  cost-analysis:
    runs-on: ubuntu-latest
    outputs:
      estimated_cost: ${{ steps.estimate.outputs.cost }}
      cost_approved: ${{ steps.approve.outputs.approved }}
    steps:
      - uses: actions/checkout@v4
      
      - name: Estimate pipeline cost
        id: estimate
        run: |
          COST=$(./scripts/estimate-pipeline-cost.sh)
          echo "cost=$COST" >> $GITHUB_OUTPUT
          echo "Estimated pipeline cost: \$$COST"
      
      - name: Check cost threshold
        id: approve
        run: |
          if (( $(echo "${{ steps.estimate.outputs.cost }} > 100" | bc -l) )); then
            echo "approved=false" >> $GITHUB_OUTPUT
            echo "::error::Pipeline cost exceeds threshold. Manual approval required."
          else
            echo "approved=true" >> $GITHUB_OUTPUT
          fi

  # Security Scanning
  security-scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        scan-type: [sast, dast, secrets, dependencies, containers, iac]
    steps:
      - uses: actions/checkout@v4
      
      - name: Run security scan - ${{ matrix.scan-type }}
        run: |
          ./scripts/security-scan.sh --type ${{ matrix.scan-type }}
      
      - name: Upload results
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: results/${{ matrix.scan-type }}.sarif

  # Monorepo Service Detection
  detect-services:
    runs-on: ubuntu-latest
    outputs:
      services: ${{ steps.detect.outputs.services }}
      build_matrix: ${{ steps.matrix.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Detect affected services
        id: detect
        run: |
          # Use build tool specific detection (nx, lerna, rush, etc.)
          SERVICES=$(npx nx affected:apps --base=${{ github.event.before }} --head=${{ github.sha }} --plain)
          echo "services=$SERVICES" >> $GITHUB_OUTPUT
      
      - name: Generate build matrix
        id: matrix
        run: |
          MATRIX=$(echo "${{ steps.detect.outputs.services }}" | \
            jq -R -s -c 'split(" ") | map(select(length > 0)) | {service: .}')
          echo "matrix=$MATRIX" >> $GITHUB_OUTPUT

  # Parallel Service Building
  build-services:
    needs: [compliance-check, cost-analysis, security-scan, detect-services]
    if: needs.cost-analysis.outputs.cost_approved == 'true'
    runs-on: ubuntu-latest
    strategy:
      matrix: ${{ fromJson(needs.detect-services.outputs.build_matrix) }}
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup build cache
        uses: actions/cache@v3
        with:
          path: |
            ~/.cache
            node_modules
            .next/cache
          key: ${{ runner.os }}-${{ matrix.service }}-${{ hashFiles('**/package-lock.json') }}
      
      - name: Build service
        run: |
          npx nx build ${{ matrix.service }} --configuration=production
      
      - name: Generate SBOM
        run: |
          ./scripts/generate-sbom.sh ${{ matrix.service }}
      
      - name: Sign artifacts
        run: |
          ./scripts/sign-artifact.sh \
            --service ${{ matrix.service }} \
            --key ${{ secrets.SIGNING_KEY }}

  # Multi-Region Deployment
  deploy:
    needs: build-services
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/release/')
    strategy:
      matrix:
        region: [us-east-1, eu-west-1, ap-southeast-1]
        environment: [staging, production]
        exclude:
          - environment: production
            region: us-east-1
            # Add more exclusions as needed
    environment:
      name: ${{ matrix.environment }}-${{ matrix.region }}
      url: https://${{ matrix.environment }}-${{ matrix.region }}.example.com
    steps:
      - uses: actions/checkout@v4
      
      - name: Get approval
        if: matrix.environment == 'production'
        uses: trstringer/manual-approval@v1
        with:
          secret: ${{ github.TOKEN }}
          approvers: platform-team,security-team
          minimum-approvals: 2
      
      - name: Deploy to region
        run: |
          ./scripts/deploy-region.sh \
            --environment ${{ matrix.environment }} \
            --region ${{ matrix.region }} \
            --services "${{ needs.detect-services.outputs.services }}"
      
      - name: Run smoke tests
        run: |
          ./scripts/smoke-test.sh \
            --url https://${{ matrix.environment }}-${{ matrix.region }}.example.com
      
      - name: Update cost allocation
        run: |
          ./scripts/update-cost-allocation.sh \
            --service "${{ needs.detect-services.outputs.services }}" \
            --environment ${{ matrix.environment }} \
            --region ${{ matrix.region }} \
            --cost-center ${{ env.COST_CENTER }}
```

### GitLab CI - Enterprise Configuration
```yaml
stages:
  - validate
  - analyze
  - build
  - test
  - security
  - deploy
  - monitor

variables:
  SECURE_ANALYZERS_PREFIX: "registry.gitlab.com/security-products"
  DS_EXCLUDED_PATHS: "vendor,node_modules"
  SAST_EXCLUDED_PATHS: "vendor,node_modules"

include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
  - template: Security/DAST.gitlab-ci.yml
  - template: Security/Container-Scanning.gitlab-ci.yml
  - template: Security/License-Scanning.gitlab-ci.yml

# Compliance and Governance
compliance:validation:
  stage: validate
  script:
    - ./scripts/validate-compliance.sh
    - ./scripts/check-change-approval.sh
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_BRANCH =~ /^release\//

cost:estimation:
  stage: validate
  script:
    - |
      COST=$(./scripts/estimate-deployment-cost.sh)
      echo "Estimated cost: \$${COST}"
      if [ $COST -gt 1000 ]; then
        echo "Cost exceeds threshold. Approval required."
        exit 1
      fi
  artifacts:
    reports:
      dotenv: cost.env

# Monorepo Analysis
analyze:affected:
  stage: analyze
  image: node:18
  script:
    - npx nx affected:graph --base=$CI_COMMIT_BEFORE_SHA --head=$CI_COMMIT_SHA --file=affected.json
    - |
      AFFECTED_PROJECTS=$(npx nx affected:apps --base=$CI_COMMIT_BEFORE_SHA --head=$CI_COMMIT_SHA --plain)
      echo "AFFECTED_PROJECTS=$AFFECTED_PROJECTS" > affected.env
  artifacts:
    reports:
      dotenv: affected.env
    paths:
      - affected.json

# Dynamic Pipeline Generation
generate:pipeline:
  stage: analyze
  needs: ["analyze:affected"]
  image: alpine:latest
  script:
    - apk add --no-cache jq
    - |
      cat > dynamic-pipeline.yml <<EOF
      stages:
        - build
        - test
        - deploy
      
      EOF
      
      for project in $AFFECTED_PROJECTS; do
        cat >> dynamic-pipeline.yml <<EOF
      build:${project}:
        stage: build
        script:
          - npx nx build ${project} --configuration=production
        artifacts:
          paths:
            - dist/apps/${project}
      
      test:${project}:
        stage: test
        needs: ["build:${project}"]
        script:
          - npx nx test ${project} --coverage
          - npx nx e2e ${project}-e2e
      
      EOF
      done
  artifacts:
    paths:
      - dynamic-pipeline.yml

trigger:dynamic:
  stage: build
  needs: ["generate:pipeline"]
  trigger:
    include:
      - artifact: dynamic-pipeline.yml
        job: generate:pipeline

# Multi-Region Deployment
.deploy_template:
  stage: deploy
  image: 
    name: amazon/aws-cli:latest
    entrypoint: [""]
  before_script:
    - aws configure set region $AWS_REGION
  script:
    - |
      for project in $AFFECTED_PROJECTS; do
        ./scripts/deploy-service.sh \
          --service ${project} \
          --environment ${CI_ENVIRONMENT_NAME} \
          --region ${AWS_REGION}
      done
  after_script:
    - |
      ./scripts/update-cost-tags.sh \
        --environment ${CI_ENVIRONMENT_NAME} \
        --cost-center ${COST_CENTER} \
        --project ${CI_PROJECT_NAME}

deploy:staging:us:
  extends: .deploy_template
  environment:
    name: staging-us
    url: https://staging-us.example.com
  variables:
    AWS_REGION: us-east-1
  only:
    - develop

deploy:staging:eu:
  extends: .deploy_template
  environment:
    name: staging-eu
    url: https://staging-eu.example.com
  variables:
    AWS_REGION: eu-west-1
  only:
    - develop

deploy:production:us:
  extends: .deploy_template
  environment:
    name: production-us
    url: https://us.example.com
  variables:
    AWS_REGION: us-east-1
  only:
    - main
  when: manual

deploy:production:eu:
  extends: .deploy_template
  environment:
    name: production-eu
    url: https://eu.example.com
  variables:
    AWS_REGION: eu-west-1
  only:
    - main
  when: manual

# Monitoring and Observability
monitor:deployment:
  stage: monitor
  script:
    - |
      ./scripts/send-deployment-metrics.sh \
        --services "$AFFECTED_PROJECTS" \
        --environment "$CI_ENVIRONMENT_NAME" \
        --version "$CI_COMMIT_SHA"
  when: on_success
```

## Governance Features

### Change Management Integration
```yaml
change:approval:
  script:
    - |
      TICKET=$(echo "$CI_COMMIT_MESSAGE" | grep -oP 'CHG\d+')
      if [ -z "$TICKET" ]; then
        echo "No change ticket found in commit message"
        exit 1
      fi
      
      STATUS=$(./scripts/check-change-status.sh $TICKET)
      if [ "$STATUS" != "approved" ]; then
        echo "Change ticket $TICKET is not approved"
        exit 1
      fi
```

### Audit Logging
```yaml
audit:log:
  script:
    - |
      ./scripts/audit-log.sh \
        --action "deployment" \
        --user "$GITLAB_USER_LOGIN" \
        --environment "$CI_ENVIRONMENT_NAME" \
        --services "$AFFECTED_PROJECTS" \
        --version "$CI_COMMIT_SHA" \
        --change-ticket "$CHANGE_TICKET"
```

### Cost Allocation
```yaml
cost:allocation:
  script:
    - |
      ./scripts/calculate-resource-costs.sh \
        --services "$AFFECTED_PROJECTS" \
        --environment "$CI_ENVIRONMENT_NAME" \
        --duration "$CI_PIPELINE_DURATION" \
        --resources "$DEPLOYED_RESOURCES" | \
      ./scripts/update-cost-database.sh
```

## Best Practices

1. **Monorepo Management**
   - Use build tool affected commands
   - Implement smart caching
   - Parallelize independent builds
   - Share common dependencies

2. **Compliance & Security**
   - Automate compliance checks
   - Integrate security scanning
   - Maintain audit trails
   - Implement least privilege

3. **Cost Optimization**
   - Track resource usage
   - Implement cost alerts
   - Use spot instances for builds
   - Optimize artifact storage

4. **Multi-Region Strategy**
   - Deploy closest to users
   - Implement region failover
   - Consider data residency
   - Monitor cross-region costs