/**
 * Zero-dependency UUID generation: v4, v5, v7.
 */

/**
 * Generate a random UUID v4.
 * Uses native crypto.randomUUID().
 */
export function uuid4(): string {
  return crypto.randomUUID()
}

/**
 * Generate a deterministic UUID v5 from a namespace UUID and a name.
 * Uses SHA-1 via crypto.subtle (async).
 *
 * @param namespace - A UUID string used as the namespace
 * @param name - The name to hash within the namespace
 */
export async function uuid5(namespace: string, name: string): Promise<string> {
  // Parse namespace UUID to bytes
  const nsBytes = uuidToBytes(namespace)

  // Concatenate namespace bytes + name bytes
  const nameBytes = new TextEncoder().encode(name)
  const data = new Uint8Array(nsBytes.length + nameBytes.length)
  data.set(nsBytes)
  data.set(nameBytes, nsBytes.length)

  // SHA-1 hash
  const hashBuffer = await crypto.subtle.digest('SHA-1', data)
  const hash = new Uint8Array(hashBuffer)

  // Set version (5) and variant (RFC 4122)
  hash[6] = (hash[6]! & 0x0f) | 0x50 // version 5
  hash[8] = (hash[8]! & 0x3f) | 0x80 // variant RFC 4122

  return bytesToUuid(hash.slice(0, 16))
}

/**
 * Generate a timestamp-sortable UUID v7.
 * Embeds millisecond-precision Unix timestamp in the high bits.
 */
export function uuid7(): string {
  const now = Date.now()
  const bytes = new Uint8Array(16)

  // Timestamp (48 bits, big-endian)
  bytes[0] = (now / 2 ** 40) & 0xff
  bytes[1] = (now / 2 ** 32) & 0xff
  bytes[2] = (now / 2 ** 24) & 0xff
  bytes[3] = (now / 2 ** 16) & 0xff
  bytes[4] = (now / 2 ** 8) & 0xff
  bytes[5] = now & 0xff

  // Random bits for the rest
  const random = crypto.getRandomValues(new Uint8Array(10))
  bytes.set(random, 6)

  // Set version (7) and variant (RFC 4122)
  bytes[6] = (bytes[6]! & 0x0f) | 0x70 // version 7
  bytes[8] = (bytes[8]! & 0x3f) | 0x80 // variant RFC 4122

  return bytesToUuid(bytes)
}

// ---------------------------------------------------------------------------
// Well-known namespace UUIDs (RFC 4122)
// ---------------------------------------------------------------------------

export const UUID_NAMESPACE = {
  DNS: '6ba7b810-9dad-11d1-80b4-00c04fd430c8',
  URL: '6ba7b811-9dad-11d1-80b4-00c04fd430c8',
  OID: '6ba7b812-9dad-11d1-80b4-00c04fd430c8',
  X500: '6ba7b814-9dad-11d1-80b4-00c04fd430c8',
} as const

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function uuidToBytes(uuid: string): Uint8Array {
  const hex = uuid.replace(/-/g, '')
  const bytes = new Uint8Array(16)
  for (let i = 0; i < 16; i++) {
    bytes[i] = parseInt(hex.slice(i * 2, i * 2 + 2), 16)
  }
  return bytes
}

function bytesToUuid(bytes: Uint8Array): string {
  const hex = Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('')
  return [
    hex.slice(0, 8),
    hex.slice(8, 12),
    hex.slice(12, 16),
    hex.slice(16, 20),
    hex.slice(20, 32),
  ].join('-')
}
