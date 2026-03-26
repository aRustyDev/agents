## Search Matrix: Offline-First Sync Frameworks for Edge Computing

### Context

- **Goal:** Compare CRDT, operational transform, and event sourcing approaches in production offline-first sync frameworks
- **Type:** Technical comparative research
- **Domain:** Distributed systems, edge computing, local-first software

### Tier 1: Primary

| # | Engine(s) | Query | Operators | Expected Results | Acceptance | Success |
|---|-----------|-------|-----------|------------------|------------|---------|
| 1 | GitHub | `CRDT offline sync framework` | `language:typescript stars:>100` | Repositories implementing CRDT-based sync (Automerge, Yjs, etc.) | At least 5 repos with README describing conflict resolution | - |
| 2 | npm | `crdt offline-first sync` | `keywords:crdt popularity:>50` | Published packages for offline-first data synchronization | At least 3 packages with weekly downloads >1000 | - |
| 3 | Google Scholar | `"conflict-free replicated data types" offline synchronization benchmark` | `after:2022` | Academic papers with latency and throughput benchmarks | At least 2 papers with quantitative performance data | - |
| 4 | Google | `Automerge vs Yjs vs PowerSync comparison` | `site:blog.* OR site:medium.com` | Blog posts and technical comparisons of specific frameworks | At least 1 post with side-by-side feature comparison | - |

### Tier 2: Broadened

| # | Engine(s) | Query | Operators | Expected Results | Acceptance | Success |
|---|-----------|-------|-----------|------------------|------------|---------|
| 1 | GitHub | `offline first database sync electric` | `stars:>50 pushed:>2024-01-01` | ElectricSQL, PowerSync, and similar Postgres-backed sync engines | At least 3 active repos with sync architecture docs | - |
| 2 | StackOverflow | `[crdt] OR [offline-first] sync conflict resolution production` | `votes:5` | Q&A threads on real-world conflict resolution challenges | At least 3 answers discussing production deployments | - |
| 3 | Google | `"event sourcing" vs CRDT offline mobile sync tradeoffs` | `-site:reddit.com` | Technical articles comparing architectural approaches | At least 1 article with concrete tradeoff analysis | - |
| 4 | Hacker News (Algolia) | `Automerge OR Yjs OR PowerSync OR ElectricSQL` | `points>50 created_at_i>1704067200` | Community discussions with practitioner experiences | At least 2 threads with implementation feedback | - |

### Tier 3: Alternative sources

| # | Engine(s) | Query | Operators | Expected Results | Acceptance | Success |
|---|-----------|-------|-----------|------------------|------------|---------|
| 1 | Semantic Scholar | `local-first software CRDT performance evaluation` | `year:2023-2026 fieldsOfStudy:Computer Science` | Peer-reviewed performance evaluations of CRDT implementations | At least 1 paper with storage backend comparison | - |
| 2 | YouTube | `CRDT offline sync architecture talk` | `duration:long upload_date:year` | Conference talks or deep-dive tutorials on sync architecture | At least 1 talk from a recognized conference (Strange Loop, GOTO, etc.) | - |
| 3 | GitHub Discussions | `ElectricSQL OR PowerSync migration production` | `is:answered` | Migration guides and production experience reports | At least 1 discussion with latency numbers | - |

### Runtime Recovery

- If CRDT-specific queries return too few results, broaden to "local-first software" or "offline database replication"
- If academic sources lack benchmarks, search for vendor-published whitepapers from Automerge or ElectricSQL teams
- If npm results are sparse, try searching the Deno and JSR registries for equivalent modules
- If no head-to-head comparisons exist, construct a comparison by pulling feature data from individual framework documentation sites

### Grading Summary

| Tier | Pass Threshold | Rationale |
|------|---------------|-----------|
| Tier 1 | 3/4 rows | Primary queries must yield core framework repos and benchmark data |
| Tier 2 | 2/4 rows | Broadened scope should surface practitioner experiences and architectural comparisons |
| Tier 3 | 1/3 rows | Alternative sources provide supplementary depth; partial coverage is acceptable |
| Overall | 6/11 rows | Minimum viable coverage for a comparative analysis report |
