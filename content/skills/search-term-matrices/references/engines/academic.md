# Academic Search Engines

Operators and tips for academic and research-focused search engines.

## Table of Contents

- [Google Scholar](#google-scholar)
- [Semantic Scholar](#semantic-scholar)
- [arXiv](#arxiv)
- [ACL Anthology](#acl-anthology)
- [PubMed](#pubmed)
- [Scopus](#scopus)
- [medRxiv](#medrxiv)
- [bioRxiv](#biorxiv)
- [PaperswithCode](#paperswithcode)

---

## Google Scholar

Google's academic paper index. Covers journals, conference proceedings, preprints, theses, and patents.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Exact phrase | `"phrase"` | `"conflict-free replicated data type"` |
| Author | `author:name` | `author:kleppmann CRDT` |
| Source / journal | `source:journal` | `source:"VLDB" CRDT` |
| Title contains | `intitle:word` | `intitle:CRDT survey` |
| All in title | `allintitle:words` | `allintitle:CRDT collaborative editing` |
| Exclude term | `-term` | `CRDT -blockchain` |
| OR | `OR` | `CRDT OR "operational transformation"` |
| Date range | (via Advanced Search UI) | Custom year range |
| Year range (URL) | `as_ylo=YYYY&as_yhi=YYYY` | URL param: `as_ylo=2020&as_yhi=2024` |

### Tips

- Google Scholar does not support `site:` or `filetype:` operators
- Use the "Cited by" link to find papers that reference a foundational work
- The "Related articles" link surfaces semantically similar papers
- Year range filtering is only available through the left sidebar or URL parameters, not via query syntax
- Scholar profiles let you follow specific authors and get alerts on new publications
- For systematic reviews, combine Scholar with Semantic Scholar for better coverage

---

## Semantic Scholar

AI-powered academic search engine from the Allen Institute for AI. Strong in computer science, biomedical, and related fields.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text) | `CRDT collaborative text editing` |
| Year filter | `year:YYYY` or `year:YYYY-YYYY` | `year:2020-2024` (via API/UI filter) |
| Venue filter | (UI filter) | Filter by conference or journal |
| Field of study | (UI filter) | Filter by Computer Science, Medicine, etc. |
| Open access filter | (UI toggle) | Show only open access papers |
| Author filter | (UI filter) | Filter by specific author |

### Special Features

- **TLDR summaries:** AI-generated one-sentence summaries for most papers
- **Citation context:** Shows the sentence where a citation appears, not just the count
- **Influential citations:** Distinguishes between perfunctory and substantive citations
- **Research feeds:** Personalized paper recommendations based on your library
- **API access:** Full REST API for programmatic search (`api.semanticscholar.org`)

### Tips

- Semantic Scholar's API is free and well-documented; useful for building automated research pipelines
- The "Influential Citations" metric is more meaningful than raw citation count for assessing impact
- TLDR summaries save time when scanning large result sets
- Coverage is strongest in CS, biomedicine, and physics; weaker in humanities and social sciences
- Use the API's `fieldsOfStudy` parameter to constrain results to specific disciplines

---

## arXiv

Open-access preprint server. Primary venue for early-stage research in physics, math, CS, and related fields.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| All fields | (free text) | `CRDT collaborative editing` |
| Title | `ti:term` | `ti:CRDT` |
| Author | `au:name` | `au:kleppmann` |
| Abstract | `abs:term` | `abs:"text editing"` |
| Category | `cat:category` | `cat:cs.DC` (distributed computing) |
| Journal ref | `jr:journal` | `jr:"VLDB"` |
| AND | `AND` | `ti:CRDT AND abs:collaborative` |
| OR | `OR` | `ti:CRDT OR ti:"operational transformation"` |
| ANDNOT | `ANDNOT` | `ti:CRDT ANDNOT abs:blockchain` |
| ID | `id:YYMM.NNNNN` | `id:2409.12345` |

### Categories (Selected CS)

| Category | Name |
|----------|------|
| `cs.DC` | Distributed, Parallel, and Cluster Computing |
| `cs.DB` | Databases |
| `cs.PL` | Programming Languages |
| `cs.SE` | Software Engineering |
| `cs.AI` | Artificial Intelligence |
| `cs.LG` | Machine Learning |
| `cs.CL` | Computation and Language (NLP) |
| `cs.CR` | Cryptography and Security |
| `cs.DS` | Data Structures and Algorithms |

### Tips

- arXiv papers are preprints; they may not be peer-reviewed yet
- Use category filtering to avoid noise from unrelated fields (e.g., `CRDT` also appears in physics contexts)
- The arXiv API supports structured queries for automated ingestion
- Check the "journal-ref" field to see if a preprint was later published in a peer-reviewed venue
- arXiv IDs encode the submission date: `YYMM.NNNNN`

---

## ACL Anthology

Digital archive for computational linguistics and NLP research.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text) | `collaborative text editing` |
| Author filter | (UI) | Filter by author name |
| Venue filter | (UI) | Filter by conference (ACL, EMNLP, NAACL, etc.) |
| Year filter | (UI) | Filter by publication year |

### Special Features

- **Complete NLP coverage:** All major CL/NLP conferences and workshops
- **BibTeX export:** Every paper has a one-click BibTeX entry
- **Open access:** All papers are freely available as PDFs
- **Anthology ID:** Stable identifiers for every paper (e.g., `2023.acl-long.1`)

### Tips

- ACL Anthology is the authoritative source for NLP/CL papers; prefer it over Google Scholar for this domain
- Search is keyword-based with limited operator support; use broad terms and filter via the UI
- The anthology covers ACL, EMNLP, NAACL, EACL, CoNLL, and many workshops
- Useful when researching language-related aspects of collaborative editing, text generation, etc.

---

## PubMed

National Library of Medicine's index of biomedical and life science literature.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Field tag (Title) | `[ti]` | `CRDT[ti]` |
| Field tag (Author) | `[au]` | `kleppmann[au]` |
| Field tag (Journal) | `[ta]` | `nature[ta]` |
| Field tag (MeSH) | `[mesh]` | `"data structures"[mesh]` |
| Field tag (Abstract) | `[tiab]` | `"real-time collaboration"[tiab]` |
| Date range | `YYYY/MM/DD:YYYY/MM/DD[dp]` | `2020/01/01:2024/12/31[dp]` |
| Publication type | `[pt]` | `review[pt]` |
| AND | `AND` | `CRDT[ti] AND collaborative[tiab]` |
| OR | `OR` | `CRDT[ti] OR "operational transformation"[ti]` |
| NOT | `NOT` | `CRDT[ti] NOT blockchain[tiab]` |

### Tips

- PubMed uses MeSH (Medical Subject Headings) for controlled vocabulary; use MeSH terms for precise biomedical searches
- The `[tiab]` tag searches both title and abstract simultaneously
- PubMed Central (PMC) is a separate full-text archive; PubMed itself indexes abstracts
- Use PubMed for any research that touches biomedical applications, health informatics, or clinical data
- The E-utilities API enables programmatic access for bulk searches

---

## Scopus

Elsevier's abstract and citation database. Broader coverage than PubMed, covering engineering, social sciences, and more.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Title | `TITLE(term)` | `TITLE(CRDT)` |
| Abstract | `ABS(term)` | `ABS("collaborative editing")` |
| Title + Abstract + Keywords | `TITLE-ABS-KEY(term)` | `TITLE-ABS-KEY(CRDT)` |
| Author | `AUTH(name)` | `AUTH(kleppmann)` |
| Affiliation | `AFID(id)` or `AF-ID(id)` | `AF-ID(60021784)` |
| Source / journal | `SRCTITLE(journal)` | `SRCTITLE("VLDB Journal")` |
| Year | `PUBYEAR = YYYY` | `PUBYEAR > 2019` |
| DOI | `DOI(doi)` | `DOI(10.1145/12345)` |
| AND / OR / AND NOT | `AND`, `OR`, `AND NOT` | `TITLE(CRDT) AND PUBYEAR > 2020` |
| Exact phrase | `{phrase}` | `{conflict-free replicated data type}` |
| Subject area | `SUBJAREA(code)` | `SUBJAREA(COMP)` |

### Tips

- Scopus requires institutional access (paid); check if your organization has a subscription
- The `TITLE-ABS-KEY()` operator is the most commonly used for broad searches
- Scopus citation analysis tools are useful for identifying influential papers and tracking research trends
- Coverage extends beyond STEM to include social sciences, arts, and humanities
- Use `PUBYEAR` for date filtering; more reliable than free-text year mentions

---

## medRxiv

Preprint server for health sciences (epidemiology, clinical research, health informatics).

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text) | `real-time clinical data synchronization` |
| Author | (UI filter) | Filter by author |
| Date range | (UI filter) | Filter by posting date |
| Subject area | (UI filter) | Filter by subject collection |

### Tips

- medRxiv papers are preprints and have not been peer-reviewed; treat findings with appropriate caution
- Useful for cutting-edge health sciences research that has not yet appeared in PubMed
- Search functionality is basic keyword matching; use broad terms and scan results manually
- Cross-reference findings with PubMed to check if a preprint was later published in a journal

---

## bioRxiv

Preprint server for biological sciences.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text) | `CRISPR gene editing efficiency` |
| Author | (UI filter) | Filter by author |
| Date range | (UI filter) | Filter by posting date |
| Subject area | (UI filter) | Filter by subject collection (e.g., Bioinformatics, Genomics) |

### Tips

- bioRxiv is the biology counterpart to medRxiv; similar caveats about preprint status apply
- Strongest in molecular biology, genomics, neuroscience, and bioinformatics
- For computational biology topics, also check arXiv `q-bio` categories
- The bioRxiv API supports programmatic access for bulk retrieval

---

## PaperswithCode

Links academic papers to their code implementations, datasets, and benchmarks.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text) | `CRDT collaborative editing` |
| Task filter | (UI) | Filter by ML/CS task |
| Dataset filter | (UI) | Filter by dataset |
| Method filter | (UI) | Filter by method/model |

### Special Features

- **Code links:** Most papers are linked to their GitHub/GitLab implementations
- **Leaderboards:** Benchmarks with state-of-the-art rankings per task
- **Datasets:** Curated dataset listings with download links
- **Methods:** Taxonomy of methods used across papers

### Tips

- PaperswithCode is essential when you need not just the paper but a working implementation
- Strongest in machine learning, computer vision, and NLP; weaker in other CS areas
- The "Libraries" section shows which frameworks are used most for a given task
- Use this to validate that a paper's claims are reproducible (code available = higher confidence)
- Check the "Results" tab for benchmark comparisons across papers
