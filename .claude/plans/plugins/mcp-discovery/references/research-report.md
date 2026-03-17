# The definitive guide to MCP ecosystem monitoring

**The MCP server registry landscape has exploded to 25+ active directories, but only three offer production-grade APIs for programmatic consumption: the Official MCP Registry, Smithery, and PulseMCP.** The Skills/Plugin registry space is far less mature, with SkillRegistry.io and OneSkill.dev emerging as the only functional open directories. This report delivers a complete operational blueprint for building a scheduled monitoring workflow across registries, GitHub repos, fork detection, scraping, and community channels — all tailored for a DevOps engineer working with Rust, Go, and CI/CD.

The five sections below constitute independent deliverables: a graded assessment of every known registry, GitHub change-tracking methods, fork/copy detection techniques, crawling strategies for non-API sources, and a community monitoring architecture. Each section is designed to be directly implementable.

---

## Deliverable 1: Registry and marketplace grading

### MCP server registries with production-grade APIs

**The Official MCP Registry (registry.modelcontextprotocol.io)** earns the highest structured-data grade of any registry. Backed by Anthropic, GitHub, PulseMCP, and Microsoft, it launched September 2025 with an API freeze at v0.1 in October 2025. Its REST API requires **no authentication for reads** — `GET /v0/servers?limit=100&search=term&cursor=X` returns JSON with full server metadata including repository URLs, package references (npm/PyPI/Docker), transport types, and timestamps. The OpenAPI 3.1.0 spec is publicly downloadable, and the entire codebase is open-source in Go. Current listing count is in the hundreds but growing daily as the canonical upstream source. Every other registry ultimately derives from or publishes to this one. The metadata is deliberately narrow by design — name, description, version, repository, packages, remotes — with no tool schemas or usage stats, as those are left to sub-registries.

**Smithery.ai** is the most feature-rich commercial registry, with **~7,300+ servers**, a documented Registry API at `registry.smithery.ai`, and rich per-listing metadata including tool schemas, weekly call counts, security scans, and deployment options. API access requires a free Bearer token from `smithery.ai/account/api-keys`. Endpoints include `GET /servers` with semantic search, owner/repo filtering, and pagination, plus `GET /servers/{id}` for full details. Smithery also offers hosted server execution, a CLI (`@smithery/cli`), and a "Toolbox" meta-MCP that auto-discovers relevant servers. Every listing links directly to its GitHub repo via the `qualifiedName` field.

**PulseMCP (pulsemcp.com)** implements the official MCP Registry OpenAPI spec as a conforming sub-registry with proprietary enrichments. Its API at `api.pulsemcp.com/v0.1/servers` returns JSON with cursor-based pagination, including a `_meta` field containing **popularity estimates** (visitor/download counts over 4 weeks), global usage ranks, security analysis, and "isOfficial" flags. Access requires an API key (X-API-Key) plus Tenant ID — contact hello@pulsemcp.com for B2B access. With **~8,610 servers** and a weekly newsletter, PulseMCP's founder sits on the MCP Steering Committee.

**Glama.ai** rounds out the top tier with a partial API at `glama.ai/api/mcp/v1/servers/{owner}/{repo}` returning JSON for individual servers. Run by the same team behind the punkpeye/awesome-mcp-servers GitHub list, it claims the largest collection (**5,000–10,000+ servers**), offers usage-based sorting, security scanning, and a ChatGPT-like UI for directly interacting with MCP servers. Bulk listing endpoints are not publicly documented, giving it a B+ on structured data.

### Mid-tier registries worth monitoring

