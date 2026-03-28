/**
 * Interactive terminal prompt library.
 *
 * Zero external dependencies -- uses raw `node:readline` and ANSI escapes.
 * All prompts respect `--yes` flag and detect non-TTY environments.
 */

/** Symbol returned when the user cancels a prompt. */
export const cancelSymbol: unique symbol = Symbol('cancel')
export type CancelSymbol = typeof cancelSymbol

export { type ConfirmOptions, confirm } from './confirm'
export {
  type SearchMultiselectOptions,
  type SelectItem,
  searchMultiselect,
} from './search-multiselect'
