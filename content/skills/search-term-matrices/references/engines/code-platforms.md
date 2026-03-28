# Code Platforms

Operators and tips for code hosting and developer Q&A platforms.

## Table of Contents

- [GitHub](#github)
- [GitLab](#gitlab)
- [StackOverflow](#stackoverflow)

---

## GitHub

The largest code hosting platform. Supports searching repositories, code, issues, pull requests, discussions, and users.

### Repository Search Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text) | `CRDT collaborative editor` |
| Language | `language:lang` | `language:typescript CRDT` |
| Stars | `stars:n` or `stars:>n` or `stars:n..m` | `stars:>100 CRDT` |
| Forks | `forks:n` or `forks:>n` | `forks:>10 CRDT` |
| Topic | `topic:name` | `topic:crdt` |
| License | `license:spdx` | `license:mit CRDT` |
| Archived | `archived:bool` | `archived:false CRDT` |
| Is fork | `fork:bool` | `fork:false CRDT` |
| Pushed date | `pushed:>YYYY-MM-DD` | `pushed:>2024-01-01 CRDT` |
| Created date | `created:>YYYY-MM-DD` | `created:>2023-01-01 CRDT` |
| Size (KB) | `size:n` or `size:>n` | `size:>100 CRDT` |
| User / org | `user:name` or `org:name` | `org:automerge CRDT` |
| In name | `in:name` | `CRDT in:name` |
| In description | `in:description` | `CRDT in:description` |
| In README | `in:readme` | `CRDT in:readme` |
| In topics | `in:topics` | `crdt in:topics` |

### Code Search Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text) | `CrdtDocument merge` |
| Language | `language:lang` | `language:rust CrdtDocument` |
| Path | `path:glob` | `path:src/**/*.ts CRDT` |
| Extension | `path:*.ext` | `path:*.rs CRDT merge` |
| Repo | `repo:owner/name` | `repo:yjs/yjs OpType` |
| Org | `org:name` | `org:automerge patch` |
| Symbol | `symbol:name` | `symbol:CrdtDocument` |
| Exact match | `/regex/` | `/fn\s+merge/` |

### Issue / PR Search Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| State | `is:open` or `is:closed` | `is:open CRDT performance` |
| Type | `is:issue` or `is:pr` | `is:issue label:bug CRDT` |
| Label | `label:name` | `label:enhancement CRDT` |
| Author | `author:name` | `author:dmonad` |
| Assignee | `assignee:name` | `assignee:dmonad` |
| Comments | `comments:>n` | `comments:>5 CRDT` |
| Created | `created:>YYYY-MM-DD` | `created:>2024-01-01 CRDT` |
| Updated | `updated:>YYYY-MM-DD` | `updated:>2024-01-01 CRDT` |
| Involves | `involves:name` | `involves:kleppmann CRDT` |
| Repo | `repo:owner/name` | `repo:automerge/automerge is:issue` |

### Tips

- GitHub's code search (cs.github.com) is more powerful than the default search bar; use it for regex and symbol searches
- Combine `stars:>N` with `pushed:>DATE` to find popular AND actively maintained repos
- The `topic:` operator searches GitHub Topics, which are curated tags set by repo owners
- Use `in:readme` to search README content; useful for finding libraries that mention specific capabilities
- For code search, `symbol:` finds function/class/type definitions specifically (not just string matches)
- GitHub Discussions search uses the same operators as issue search with `type:discussions`

---

## GitLab

Code hosting platform with built-in CI/CD. Both gitlab.com (SaaS) and self-hosted instances.

### Search Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text) | `CRDT collaborative editing` |
| Filename | `filename:name` | `filename:Cargo.toml CRDT` |
| Path | `path:dir` | `path:src CRDT` |
| Extension | `extension:ext` | `extension:rs CRDT` |
| Blob | `blob:hash` | `blob:abc123` |

### Scope Filters (UI)

| Scope | Description |
|-------|-------------|
| Projects | Search project names and descriptions |
| Issues | Search issue titles and descriptions |
| Merge Requests | Search MR titles and descriptions |
| Milestones | Search milestone titles |
| Code | Search file contents (requires Elasticsearch on self-hosted) |
| Commits | Search commit messages |
| Wiki | Search wiki page contents |
| Snippets | Search snippet titles and contents |

### Tips

- GitLab's search operators are simpler than GitHub's; most filtering happens through the UI scope selector
- Code search on gitlab.com requires the "Advanced Search" feature (powered by Elasticsearch)
- Self-hosted GitLab instances may or may not have advanced search enabled; check with your admin
- GitLab groups allow searching across all projects in a group at once
- For public open-source projects, many are mirrored on both GitHub and GitLab; GitHub usually has more stars/activity

---

## StackOverflow

The largest developer Q&A platform. Covers programming, software development, databases, DevOps, and more.

### Search Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text) | `CRDT collaborative editing` |
| Exact phrase | `"phrase"` | `"conflict-free replicated data type"` |
| Tag | `[tag]` | `[crdt]` |
| Multiple tags | `[tag1] [tag2]` | `[javascript] [crdt]` |
| Exclude tag | `-[tag]` | `[crdt] -[blockchain]` |
| User | `user:id` | `user:12345` |
| Is answered | `isanswered:yes` | `[crdt] isanswered:yes` |
| Has accepted | `hasaccepted:yes` | `[crdt] hasaccepted:yes` |
| Answers count | `answers:n` | `[crdt] answers:3` |
| Score | `score:n` | `[crdt] score:5` |
| Views | `views:n` | `[crdt] views:1000` |
| Created date | `created:YYYY-MM-DD` | `[crdt] created:2024..` |
| Body contains | `body:"phrase"` | `body:"automerge"` |
| Title contains | `title:"phrase"` | `title:"CRDT library"` |
| Is question | `is:question` | `is:question [crdt]` |
| Is answer | `is:answer` | `is:answer [crdt]` |
| Wiki | `wiki:yes` | `[crdt] wiki:yes` |
| Duplicate | `duplicate:yes` | `[crdt] duplicate:yes` |
| Closed | `closed:yes` | `[crdt] closed:yes` |
| URL | `url:pattern` | `url:github.com` |
| Inquestion | `inquestion:id` | `inquestion:12345` |

### Tips

- Tag-based search (`[tag]`) is the most effective way to find relevant Q&A on StackOverflow
- Combine `isanswered:yes` with `score:>N` to filter for high-quality, verified answers
- The `answers:` operator helps find questions with multiple perspectives
- Check the "Linked" and "Related" sidebars on any question for adjacent topics
- StackOverflow also covers Server Fault, Super User, and other Stack Exchange sites via stackexchange.com
- For niche topics, check if a dedicated Stack Exchange site exists (e.g., Data Science, Information Security)
- Use `created:YYYY..` (with trailing dots) to find questions from a specific year onward
