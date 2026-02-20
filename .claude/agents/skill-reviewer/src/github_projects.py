"""GitHub Projects V2 API operations for project-status management."""

import subprocess
from dataclasses import dataclass

from .graphql import execute_query


@dataclass
class ProjectItem:
    """A GitHub project item (issue linked to a project)."""

    item_id: str
    issue_number: int
    title: str
    status: str | None
    assignees: list[str]
    created_at: str
    updated_at: str


@dataclass
class ProjectField:
    """A GitHub project field definition."""

    id: str
    name: str
    field_type: str  # SingleSelect, Text, Number, Date, etc.
    options: list[dict] | None = None  # For SingleSelect fields


def get_project_id(owner: str, project_number: int) -> str | None:
    """Get the node ID of a GitHub project.

    Args:
        owner: Repository/org owner
        project_number: Project number (visible in URL)

    Returns:
        Project node ID or None
    """
    # Try user project first
    success, data = execute_query("get-user-project", {"owner": owner, "number": project_number})

    if success and data:
        try:
            return data["data"]["user"]["projectV2"]["id"]
        except (KeyError, TypeError):
            pass

    # Try organization project
    success, data = execute_query("get-org-project", {"owner": owner, "number": project_number})

    if success and data:
        try:
            return data["data"]["organization"]["projectV2"]["id"]
        except (KeyError, TypeError):
            pass

    return None


def get_project_fields(project_id: str) -> list[ProjectField]:
    """Get all fields defined in a project.

    Args:
        project_id: Project node ID

    Returns:
        List of ProjectField objects
    """
    success, data = execute_query("get-project-fields", {"projectId": project_id})

    if not success or not data:
        return []

    fields = []

    try:
        for node in data["data"]["node"]["fields"]["nodes"]:
            if not node:
                continue
            fields.append(
                ProjectField(
                    id=node["id"],
                    name=node["name"],
                    field_type=node.get("dataType", "Unknown"),
                    options=node.get("options"),
                )
            )
    except (KeyError, TypeError):
        pass

    return fields


def get_status_field(project_id: str) -> ProjectField | None:
    """Get the Status field from a project.

    Args:
        project_id: Project node ID

    Returns:
        ProjectField for Status or None
    """
    fields = get_project_fields(project_id)
    for field in fields:
        if field.name.lower() == "status":
            return field
    return None


def get_issue_project_item(
    project_id: str, issue_number: int, owner: str, repo: str
) -> ProjectItem | None:
    """Get project item for an issue.

    Args:
        project_id: Project node ID
        issue_number: Issue number
        owner: Repository owner
        repo: Repository name

    Returns:
        ProjectItem or None
    """
    # First get the issue node ID
    issue_result = subprocess.run(
        ["gh", "api", f"/repos/{owner}/{repo}/issues/{issue_number}", "--jq", ".node_id"],
        capture_output=True,
        text=True,
        check=False,
    )

    if issue_result.returncode != 0:
        return None

    issue_result.stdout.strip()

    # Query project items
    success, data = execute_query("get-project-items", {"projectId": project_id})

    if not success or not data:
        return None

    try:
        for item in data["data"]["node"]["items"]["nodes"]:
            if not item or not item.get("content"):
                continue
            if item["content"].get("number") == issue_number:
                # Extract status from field values
                status = None
                for fv in item.get("fieldValues", {}).get("nodes", []):
                    if fv and fv.get("field", {}).get("name", "").lower() == "status":
                        status = fv.get("name")
                        break

                return ProjectItem(
                    item_id=item["id"],
                    issue_number=issue_number,
                    title=item["content"]["title"],
                    status=status,
                    assignees=[a["login"] for a in item["content"]["assignees"]["nodes"]],
                    created_at=item["content"]["createdAt"],
                    updated_at=item["content"]["updatedAt"],
                )
    except (KeyError, TypeError):
        pass

    return None


