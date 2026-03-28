/**
 * Toast notification system.
 *
 * Displays temporary messages in the bottom-right corner of the viewport.
 * Toasts auto-dismiss after a configurable duration and can be manually
 * dismissed by clicking.
 *
 * Listens to the `ui:toast` event bus event for programmatic toasts.
 */

import { bus } from '../state/events'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const DEFAULT_DURATION_MS = 4000
const TOAST_CONTAINER_ID = 'gv-toast-container'

// ---------------------------------------------------------------------------
// Toast container
// ---------------------------------------------------------------------------

function getOrCreateContainer(): HTMLElement {
  let container = document.getElementById(TOAST_CONTAINER_ID)
  if (!container) {
    container = document.createElement('div')
    container.id = TOAST_CONTAINER_ID
    container.className = 'gv-toast-container'
    document.body.appendChild(container)
  }
  return container
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Show a toast notification.
 *
 * @param message - The message to display.
 * @param type - Visual style: 'info', 'warn', or 'error'.
 * @param duration - Auto-dismiss after this many milliseconds. 0 = no auto-dismiss.
 */
export function showToast(
  message: string,
  type: 'info' | 'warn' | 'error' = 'info',
  duration: number = DEFAULT_DURATION_MS
): void {
  const container = getOrCreateContainer()

  const toast = document.createElement('div')
  toast.className = `gv-toast gv-toast--${type}`
  toast.textContent = message

  // Click to dismiss
  toast.addEventListener('click', () => {
    dismissToast(toast)
  })

  container.appendChild(toast)

  // Trigger entrance animation on next frame
  requestAnimationFrame(() => {
    toast.classList.add('gv-toast--visible')
  })

  // Auto-dismiss
  if (duration > 0) {
    setTimeout(() => {
      dismissToast(toast)
    }, duration)
  }
}

/**
 * Dismiss a toast with exit animation.
 */
function dismissToast(toast: HTMLElement): void {
  toast.classList.remove('gv-toast--visible')
  toast.classList.add('gv-toast--exiting')

  toast.addEventListener(
    'transitionend',
    () => {
      toast.remove()
    },
    { once: true }
  )

  // Fallback removal in case transitionend does not fire
  setTimeout(() => {
    if (toast.parentNode) {
      toast.remove()
    }
  }, 500)
}

// ---------------------------------------------------------------------------
// Event bus integration
// ---------------------------------------------------------------------------

/**
 * Initialize the toast system and connect it to the event bus.
 * Call this once during application startup.
 */
export function initToastSystem(): void {
  bus.on('ui:toast', ({ message, type, duration }) => {
    showToast(message, type, duration)
  })
}
