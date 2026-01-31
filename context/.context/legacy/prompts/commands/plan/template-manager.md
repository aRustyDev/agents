---
module: PlanTemplateManager
scope: context
triggers: []
conflicts: []
dependencies: []
priority: medium
---

# PlanTemplateManager - Template Management

## Purpose
Manages templates for plan command, including loading, saving, and import/export functionality.

## Template Functions

### Load Template
```bash
load_template() {
  local template_name=$1
  local template_file=".plan/templates/${template_name}.json"
  
  if [ -f "$template_file" ]; then
    cat "$template_file"
  else
    echo "{}" # Return empty object if template not found
  fi
}
```

### Save Template
```bash
save_template() {
  local template_name=$1
  local template_data=$2
  
  mkdir -p .plan/templates
  echo "$template_data" > ".plan/templates/${template_name}.json"
  echo "✅ Template saved: $template_name"
}
```

### List Templates
```bash
list_templates() {
  if [ -d ".plan/templates" ] && [ "$(ls -A .plan/templates)" ]; then
    echo "📄 Available templates:"
    for template in .plan/templates/*.json; do
      template_name=$(basename "$template" .json)
      echo "  • $template_name"
    done
  else
    echo "ℹ️ No templates found"
  fi
}
```

## Import/Export Functions

### Import from Markdown
```bash
import_from_markdown() {
  local markdown_file=$1
  local session_dir=$2
  
  # Parse markdown for task items
  grep -E "^- \[ \]" "$markdown_file" | while read -r line; do
    # Extract task title
    task_title=$(echo "$line" | sed 's/^- \[ \] //')
    echo "$task_title"
  done > "$session_dir/imported_tasks.txt"
}
```

### Export to Markdown
```bash
export_to_markdown() {
  local session_dir=$1
  local output_file=$2
  
  cat > "$output_file" << EOF
# Project Plan
Generated: $(date)

## Issues
$(jq -r '.[] | "- [ ] \(.title)"' "$session_dir/issues.json")

## Milestones
$(jq -r '.[] | "### \(.title)\n\(.description)\n"' "$session_dir/milestones.json")
EOF
}
```

### Import from JSON
```bash
import_from_json() {
  local json_file=$1
  local session_dir=$2
  
  # Validate JSON
  if ! jq empty "$json_file" 2>/dev/null; then
    echo "❌ Invalid JSON file"
    return 1
  fi
  
  # Import issues
  jq '.issues' "$json_file" > "$session_dir/issues.json"
  
  # Import milestones
  jq '.milestones' "$json_file" > "$session_dir/milestones.json"
  
  echo "✅ Imported from JSON"
}
```

## Template Schema

Default template structure:
```json
{
  "name": "template_name",
  "description": "Template description",
  "issues": [
    {
      "title": "Issue title",
      "body": "Issue description",
      "labels": ["label1", "label2"]
    }
  ],
  "milestones": [
    {
      "title": "Milestone title",
      "description": "Milestone description",
      "due_on": "YYYY-MM-DD"
    }
  ],
  "project": {
    "title": "Project title",
    "body": "Project description",
    "columns": ["To Do", "In Progress", "Done"]
  }
}
```

## Usage Examples

```bash
# Save current session as template
save_template "web-app" "$(cat .plan/sessions/current/plan.json)"

# Load template for new project
template_data=$(load_template "web-app")

# Import tasks from markdown
import_from_markdown "tasks.md" ".plan/sessions/current"

# Export plan to markdown
export_to_markdown ".plan/sessions/current" "project-plan.md"
```