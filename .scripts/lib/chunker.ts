/**
 * Markdown chunking module.
 *
 * Splits markdown content into hierarchical chunks:
 * - file: Entire file content
 * - section: Content under ## headings
 * - paragraph: Individual paragraphs within sections
 *
 * Port of .scripts/lib/chunker.py -- the algorithm is identical
 * so that both implementations produce the same chunks for the same input.
 */

import yaml from 'js-yaml'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Chunk {
  level: 'file' | 'section' | 'paragraph'
  index: number
  text: string
  heading?: string
  startLine?: number
  endLine?: number
  parentIndex?: number
}

export interface ParsedMarkdown {
  frontmatter: Record<string, unknown>
  content: string
  chunks: Chunk[]
}

interface Section {
  heading: string | null
  content: string
  startLine: number
  endLine: number
}

// ---------------------------------------------------------------------------
// parseFrontmatter
// ---------------------------------------------------------------------------

/**
 * Extract YAML frontmatter from markdown content.
 *
 * Looks for content between opening and closing `---` delimiters at the
 * start of the file. Uses `js-yaml` for parsing the YAML block.
 *
 * @returns Object with `meta` (parsed YAML or empty object) and `body`
 *          (remaining content after frontmatter, trimmed).
 */
export function parseFrontmatter(content: string): {
  meta: Record<string, unknown>
  body: string
} {
  if (!content.startsWith('---')) {
    return { meta: {}, body: content }
  }

  // Find closing ---
  const lines = content.split('\n')
  let endIdx: number | null = null
  for (let i = 1; i < lines.length; i++) {
    if (lines[i]!.trim() === '---') {
      endIdx = i
      break
    }
  }

  if (endIdx === null) {
    return { meta: {}, body: content }
  }

  const frontmatterText = lines.slice(1, endIdx).join('\n')
  const remaining = lines.slice(endIdx + 1).join('\n')

  let meta: Record<string, unknown>
  try {
    const parsed = yaml.load(frontmatterText)
    meta = (parsed as Record<string, unknown>) ?? {}
  } catch {
    meta = {}
  }

  return { meta, body: remaining.trim() }
}

// ---------------------------------------------------------------------------
// splitIntoSections
// ---------------------------------------------------------------------------

const HEADING_PATTERN = /^##\s+(.+)$/

/**
 * Split content by `## ` headings (H2).
 *
 * Content before the first heading is returned as a section with
 * `heading: null`. Only sections with non-empty trimmed content are included.
 * Line numbers are tracked relative to the input string.
 *
 * @returns Array of section objects with heading, content, startLine, endLine.
 */
export function splitIntoSections(content: string): Section[] {
  const lines = content.split('\n')
  const sections: Section[] = []
  let currentHeading: string | null = null
  let currentLines: string[] = []
  let currentStart = 0

  for (let i = 0; i < lines.length; i++) {
    const match = HEADING_PATTERN.exec(lines[i]!)
    if (match) {
      // Save previous section if it has content
      if (currentLines.length > 0) {
        const sectionText = currentLines.join('\n').trim()
        if (sectionText) {
          sections.push({
            heading: currentHeading,
            content: sectionText,
            startLine: currentStart,
            endLine: i - 1,
          })
        }
      }
      // Start new section
      currentHeading = match[1]!.trim()
      currentLines = []
      currentStart = i
    } else {
      currentLines.push(lines[i]!)
    }
  }

  // Don't forget last section
  if (currentLines.length > 0) {
    const sectionText = currentLines.join('\n').trim()
    if (sectionText) {
      sections.push({
        heading: currentHeading,
        content: sectionText,
        startLine: currentStart,
        endLine: lines.length - 1,
      })
    }
  }

  return sections
}

// ---------------------------------------------------------------------------
// splitIntoParagraphs
// ---------------------------------------------------------------------------

