// === ViewerData: CLI -> Viewer ===

export interface ViewerData {
  skillName: string
  iteration: number
  generatedAt: string
  evals: EvalCase[]
  benchmark: Benchmark
  engineOperators: Record<string, EngineOperator[]>
  previousEvals?: EvalCase[]
}

export interface EvalCase {
  evalId: number
  evalName: string
  prompt: string
  configurations: {
    with_skill: RunData
    without_skill: RunData
  }
  assertions: Assertion[]
}

export interface RunData {
  raw: string
  parsed: ParsedMatrix
  grading: GradingResult
  timing: { total_tokens: number; duration_ms: number }
}

export interface Assertion {
  id: string
  text: string
  type: 'structural' | 'quality' | 'behavioral'
}

export interface GradingResult {
  pass_rate: number
  passed: number
  total: number
  expectations: GradedExpectation[]
}

export interface GradedExpectation {
  text: string
  passed: boolean
  evidence: string
}

// === ParsedMatrix ===

export interface ParsedMatrix {
  context: { goal: string; type: string; domain: string } | null
  tiers: Tier[]
  runtimeRecovery: string[]
  gradingSummary: string
  decomposition: { subQuestions: string[]; executionOrder: string } | null
}

export interface Tier {
  level: 1 | 2 | 3
  label: string
  rows: MatrixRow[]
}

export interface MatrixRow {
  num: number
  engines: string[]
  query: string
  operators: string
  expectedResults: string
  acceptance: string
  success: string
}

// === Benchmark ===

export interface Benchmark {
  configurations: BenchmarkConfig[]
  delta: Record<string, string>
  analysis: { observations: string[] }
}

export interface BenchmarkConfig {
  name: string
  evals: { eval_name: string; pass_rate: number; tokens: number; duration_seconds: number }[]
  aggregate: { mean_pass_rate: number; mean_tokens: number; mean_duration_seconds: number }
}

// === Engine Operators (Pass 2 -- stub for now) ===

export interface EngineOperator {
  engine: string
  operator: string
  syntax: string
  example: string
  description: string
}

// === Semantic Comments (Viewer -> File) ===

export interface CommentFile {
  metadata: {
    skillName: string
    iteration: number
    exportedAt: string
  }
  comments: Comment[]
}

export interface Comment {
  id: string
  anchor: SemanticAnchor
  anchorLabel: string
  text: string
  timestamp: string
  resolved: boolean
}

export interface SemanticAnchor {
  evalId: number
  configuration: 'with_skill' | 'without_skill'
  section: 'context' | 'tier1' | 'tier2' | 'tier3' | 'recovery' | 'grading' | 'decomposition'
  row?: number
  column?: 'engines' | 'query' | 'operators' | 'expected' | 'acceptance' | 'success'
  token?: string
  tokenOffset?: number
}