| Registry | Listings | Structured Data | API | GitHub Links | Status |
|---|---|---|---|---|---|
| **himcp.ai** | ~23,989 | C (no API) | D | ✅ Direct | Active, largest raw count |
| **MCP.so** | ~17,805 | C+ (open-source Supabase) | D | ✅ Direct | Active, open-source |
| **MCPServers.org** | ~2,000–5,000 | C (no API) | D | ✅ Direct | Active, synced with awesome-mcp-servers |
| **LobeHub** | Hundreds–1000s | B+ (JSON plugin indexes) | B | ✅ Direct | Active, 71.9k GH stars, A-F scoring |
| **Cline Marketplace** | Hundreds | C+ (GH Issues) | D | ✅ Required | Very active, one-click install, AWS partnerships |
| **Portkey.ai** | 138 curated | B+ (Admin API) | B | ✅ Direct | Active, MCP Gateway product |
| **Spekter.io** | ~779 | A (official registry frontend) | A | ✅ Direct | Active, official registry browser |

**himcp.ai** deserves special attention for its sheer scale at **23,989 listings** — the largest raw count of any registry — with full README reproduction, language filtering, and category browsing. However, it lacks any public API, requiring scraping to consume programmatically. **MCP.so** is notable for being fully open-source (Next.js + Supabase), meaning you can clone the codebase and query its database directly. **LobeHub** uniquely offers a **quality scoring system (A through F)** based on activity, stability, and community feedback — metadata no other registry provides.

### Small or niche registries

**MACH Alliance** (machalliance.org) provides a unique **enterprise/commerce-focused** directory of ~40–50 servers from MACH-certified vendors (Stripe, Contentful, PayPal, AWS). Static HTML with no API, but valuable for the enterprise niche. **apitracker.io** lists 110 servers as part of a broader API tracking platform by Apideck, cross-referencing MCP servers with parent API listings. **mcp-get.com** takes a package-manager approach but blocks all crawlers via robots.txt and has no documented API. **MCPServer.directory** returned 503 errors, suggesting infrastructure issues or aggressive bot protection. **AIxploria** is a WordPress-based general AI directory with an MCP section claiming 500+ servers across 35 languages.

The **awesome-mcp-servers GitHub list** (punkpeye/awesome-mcp-servers) remains foundational with **79.9k stars**, ~2,000+ entries, and daily updates via PRs. It's machine-readable as structured Markdown with emoji-based metadata and serves as the seed data for MCPServers.org and Glama.ai. The official **github.com/modelcontextprotocol/servers** repo is pivoting to reference implementations only, redirecting community listings to the official registry.

**Mastra's MCP Registry Registry** (mastra.ai/mcp-registry-registry) is the only **meta-registry** — a registry of registries available as both a web page and an MCP server itself, plus an npm package (`@mastra/mcp-registry-registry`) for programmatic consumption.

**Reddit r/mcp** is not a registry but offers excellent structured access: append `.json` to any URL for JSON, `.rss` for RSS feeds. The subreddit serves as a first-announcement venue for many new servers. Multiple MCP servers exist specifically for Reddit content access.

### Registries that are dead, blocked, or not what they claim

**mcpdb.org** returned a **404 error** despite claiming 10,000+ servers — either temporarily down or abandoned. **cursor.directory/mcp** blocks all crawlers via robots.txt. **github.com/mcp** does not exist as a registry — the official MCP organization is at `github.com/modelcontextprotocol`. **OpenTools.com** is primarily a commercial API platform (unified LLM API with MCP tool integration) rather than a browsable registry, with a small curated set of ~50–200 supported servers.

### All registries link to GitHub

Every evaluated MCP server registry provides direct links to origin GitHub repositories. The official registry mandates `repository.url` as a structured field. For registries that somehow omit GitHub links, **reverse-engineering strategies** include: mapping npm package names to GitHub via the npm registry API (`registry.npmjs.org/{package}`), searching PyPI project URLs, looking up Docker Hub image labels, and using the GitHub Search API to match server names to repositories.

---

### Skills and plugin registries are nascent

The Anthropic Skills/Plugin registry landscape is far less mature than MCP servers. Of the 10 URLs evaluated, only 3 are functional, relevant registries:

