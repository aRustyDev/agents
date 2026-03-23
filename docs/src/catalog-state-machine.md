# Skill Catalog Entry State Machine

## States Summary

| State | Count | % | Terminal? |
|-------|-------|---|-----------|
| Not Found | 280 | 2.2% | Yes |
| Archived | 833 | 6.4% | Yes |
| Never Attempted | 72 | 0.6% | No |
| Batch Failed (unclassified) | 458 | 3.5% | No (reclassifiable) |
| Permanent Download Failure | 2,145 | 16.5% | Yes (unless repo restored) |
| Partially Analyzed | 2,165 | 16.7% | No (backfillable / re-analyzable) |
| Fully Complete | 7,049 | 54.2% | No (progresses to Tier 2) |

## State Machine

```mermaid
stateDiagram-v2
    direction TB

    [*] --> Discovered : Registry scan finds source/skill

    %% === Availability Check ===
    Discovered --> NotFound : HTTP 404
    Discovered --> Archived : Repo archived
    Discovered --> Available : HTTP 200, public

    %% === Terminal unavailable states ===
    NotFound --> [*]
    Archived --> [*]

    %% === Available entry lifecycle ===
    Available --> NeverAttempted : Queued for processing

    %% === Download phase ===
    NeverAttempted --> Downloading : analyze picks up entry
    BatchFailed --> Downloading : --retry-errors
    Timeout --> Downloading : --retry-errors

    Downloading --> PermanentFail : Auth error, repo deleted, private
    Downloading --> SkillMissing : Clone OK, SKILL.md not found
    Downloading --> Timeout : Clone exceeds 30s
    Downloading --> Downloaded : Clone + discover succeeds

    SkillMissing --> PermanentFail : Classified as download_failed

    %% === Agent analysis phase ===
    Downloaded --> AgentAnalysis : Haiku agent dispatched

    AgentAnalysis --> PartiallyAnalyzed : Output missing fields (complexity, keywords)
    AgentAnalysis --> FullyComplete : All Tier 1 fields present
    AgentAnalysis --> BatchFailed : Agent crash / parse failure (legacy)

    %% === Backfill phase (mechanical, no agent) ===
    PartiallyAnalyzed --> BackfillAttempt : catalog backfill
    PartiallyAnalyzed --> Downloading : analyze --missing <field>

    BackfillAttempt --> PartiallyAnalyzed : Repo deleted since analysis
    BackfillAttempt --> FullyComplete : All gaps filled mechanically

    %% === Error reclassification ===
    BatchFailed --> PermanentFail : backfill reclassifies to download_failed
    BatchFailed --> SourceInvalid : backfill reclassifies to source_invalid

    %% === Stale detection (future) ===
    FullyComplete --> StaleDetected : catalog stale finds treeSha mismatch
    StaleDetected --> Downloading : Re-analyze with --force

    %% === Tier 2 progression ===
    FullyComplete --> Tier2Analysis : Sonnet agent (Phase 5)

    %% === State descriptions ===
    state "NotFound" as NotFound : 280 entries
    state "Archived" as Archived : 833 entries
    state "NeverAttempted" as NeverAttempted : 72 entries
    state "Timeout" as Timeout : 0 entries (retryable)
    state "PermanentFail" as PermanentFail : 2,145 entries
    state "SourceInvalid" as SourceInvalid : Unparseable source string
    state "BatchFailed" as BatchFailed : 458 entries (legacy)
    state "PartiallyAnalyzed" as PartiallyAnalyzed : 2,165 entries
    state "FullyComplete" as FullyComplete : 7,049 entries
    state "StaleDetected" as StaleDetected : Upstream content changed
    state "Tier2Analysis" as Tier2Analysis : Phase 5 (future)
```

## Transition Table

| From | To | Trigger | Notes |
|------|----|---------|-------|
| Discovered | NotFound | Availability check returns 404 | Terminal |
| Discovered | Archived | Repo flagged as archived | Terminal |
| Discovered | Available | HTTP 200, public repo | Enters processing pipeline |
| Available | NeverAttempted | Initial state after availability check | Waiting for analyze run |
| NeverAttempted | Downloading | `catalog analyze` picks up entry | Normal flow |
| BatchFailed | Downloading | `--retry-errors` flag | Retries legacy failures |
| Timeout | Downloading | `--retry-errors` flag | Retries timeouts |
| Downloading | PermanentFail | Clone fails (auth, deleted, private) | `download_failed`, not retryable |
| Downloading | SkillMissing | Clone OK but SKILL.md not found | Skill name mismatch |
| Downloading | Timeout | Clone exceeds 30s | `download_timeout`, retryable |
| Downloading | Downloaded | Clone + discover succeeds | Ready for agent |
| SkillMissing | PermanentFail | Classified as `download_failed` | Immediate transition |
| Downloaded | AgentAnalysis | Haiku agent dispatched in worktree | Judgment analysis |
| AgentAnalysis | FullyComplete | All fields in NDJSON output | Best outcome |
| AgentAnalysis | PartiallyAnalyzed | Missing complexity/keywords in output | Agent output incomplete |
| AgentAnalysis | BatchFailed | Agent crash or NDJSON parse failure | Legacy error type |
| PartiallyAnalyzed | BackfillAttempt | `catalog backfill` command | Mechanical, no agent |
| PartiallyAnalyzed | Downloading | `analyze --missing <field>` | Full re-analysis |
| BackfillAttempt | FullyComplete | All gaps filled mechanically | headingTree, treeSha, keywords |
| BackfillAttempt | PartiallyAnalyzed | Repo deleted since original analysis | Can't fill remaining gaps |
| BatchFailed | PermanentFail | `catalog backfill` reclassifies | Structured error type |
| BatchFailed | SourceInvalid | `catalog backfill` reclassifies | Source string unparseable |
| FullyComplete | StaleDetected | `catalog stale` finds treeSha mismatch | Upstream changed |
| StaleDetected | Downloading | Re-analyze with `--force` | Fresh analysis |
| FullyComplete | Tier2Analysis | Phase 5 (future) | Sonnet-level quality scoring |

## Why Entries Get Stuck

### Partially Analyzed (2,165)

Entries were analyzed successfully in an earlier run, but the repo has since been deleted/made private. The backfill command can't re-download to fill missing fields. These entries have `wordCount` (from the original analysis) but are missing `treeSha` (not computed in old runs), `headingTree` (not computed in old runs), or `complexity` (agent didn't output it).

### Permanent Download Failure (2,145)

Repos that consistently fail to clone: deleted, made private, renamed, or require auth that isn't available. These have `lastErrorType: download_failed` and `retryable: false`.

### Batch Failed (458)

Legacy errors from runs before the structured error classification existed. These have `lastErrorType: batch_failed` — the generic fallback. The `catalog backfill` command reclassifies some of these, but 458 remain because the backfill also failed (can't determine the specific error type if the repo is gone).

### Never Attempted (72)

Entries that were never picked up by any analyze run. Likely added to the catalog after the last full run, or fell through a gap in batch scheduling.
