# Multi-Platform Project Management Sync

## Purpose
Unified integration layer for synchronizing project data across multiple project management platforms (Asana, Jira, Notion, GitHub Projects).

## Overview
This process provides a consistent interface for querying and aggregating project data from different PM tools, handling authentication, rate limiting, and data normalization.

## Supported Platforms

### 1. Asana
```bash
# API Authentication
export ASANA_API_TOKEN="your-token"

# Query projects
query_asana_projects() {
    local workspace_id="$1"
    curl -H "Authorization: Bearer $ASANA_API_TOKEN" \
         "https://app.asana.com/api/1.0/workspaces/$workspace_id/projects"
}

# Get project details with custom fields
get_asana_project() {
    local project_gid="$1"
    curl -H "Authorization: Bearer $ASANA_API_TOKEN" \
         "https://app.asana.com/api/1.0/projects/$project_gid?opt_fields=name,notes,status,due_date,custom_fields"
}
```

### 2. Jira
```bash
# API Authentication  
export JIRA_API_TOKEN="your-token"
export JIRA_EMAIL="your-email"
export JIRA_INSTANCE="company.atlassian.net"

# Query projects using JQL
query_jira_projects() {
    local jql="project in (projectsLeadByUser()) AND statusCategory != Done"
    curl -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
         -H "Accept: application/json" \
         "https://$JIRA_INSTANCE/rest/api/3/search?jql=$jql"
}

# Get project details
get_jira_project() {
    local project_key="$1"
    curl -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
         "https://$JIRA_INSTANCE/rest/api/3/project/$project_key"
}
```

### 3. Notion
```bash
# API Authentication
export NOTION_API_TOKEN="your-token"

# Query database for projects
query_notion_projects() {
    local database_id="$1"
    curl -X POST "https://api.notion.com/v1/databases/$database_id/query" \
         -H "Authorization: Bearer $NOTION_API_TOKEN" \
         -H "Notion-Version: 2022-06-28" \
         -H "Content-Type: application/json"
}

# Get page details
get_notion_page() {
    local page_id="$1"
    curl "https://api.notion.com/v1/pages/$page_id" \
         -H "Authorization: Bearer $NOTION_API_TOKEN" \
         -H "Notion-Version: 2022-06-28"
}
```

### 4. GitHub Projects
```bash
# Using GitHub CLI (gh)
# Authentication handled by gh

# Query organization projects
query_github_projects() {
    local org="$1"
    gh api graphql -f query='
    query($org: String!) {
        organization(login: $org) {
            projectsV2(first: 100) {
                nodes {
                    id
                    title
                    shortDescription
                    closed
                }
            }
        }
    }' -f org="$org"
}

# Get project details with items
get_github_project() {
    local project_id="$1"
    gh api graphql -f query='
    query($projectId: ID!) {
        node(id: $projectId) {
            ... on ProjectV2 {
                title
                items(first: 100) {
                    nodes {
                        content {
                            ... on Issue {
                                title
                                state
                                labels(first: 10) {
                                    nodes { name }
                                }
                            }
                        }
                    }
                }
            }
        }
    }' -f projectId="$project_id"
}
```

## Unified Data Model

All platforms normalize to this structure:

```json
{
    "id": "platform_specific_id",
    "platform": "asana|jira|notion|github",
    "name": "Project Name",
    "description": "Project description",
    "status": "active|on_hold|completed|cancelled",
    "health": {
        "overdue_items": 0,
        "total_items": 0,
        "completed_items": 0,
        "blocked_items": 0
    },
    "dates": {
        "created": "ISO8601",
        "due": "ISO8601",
        "last_activity": "ISO8601"
    },
    "priority": "critical|high|medium|low",
    "milestones": [
        {
            "name": "Milestone 1",
            "due_date": "ISO8601",
            "status": "overdue|upcoming|completed"
        }
    ],
    "metrics": {
        "completion_percentage": 85,
        "days_until_due": 7,
        "stale_items": 3
    },
    "links": {
        "github_repo": "org/repo",
        "external_url": "https://..."
    }
}
```