**SkillRegistry.io** is the strongest — "The Official SKILLS.md Hub" with **61 skills**, a CLI (`npm install -g skill-registry-cli`), direct download URLs (`skillregistry.io/skills/{name}.md`), and skills from major vendors including Anthropic, Vercel, Slack, Google, and Brave. Updated as recently as February 22, 2026. **OneSkill.dev** is an open-source directory indexing **548+ artifacts** across Skills, MCP servers, Cursor Rules, LangChain Tools, and CrewAI Tools from GitHub. All listings link directly to GitHub repos. **MCPMarket.com/tools/skills** has hundreds of skills across 23+ categories with Featured/Official tags, though it blocks crawlers.

**NoriSkillsets.dev** provides curated, verified Claude Code Skills packaged as "Skillsets" (Skills + CLAUDE.md + Subagents + Slash Commands) — small but high quality, with npm-based distribution. **Agentman.ai** offers **85 enterprise skills** across 21 business functions with deep metadata including decision logic, templates, and HIPAA/SOC2 compliance — but it's a proprietary platform, not an open registry.

The remaining URLs are either **irrelevant** (skillsfinder.ai is an Ontario education tool), **not registries** (solmaz.io/skillflag is a blog post proposing an anti-registry philosophy; tilework.tech is a corporate landing page), **pre-launch** (skills.re returned 403), or **proprietary enterprise features** (thingsolver.com/tools-registry is an internal SaaS feature).

### Newly discovered registries and platforms

| Discovery | URL | Type | Why It Matters |
|---|---|---|---|
| **JetBrains/Zed ACP Agent Registry** | agentclientprotocol.com | AI coding agent registry | New open standard (Jan 2026) backed by JetBrains and Zed, analogous to MCP but for coding agents |
| **Composio** | composio.dev | Tool integration platform | 250+ tools, 25+ framework support, full SDK/API, 27K+ GH stars |
| **Toolhouse AI** | toolhouse.ai | Tool marketplace | Curated Tool Store, universal SDK, backed by Cloudflare/NVIDIA |
| **ChatGPT App Directory** | In-app (Dec 2025) | Full app marketplace | OpenAI's evolution from GPT Store to full app platform with Apps SDK |
| **Playbooks MCP** | playbooks.com/mcp | MCP server pages | Searchable directory with install instructions |
| **Composio MCP** | mcp.composio.dev | MCP integrations | 100+ managed MCP integrations with OAuth handling |
| **wong2/awesome-mcp-servers** | GitHub | Separate curated list | Independent from punkpeye's list, with web directory |
| **LobeHub Skills** | lobehub.com/skills | Skills marketplace | API at `market.lobehub.com/api/v1/skills/{id}/download` |
| **Anthropic Official Skills** | github.com/anthropics/skills | Official Claude Code plugins | Canonical source for Anthropic's own skills |

### Package manager discovery strategies

For npm, search using prefix `mcp-server-*` or scoped packages `@modelcontextprotocol/server-*`. For PyPI, search `mcp-server-*` or `mcp_server_*` and use `uvx mcp-server-{name}` for direct execution. On crates.io, search `mcp` for Rust implementations. GitHub Topics provide the best discovery surface: `mcp-server`, `model-context-protocol`, `awesome-mcp-servers`, `mcp-directory`. Several MCP servers themselves function as package registry meta-searchers — **PackageLens MCP** searches 6 ecosystems simultaneously, while **package-version-check-mcp** covers 14 package managers including npm, PyPI, NuGet, Maven, Go, Docker, Helm, and Terraform.

---

## Deliverable 2: GitHub change tracking methods

### REST API commit tracking is the foundation

The `GET /repos/{owner}/{repo}/commits` endpoint accepts a `path` parameter for file-level filtering, plus `since` and `until` (ISO 8601) for time-based scoping. With authenticated access at **5,000 requests/hour**, you can poll ~5,000 repos hourly at one request each. Pagination uses `Link` headers with `rel="next"`, returning up to 100 results per page.

