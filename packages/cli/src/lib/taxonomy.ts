#!/usr/bin/env bun
/* cspell:disable */
/**
 * Taxonomy Rule Engine — Phase 1 of Skill Catalog Inspection Pipeline
 *
 * Classifies skill names into 19 categories using regex rules.
 * Usage: bun run cli/lib/taxonomy.ts
 *
 * Reads:  content/skills/.TODO.yaml   (key: skills, entries: org/repo@skill-name)
 * Writes: content/skills/.taxonomy.yaml
 */

import * as fs from 'node:fs'
import * as path from 'node:path'
import * as yaml from 'js-yaml'
import { currentDir } from './runtime'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export const CATEGORIES = [
  'lang',
  'frontend',
  'ui',
  'ux',
  'backend',
  'devops',
  'ai-ml',
  'mobile',
  'security',
  'data',
  'content',
  'testing',
  'methodology',
  'tooling',
  'cloud',
  'finance',
  'game',
  'iot-embedded',
  'misc',
] as const

export type Category = (typeof CATEGORIES)[number]

export interface TaxonomyEntry {
  category: Category
  subcategory: string
}

export interface TaxonomyManifest {
  taxonomy: Record<string, TaxonomyEntry>
}

interface TodoManifest {
  skills: string[]
}

// ---------------------------------------------------------------------------
// Rules: [regex, category, subcategory]
// ---------------------------------------------------------------------------

