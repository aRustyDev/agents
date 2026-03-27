import { load as yamlLoad } from 'js-yaml'

export function parseFrontmatter(content: string): {
  attrs: Record<string, unknown>
  body: string
} {
  const match = content.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/)
  if (!match) return { attrs: {}, body: content }
  try {
    return { attrs: (yamlLoad(match[1]) as Record<string, unknown>) ?? {}, body: match[2] ?? '' }
  } catch {
    return { attrs: {}, body: content }
  }
}

/** Chunker-compatible frontmatter parser (returns { meta, body } shape). */
export function parseMarkdownFrontmatter(raw: string): {
  meta: Record<string, unknown>
  body: string
} {
  const { attrs, body } = parseFrontmatter(raw)
  return { meta: attrs, body }
}

export function computeBasicMetadata(content: string, body: string) {
  const lines = content.split('\n')
  const headings = lines
    .filter((l) => l.startsWith('#'))
    .map((l) => {
      const m = l.match(/^(#{1,6})\s+(.*)/)
      return m ? { depth: (m[1] ?? '').length, title: (m[2] ?? '').trim() } : null
    })
    .filter(Boolean) as Array<{ depth: number; title: string }>
  return {
    wordCount: body.split(/\s+/).filter(Boolean).length,
    sectionCount: headings.length,
    headingTree: headings,
    lineCount: lines.length,
  }
}
