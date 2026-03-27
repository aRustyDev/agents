;(() => {
  const MV = window.MatrixViewer
  MV.overlays = MV.overlays || {}

  let container = null

  // Engine category lookup tables
  const ENGINE_CATEGORIES = [
    {
      names: ['google', 'bing', 'duckduckgo', 'brave', 'searxng', 'marginalia'],
      category: 'general',
    },
    {
      names: [
        'scholar',
        'semantic scholar',
        'arxiv',
        'acl',
        'pubmed',
        'scopus',
        'medrxiv',
        'biorxiv',
        'paperswithcode',
      ],
      category: 'academic',
    },
    {
      names: ['npm', 'crates', 'pypi', 'docs.rs', 'godocs', 'hexdocs', 'pkg.go'],
      category: 'packages',
    },
    { names: ['github', 'gitlab', 'stackoverflow'], category: 'code' },
    {
      names: ['mdn', 'aws', 'apple', 'cloudflare', 'deepwiki', 'mkdocs', 'prisma', 'context7'],
      category: 'docs',
    },
    { names: ['fda', 'sec', 'eur-lex', 'eiopa', 'edgar'], category: 'regulatory' },
    { names: ['tavily', 'perplexity', 'serper', 'exa', 'jina', 'firecrawl'], category: 'paid' },
  ]

  function categorizeEngine(engine) {
    const lower = (engine || '').toLowerCase()
    for (const group of ENGINE_CATEGORIES) {
      if (group.names.some((e) => lower.includes(e))) return group.category
    }
    return 'other'
  }

  function checkLargeTier1(tier1) {
    if (tier1 && tier1.rows.length > 5) {
      return {
        severity: 'warning',
        title: 'Large Tier 1',
        body: `This matrix has ${tier1.rows.length} Tier 1 rows (recommended max: 5). Consider splitting into focused sub-questions with separate matrices.`,
      }
    }
    return null
  }

  function checkEngineCategories(matrix) {
    const allEngines = new Set()
    for (const tier of matrix.tiers) {
      for (const row of tier.rows) {
        for (const e of row.engines) allEngines.add(categorizeEngine(e))
      }
    }
    if (allEngines.size >= 3) {
      return {
        severity: 'info',
        title: 'Multiple engine categories',
        body: `This matrix spans ${allEngines.size} engine categories (${[...allEngines].join(', ')}). If they serve different sub-questions, consider decomposing by domain.`,
      }
    }
    return null
  }

  function checkMixedDomain(matrix) {
    if (!matrix.context) return null
    const domain = (matrix.context.domain || '').toLowerCase()
    if (domain.includes('+') || domain.includes('mixed') || domain.includes(',')) {
      return {
        severity: 'warning',
        title: 'Mixed domain',
        body: `Domain is "${matrix.context.domain}". Multi-domain research typically benefits from separate matrices per domain, each with domain-appropriate engines.`,
      }
    }
    return null
  }

  function checkIndependentQueries(tier1) {
    if (!tier1 || tier1.rows.length < 3) return null
    const engineSets = tier1.rows.map((r) => new Set(r.engines))
    let independentPairs = 0
    for (let i = 0; i < engineSets.length; i++) {
      for (let j = i + 1; j < engineSets.length; j++) {
        const overlap = [...engineSets[i]].filter((e) => engineSets[j].has(e))
        if (overlap.length === 0) independentPairs++
      }
    }
    if (independentPairs > tier1.rows.length / 2) {
      return {
        severity: 'info',
        title: 'Potentially independent queries',
        body: `${independentPairs} pairs of Tier 1 rows share no engines. These may be independent sub-questions that could be researched in parallel with separate matrices.`,
      }
    }
    return null
  }

  function activate() {
    const state = MV.getState()
    const evalCase = state.data.evals[state.currentEvalIndex]
    if (!evalCase) return

    const raw = evalCase.configurations.with_skill.raw
    const matrix = MV.parseMatrix ? MV.parseMatrix(raw) : null
    if (!matrix) return

    const tier1 = matrix.tiers.find((t) => t.level === 1)
    const checks = [
      checkLargeTier1(tier1),
      checkEngineCategories(matrix),
      checkMixedDomain(matrix),
      checkIndependentQueries(tier1),
    ]

    const suggestions = checks.filter(Boolean)

    if (suggestions.length === 0) {
      suggestions.push({
        severity: 'info',
        title: 'No decomposition issues detected',
        body: 'This matrix appears well-scoped for a single research question.',
      })
    }

    container = document.createElement('div')
    container.className = 'decomp-suggestions'

    for (const s of suggestions) {
      const card = document.createElement('div')
      card.className = `decomp-card ${s.severity}`
      card.innerHTML = `<div class="decomp-card-title">${escapeHtml(s.title)}</div><div class="decomp-card-body">${escapeHtml(s.body)}</div>`
      container.appendChild(card)
    }

    const content = document.getElementById('matrix-content')
    if (content) content.appendChild(container)
  }

  function deactivate() {
    if (container) {
      container.remove()
      container = null
    }
  }

  function escapeHtml(text) {
    return (text || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  }

  MV.overlays.decomposition = { activate, deactivate }
})()
