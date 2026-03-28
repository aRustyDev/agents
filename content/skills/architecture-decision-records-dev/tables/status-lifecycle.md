# ADR Status Lifecycle

## Status Definitions

| Status | Meaning | Who Can Set |
|--------|---------|-------------|
| Proposed | Under discussion, not yet approved | Any contributor |
| Accepted | Approved and drives implementation | Team lead / maintainer |
| Deprecated | No longer relevant, not replaced | Team lead / maintainer |
| Superseded | Replaced by a newer ADR | Team lead / maintainer |
| Withdrawn | Rejected before implementation | Proposer or team lead |

## Transitions

```
Proposed ──→ Accepted ──→ Deprecated
    │            │
    │            └──→ Superseded by ADR-NNN
    │
    └──→ Withdrawn
```

| From | To | Trigger | Required Action |
|------|----|---------|-----------------|
| Proposed | Accepted | Team/lead approval | Resolve all INVESTIGATE markers |
| Proposed | Withdrawn | Decision rejected or no longer needed | Document rejection reason |
| Accepted | Deprecated | Decision no longer relevant | Add deprecation context |
| Accepted | Superseded | New ADR replaces this one | Link to replacement ADR |

## Supersession Workflow

| Step | Action | File |
|------|--------|------|
| 1 | Create new ADR with replacement decision | New ADR |
| 2 | Add `related: { supersedes: [<old-uuid>] }` in frontmatter | New ADR |
| 3 | Reference old ADR in context, explain why it's replaced | New ADR |
| 4 | Change `status: superseded` | Old ADR |
| 5 | Add note: `Superseded by [ADR-NNN](./adr-NNN-title.md)` | Old ADR |

Never delete the old ADR — it preserves decision history.

## Deprecation Workflow

| Step | Action |
|------|--------|
| 1 | Update `status: deprecated` |
| 2 | Add context explaining why the decision is no longer relevant |
| 3 | No replacement ADR needed (unlike supersession) |

## Governance

| Question | Answer |
|----------|--------|
| Who can propose? | Any contributor |
| Who can accept? | Team lead or designated maintainer |
| Can accepted ADRs be edited? | No — write a new ADR that supersedes |
| Can proposed ADRs be edited? | Yes — iteration is expected before acceptance |
| Minimum review period? | Project-specific (document in CONTRIBUTING.md) |
