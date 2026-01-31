# SAST Integration Guide

## Open Source Tools

### 1. Semgrep
Multi-language static analysis with custom rules

#### Installation and Setup
```yaml
# GitHub Actions
semgrep:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Run Semgrep
      uses: returntocorp/semgrep-action@v1
      with:
        config: >-
          p/security-audit
          p/owasp-top-ten
          p/r2c-best-practices
        generateSarif: true
    
    - name: Upload SARIF
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: semgrep.sarif

# GitLab CI
semgrep:
  stage: test
  image: returntocorp/semgrep
  script:
    - semgrep --config=auto --json --output=semgrep.json .
    - semgrep --config=auto --gitlab-sast > gl-sast-report.json
  artifacts:
    reports:
      sast: gl-sast-report.json
```

#### Custom Rules
```yaml
# .semgrep.yml
rules:
  - id: hardcoded-secret
    patterns:
      - pattern-either:
          - pattern: $KEY = "..."
          - pattern: $KEY = '...'
      - metavariable-regex:
          metavariable: $KEY
          regex: '.*(password|secret|token|key|api_key).*'
      - metavariable-regex:
          metavariable: $X
          regex: '.{8,}'
    message: Hardcoded secret detected
    languages: [python, javascript, go]
    severity: ERROR

  - id: sql-injection
    patterns:
      - pattern-either:
          - pattern: |
              $QUERY = "..." + $INPUT
              $DB.execute($QUERY)
          - pattern: |
              $QUERY = f"...{$INPUT}..."
              $DB.execute($QUERY)
    message: Potential SQL injection vulnerability
    languages: [python]
    severity: ERROR
```

### 2. SonarQube Community Edition
Continuous code quality and security analysis

#### Docker Setup
```yaml
# docker-compose.yml
version: "3"
services:
  sonarqube:
    image: sonarqube:community
    ports:
      - "9000:9000"
    environment:
      - SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true
    volumes:
      - sonarqube_data:/opt/sonarqube/data
      - sonarqube_extensions:/opt/sonarqube/extensions
      - sonarqube_logs:/opt/sonarqube/logs

volumes:
  sonarqube_data:
  sonarqube_extensions:
  sonarqube_logs:
```

#### CI Integration
```yaml
# GitHub Actions
sonarqube:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: SonarQube Scan
      uses: sonarsource/sonarqube-scan-action@master
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
    
    - name: SonarQube Quality Gate
      uses: sonarsource/sonarqube-quality-gate-action@master
      timeout-minutes: 5
      env:
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

# GitLab CI
sonarqube:
  stage: test
  image: 
    name: sonarsource/sonar-scanner-cli:latest
    entrypoint: [""]
  variables:
    SONAR_USER_HOME: "${CI_PROJECT_DIR}/.sonar"
    GIT_DEPTH: "0"
  cache:
    key: "${CI_JOB_NAME}"
    paths:
      - .sonar/cache
  script:
    - sonar-scanner
  allow_failure: true
```

#### Configuration
```properties
# sonar-project.properties
sonar.projectKey=my-project
sonar.organization=my-org
sonar.sources=src
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.javascript.lcov.reportPaths=coverage/lcov.info

# Quality gate
sonar.qualitygate.wait=true
```

### 3. CodeQL
GitHub's semantic code analysis engine

#### Setup
```yaml
# GitHub Actions only
codeql:
  runs-on: ubuntu-latest
  permissions:
    security-events: write
  
  strategy:
    matrix:
      language: [javascript, python, java, go]
  
  steps:
    - uses: actions/checkout@v4
    
    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
      with:
        languages: ${{ matrix.language }}
        queries: security-and-quality
    
    - name: Autobuild
      uses: github/codeql-action/autobuild@v2
    
    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2
```

#### Custom Queries
```ql
/**
 * @name Hardcoded credentials
 * @description Finds hardcoded credentials in code
 * @kind problem
 * @problem.severity error
 * @security-severity 8.8
 * @id custom/hardcoded-credentials
 * @tags security
 */

import javascript

from Assignment assign, StringLiteral str
where 
  assign.getRhs() = str and
  assign.getLhs().(VarAccess).getName().regexpMatch(".*(password|secret|key|token).*") and
  str.getValue().length() > 7
select assign, "Hardcoded credential: " + assign.getLhs()
```

### 4. Bandit (Python)
Security linter for Python

```yaml
# CI Integration
bandit:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Run Bandit
      run: |
        pip install bandit[toml]
        bandit -r . -f json -o bandit-report.json
        
        # Convert to SARIF
        pip install bandit-sarif-formatter
        bandit -r . -f sarif -o bandit.sarif
    
    - name: Upload SARIF
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: bandit.sarif
```

