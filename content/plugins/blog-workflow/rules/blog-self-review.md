# Self-Review Standard

Self-review is an automated quality check that runs after artifact creation or modification.

## How It Works

1. Self-review uses the **same checklist** as the dedicated review command
2. Only **fail** items are flagged (items that would block approval)
3. **Warn** items are left for dedicated review (human gating point)

## When It Runs

Self-review runs automatically at the end of:

- `brainstorm.md` — checks idea against `idea.md` checklist
- `draft-plan.md` — checks plan against `plan.md` checklist
- `refine.md` — checks artifact against its type checklist
- All `draft.md` commands — checks output against relevant checklist

## Outcome Handling

| Result | Behavior |
|--------|----------|
| All pass | Continue silently |
| Fail items | Report issues, set status to `draft` |
| Warn items | Ignored (left for `/review`) |

## Example

After `brainstorm.md` creates an idea:

1. Load `idea.md` checklist
2. Check each criterion
3. If "Scope is achievable" fails → report and set status: `draft`
4. If "Unique angle" is warning-level → ignore (human will check in review)
