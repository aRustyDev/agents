# Paid Search Services

Operators and tips for commercial search APIs, AI-powered search, and web scraping services.

These services require API keys, subscriptions, or per-query payment. This reference covers their search capabilities and operators, not setup or authentication. Check each service's documentation for pricing and API key configuration.

## Table of Contents

- [Tavily](#tavily)
- [Perplexity](#perplexity)
- [Serper](#serper)
- [Exa](#exa)
- [Jina AI](#jina-ai)
- [FireCrawl](#firecrawl)
- [search1API](#search1api)
- [ScrapeGraph](#scrapegraph)
- [Linkup](#linkup)
- [Apify](#apify)

---

## Tavily

AI-optimized search API designed for LLM agent workflows. Returns structured, relevant results with content extraction.

### Operators / Parameters

| Parameter | Syntax | Example |
|-----------|--------|---------|
| Query | `query` (string) | `"CRDT libraries for collaborative editing"` |
| Search depth | `search_depth: "basic" \| "advanced"` | `"advanced"` for thorough results |
| Topic | `topic: "general" \| "news" \| "finance"` | `"general"` |
| Include domains | `include_domains: [domains]` | `["github.com", "arxiv.org"]` |
| Exclude domains | `exclude_domains: [domains]` | `["pinterest.com", "quora.com"]` |
| Max results | `max_results: n` | `5` |
| Include answer | `include_answer: bool` | `true` for AI-generated summary |
| Include raw content | `include_raw_content: bool` | `true` for full page text |
| Days | `days: n` | `30` for last 30 days only |

### Tips

- Tavily is purpose-built for AI agent search workflows; results are pre-filtered for relevance
- The `include_answer` option returns an AI-synthesized answer alongside raw results
- Use `include_domains` and `exclude_domains` to constrain results to authoritative sources
- The "advanced" search depth takes longer but returns more thorough results
- Tavily handles content extraction automatically; no need for separate scraping

---

## Perplexity

AI-powered search engine that synthesizes answers from multiple sources with citations.

### Operators / Parameters

| Parameter | Syntax | Example |
|-----------|--------|---------|
| Query | (free text or API) | `"What CRDT libraries exist for text editing?"` |
| Focus | `web \| academic \| writing \| math \| video` | `academic` for scholarly results |
| Pro search | (UI toggle / API tier) | Deeper multi-step research |
| Follow-up | (conversation thread) | Refine results with follow-up questions |

### API Parameters (pplx-api)

| Parameter | Syntax | Example |
|-----------|--------|---------|
| Model | `model` | `sonar`, `sonar-pro` |
| Search domain filter | `search_domain_filter` | `["github.com"]` |
| Search recency filter | `search_recency_filter` | `"week"`, `"month"`, `"year"` |
| Return citations | `return_citations: bool` | `true` |

### Tips

- Perplexity excels at synthesizing information from multiple sources into a coherent answer
- The "Academic" focus mode constrains results to scholarly sources
- Pro search performs multi-step reasoning, useful for complex research questions
- Citations are inline and verifiable; always check the source links
- The API (sonar models) can be integrated into agent workflows for programmatic access

---

## Serper

Google Search API that returns structured SERP (Search Engine Results Page) data.

### Operators / Parameters

| Parameter | Syntax | Example |
|-----------|--------|---------|
| Query | `q` (string) | `"CRDT library comparison"` |
| Search type | `type: "search" \| "news" \| "images" \| "places" \| "shopping"` | `"search"` |
| Location | `gl: "us"`, `hl: "en"` | Country and language codes |
| Number of results | `num: n` | `10` |
| Page | `page: n` | `2` for second page |
| Time range | `tbs: "qdr:d" \| "qdr:w" \| "qdr:m" \| "qdr:y"` | `"qdr:m"` for past month |
| Site | Include `site:` in query | `"site:github.com CRDT"` |

### Special Features

- **Structured output:** Returns JSON with organic results, knowledge graph, "People also ask," and related searches
- **Google operators:** All standard Google operators work in the query string
- **SERP features:** Extracts featured snippets, knowledge panels, and other SERP elements

### Tips

- Serper gives you raw Google results in structured JSON; useful when you need programmatic access to Google
- All Google operators documented in [general-search.md](general-search.md) work in Serper queries
- The structured output includes metadata (position, snippet, links) useful for automated analysis
- Cheaper than Google's official Custom Search API for most use cases

---

## Exa

Neural search API. Uses embeddings to find semantically similar content rather than keyword matching.

### Operators / Parameters

| Parameter | Syntax | Example |
|-----------|--------|---------|
| Query | `query` (string) | `"CRDT implementation for real-time collaboration"` |
| Search type | `type: "neural" \| "keyword" \| "auto"` | `"neural"` |
| Use autoprompt | `use_autoprompt: bool` | `true` |
| Include domains | `include_domains: [domains]` | `["github.com"]` |
| Exclude domains | `exclude_domains: [domains]` | `["pinterest.com"]` |
| Start published date | `start_published_date: "YYYY-MM-DD"` | `"2023-01-01"` |
| End published date | `end_published_date: "YYYY-MM-DD"` | `"2024-12-31"` |
| Category | `category` | `"research paper"`, `"blog post"`, `"github repo"` |
| Num results | `num_results: n` | `10` |
| Contents | `text: bool, highlights: bool` | Retrieve page content |

### Special Features

- **Neural search:** Finds semantically similar pages, not just keyword matches
- **Category filtering:** Constrain to specific content types (research papers, blog posts, GitHub repos, etc.)
- **Content extraction:** Returns page text and highlighted relevant passages
- **Similarity search:** Given a URL, find similar pages

### Tips

- Exa's neural search is particularly good at finding conceptually related content even without exact keyword matches
- The `category` filter is powerful for ensuring result type matches your research needs
- Use `"auto"` type to let Exa decide between neural and keyword search
- The similarity search feature (find-similar) is useful for expanding a known good source into related content
- Autoprompt rephrases your query for better neural search results

---

## Jina AI

AI-powered web reading and search. Converts web pages into clean, LLM-friendly text.

### Operators / Parameters

| Parameter | Syntax | Example |
|-----------|--------|---------|
| Reader API | `r.jina.ai/URL` | `r.jina.ai/https://github.com/yjs/yjs` |
| Search API | `s.jina.ai/query` | `s.jina.ai/CRDT collaborative editing` |
| Grounding API | `g.jina.ai/statement` | `g.jina.ai/yjs is the most popular CRDT library` |

### Special Features

- **Reader:** Converts any URL into clean markdown text, stripping navigation, ads, and boilerplate
- **Search:** Returns search results as clean, extracted text (not just links)
- **Grounding:** Fact-checks a statement against web sources
- **Segmenter:** Splits text into semantically meaningful chunks

### Tips

- The Reader API is invaluable for converting web pages into LLM-consumable text
- Use the Search API when you need both search and content extraction in one step
- The Grounding API is useful for verification research types
- Jina handles JavaScript-rendered pages, which many simple scrapers miss
- Free tier has rate limits; paid tiers support higher throughput

---

## FireCrawl

Web scraping and crawling API designed for AI applications. Extracts structured data from websites.

### Operators / Parameters

| Parameter | Syntax | Example |
|-----------|--------|---------|
| Scrape | `url` (string) | `"https://github.com/yjs/yjs"` |
| Crawl | `url` + `max_pages` | Crawl a site up to n pages |
| Map | `url` | Get all URLs on a domain |
| Search | `query` (string) | `"CRDT libraries"` |
| Extract | `prompt` + `schema` | Extract structured data from a page |
| Formats | `formats: ["markdown", "html", "links"]` | Output format selection |
| Include paths | `includePaths: ["/docs/*"]` | Only crawl matching paths |
| Exclude paths | `excludePaths: ["/blog/*"]` | Skip matching paths |

### Special Features

- **Search + scrape:** Built-in search that returns full page content (not just links)
- **Structured extraction:** Define a schema and extract structured data from pages
- **Site crawling:** Crawl entire sites with path include/exclude filters
- **Site mapping:** Get a complete URL map of a domain
- **JavaScript rendering:** Handles SPAs and JS-rendered content

### Tips

- FireCrawl's search feature combines web search with content extraction; useful for one-shot research queries
- The structured extraction feature is powerful for pulling specific data points from pages
- Use `includePaths` and `excludePaths` to focus crawls on relevant sections of a site
- Markdown output format is most useful for LLM consumption
- The map feature is useful for understanding a documentation site's structure before targeted scraping

---

## search1API

Unified search API aggregating multiple search engines.

### Operators / Parameters

| Parameter | Syntax | Example |
|-----------|--------|---------|
| Query | `query` (string) | `"CRDT library comparison"` |
| Search service | `search_service` | Select backend engine |
| Max results | `max_results: n` | `10` |
| Crawl results | `crawl_results: bool` | `true` to extract page content |

### Tips

- search1API provides a single interface to multiple search backends
- Use `crawl_results` to get page content alongside search results
- Useful when you want to switch between search engines without changing your API integration

---

## ScrapeGraph

AI-powered web scraping that uses LLMs to extract structured data from pages.

### Operators / Parameters

| Parameter | Syntax | Example |
|-----------|--------|---------|
| URL | `url` (string) | `"https://github.com/yjs/yjs"` |
| Prompt | `prompt` (string) | `"Extract the library name, description, and star count"` |
| Schema | (JSON schema) | Define output structure |

### Tips

- ScrapeGraph uses LLMs to understand page structure, so it handles varied layouts without custom selectors
- Define a clear schema for consistent, structured output
- Best for extracting specific data points from pages, not for full-text retrieval
- More expensive per-query than rule-based scrapers but more flexible

---

## Linkup

Search API with web content retrieval.

### Operators / Parameters

| Parameter | Syntax | Example |
|-----------|--------|---------|
| Query | `query` (string) | `"CRDT collaborative editing"` |
| Depth | `depth: "standard" \| "deep"` | `"deep"` for thorough results |
| Output type | `output_type: "searchResults" \| "sourcedAnswer"` | `"sourcedAnswer"` for synthesized answers |

### Tips

- Linkup provides both raw search results and AI-sourced answers with citations
- The "deep" depth performs more thorough searches at the cost of latency
- Use `sourcedAnswer` output type when you want a synthesized answer rather than a list of links

---

## Apify

Web scraping and automation platform with a marketplace of pre-built scrapers ("Actors").

### Operators / Parameters

| Parameter | Syntax | Example |
|-----------|--------|---------|
| Actor | (actor name or ID) | `apify/google-search-scraper` |
| Input | (actor-specific JSON) | `{"queries": "CRDT library", "maxResults": 10}` |
| Dataset | (output) | Results stored in Apify datasets |

### Pre-built Actors (Selected)

| Actor | Purpose |
|-------|---------|
| `apify/google-search-scraper` | Scrape Google search results |
| `apify/web-scraper` | General-purpose web scraper |
| `apify/cheerio-scraper` | Fast HTML-only scraper |
| `apify/puppeteer-scraper` | JS-rendering scraper |
| `apify/instagram-scraper` | Instagram data extraction |
| `apify/twitter-scraper` | Twitter/X data extraction |

### Tips

- Apify's strength is its marketplace of pre-built scrapers for specific sites and use cases
- Use pre-built actors when available; they handle site-specific quirks (pagination, anti-bot, etc.)
- Custom actors can be built in JavaScript/TypeScript for bespoke scraping needs
- Apify manages proxy rotation, browser fingerprinting, and other anti-detection measures
- Free tier has limited compute units; paid tiers scale for production workloads