The critical optimization is **conditional requests**. Every REST response includes an `ETag` header. On subsequent requests, pass `If-None-Match: "{etag}"` — if nothing changed, you get HTTP 304 which **does not count against your rate limit**. For steady-state monitoring where most repos haven't changed, this reduces effective API consumption by 80–95%. Store `{repo, path, ETag, last_commit_sha, last_checked_at}` in a database and only process repos returning 200.

### GraphQL enables efficient bulk queries

The GraphQL API supports path-filtered commit history via `history(path: "file.yaml", first: 1, since: "2026-02-01T00:00:00Z")` on Commit objects. Its killer feature is **aliasing** — a single request can query 20–50 repos simultaneously:

```graphql
{
  r1: repository(owner:"org", name:"repo-a") {
    defaultBranchRef { target { ... on Commit { history(path:"config.yaml", first:1) { nodes { oid committedDate } } } } }
  }
  r2: repository(owner:"org", name:"repo-b") { /* same pattern */ }
  rateLimit { cost remaining }
}
```

At ~1 point per repo queried, you can check **~4,900 repos/hour** within the 5,000 points/hour budget. GraphQL lacks ETag support, however, so unchanged repos still consume points. It also **cannot return the list of changed files** in a commit — you must fall back to REST for per-file diff data.

### Webhooks for real-time, polling for scale

GitHub webhooks fire in real-time on push events, with payloads containing `commits[].added`, `commits[].removed`, and `commits[].modified` arrays for path-level filtering in your handler. However, webhooks require **admin access** per repo (or organization owner for org-wide webhooks), do **not automatically retry** failed deliveries, and have no native path filtering — you must filter in your consumer code. Maximum 20 webhooks per event type per repo.

GitHub Actions `on.push.paths` provides native path-based triggering with glob patterns, but requires a workflow file in each monitored repo — impractical at scale. Scheduled Actions (`cron`) can poll the API from within a workflow but consume runner minutes.

**RSS/Atom feeds** (`/{owner}/{repo}/commits.atom`) are free and require no authentication, but support **no path filtering** — you get all commits on the branch.

The **Events API** is optimized for polling with `X-Poll-Interval` headers (typically 60 seconds) and ETag-based 304 responses, but caps at **300 events** with 30-day retention and provides no path filtering.

### Hybrid architecture recommended at scale

For monitoring hundreds to thousands of repos:

- **\<50 repos**: REST API with ETags, cron job every 15–60 minutes. Simple and effective.
- **50–500 repos**: GraphQL batch queries for bulk checks, REST+ETags for high-priority repos. Single GitHub App installation for 15,000 req/hr limit.
- **500–5,000 repos**: GitHub App across multiple org installations (15K/hr each). Org webhooks for owned repos, GraphQL batching for external repos. Redis/PostgreSQL for state. Multiple token rotation.
- **5,000+ repos**: All of the above plus sharded polling workers, dedicated webhook infrastructure (Hookdeck or custom), separate GraphQL and REST pools, monitoring/alerting on rate limit consumption.

A **GitHub App** gets up to **15,000 requests/hour** per installation (vs. 5,000 for PATs). For 5 organizations with separate installations, that's 75,000 REST requests/hour. Authentication flow: App private key → JWT (10-min TTL) → `POST /app/installations/{id}/access_tokens` → Bearer token.

**Third-party tools worth evaluating**: `changedetection.io` can monitor raw GitHub file URLs with zero API cost. `git-repo-watcher` is a bash script polling via `git fetch` every 10 seconds with custom hooks. The GitHub CLI (`gh api`) is excellent for scripting in cron jobs.

### Database schema for tracking state

