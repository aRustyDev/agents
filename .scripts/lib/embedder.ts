/**
 * Embedding utilities module.
 *
 * Provides helpers for preparing text before embedding generation.
 * The actual embedding backends (Ollama, sentence-transformers) remain
 * in the Python implementation (embedder.py).
 */

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
