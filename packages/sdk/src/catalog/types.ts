import type { ComponentType } from '../context/types'

export type AvailabilityStatus =
  | 'available'
  | 'archived'
  | 'not_found'
  | 'private'
  | 'error'
  | 'removed_from_repo'

export interface CatalogEntry {
  source: string
  name: string
  type: ComponentType
  availability: AvailabilityStatus
  mechanical?: MechanicalFields
  analysis?: AnalysisFields
  discoveredAt?: string
  analyzedAt?: string
  contentHash?: string
  errorCount?: number
}

export interface MechanicalFields {
  wordCount?: number
  sectionCount?: number
  lineCount?: number
  fileCount?: number
  headingTree?: Array<{ depth: number; title: string }>
  fileTree?: string[]
  skillSizeBytes?: number
  isSimple?: boolean
  keywords?: string[]
}

export interface AnalysisFields {
  complexity?: 'simple' | 'moderate' | 'complex'
  progressiveDisclosure?: boolean
  pdTechniques?: string[]
  bestPractices?: { score: number; violations: string[] }
  security?: { score: number; concerns: string[] }
  refinedKeywords?: string[]
}

export interface CatalogQuery {
  query?: string
  type?: ComponentType
  source?: string
  availability?: AvailabilityStatus
  limit?: number
  offset?: number
}

export interface CatalogFilter {
  type?: ComponentType
  availability?: AvailabilityStatus
  hasAnalysis?: boolean
  source?: string
}

export interface SyncResult {
  added: number
  updated: number
  removed: number
  moved: number
  errors: number
}

export interface StaleResult {
  source: string
  name: string
  status: 'current' | 'stale' | 'unknown'
  localHash?: string
  upstreamHash?: string
}

export interface ErrorRecord {
  source: string
  name: string
  runId: string
  error: string
  errorType: string
  errorDetail: string
  attemptCount: number
  lastAttemptAt: string
}

export interface DiscoveryResult {
  source: string
  name: string
  type: ComponentType
  mechanical: MechanicalFields
  content?: string
}

export interface CatalogStats {
  total: number
  byType: Record<string, number>
  byAvailability: Record<string, number>
  analyzed: number
  withErrors: number
}
