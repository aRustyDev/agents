# CI/CD Extension Requirements Document

## Overview
These CI/CD extensions will be placed in user-level Claude configurations and used across multiple different repositories of varying size, scope, and complexity levels. The solution must be modular, scoped, and include conditional loading logic to load appropriate prompts for each project context.

## 1. Scope & Complexity Requirements

### Project Coverage
- **Must support all ranges of projects**: From simple single-file applications to complex enterprise systems
- **Modular and scoped prompts**: Each prompt should be as focused and modular as possible
- **Conditional loading**: Include logic throughout dependent prompts to conditionally load the correct prompts for the project

### CI/CD Pattern Support
- Build/Test/Deploy (traditional)
- GitOps
- Progressive Delivery
- All other major CI/CD patterns
- Each pattern requires dedicated prompt files

### Pipeline Complexity Levels
- Simple (basic build and test)
- Moderate (multi-stage, matrix builds)
- Complex (dynamic pipelines, conditional workflows)
- Enterprise (multi-region, compliance-heavy)
- Must include prompts for each complexity level

## 2. Platform Requirements

### Platform Parity
- **Equal depth for both GitHub Actions and GitLab CI**
- Support all platform-specific features:
  - GitHub: environments, OIDC, marketplace actions
  - GitLab: runners, environments, includes, templates
- Use platform-specific features when working with that platform

### Migration Support
- **Detailed and omni-directional migration guides**
- GitHub → GitLab migration
- GitLab → GitHub migration
- Pattern migration (e.g., traditional → GitOps)

## 3. Integration Requirements

### Cloud Providers
All major cloud providers require API integration support:
- AWS
- Azure
- Google Cloud Platform
- DigitalOcean
- Linode
- Guides location: `guides/cloud/<provider>/`

### Container Registries
All major container registries need individual guides:
- Docker Hub
- Amazon ECR
- Azure Container Registry
- Google Container Registry
- Harbor
- Quay.io
- Guides location: `guides/registries/<registry>/`

### Monitoring & Observability
Primary monitoring tools requiring integration:
- Sentry
- Codecov
- GitGuardian
- Prometheus
- OpenTelemetry

### Infrastructure as Code (IaC)
Required IaC tool support:
- **Primary**: Terraform, OpenTofu
- **Secondary**: Terragrunt, Ansible
- **Additional Required**:
  - Salt
  - Puppet
  - Azure Resource Manager (ARM) templates
  - Bicep
  - Vagrant
  - Packer
  - HashiCorp Vault
  - AWS CloudFormation templates

### Security Scanning
Support for all major open source tools:
- **SAST** (Static Application Security Testing)
- **DAST** (Dynamic Application Security Testing)
- **Dependency Scanning**

## 4. Operational Requirements

### Performance
- Include performance optimization capabilities
- Pipeline execution time optimization
- Resource utilization optimization
- Caching strategies

### Governance
- **Optional approval workflows**: Must be toggleable
- **Optional change management processes**: ITIL-compatible when enabled
- **Cost optimization tracking**: Monitor and optimize CI/CD costs

## 5. User Context

### Primary Use
- Primarily used by a single developer
- May be shared with others
- Must accommodate varying levels of CI/CD expertise

### Documentation Requirements
- Clear, modular documentation
- Progressive disclosure of complexity
- Examples for each pattern and complexity level

## 6. Structural Requirements

### File Organization
- Patterns must go in the `patterns/` directory
- Maintain consistent structure across all modules
- Support conditional loading based on project context
- Each module should be self-contained with minimal dependencies

### Extensibility
- Easy to add new platforms
- Simple to integrate new tools
- Clear extension points for custom patterns
- Consistent naming conventions
