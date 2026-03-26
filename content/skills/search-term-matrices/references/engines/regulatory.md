# Regulatory and Compliance Search Engines

Operators and tips for searching regulatory databases, government agencies, and compliance-related sources.

## Table of Contents

- [FDA (U.S. Food and Drug Administration)](#fda-us-food-and-drug-administration)
- [SEC (U.S. Securities and Exchange Commission)](#sec-us-securities-and-exchange-commission)
- [PubMed (Regulatory Context)](#pubmed-regulatory-context)
- [medRxiv (Regulatory Context)](#medrxiv-regulatory-context)
- [bioRxiv (Regulatory Context)](#biorxiv-regulatory-context)

---

## FDA (U.S. Food and Drug Administration)

Regulatory filings, guidance documents, approval databases, and safety information for drugs, devices, biologics, and food.

### Search Surfaces

| Surface | URL | Content |
|---------|-----|---------|
| FDA.gov search | `search.fda.gov` | All FDA content |
| Drugs@FDA | `accessdata.fda.gov/scripts/cder/daf/` | Drug approval packages |
| 510(k) Database | `accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm` | Device clearances |
| PMA Database | `accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm` | Pre-market approvals |
| Guidance Documents | `fda.gov/regulatory-information/search-fda-guidance-documents` | Regulatory guidance |
| MAUDE | `accessdata.fda.gov/scripts/cdrh/cfdocs/cfmaude/search.cfm` | Adverse event reports (devices) |
| FAERS | `fda.gov/drugs/questions-and-answers-fdas-adverse-event-reporting-system-faers` | Adverse event reports (drugs) |
| Federal Register | `federalregister.gov` | Proposed and final rules |

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Google site-scoped | `site:fda.gov term` | `site:fda.gov "software as medical device" guidance` |
| File type | `site:fda.gov filetype:pdf term` | `site:fda.gov filetype:pdf "clinical decision support"` |
| Guidance search | (FDA guidance search page) | Keyword + product area + date range |
| Drugs@FDA | (form fields) | Active ingredient, application number, applicant |
| 510(k) search | (form fields) | Product code, applicant, decision date range |

### Tips

- FDA guidance documents carry significant regulatory weight even though they are not legally binding
- Use `site:fda.gov filetype:pdf` via Google to find specific guidance documents by keyword
- The 510(k) and PMA databases have structured search forms; use product codes for precise results
- MAUDE adverse event reports are useful for risk analysis but contain unverified reports
- Check both the FDA website and the Federal Register for proposed rules that may affect your domain
- The FDA's "Digital Health" and "Software as a Medical Device" pages are entry points for health-tech regulatory research

---

## SEC (U.S. Securities and Exchange Commission)

Regulatory filings, company disclosures, financial statements, and enforcement actions.

### Search Surfaces

| Surface | URL | Content |
|---------|-----|---------|
| EDGAR Full-Text Search | `efts.sec.gov/LATEST/search-index?q=term` | All EDGAR filings |
| EDGAR Company Search | `sec.gov/cgi-bin/browse-edgar?action=getcompany` | Filings by company |
| SEC.gov search | `sec.gov/search` | All SEC content |
| SEC Rules | `sec.gov/rules/` | Proposed and final rules |
| Enforcement Actions | `sec.gov/litigation.shtml` | Enforcement proceedings |

### EDGAR Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Full-text search | (EDGAR EFTS) | `"artificial intelligence" risk factor` |
| Company name | (Company Search form) | `Company: OpenAI` |
| CIK number | (Company Search form) | `CIK: 0001234567` |
| Filing type | (form filter) | `Type: 10-K` (annual report) |
| Date range | (form filter) | Date filed range |
| SIC code | (form filter) | `SIC: 7372` (software) |

### Common Filing Types

| Filing | Description |
|--------|-------------|
| 10-K | Annual report (comprehensive) |
| 10-Q | Quarterly report |
| 8-K | Current report (material events) |
| S-1 | IPO registration statement |
| DEF 14A | Proxy statement |
| 13-F | Institutional investment holdings |
| Form 4 | Insider trading |
| 20-F | Annual report (foreign private issuers) |

### Tips

- EDGAR full-text search is the most powerful tool for searching across all SEC filings
- 10-K filings contain risk factors, business descriptions, and financial data; search these for industry analysis
- The "Risk Factors" section of 10-K filings is particularly useful for understanding industry risks
- Use SIC codes to find all companies in a specific industry sector
- SEC enforcement actions (litigation releases) are useful for compliance research
- The SEC's proposed rules page shows upcoming regulatory changes

---

## PubMed (Regulatory Context)

PubMed is documented in detail in [academic.md](academic.md). This section covers its use specifically for regulatory and compliance research.

### Regulatory-Relevant Searches

| Use Case | Query Pattern | Example |
|----------|---------------|---------|
| Drug safety | `drug_name[tiab] AND adverse[tiab]` | `metformin[tiab] AND adverse[tiab] AND review[pt]` |
| Clinical guidelines | `"practice guideline"[pt]` | `"diabetes management"[tiab] AND "practice guideline"[pt]` |
| Systematic reviews | `"systematic review"[pt]` | `"drug interaction"[tiab] AND "systematic review"[pt]` |
| Regulatory science | `"regulatory science"[tiab]` | `"regulatory science"[tiab] AND "FDA"[tiab]` |
| Post-market surveillance | `"post-market"[tiab] OR "postmarket"[tiab]` | `"medical device"[tiab] AND "postmarket surveillance"[tiab]` |

### Tips

- Use PubMed's publication type filter `[pt]` to find clinical guidelines, systematic reviews, and meta-analyses
- MeSH terms provide controlled vocabulary for regulatory topics (e.g., `"Drug-Related Side Effects and Adverse Reactions"[mesh]`)
- PubMed Central (PMC) has full-text articles; useful when the abstract alone is insufficient
- For drug safety research, combine PubMed searches with FDA FAERS data for a complete picture

---

## medRxiv (Regulatory Context)

medRxiv is documented in detail in [academic.md](academic.md). This section covers its use specifically for regulatory and compliance research.

### Regulatory-Relevant Use Cases

| Use Case | Description |
|----------|-------------|
| Emerging safety signals | Preprints reporting adverse events or safety concerns before journal publication |
| Public health policy | Studies informing policy decisions (e.g., pandemic response, vaccination strategies) |
| Health economics | Cost-effectiveness analyses relevant to regulatory pricing decisions |
| Epidemiological data | Disease burden and incidence data used in regulatory impact assessments |

### Tips

- medRxiv preprints are not peer-reviewed; exercise extra caution when using them for regulatory arguments
- Useful for identifying emerging health concerns before they appear in published literature
- Cross-reference any medRxiv findings with published PubMed articles before citing in regulatory contexts
- Check the "Now published in..." banner at the top of preprints to find the peer-reviewed version

---

## bioRxiv (Regulatory Context)

bioRxiv is documented in detail in [academic.md](academic.md). This section covers its use specifically for regulatory and compliance research.

### Regulatory-Relevant Use Cases

| Use Case | Description |
|----------|-------------|
| Preclinical research | Early-stage biological research relevant to drug/device development |
| Biomarker discovery | Novel biomarkers that may inform diagnostic device regulation |
| Gene therapy | Cutting-edge gene editing and therapy research with regulatory implications |
| Environmental biology | Studies relevant to EPA and environmental regulatory decisions |

### Tips

- bioRxiv preprints are not peer-reviewed; same caveats as medRxiv apply
- Useful for tracking cutting-edge biological research that may create new regulatory categories
- For regulatory submissions, always prefer the peer-reviewed published version of a study
- The "Subject Area" filter helps narrow to bioinformatics, genomics, or other specific fields
