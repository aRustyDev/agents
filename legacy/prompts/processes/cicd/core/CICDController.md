# Process: CICDController

## Purpose
Master controller for intelligent CI/CD module loading based on project context

## Trigger
- Any CI/CD related query
- Commands starting with `/cicd`
- Repository CI/CD assessment requests

## Steps

### 1. Project Analysis
```yaml
1.1 Detect Repository Context
    - Run: git config --get remote.origin.url
    - Identify platform (GitHub/GitLab)
    - Check for existing CI/CD files
    
1.2 Analyze Project Structure
    - Language detection
    - Monorepo vs single service
    - Existing IaC tools
    - Current CI/CD patterns

1.3 Determine Complexity Level
    IF monorepo OR microservices:
        complexity = "enterprise"
    ELIF multiple_stages AND matrix_builds:
        complexity = "complex"
    ELIF basic_pipeline:
        complexity = "moderate"
    ELSE:
        complexity = "simple"
```

### 2. Module Selection
```yaml
2.1 Load Base Modules
    - Load: processes/cicd/complexity/${complexity}.md
    - Load: guides/cicd/platforms/${platform}/

2.2 Pattern Detection
    FOR EACH detected_pattern:
        - Load: patterns/cicd/${pattern}/

2.3 Integration Loading
    IF terraform_detected:
        - Load: guides/iac/terraform/
    IF aws_detected:
        - Load: guides/cloud/aws/
    # Continue for all detected tools
```

### 3. Context Assembly
```yaml
3.1 Create Working Context
    context = {
        platform: ${detected_platform},
        complexity: ${complexity_level},
        patterns: ${applicable_patterns},
        integrations: ${required_integrations},
        constraints: ${identified_constraints}
    }

3.2 Load Relevant Processes
    - Only load processes matching context
    - Skip unneeded complexity levels
    - Exclude irrelevant platforms
```

## Detection Functions

### Platform Detection
```bash
detect_platform() {
    local remote_url=$(git config --get remote.origin.url 2>/dev/null)
    
    if [[ "$remote_url" =~ github\.com ]]; then
        echo "github"
    elif [[ "$remote_url" =~ gitlab\.com ]] || [[ "$remote_url" =~ gitlab\. ]]; then
        echo "gitlab"
    else
        echo "unknown"
    fi
}
```

### Existing CI/CD Detection
```bash
detect_existing_cicd() {
    local ci_files=()
    
    # GitHub Actions
    [[ -d ".github/workflows" ]] && ci_files+=("github-actions")
    
    # GitLab CI
    [[ -f ".gitlab-ci.yml" ]] && ci_files+=("gitlab-ci")
    
    # Other CI systems
    [[ -f "Jenkinsfile" ]] && ci_files+=("jenkins")
    [[ -f ".circleci/config.yml" ]] && ci_files+=("circleci")
    [[ -f ".travis.yml" ]] && ci_files+=("travis")
    
    echo "${ci_files[@]}"
}
```

### Language Detection
```bash
detect_languages() {
    local languages=()
    
    # Package managers and language files
    [[ -f "package.json" ]] && languages+=("javascript")
    [[ -f "requirements.txt" ]] || [[ -f "setup.py" ]] || [[ -f "pyproject.toml" ]] && languages+=("python")
    [[ -f "go.mod" ]] && languages+=("go")
    [[ -f "Cargo.toml" ]] && languages+=("rust")
    [[ -f "pom.xml" ]] || [[ -f "build.gradle" ]] && languages+=("java")
    [[ -f "composer.json" ]] && languages+=("php")
    [[ -f "Gemfile" ]] && languages+=("ruby")
    [[ -f "*.csproj" ]] || [[ -f "*.sln" ]] && languages+=("dotnet")
    
    echo "${languages[@]}"
}
```

### Project Structure Analysis
```bash
analyze_project_structure() {
    local structure="single"
    
    # Check for monorepo indicators
    if [[ -f "lerna.json" ]] || [[ -f "nx.json" ]] || [[ -f "rush.json" ]]; then
        structure="monorepo"
    elif [[ -f "pnpm-workspace.yaml" ]] || [[ -f "yarn.lock" && -d "packages" ]]; then
        structure="monorepo"
    elif [[ -d "services" ]] && [[ $(find services -maxdepth 2 -name "Dockerfile" | wc -l) -gt 2 ]]; then
        structure="microservices"
    fi
    
    echo "$structure"
}
```

### IaC Tool Detection
```bash
detect_iac_tools() {
    local tools=()
    
    # Terraform variants
    [[ -f "*.tf" ]] || [[ -d ".terraform" ]] && tools+=("terraform")
    [[ -f ".terraform-version" ]] && tools+=("tfenv")
    [[ -f "terragrunt.hcl" ]] && tools+=("terragrunt")
    
    # Other IaC tools
    [[ -f "ansible.cfg" ]] || [[ -d "playbooks" ]] && tools+=("ansible")
    [[ -f "Pulumi.yaml" ]] && tools+=("pulumi")
    [[ -f "template.yaml" ]] || [[ -f "template.yml" ]] && tools+=("cloudformation")
    [[ -f "*.bicep" ]] && tools+=("bicep")
    
    echo "${tools[@]}"
}
```

## Output
- Loaded module list
- Project context object
- Ready for CI/CD operations

## Module Loading Log Format
```yaml
loaded_modules:
  core:
    - processes/cicd/complexity/${complexity}.md
  platform:
    - guides/cicd/platforms/${platform}/
  patterns:
    - patterns/cicd/${pattern1}/
    - patterns/cicd/${pattern2}/
  integrations:
    - guides/cloud/${cloud}/
    - guides/iac/${iac_tool}/
    - guides/security/${security_tool}/
```