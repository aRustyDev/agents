# Project Focus Configuration Management

## Purpose
Manage project focus configuration files that define which projects to track, their cross-platform mappings, and filtering criteria.

## Overview
This process handles reading, validating, and querying the `~/.config/projects/focus.yaml` configuration file that controls project scope for commands like `/FindProject`.

## Configuration Schema

### Full Schema Definition
```yaml
# ~/.config/projects/focus.yaml
version: "1.0"
defaults:
  deadline_window: 14  # days
  completion_threshold: 80  # percent
  
projects:
  - name: "Project Name"               # Required: Display name
    description: "Brief description"   # Optional: Project purpose
    github_repo: "org/repo"           # Optional: GitHub repository
    platforms:                        # Required: At least one platform
      asana: "project_gid"
      jira: "PROJECT-KEY"
      notion: "page_id"
      github_projects: 123            # Numeric project ID
    tags:                            # Optional: For filtering
      - "backend"
      - "critical"
      - "q1-priority"
    settings:                        # Optional: Override defaults
      deadline_window: 7
      include_archived: false
    status: "active"                 # Optional: active|paused|archived
    
platform_config:
  asana:
    workspace_id: "123456789"
    custom_field_mapping:
      priority: "custom_fields.123"
      sprint: "custom_fields.456"
  jira:
    instance: "company.atlassian.net"
    project_categories:
      - "Development"
      - "Infrastructure"
  notion:
    database_ids:
      - "projects_db_uuid"
      - "roadmap_db_uuid"
  github:
    organizations:
      - "my-org"
      - "client-org"
    include_private: true
```

### Minimal Configuration
```yaml
version: "1.0"
projects:
  - name: "My Project"
    platforms:
      github_projects: 1
```

## Configuration Operations

### 1. Load and Validate Configuration
```bash
load_focus_config() {
    local config_file="${1:-$HOME/.config/projects/focus.yaml}"
    
    # Check if file exists
    if [ ! -f "$config_file" ]; then
        echo "Error: Focus configuration not found at $config_file" >&2
        echo "Run 'find-project --init' to create one" >&2
        return 1
    fi
    
    # Validate YAML syntax
    if ! yq eval '.' "$config_file" >/dev/null 2>&1; then
        echo "Error: Invalid YAML in $config_file" >&2
        return 1
    fi
    
    # Validate schema
    validate_focus_schema "$config_file"
}

validate_focus_schema() {
    local config_file="$1"
    local errors=()
    
    # Check version
    local version=$(yq eval '.version' "$config_file")
    if [ "$version" != "1.0" ]; then
        errors+=("Unsupported version: $version")
    fi
    
    # Check each project
    local project_count=$(yq eval '.projects | length' "$config_file")
    for i in $(seq 0 $((project_count - 1))); do
        local name=$(yq eval ".projects[$i].name" "$config_file")
        if [ "$name" = "null" ]; then
            errors+=("Project $i missing required 'name' field")
        fi
        
        local platforms=$(yq eval ".projects[$i].platforms" "$config_file")
        if [ "$platforms" = "null" ]; then
            errors+=("Project '$name' missing required 'platforms' field")
        fi
    done
    
    if [ ${#errors[@]} -gt 0 ]; then
        printf "Schema validation errors:\n" >&2
        printf " - %s\n" "${errors[@]}" >&2
        return 1
    fi
    
    return 0
}
```

### 2. Query Projects by Criteria
```bash
# Get all active projects
get_active_projects() {
    local config_file="$1"
    yq eval '.projects[] | select(.status != "archived")' "$config_file"
}

# Filter by tags
filter_projects_by_tag() {
    local config_file="$1"
    local tag="$2"
    yq eval ".projects[] | select(.tags[] == \"$tag\")" "$config_file"
}

# Get projects with GitHub repos
get_github_projects() {
    local config_file="$1"
    yq eval '.projects[] | select(.github_repo != null)' "$config_file"
}

# Get projects by platform
get_projects_by_platform() {
    local config_file="$1"
    local platform="$2"
    yq eval ".projects[] | select(.platforms.$platform != null)" "$config_file"
}
```

### 3. Project Correlation Mapping
```bash
# Build correlation map between platforms
build_correlation_map() {
    local config_file="$1"
    local temp_file=$(mktemp)
    
    # Create JSON map for easier lookup
    yq eval -o=json '.projects[] | {
        (.name): {
            "github": .github_repo,
            "platforms": .platforms
        }
    }' "$config_file" | jq -s 'add' > "$temp_file"
    
    echo "$temp_file"
}

# Find project by platform ID
find_project_by_id() {
    local config_file="$1"
    local platform="$2"
    local id="$3"
    
    yq eval ".projects[] | select(.platforms.$platform == \"$id\")" "$config_file"
}

# Get all platform IDs for a project
get_project_platform_ids() {
    local config_file="$1"
    local project_name="$2"
    
    yq eval ".projects[] | select(.name == \"$project_name\") | .platforms" "$config_file"
}
```

