import { describe, expect, it } from 'bun:test'
import { GitHubProvider } from '../../src/providers/github'
import {
  buildComponentSearchQuery,
  buildSkillSearchQuery,
  buildTopicSearchQuery,
} from '../../src/providers/github/search'

describe('GitHubProvider', () => {
  const provider = new GitHubProvider()

  describe('capabilities', () => {
    it('has search capability for skill type', () => {
      expect(provider.capabilities.search).toEqual(['skill'])
    })

    it('has no add/remove/list/info/publish capabilities', () => {
      expect(provider.capabilities.add).toEqual([])
      expect(provider.capabilities.remove).toEqual([])
      expect(provider.capabilities.list).toEqual([])
      expect(provider.capabilities.info).toEqual([])
      expect(provider.capabilities.publish).toEqual([])
    })
  })

  describe('unsupported operations', () => {
    it('add returns error', async () => {
      const result = await provider.add('source', {})
      expect(result.ok).toBe(false)
    })

    it('remove returns error', async () => {
      const result = await provider.remove('name', 'skill')
      expect(result.ok).toBe(false)
    })

    it('info returns error', async () => {
      const result = await provider.info('name', 'skill')
      expect(result.ok).toBe(false)
    })

    it('publish returns error', async () => {
      const result = await provider.publish('skill', {})
      expect(result.ok).toBe(false)
    })

    it('list returns empty array', async () => {
      const result = await provider.list('skill')
      expect(result.ok).toBe(true)
      if (result.ok) {
        expect(result.value).toEqual([])
      }
    })
  })

  describe('search type filtering', () => {
    it('returns empty page for non-skill types', async () => {
      const result = await provider.search({ query: 'test', type: 'agent' })
      expect(result.ok).toBe(true)
      if (result.ok) {
        expect(result.value.items).toEqual([])
      }
    })
  })
})

describe('GitHub search query builders', () => {
  describe('buildSkillSearchQuery', () => {
    it('includes SKILL.md filename', () => {
      const query = buildSkillSearchQuery('')
      expect(query).toContain('filename:SKILL.md')
    })

    it('appends user query', () => {
      const query = buildSkillSearchQuery('kubernetes')
      expect(query).toContain('filename:SKILL.md')
      expect(query).toContain('kubernetes')
    })
  })

  describe('buildTopicSearchQuery', () => {
    it('uses default claude-code topic', () => {
      const query = buildTopicSearchQuery('')
      expect(query).toContain('topic:claude-code')
    })

    it('uses custom topic', () => {
      const query = buildTopicSearchQuery('', 'mcp-server')
      expect(query).toContain('topic:mcp-server')
    })

    it('appends user query', () => {
      const query = buildTopicSearchQuery('deploy')
      expect(query).toContain('deploy')
    })
  })

  describe('buildComponentSearchQuery', () => {
    it('builds query with topic and language', () => {
      const query = buildComponentSearchQuery('test', { topic: 'mcp', language: 'typescript' })
      expect(query).toContain('test')
      expect(query).toContain('topic:mcp')
      expect(query).toContain('language:typescript')
    })

    it('handles empty options', () => {
      const query = buildComponentSearchQuery('search')
      expect(query).toBe('search')
    })
  })
})