```sql
CREATE TABLE monitored_paths (
    id SERIAL PRIMARY KEY,
    owner TEXT NOT NULL, repo TEXT NOT NULL,
    path TEXT NOT NULL, branch TEXT DEFAULT 'main',
    last_commit_sha TEXT, last_commit_date TIMESTAMPTZ,
    etag TEXT, last_checked_at TIMESTAMPTZ,
    poll_interval_seconds INT DEFAULT 3600,
    UNIQUE(owner, repo, path, branch)
);
CREATE TABLE detected_changes (
    id SERIAL PRIMARY KEY,
    monitored_path_id INT REFERENCES monitored_paths(id),
    commit_sha TEXT NOT NULL, commit_date TIMESTAMPTZ,
    commit_message TEXT, author TEXT,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    notification_sent BOOLEAN DEFAULT FALSE
);
```

---

## Deliverable 3: Fork and copy detection across three levels

### Level 1 uses the GitHub API fork graph

The `GET /repos/{owner}/{repo}` endpoint returns three critical fields when a repo is a fork: `fork` (boolean), `parent` (immediate fork source), and `source` (the root of the entire fork network). **Renamed forks are still detectable** — the `source` field persists regardless of name changes. To build a complete fork tree, recursively call `GET /repos/{owner}/{repo}/forks?per_page=100` for each node.

For detecting shared git ancestry without an explicit fork relationship (manual `git clone` without the fork button), use the **Commit Search API**: `GET /search/commits?q=hash:{SHA}` finds all public repos containing a specific commit SHA. Repos sharing identical commits prove common ancestry even without GitHub fork metadata.

**Limitations**: Manual clones create no API-visible fork relationship. Users can detach forks by contacting GitHub support. Private forks are invisible without access. The Search API also excludes forks by default — add `fork:true` or `fork:only` to GraphQL search queries.

### Level 2 uses vector embeddings for conceptual similarity

For detecting similar functionality with different implementations, embed README files, tool schemas, and code using appropriate models. **UniXcoder** (`microsoft/unixcoder-base`, 768 dimensions) is the best open-source code embedding model, achieving state-of-the-art MRR for code search. For documentation similarity, **OpenAI text-embedding-3-large** (3072 dims) or **text-embedding-3-small** (1536 dims, cost-effective) work well. **Voyage Code 2** is the best proprietary option for code similarity.

Recommended cosine similarity thresholds (calibrate per model): **\>0.95** = near-certain clone, **\>0.85** = likely derivative (flag for review), **\>0.70** = conceptual similarity, **\<0.50** = likely unrelated.

For clustering similar MCP servers, use the **UMAP + HDBSCAN pipeline**: reduce embedding dimensions with UMAP (`n_neighbors=30, min_dist=0.0, n_components=10`) then cluster with HDBSCAN (`min_cluster_size=5`). HDBSCAN automatically determines cluster count and labels noise. Research shows UMAP improves HDBSCAN accuracy by up to 60%.

**Lightweight first-pass approaches** before expensive embedding: Jaccard similarity on sets of tool names and parameter names (threshold J > 0.5 suggests significant overlap), TF-IDF vectors on tool descriptions, and **MinHash/LSH** for approximate nearest-neighbor search at scale. The Rust `gaoya` crate provides MinHash LSH; Milvus has native `MINHASH_LSH` index support. Configuration: 128 hash functions, 32 bands × 4 rows balances precision and recall for ~0.5 Jaccard threshold.

### Level 3 detects partial code and schema reuse

**AST-based analysis** uses tree-sitter for multi-language parsing (40+ languages, millisecond parsing, Rust/Go/Python bindings). Extract tool handler functions, normalize (strip comments, standardize variable names), then compare using tools like **SourcererCC** (token-based, handles 250 MLOC scale), **JPlag** (open-source Java, runs locally, obfuscation-resilient), or **NiCad** (text normalization). JPlag is especially useful: its `--base-code` flag excludes common MCP SDK boilerplate from comparison, reducing false positives.

**Schema fingerprinting** provides fast exact-match detection: normalize JSON Schemas (sort keys, lowercase strings, strip descriptions, remove defaults), then SHA-256 hash. For fuzzy matching, hash individual parameter schemas separately and compute Jaccard similarity on hash sets. Flag tools where \>70% of parameter hashes match another tool.