### 4. Configuration Initialization
```bash
# Create initial configuration
init_focus_config() {
    local config_dir="$HOME/.config/projects"
    local config_file="$config_dir/focus.yaml"
    
    mkdir -p "$config_dir"
    
    if [ -f "$config_file" ]; then
        echo "Configuration already exists at $config_file"
        read -p "Overwrite? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 1
        fi
    fi
    
    # Create template
    cat > "$config_file" << 'EOF'
version: "1.0"
defaults:
  deadline_window: 14
  completion_threshold: 80

projects:
  # Example project structure
  - name: "Example Project"
    description: "Remove this example and add your own projects"
    github_repo: "org/repo"  # Optional
    platforms:
      # Add at least one platform mapping
      github_projects: 1
      # asana: "project_gid"
      # jira: "PROJECT-KEY"
      # notion: "page_id"
    tags:
      - "example"
    status: "active"  # active|paused|archived

platform_config:
  # Configure your platforms here
  github:
    organizations:
      - "your-org"
    include_private: true
  
  # Uncomment and configure as needed:
  # asana:
  #   workspace_id: "your_workspace_id"
  # jira:
  #   instance: "your-company.atlassian.net"
  # notion:
  #   database_ids:
  #     - "your_database_id"
EOF
    
    echo "Created focus configuration at $config_file"
    echo "Edit this file to add your projects and platform mappings"
}
```

### 5. Configuration Merge Operations
```bash
# Merge platform-specific settings with project settings
get_project_settings() {
    local config_file="$1"
    local project_name="$2"
    
    # Get defaults
    local defaults=$(yq eval '.defaults' "$config_file")
    
    # Get project-specific overrides
    local overrides=$(yq eval ".projects[] | select(.name == \"$project_name\") | .settings // {}" "$config_file")
    
    # Merge (project settings override defaults)
    echo "$defaults" | yq eval-all '. * input' - <(echo "$overrides")
}

# Get platform configuration
get_platform_config() {
    local config_file="$1"
    local platform="$2"
    
    yq eval ".platform_config.$platform // {}" "$config_file"
}
```

## Error Handling

### Common Errors and Solutions
```bash
handle_config_error() {
    local error_type="$1"
    
    case "$error_type" in
        "missing_file")
            cat << EOF
No focus configuration found. Create one with:
  find-project --init
  
Or create manually at ~/.config/projects/focus.yaml
EOF
            ;;
        "invalid_yaml")
            cat << EOF
Invalid YAML syntax in configuration file.
Validate with: yq eval '.' ~/.config/projects/focus.yaml
EOF
            ;;
        "missing_platforms")
            cat << EOF
Project missing platform mappings. Each project needs at least one:
  platforms:
    github_projects: 123
    asana: "project_id"
    jira: "KEY"
    notion: "page_id"
EOF
            ;;
    esac
}
```

## Integration with Commands

### Usage in /FindProject
```bash
# Load configuration at command start
load_focus_config || exit 1

# Get projects to analyze
if [ -n "$TAG_FILTER" ]; then
    projects=$(filter_projects_by_tag "$CONFIG_FILE" "$TAG_FILTER")
else
    projects=$(get_active_projects "$CONFIG_FILE")
fi

# Process each project
echo "$projects" | while read -r project; do
    name=$(echo "$project" | yq eval '.name' -)
    platforms=$(echo "$project" | yq eval '.platforms' -)
    # ... analyze project across platforms
done
```

## Best Practices

1. **Version Control**: Keep focus.yaml in version control for team sharing
2. **Environment Variables**: Use ${ENV_VAR} syntax for sensitive values
3. **Modular Projects**: Group related repositories under one project
4. **Consistent Naming**: Use same project names across platforms
5. **Regular Updates**: Archive completed projects to reduce noise

## Migration Support

### From Legacy Formats
```bash
migrate_from_legacy() {
    local old_config="$1"
    local new_config="$2"
    
    # Example: Migrate from simple project list
    echo "version: \"1.0\"" > "$new_config"
    echo "projects:" >> "$new_config"
    
    while IFS= read -r project; do
        cat >> "$new_config" << EOF
  - name: "$project"
    platforms:
      github_projects: 1
    status: "active"
EOF
    done < "$old_config"
}
```

---

*This process provides robust configuration management for project-focused commands, enabling flexible project tracking across multiple platforms.*