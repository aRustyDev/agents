import { type CancelSymbol, cancelSymbol } from './index'

export interface SelectItem<T> {
  label: string
  value: T
  locked?: boolean
}

export interface SearchMultiselectOptions<T> {
  message: string
  items: SelectItem<T>[]
  initial?: T[]
  pageSize?: number
  yes?: boolean
}

export async function searchMultiselect<T>(
  opts: SearchMultiselectOptions<T>
): Promise<T[] | CancelSymbol> {
  const lockedValues = opts.items.filter((i) => i.locked).map((i) => i.value)
  const initialValues = [...lockedValues, ...(opts.initial ?? [])]

  // Non-interactive mode
  if (opts.yes || !process.stdin.isTTY) {
    return initialValues
  }

  // Full interactive implementation
  return new Promise((resolve) => {
    const stdin = process.stdin
    if (!stdin.setRawMode) {
      resolve(initialValues)
      return
    }

    stdin.setRawMode(true)
    stdin.resume()

    let filterText = ''
    const selected = new Set(initialValues)
    let cursorIndex = 0
    let debounceTimer: ReturnType<typeof setTimeout> | null = null
    let lastRenderedLines = 0

    const filtered = () =>
      opts.items.filter((item) => item.label.toLowerCase().includes(filterText.toLowerCase()))

    const clearRendered = () => {
      // Move up and clear each previously rendered line
      for (let i = 0; i < lastRenderedLines; i++) {
        process.stdout.write('\x1B[A\x1B[2K')
      }
      process.stdout.write('\r')
    }

    const render = () => {
      if (lastRenderedLines > 0) clearRendered()

      const items = filtered()
      const pageSize = opts.pageSize ?? 10
      const visibleCount = Math.min(items.length, pageSize)
      let lines = 0

      // Header line
      process.stdout.write(`\x1B[2K\r${opts.message} > ${filterText}\n`)
      lines++

      for (let i = 0; i < visibleCount; i++) {
        // biome-ignore lint/style/noNonNullAssertion: index bounded by visibleCount which is min(items.length, pageSize)
        const item = items[i]!
        const isSelected = selected.has(item.value)
        const isCursor = i === cursorIndex
        const prefix = isCursor ? '\x1B[36m>\x1B[0m' : ' '
        const check = isSelected ? '\x1B[32m[x]\x1B[0m' : '[ ]'
        const lock = item.locked ? ' \x1B[90m(locked)\x1B[0m' : ''
        process.stdout.write(`\x1B[2K${prefix} ${check} ${item.label}${lock}\n`)
        lines++
      }

      if (items.length === 0) {
        process.stdout.write('\x1B[2K  \x1B[90m(no matches)\x1B[0m\n')
        lines++
      }

      lastRenderedLines = lines
    }

    const scheduleRender = () => {
      if (debounceTimer) clearTimeout(debounceTimer)
      debounceTimer = setTimeout(render, 150)
    }

    const cleanup = () => {
      if (debounceTimer) clearTimeout(debounceTimer)
      stdin.setRawMode(false)
      stdin.pause()
      stdin.removeListener('data', onKeypress)
    }

    const onKeypress = (data: Buffer) => {
      const key = data.toString()

      // Escape
      if (key === '\x1B') {
        cleanup()
        resolve(cancelSymbol)
        return
      }

      // Enter
      if (key === '\r') {
        cleanup()
        resolve([...selected])
        return
      }

      // Ctrl+C
      if (key === '\x03') {
        cleanup()
        resolve(cancelSymbol)
        return
      }

      // Space: toggle
      if (key === ' ') {
        const items = filtered()
        const item = items[cursorIndex]
        if (item && !item.locked) {
          if (selected.has(item.value)) selected.delete(item.value)
          else selected.add(item.value)
        }
        render()
        return
      }

      // Arrow up
      if (key === '\x1B[A') {
        cursorIndex = Math.max(0, cursorIndex - 1)
        render()
        return
      }

      // Arrow down
      if (key === '\x1B[B') {
        cursorIndex = Math.min(filtered().length - 1, cursorIndex + 1)
        render()
        return
      }

      // Backspace
      if (key === '\x7F') {
        filterText = filterText.slice(0, -1)
        cursorIndex = 0
        scheduleRender()
        return
      }

      // Printable character
      if (key.length === 1 && key >= ' ') {
        filterText += key
        cursorIndex = 0
        scheduleRender()
      }
    }

    stdin.on('data', onKeypress)
    render()
  })
}