export const RULES: [RegExp, Category, string][] = [
  // =========================================================================
  // lang — Programming languages
  // =========================================================================
  [
    /^python[-_ ]|^py[-_ ]|^django|^flask|^fastapi|^pydantic|^pytest|[-_ ]python$|^python$/,
    'lang',
    'python',
  ],
  [/^rust[-_ ]|^cargo[-_ ]|^tokio|^axum|^clippy|[-_ ]rust$|^rust$/, 'lang', 'rust'],
  [/^swift[-_ ]|^swift[0-9]|^swiftui|[-_ ]swift$|^swift$/, 'lang', 'swift'],
  [/^golang[-_ ]|^go[-_ ]|^gin[-_ ]|[-_ ]golang$|^go$/, 'lang', 'golang'],
  [/^typescript[-_ ]|^ts[-_ ]|[-_ ]typescript$|^typescript$/, 'lang', 'typescript'],
  [
    /^javascript[-_ ]|^js[-_ ]|^node[-_ ]|^nodejs|[-_ ]javascript$|^javascript$/,
    'lang',
    'javascript',
  ],
  [/^java[-_ ]|^spring[-_ ]|^maven|^gradle|[-_ ]java$|^java$/, 'lang', 'java'],
  [/^kotlin[-_ ]|[-_ ]kotlin$|^kotlin$/, 'lang', 'kotlin'],
  [/^elixir[-_ ]|^phoenix[-_ ]|^ecto|[-_ ]elixir$|^elixir$/, 'lang', 'elixir'],
  [/^ruby[-_ ]|^rails[-_ ]|^sinatra|[-_ ]ruby$|^ruby$/, 'lang', 'ruby'],
  [/^php[-_ ]|^laravel|^symfony|[-_ ]php$|^php$/, 'lang', 'php'],
  [/^csharp[-_ ]|^c#|^dotnet|^\.net|^blazor|^asp\.net|^aspnet/, 'lang', 'csharp'],
  [/^cpp[-_ ]|^c\+\+|[-_ ]cpp$|^cpp$/, 'lang', 'cpp'],
  [/^scala[-_ ]|[-_ ]scala$|^scala$/, 'lang', 'scala'],
  [/^haskell[-_ ]|[-_ ]haskell$|^haskell$/, 'lang', 'haskell'],
  [/^erlang[-_ ]|^otp[-_ ]|[-_ ]erlang$|^erlang$/, 'lang', 'erlang'],
  [/^clojure[-_ ]|[-_ ]clojure$|^clojure$/, 'lang', 'clojure'],
  [/^zig[-_ ]|[-_ ]zig$|^zig$/, 'lang', 'zig'],
  [/^lua[-_ ]|[-_ ]lua$|^lua$/, 'lang', 'lua'],
  [/^r[-_ ]language|^rlang|^tidyverse|^shiny[-_ ]/, 'lang', 'r'],
  [/^dart[-_ ]|[-_ ]dart$|^dart$/, 'lang', 'dart'],
  [/^solidity[-_ ]|^vyper|[-_ ]solidity$/, 'lang', 'solidity'],
  [/^sql[-_ ]|^postgres|^mysql|^sqlite|^postgresql|[-_ ]sql$|^sql$/, 'lang', 'sql'],
  [/^graphql[-_ ]|[-_ ]graphql$|^graphql$/, 'lang', 'graphql'],
  [/^bun[-_ ]|[-_ ]bun$|^bun$/, 'lang', 'bun'],
  [/^fsharp[-_ ]|^f#[-_ ]|[-_ ]fsharp$|^fsharp$/, 'lang', 'fsharp'],
  [/^elm[-_ ]|[-_ ]elm$|^elm$/, 'lang', 'elm'],
  [/^roc[-_ ]|[-_ ]roc$|^roc$/, 'lang', 'roc'],
  [/^objc[-_ ]|^objective[-_ ]c|[-_ ]objc$|^objc$/, 'lang', 'objc'],
  [/^carbon[-_ ]|[-_ ]carbon$|^carbon$/, 'lang', 'carbon'],
  [/^lean4[-_ ]|^lean[-_ ]4|[-_ ]lean4$/, 'lang', 'lean4'],
  [/^sparql[-_ ]|[-_ ]sparql$|^sparql$/, 'lang', 'sparql'],
  [/^cypher[-_ ]|[-_ ]cypher$|^cypher$/, 'lang', 'cypher'],
  [/^c[-_ ]language|^lang[-_ ]c$|^c[-_ ]dev$|^c[-_ ]library/, 'lang', 'c'],
  [/^ocaml[-_ ]|[-_ ]ocaml$|^ocaml$/, 'lang', 'ocaml'],

  // =========================================================================
  // frontend — Frontend frameworks and web UI
  // =========================================================================
  [/^react[-_ ](?!native)|^nextjs|^next[-_ ](?!gen)|^remix[-_ ]/, 'frontend', 'react'],
  [/^vue[-_ ]|^vuex|^nuxt|^pinia/, 'frontend', 'vue'],
  [/^svelte[-_ ]|^sveltekit/, 'frontend', 'svelte'],
  [/^angular[-_ ]/, 'frontend', 'angular'],
  [/^css[-_ ]|^scss[-_ ]|^sass[-_ ]|^less[-_ ]|^postcss/, 'frontend', 'css'],
  [/^tailwind/, 'frontend', 'tailwind'],
  [/^astro[-_ ]|[-_ ]astro$|^astro$/, 'frontend', 'astro'],
  [/^htmx/, 'frontend', 'htmx'],
  [/^webpack|^vite[-_ ]|^esbuild|^rollup/, 'frontend', 'bundler'],
  [/^web[-_ ]artifacts|^artifacts[-_ ]builder|^web[-_ ]artifact/, 'frontend', 'artifacts'],
  [/^frontend[-_ ]design|^frontend[-_ ]testing|^frontend[-_ ]web/, 'frontend', 'general'],
  [/^tinacms|^tina[-_ ]/, 'frontend', 'cms'],

  // =========================================================================
  // ui — UI design systems and components
  // =========================================================================
  [/^ui[-_ ]design|^ui[-_ ]ux[-_ ]|^design[-_ ]system|^design[-_ ]to[-_ ]/, 'ui', 'design-system'],
  [/^component[-_ ]|^storybook/, 'ui', 'components'],
  [/^icon[-_ ]|^icons/, 'ui', 'icons'],
  [/^color[-_ ]palette|^typography/, 'ui', 'visual'],
  [/^responsive/, 'ui', 'responsive'],
  [/^animation[-_ ]|^motion[-_ ]|^framer/, 'ui', 'animation'],
  [/^landing[-_ ]page/, 'ui', 'landing-page'],
  [/^material[-_ ]design|^shadcn|^ark[-_ ]ui|^panda[-_ ]css/, 'ui', 'design-system'],
  [/^canvas[-_ ]design|^algorithmic[-_ ]art|^canvas[-_ ]/, 'ui', 'canvas'],
  [/^theme[-_ ]factory|^design[-_ ]brand|^brand[-_ ]apply|^applying[-_ ]brand/, 'ui', 'theming'],
  [/^ui[-_ ]ux[-_ ]pro|^nextlevelbuilder/, 'ui', 'general'],

  // =========================================================================
  // ux — User experience, research, accessibility
  // =========================================================================
  [/^user[-_ ]research|^user[-_ ]discovery/, 'ux', 'research'],
  [/^user[-_ ]stor|^persona/, 'ux', 'user-story'],
  [/^wireframe|^prototype|^prototyping/, 'ux', 'prototyping'],
  [/^a11y[-_ ]|^accessibility[-_ ]|^wcag/, 'ux', 'accessibility'],
  [/^ux[-_ ]|[-_ ]ux$/, 'ux', 'general'],

  // =========================================================================
  // backend — APIs, databases, auth, caching
  // =========================================================================
  [/^api[-_ ]design|^rest[-_ ]api|^openapi|^openapi[-_ ]spec/, 'backend', 'api'],
  [/^database[-_ ]|^db[-_ ]|^postgres[-_ ]schema|^postgres[-_ ]schema/, 'backend', 'database'],
  [/^redis[-_ ]|^cache[-_ ]|^caching/, 'backend', 'cache'],
  [/^supabase[-_ ]/, 'backend', 'supabase'],
  [/^auth[-_ ]|^oauth|^jwt[-_ ]|^auth[-_ ]implementation/, 'backend', 'auth'],
  [/^graphdb|^neo4j|^cypher[-_ ]graph/, 'backend', 'graphdb'],
  [/^clickhouse|^duckdb|^timescale/, 'backend', 'database'],
  [/^grpc/, 'backend', 'grpc'],
  [/^microservices|^saga[-_ ]|^cqrs|^event[-_ ]store|^projection[-_ ]/, 'backend', 'patterns'],
  [/^architecture[-_ ]patterns|^api[-_ ]design[-_ ]principles/, 'backend', 'patterns'],
  [/^postgresql$|^mysql$|^sqlite$/, 'backend', 'database'],
  [
    /^query[-_ ]performance|^database[-_ ]index|^database[-_ ]diff|^database[-_ ]health/,
    'backend',
    'database',
  ],
  [/^sql[-_ ]optimization/, 'backend', 'database'],

  // =========================================================================
  // devops — CI/CD, containers, IaC, monitoring
  // =========================================================================
  [/^docker[-_ ]|^container/, 'devops', 'docker'],
  [
    /^k8s[-_ ]|^kubernetes[-_ ]|^helm[-_ ]|^k8s[-_ ]security|^k8s[-_ ]manifest/,
    'devops',
    'kubernetes',
  ],
  [/^terraform[-_ ]|^opentofu|^terraform[-_ ]module|^iac[-_ ]terraform/, 'devops', 'terraform'],
  [
    /^ci[-_ ]cd|^cicd|^github[-_ ]action|^gitlab[-_ ]ci|^deployment[-_ ]pipeline/,
    'devops',
    'ci-cd',
  ],
  [/^gitops|^gitops[-_ ]workflow/, 'devops', 'gitops'],
  [/^ansible[-_ ]|^puppet[-_ ]|^chef[-_ ]/, 'devops', 'config-management'],
  [
    /^monitoring[-_ ]|^grafana|^prometheus|^observability|^prometheus[-_ ]config|^slo[-_ ]/,
    'devops',
    'monitoring',
  ],
  [/^nginx|^caddy|^traefik/, 'devops', 'proxy'],
  [/^bazel[-_ ]/, 'devops', 'build'],
  [
    /^multi[-_ ]cloud|^service[-_ ]mesh|^cost[-_ ]optimization|^linkerd|^mtls/,
    'devops',
    'cloud-ops',
  ],
  [/^distributed[-_ ]tracing|^service[-_ ]mesh[-_ ]observability/, 'devops', 'monitoring'],
  [/^secrets[-_ ]management/, 'devops', 'secrets'],
  [/^gitops[-_ ]workflow|^git[-_ ]ops/, 'devops', 'gitops'],
  [/^changelog[-_ ]automation/, 'devops', 'release'],
  [/^cicd[-_ ]|^cicd$/, 'devops', 'ci-cd'],
  [/^github[-_ ]actions[-_ ]templates|^gitlab[-_ ]ci[-_ ]patterns/, 'devops', 'ci-cd'],
  [/^helm[-_ ]chart[-_ ]scaffolding/, 'devops', 'kubernetes'],

  // =========================================================================
  // ai-ml — LLMs, RAG, agents, ML/AI tools
  // =========================================================================
  [/^llm[-_ ]|^large[-_ ]language/, 'ai-ml', 'llm'],
  [/^rag[-_ ]|^retrieval[-_ ]augmented|^rag[-_ ]implementation/, 'ai-ml', 'rag'],
  [/^agent[-_ ]|^agentic|^dispatching[-_ ]parallel/, 'ai-ml', 'agent'],
  [/^mcp[-_ ]|^model[-_ ]context|^mcp[-_ ]builder/, 'ai-ml', 'mcp'],
  [/^langchain|^langgraph|^llamaindex|^langchain[-_ ]architecture/, 'ai-ml', 'langchain'],
  [/^embedding|^vector[-_ ]|^embedding[-_ ]strategies|^vector[-_ ]index/, 'ai-ml', 'embedding'],
  [/^prompt[-_ ]|^prompting|^prompt[-_ ]engineering/, 'ai-ml', 'prompt'],
  [/^fine[-_ ]tun|^training[-_ ]/, 'ai-ml', 'training'],
  [/^mlops|^ml[-_ ]ops|^ai[-_ ]mlops/, 'ai-ml', 'mlops'],
  [/^openai[-_ ]|^claude[-_ ]|^gemini[-_ ]/, 'ai-ml', 'llm'],
  [/^diffusion|^stable[-_ ]diffusion|^image[-_ ]gen/, 'ai-ml', 'image-gen'],
  [/^perplexity[-_ ]search|^llm[-_ ]perplexity/, 'ai-ml', 'search'],
  [/^similarity[-_ ]search|^hybrid[-_ ]search/, 'ai-ml', 'search'],
  [/^llm[-_ ]evaluation|^ai[-_ ]evaluation|^ai[-_ ]rag|^ai[-_ ]agents/, 'ai-ml', 'evaluation'],
  [/^model[-_ ]architecture|^tokenization|^fine[-_ ]tuning|^mechanistic/, 'ai-ml', 'research'],
  [
    /^post[-_ ]training|^safety[-_ ]alignment|^distributed[-_ ]training|^ai[-_ ]infrastructure/,
    'ai-ml',
    'research',
  ],
  [
    /^inference[-_ ]serving|^ai[-_ ]optimization|^ai[-_ ]observability|^ai[-_ ]prompt/,
    'ai-ml',
    'ops',
  ],
  [
    /^multimodal$|^emerging[-_ ]techniques|^ai[-_ ]research[-_ ]|^ai[-_ ]mlops/,
    'ai-ml',
    'research',
  ],
  [
    /^context[-_ ]fundamentals|^context[-_ ]optimization|^context[-_ ]compress|^context[-_ ]degradation/,
    'ai-ml',
    'content',
  ],
  [/^memory[-_ ]systems/, 'ai-ml', 'memory'],
  [/^perplexity/, 'ai-ml', 'search'],
  [/^advanced[-_ ]evaluation|^context[-_ ]evaluation|^evaluation$/, 'ai-ml', 'evaluation'],

  // =========================================================================
  // mobile — iOS, Android, React Native, Flutter
  // =========================================================================
  [/^ios[-_ ]|^iphone/, 'mobile', 'ios'],
  [/^android[-_ ]/, 'mobile', 'android'],
  [/^react[-_ ]native/, 'mobile', 'react-native'],
  [/^flutter[-_ ]|[-_ ]flutter$|^flutter$/, 'mobile', 'flutter'],
  [/^app[-_ ]store|^asc[-_ ]/, 'mobile', 'app-store'],
  [/^expo[-_ ]/, 'mobile', 'expo'],

  // =========================================================================
  // security — Pentesting, forensics, compliance, crypto
  // =========================================================================
  [/^pentest|^penetration/, 'security', 'pentest'],
  [/^burp[-_ ]|^zap[-_ ]/, 'security', 'tools'],
  [/^malware|^reverse[-_ ]engineer|^anti[-_ ]revers/, 'security', 'malware'],
  [/^forensic|^incident[-_ ]response/, 'security', 'forensics'],
  [/^vulnerab|^cve[-_ ]|^exploit/, 'security', 'vulnerability'],
  [/^osint|^intel[-_ ]|^threat[-_ ]intel/, 'security', 'intel'],
  [/^bug[-_ ]bounty/, 'security', 'bug-bounty'],
  [/^crypto[-_ ]graph|^encrypt|^tls[-_ ]|^ssl[-_ ]/, 'security', 'cryptography'],
  [/^compliance|^soc[-_ ]2|^hipaa|^gdpr|^pci/, 'security', 'compliance'],
  [
    /^sast[-_ ]|^threat[-_ ]mitigation|^security[-_ ]requirement|^k8s[-_ ]security[-_ ]/,
    'security',
    'scanning',
  ],
  [/^defense[-_ ]in[-_ ]depth|^defense[-_ ]|^iot[-_ ]hack|^iot[-_ ]pentest/, 'security', 'defense'],
  [/^sec[-_ ]ops|^security[-_ ]ops/, 'security', 'secops'],
  [/^mtls[-_ ]|^secrets[-_ ]management$/, 'security', 'cryptography'],
  [/^security[-_ ]guidance|^security[-_ ]scanning/, 'security', 'general'],

  // =========================================================================
  // data — Data engineering, analytics, visualization
  // =========================================================================
  [/^data[-_ ]engineer|^data[-_ ]pipeline|^etl|^elt/, 'data', 'engineering'],
  [/^data[-_ ]analy|^analytics|^exploratory[-_ ]data/, 'data', 'analytics'],
  [/^data[-_ ]viz|^visualization|^chart|^matplotlib|^seaborn|^plotly/, 'data', 'visualization'],
  [/^dbt[-_ ]|^dbt[-_ ]transformation/, 'data', 'dbt'],
  [/^spark[-_ ]|^flink[-_ ]|^kafka[-_ ]|^airflow|^airflow[-_ ]dag/, 'data', 'streaming'],
  [/^data[-_ ]quality|^data[-_ ]quality[-_ ]frameworks/, 'data', 'quality'],
  [
    /^polars|^dask|^statsmodels|^pymc|^anndata|^networkx|^shap|^sympy|^transformers[-_ ]/,
    'data',
    'libraries',
  ],
  [/^data[-_ ]market[-_ ]research|^market[-_ ]research/, 'data', 'analysis'],
  [/^statistical[-_ ]analysis|^hypothesis[-_ ]generation/, 'data', 'statistics'],
  [/^neuropixels|^histolab|^qiskit|^pennylane|^qutip/, 'data', 'scientific'],
  [
    /^loading[-_ ]datasets|^performing[-_ ]causal|^running[-_ ]placebo|^designing[-_ ]experiments/,
    'data',
    'analysis',
  ],
  [/^citation[-_ ]management|^scientific[-_ ]writing/, 'data', 'research'],
  [/^labarchive|^protocolsio/, 'data', 'research'],
  [/^reportlab|^market[-_ ]research[-_ ]reports/, 'data', 'reporting'],

  // =========================================================================
  // content — SEO, copywriting, marketing, brand
  // =========================================================================
  [/^seo[-_ ]/, 'content', 'seo'],
  [/^marketing[-_ ]|^growth[-_ ]/, 'content', 'marketing'],
  [/^blog[-_ ]|^technical[-_ ]writ|^scientific[-_ ]writ/, 'content', 'writing'],
  [/^copywriting|^copy[-_ ]edit|^humanizer/, 'content', 'copywriting'],
  [/^social[-_ ]media|^social[-_ ]content/, 'content', 'social-media'],
  [
    /^brand[-_ ]guidelines|^brand[-_ ]apply|^applying[-_ ]brand|^design[-_ ]brand/,
    'content',
    'brand',
  ],
  [/^content[-_ ]strat|^content[-_ ]creat/, 'content', 'strategy'],
  [/^email[-_ ]|^newsletter/, 'content', 'email'],
  [/^doc[-_ ]coauthoring|^internal[-_ ]comms|^pptx|^docx|^xlsx|^pdf[-_ ]/, 'content', 'documents'],
  [/^slack[-_ ]gif|^canvas[-_ ]/, 'content', 'social-media'],

  // =========================================================================
  // testing — Unit, E2E, visual, load, QA
  // =========================================================================
  [
    /^e2e[-_ ]|^end[-_ ]to[-_ ]end|^playwright[-_ ]|^cypress[-_ ]|^selenium|^e2e[-_ ]testing/,
    'testing',
    'e2e',
  ],
  [/^jest[-_ ]|^vitest[-_ ]|^mocha/, 'testing', 'unit'],
  [/^unit[-_ ]test/, 'testing', 'unit'],
  [/^mock[-_ ]|^mocking/, 'testing', 'mock'],
  [/^qa[-_ ]|^quality[-_ ]assur/, 'testing', 'qa'],
  [/^integration[-_ ]test/, 'testing', 'integration'],
  [/^chaos[-_ ]/, 'testing', 'chaos'],
  [/^visual[-_ ]test|^snapshot[-_ ]test/, 'testing', 'visual'],
  [/^coverage|^code[-_ ]coverage|^gcov/, 'testing', 'coverage'],
  [/^load[-_ ]test|^stress[-_ ]test|^perf[-_ ]test/, 'testing', 'performance'],
  [/^webapp[-_ ]test|^frontend[-_ ]testing|^testing[-_ ]anti[-_ ]pattern/, 'testing', 'e2e'],
  [
    /^tdd[-_ ]|^test[-_ ]driven|^python[-_ ]testing|^javascript[-_ ]testing|^java[-_ ]testing/,
    'testing',
    'general',
  ],
  [/^rr[-_ ]debugger|^function[-_ ]tracing|^line[-_ ]execution/, 'testing', 'debugging'],
  [/^testing[-_ ]hash|^testing[-_ ]skills[-_ ]with/, 'testing', 'general'],

  // =========================================================================
  // methodology — Debugging, code review, architecture, refactoring
  // =========================================================================
  [/^brainstorm|^method[-_ ]brainstorm/, 'methodology', 'brainstorming'],
  [/^debug|^troubleshoot|^systematic[-_ ]debug|^debugging[-_ ]strateg/, 'methodology', 'debugging'],
  [
    /^code[-_ ]review|^pr[-_ ]review|^review[-_ ]|^receiving[-_ ]code[-_ ]review|^requesting[-_ ]code[-_ ]review/,
    'methodology',
    'code-review',
  ],
  [/^spec[-_ ]|^specification/, 'methodology', 'spec'],
  [/^architecture[-_ ]decision|^adr|^system[-_ ]design/, 'methodology', 'architecture'],
  [/^refactor/, 'methodology', 'refactoring'],
  [
    /^documentation[-_ ]|^docs[-_ ]|^openapi[-_ ]spec|^architecture[-_ ]decision[-_ ]records/,
    'methodology',
    'documentation',
  ],
  [
    /^parallel[-_ ]agents|^dispatching[-_ ]parallel|^subagent[-_ ]driven|^subagent[-_ ]dev/,
    'methodology',
    'agents',
  ],
  [/^kaizen|^hypothesis[-_ ]generation|^critical[-_ ]thinking/, 'methodology', 'improvement'],
  [
    /^peer[-_ ]review|^literature[-_ ]review|^research[-_ ]grants|^scholar[-_ ]evaluation/,
    'methodology',
    'research',
  ],
  [/^verification|^method[-_ ]verification/, 'methodology', 'verification'],
  [
    /^execution[-_ ]|^executing[-_ ]plan|^writing[-_ ]plan|^method[-_ ]executing|^method[-_ ]writing/,
    'methodology',
    'planning',
  ],
  [/^branch[-_ ]completion|^finishing[-_ ]a[-_ ]dev/, 'methodology', 'git-workflow'],
  [/^reproduce[-_ ]reduce|^reproduce[-_ ]|^method[-_ ]reproduce/, 'methodology', 'debugging'],
  [/^root[-_ ]cause/, 'methodology', 'debugging'],
  [/^defense[-_ ]in[-_ ]depth/, 'methodology', 'security'],
  [/^working[-_ ]with[-_ ]marimo/, 'methodology', 'tools'],
  [
    /^context[-_ ]engineering|^context[-_ ]evaluation|^context[-_ ]optimization|^meta[-_ ]context/,
    'methodology',
    'content',
  ],
  [
    /^skill[-_ ]|^meta[-_ ]skill|^writing[-_ ]skills|^using[-_ ]superpowers|^superpowers/,
    'methodology',
    'meta',
  ],
  [
    /^plugin[-_ ]|^hook[-_ ]dev|^command[-_ ]dev|^agent[-_ ]dev|^meta[-_ ]plugin|^meta[-_ ]hook|^meta[-_ ]command|^meta[-_ ]agent/,
    'methodology',
    'meta',
  ],
  [/^convert[-_ ]|^meta[-_ ]convert/, 'methodology', 'conversion'],

  // =========================================================================
  // tooling — Developer tools, editors, linters, git, diagrams
  // =========================================================================
  [
    /^mermaid|^plantuml|^d2[-_ ]|^drawio|^scientific[-_ ]schematics|^docs[-_ ]scientific/,
    'tooling',
    'diagrams',
  ],
  [
    /^git[-_ ]|^gitflow|^conventional[-_ ]commit|^managing[-_ ]git|^git[-_ ]advanced|^git[-_ ]workflow/,
    'tooling',
    'git',
  ],
  [/^vscode[-_ ]|^editor[-_ ]|^neovim/, 'tooling', 'editor'],
  [/^cli[-_ ]|^terminal/, 'tooling', 'cli'],
  [/^lint|^eslint|^prettier|^biome|^shellcheck|^bash[-_ ]defensive|^shfmt/, 'tooling', 'linting'],
  [/^repomix/, 'tooling', 'repomix'],
  [/^mdbook[-_ ]|^docs[-_ ]mdbook/, 'tooling', 'mdbook'],
  [/^justfile|^just[-_ ]file/, 'tooling', 'just'],
  [/^n8n[-_ ]|^workflow[-_ ]automation/, 'tooling', 'automation'],
  [/^changelog[-_ ]automation/, 'tooling', 'automation'],
  [/^git[-_ ]worktree|^using[-_ ]git[-_ ]worktree|^method[-_ ]git/, 'tooling', 'git'],
  [/^openmetadata|^open[-_ ]metadata/, 'tooling', 'metadata'],
  [/^openfeature|^open[-_ ]feature/, 'tooling', 'feature-flags'],
  [
    /^raptor|^windbg|^valgrind|^crash[-_ ]analysis|^oss[-_ ]forensics|^github[-_ ]wayback/,
    'tooling',
    'debugging',
  ],
  [
    /^skill[-_ ]creator|^plugin[-_ ]dev|^feature[-_ ]dev|^claude[-_ ]code|^claude[-_ ]md/,
    'tooling',
    'claude',
  ],
  [/^nanobanana|^youtube[-_ ]|^kiro[-_ ]/, 'tooling', 'productivity'],

  // =========================================================================
  // cloud — AWS, GCP, Azure, Cloudflare, hosting
  // =========================================================================
  [/^aws[-_ ]|^amazon[-_ ]|^lambda[-_ ]|^s3[-_ ]|^ec2/, 'cloud', 'aws'],
  [/^gcp[-_ ]|^google[-_ ]cloud/, 'cloud', 'gcp'],
  [/^azure[-_ ]/, 'cloud', 'azure'],
  [/^cloudflare[-_ ]|^cf[-_ ]worker|^cloud[-_ ]cloudflare/, 'cloud', 'cloudflare'],
  [/^vercel[-_ ]/, 'cloud', 'vercel'],
  [/^serverless|^lambda/, 'cloud', 'serverless'],
  [/^digitalocean|^linode|^hetzner/, 'cloud', 'hosting'],
  [/^terraform[-_ ]module[-_ ]library|^multi[-_ ]cloud[-_ ]architecture/, 'cloud', 'multi-cloud'],

  // =========================================================================
  // finance — Trading, crypto, fintech
  // =========================================================================
  [/^stock[-_ ]|^trading[-_ ]|^algo[-_ ]trad/, 'finance', 'trading'],
  [/^crypto[-_ ](?!graph)|^blockchain|^web3|^defi|^nft/, 'finance', 'crypto'],
  [/^fintech|^payment|^stripe[-_ ]/, 'finance', 'fintech'],
  [
    /^financial[-_ ]|^finance[-_ ]|^analyzing[-_ ]financial|^creating[-_ ]financial/,
    'finance',
    'analysis',
  ],

  // =========================================================================
  // game — Game engines, 3D, game design
  // =========================================================================
  [/^godot[-_ ]/, 'game', 'godot'],
  [/^unity[-_ ]/, 'game', 'unity'],
  [/^unreal[-_ ]|^ue[-_ ]/, 'game', 'unreal'],
  [/^3d[-_ ]|^three[-_ ]js|^webgl/, 'game', '3d'],
  [/^game[-_ ]design|^game[-_ ]dev/, 'game', 'game-design'],

  // =========================================================================
  // iot-embedded — IoT, embedded systems, Arduino, Raspberry Pi
  // =========================================================================
  [/^hardware[-_ ]|^firmware[-_ ]|^embedded/, 'iot-embedded', 'embedded'],
  [/^raspberry[-_ ]pi|^rpi/, 'iot-embedded', 'raspberry-pi'],
  [/^arduino/, 'iot-embedded', 'arduino'],
  [/^iot[-_ ]|^mqtt/, 'iot-embedded', 'iot'],
  [/^iothackbot|^iot[-_ ]hack/, 'iot-embedded', 'security'],

  // =========================================================================
  // Additional targeted rules for known skill names
  // =========================================================================

  // lang — specific library/tool skills
  [/^async[-_ ]python|^python[-_ ]perf|^python[-_ ]pack|^uv[-_ ]package/, 'lang', 'python'],
  [
    /^documenting[-_ ]rust|^exploring[-_ ]rust|^handling[-_ ]rust|^managing[-_ ]cargo|^rust[-_ ]error|^use[-_ ]facet|^memory[-_ ]safety/,
    'lang',
    'rust',
  ],
  [/^transformers$/, 'lang', 'python'],
  [/^profiling$|^benchmarking$/, 'lang', 'rust'],
  [/^zod$/, 'lang', 'typescript'],
  [/^mastra$/, 'lang', 'typescript'],
  [/^writing[-_ ]hashql|^testing[-_ ]hashql|^hashql/, 'lang', 'typescript'],
  [/^error[-_ ]handling[-_ ]patterns|^workflow[-_ ]orchestration[-_ ]patterns/, 'lang', 'general'],
  [/^pytorch|^pytorch[-_ ]skill/, 'lang', 'python'],
  [/^move[-_ ]code/, 'lang', 'move'],

  // tooling — specific tools
  [/^beads$/, 'tooling', 'issue-tracking'],
  [/^context7/, 'tooling', 'content'],
  [/^notebooklm|^notebook[-_ ]lm/, 'tooling', 'productivity'],
  [/^writing[-_ ]hookify|^hookify/, 'tooling', 'claude'],
  [
    /^web[-_ ]asset[-_ ]gen|^article[-_ ]extractor|^csv[-_ ]data|^metadata[-_ ]extraction/,
    'tooling',
    'automation',
  ],
  [/^tapestry$/, 'tooling', 'productivity'],
  [/^arxiv[-_ ]search|^web[-_ ]research/, 'tooling', 'research'],
  [/^file[-_ ]deletion|^github[-_ ]commit[-_ ]recovery|^github[-_ ]evidence/, 'tooling', 'git'],
  [/^ffuf|^web[-_ ]fuzz/, 'tooling', 'security'],
  [/^pypict|^d3js|^flow[-_ ]nexus/, 'tooling', 'visualization'],
  [/^neolab[-_ ]/, 'tooling', 'productivity'],

  // ai-ml — agent/LLM personas and research tools
  [/^senior[-_ ]ml|^senior[-_ ]prompt[-_ ]eng|^ml[-_ ]engineer/, 'ai-ml', 'roles'],
  [/^neolab[-_ ]prompt|^neolab[-_ ]sub/, 'ai-ml', 'prompt'],
  [/^lead[-_ ]research[-_ ]assistant|^content[-_ ]research/, 'ai-ml', 'agent'],
  [/^codex[-_ ]plan|^codex[-_ ]skill/, 'ai-ml', 'llm'],
  [/^ship[-_ ]learn|^review[-_ ]implementing/, 'ai-ml', 'agent'],
  [/^tool[-_ ]design$/, 'ai-ml', 'agent'],

  // methodology — agile, architecture
  [
    /^agile[-_ ]|^product[-_ ]owner|^product[-_ ]manager|^product[-_ ]strat/,
    'methodology',
    'agile',
  ],
  [
    /^neolab[-_ ]software[-_ ]arch|^neolab[-_ ]kaizen|^senior[-_ ]architect/,
    'methodology',
    'architecture',
  ],
  [/^cto[-_ ]advisor/, 'methodology', 'leadership'],
  [/^test[-_ ]fixing/, 'methodology', 'debugging'],
  [/^browser[-_ ]extension|^extension[-_ ]dev/, 'frontend', 'extensions'],

  // security — compliance, forensics, threat hunting
  [/^computer[-_ ]forensics|^oss[-_ ]forensic/, 'security', 'forensics'],
  [/^sigma[-_ ]threat|^threat[-_ ]hunt|^redteam/, 'security', 'threat-hunting'],
  [/^information[-_ ]security|^isms[-_ ]audit|^iso27001/, 'security', 'compliance'],
  [/^security[-_ ]compliance|^data[-_ ]privacy[-_ ]compliance/, 'security', 'compliance'],
  [/^capa[-_ ]officer|^ffuf|^web[-_ ]fuzz/, 'security', 'pentest'],
  [/^senior[-_ ]secops|^senior[-_ ]security/, 'security', 'roles'],

  // content — research, writing
  [/^family[-_ ]history|^employment[-_ ]contract/, 'content', 'writing'],
  [/^executing[-_ ]marketing|^content[-_ ]research[-_ ]writer/, 'content', 'marketing'],
  [/^quality[-_ ]doc|^quality[-_ ]documentation/, 'content', 'documents'],
  [/^arxiv/, 'content', 'research'],

  // data — processing
  [/^data[-_ ]processing$/, 'data', 'engineering'],
  [/^scientific[-_ ]critical/, 'data', 'scientific'],

  // devops — senior roles
  [/^senior[-_ ]devops/, 'devops', 'roles'],

  // backend/fullstack roles
  [/^senior[-_ ]backend|^senior[-_ ]fullstack|^senior[-_ ]qa/, 'backend', 'roles'],
]

// ---------------------------------------------------------------------------
// Classification function
// ---------------------------------------------------------------------------

export function classifyByRules(name: string): TaxonomyEntry | null {
  const lower = name.toLowerCase()
  for (const [regex, category, subcategory] of RULES) {
    if (regex.test(lower)) {
      return { category, subcategory }
    }
  }
  return null
}

// ---------------------------------------------------------------------------
// Extract unique skill names from .TODO.yaml
// ---------------------------------------------------------------------------

function extractSkillNames(todoPath: string): string[] {
  const content = fs.readFileSync(todoPath, 'utf-8')
  const data = yaml.load(content) as TodoManifest

  if (!data || !data.skills || !Array.isArray(data.skills)) {
    throw new Error(`Invalid .TODO.yaml: missing 'skills' array key`)
  }

  const skillNames = new Set<string>()
  for (const entry of data.skills) {
    // Skip non-string entries (some entries are dicts with descriptions)
    const raw =
      typeof entry === 'string' ? entry : typeof entry === 'object' ? Object.keys(entry)[0] : null
    if (!raw) continue
    // Format: org/repo@skill-name
    const atIdx = raw.lastIndexOf('@')
    if (atIdx !== -1) {
      skillNames.add(raw.slice(atIdx + 1))
    } else {
      // Fallback: use full entry as name
      skillNames.add(raw)
    }
  }

  return Array.from(skillNames).sort()
}

// ---------------------------------------------------------------------------
// Load existing taxonomy (for incremental updates)
// ---------------------------------------------------------------------------

function loadExistingTaxonomy(taxonomyPath: string): Record<string, TaxonomyEntry> {
  if (!fs.existsSync(taxonomyPath)) {
    return {}
  }
  const content = fs.readFileSync(taxonomyPath, 'utf-8')
  const data = yaml.load(content) as TaxonomyManifest
  if (!data || !data.taxonomy) {
    return {}
  }
  return data.taxonomy
}

// ---------------------------------------------------------------------------
// Main classification loop
// ---------------------------------------------------------------------------

function classify(
  skillNames: string[],
  existing: Record<string, TaxonomyEntry>,
  force: boolean
): Record<string, TaxonomyEntry> {
  const result: Record<string, TaxonomyEntry> = { ...existing }
  let classified = 0
  let unclassified = 0
  let skipped = 0

  for (const name of skillNames) {
    // Skip if already classified and not forcing
    if (!force && result[name]) {
      skipped++
      continue
    }

    const entry = classifyByRules(name)
    if (entry) {
      result[name] = entry
      classified++
    } else {
      result[name] = { category: 'misc', subcategory: 'unclassified' }
      unclassified++
    }
  }

  if (skipped > 0) {
    console.log(`  Skipped ${skipped} already-classified entries (use --force to reclassify)`)
  }
  console.log(`  Classified by rules: ${classified}`)
  console.log(`  Unclassified (misc): ${unclassified}`)

  return result
}

// ---------------------------------------------------------------------------
// Print distribution report
// ---------------------------------------------------------------------------

function printReport(
  taxonomy: Record<string, TaxonomyEntry>,
  totalSkillNames: number,
  allEntries: number
) {
  const counts: Record<string, number> = {}
  for (const entry of Object.values(taxonomy)) {
    counts[entry.category] = (counts[entry.category] || 0) + 1
  }

  const classified = totalSkillNames - (counts.misc || 0)
  const unclassified = counts.misc || 0
  const classifiedPct = ((classified / totalSkillNames) * 100).toFixed(1)
  const unclassifiedPct = ((unclassified / totalSkillNames) * 100).toFixed(1)

  console.log('\n=== Taxonomy Classification Report ===')
  console.log(`Total unique skill names:   ${totalSkillNames}`)
  console.log(`Total .TODO.yaml entries:   ${allEntries}`)
  console.log(`Classified by rules:        ${classified} (${classifiedPct}%)`)
  console.log(`Unclassified (misc):        ${unclassified} (${unclassifiedPct}%)`)
  console.log('\nDistribution by category:')

  const sortedCategories = Object.entries(counts).sort((a, b) => b[1] - a[1])
  for (const [cat, count] of sortedCategories) {
    const pct = ((count / totalSkillNames) * 100).toFixed(1)
    console.log(`  ${cat.padEnd(20)} ${String(count).padStart(5)}  (${pct}%)`)
  }
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------

const REPO_ROOT = path.resolve(currentDir(import.meta), '../../../..')
const TODO_PATH = path.join(REPO_ROOT, 'content/skills/.TODO.yaml')
const TAXONOMY_PATH = path.join(REPO_ROOT, 'content/skills/.taxonomy.yaml')

const args = process.argv.slice(2)
const force = args.includes('--force')
const jsonOutput = args.includes('--json')

if (!fs.existsSync(TODO_PATH)) {
  console.error(`Error: .TODO.yaml not found at ${TODO_PATH}`)
  console.error('Generate it first with: uv run python cli/generate-todo.py')
  process.exit(1)
}

console.log('Loading .TODO.yaml...')
const rawContent = fs.readFileSync(TODO_PATH, 'utf-8')
const rawData = yaml.load(rawContent) as TodoManifest
const allEntries = rawData?.skills?.length ?? 0

console.log(`Extracting unique skill names...`)
const skillNames = extractSkillNames(TODO_PATH)
console.log(`  Total .TODO.yaml entries: ${allEntries}`)
console.log(`  Unique skill names: ${skillNames.length}`)

console.log('\nLoading existing taxonomy (incremental)...')
const existing = loadExistingTaxonomy(TAXONOMY_PATH)
const existingCount = Object.keys(existing).length
console.log(`  Existing entries: ${existingCount}`)

console.log('\nClassifying by rules...')
const taxonomy = classify(skillNames, existing, force)

// Write output
const output: TaxonomyManifest = { taxonomy }
const yamlContent = yaml.dump(output, {
  sortKeys: true,
  lineWidth: 120,
  quotingType: '"',
  forceQuotes: false,
})

fs.writeFileSync(
  TAXONOMY_PATH,
  `# Skill Taxonomy — auto-generated by cli/lib/taxonomy.ts\n# Phase 1: Rule-based classification (LLM batch fills remaining misc entries)\n# DO NOT EDIT manually — regenerate with: bun run cli/lib/taxonomy.ts\n\n${yamlContent}`
)

if (jsonOutput) {
  console.log(
    '\n' +
      JSON.stringify(
        Object.entries(taxonomy).map(([name, entry]) => ({ name, ...entry })),
        null,
        2
      )
  )
}

printReport(taxonomy, skillNames.length, allEntries)

console.log(`\nTaxonomy written to: ${TAXONOMY_PATH}`)
