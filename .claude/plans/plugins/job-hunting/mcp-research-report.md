# MCP Server Research: Job-Hunting

**Date**: 2026-02-05
**Purpose**: Job hunting automation - LinkedIn, resume building, job search, application tracking

---

## Top Recommendations

### Recommended Suite

For a complete job-hunting workflow, use this combination:

| Component | Server | Install |
|-----------|--------|---------|
| Job Discovery | mcp-jobs | `npx -y mcp-jobs` |
| Google Jobs | google-jobs-server | `npx -y @smithery/cli install @chanmeng666/google-jobs-server --client claude` |
| LinkedIn | linkedin-mcp-server | `uvx linkedin-scraper-mcp` |
| Applications | cv-forge | `npm install -g cv-forge` |
| Tracking | job-tracker-ai | Manual (Node.js + Supabase) |

---

## Detailed Server Profiles

### 1. LinkedIn MCP (stickerdaniel) — 96/100

| Field | Value |
|-------|-------|
| Repository | https://github.com/stickerdaniel/linkedin-mcp-server |
| Install | `uvx linkedin-scraper-mcp` |
| Language | Python |
| Stars | 804 |
| Last Updated | 2026-02-04 |
| Auth Required | Yes (LinkedIn session cookie `li_at`) |

**Features**:
- Profile scraping (work history, education, skills, connections)
- Company analysis and company posts
- Job search with filters (keywords, location)
- Job recommendations
- Job details retrieval
- Session management

**Tools**:
| Tool | Description |
|------|-------------|
| `get_person_profile` | Get detailed profile info including work history, education, contacts |
| `get_company_profile` | Extract company information including employees |
| `get_company_posts` | Get recent posts from a company LinkedIn feed |
| `search_jobs` | Search for jobs with keywords and location filters |
| `get_job_details` | Get detailed information about a specific job posting |
| `close_session` | Close browser session and clean up resources |

**Setup**:
```bash
# Install
curl -LsSf https://astral.sh/uv/install.sh | sh
uvx playwright install chromium

# Create session (first time)
uvx linkedin-scraper-mcp --get-session

# Run
uvx linkedin-scraper-mcp
```

**Claude Desktop Config**:
```json
{
  "mcpServers": {
    "linkedin": {
      "command": "uvx",
      "args": ["linkedin-scraper-mcp"]
    }
  }
}
```

---

### 2. MCP Jobs — 94/100

| Field | Value |
|-------|-------|
| Repository | https://github.com/mergedao/mcp-jobs |
| Install | `npx -y mcp-jobs` |
| Language | TypeScript |
| Stars | 57 |
| Last Updated | 2026-01-31 |
| Auth Required | No (zero-configuration) |

**Features**:
- Multi-platform job aggregation from major recruitment sites
- Job search filtering by position, location, and salary range
- Zero-configuration setup (no API keys needed)
- Real-time job information updates
- Standardized data output compatible with AI models

**Tools**:
| Tool | Description |
|------|-------------|
| `search_jobs` | Search and filter jobs by position, location, salary |
| `get_job_details` | Fetch comprehensive information about job positions |
| `list_platforms` | List available job recruitment platforms |
| `get_latest_jobs` | Retrieve latest job listings across platforms |

**Claude Desktop Config**:
```json
{
  "mcpServers": {
    "jobs": {
      "command": "npx",
      "args": ["-y", "mcp-jobs"]
    }
  }
}
```

---

### 3. CV Forge — 93/100

| Field | Value |
|-------|-------|
| Repository | https://github.com/thechandanbhagat/cv-forge |
| Install | `npm install -g cv-forge` |
| Language | TypeScript |
| Stars | 23 |
| Last Updated | 2025-12-19 |
| Auth Required | No |

**Features**:
- Parse job requirements and extract key information
- Generate customized CV content matched to job requirements
- Create personalized cover letters
- Generate professional email templates
- Produce complete application packages in one command
- ATS-friendly optimization
- PDF, HTML, Markdown output formats

**Tools** (14 total):
| Tool | Description |
|------|-------------|
| `parse_job_requirements` | Extract skills, qualifications, emails from job postings |
| `generate_cv` | Generate tailored CV in various formats |
| `generate_cover_letter` | Create tailored cover letter for specific job |
| `generate_email_template` | Professional email templates with auto email extraction |
| `draft_complete_application` | One-stop: CV + cover letter + email template |

