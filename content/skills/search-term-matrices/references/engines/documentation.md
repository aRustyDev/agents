# Documentation Platforms

Operators and tips for official documentation sites, documentation aggregators, and developer reference platforms.

## Table of Contents

- [MDN Web Docs](#mdn-web-docs)
- [AWS Documentation](#aws-documentation)
- [Apple Developer Documentation](#apple-developer-documentation)
- [Cloudflare Docs](#cloudflare-docs)
- [DeepWiki](#deepwiki)
- [MkDocs-based Sites](#mkdocs-based-sites)
- [Prisma Docs](#prisma-docs)
- [Refs](#refs)
- [Context7](#context7)

---

## MDN Web Docs

Mozilla's web technology documentation. The authoritative reference for HTML, CSS, JavaScript, Web APIs, and HTTP.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (site search bar) | `WebSocket API` |
| Google site-scoped | `site:developer.mozilla.org term` | `site:developer.mozilla.org CRDT SharedArrayBuffer` |
| URL path filtering | (URL structure) | `developer.mozilla.org/en-US/docs/Web/API/...` |

### URL Structure

| Path Prefix | Content |
|-------------|---------|
| `/en-US/docs/Web/API/` | Web APIs |
| `/en-US/docs/Web/JavaScript/` | JavaScript language reference |
| `/en-US/docs/Web/CSS/` | CSS reference |
| `/en-US/docs/Web/HTML/` | HTML reference |
| `/en-US/docs/Web/HTTP/` | HTTP reference |
| `/en-US/docs/Learn/` | Tutorials and guides |
| `/en-US/docs/Glossary/` | Web technology glossary |

### Tips

- MDN is the canonical reference for web platform APIs; prefer it over blog posts or tutorials
- The built-in search is good but `site:developer.mozilla.org` via Google often finds pages faster
- Every API page includes browser compatibility tables showing support across engines
- The "Specifications" section links to the relevant W3C/WHATWG spec
- MDN pages have structured data that tools and search engines can consume

---

## AWS Documentation

Amazon Web Services official documentation. Covers all AWS services, SDKs, and CLI tools.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (docs.aws.amazon.com search bar) | `DynamoDB conflict resolution` |
| Google site-scoped | `site:docs.aws.amazon.com term` | `site:docs.aws.amazon.com "eventual consistency"` |
| Service-scoped | (URL path) | `docs.aws.amazon.com/amazondynamodb/latest/developerguide/` |

### URL Structure (Selected Services)

| Path | Service |
|------|---------|
| `/amazondynamodb/` | DynamoDB |
| `/AmazonS3/` | S3 |
| `/lambda/` | Lambda |
| `/AmazonECS/` | ECS |
| `/AmazonEKS/` | EKS |
| `/AWSCloudFormation/` | CloudFormation |
| `/IAM/` | IAM |
| `/cli/` | AWS CLI |
| `/sdk-for-javascript/` | JavaScript SDK |

### Tips

- AWS docs are organized by service; start with the service's developer guide for conceptual docs and API reference for specifics
- The "User Guide" and "Developer Guide" are different documents for most services; check both
- API reference docs are auto-generated and comprehensive but can be hard to navigate
- Use `site:docs.aws.amazon.com` with Google for full-text search; the built-in search can miss pages
- AWS blog posts (aws.amazon.com/blogs/) often cover patterns and best practices not in the official docs

---

## Apple Developer Documentation

Apple's documentation for iOS, macOS, watchOS, tvOS, visionOS, Swift, and Objective-C frameworks.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (developer.apple.com/search) | `CloudKit conflict resolution` |
| Google site-scoped | `site:developer.apple.com/documentation term` | `site:developer.apple.com/documentation CKRecord` |
| Framework-scoped | (URL path) | `developer.apple.com/documentation/cloudkit` |
| Symbol lookup | (URL path) | `developer.apple.com/documentation/cloudkit/ckrecord` |

### URL Structure

| Path | Content |
|------|---------|
| `/documentation/swift/` | Swift language |
| `/documentation/foundation/` | Foundation framework |
| `/documentation/swiftui/` | SwiftUI |
| `/documentation/uikit/` | UIKit |
| `/documentation/cloudkit/` | CloudKit |
| `/documentation/coredata/` | Core Data |
| `/documentation/combine/` | Combine framework |
| `/tutorials/` | Interactive tutorials |

### Tips

- Apple's documentation is organized by framework; each framework has a top-level landing page
- Symbol pages include declaration, discussion, availability (which OS versions), and related symbols
- The "See Also" section at the bottom of each page links to related APIs
- WWDC session videos often explain APIs more thoroughly than the documentation text
- Use `site:developer.apple.com/documentation` to search only API docs (excluding forums, articles, etc.)

---

## Cloudflare Docs

Cloudflare's product documentation covering Workers, Pages, R2, D1, KV, Durable Objects, and more.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (developers.cloudflare.com search) | `Durable Objects WebSocket` |
| Google site-scoped | `site:developers.cloudflare.com term` | `site:developers.cloudflare.com "Durable Objects" CRDT` |
| Product-scoped | (URL path) | `developers.cloudflare.com/workers/` |

### URL Structure (Selected Products)

| Path | Product |
|------|---------|
| `/workers/` | Cloudflare Workers |
| `/pages/` | Cloudflare Pages |
| `/r2/` | R2 Object Storage |
| `/d1/` | D1 Database |
| `/kv/` | Workers KV |
| `/durable-objects/` | Durable Objects |
| `/vectorize/` | Vectorize |
| `/ai/` | Workers AI |

### Tips

- Cloudflare docs are well-organized with clear product boundaries
- The "Get started" guide for each product is a good entry point for understanding capabilities
- API reference docs include curl examples and TypeScript types
- The Cloudflare blog (blog.cloudflare.com) often contains deep technical content that supplements docs
- For Workers-specific patterns, check the "Examples" section under each product

---

## DeepWiki

AI-generated documentation for open-source repositories on GitHub.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Repository lookup | (URL path) | `deepwiki.com/yjs/yjs` |
| Keyword search | (within a repo's DeepWiki page) | Search within generated docs |
| Google site-scoped | `site:deepwiki.com term` | `site:deepwiki.com yjs CRDT` |

### Special Features

- **Auto-generated overviews:** AI-produced summaries of repository purpose, architecture, and key concepts
- **Code walkthroughs:** Explains how major components work
- **Dependency analysis:** Maps out key dependencies and their roles
- **Architecture diagrams:** Generated diagrams showing code structure

### Tips

- DeepWiki is useful for getting a quick overview of an unfamiliar repository
- Generated docs may contain inaccuracies; always verify against the actual source code and official README
- Best used as a starting point, not a definitive reference
- Coverage depends on repository popularity; niche repos may not have DeepWiki pages

---

## MkDocs-based Sites

Many open-source projects use MkDocs (or MkDocs Material) for documentation hosting. These sites share common search behavior.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Built-in search | (site search bar) | Uses lunr.js or another client-side search |
| Google site-scoped | `site:docs.project.com term` | `site:docs.pydantic.dev validation` |

### Identifying MkDocs Sites

- URL pattern: often `*.readthedocs.io` or custom domains
- Footer credits: "Built with MkDocs" or "Material for MkDocs"
- Search behavior: client-side search with instant results (lunr.js)

### Tips

- MkDocs search is client-side and limited; use `site:` with Google for more thorough searches
- Many Python and DevOps projects use MkDocs; recognize the style to know when to use `site:` Google searches
- ReadTheDocs-hosted projects (`*.readthedocs.io`) support version switching; make sure you are reading docs for the correct version
- The `mkdocs.yml` file in a project's repo shows the full documentation structure

---

## Prisma Docs

Documentation for the Prisma ORM (Node.js / TypeScript database toolkit).

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (prisma.io/docs search bar) | `relation conflict` |
| Google site-scoped | `site:prisma.io/docs term` | `site:prisma.io/docs "optimistic concurrency"` |
| Section-scoped | (URL path) | `prisma.io/docs/orm/prisma-client/...` |

### URL Structure

| Path | Content |
|------|---------|
| `/docs/orm/` | Prisma ORM docs |
| `/docs/orm/prisma-schema/` | Schema language reference |
| `/docs/orm/prisma-client/` | Client API reference |
| `/docs/orm/prisma-migrate/` | Migration tool docs |
| `/docs/accelerate/` | Prisma Accelerate (connection pooling) |
| `/docs/pulse/` | Prisma Pulse (real-time events) |

### Tips

- Prisma docs are comprehensive and well-structured; the search works well for common queries
- The "Reference" section has detailed API docs; the "Guides" section has how-to content
- Check the "Known limitations" sections for each feature before assuming it supports your use case
- Prisma's changelog and "What's new" page tracks breaking changes between versions

---

## Refs

A documentation search aggregator that indexes multiple documentation sources.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text) | `CRDT WebSocket` |
| Source filter | (UI) | Filter by documentation source |

### Tips

- Refs aggregates across multiple documentation sites, useful when you are unsure which source has the answer
- Results link back to the original documentation page
- Best for broad searches across multiple ecosystems; use direct site search when you know the source

---

## Context7

MCP-based documentation lookup service. Provides up-to-date documentation and code examples for libraries.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Library resolution | `resolve-library-id` | Resolve a library name to its Context7 ID |
| Documentation query | `query-docs` | Query documentation for a resolved library |

### Special Features

- **MCP integration:** Accessible as an MCP tool within Claude and other LLM agents
- **Up-to-date content:** Pulls current documentation, not training-data snapshots
- **Code examples:** Returns relevant code examples alongside documentation text
- **Library resolution:** Disambiguates library names to specific packages

### Tips

- Context7 is most useful when you need documentation content within an agent workflow (not a browser)
- Resolve the library ID first, then query for specific topics within that library
- Particularly valuable for checking current API signatures that may have changed since training data cutoff
- Use for verification searches to confirm that an API works as expected