**Git-based detection** catches cherry-picked code: `git patch-id --stable` computes content-based hashes of diffs, ignoring line numbers and whitespace. Two commits with identical patch-IDs represent the same change regardless of commit SHA. Compare patch-ID sets across repos to find cherry-picked or rebased code.

### Building the fingerprint database

**Qdrant** is the recommended vector database for a Rust/Go stack — written in Rust with native gRPC API, supporting HNSW indexing with cosine similarity and rich metadata filtering. Store embeddings alongside payload metadata (repo URL, file path, hashes). Use PostgreSQL with pgvector as a secondary store for relational queries and backup vector search.

**Incremental updates**: Store `last_analyzed_commit_sha` per repo. On each scan, use `GET /repos/{owner}/{repo}/compare/{old_sha}...{new_sha}` to fetch only changed files, re-embed those files only, and upsert updated fingerprints via Qdrant's upsert operation. Use `hash(f"{repo_full_name}/{file_path}")` as deterministic vector IDs.

**False positive management**: Pre-compute fingerprints of MCP SDK templates (`create-mcp-server` output, `@modelcontextprotocol/sdk` starter code) and subtract matches. Ignore repos where \>80% of code matches templates. Only analyze tool handler files, not config/build files. Maintain a human review queue with confidence scores, feeding confirmed decisions back to calibrate thresholds.

**Cost estimate for 1,000 repos**: First run takes ~4–8 hours and ~$10–20 (mostly OpenAI embedding costs). Incremental updates of ~100 changed repos take 30–60 minutes at ~$1–2.

---

## Deliverable 4: Crawling strategies for non-API registries

### Always check for hidden APIs first

Before writing any scraper, open the browser DevTools Network tab, filter XHR/Fetch requests, and look for the JSON API the frontend calls. Many SPA-based registries (himcp.ai, mcpmarket.com, mcp.so) fetch data from internal API routes that return clean JSON. Replicating those HTTP calls directly is **10× more reliable and fast** than scraping rendered HTML. Playwright's `page.waitForResponse()` can also intercept and capture these API responses.

### Choosing the right scraping tool

For **server-rendered HTML sites** (MACH Alliance, AIxploria), use HTTP-based scraping: `reqwest` + `scraper` crate in Rust, `colly` + `goquery` in Go, or `httpx` + `selectolax` in Python (selectolax is **5–30× faster than BeautifulSoup**). For **JavaScript-rendered SPAs** that lack discoverable APIs, use headless browsers: Playwright (cross-browser, multi-language, auto-waiting) is preferred over Puppeteer. In Rust, `fantoccini` (async, WebDriver-based) is more mature than `headless_chrome`. In Go, `rod` offers built-in `WaitStable()` and page pool management.

Block non-essential resources (images, CSS, fonts) via `page.route()` for 2–5× speedup on resource-heavy pages. For fingerprint management, use coherent configuration (matching UA, timezone, locale, viewport) rather than random rotation.

### changedetection.io is the best self-hosted all-in-one solution

For monitoring \<100 pages with minimal custom code, **changedetection.io** (Docker: `ghcr.io/dgtlmoon/changedetection.io`) provides CSS selector/XPath/JSONPath filtering, browser automation via Playwright backend, JSON API monitoring, and **70+ notification channels** (Discord, Slack, Telegram, email, webhooks). Resource usage is minimal: \<1% CPU, ~100MB RAM for ~20 monitored sites. It has its own REST API for programmatic watch management.

For more control, **urlwatch** (Python CLI) monitors webpages and sends diff notifications via email/Telegram/Slack. Configure via YAML, schedule via cron. **RSS-Bridge** (self-hosted PHP/Docker) generates RSS feeds from any site using the CssSelectorBridge — define CSS selectors to scrape listings into a feed format without coding.

### Content-addressed hashing detects new registry entries

The gold standard for detecting new entries in listing pages: extract individual items using CSS selectors, generate SHA-256 hashes of key fields (name + URL), store hashes in SQLite/PostgreSQL, and on each check compare current hashes against stored set. New hashes = new entries → trigger alert. This is more reliable than whole-page diffing, which produces noise from ads, timestamps, and layout changes.

