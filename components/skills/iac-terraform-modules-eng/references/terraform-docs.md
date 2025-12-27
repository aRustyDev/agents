# terraform-docs Reference

terraform-docs is a utility to generate documentation from Terraform modules in various output formats. It automatically extracts inputs, outputs, providers, and resources from your module code.

## Installation

```bash
# macOS
brew install terraform-docs

# Linux
curl -L https://github.com/terraform-docs/terraform-docs/releases/latest/download/terraform-docs-linux-amd64.tar.gz | tar xz
sudo mv terraform-docs /usr/local/bin/

# Go install
go install github.com/terraform-docs/terraform-docs@latest

# Docker
docker run --rm -v $(pwd):/terraform-docs quay.io/terraform-docs/terraform-docs:latest .

# Windows
choco install terraform-docs
# or
scoop install terraform-docs
```

## CLI Commands

```bash
# Generate markdown table format
terraform-docs markdown table .

# Generate markdown document format
terraform-docs markdown document .

# Write output to README.md
terraform-docs markdown table . > README.md

# Use custom configuration file
terraform-docs -c .terraform-docs.yml .

# Generate JSON output
terraform-docs json .

# Generate YAML output
terraform-docs yaml .

# Generate AsciiDoc
terraform-docs asciidoc table .

# Show version
terraform-docs version
```

## Output Formats

| Format | Command | Use Case |
|--------|---------|----------|
| Markdown Table | `markdown table` | GitHub/GitLab READMEs |
| Markdown Document | `markdown document` | Documentation sites |
| JSON | `json` | API consumption, custom processing |
| YAML | `yaml` | Configuration files |
| TOML | `toml` | TOML-based configs |
| AsciiDoc | `asciidoc table` | AsciiDoc documentation |
| tfvars | `tfvars hcl` | Generate .tfvars template |

## Configuration File

### Basic Configuration

```yaml
# .terraform-docs.yml
formatter: markdown table

version: ">= 0.16.0"

header-from: main.tf
footer-from: ""

recursive:
  enabled: false
  path: modules

sections:
  hide: []
  show: []

content: ""

output:
  file: README.md
  mode: inject
  template: |-
    <!-- BEGIN_TF_DOCS -->
    {{ .Content }}
    <!-- END_TF_DOCS -->

output-values:
  enabled: false
  from: ""

sort:
  enabled: true
  by: name

settings:
  anchor: true
  color: true
  default: true
  description: false
  escape: true
  hide-empty: false
  html: true
  indent: 2
  lockfile: true
  read-comments: true
  required: true
  sensitive: true
  type: true
```

### Full Configuration Example

```yaml
# .terraform-docs.yml
formatter: markdown table

version: ">= 0.16.0"

header-from: main.tf

sections:
  show:
    - header
    - requirements
    - providers
    - inputs
    - outputs
    - resources

content: |-
  {{ .Header }}

  ## Usage

  ```hcl
  module "{{ .Module.Name }}" {
    source  = "your-org/{{ .Module.Name }}/aws"
    version = "~> {{ .Module.Version }}"

    {{- range .Module.Inputs }}
    {{ .Name }} = {{ if eq .Type "string" }}"value"{{ else }}value{{ end }}
    {{- end }}
  }
  ```

  {{ .Requirements }}

  {{ .Providers }}

  {{ .Resources }}

  {{ .Inputs }}

  {{ .Outputs }}

  ## License

  MIT License

output:
  file: README.md
  mode: inject
  template: |-
    <!-- BEGIN_TF_DOCS -->
    {{ .Content }}
    <!-- END_TF_DOCS -->

sort:
  enabled: true
  by: required

settings:
  anchor: true
  color: true
  default: true
  escape: true
  hide-empty: false
  html: true
  indent: 2
  lockfile: true
  read-comments: true
  required: true
  sensitive: true
  type: true
```

## Inject Mode

Use inject mode to update only the documentation section while preserving the rest of the README:

```markdown
# My Terraform Module

Custom introduction and overview here.

<!-- BEGIN_TF_DOCS -->
This content will be replaced by terraform-docs
<!-- END_TF_DOCS -->

## Additional Information

Custom content after the generated docs.
```

```yaml
# .terraform-docs.yml
output:
  file: README.md
  mode: inject
  template: |-
    <!-- BEGIN_TF_DOCS -->
    {{ .Content }}
    <!-- END_TF_DOCS -->
```

## Custom Templates

### Go Template Syntax

```yaml
content: |-
  # {{ .Module.Name }}

  {{ .Header }}

  ## Requirements

  | Name | Version |
  |------|---------|
  {{- range .Requirements }}
  | {{ .Name }} | {{ .Version }} |
  {{- end }}

  ## Inputs

  | Name | Description | Type | Default | Required |
  |------|-------------|------|---------|:--------:|
  {{- range .Inputs }}
  | {{ .Name }} | {{ .Description }} | `{{ .Type }}` | {{ .Default }} | {{ .Required }} |
  {{- end }}

  ## Outputs

  | Name | Description |
  |------|-------------|
  {{- range .Outputs }}
  | {{ .Name }} | {{ .Description }} |
  {{- end }}
```

### Available Template Variables