### 5. ESLint Security Plugins (JavaScript)
```yaml
# Installation
npm install --save-dev \
  eslint-plugin-security \
  eslint-plugin-no-secrets \
  eslint-config-security

# .eslintrc.js
module.exports = {
  extends: ['plugin:security/recommended'],
  plugins: ['security', 'no-secrets'],
  rules: {
    'no-secrets/no-secrets': 'error',
    'security/detect-eval-with-expression': 'error',
    'security/detect-non-literal-regexp': 'error',
    'security/detect-non-literal-fs-filename': 'error'
  }
};
```

## Integration Patterns

### 1. Fail-Fast vs Report-Only
```yaml
# Fail-fast approach
security-scan-blocking:
  steps:
    - name: Run security scan
      run: |
        semgrep --config=auto --error
        # Fails the pipeline on any finding

# Report-only approach
security-scan-informational:
  steps:
    - name: Run security scan
      continue-on-error: true
      run: |
        semgrep --config=auto --json > results.json
    
    - name: Comment PR
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v7
      with:
        script: |
          const results = require('./results.json');
          if (results.errors.length > 0) {
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `⚠️ Security scan found ${results.errors.length} issues`
            });
          }
```

### 2. Baseline Establishment
```yaml
# Create baseline
create-baseline:
  steps:
    - name: Generate baseline
      run: |
        # Run scan and save current findings
        semgrep --config=auto --json > .semgrep-baseline.json
        
        # Commit baseline
        git add .semgrep-baseline.json
        git commit -m "chore: update security baseline"

# Check against baseline
check-baseline:
  steps:
    - name: Compare with baseline
      run: |
        # Get current findings
        semgrep --config=auto --json > current.json
        
        # Compare with baseline
        python scripts/compare-findings.py .semgrep-baseline.json current.json
```

### 3. Progressive Enforcement
```yaml
# Gradual rollout
security-scan:
  steps:
    - name: Run scans with severity levels
      run: |
        # Block on critical/high
        semgrep --config=auto --severity=ERROR --error
        
        # Warn on medium
        semgrep --config=auto --severity=WARNING --json > warnings.json || true
        
        # Info on low
        semgrep --config=auto --severity=INFO --json > info.json || true
```

## Best Practices

### 1. Rule Tuning
```yaml
# .semgrep/config.yml
rules:
  - id: custom-rule
    pattern: $X
    paths:
      include:
        - "src/**/*.py"
      exclude:
        - "tests/**"
        - "**/migrations/**"
    fix: |
      # Suggested fix
    metadata:
      cwe: "CWE-798"
      owasp: "A3:2021"
      confidence: HIGH
```

### 2. Performance Optimization
```yaml
# Parallel scanning
parallel-scan:
  strategy:
    matrix:
      directory: [frontend, backend, services]
  steps:
    - name: Scan ${{ matrix.directory }}
      run: |
        semgrep --config=auto ${{ matrix.directory }}
```

### 3. Developer Experience
```yaml
# Pre-commit hooks
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/returntocorp/semgrep
    rev: v1.45.0
    hooks:
      - id: semgrep
        args: ['--config=auto', '--error']
        
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-r', 'src/']
```

### 4. Reporting and Metrics
```yaml
# Generate reports
generate-report:
  steps:
    - name: Aggregate results
      run: |
        # Combine all scan results
        jq -s '.[0] + .[1] + .[2]' \
          semgrep.json \
          bandit.json \
          eslint.json > combined-report.json
    
    - name: Generate HTML report
      run: |
        python scripts/generate-security-report.py \
          --input combined-report.json \
          --output security-report.html
    
    - name: Upload report
      uses: actions/upload-artifact@v3
      with:
        name: security-report
        path: security-report.html
```

## Tool Comparison

| Tool | Languages | Speed | Accuracy | Custom Rules | Free |
|------|-----------|--------|----------|--------------|------|
| Semgrep | 30+ | Fast | High | Yes | Yes |
| SonarQube | 25+ | Medium | Medium | Limited | Yes* |
| CodeQL | 10+ | Slow | Very High | Yes | Yes** |
| Bandit | Python | Fast | Medium | Yes | Yes |
| ESLint | JavaScript | Fast | Medium | Yes | Yes |

*Community edition only
**GitHub only

## Common Issues and Solutions

### 1. False Positives
```yaml
# Inline suppression
# nosemgrep: rule-id
password = get_from_env()  # nosemgrep: hardcoded-secret

# File-level suppression
# .semgrepignore
tests/
vendor/
*.min.js
```

### 2. Performance Issues
```yaml
# Optimize scanning
fast-scan:
  steps:
    - name: Scan only changed files
      run: |
        CHANGED_FILES=$(git diff --name-only HEAD~1)
        semgrep --config=auto $CHANGED_FILES
```

### 3. Integration Conflicts
```yaml
# Deduplicate findings
deduplicate:
  steps:
    - name: Merge and deduplicate
      run: |
        python scripts/deduplicate-findings.py \
          --inputs "*.sarif" \
          --output final-report.sarif
```