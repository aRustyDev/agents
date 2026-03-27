/**
 * Mechanical computation functions for catalog entries.
 *
 * All functions are pure — no I/O except filesystem reads for
 * directory scanning. No LLM involvement.
 */

import { join } from 'node:path'
import type { SectionMapEntry } from './types'

// ---------------------------------------------------------------------------
// Content Hash
// ---------------------------------------------------------------------------

/**
 * Compute SHA-256 content hash of a string.
 * Returns `sha256:<hex>` format.
 */
export function computeContentHash(content: string): string {
  const { createSha256Hasher } =
    require('@agents/core/runtime') as typeof import('@agents/core/runtime')
  const hasher = createSha256Hasher()
  hasher.update(content)
  return `sha256:${hasher.digest('hex')}`
}

// ---------------------------------------------------------------------------
// Word / Section / Line Counting
// ---------------------------------------------------------------------------

/**
 * Count words in content by splitting on whitespace.
 */
export function computeWordCount(content: string): number {
  const trimmed = content.trim()
  if (!trimmed) return 0
  return trimmed.split(/\s+/).length
}

/**
 * Count markdown sections (lines starting with # through ######).
 */
export function computeSectionCount(content: string): number {
  let count = 0
  for (const line of content.split('\n')) {
    if (/^#{1,6}\s/.test(line)) count++
  }
  return count
}

/**
 * Count lines in content.
 */
export function computeLineCount(content: string): number {
  if (!content) return 0
  return content.split('\n').length
}

// ---------------------------------------------------------------------------
// Heading Tree
// ---------------------------------------------------------------------------

/**
 * Extract heading tree from markdown content.
 * Returns array of {depth, title} for each heading.
 */
export function computeHeadingTree(content: string): Array<{ depth: number; title: string }> {
  const tree: Array<{ depth: number; title: string }> = []
  for (const line of content.split('\n')) {
    const match = line.match(/^(#{1,6})\s+(.+)$/)
    if (match) {
      tree.push({ depth: match[1].length, title: match[2].trim() })
    }
  }
  return tree
}

// ---------------------------------------------------------------------------
// Section Map
// ---------------------------------------------------------------------------

/**
 * Compute a section map: heading text + line number for navigation.
 */
export function computeSectionMap(content: string): SectionMapEntry[] {
  const entries: SectionMapEntry[] = []
  const lines = content.split('\n')
  for (let i = 0; i < lines.length; i++) {
    const match = lines[i].match(/^(#{1,6})\s+(.+)$/)
    if (match) {
      entries.push({ heading: match[2].trim(), line: i + 1, depth: match[1].length })
    }
  }
  return entries
}

// ---------------------------------------------------------------------------
// File System Analysis
// ---------------------------------------------------------------------------

/**
 * Count files recursively in a directory.
 * Returns 0 for nonexistent directories.
 */
export function computeFileCount(dir: string): number {
  const { readdirSync } = require('node:fs')
  try {
    let count = 0
    const entries = readdirSync(dir, { withFileTypes: true })
    for (const entry of entries) {
      if (entry.isFile()) {
        count++
      } else if (entry.isDirectory()) {
        count += computeFileCount(join(dir, entry.name))
      }
    }
    return count
  } catch {
    return 0
  }
}

/**
 * List all files in a directory recursively (relative paths).
 * Returns empty array for nonexistent directories.
 */
export function computeFileTree(dir: string): string[] {
  const { readdirSync, statSync } = require('node:fs') as typeof import('node:fs')
  const { relative } = require('node:path') as typeof import('node:path')
  const files: string[] = []
  try {
    function walk(current: string): void {
      for (const entry of readdirSync(current, { withFileTypes: true })) {
        const full = join(current, entry.name)
        if (entry.isFile()) {
          files.push(relative(dir, full))
        } else if (entry.isDirectory() && entry.name !== '.git' && entry.name !== 'node_modules') {
          walk(full)
        }
      }
    }
    walk(dir)
  } catch {
    /* nonexistent dir */
  }
  return files.sort()
}

/**
 * Compute total size of a directory in bytes.
 * Returns 0 for nonexistent directories.
 */
export function computeSkillSizeBytes(dir: string): number {
  const { statSync, readdirSync } = require('node:fs') as typeof import('node:fs')
  try {
    let total = 0
    function walk(current: string): void {
      for (const entry of readdirSync(current, { withFileTypes: true })) {
        const full = join(current, entry.name)
        if (entry.isFile()) {
          total += statSync(full).size
        } else if (entry.isDirectory() && entry.name !== '.git') {
          walk(full)
        }
      }
    }
    walk(dir)
    return total
  } catch {
    return 0
  }
}

/**
 * Check if a skill is "simple" — directory contains only SKILL.md.
 * No resources, no subdirectories, no additional files.
 */
export function isSimpleSkill(dir: string): boolean {
  const { readdirSync } = require('node:fs') as typeof import('node:fs')
  try {
    const entries = readdirSync(dir, { withFileTypes: true })
    return entries.length === 1 && entries[0].isFile() && entries[0].name === 'SKILL.md'
  } catch {
    return false
  }
}

// ---------------------------------------------------------------------------
// Keyword Extraction (Mechanical)
// ---------------------------------------------------------------------------

const STOP_WORDS = new Set([
  'a',
  'an',
  'the',
  'and',
  'or',
  'but',
  'in',
  'on',
  'at',
  'to',
  'for',
  'of',
  'with',
  'by',
  'from',
  'is',
  'are',
  'was',
  'were',
  'be',
  'been',
  'being',
  'have',
  'has',
  'had',
  'do',
  'does',
  'did',
  'will',
  'would',
  'could',
  'should',
  'may',
  'might',
  'shall',
  'can',
  'not',
  'no',
  'nor',
  'so',
  'if',
  'then',
  'than',
  'that',
  'this',
  'these',
  'those',
  'it',
  'its',
  'as',
  'up',
  'out',
  'about',
  'into',
  'over',
  'after',
  'before',
  'between',
  'under',
  'above',
  'such',
  'each',
  'every',
  'all',
  'any',
  'both',
  'few',
  'more',
  'most',
  'other',
  'some',
  'only',
  'own',
  'same',
  'how',
  'what',
  'when',
  'where',
  'which',
  'who',
  'whom',
  'why',
  'use',
  'using',
  'used',
  'also',
  'just',
  'like',
  'make',
  'get',
])

/**
 * Extract keywords mechanically from markdown content.
 *
 * Sources (in priority order):
 * 1. Heading titles (h1-h3) — split into individual terms
 * 2. Frontmatter description — significant terms
 * 3. Code fence language identifiers (e.g., typescript, python, rust)
 *
 * Filters stop words, deduplicates, lowercases.
 */
export function extractKeywords(content: string): string[] {
  const terms = new Set<string>()

  // 1. Headings (h1-h3 only — deeper headings are too specific)
  for (const line of content.split('\n')) {
    const match = line.match(/^#{1,3}\s+(.+)$/)
    if (match) {
      for (const word of tokenize(match[1])) {
        terms.add(word)
      }
    }
  }

  // 2. Frontmatter description
  const descMatch = content.match(/^---[\s\S]*?description:\s*(.+?)$/m)
  if (descMatch) {
    for (const word of tokenize(descMatch[1])) {
      terms.add(word)
    }
  }

  // 3. Code fence languages
  for (const match of content.matchAll(/^```(\w+)/gm)) {
    const lang = match[1].toLowerCase()
    if (lang !== 'text' && lang !== 'markdown' && lang !== 'md' && lang !== 'plaintext') {
      terms.add(lang)
    }
  }

  return [...terms].slice(0, 30) // cap at 30 keywords
}

/** Tokenize a string into lowercase terms, filtering stop words and short tokens. */
function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, ' ')
    .split(/\s+/)
    .filter((w) => w.length > 2 && !STOP_WORDS.has(w))
}
