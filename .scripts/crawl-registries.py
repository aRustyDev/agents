#!/usr/bin/env python3
"""
Crawl component registries and output to Meilisearch-compatible JSON.

Usage:
    uv run python .scripts/crawl-registries.py --tier api --resume
    uv run python .scripts/crawl-registries.py --tier scrape --resume
    uv run python .scripts/crawl-registries.py --tier awesome --resume
    uv run python .scripts/crawl-registries.py --validate-only
    uv run python .scripts/crawl-registries.py --stats
    uv run python .scripts/crawl-registries.py --dry-run --tier api
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from jsonschema import Draft202012Validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Paths
DEFAULT_OUTPUT_DIR = Path("/private/etc/dotfiles/adam/services/databases/meilisearch/indices")
SCHEMA_DIR = DEFAULT_OUTPUT_DIR / "schemas"
STATE_FILE = DEFAULT_OUTPUT_DIR / ".crawl-state.json"

# Backoff configuration
BACKOFF_CONFIG = {
    "initial_delay": 2,
    "multiplier": 2,
    "max_delay": 300,  # 5 minute ceiling
    "max_retries": 5,
}

# Rate limits per registry
RATE_LIMITS = {
    "skillsmp": {"delay": 2, "daily_limit": 500},
    "github": {"delay": 2, "daily_limit": 5000},
    "claudemarketplaces": {"delay": 0.5, "daily_limit": None},
    "buildwithclaude": {"delay": 1, "daily_limit": None},
    "mcp_so": {"delay": 3, "daily_limit": None},
}


@dataclass
class RegistryState:
    """State for a single registry."""

    status: str = "pending"  # pending, in_progress, completed
    last_page: int = 0
    total_fetched: int = 0
    estimated_total: int | None = None
    last_url: str | None = None


@dataclass
class TierState:
    """State for a crawl tier."""

    status: str = "pending"
    registries: dict[str, dict] = field(default_factory=dict)


@dataclass
class CrawlState:
    """Full crawl state with checkpoint/resume support."""

    version: str = "1.0"
    started_at: str | None = None
    last_updated: str | None = None
    tiers: dict[str, dict] = field(default_factory=dict)
    failures: list[dict] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path = STATE_FILE) -> CrawlState:
        """Load state from file or create new."""
        if path.exists():
            data = json.loads(path.read_text())
            state = cls()
            state.version = data.get("version", "1.0")
            state.started_at = data.get("started_at")
            state.last_updated = data.get("last_updated")
            state.tiers = data.get("tiers", {})
            state.failures = data.get("failures", [])
            state.stats = data.get("stats", {})
            return state
        return cls(started_at=datetime.now(UTC).isoformat())

    def save(self, path: Path = STATE_FILE) -> None:
        """Save state to file."""
        self.last_updated = datetime.now(UTC).isoformat()
        path.write_text(json.dumps(self.__dict__, indent=2))

    def get_registry_state(self, tier: str, registry: str) -> dict:
        """Get or create registry state."""
        if tier not in self.tiers:
            self.tiers[tier] = {"status": "pending", "registries": {}}
        if registry not in self.tiers[tier]["registries"]:
            self.tiers[tier]["registries"][registry] = {
                "status": "pending",
                "last_page": 0,
                "total_fetched": 0,
            }
        return self.tiers[tier]["registries"][registry]

    def log_failure(self, url: str, error: str) -> None:
        """Log a crawl failure."""
        self.failures.append(
            {
                "url": url,
                "error": error,
                "timestamp": datetime.now(UTC).isoformat(),
                "will_retry": True,
            }
        )
        self.save()


class DailyRateLimiter:
    """Track daily request counts for rate-limited APIs."""

    def __init__(self, registry: str, daily_limit: int | None):
        self.registry = registry
        self.daily_limit = daily_limit
        self.requests_today = 0
        self.reset_date = date.today()

    def can_request(self) -> bool:
        """Check if we can make another request today."""
        if self.daily_limit is None:
            return True
        if date.today() > self.reset_date:
            self.requests_today = 0
            self.reset_date = date.today()
        return self.requests_today < self.daily_limit

    def record_request(self) -> None:
        """Record a request was made."""
        self.requests_today += 1
        if self.daily_limit and self.requests_today >= self.daily_limit:
            logger.warning(f"{self.registry}: Daily limit reached ({self.daily_limit})")
            logger.info("Resume tomorrow with: --tier <tier> --resume")


def fetch_with_backoff(
    url: str,
    session: httpx.Client,
    state: CrawlState,
) -> httpx.Response | None:
    """Fetch with exponential backoff until ceiling, then log and continue."""
    delay = BACKOFF_CONFIG["initial_delay"]

    for attempt in range(BACKOFF_CONFIG["max_retries"]):
        try:
            response = session.get(url, timeout=30)

            if response.status_code == 429:  # Rate limited
                retry_after = int(response.headers.get("Retry-After", delay))
                logger.warning(f"Rate limited, waiting {retry_after}s (attempt {attempt + 1})")
                time.sleep(retry_after)
                continue

            if response.status_code >= 500:  # Server error
                logger.warning(f"Server error {response.status_code}, backoff {delay}s")
                time.sleep(delay)
                delay = min(delay * BACKOFF_CONFIG["multiplier"], BACKOFF_CONFIG["max_delay"])
                continue

            if response.status_code >= 400:
                logger.error(f"Client error {response.status_code}: {url}")
                state.log_failure(url, f"http_{response.status_code}")
                return None

            return response

        except httpx.TimeoutException:
            logger.warning(f"Timeout, backoff {delay}s (attempt {attempt + 1})")
            time.sleep(delay)
            delay = min(delay * BACKOFF_CONFIG["multiplier"], BACKOFF_CONFIG["max_delay"])

        except httpx.ConnectError as e:
            logger.warning(f"Connection error: {e}, backoff {delay}s")
            time.sleep(delay)
            delay = min(delay * BACKOFF_CONFIG["multiplier"], BACKOFF_CONFIG["max_delay"])

    # Max retries exhausted - log failure and continue
    logger.error(f"FAILED after {BACKOFF_CONFIG['max_retries']} attempts: {url}")
    state.log_failure(url, "max_retries_exhausted")
    return None


def transform_to_component(
    raw: dict,
    component_type: str,
    source_name: str,
) -> dict:
    """Transform raw data to component schema."""
    # Generate deterministic ID
    author = raw.get("author") or raw.get("owner") or "unknown"
    name = raw.get("name", "unknown")
    component_id = f"{source_name}_{author}_{name}".lower().replace("/", "_").replace(" ", "-")

    return {
        "id": component_id,
        "name": name,
        "type": component_type,
        "description": raw.get("description"),
        "author": author,
        "canonical_url": raw.get("url") or raw.get("skillUrl") or raw.get("html_url"),
        "github_url": raw.get("githubUrl") or raw.get("html_url"),
        "star_count": raw.get("stars") or raw.get("stargazers_count") or 0,
        "source_type": "registry" if source_name != "github" else "github",
        "source_name": source_name,
        "source_url": f"https://{source_name}.com"
        if source_name != "github"
        else "https://github.com",
        "tags": raw.get("keywords") or raw.get("topics") or [],
        "discovered_at": datetime.now(UTC).isoformat(),
    }


def crawl_skillsmp(
    state: CrawlState,
    output_file: Path,
    dry_run: bool = False,
) -> int:
    """Crawl skillsmp.com API."""
    logger.info("Crawling skillsmp.com...")

    # Get API key from 1Password
    try:
        result = subprocess.run(
            ["op", "read", "op://Developer/skillsmp/credential"],
            capture_output=True,
            text=True,
            check=True,
        )
        api_key = result.stdout.strip()
    except subprocess.CalledProcessError:
        logger.error("Failed to get skillsmp API key from 1Password")
        return 0

    reg_state = state.get_registry_state("api", "skillsmp")
    rate_limiter = DailyRateLimiter("skillsmp", RATE_LIMITS["skillsmp"]["daily_limit"])

    # Resume from last page
    start_page = reg_state.get("last_page", 0) + 1
    total_fetched = reg_state.get("total_fetched", 0)

    with httpx.Client() as session:
        session.headers["Authorization"] = f"Bearer {api_key}"

        page = start_page
        while rate_limiter.can_request():
            url = f"https://skillsmp.com/api/v1/skills/search?q=*&limit=100&page={page}"

            if dry_run:
                logger.info(f"[DRY RUN] Would fetch: {url}")
                page += 1
                if page > start_page + 2:
                    break
                continue

            response = fetch_with_backoff(url, session, state)
            if not response:
                break

            rate_limiter.record_request()
            time.sleep(RATE_LIMITS["skillsmp"]["delay"])

            data = response.json()
            skills = data.get("data", {}).get("skills", [])

            if not skills:
                logger.info(f"No more skills at page {page}")
                reg_state["status"] = "completed"
                break

            # Write to NDJSON
            with output_file.open("a") as f:
                for skill in skills:
                    component = transform_to_component(skill, "skill", "skillsmp")
                    f.write(json.dumps(component) + "\n")

            total_fetched += len(skills)
            reg_state["last_page"] = page
            reg_state["total_fetched"] = total_fetched
            reg_state["status"] = "in_progress"
            state.save()

            logger.info(f"Page {page}: fetched {len(skills)} skills (total: {total_fetched})")
            page += 1

    return total_fetched


def crawl_github_topics(
    state: CrawlState,
    output_file: Path,
    dry_run: bool = False,
) -> int:
    """Crawl GitHub topic searches."""
    logger.info("Crawling GitHub topics...")

    topics = [
        ("claude-skills", "skill"),
        ("claude-code-agents", "agent"),
        ("claude-code-hooks", "hook"),
        ("mcp-server", "mcp_server"),
        ("claude-code-plugin", "plugin"),
    ]

    reg_state = state.get_registry_state("api", "github")
    completed_topics = set(reg_state.get("topics_completed", []))
    total_fetched = reg_state.get("total_fetched", 0)

    for topic, component_type in topics:
        if topic in completed_topics:
            logger.info(f"Skipping {topic} (already completed)")
            continue

        if dry_run:
            logger.info(f"[DRY RUN] Would search: topic:{topic}")
            continue

        # Use gh CLI for search
        cmd = [
            "gh",
            "search",
            "repos",
            f"topic:{topic}",
            "--sort",
            "stars",
            "--limit",
            "100",
            "--json",
            "name,url,description,stargazersCount,owner",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            repos = json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"gh search failed: {e}")
            state.log_failure(f"topic:{topic}", "gh_cli_error")
            continue

        # Write to NDJSON
        with output_file.open("a") as f:
            for repo in repos:
                component = transform_to_component(
                    {
                        "name": repo["name"],
                        "description": repo.get("description"),
                        "owner": repo.get("owner", {}).get("login"),
                        "html_url": repo["url"],
                        "stargazers_count": repo.get("stargazersCount", 0),
                    },
                    component_type,
                    "github",
                )
                f.write(json.dumps(component) + "\n")

        total_fetched += len(repos)
        completed_topics.add(topic)
        reg_state["topics_completed"] = list(completed_topics)
        reg_state["total_fetched"] = total_fetched
        state.save()

        logger.info(f"Topic {topic}: fetched {len(repos)} repos")
        time.sleep(RATE_LIMITS["github"]["delay"])

    if len(completed_topics) == len(topics):
        reg_state["status"] = "completed"
        state.save()

    return total_fetched


def crawl_claudemarketplaces(
    state: CrawlState,
    output_file: Path,
    dry_run: bool = False,
) -> int:
    """Crawl claudemarketplaces.com JSON API."""
    logger.info("Crawling claudemarketplaces.com...")

    reg_state = state.get_registry_state("api", "claudemarketplaces")
    if reg_state.get("status") == "completed":
        logger.info("claudemarketplaces already completed")
        return reg_state.get("total_fetched", 0)

    url = "https://claudemarketplaces.com/api/marketplaces"

    if dry_run:
        logger.info(f"[DRY RUN] Would fetch: {url}")
        return 0

    with httpx.Client() as session:
        response = fetch_with_backoff(url, session, state)
        if not response:
            return 0

        data = response.json()
        marketplaces = data if isinstance(data, list) else data.get("marketplaces", [])

        with output_file.open("a") as f:
            for item in marketplaces:
                component = transform_to_component(item, "plugin", "claudemarketplaces")
                f.write(json.dumps(component) + "\n")

        reg_state["status"] = "completed"
        reg_state["total_fetched"] = len(marketplaces)
        state.save()

        logger.info(f"Fetched {len(marketplaces)} marketplaces")
        return len(marketplaces)


def crawl_buildwithclaude(
    state: CrawlState,
    output_file: Path,
    dry_run: bool = False,
) -> int:
    """Crawl buildwithclaude.com via page scraping.

    Uses pagination through query params. Site renders static HTML.
    """
    logger.info("Crawling buildwithclaude.com...")

    reg_state = state.get_registry_state("scrape", "buildwithclaude")
    if reg_state.get("status") == "completed":
        logger.info("buildwithclaude already completed")
        return reg_state.get("total_fetched", 0)

    base_url = "https://buildwithclaude.com/showcase"
    start_page = reg_state.get("last_page", 0) + 1
    total_fetched = reg_state.get("total_fetched", 0)

    with httpx.Client() as session:
        page = start_page
        consecutive_empty = 0

        while consecutive_empty < 2:  # Stop after 2 empty pages
            url = f"{base_url}?page={page}"

            if dry_run:
                logger.info(f"[DRY RUN] Would fetch: {url}")
                page += 1
                if page > start_page + 2:
                    break
                continue

            response = fetch_with_backoff(url, session, state)
            if not response:
                break

            time.sleep(RATE_LIMITS["buildwithclaude"]["delay"])

            # Parse HTML for project cards
            # Look for JSON-LD or structured data first
            html = response.text
            projects = _parse_buildwithclaude_html(html)

            if not projects:
                consecutive_empty += 1
                logger.info(f"No projects at page {page}, empty count: {consecutive_empty}")
                page += 1
                continue

            consecutive_empty = 0

            # Write to NDJSON
            with output_file.open("a") as f:
                for proj in projects:
                    component = transform_to_component(proj, "plugin", "buildwithclaude")
                    f.write(json.dumps(component) + "\n")

            total_fetched += len(projects)
            reg_state["last_page"] = page
            reg_state["total_fetched"] = total_fetched
            reg_state["status"] = "in_progress"
            state.save()

            logger.info(f"Page {page}: fetched {len(projects)} projects (total: {total_fetched})")
            page += 1

    if consecutive_empty >= 2:
        reg_state["status"] = "completed"
        state.save()

    return total_fetched


def _parse_buildwithclaude_html(html: str) -> list[dict]:
    """Parse project data from buildwithclaude HTML.

    Looks for common patterns in showcase sites.
    """
    import re

    projects = []

    # Try to find JSON data embedded in script tags
    json_pattern = r'<script[^>]*type="application/json"[^>]*>([^<]+)</script>'
    for match in re.finditer(json_pattern, html, re.IGNORECASE):
        try:
            data = json.loads(match.group(1))
            if isinstance(data, dict) and "projects" in data:
                for proj in data["projects"]:
                    projects.append(
                        {
                            "name": proj.get("name") or proj.get("title"),
                            "description": proj.get("description"),
                            "url": proj.get("url") or proj.get("link"),
                            "author": proj.get("author") or proj.get("creator"),
                        }
                    )
        except json.JSONDecodeError:
            continue

    # Fallback: parse HTML structure for card patterns
    if not projects:
        # Look for card-like structures
        card_pattern = r'<div[^>]*class="[^"]*card[^"]*"[^>]*>([\s\S]*?)</div>'
        title_pattern = r"<h[23][^>]*>([^<]+)</h[23]>"
        desc_pattern = r"<p[^>]*>([^<]{10,200})</p>"
        link_pattern = r'<a[^>]*href="([^"]+)"[^>]*>'

        for card_match in re.finditer(card_pattern, html, re.IGNORECASE):
            card_html = card_match.group(1)
            title_match = re.search(title_pattern, card_html)
            desc_match = re.search(desc_pattern, card_html)
            link_match = re.search(link_pattern, card_html)

            if title_match:
                projects.append(
                    {
                        "name": title_match.group(1).strip(),
                        "description": desc_match.group(1).strip() if desc_match else None,
                        "url": link_match.group(1) if link_match else None,
                        "author": None,
                    }
                )

    return projects


def crawl_mcp_so(
    state: CrawlState,
    output_file: Path,
    dry_run: bool = False,
) -> int:
    """Crawl mcp.so MCP server directory.

    This site may use client-side rendering, so we try the API first,
    then fall back to HTML parsing.
    """
    logger.info("Crawling mcp.so...")

    reg_state = state.get_registry_state("scrape", "mcp_so")
    if reg_state.get("status") == "completed":
        logger.info("mcp.so already completed")
        return reg_state.get("total_fetched", 0)

    # Try known API endpoints first
    api_endpoints = [
        "https://mcp.so/api/servers",
        "https://mcp.so/api/v1/servers",
        "https://mcp.so/servers.json",
    ]

    total_fetched = 0

    with httpx.Client() as session:
        # Try API endpoints
        for api_url in api_endpoints:
            if dry_run:
                logger.info(f"[DRY RUN] Would try API: {api_url}")
                continue

            try:
                response = session.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    servers = data if isinstance(data, list) else data.get("servers", [])

                    with output_file.open("a") as f:
                        for server in servers:
                            component = transform_to_component(server, "mcp_server", "mcp_so")
                            f.write(json.dumps(component) + "\n")

                    total_fetched = len(servers)
                    reg_state["status"] = "completed"
                    reg_state["total_fetched"] = total_fetched
                    reg_state["api_used"] = api_url
                    state.save()

                    logger.info(f"API {api_url}: fetched {total_fetched} servers")
                    return total_fetched
            except (httpx.HTTPError, json.JSONDecodeError):
                continue

        # Fallback: scrape HTML pages
        if not dry_run:
            logger.info("API endpoints failed, falling back to HTML scraping")
            total_fetched = _scrape_mcp_so_html(state, reg_state, session, output_file)

    return total_fetched


def _scrape_mcp_so_html(
    state: CrawlState,
    reg_state: dict,
    session: httpx.Client,
    output_file: Path,
) -> int:
    """Scrape mcp.so via HTML pages with pagination."""

    base_url = "https://mcp.so"
    start_page = reg_state.get("last_page", 0) + 1
    total_fetched = reg_state.get("total_fetched", 0)

    page = start_page
    consecutive_empty = 0

    while consecutive_empty < 2:
        # Try different pagination patterns
        for url_pattern in [
            f"{base_url}/servers?page={page}",
            f"{base_url}?page={page}",
            f"{base_url}/page/{page}",
        ]:
            response = fetch_with_backoff(url_pattern, session, state)
            if response and response.status_code == 200:
                break
        else:
            logger.warning(f"No valid response for page {page}")
            break

        time.sleep(RATE_LIMITS["mcp_so"]["delay"])

        html = response.text
        servers = _parse_mcp_so_html(html)

        if not servers:
            consecutive_empty += 1
            page += 1
            continue

        consecutive_empty = 0

        with output_file.open("a") as f:
            for server in servers:
                component = transform_to_component(server, "mcp_server", "mcp_so")
                f.write(json.dumps(component) + "\n")

        total_fetched += len(servers)
        reg_state["last_page"] = page
        reg_state["total_fetched"] = total_fetched
        reg_state["status"] = "in_progress"
        state.save()

        logger.info(f"Page {page}: fetched {len(servers)} servers (total: {total_fetched})")
        page += 1

    if consecutive_empty >= 2:
        reg_state["status"] = "completed"
        state.save()

    return total_fetched


def _parse_mcp_so_html(html: str) -> list[dict]:
    """Parse MCP server data from mcp.so HTML."""
    import re

    servers = []

    # Look for JSON-LD data
    json_ld_pattern = r'<script[^>]*type="application/ld\+json"[^>]*>([^<]+)</script>'
    for match in re.finditer(json_ld_pattern, html, re.IGNORECASE):
        try:
            data = json.loads(match.group(1))
            if isinstance(data, dict) and data.get("@type") == "SoftwareApplication":
                servers.append(
                    {
                        "name": data.get("name"),
                        "description": data.get("description"),
                        "url": data.get("url"),
                        "author": data.get("author", {}).get("name"),
                    }
                )
        except json.JSONDecodeError:
            continue

    # Look for Next.js __NEXT_DATA__ which is common in React sites
    next_data_pattern = r'<script[^>]*id="__NEXT_DATA__"[^>]*>([^<]+)</script>'
    match = re.search(next_data_pattern, html, re.IGNORECASE)
    if match:
        try:
            data = json.loads(match.group(1))
            props = data.get("props", {}).get("pageProps", {})
            # Look for servers/items in various locations
            for key in ["servers", "items", "data", "results"]:
                if key in props and isinstance(props[key], list):
                    for item in props[key]:
                        if isinstance(item, dict) and item.get("name"):
                            servers.append(
                                {
                                    "name": item.get("name"),
                                    "description": item.get("description"),
                                    "url": item.get("url") or item.get("homepage"),
                                    "author": item.get("author") or item.get("owner"),
                                    "stars": item.get("stars") or item.get("stargazers_count"),
                                    "githubUrl": item.get("github") or item.get("repository"),
                                }
                            )
        except json.JSONDecodeError:
            pass

    return servers


def crawl_awesome_lists(
    state: CrawlState,
    output_file: Path,
    dry_run: bool = False,
) -> int:
    """Crawl awesome list repositories for component links."""
    logger.info("Crawling awesome lists...")

    # Curated list of awesome repos with Claude/MCP content
    awesome_repos = [
        ("punkpeye/awesome-mcp-servers", "mcp_server"),
        ("anthropics/anthropic-cookbook", "skill"),
        ("wong2/awesome-mcp-servers", "mcp_server"),
        ("modelcontextprotocol/servers", "mcp_server"),
    ]

    reg_state = state.get_registry_state("awesome", "awesome_lists")
    completed_repos = set(reg_state.get("repos_completed", []))
    total_fetched = reg_state.get("total_fetched", 0)

    for repo, default_type in awesome_repos:
        if repo in completed_repos:
            logger.info(f"Skipping {repo} (already completed)")
            continue

        if dry_run:
            logger.info(f"[DRY RUN] Would parse: {repo}")
            continue

        # Fetch README.md using gh CLI
        cmd = [
            "gh",
            "api",
            f"repos/{repo}/readme",
            "--jq",
            ".content",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import base64

            readme_content = base64.b64decode(result.stdout.strip()).decode("utf-8")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to fetch {repo} README: {e}")
            state.log_failure(f"gh:repos/{repo}/readme", "gh_api_error")
            continue
        except Exception as e:
            logger.error(f"Failed to decode {repo} README: {e}")
            continue

        # Parse markdown for links
        links = _parse_awesome_readme(readme_content)

        with output_file.open("a") as f:
            for link in links:
                component_type = link.get("type", default_type)
                component = transform_to_component(link, component_type, f"awesome:{repo}")
                f.write(json.dumps(component) + "\n")

        total_fetched += len(links)
        completed_repos.add(repo)
        reg_state["repos_completed"] = list(completed_repos)
        reg_state["total_fetched"] = total_fetched
        state.save()

        logger.info(f"{repo}: parsed {len(links)} components")
        time.sleep(1)  # Respect rate limits

    if len(completed_repos) == len(awesome_repos):
        reg_state["status"] = "completed"
        state.save()

    return total_fetched


def _parse_awesome_readme(content: str) -> list[dict]:
    """Parse awesome list README for component links."""
    import re

    components = []

    # Match markdown links: [Name](url) - Description
    # Also captures: - [Name](url) description
    # Note: matches hyphen-minus, en-dash, or colon as separator
    link_pattern = r"[-*]\s*\[([^\]]+)\]\(([^)]+)\)\s*[-\u2013:]?\s*(.*)$"

    for line in content.split("\n"):
        match = re.search(link_pattern, line)
        if match:
            name = match.group(1).strip()
            url = match.group(2).strip()
            description = match.group(3).strip() if match.group(3) else None

            # Skip non-component links (badges, images, etc.)
            if url.startswith("http://shields.io") or url.endswith((".png", ".svg", ".gif")):
                continue

            # Skip anchor links
            if url.startswith("#"):
                continue

            # Determine if it's a GitHub repo
            github_match = re.match(r"https://github\.com/([^/]+/[^/]+)", url)
            owner = None
            if github_match:
                owner = github_match.group(1).split("/")[0]

            components.append(
                {
                    "name": name,
                    "description": description,
                    "url": url,
                    "githubUrl": url if "github.com" in url else None,
                    "author": owner,
                }
            )

    return components


def _validate_ndjson(data_path: Path, validator: Draft202012Validator, data_file: str) -> int:
    """Validate NDJSON file, return error count."""
    errors_found = 0
    for i, line in enumerate(data_path.open()):
        if not line.strip():
            continue
        try:
            doc = json.loads(line)
            errs = list(validator.iter_errors(doc))
            if errs:
                logger.error(f"{data_file}:{i + 1} - {errs[0].message}")
                errors_found += 1
                if errors_found > 10:
                    logger.error("Too many errors, stopping validation")
                    break
        except json.JSONDecodeError as e:
            logger.error(f"{data_file}:{i + 1} - Invalid JSON: {e}")
            errors_found += 1
    return errors_found


def _validate_json_array(data_path: Path, validator: Draft202012Validator, data_file: str) -> int:
    """Validate JSON array file, return error count."""
    errors_found = 0
    try:
        data = json.loads(data_path.read_text())
        for i, doc in enumerate(data):
            errs = list(validator.iter_errors(doc))
            if errs:
                logger.error(f"{data_file}[{i}] - {errs[0].message}")
                errors_found += 1
    except json.JSONDecodeError as e:
        logger.error(f"{data_file} - Invalid JSON: {e}")
        errors_found += 1
    return errors_found


def validate_output(output_dir: Path) -> bool:
    """Validate all output files against schemas."""
    try:
        import jsonschema
    except ImportError:
        logger.error("jsonschema not installed. Run: uv add jsonschema")
        return False

    schema_dir = output_dir / "schemas"
    validators = {
        "components.json": "components.schema.json",
        "registries.json": "registries.schema.json",
        "plugin_components.json": "plugin_components.schema.json",
    }

    all_valid = True
    for data_file, schema_file in validators.items():
        data_path = output_dir / data_file
        schema_path = schema_dir / schema_file

        if not data_path.exists():
            logger.warning(f"Missing: {data_file}")
            continue

        if not schema_path.exists():
            logger.error(f"Missing schema: {schema_file}")
            all_valid = False
            continue

        schema = json.loads(schema_path.read_text())
        schema.pop("meilisearch", None)  # Remove Meilisearch-specific keys
        validator = jsonschema.Draft202012Validator(schema)

        # NDJSON for components, JSON array for others
        if data_file == "components.json":
            errors_found = _validate_ndjson(data_path, validator, data_file)
        else:
            errors_found = _validate_json_array(data_path, validator, data_file)

        if errors_found:
            all_valid = False
            logger.error(f"{data_file}: {errors_found} validation errors")
        else:
            logger.info(f"{data_file}: valid")

    return all_valid


def print_stats(state: CrawlState) -> None:
    """Print crawl statistics."""
    print("\n=== Crawl Statistics ===\n")
    print(f"Started: {state.started_at}")
    print(f"Updated: {state.last_updated}")

    total = 0
    for tier_name, tier_data in state.tiers.items():
        print(f"\n--- {tier_name.upper()} Tier ---")
        for reg_name, reg_data in tier_data.get("registries", {}).items():
            status = reg_data.get("status", "pending")
            fetched = reg_data.get("total_fetched", 0)
            total += fetched
            print(f"  {reg_name}: {status} ({fetched} fetched)")

    print("\n--- Totals ---")
    print(f"Total fetched: {total}")
    print(f"Failures: {len(state.failures)}")

    if state.failures:
        print("\n--- Recent Failures ---")
        for f in state.failures[-5:]:
            print(f"  {f['timestamp']}: {f['url'][:60]}...")


def main():
    parser = argparse.ArgumentParser(description="Crawl component registries")
    parser.add_argument(
        "--tier",
        choices=["api", "scrape", "awesome", "all"],
        help="Tier to crawl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last checkpoint",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate existing output",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show crawl statistics",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be crawled without fetching",
    )

    args = parser.parse_args()

    # Load or create state
    state = CrawlState.load()

    if args.stats:
        print_stats(state)
        return

    if args.validate_only:
        valid = validate_output(args.output)
        sys.exit(0 if valid else 1)

    if not args.tier:
        parser.error("--tier is required unless using --validate-only or --stats")

    output_file = args.output / "components.json"

    # Ensure output directory exists
    args.output.mkdir(parents=True, exist_ok=True)

    if args.tier in ("api", "all"):
        logger.info("=== API Tier ===")
        crawl_skillsmp(state, output_file, args.dry_run)
        crawl_github_topics(state, output_file, args.dry_run)
        crawl_claudemarketplaces(state, output_file, args.dry_run)

    if args.tier in ("scrape", "all"):
        logger.info("=== Scrape Tier ===")
        crawl_buildwithclaude(state, output_file, args.dry_run)
        crawl_mcp_so(state, output_file, args.dry_run)

    if args.tier in ("awesome", "all"):
        logger.info("=== Awesome Lists Tier ===")
        crawl_awesome_lists(state, output_file, args.dry_run)

    # Save final state
    state.save()
    print_stats(state)


if __name__ == "__main__":
    main()
