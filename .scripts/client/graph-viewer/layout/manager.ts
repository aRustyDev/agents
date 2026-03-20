/**
 * Layout algorithm manager.
 *
 * Provides a unified interface to switch between layout algorithms:
 * - ForceAtlas2 (worker-based, continuous)
 * - Circular (synchronous, one-shot)
 * - Random (synchronous, one-shot)
 *
 * ForceAtlas2 runs in a web worker via graphology-layout-forceatlas2/worker
 * and can be started/stopped. Circular and random are applied immediately.
 */

import type Graph from 'graphology'
import circular from 'graphology-layout/circular'
import random from 'graphology-layout/random'
import FA2Layout from 'graphology-layout-forceatlas2/worker'
import { bus } from '../state/events'
import { store } from '../state/store'
import {
  CIRCULAR_OPTIONS,
  FA2_AUTO_STOP_MS,
  FA2_SETTINGS,
  type LayoutName,
  RANDOM_OPTIONS,
} from './presets'

// ---------------------------------------------------------------------------
// Layout Manager
// ---------------------------------------------------------------------------

export class LayoutManager {
  private graph: Graph
  private fa2Layout: FA2Layout | null = null
  private fa2Timer: ReturnType<typeof setTimeout> | null = null
  private currentLayout: LayoutName = 'forceatlas2'

  constructor(graph: Graph) {
    this.graph = graph
  }

  /**
   * Swap the graph that this manager operates on.
   *
   * Kills any running FA2 worker so the next `apply()` creates a fresh
   * worker bound to the new graph.
   */
  setGraph(graph: Graph): void {
    this.stopFA2()
    if (this.fa2Layout) {
      this.fa2Layout.kill()
      this.fa2Layout = null
    }
    this.graph = graph
  }

  /**
   * Get the currently active layout name.
   */
  getCurrent(): LayoutName {
    return this.currentLayout
  }

  /**
   * Check whether the ForceAtlas2 layout is currently running.
   */
  isRunning(): boolean {
    return this.fa2Layout?.isRunning() ?? false
  }

  /**
   * Apply a layout algorithm to the graph.
   *
   * For ForceAtlas2, this starts the worker-based continuous layout.
   * For circular and random, the layout is applied synchronously and
   * the graph is updated immediately.
   */
  apply(algorithm: LayoutName): void {
    // Stop any running FA2 before switching
    this.stopFA2()

    this.currentLayout = algorithm
    store.set('activeLayout', algorithm)

    switch (algorithm) {
      case 'forceatlas2':
        this.startFA2()
        break

      case 'circular':
        circular.assign(this.graph, CIRCULAR_OPTIONS)
        bus.emit('layout:changed', { algorithm: 'circular' })
        break

      case 'random':
        random.assign(this.graph, RANDOM_OPTIONS)
        bus.emit('layout:changed', { algorithm: 'random' })
        break
    }
  }

  /**
   * Start the ForceAtlas2 layout worker.
   */
  startFA2(): void {
    if (this.fa2Layout?.isRunning()) return

    // Create a new FA2 worker layout if needed
    if (!this.fa2Layout) {
      this.fa2Layout = new FA2Layout(this.graph, {
        settings: FA2_SETTINGS,
      })
    }

    this.fa2Layout.start()
    store.set('layoutRunning', true)
    bus.emit('layout:started', { algorithm: 'forceatlas2' })

    // Auto-stop after convergence timeout to prevent perpetual shaking
    if (this.fa2Timer) clearTimeout(this.fa2Timer)
    this.fa2Timer = setTimeout(() => {
      this.stopFA2()
    }, FA2_AUTO_STOP_MS)
  }

  /**
   * Stop the ForceAtlas2 layout worker.
   */
  stopFA2(): void {
    if (this.fa2Timer) {
      clearTimeout(this.fa2Timer)
      this.fa2Timer = null
    }
    if (this.fa2Layout?.isRunning()) {
      this.fa2Layout.stop()
      store.set('layoutRunning', false)
      bus.emit('layout:stopped', { algorithm: 'forceatlas2' })
    }
  }

  /**
   * Toggle ForceAtlas2 on/off.
   */
  toggleFA2(): void {
    if (this.fa2Layout?.isRunning()) {
      this.stopFA2()
    } else {
      this.currentLayout = 'forceatlas2'
      store.set('activeLayout', 'forceatlas2')
      this.startFA2()
    }
  }

  /**
   * Kill the FA2 worker and release resources.
   * Call this when the graph viewer is being torn down.
   */
  destroy(): void {
    if (this.fa2Layout) {
      this.fa2Layout.kill()
      this.fa2Layout = null
      store.set('layoutRunning', false)
    }
  }
}
