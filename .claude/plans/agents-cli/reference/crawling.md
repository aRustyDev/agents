modules:
    - crawler
    - scraper
    - filesys
    - git
    - output
        - user v machine
        - branding
    - config management (like figment)
    - search
    - types / structs / enums

compositions: (multiple modules, atomic actions)
workflows: (multiple compositions, idempotent results)
binaries: (tools with multiple workflows)

<https://github.com/edoardottt/cariddi>
<https://github.com/hakluke/hakrawler>
<https://github.com/lorien/awesome-web-scraping>
<https://github.com/go-rod/rod>
<https://github.com/MontFerret/ferret>
<https://github.com/gocolly/colly>
<https://github.com/apify/crawlee>
<https://github.com/codelucas/newspaper>
<https://github.com/D4Vinci/Scrapling>
<https://github.com/spider-rs/web-crawling-guides>
<https://github.com/masa-finance/crawler>
<https://github.com/scrapy/scrapy>
<https://github.com/scrapinghub/frontera/blob/master/docs/source/topics/strategies.rst>

- Strategies
  - Basic
  - Depth First
  - Breadth First
  - Discovery
<https://github.com/VIDA-NYU/ache/blob/master/docs/crawling-strategies.rst>
- Scope
- Hard-focus vs. Soft-focus
- Link Classifiers
- Backlink/Bipartite Crawling
- Page Classifiers
- Link Filters
- TOR
- proxy
- HTTP fetcher implementation
- formats
  - WARC
  - Elasticsearch
  - Kafka / ZeroMQ
  - Filesystem
  - Files
  - SqlAlchemy / Redis / HBase / Valkey
  - SurrealDB
  - Neo4j
  - QDrant
- cookies
-
<https://github.com/transducens/linguacrawl>
- seed_urls
- langs_of_interest
- accepted_tlds
- accepted_content
- user_agent
- timeout / rate-limiting
- crawl_delay
- max_time_per_site
- prefix_filter
- max_folder_tree_depth
- blacklist
- scout_steps
- min_langs_in_site
- mandatory_lang