**Claude Desktop Config**:
```json
{
  "mcpServers": {
    "cv-forge": {
      "command": "cv-forge",
      "args": []
    }
  }
}
```

---

### 4. Google Jobs Server — 91/100

| Field | Value |
|-------|-------|
| Repository | https://github.com/ChanMeng666/server-google-jobs |
| Install | `npx -y @smithery/cli install @chanmeng666/google-jobs-server --client claude` |
| Language | JavaScript |
| Stars | 18 |
| Last Updated | 2026-02-04 |
| Auth Required | Yes (SerpAPI key - free tier: 100/month) |

**Features**:
- Multi-language support (English, Chinese, Japanese, Korean)
- Flexible search parameters (keywords, location, employment type, salary)
- Geographic radius search
- Pagination support
- Advanced sorting (date, relevance, salary)

**Tools**:
| Tool | Description |
|------|-------------|
| `search_jobs` | Search Google Jobs with comprehensive filters |

**Environment**:
```bash
export SERP_API_KEY=your_key_here
```

---

### 5. Job Tracker AI — 89/100

| Field | Value |
|-------|-------|
| Repository | https://github.com/shayyzhakov/job-tracker-ai |
| Install | Manual (clone + npm install + build) |
| Language | TypeScript |
| Stars | 0 |
| Last Updated | 2025-07-20 |
| Auth Required | Yes (Supabase access token) |

**Features**:
- Company and role tracking
- Interview event management
- Contact CRM
- Supabase persistent storage
- Multi-session tracking

**Tools**:
| Tool | Description |
|------|-------------|
| `getCompanies` | Fetch all companies with active interview progress |
| `updateCompany` | Update company information |
| `getRoles` | Fetch all roles/applications |
| `createRole` | Create new job application entry |
| `getInterviewEvents` | Fetch interview events and schedules |
| `createInterviewEvent` | Log new interview event |
| `getContacts` | Fetch contact information |
| `createContact` | Add new contact for a company |

**Setup**:
```bash
git clone https://github.com/shayyzhakov/job-tracker-ai.git
cd job-tracker-ai
npm install
npm run build
```

---

## Additional Servers

### Resume & Cover Letter

| Server | Score | Install | Focus |
|--------|-------|---------|-------|
| resumake-mcp | 85 | manual | LaTeX resumes (9 templates) |
| cover-letter-mcp | 84 | docker | Professional PDF cover letters |
| mcp-resume | 80 | manual | Resume chat + job analysis |

### Job Search

| Server | Score | Install | Focus |
|--------|-------|---------|-------|
| job-searchoor | 88 | `npx -y job-searchoor` | Simple keyword filtering |
| hh-mcp-server | 87 | npx | HeadHunter (Russian market) |
| coresignal-mcp | 78 | remote | B2B data (399M+ postings) |
| jobapply-mcp-server | 75 | pip | Job posting scraper |

### Contact & Networking

| Server | Score | Install | Focus |
|--------|-------|---------|-------|
| hunter-mcp | 86 | pip | Email finding (Hunter.io) |
| linkedin-profile-researcher | 83 | npm | Profile + Apollo.io enrichment |
| hatch-mcp-server | 82 | manual | Contact enrichment |

---

## Workflow Example

```
1. DISCOVER: Use mcp-jobs to search across platforms
   → "Search for senior software engineer roles in Austin, TX"

2. RESEARCH: Use linkedin-mcp to analyze companies
   → "Get company profile for Acme Corp"
   → "Search for employees at Acme Corp who are engineering managers"

3. APPLY: Use cv-forge to generate application materials
   → "Parse this job posting and draft a complete application"
   → Outputs: tailored CV, cover letter, email template

4. TRACK: Use job-tracker-ai to manage pipeline
   → "Create a new role entry for Senior Engineer at Acme Corp"
   → "Log interview scheduled for Friday at 2pm"
```

---

## Sources

- [LinkedIn MCP Server](https://github.com/stickerdaniel/linkedin-mcp-server)
- [MCP Jobs](https://github.com/mergedao/mcp-jobs)
- [CV Forge](https://github.com/thechandanbhagat/cv-forge)
- [Google Jobs Server](https://github.com/ChanMeng666/server-google-jobs)
- [Job Tracker AI](https://github.com/shayyzhakov/job-tracker-ai)
- [mcpservers.org](https://mcpservers.org)
- [Smithery Registry](https://smithery.ai)
