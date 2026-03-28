# General Search Engines

Operators and tips for general-purpose web search engines.

## Table of Contents

- [Google](#google)
- [Bing](#bing)
- [DuckDuckGo](#duckduckgo)
- [Brave Search](#brave-search)
- [SearXNG](#searxng)
- [Marginalia](#marginalia)

---

## Google

The default general-purpose engine with the broadest index and most mature operator support.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Exact phrase | `"phrase"` | `"conflict-free replicated data type"` |
| Site restriction | `site:domain` | `site:github.com CRDT` |
| Exclude site | `-site:domain` | `CRDT -site:pinterest.com` |
| File type | `filetype:ext` | `filetype:pdf CRDT survey` |
| Title contains | `intitle:word` | `intitle:CRDT comparison` |
| All in title | `allintitle:words` | `allintitle:CRDT text editor` |
| URL contains | `inurl:word` | `inurl:awesome-crdt` |
| All in URL | `allinurl:words` | `allinurl:crdt collaborative` |
| Text contains | `intext:word` | `intext:automerge` |
| Wildcard | `*` | `"best * for collaborative editing"` |
| OR | `OR` | `CRDT OR OT collaborative` |
| Exclude term | `-term` | `CRDT -blockchain` |
| Number range | `num1..num2` | `CRDT library 2022..2024` |
| Before date | `before:YYYY-MM-DD` | `CRDT before:2024-01-01` |
| After date | `after:YYYY-MM-DD` | `CRDT after:2023-01-01` |
| Related sites | `related:domain` | `related:github.com/yjs/yjs` |
| Cache | `cache:url` | `cache:example.com/article` |

### Tips

- Combine `site:` with `filetype:` for targeted document retrieval (e.g., `site:arxiv.org filetype:pdf CRDT`)
- Use `after:` and `before:` to constrain results to a time window; useful for fast-moving fields
- The `*` wildcard matches one or more words inside exact-phrase queries
- Google Advanced Search (web UI) exposes these operators through form fields for users unfamiliar with syntax
- Results degrade when stacking more than 3-4 operators; prefer fewer, more targeted operators

---

## Bing

Microsoft's search engine. Shares most operator syntax with Google but has some differences.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Exact phrase | `"phrase"` | `"collaborative editing CRDT"` |
| Site restriction | `site:domain` | `site:github.com CRDT` |
| File type | `filetype:ext` | `filetype:pdf CRDT` |
| Title contains | `intitle:word` | `intitle:CRDT` |
| URL contains | `inurl:word` | `inurl:automerge` |
| Body contains | `inbody:word` | `inbody:yjs` |
| Exclude term | `-term` | `CRDT -blockchain` |
| OR | `OR` | `CRDT OR OT` |
| Contains | `contains:ext` | `contains:pdf` |
| Near | `near:n` | `CRDT near:3 editor` |
| Language | `language:code` | `language:en CRDT` |
| Location | `loc:countrycode` | `loc:us CRDT` |
| Feed | `feed:topic` | `feed:CRDT` |
| IP address | `ip:address` | `ip:192.168.1.1` |
| Prefer | `prefer:term` | `prefer:tutorial CRDT` |

### Tips

- Bing's `near:n` operator finds words within n words of each other; Google does not have an equivalent
- `inbody:` is Bing-specific and constrains to page body text, excluding headers and menus
- Bing tends to index Microsoft-ecosystem content (docs.microsoft.com, Azure) more aggressively
- The `prefer:` operator boosts a term without requiring it

---

## DuckDuckGo

Privacy-focused search engine. Supports a subset of operators and provides instant answers via "bangs."

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Exact phrase | `"phrase"` | `"CRDT library"` |
| Site restriction | `site:domain` | `site:github.com CRDT` |
| Title contains | `intitle:word` | `intitle:CRDT` |
| File type | `filetype:ext` | `filetype:pdf CRDT` |
| Exclude term | `-term` | `CRDT -blockchain` |
| OR | `OR` | `CRDT OR OT` |
| Bang redirect | `!bang` | `!gh CRDT` (redirects to GitHub search) |
| Region | `r:region` | `r:us-en CRDT` |

### Bangs (Selected)

| Bang | Target |
|------|--------|
| `!gh` | GitHub |
| `!so` | StackOverflow |
| `!npm` | npm |
| `!mdn` | MDN Web Docs |
| `!arxiv` | arXiv |
| `!scholar` | Google Scholar |
| `!crates` | crates.io |
| `!pypi` | PyPI |
| `!w` | Wikipedia |

### Tips

- Bangs are DuckDuckGo's primary power feature; they redirect to the target site's own search
- Operator support is narrower than Google/Bing; complex multi-operator queries work better on Google
- DDG aggregates results from multiple sources (primarily Bing); useful as a second opinion

---

## Brave Search

Independent search index (not sourced from Google or Bing). Good for diverse result sets.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Exact phrase | `"phrase"` | `"CRDT implementation"` |
| Site restriction | `site:domain` | `site:github.com CRDT` |
| File type | `filetype:ext` | `filetype:pdf CRDT` |
| Exclude term | `-term` | `CRDT -blockchain` |
| OR | `OR` | `CRDT OR OT` |
| After date | `after:YYYY-MM-DD` | `after:2023-01-01 CRDT` |
| Before date | `before:YYYY-MM-DD` | `before:2024-06-01 CRDT` |

### Tips

- Brave has its own independent index, so it often surfaces results that Google and Bing miss
- Operator support is growing but still narrower than Google
- Brave Search API is available for programmatic access (free tier exists)
- Particularly good for finding independent blogs, smaller sites, and non-SEO-optimized content

---

## SearXNG

Self-hosted meta-search engine that aggregates results from multiple engines.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Exact phrase | `"phrase"` | `"CRDT library"` |
| Exclude term | `-term` | `CRDT -blockchain` |
| Site restriction | `site:domain` | `site:github.com CRDT` |
| Engine selection | `!engine` | `!google CRDT` |
| Category | `!category` | `!science CRDT` |
| Language | `:language` | `:en CRDT` |
| Time range | `!time` | Configured via UI or API parameters |

### Special Features

- **Engine selection:** Choose which backend engines to query per search using `!engine` prefix
- **Categories:** `!general`, `!images`, `!news`, `!science`, `!files`, `!social_media`
- **Configurable instances:** Each SearXNG deployment can enable different engines
- **No tracking:** No user profiling or result personalization

### Tips

- SearXNG is most useful when you want to aggregate across many engines in one query
- The engine selection bang lets you target specific backends (e.g., `!google`, `!bing`, `!ddg`)
- Results quality depends heavily on the instance configuration; self-hosted instances are recommended for research workflows
- Operators passed to SearXNG are forwarded to the selected backend engines where supported

---

## Marginalia

Independent search engine focused on non-commercial, text-heavy web content.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Exact phrase | `"phrase"` | `"CRDT algorithm"` |
| Exclude term | `-term` | `CRDT -blockchain` |
| Site restriction | `site:domain` | `site:martin.kleppmann.com CRDT` |

### Special Features

- **Non-commercial bias:** Marginalia deliberately deprioritizes SEO-optimized and ad-heavy pages
- **Text-heavy content:** Favors pages with high text-to-code ratios, academic write-ups, personal blogs
- **Small-web focus:** Surfaces content from personal sites, small communities, and niche blogs that mainstream engines bury

### Tips

- Use Marginalia when mainstream engines return too many SEO-driven results
- Particularly effective for finding personal blog posts, academic home pages, and technical write-ups
- Limited operator support; keep queries simple and keyword-focused
- Not suitable for finding recent news or commercial product pages