## Rate Limiting

Implement exponential backoff for all platforms:

```bash
api_call_with_retry() {
    local platform="$1"
    local request="$2"
    local max_retries=3
    local retry=0
    local wait_time=1
    
    while [ $retry -lt $max_retries ]; do
        response=$(eval "$request" 2>&1)
        status=$?
        
        if [ $status -eq 0 ]; then
            echo "$response"
            return 0
        fi
        
        # Check for rate limit
        if echo "$response" | grep -q "rate limit\|429"; then
            echo "Rate limit hit for $platform, waiting ${wait_time}s..." >&2
            sleep $wait_time
            wait_time=$((wait_time * 2))
            retry=$((retry + 1))
        else
            echo "Error calling $platform API: $response" >&2
            return 1
        fi
    done
    
    echo "Max retries reached for $platform" >&2
    return 1
}
```

## Parallel Fetching

Fetch from all platforms concurrently:

```bash
fetch_all_platforms() {
    local config_file="$1"
    local temp_dir=$(mktemp -d)
    
    # Start background jobs for each platform
    fetch_asana_data "$config_file" > "$temp_dir/asana.json" &
    fetch_jira_data "$config_file" > "$temp_dir/jira.json" &
    fetch_notion_data "$config_file" > "$temp_dir/notion.json" &
    fetch_github_data "$config_file" > "$temp_dir/github.json" &
    
    # Wait for all to complete
    wait
    
    # Merge results
    jq -s 'add' "$temp_dir"/*.json
    rm -rf "$temp_dir"
}
```

## Error Handling

Each platform adapter implements graceful degradation:

```bash
safe_platform_fetch() {
    local platform="$1"
    local fetch_function="$2"
    
    if ! command -v "$fetch_function" &> /dev/null; then
        echo "{\"error\": \"$platform integration not configured\"}" >&2
        return 1
    fi
    
    if ! $fetch_function 2>/dev/null; then
        echo "{\"error\": \"Failed to fetch from $platform\"}" >&2
        return 1
    fi
}
```

## Caching

Implement 15-minute cache to reduce API calls:

```bash
CACHE_DIR="$HOME/.cache/find-project"
CACHE_TTL=900  # 15 minutes

get_cached_or_fetch() {
    local cache_key="$1"
    local fetch_command="$2"
    local cache_file="$CACHE_DIR/$cache_key.json"
    
    mkdir -p "$CACHE_DIR"
    
    # Check if cache exists and is fresh
    if [ -f "$cache_file" ]; then
        local age=$(($(date +%s) - $(stat -f %m "$cache_file" 2>/dev/null || stat -c %Y "$cache_file")))
        if [ $age -lt $CACHE_TTL ]; then
            cat "$cache_file"
            return 0
        fi
    fi
    
    # Fetch fresh data
    local data=$($fetch_command)
    echo "$data" > "$cache_file"
    echo "$data"
}
```

## Usage Example

```bash
# Load platform sync
!load integrations/multi-platform-sync

# Fetch all project data
projects=$(fetch_all_platforms "~/.config/projects/focus.yaml")

# Process each project
echo "$projects" | jq -r '.[] | select(.status == "active")'
```

## Platform-Specific Notes

### Asana
- Custom fields must be configured per workspace
- Use opt_fields to minimize payload size
- Workspace ID required for all queries

### Jira
- JQL provides powerful filtering
- Issue types and statuses vary by instance
- API v3 recommended over v2

### Notion
- Database schema must be predefined
- Properties map to our unified model
- Rate limits are strict (3 requests/second)

### GitHub
- GraphQL API more efficient for complex queries
- Project items can be issues or notes
- Organization-level permissions required

## Extensibility

To add a new platform:

1. Create adapter functions following naming convention
2. Implement data normalization to unified model
3. Add platform to fetch_all_platforms
4. Update configuration schema
5. Document authentication requirements

---

*This process enables consistent multi-platform project data aggregation for any command that needs cross-platform project information.*