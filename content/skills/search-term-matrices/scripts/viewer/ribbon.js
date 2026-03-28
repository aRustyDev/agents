;(() => {
  const MV = window.MatrixViewer

  const activeOverlays = new Set()

  MV.initRibbon = () => {
    const ribbon = document.getElementById('overlay-ribbon')
    if (!ribbon) return
    ribbon.classList.remove('hidden')

    ribbon.querySelectorAll('.overlay-toggle').forEach((btn) => {
      btn.addEventListener('click', () => {
        const overlay = btn.dataset.overlay
        if (activeOverlays.has(overlay)) {
          activeOverlays.delete(overlay)
          btn.classList.remove('active')
          MV.deactivateOverlay(overlay)
        } else {
          activeOverlays.add(overlay)
          btn.classList.add('active')
          MV.activateOverlay(overlay)
        }
      })
    })
  }

  MV.activateOverlay = (name) => {
    const fn = MV.overlays?.[name]
    if (fn?.activate) fn.activate()
  }

  MV.deactivateOverlay = (name) => {
    const fn = MV.overlays?.[name]
    if (fn?.deactivate) fn.deactivate()
  }

  MV.getActiveOverlays = () => activeOverlays

  // Registry for overlay modules
  MV.overlays = MV.overlays || {}
})()