def update_project_item_status(
    project_id: str, item_id: str, status_field_id: str, status_option_id: str
) -> bool:
    """Update the status of a project item.

    Args:
        project_id: Project node ID
        item_id: Project item ID
        status_field_id: Status field ID
        status_option_id: Status option ID to set

    Returns:
        True if successful
    """
    success, _ = execute_query(
        "update-project-item-status",
        {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": status_field_id,
            "optionId": status_option_id,
        },
    )

    return success


def find_backlog_issues(
    project_id: str,
    owner: str,
    repo: str,
    status_name: str = "Backlog",
    assignee: str | None = None,
    labels: list[str] | None = None,
) -> list[ProjectItem]:
    """Find issues in a specific project status.

    Args:
        project_id: Project node ID
        owner: Repository owner
        repo: Repository name
        status_name: Status to filter by (default: "Backlog")
        assignee: Filter by assignee (optional)
        labels: Filter by labels (optional)

    Returns:
        List of ProjectItem, sorted by created_at (oldest first)
    """
    success, data = execute_query("get-project-items", {"projectId": project_id})

    if not success or not data:
        return []

    items = []

    try:
        for item in data["data"]["node"]["items"]["nodes"]:
            if not item or not item.get("content"):
                continue

            content = item["content"]

            # Check repository matches
            if content.get("repository", {}).get("name") != repo:
                continue
            if content.get("repository", {}).get("owner", {}).get("login") != owner:
                continue

            # Extract status
            status = None
            for fv in item.get("fieldValues", {}).get("nodes", []):
                if fv and fv.get("field", {}).get("name", "").lower() == "status":
                    status = fv.get("name")
                    break

            # Filter by status
            if status != status_name:
                continue

            # Extract assignees
            assignees = [a["login"] for a in content.get("assignees", {}).get("nodes", [])]

            # Filter by assignee if specified
            if assignee and assignee not in assignees:
                continue

            # Extract labels
            issue_labels = [lbl["name"] for lbl in content.get("labels", {}).get("nodes", [])]

            # Filter by labels if specified
            if labels:
                if not all(lbl in issue_labels for lbl in labels):
                    continue

            items.append(
                ProjectItem(
                    item_id=item["id"],
                    issue_number=content["number"],
                    title=content["title"],
                    status=status,
                    assignees=assignees,
                    created_at=content["createdAt"],
                    updated_at=content["updatedAt"],
                )
            )
    except (KeyError, TypeError) as e:
        print(f"Error parsing project items: {e}")

    # Sort by created_at (oldest first)
    items.sort(key=lambda x: x.created_at)

    return items


def get_status_option_id(status_field: ProjectField, status_name: str) -> str | None:
    """Get the option ID for a status name.

    Args:
        status_field: The Status ProjectField
        status_name: Name of the status option

    Returns:
        Option ID or None
    """
    if not status_field.options:
        return None

    for opt in status_field.options:
        if opt["name"].lower() == status_name.lower():
            return opt["id"]

    return None


def set_issue_status(
    owner: str, repo: str, project_number: int, issue_number: int, new_status: str
) -> bool:
    """Convenience function to set an issue's project status.

    Args:
        owner: Repository owner
        repo: Repository name
        project_number: Project number
        issue_number: Issue number
        new_status: New status name (e.g., "In Progress", "Done")

    Returns:
        True if successful
    """
    # Get project ID
    project_id = get_project_id(owner, project_number)
    if not project_id:
        return False

    # Get status field
    status_field = get_status_field(project_id)
    if not status_field:
        return False

    # Get status option ID
    option_id = get_status_option_id(status_field, new_status)
    if not option_id:
        return False

    # Get project item for issue
    item = get_issue_project_item(project_id, issue_number, owner, repo)
    if not item:
        return False

    # Update status
    return update_project_item_status(project_id, item.item_id, status_field.id, option_id)
