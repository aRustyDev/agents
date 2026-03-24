/**
 * Skill manifest builder for Tier 1 analysis.
 *
 * Builds pre-computed manifests from discovery results so the
 * Haiku agent receives ALL mechanical data and performs judgment-only.
 */

import type { CatalogEntryWithTier1, SectionMapEntry } from './catalog'
import type { DiscoveredSkillResult } from './catalog-discover'

// ---------------------------------------------------------------------------
// Manifest (input to agent)
// ---------------------------------------------------------------------------

/**
 * Pre-computed manifest for a single skill, sent to the Tier 1 agent.
 * Contains everything the agent needs — no tool use required.
 */
export interface SkillManifest {
  source: string
  skill: string
  /** Full SKILL.md content (inline, not a file path). */
  content: string
  /** Mechanical fields pre-computed by discovery. */
  wordCount: number
  sectionCount: number
  fileCount: number
  headingTree: Array<{ depth: number; title: string }>
  sectionMap: SectionMapEntry[]
  fileTree: string[]
  contentHash: string
  /** Mechanically extracted keywords (from headings + description + code fences). */
  mechanicalKeywords: string[]
  /** True if SKILL.md is the only file (no resources/subdirs). */
  isSimple: boolean
}

// ---------------------------------------------------------------------------
// Judgment (output from agent)
// ---------------------------------------------------------------------------

/**
 * Tier 1 judgment output from the Haiku agent.
 * These fields require LLM reasoning — they cannot be computed mechanically.
 */
export interface Tier1Judgment {
  source: string
  skill: string
  /** Structural complexity assessment. */
  complexity: 'simple' | 'moderate' | 'complex'
  /** Whether the skill uses progressive disclosure (details blocks, collapsible sections). */
  progressiveDisclosure: boolean
  /** Specific PD techniques found. */
  pdTechniques: string[]
  /** Best practices score (1-10) with specific violations. */
  bestPractices: { score: number; violations: string[] }
  /** Security review score (1-10) with specific concerns. */
  security: { score: number; concerns: string[] }
  /** Agent-refined keywords (improves/expands mechanical keywords). */
  refinedKeywords: string[]
}

// ---------------------------------------------------------------------------
// Manifest Builder
// ---------------------------------------------------------------------------

/**
 * Build a SkillManifest from a discovery result + SKILL.md content.
 *
 * The content parameter is required because discovery results don't
 * store the full SKILL.md text — only computed fields.
 */
export function buildManifest(disc: DiscoveredSkillResult, content: string): SkillManifest {
  return {
    source: disc.source,
    skill: disc.skill,
    content,
    wordCount: disc.mechanical.wordCount,
    sectionCount: disc.mechanical.sectionCount,
    fileCount: disc.mechanical.fileCount,
    headingTree: disc.mechanical.headingTree,
    sectionMap: disc.mechanical.sectionMap ?? [],
    fileTree: disc.mechanical.fileTree ?? [],
    contentHash: disc.mechanical.contentHash,
    mechanicalKeywords: disc.mechanical.keywords,
    isSimple: disc.mechanical.isSimple ?? true,
  }
}

/**
 * Build a SkillManifest from an existing catalog entry + content.
 * Used when discovery data is cached and we just need to build the manifest
 * for agent dispatch.
 */
export function buildManifestFromEntry(
  entry: CatalogEntryWithTier1,
  content: string
): SkillManifest {
  return {
    source: entry.source,
    skill: entry.skill,
    content,
    wordCount: entry.wordCount ?? 0,
    sectionCount: entry.sectionCount ?? 0,
    fileCount: entry.fileCount ?? 0,
    headingTree: entry.headingTree ?? [],
    sectionMap: entry.sectionMap ?? [],
    fileTree: entry.fileTree ?? [],
    contentHash: entry.contentHash ?? '',
    mechanicalKeywords: entry.keywords ?? [],
    isSimple: entry.isSimple ?? true,
  }
}

/**
 * Format a batch of manifests as a string for the agent prompt.
 * Each skill is a JSON block the agent can parse.
 */
export function formatManifestBatch(manifests: SkillManifest[]): string {
  return manifests
    .map((m) => {
      // Include content inline but cap at 50K chars to avoid token overflow
      const content =
        m.content.length > 50_000
          ? `${m.content.slice(0, 50_000)}\n\n[... truncated at 50K chars ...]`
          : m.content
      return JSON.stringify({
        source: m.source,
        skill: m.skill,
        content,
        wordCount: m.wordCount,
        sectionCount: m.sectionCount,
        fileCount: m.fileCount,
        headingTree: m.headingTree,
        mechanicalKeywords: m.mechanicalKeywords,
        isSimple: m.isSimple,
      })
    })
    .join('\n')
}