### Legal and ethical compliance is non-negotiable

Always check `robots.txt` before scraping — CNIL (France's GDPR regulator) treats robots.txt compliance as a factor in Legitimate Interest assessments. Review Terms of Service for explicit scraping prohibitions. Identify your bot transparently in the User-Agent string: `RegistryMonitor/1.0 (+https://yoursite.com/bot-info)`. Implement exponential backoff with jitter, respect `Retry-After` headers, and use per-domain throttling (1 request every 3–5 seconds as a conservative baseline). Avoid scraping personal data, and document your legal basis for any data collection.

---

## Deliverable 5: Community monitoring architecture

### The highest-signal sources for new MCP servers

**GitHub** is the primary source. Monitor via: the Search API for new repos with `topic:mcp-server created:>YESTERDAY` (30 requests/minute authenticated), Atom feeds for specific repos (`/commits.atom`, `/releases.atom`), and GitHub Topics pages. The **awesome-mcp-servers** repo's commits feed captures nearly every curated addition. Watch the `modelcontextprotocol` organization for official releases.

**Hacker News** provides high-quality signals via the **Algolia Search API** (no auth needed, ~10,000 requests/hour): `GET https://hn.algolia.com/api/v1/search_by_date?query=MCP&tags=story&numericFilters=created_at_i>{unix_timestamp}`. Poll every 10 minutes. HN's discerning community means MCP-related posts tend to be substantive.

**Reddit** is best consumed via RSS feeds (no auth needed): `reddit.com/r/mcp/new/.rss`, `reddit.com/r/ClaudeAI/new/.rss`. Poll every 5–10 minutes. The Reddit API's current state requires OAuth with a free tier at ~100 QPM for non-commercial use, but RSS is simpler and sufficient. Key subreddits: r/mcp (highest signal), r/ClaudeAI, r/cursor, r/LocalLLaMA.

**Discord** provides real-time signals but requires a bot. Key servers: MCP Contributors (official, ~3,700 members), Model Context Protocol community (~11,370 members), plus Anthropic, Cursor, LangChain, and CrewAI servers. Use `serenity` (Rust) or `discordgo` (Go) for bot implementation. The `MESSAGE_CONTENT` privileged intent is required for keyword monitoring.

### Practical monitoring for other channels

**Twitter/X** is expensive for programmatic monitoring: the free tier offers only ~50 reads/month, Basic costs $200/month, and Pro costs $5,000/month. The budget alternative is self-hosting **Nitter** or using **RSS-Bridge** to generate RSS feeds from key accounts — fragile but free. Key accounts: `@AnthropicAI`, `@alexalbert__` (MCP lead), `@daborpa` and `@jspahrs` (MCP co-creators).

**Dev.to** provides free RSS feeds per tag: `dev.to/feed/tag/mcp`. **Medium** offers tag-based RSS: `medium.com/feed/tag/model-context-protocol`. **YouTube** channels have free RSS feeds: `youtube.com/feeds/videos.xml?channel_id={ID}` — poll every 30–60 minutes for channels like Fireship, AI Explained, and Matt Wolfe. **Lobste.rs** offers a JSON API (`lobste.rs/newest.json`) and tag-based RSS (`lobste.rs/t/ai.rss`) — high-quality, invite-only community. **Product Hunt** has a GraphQL API v2 at `api.producthunt.com/v2/api/graphql` for monitoring Developer Tools/AI launches.

For newsletters (Pragmatic Engineer, TLDR AI, Ben's Bites), use **Kill the Newsletter** (kill-the-newsletter.com) to convert email subscriptions to RSS feeds, or parse emails via IMAP with keyword matching.

### Unified monitoring daemon design

The simplest starting point covers ~70% of new MCP server discovery with zero API keys and zero cost:

```bash
#!/bin/bash
SINCE=$(date -d '15 minutes ago' +%s)
curl -s "https://hn.algolia.com/api/v1/search_by_date?query=MCP&tags=story&numericFilters=created_at_i>$SINCE" \
  | jq -r '.hits[] | "\(.title) - \(.url)"' \
  | while read line; do curl -d "$line" ntfy.sh/my-mcp-alerts; done
curl -s "https://www.reddit.com/r/mcp/new/.rss" | # parse with xmlstarlet
```

For a production daemon, build a single Rust binary (tokio + reqwest + feed-rs + serenity + rusqlite + serde) or Go binary (goroutines + gofeed + discordgo + modernc.org/sqlite) as a systemd service. Configuration via TOML with keyword lists, source URLs, alert webhook URLs, and polling intervals.

**Deduplication** is critical across sources: normalize URLs (strip tracking parameters), use simhash on titles with threshold ~0.7 for cross-source dedup, group items within 4-hour windows, and store seen URLs in SQLite. **Alert prioritization**: P1 (immediate push notification) for official org releases and major vendor launches; P2 (Slack) for trending GitHub repos (\>50 stars); P3 (daily digest) for blog posts and moderate-engagement Reddit posts; P4 (weekly summary) for general discussion.

**Master keyword list**: Primary (high signal): "MCP server", "Model Context Protocol", "mcp-server-", "Claude tool", "claude-code skill". Secondary: "AI agent tool", "function calling", "tool use", "agentic". Tertiary (broad, needs context): "Claude", "Cursor", "Windsurf", "Cline".

| Source | Method | Frequency | Auth | Signal-to-Noise |
|---|---|---|---|---|
| GitHub Search API | REST | 30 min | PAT | Very High |
| GitHub Atom feeds | RSS | 15 min | None | Very High |
| HN Algolia | REST | 10 min | None | High |
| Reddit r/mcp | RSS | 5–10 min | None | High |
| Discord (MCP servers) | WebSocket bot | Real-time | Bot token | High |
| MCP registries (Smithery, PulseMCP) | REST API | 60 min | API keys | Very High |
| Dev.to, Medium | RSS | 30–60 min | None | Medium |
| YouTube channels | RSS | 60 min | None | Low-Medium |
| Twitter/X | Nitter RSS or API | 15 min | Varies | Medium |
| Product Hunt | GraphQL | 60 min | OAuth | Medium |
| Lobste.rs | JSON API | 30 min | None | High |

---

## Conclusion

Three registries form the monitoring backbone: the **Official MCP Registry** (best API, canonical upstream, no auth for reads), **Smithery** (richest metadata, hosted execution stats), and **PulseMCP** (popularity estimates, conforming sub-registry API). Together they cover the structured-data tier. For breadth, **himcp.ai** (23,989 listings) and **awesome-mcp-servers** (79.9k GitHub stars) capture the long tail, though both require scraping.

The Skills ecosystem is a year behind MCP servers in maturity — **SkillRegistry.io** and **OneSkill.dev** are the only functional open directories. Watch **github.com/anthropics/skills** as Anthropic's canonical skills source.

The most significant new discovery is the **JetBrains/Zed ACP Agent Registry** (January 2026) — a competing open standard for coding agents that may converge with or diverge from MCP. Also notable: **Composio** (250+ tools, full SDK) and the **ChatGPT App Directory** (December 2025) represent the broader agent tooling context.

For the monitoring workflow itself, a hybrid GitHub tracking approach (org webhooks for owned repos, GraphQL batching for external repos, REST+ETags for steady-state polling) scales to thousands of repos within rate limits. Fork detection is best implemented as a four-tier pipeline: GitHub API fork check → MinHash/LSH first pass → vector embedding comparison → AST-based deep analysis, with Qdrant as the fingerprint database. And a minimal shell script polling HN Algolia + Reddit RSS every 10–15 minutes captures ~70% of new server announcements at zero cost, serving as the foundation before investing in a full Rust/Go daemon.