```go
// Module information
{{ .Module.Name }}
{{ .Module.Version }}
{{ .Module.ProviderRequirements }}

// Content sections
{{ .Header }}
{{ .Footer }}
{{ .Inputs }}
{{ .Outputs }}
{{ .Providers }}
{{ .Requirements }}
{{ .Resources }}
{{ .Modules }}

// Iterate over items
{{ range .Inputs }}
  {{ .Name }}
  {{ .Type }}
  {{ .Description }}
  {{ .Default }}
  {{ .Required }}
{{ end }}

{{ range .Outputs }}
  {{ .Name }}
  {{ .Description }}
  {{ .Value }}
  {{ .Sensitive }}
{{ end }}

{{ range .Providers }}
  {{ .Name }}
  {{ .Alias }}
  {{ .Version }}
{{ end }}

{{ range .Resources }}
  {{ .Type }}
  {{ .Name }}
  {{ .Mode }}
  {{ .Provider }}
{{ end }}
```

## Pre-commit Hook

### Installation

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/terraform-docs/terraform-docs
    rev: v0.17.0
    hooks:
      - id: terraform-docs-go
        args: ["--config", ".terraform-docs.yml"]
```

### Alternative with system binary

```yaml
repos:
  - repo: https://github.com/terraform-docs/terraform-docs
    rev: v0.17.0
    hooks:
      - id: terraform-docs-system
        args: ["markdown", "table", "--output-file", "README.md", "."]
```

### Multiple modules

```yaml
repos:
  - repo: https://github.com/terraform-docs/terraform-docs
    rev: v0.17.0
    hooks:
      - id: terraform-docs-go
        args: ["--config", ".terraform-docs.yml"]
        files: ^modules/
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Terraform Docs
on:
  push:
    branches: [main]
    paths:
      - '**.tf'
      - '.terraform-docs.yml'
  pull_request:
    paths:
      - '**.tf'
      - '.terraform-docs.yml'

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.ref }}

      - name: Render terraform docs
        uses: terraform-docs/gh-actions@v1
        with:
          working-dir: .
          output-file: README.md
          output-method: inject
          git-push: true
          config-file: .terraform-docs.yml
```

### GitHub Actions (multiple modules)

```yaml
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.ref }}

      - name: Render terraform docs for all modules
        uses: terraform-docs/gh-actions@v1
        with:
          find-dir: modules/
          output-file: README.md
          output-method: inject
          git-push: true
```

### GitLab CI

```yaml
terraform-docs:
  image: quay.io/terraform-docs/terraform-docs:latest
  stage: docs
  script:
    - terraform-docs -c .terraform-docs.yml .
  artifacts:
    paths:
      - README.md
  only:
    changes:
      - "*.tf"
      - ".terraform-docs.yml"
```

## Recursive Documentation

Generate docs for nested modules:

```yaml
# .terraform-docs.yml
recursive:
  enabled: true
  path: modules
```

```bash
# Directory structure
module/
├── main.tf
├── README.md
├── .terraform-docs.yml
└── modules/
    ├── submodule-a/
    │   ├── main.tf
    │   └── README.md
    └── submodule-b/
        ├── main.tf
        └── README.md

# Generate docs for all
terraform-docs -c .terraform-docs.yml .
```

## Lockfile Integration

Show provider versions from lockfile:

```yaml
settings:
  lockfile: true
```

This reads `.terraform.lock.hcl` to show actual resolved provider versions.

## Best Practices

### 1. Use Inject Mode

Keep custom content in README while auto-updating the docs section:

```markdown
# My Module

Custom introduction explaining the module purpose.

<!-- BEGIN_TF_DOCS -->
<!-- END_TF_DOCS -->

## Examples

Custom examples section.
```

### 2. Add Descriptions Everywhere

terraform-docs extracts descriptions from your code:

```hcl
variable "name" {
  description = "Name of the resource. Used for tagging and identification."
  type        = string
}

output "id" {
  description = "The unique identifier of the created resource."
  value       = aws_resource.main.id
}
```

### 3. Use Header Comments

Add module overview in main.tf:

```hcl
/**
 * # AWS VPC Module
 *
 * This module creates a VPC with public and private subnets.
 *
 * ## Features
 * - Multi-AZ deployment
 * - NAT Gateway support
 * - DNS configuration
 */

resource "aws_vpc" "main" {
  # ...
}
```

### 4. Sort Inputs by Required

```yaml
sort:
  enabled: true
  by: required
```

### 5. Show Types and Defaults

```yaml
settings:
  type: true
  default: true
  required: true
```

### 6. Hide Sensitive Defaults

```yaml
settings:
  sensitive: true  # Shows "sensitive" instead of actual value
```

### 7. Pre-commit Hook

Always regenerate docs before commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/terraform-docs/terraform-docs
    rev: v0.17.0
    hooks:
      - id: terraform-docs-go
```

### 8. CI Validation

Check docs are up-to-date in CI:

```yaml
- name: Check terraform-docs
  run: |
    terraform-docs -c .terraform-docs.yml .
    git diff --exit-code README.md
```

## Troubleshooting

### Empty Output

```bash
# Check if .tf files exist
ls *.tf

# Run with verbose
terraform-docs --debug markdown table .
```

### Missing Descriptions

Ensure variables and outputs have `description` attributes:

```hcl
variable "name" {
  description = "Required: Add a description here"
  type        = string
}
```

### Config Not Found

```bash
# Explicit config path
terraform-docs -c /path/to/.terraform-docs.yml .

# Check YAML syntax
cat .terraform-docs.yml | yq .
```

## Resources

- [terraform-docs GitHub](https://github.com/terraform-docs/terraform-docs)
- [Documentation](https://terraform-docs.io/)
- [Configuration Reference](https://terraform-docs.io/user-guide/configuration/)
- [GitHub Action](https://github.com/terraform-docs/gh-actions)
