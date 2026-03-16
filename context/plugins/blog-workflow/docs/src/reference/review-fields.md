# Review Fields Reference

Reference for universal and subtype-specific review fields.

## Universal Fields

These fields apply to all review types:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `review-subtype` | string | Yes | Type of review (course, tool, etc.) |
| `rating` | number | No | Overall rating (1-5) |
| `summary` | string | Yes | Brief summary/verdict |
| `pros` | string[] | Yes | List of positives |
| `cons` | string[] | Yes | List of negatives |
| `recommendation` | string | Yes | Who should/shouldn't use this |
| `last-evaluated` | date | Yes | When review was last updated |

### Example

```yaml
type: review
review-subtype: tool
rating: 4
summary: "Excellent editor for terminal enthusiasts"
pros:
  - "Fast startup"
  - "Great keybindings"
  - "Active development"
cons:
  - "Smaller plugin ecosystem"
  - "Steeper learning curve"
recommendation: "Recommended for Vim users wanting a modern alternative"
last-evaluated: 2026-03-01
```

---

## Built-in Subtypes

### course

Review of educational courses (online, in-person, bootcamps).

| Field | Type | Description |
|-------|------|-------------|
| `instructor` | string | Instructor name(s) |
| `platform` | string | Where hosted (Udemy, Coursera, etc.) |
| `duration` | string | Course length |
| `difficulty` | string | Beginner, Intermediate, Advanced |
| `prerequisites` | string[] | What you should know first |
| `instructor-quality` | number | Rating 1-5 |
| `content-quality` | number | Rating 1-5 |
| `production-quality` | number | Rating 1-5 |
| `value-for-money` | number | Rating 1-5 |

### tool

Review of software tools, CLI utilities, applications.

| Field | Type | Description |
|-------|------|-------------|
| `version-reviewed` | string | Version tested |
| `platforms` | string[] | OS/platforms supported |
| `pricing` | string | Free, paid, freemium details |
| `installation` | number | Ease of install (1-5) |
| `documentation` | number | Doc quality (1-5) |
| `performance` | number | Performance (1-5) |
| `ergonomics` | number | UX/DX (1-5) |

### library

Review of programming libraries, frameworks, SDKs.

| Field | Type | Description |
|-------|------|-------------|
| `language` | string | Primary language |
| `version-reviewed` | string | Version tested |
| `license` | string | Open source license |
| `api-ergonomics` | number | API design quality (1-5) |
| `documentation` | number | Doc quality (1-5) |
| `maintenance` | number | Active development (1-5) |
| `community` | number | Community support (1-5) |
| `test-coverage` | string | Testing quality notes |

### book

Review of technical books (physical, ebook, audiobook).

| Field | Type | Description |
|-------|------|-------------|
| `author` | string | Author name(s) |
| `publisher` | string | Publisher |
| `published` | string | Publication year |
| `pages` | number | Page count |
| `isbn` | string | ISBN |
| `format-read` | string | Physical, ebook, audiobook |
| `writing-quality` | number | Clarity, style (1-5) |
| `technical-depth` | number | Depth of content (1-5) |
| `practicality` | number | Applied value (1-5) |
| `still-relevant` | boolean | Current in 2026? |

### policy

Review of policies, standards, specifications, RFCs.

| Field | Type | Description |
|-------|------|-------------|
| `issuer` | string | Who issued the policy |
| `effective-date` | date | When it took effect |
| `scope` | string | What it covers |
| `clarity` | number | How clear is it (1-5) |
| `practicality` | number | How implementable (1-5) |
| `impact` | string | Who is affected |

---

## Custom Subtypes

Create custom subtypes in `content/_templates/reviews/`:

```markdown
---
name: conference
extends: review  # Inherits universal fields
description: Review of technical conferences
---

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `location` | string | Where held |
| `dates` | string | When held |
| `attendance` | number | Approximate attendees |
| `talk-quality` | number | Rating 1-5 |
| `networking` | number | Rating 1-5 |
| `venue-quality` | number | Rating 1-5 |
| `value-for-cost` | number | Rating 1-5 |
```

### Using Custom Subtypes

```yaml
type: review
review-subtype: conference
location: "San Francisco, CA"
dates: "March 10-12, 2026"
talk-quality: 4
networking: 5
```

---

## Adding Fields

### Via Command

```bash
/blog/review/fields/add tool "security-features"
```

This adds the field to the tool subtype template.

### Manually

Edit `content/_templates/reviews/tool.md` to add fields.

---

## Field Validation

At build time:

- Required fields must be present
- Numeric ratings must be 1-5
- Dates must be valid ISO format
- Custom fields are allowed (no strict validation)
