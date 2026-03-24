/**
 * Layout algorithm preset configurations.
 *
 * Each preset defines the parameters for a specific layout algorithm.
 * These are referenced by the layout manager when applying or switching
 * layouts.
 */

import type { CircularLayoutOptions } from 'graphology-layout/circular'
import type { RandomLayoutOptions } from 'graphology-layout/random'
import type { ForceAtlas2Settings } from 'graphology-layout-forceatlas2'

// ---------------------------------------------------------------------------
// Layout names (union type)
// ---------------------------------------------------------------------------

export type LayoutName = 'forceatlas2' | 'circular' | 'random'

export const LAYOUT_NAMES: readonly LayoutName[] = ['forceatlas2', 'circular', 'random'] as const

export const LAYOUT_LABELS: Record<LayoutName, string> = {
  forceatlas2: 'ForceAtlas2',
  circular: 'Circular',
  random: 'Random',
}

// ---------------------------------------------------------------------------
// ForceAtlas2 preset
// ---------------------------------------------------------------------------

export const FA2_SETTINGS: ForceAtlas2Settings = {
  linLogMode: false,
  outboundAttractionDistribution: true,
  adjustSizes: false,
  edgeWeightInfluence: 1,
  scalingRatio: 1,
  strongGravityMode: false,
  gravity: 1,
  slowDown: 10,
  barnesHutOptimize: false,
  barnesHutTheta: 0.5,
}

/** Auto-stop FA2 after this many milliseconds. */
export const FA2_AUTO_STOP_MS = 5000

// ---------------------------------------------------------------------------
// Circular preset
// ---------------------------------------------------------------------------

export const CIRCULAR_OPTIONS: CircularLayoutOptions = {
  scale: 500,
  center: 0,
}

// ---------------------------------------------------------------------------
// Random preset
// ---------------------------------------------------------------------------

export const RANDOM_OPTIONS: RandomLayoutOptions = {
  scale: 1000,
  center: 0,
}
