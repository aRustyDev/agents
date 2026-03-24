/**
 * Embedding utilities module.
 *
 * Provides helpers for preparing text before embedding generation,
 * and health checks for the Ollama embedding backend.
 */

import { Ollama } from 'ollama'

// ---------------------------------------------------------------------------
// Health checks
// ---------------------------------------------------------------------------

/**
 * Check if Ollama is reachable by listing available models.
 */
export async function isOllamaAvailable(): Promise<boolean> {
  try {
    const ollama = new Ollama()
    await ollama.list()
    return true
  } catch {
    return false
  }
}

/**
 * Check if a specific model is pulled and available in Ollama.
 */
export async function hasModel(model: string): Promise<boolean> {
  try {
    const ollama = new Ollama()
    const list = await ollama.list()
    return list.models.some((m) => m.name === model || m.name.startsWith(`${model}:`))
  } catch {
    return false
  }
}

// ---------------------------------------------------------------------------
// prepareEmbeddingText
// ---------------------------------------------------------------------------

/**
 * Prepare text for embedding by prepending the entity/document title.
 *
 * This gives the embedding model context about what document a chunk
 * belongs to, improving retrieval quality for chunks that lack
 * self-contained context (e.g. a paragraph that starts with "It also
 * supports..." without mentioning the tool name).
 *
 * @param title - The entity or document title to prepend
 * @param chunkText - The raw chunk text to embed
 * @returns Text ready for embedding, with title prepended if non-empty
 */
export function prepareEmbeddingText(title: string, chunkText: string): string {
  if (!title.trim()) return chunkText
  return `${title.trim()}\n\n${chunkText}`
}
