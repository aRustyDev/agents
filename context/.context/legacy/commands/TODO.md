# Slash Command TODO list

- [ ] `/update-frontmatter "file"` : Review document and update frontmatter based on content.
  - Update `tags`: Will require some central tag taxonomy or schema to reference.
  - Update `scope`:
  - Update `roles`:
  - Update `audience`:
  - Update `related`: List of `id` of related documents.
    - Docs that aren't project local must be centrally listed by `id` in `reference.md`.

`roles` or `audience`: identifies who should act on the guidance (e.g., `["devops", "cloud-engineer"]`).
`appliesTo` or `scope`: clarifies the systems or toolchains governed by the document.
`lastUpdated` (ISO timestamp) and optionally `version`: helps agents prefer fresher guidance and detect staleness.

["cryptography", "iac", "terraform", "packer", "ansible", "cloud"]
