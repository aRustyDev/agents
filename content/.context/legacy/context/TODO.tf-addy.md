# Terraform Provider Addy Roadmap (Grouped)

## Foundation
- [ ] Normalize provider address (development vs registry).
- [ ] Correct api_key error path (path.Root("api_key")).

- [ ] Single source version usage (inject from internal/about/version.go).
- [ ] ENV var precedence: ADDY_API_KEY > config attribute (doc & code).
- [ ] Move license text to top-level LICENSE file.

## HTTP & Error Handling
- [ ] Implement error loader (parse errors.toml once, expose lookup).
- [ ] Refactor HTTP client: timeout, User-Agent, retry on 429 with backoff+jitter.
- [ ] Centralize error wrapping (status + meaning + raw body excerpt).
- [ ] Add rate limit metrics counters (optional future).

## Data Sources (Read-only / First Pass)
- [ ] api_token_details (refine: tests + null expiry handling).
- [ ] app_version (simple schema).
- [ ] domain_options.
- [ ] domains (list, minimal attrs, pagination).
- [ ] domain (single).
- [ ] aliases (list).
- [ ] alias (single).
- [ ] recipients (list).
- [ ] failed_deliveries (list + single).
- [ ] rules (list).
- [ ] usernames (list).

## Resources (CRUD / State)
- [ ] domain (activation, catch_all toggles).
- [ ] alias (create/update/delete).
- [ ] recipient (with encryption flags as attributes).
- [ ] rule (conditions/actions nested blocks).
- [ ] username (activation, catch_all, login flags).
- [ ] Consider modeling encryption toggles as part of recipient resource rather than separate resources.

## Cross-Cutting
- [ ] Pagination helper utility (shared).
- [ ] Retry helper wrapping Curl.
- [ ] Shared model structs (internal/model) for unmarshalling.

## Testing & Quality
- [ ] Unit test harness (mock RoundTripper).
- [ ] Golangci-lint integration.
- [ ] Acceptance test scaffold (TF_ACC gating).
- [ ] Add Makefile (build, test, lint, docs).
- [ ] Golden file tests for representative JSON payloads.

## Documentation
- [ ] Expand README (install, usage, examples, env var, limitations).
- [ ] Add examples for each resource/data source.
- [ ] Inline MarkdownDescription for all attributes.
- [ ] CONTRIBUTING.md (development workflow).
- [ ] CHANGELOG.md (start tracking changes).
- [ ] Registry documentation templates (once near release).

## Importers (Post-Stability)
- [ ] domain importer (by id or domain name).
- [ ] alias importer.
- [ ] recipient importer.
- [ ] rule importer.
- [ ] username importer.

## Release Prep
- [ ] Version bump & tag strategy.
- [ ] Validate schema stability (no breaking changes planned short-term).
- [ ] Pre-release audit: remove panics, ensure error messages consistent.

## Optional / Deferred
- [ ] Bulk endpoints modeling.
- [ ] Code generation from OpenAPI.
- [ ] Performance tuning (connection reuse, concurrency).
- [ ] Terraform debug docs.
