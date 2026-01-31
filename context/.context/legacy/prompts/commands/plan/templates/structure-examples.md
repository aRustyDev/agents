# Plan Structure Examples

## JSON Structure Examples

### issues.json
```json
[
  {
    "title": "Issue title",
    "body": "Detailed description",
    "labels": ["enhancement", "p2-medium", "effort-medium"],
    "milestone": 1,
    "assignees": []
  }
]
```

### milestones.json
```json
[
  {
    "title": "v1.0 - MVP",
    "description": "Minimum viable product",
    "due_on": "2024-03-31T00:00:00Z"
  }
]
```

### projects.json
```json
[
  {
    "name": "Project Name",
    "body": "Project description",
    "columns": ["To Do", "In Progress", "Review", "Done"]
  }
]
```

### labels.json
```json
[
  {
    "name": "p0-critical",
    "color": "B60205",
    "description": "Critical priority"
  },
  {
    "name": "p1-high",
    "color": "D93F0B",
    "description": "High priority"
  },
  {
    "name": "effort-small",
    "color": "C5DEF5",
    "description": "Small effort (< 1 day)"
  }
]
```

## Script Structure

### execute_plan.sh
The execution script follows this structure:
1. Pre-execution validation
2. Create labels
3. Create milestones (track mapping)
4. Create issues (with milestone references)
5. Create projects
6. Post-execution summary

See `scripts/execute_plan.sh` for full implementation.