/**
 * Split content into paragraphs.
 *
 * Splits on double newlines (paragraph breaks, matching `\n\s*\n`).
 * Skips paragraphs that start with triple backticks (code blocks) and
 * paragraphs shorter than `minLength`.
 *
 * @param content - Text content to split
 * @param minLength - Minimum paragraph length to include (default: 50)
 * @returns Array of paragraph strings
 */
export function splitIntoParagraphs(content: string, minLength = 50): string[] {
  // Split on double newlines (paragraph breaks)
  const paragraphs = content.split(/\n\s*\n/)

  // Filter and clean
  const result: string[] = []
  for (const raw of paragraphs) {
    const para = raw.trim()
    // Skip code blocks (start with ```)
    if (para.startsWith('```')) {
      continue
    }
    // Skip very short paragraphs
    if (para.length < minLength) {
      continue
    }
    result.push(para)
  }

  return result
}

// ---------------------------------------------------------------------------
// chunkMarkdown
// ---------------------------------------------------------------------------

export interface ChunkOptions {
  /** Whether to create paragraph-level chunks. Defaults to true. */
  includeParagraphs?: boolean
}

/**
 * Parse and chunk markdown content into a 3-level hierarchy.
 *
 * 1. Level 'file': entire body content as one chunk (index 0)
 * 2. Level 'section': one chunk per H2 section (parentIndex: 0)
 * 3. Level 'paragraph': one chunk per paragraph within each section
 *    (parentIndex: the section chunk's index in the chunks array),
 *    only if `includeParagraphs` is true (default: true)
 *
 * @param content - Raw markdown content (may include frontmatter)
 * @param opts - Chunking options
 * @returns ParsedMarkdown with frontmatter, body content, and chunks
 */
export function chunkMarkdown(
  content: string,
  opts?: ChunkOptions,
): ParsedMarkdown {
  const includeParagraphs = opts?.includeParagraphs ?? true

  const result: ParsedMarkdown = {
    frontmatter: {},
    content: '',
    chunks: [],
  }

  // Extract frontmatter
  const { meta, body } = parseFrontmatter(content)
  result.frontmatter = meta
  result.content = body

  const chunks: Chunk[] = []

  // Level 0: Whole file
  const fileChunk: Chunk = {
    level: 'file',
    index: 0,
    text: body,
    startLine: 0,
    endLine: body.split('\n').length - 1,
  }
  chunks.push(fileChunk)

  // Level 1: Sections
  const sections = splitIntoSections(body)
  for (let sectionIdx = 0; sectionIdx < sections.length; sectionIdx++) {
    const section = sections[sectionIdx]!
    const sectionChunk: Chunk = {
      level: 'section',
      index: sectionIdx,
      text: section.content,
      heading: section.heading ?? undefined,
      startLine: section.startLine,
      endLine: section.endLine,
      parentIndex: 0, // Parent is file chunk
    }
    chunks.push(sectionChunk)

    // Level 2: Paragraphs within section
    if (includeParagraphs) {
      const paragraphs = splitIntoParagraphs(section.content)
      for (let paraIdx = 0; paraIdx < paragraphs.length; paraIdx++) {
        const paraChunk: Chunk = {
          level: 'paragraph',
          index: paraIdx,
          text: paragraphs[paraIdx]!,
          parentIndex: chunks.length - 1, // Parent is section chunk
        }
        chunks.push(paraChunk)
      }
    }
  }

  result.chunks = chunks
  return result
}

// ---------------------------------------------------------------------------
// chunkFile
// ---------------------------------------------------------------------------

/**
 * Chunk a markdown file.
 *
 * Reads the file using `Bun.file().text()` and delegates to `chunkMarkdown`.
 *
 * @param path - Path to the markdown file
 * @param opts - Chunking options
 * @returns ParsedMarkdown with frontmatter, body content, and chunks
 */
export async function chunkFile(
  path: string,
  opts?: ChunkOptions,
): Promise<ParsedMarkdown> {
  const content = await Bun.file(path).text()
  return chunkMarkdown(content, opts)
}
