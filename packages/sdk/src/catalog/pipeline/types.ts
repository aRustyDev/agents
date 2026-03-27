/**
 * Pipeline-specific types for catalog processing.
 *
 * These extend the base catalog types with tier1 analysis fields,
 * repo manifest structures, and error handling.
 */

import type {
  AvailabilityStatus,
  MechanicalFields,
  CatalogEntry as SdkCatalogEntry,
} from '../types'

// ---------------------------------------------------------------------------
// Legacy CatalogEntry (CLI-compatible shape)
// ---------------------------------------------------------------------------

/**
 * CLI-compatible catalog entry shape used throughout the pipeline.
 * Maps to the original CLI catalog entry format where fields are flat
 * (not nested under mechanical/analysis objects).
 */
export interface CatalogEntry {
  source: string // org/repo
  skill: string // skill name (part after @)
  availability: AvailabilityStatus
}

// ---------------------------------------------------------------------------
// Section Map
// ---------------------------------------------------------------------------

/** A single heading with its line number for section-level navigation. */
export interface SectionMapEntry {
  heading: string
  line: number
  depth: number
}

// ---------------------------------------------------------------------------
// Component Metadata (per-skill enrichment from discovery)
// ---------------------------------------------------------------------------

/**
 * Metadata computed per-component during repo discovery.
 * These fields are added to Tier1Result and stored on catalog entries.
 * All fields are optional — entries from before discovery won't have them.
 */
export interface ComponentMetadata {
  /** Actual path where SKILL.md was found (e.g., "content/skills/foo") */
  discoveredPath?: string
  /** ISO timestamp when this skill was last seen in a discovery run */
  lastSeenAt?: string
  /** HEAD SHA of the repo when skill was last seen */
  lastSeenHeadSha?: string
  /** Previous discoveredPath if the skill was moved */
  movedFrom?: string
  /** Total size of the skill directory in bytes */
  skillSizeBytes?: number
  /** Line count of SKILL.md */
  lineCount?: number
  /** Section map: heading text + line number for navigation */
  sectionMap?: SectionMapEntry[]
  /** All files in the skill directory (relative paths) */
  fileTree?: string[]
  /** True if skill directory contains only SKILL.md (no resources, no subdirs) */
  isSimple?: boolean
}

// ---------------------------------------------------------------------------
// Repo Manifest (per-repo metadata from discovery)
// ---------------------------------------------------------------------------

/**
 * Repo-level metadata captured during discovery.
 * Stored in `.catalog-repos.ndjson` (gitignored).
 */
export interface RepoManifest {
  /** owner/repo identifier */
  repo: string
  /** ISO timestamp of last clone/discovery */
  clonedAt: string
  /** Git HEAD SHA at time of clone */
  headSha: string
  /** Total file count in repo */
  totalFiles: number
  /** Repo size in bytes */
  repoSizeBytes: number
  /** Whether the repo is archived on GitHub */
  archived: boolean
  /** ISO timestamp of most recent commit */
  lastCommitAt?: string
  /** Total number of commits */
  commitCount?: number
  /** Number of unique contributors */
  contributorCount?: number
  /** Number of skills discovered in this repo */
  skillCount: number
  /** Names of discovered skills */
  skills: string[]
}

// ---------------------------------------------------------------------------
// Tier 1 Analysis Types
// ---------------------------------------------------------------------------

export type Tier1ErrorType =
  | 'download_failed'
  | 'download_timeout'
  | 'analysis_failed'
  | 'analysis_timeout'
  | 'rate_limited'
  | 'batch_failed'
  | 'invalid_source_entry'

export interface Tier1Result extends ComponentMetadata {
  source: string
  skill: string
  wordCount?: number
  sectionCount?: number
  fileCount?: number
  headingTree?: Array<{ depth: number; title: string }>
  keywords?: string[]
  internalLinks?: string[]
  externalLinks?: string[]
  complexity?: 'simple' | 'moderate' | 'complex'
  progressiveDisclosure?: boolean
  pdTechniques?: string[]
  bestPracticesMechanical?: { score: number; violations: string[] }
  securityMechanical?: { score: number; concerns: string[] }
  contentHash?: string
  treeSha?: string // git tree SHA of the skill folder (for stale detection)
  tier2Reviewed?: boolean
  // Error cache fields (detail lives in error log)
  attemptCount?: number
  lastErrorType?: Tier1ErrorType
  retryable?: boolean
  possibleForkOf?: string
  runId?: string
  batchId?: string
  analyzedAt?: string
}

// ---------------------------------------------------------------------------
// Error Log Types (ADR-019)
// ---------------------------------------------------------------------------

export interface ErrorRecord {
  source: string
  skill: string
  runId: string
  batchId: string
  timestamp: string
  errorType: Tier1ErrorType
  errorDetail: string
  errorCode?: number
  retryable: boolean
}

// ---------------------------------------------------------------------------
// Composed Types
// ---------------------------------------------------------------------------

/** CatalogEntry extended with optional Tier1 analysis fields. */
export type CatalogEntryWithTier1 = CatalogEntry & Partial<Tier1Result>

/** Internal fields used during processing but not persisted to catalog. */
export interface TransientErrorFields {
  error?: string
  errorType?: Tier1ErrorType
  errorDetail?: string
  errorCode?: number
}

/**
 * Tier1Result extended with transient error fields from the orchestrator.
 * These fields are used internally by mergeTier1Results to route errors
 * to the error log — they are NOT written to the catalog.
 */
export type Tier1ResultWithTransient = Tier1Result & TransientErrorFields

/** Result from a backfill operation — partial fields only. */
export interface BackfillResult {
  source: string
  skill: string
  headingTree?: Array<{ depth: number; title: string }>
  treeSha?: string
  keywords?: string[]
  fileCount?: number
  sectionCount?: number
  error?: string
  errorType?: Tier1ErrorType
  errorDetail?: string
  runId?: string
}

/** Validation report for batch results. */
export interface ValidationReport {
  total: number
  missingContentHash: number
  pendingContentHash: number
  missingWordCount: number
  missingKeywords: number
  issues: string[]
}

/** Processing filter options. */
export interface FilterProcessingOpts {
  force?: boolean
  retryErrors?: boolean
}
