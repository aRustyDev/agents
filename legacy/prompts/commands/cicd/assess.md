---
name: cicd-assess
description: Execute comprehensive CI/CD assessment for repository
author: Claude
version: 1.0.0
---

# Command: /cicd assess

Execute comprehensive CI/CD assessment to analyze current state and provide recommendations.

## Usage
```
/cicd assess [options]
```

## Options
- `--platform` - Override auto-detected platform (github/gitlab)
- `--depth` - Assessment depth (quick/standard/deep)
- `--focus` - Specific area focus (security/performance/cost/compliance)

## Workflow

### Phase 1: Discovery
1. **Run Process: CICDController**
   - Detect repository platform
   - Analyze project structure
   - Identify existing CI/CD configuration
   - Determine complexity level

2. **Gather Additional Context**
   ```bash
   # Check for CI/CD files
   find . -name ".github" -o -name ".gitlab-ci.yml" -o -name "Jenkinsfile" -o -name ".circleci"
   
   # Analyze repository statistics
   git log --pretty=format:"%ae" | sort | uniq -c | sort -nr  # Contributors
   find . -type f -name "*.yml" -o -name "*.yaml" | wc -l    # YAML files
   ```

### Phase 2: Analysis
3. **Configuration Analysis**
   - Parse existing CI/CD files
   - Identify stages and jobs
   - Analyze dependencies
   - Check for anti-patterns

4. **Security Assessment**
   - Secret management practices
   - Credential exposure risks
   - Security scanning integration
   - SAST/DAST implementation

5. **Performance Analysis**
   - Build times
   - Caching effectiveness
   - Parallelization opportunities
   - Resource utilization

6. **Cost Analysis**
   - Runner usage
   - Storage consumption
   - Third-party service costs
   - Optimization opportunities

### Phase 3: Gap Analysis
7. **Compare Against Best Practices**
   - Load appropriate complexity template
   - Identify missing components
   - Evaluate maturity level
   - Check compliance requirements

8. **Pattern Matching**
   - Identify applicable patterns
   - Check implementation completeness
   - Suggest pattern adoption

### Phase 4: Report Generation
9. **Generate Assessment Report**
   - Use template: CICD_ASSESSMENT.md
   - Include specific recommendations
   - Prioritize improvements
   - Create implementation roadmap

## Output Format

The assessment will generate a comprehensive report including:

1. **Executive Summary**
   - Current maturity level
   - Key findings
   - Priority recommendations

2. **Detailed Analysis**
   - Configuration review
   - Security assessment
   - Performance metrics
   - Cost analysis

3. **Recommendations**
   - Immediate actions
   - Short-term improvements
   - Long-term roadmap

4. **Implementation Guide**
   - Step-by-step instructions
   - Code examples
   - Migration paths

## Example Usage

### Basic Assessment
```
/cicd assess
```

### Deep Security-Focused Assessment
```
/cicd assess --depth deep --focus security
```

### Platform-Specific Assessment
```
/cicd assess --platform gitlab
```

## Assessment Criteria

### Maturity Levels
1. **Initial** - Ad-hoc or no CI/CD
2. **Managed** - Basic CI/CD implementation
3. **Defined** - Standardized processes
4. **Quantified** - Metrics-driven optimization
5. **Optimizing** - Continuous improvement

### Key Metrics
- **Build Success Rate**: Target >95%
- **Deployment Frequency**: Based on project type
- **Lead Time**: From commit to production
- **MTTR**: Mean time to recovery
- **Test Coverage**: Code and infrastructure

## Integration with Other Commands

After assessment, use:
- `/cicd plan` - Create implementation plan
- `/cicd implement` - Execute improvements
- `/cicd optimize` - Fine-tune performance