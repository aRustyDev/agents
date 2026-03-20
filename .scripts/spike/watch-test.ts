/**
 * Phase 0 spike: Bun fs.watch reliability test.
 * Watches a temp directory, writes a file, verifies callback fires.
 * Exit 0 = pass, exit 1 = fail.
 */

import { watch } from 'node:fs'
import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

const dir = await mkdtemp(join(tmpdir(), 'gv-watch-'))

const result = await new Promise<{ filename: string; eventType: string }>((resolve, reject) => {
  const timeout = setTimeout(() => {
    watcher.close()
    reject(new Error('fs.watch timeout — no event after 3s'))
  }, 3000)

  const watcher = watch(dir, (eventType, filename) => {
    clearTimeout(timeout)
    watcher.close()
    resolve({ eventType, filename: String(filename) })
  })

  // Write a file after a small delay to ensure watcher is ready
  setTimeout(async () => {
    await Bun.write(join(dir, 'test.json'), '{"test": true}')
  }, 100)
})

console.log('fs.watch event:', result.eventType, result.filename)

if (result.filename === 'test.json') {
  console.log('PASS: fs.watch fires reliably for file writes')
  await rm(dir, { recursive: true })
  process.exit(0)
} else {
  console.error('FAIL: unexpected filename:', result.filename)
  await rm(dir, { recursive: true })
  process.exit(1)
}
