/**
 * Undo/Redo manager using the Command pattern.
 *
 * Each CRUD operation pushes a Command onto the undo stack. Commands
 * know how to reverse themselves (undo) and re-apply (redo).
 *
 * The manager is a singleton imported wherever undo support is needed.
 */

// ---------------------------------------------------------------------------
// Command interface
// ---------------------------------------------------------------------------

export interface Command {
  /** Re-execute the operation (for redo). The initial execute is done externally. */
  execute(): void
  /** Reverse the operation. */
  undo(): void
  /** Human-readable description for debugging/UI. */
  description: string
}

// ---------------------------------------------------------------------------
// UndoManager
// ---------------------------------------------------------------------------

class UndoManager {
  private undoStack: Command[] = []
  private redoStack: Command[] = []
  private maxSize = 50

  /**
   * Push an already-executed command onto the undo stack.
   * Clears the redo stack since the history has diverged.
   */
  push(cmd: Command): void {
    this.undoStack.push(cmd)

    // Trim if over capacity
    if (this.undoStack.length > this.maxSize) {
      this.undoStack.shift()
    }

    // Any new command invalidates the redo history
    this.redoStack.length = 0
  }

  /**
   * Undo the most recent command.
   *
   * @returns `true` if an undo was performed, `false` if the stack was empty.
   */
  undo(): boolean {
    const cmd = this.undoStack.pop()
    if (!cmd) return false

    cmd.undo()
    this.redoStack.push(cmd)
    return true
  }

  /**
   * Redo the most recently undone command.
   *
   * @returns `true` if a redo was performed, `false` if the stack was empty.
   */
  redo(): boolean {
    const cmd = this.redoStack.pop()
    if (!cmd) return false

    cmd.execute()
    this.undoStack.push(cmd)
    return true
  }

  /**
   * Clear both stacks. Call this when the graph is reloaded.
   */
  clear(): void {
    this.undoStack.length = 0
    this.redoStack.length = 0
  }

  canUndo(): boolean {
    return this.undoStack.length > 0
  }

  canRedo(): boolean {
    return this.redoStack.length > 0
  }
}

// ---------------------------------------------------------------------------
// Singleton
// ---------------------------------------------------------------------------

export const undoManager = new UndoManager()
