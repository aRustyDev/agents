;(() => {
  const MV = window.MatrixViewer
  MV.overlays = MV.overlays || {}

  const sectionKeywords = {
    context: ['context'],
    tier1: ['tier 1', 'tier1'],
    tier2: ['tier 2', 'tier2'],
    tier3: ['tier 3', 'tier3'],
    recovery: ['recovery', 'runtime recovery'],
    grading: ['grading', 'grading summary'],
  }

  function passOrFail(passed) {
    return passed ? 'pass' : 'fail'
  }

  function matchesKeywords(text, keywords) {
    const lower = text.toLowerCase()
    return keywords.some((kw) => lower.includes(kw))
  }

  function isStructuralAssertion(exp, structuralAssertions) {
    return structuralAssertions.some((a) => a.text === exp.text)
  }

  function findBadge(sectionId, grading, assertions) {
    const keywords = sectionKeywords[sectionId] || [sectionId]
    const structural = assertions.filter((a) => a.type === 'structural')

    if (!grading?.expectations) return 'unknown'

    let fallback = 'unknown'
    for (const exp of grading.expectations) {
      if (!matchesKeywords(exp.text, keywords)) continue
      if (isStructuralAssertion(exp, structural)) return passOrFail(exp.passed)
      if (fallback === 'unknown') fallback = passOrFail(exp.passed)
    }
    return fallback
  }

  function createBadgeEl(badge) {
    const badgeEl = document.createElement('span')
    badgeEl.className = `structural-badge ${badge}`
    badgeEl.textContent = badge === 'pass' ? '\u2713' : badge === 'fail' ? '\u2717' : '?'
    badgeEl.title = badge === 'pass' ? 'Passed' : badge === 'fail' ? 'Failed' : 'No assertion'
    return badgeEl
  }

  function activate() {
    const state = MV.getState()
    const evalCase = state.data.evals[state.currentEvalIndex]
    if (!evalCase) return

    const grading = evalCase.configurations.with_skill.grading
    const assertions = evalCase.assertions || []
    const sections = ['context', 'tier1', 'tier2', 'tier3', 'recovery', 'grading']

    for (const sectionId of sections) {
      const el = document.querySelector(`[data-section="${sectionId}"]`)
      if (!el) continue

      const badge = findBadge(sectionId, grading, assertions)
      el.appendChild(createBadgeEl(badge))
    }
  }

  function deactivate() {
    document.querySelectorAll('.structural-badge').forEach((el) => el.remove())
  }

  MV.overlays.structural = { activate, deactivate }
})()
