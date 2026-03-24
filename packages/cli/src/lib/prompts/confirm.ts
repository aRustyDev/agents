import { createInterface } from 'node:readline'
import type { CancelSymbol } from './index'

export interface ConfirmOptions {
  message: string
  default?: boolean
  yes?: boolean
}

export async function confirm(opts: ConfirmOptions): Promise<boolean | CancelSymbol> {
  const defaultValue = opts.default ?? false

  // Non-interactive mode
  if (opts.yes || !process.stdin.isTTY) {
    return defaultValue
  }

  const hint = defaultValue ? '[Y/n]' : '[y/N]'

  return new Promise((resolve) => {
    const rl = createInterface({
      input: process.stdin,
      output: process.stdout,
    })

    rl.question(`${opts.message} ${hint} `, (answer) => {
      rl.close()
      const trimmed = answer.trim().toLowerCase()
      if (trimmed === '') resolve(defaultValue)
      else if (trimmed === 'y' || trimmed === 'yes') resolve(true)
      else if (trimmed === 'n' || trimmed === 'no') resolve(false)
      else resolve(defaultValue)
    })
  })
}
