export type SdkErrorCode =
  | 'E_PROVIDER_UNAVAILABLE'
  | 'E_COMPONENT_NOT_FOUND'
  | 'E_PARSE_FRONTMATTER'
  | 'E_CATALOG_SYNC_FAILED'
  | 'E_VALIDATION_FAILED'
  | 'E_STORAGE_BACKEND'
  | 'E_SCHEMA_INVALID'
  | 'E_PROVIDER_TIMEOUT'

export class SdkError extends Error {
  readonly code: SdkErrorCode
  readonly detail?: string

  constructor(message: string, code: SdkErrorCode, detail?: string) {
    super(message)
    this.name = 'SdkError'
    this.code = code
    this.detail = detail
  }

  display(): string {
    return this.detail ? `${this.message}: ${this.detail}` : this.message
  }
}
