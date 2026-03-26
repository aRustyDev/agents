/**
 * GitHub search query builders for discovering Claude Code components.
 *
 * Constructs GitHub search API queries to find repositories containing
 * SKILL.md files and repositories tagged with `claude-code` topics.
 */

/** Build a GitHub code search query for SKILL.md files. */
export function buildSkillSearchQuery(query: string): string {
  const parts = ['filename:SKILL.md']
  if (query) {
    parts.push(query)
  }
  return parts.join(' ')
}

/** Build a GitHub repository search query for claude-code topics. */
export function buildTopicSearchQuery(query: string, topic = 'claude-code'): string {
  const parts = [`topic:${topic}`]
  if (query) {
    parts.push(query)
  }
  return parts.join(' ')
}

/** Build a combined search query that looks for skill repositories. */
export function buildComponentSearchQuery(
  query: string,
  opts?: { language?: string; topic?: string }
): string {
  const parts: string[] = []
  if (query) parts.push(query)
  if (opts?.topic) parts.push(`topic:${opts.topic}`)
  if (opts?.language) parts.push(`language:${opts.language}`)
  return parts.join(' ')
}
