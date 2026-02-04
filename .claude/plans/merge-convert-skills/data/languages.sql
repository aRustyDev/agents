-- Convert Skills Language Database Extension
-- Task: ai-p28.15
-- Purpose: Extended schema for comprehensive language profile data
-- Generated: 2024-02-04
--
-- This file extends the base schema.sql with:
--   - language_versions: Version history for major languages
--   - language_ecosystem: Tooling and ecosystem data
--   - language_relationships: Language connections (influence, compilation, FFI)
--   - convert_skills: Skill coverage tracking
--
-- Use: sqlite3 patterns.db < languages.sql
-- Note: Run schema.sql first to create base tables

-- ============================================================================
-- NEW TABLES
-- ============================================================================

-- Version history for major languages
-- Tracks significant versions with conversion-relevant notes
DROP TABLE IF EXISTS language_versions;
CREATE TABLE language_versions (
    language_id TEXT NOT NULL,
    version TEXT NOT NULL,
    release_year INTEGER,
    release_date TEXT,           -- More precise than year when available
    status TEXT,                 -- legacy, lts, baseline, current, latest_stable, etc.
    key_features TEXT,           -- JSON array of notable features
    is_lts BOOLEAN DEFAULT FALSE,
    conversion_notes TEXT,       -- JSON array of conversion-relevant notes
    PRIMARY KEY (language_id, version)
);

CREATE INDEX idx_lang_versions_status ON language_versions(status);
CREATE INDEX idx_lang_versions_lts ON language_versions(is_lts);

-- Language ecosystem and tooling
-- Captures package managers, build tools, LSP servers, formatters, etc.
DROP TABLE IF EXISTS language_ecosystem;
CREATE TABLE language_ecosystem (
    language_id TEXT PRIMARY KEY,
    package_managers TEXT,       -- JSON array
    build_tools TEXT,            -- JSON array
    lsp_servers TEXT,            -- JSON array
    formatters TEXT,             -- JSON array
    linters TEXT,                -- JSON array
    repls TEXT,                  -- JSON array
    test_frameworks TEXT         -- JSON array
);

-- Language relationships
-- Captures influence, compilation targets, FFI, and superset relationships
DROP TABLE IF EXISTS language_relationships;
CREATE TABLE language_relationships (
    source_language_id TEXT NOT NULL,
    target_language_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,  -- 'influenced_by', 'compiles_to', 'ffi', 'superset_of', 'interop', 'runtime_target'
    targets TEXT,                     -- JSON array for compilation targets, platforms, etc.
    notes TEXT,
    PRIMARY KEY (source_language_id, target_language_id, relationship_type)
);

CREATE INDEX idx_lang_rel_type ON language_relationships(relationship_type);
CREATE INDEX idx_lang_rel_source ON language_relationships(source_language_id);
CREATE INDEX idx_lang_rel_target ON language_relationships(target_language_id);

-- Convert-* skill coverage tracking
-- Records all convert-X-Y skills and their status
DROP TABLE IF EXISTS convert_skills;
CREATE TABLE convert_skills (
    id TEXT PRIMARY KEY,              -- Format: source-target (e.g., python-rust)
    source_language_id TEXT NOT NULL,
    target_language_id TEXT NOT NULL,
    skill_path TEXT,                  -- Path to SKILL.md if exists
    pattern_count INTEGER DEFAULT 0,  -- Number of patterns extracted
    status TEXT DEFAULT 'active',     -- active, planned, deprecated
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_convert_skills_source ON convert_skills(source_language_id);
CREATE INDEX idx_convert_skills_target ON convert_skills(target_language_id);
CREATE INDEX idx_convert_skills_status ON convert_skills(status);

-- Language concurrency models
-- Captures concurrency primitives and patterns for languages with notable models
DROP TABLE IF EXISTS language_concurrency;
CREATE TABLE language_concurrency (
    language_id TEXT PRIMARY KEY,
    model_type TEXT,                 -- csp, actor, stm, async, threads, etc.
    primitives TEXT,                 -- JSON array of {name, description}
    patterns TEXT,                   -- JSON array of common patterns
    notes TEXT
);

-- Language-specific architectural patterns
-- For languages with notable architecture patterns (TEA, OTP, etc.)
DROP TABLE IF EXISTS language_architecture;
CREATE TABLE language_architecture (
    id INTEGER PRIMARY KEY,
    language_id TEXT NOT NULL,
    pattern_name TEXT NOT NULL,
    description TEXT,
    components TEXT,                 -- JSON array of {name, description}
    UNIQUE(language_id, pattern_name)
);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Languages with ecosystem summary
DROP VIEW IF EXISTS v_language_ecosystem;
CREATE VIEW v_language_ecosystem AS
SELECT
    l.name as language,
    l.tier,
    le.package_managers,
    le.build_tools,
    le.lsp_servers,
    le.formatters
FROM languages l
LEFT JOIN language_ecosystem le ON l.name = le.language_id;

-- View: Language version summary
DROP VIEW IF EXISTS v_language_versions;
CREATE VIEW v_language_versions AS
SELECT
    language_id,
    COUNT(*) as version_count,
    GROUP_CONCAT(version, ', ') as versions,
    MAX(CASE WHEN is_lts THEN version END) as latest_lts
FROM language_versions
GROUP BY language_id;

-- View: Language compilation targets
DROP VIEW IF EXISTS v_compilation_targets;
CREATE VIEW v_compilation_targets AS
SELECT
    source_language_id as language,
    target_language_id as target,
    targets,
    notes
FROM language_relationships
WHERE relationship_type = 'compiles_to';

-- View: Skill coverage matrix
DROP VIEW IF EXISTS v_convert_skill_matrix;
CREATE VIEW v_convert_skill_matrix AS
SELECT
    cs.source_language_id as source,
    cs.target_language_id as target,
    cs.id as skill_id,
    cs.pattern_count,
    cs.status
FROM convert_skills cs
ORDER BY cs.source_language_id, cs.target_language_id;

-- View: Language skill summary
DROP VIEW IF EXISTS v_language_skill_summary;
CREATE VIEW v_language_skill_summary AS
SELECT
    l.name as language,
    l.tier,
    (SELECT COUNT(*) FROM convert_skills WHERE source_language_id = l.name) as skills_as_source,
    (SELECT COUNT(*) FROM convert_skills WHERE target_language_id = l.name) as skills_as_target,
    (SELECT SUM(pattern_count) FROM convert_skills WHERE source_language_id = l.name OR target_language_id = l.name) as total_patterns
FROM languages l;

-- ============================================================================
-- DATA: Language Versions
-- ============================================================================

-- Python version history
INSERT OR REPLACE INTO language_versions (language_id, version, release_year, release_date, status, is_lts, conversion_notes) VALUES
('python', '2.7', 2010, '2010-07', 'legacy', FALSE, '["print statement vs function", "unicode vs str handling", "/ integer division", "dict.keys() returns list"]'),
('python', '3.6', 2016, '2016-12', 'baseline_modern', FALSE, '["f-strings introduced", "async/await stabilized", "type hints expanded (PEP 526)", "dict maintains insertion order"]'),
('python', '3.10', 2021, '2021-10', 'current_reference', FALSE, '["Pattern matching (match/case)", "Union types X | Y syntax", "ParamSpec for typing"]'),
('python', '3.12', 2023, '2023-10', 'latest_stable', FALSE, '["Type parameter syntax (PEP 695)", "f-string improvements", "Per-interpreter GIL (PEP 684)"]');

-- Java version history
INSERT OR REPLACE INTO language_versions (language_id, version, release_year, release_date, status, is_lts, conversion_notes) VALUES
('java', '8', 2014, '2014-03', 'legacy_lts', TRUE, '["Lambdas and functional interfaces", "Stream API", "Optional", "Default methods in interfaces", "Method references"]'),
('java', '11', 2018, '2018-09', 'lts', TRUE, '["var for local variables", "HTTP Client API", "Collection factory methods (List.of)", "String improvements"]'),
('java', '17', 2021, '2021-09', 'lts', TRUE, '["Sealed classes", "Pattern matching for instanceof", "Records", "Text blocks", "Switch expressions"]'),
('java', '21', 2023, '2023-09', 'latest_lts', TRUE, '["Virtual threads", "Record patterns", "Pattern matching for switch", "Sequenced collections", "String templates (preview)"]');

-- C version history
INSERT OR REPLACE INTO language_versions (language_id, version, release_year, release_date, status, is_lts, conversion_notes) VALUES
('c', 'C89', 1989, '1989', 'legacy', FALSE, '["K&R to ANSI function declarations", "No // comments", "No inline"]'),
('c', 'C99', 1999, '1999', 'common_baseline', FALSE, '["// comments", "inline functions", "designated initializers", "_Bool type", "variable-length arrays (VLAs)"]'),
('c', 'C11', 2011, '2011', 'modern_baseline', FALSE, '["_Generic type selection", "_Static_assert", "Threading support (<threads.h>)", "_Atomic qualifier"]'),
('c', 'C23', 2023, '2023', 'latest_stable', FALSE, '["typeof operator", "constexpr objects", "#embed directive", "Improved Unicode support"]');

-- C++ version history
INSERT OR REPLACE INTO language_versions (language_id, version, release_year, release_date, status, is_lts, conversion_notes) VALUES
('cpp', 'C++11', 2011, '2011', 'modern_baseline', FALSE, '["Move semantics", "auto type inference", "Lambda expressions", "Smart pointers (unique_ptr, shared_ptr)", "Range-based for"]'),
('cpp', 'C++17', 2017, '2017', 'common_modern', FALSE, '["Structured bindings", "if constexpr", "std::optional, std::variant", "Fold expressions"]'),
('cpp', 'C++20', 2020, '2020', 'latest_major', FALSE, '["Concepts", "Ranges", "Coroutines", "Modules", "Three-way comparison (<=>)"]'),
('cpp', 'C++23', 2023, '2023', 'latest_stable', FALSE, '["std::expected", "deducing this", "import std", "std::print"]');

-- Fortran version history (Tier 3)
INSERT OR REPLACE INTO language_versions (language_id, version, release_year, release_date, status, is_lts, conversion_notes) VALUES
('fortran', 'FORTRAN 77', 1978, '1978', 'legacy', FALSE, '["Fixed-form source", "Structured programming"]'),
('fortran', 'Fortran 90', 1991, '1991', 'baseline', FALSE, '["Free-form source", "Modules", "Array operations"]'),
('fortran', 'Fortran 2018', 2018, '2018', 'current', FALSE, '["Coarray parallelism", "Enhanced parallel features"]');

-- Ada version history (Tier 3)
INSERT OR REPLACE INTO language_versions (language_id, version, release_year, release_date, status, is_lts, conversion_notes) VALUES
('ada', 'Ada 83', 1983, '1983', 'legacy', FALSE, '["Original standard"]'),
('ada', 'Ada 95', 1995, '1995', 'baseline', FALSE, '["OOP support", "Protected types"]'),
('ada', 'Ada 2012', 2012, '2012', 'current', FALSE, '["Contracts", "Iterators"]'),
('ada', 'Ada 2022', 2022, '2022', 'latest', FALSE, '["Parallel blocks"]');

-- ============================================================================
-- DATA: Language Ecosystem
-- ============================================================================

INSERT OR REPLACE INTO language_ecosystem (language_id, package_managers, build_tools, lsp_servers, formatters, linters, repls, test_frameworks) VALUES
-- Tier 1 Languages
('python', '["pip", "uv", "poetry"]', '["setuptools", "hatch", "flit"]', '["pylsp", "pyright"]', '["black", "ruff"]', '["ruff", "flake8", "pylint"]', '["python", "ipython", "jupyter"]', '["pytest", "unittest"]'),
('typescript', '["npm", "pnpm", "yarn", "bun"]', '["tsc", "esbuild", "swc", "vite"]', '["typescript-language-server"]', '["prettier", "biome"]', '["eslint", "biome"]', '["ts-node", "tsx", "bun"]', '["jest", "vitest", "mocha"]'),
('rust', '["Cargo"]', '["Cargo"]', '["rust-analyzer"]', '["rustfmt"]', '["clippy"]', '["evcxr"]', '["built-in"]'),
('golang', '["go mod"]', '["go build"]', '["gopls"]', '["gofmt"]', '["golangci-lint"]', '["gore"]', '["testing"]'),
('java', '["Maven", "Gradle"]', '["Maven", "Gradle", "Bazel"]', '["Eclipse JDT LS"]', '["google-java-format"]', '["SpotBugs", "Error Prone"]', '["JShell"]', '["JUnit", "TestNG"]'),
('scala', '["sbt", "Mill", "Maven", "Gradle"]', '["sbt", "Mill"]', '["Metals"]', '["scalafmt"]', '["scalafix", "Wartremover"]', '["scala", "Ammonite"]', '["ScalaTest", "MUnit", "specs2"]'),
('haskell', '["Cabal", "Stack"]', '["Cabal", "Stack", "Nix"]', '["HLS"]', '["Ormolu", "Fourmolu", "stylish-haskell"]', '["HLint"]', '["GHCi"]', '["Hspec", "Tasty", "QuickCheck"]'),
('roc', '["roc"]', '["roc build"]', '["roc built-in"]', '["roc format"]', '[]', '["roc repl"]', '["roc test"]'),
('fsharp', '["NuGet", "Paket"]', '["dotnet CLI", "FAKE"]', '["Ionide", "FsAutoComplete"]', '["Fantomas"]', '["FSharpLint"]', '["fsi"]', '["Expecto", "xUnit", "NUnit"]'),
('elm', '["elm"]', '["elm make", "elm-live"]', '["elm-language-server"]', '["elm-format"]', '["elm-review"]', '["elm repl"]', '["elm-test"]'),
('c', '["none", "vcpkg", "Conan"]', '["Make", "CMake", "Meson"]', '["clangd"]', '["clang-format"]', '["clang-tidy", "cppcheck"]', '[]', '["Unity", "Check", "CUnit"]'),
('cpp', '["vcpkg", "Conan"]', '["CMake", "Meson", "Bazel"]', '["clangd"]', '["clang-format"]', '["clang-tidy"]', '["Cling"]', '["Google Test", "Catch2"]'),
('elixir', '["Hex", "Mix"]', '["Mix"]', '["ElixirLS", "lexical"]', '["mix format"]', '["Credo"]', '["IEx"]', '["ExUnit"]'),
('erlang', '["Hex", "rebar3"]', '["rebar3", "erlang.mk"]', '["erlang_ls"]', '["erlfmt"]', '["elvis"]', '["erl"]', '["EUnit", "Common Test"]'),
('clojure', '["Leiningen", "deps.edn"]', '["Leiningen", "tools.deps"]', '["clojure-lsp"]', '["cljfmt", "zprint"]', '["clj-kondo"]', '["built-in"]', '["clojure.test"]'),
('swift', '["Swift Package Manager"]', '["Xcode", "SwiftPM"]', '["SourceKit-LSP"]', '["swift-format"]', '["SwiftLint"]', '["swift"]', '["XCTest"]'),
('objc', '["CocoaPods", "Carthage", "SPM"]', '["Xcode"]', '["SourceKit-LSP"]', '["clang-format"]', '["OCLint"]', '[]', '["XCTest"]'),

-- Tier 2 Languages
('javascript', '["npm", "pnpm", "yarn", "bun"]', '["webpack", "vite", "esbuild", "rollup"]', '["typescript-language-server"]', '["prettier", "biome"]', '["eslint", "biome"]', '["node", "deno", "bun", "browser console"]', '["jest", "vitest", "mocha"]'),
('kotlin', '["Gradle", "Maven"]', '["Gradle"]', '["Kotlin Language Server"]', '["ktlint", "detekt"]', '["detekt"]', '["kotlin", "ki"]', '["JUnit", "Kotest"]'),
('gleam', '["gleam"]', '["gleam build"]', '["gleam lsp"]', '["gleam format"]', '[]', '[]', '["gleeunit"]'),
('ruby', '["RubyGems", "Bundler"]', '["Rake"]', '["Solargraph", "ruby-lsp"]', '["RuboCop"]', '["RuboCop"]', '["irb", "pry"]', '["RSpec", "Minitest"]'),
('zig', '["zig"]', '["zig build"]', '["zls"]', '["zig fmt"]', '[]', '[]', '["built-in"]');

-- ============================================================================
-- DATA: Language Relationships (Compilation Targets)
-- ============================================================================

-- Compilation targets
INSERT OR REPLACE INTO language_relationships (source_language_id, target_language_id, relationship_type, targets, notes) VALUES
-- Systems languages -> native
('rust', 'native', 'compiles_to', '["LLVM", "multiple architectures"]', NULL),
('rust', 'wasm', 'compiles_to', '["WebAssembly"]', NULL),
('c', 'native', 'compiles_to', '["machine code for all major architectures"]', NULL),
('cpp', 'native', 'compiles_to', '["machine code for all major architectures"]', NULL),
('golang', 'native', 'compiles_to', '["multiple OS/arch via GOOS/GOARCH"]', NULL),
('zig', 'native', 'compiles_to', '["LLVM", "multiple architectures"]', NULL),
('zig', 'c', 'compiles_to', '["C source code"]', 'Can output C source'),

-- JVM languages
('java', 'jvm', 'compiles_to', '["JVM bytecode"]', NULL),
('java', 'native', 'compiles_to', '["GraalVM native-image"]', NULL),
('scala', 'jvm', 'compiles_to', '["JVM bytecode"]', NULL),
('scala', 'javascript', 'compiles_to', '["Scala.js"]', NULL),
('scala', 'native', 'compiles_to', '["Scala Native"]', NULL),
('kotlin', 'jvm', 'compiles_to', '["JVM bytecode"]', NULL),
('kotlin', 'javascript', 'compiles_to', '["Kotlin/JS"]', NULL),
('kotlin', 'native', 'compiles_to', '["Kotlin/Native via LLVM"]', NULL),
('clojure', 'jvm', 'compiles_to', '["JVM bytecode"]', NULL),
('clojure', 'javascript', 'compiles_to', '["ClojureScript"]', NULL),
('clojure', 'dotnet', 'compiles_to', '["ClojureCLR"]', NULL),

-- BEAM languages
('elixir', 'beam', 'compiles_to', '["BEAM bytecode"]', NULL),
('erlang', 'beam', 'compiles_to', '["BEAM bytecode"]', NULL),
('gleam', 'beam', 'compiles_to', '["BEAM bytecode"]', NULL),
('gleam', 'javascript', 'compiles_to', '["JavaScript"]', NULL),

-- ML-FP languages
('haskell', 'native', 'compiles_to', '["GHC native codegen", "LLVM"]', NULL),
('haskell', 'javascript', 'compiles_to', '["GHCJS"]', NULL),
('fsharp', 'dotnet-il', 'compiles_to', '[".NET IL"]', NULL),
('fsharp', 'javascript', 'compiles_to', '["Fable"]', NULL),
('elm', 'javascript', 'compiles_to', '["JavaScript (ES5)"]', NULL),
('roc', 'native', 'compiles_to', '["LLVM"]', NULL),
('roc', 'wasm', 'compiles_to', '["WebAssembly"]', NULL),

-- Apple languages
('swift', 'native', 'compiles_to', '["LLVM", "Apple platforms", "Linux", "Windows"]', NULL),
('objc', 'native', 'compiles_to', '["LLVM", "Apple platforms"]', NULL),

-- TypeScript/JavaScript relationship
('typescript', 'javascript', 'compiles_to', '["ES3", "ES5", "ES6", "ES2015-ES2022", "ESNext"]', 'Type erasure during compilation'),

-- Dynamic languages (interpreted)
('python', 'bytecode', 'compiles_to', '["CPython bytecode"]', NULL),
('ruby', 'bytecode', 'compiles_to', '["YARV"]', NULL),
('ruby', 'native', 'compiles_to', '["TruffleRuby", "mruby"]', NULL),
('javascript', 'bytecode', 'compiles_to', '["V8", "SpiderMonkey", "JavaScriptCore"]', NULL);

-- FFI/Interop relationships
INSERT OR REPLACE INTO language_relationships (source_language_id, target_language_id, relationship_type, targets, notes) VALUES
('c', 'universal', 'ffi', '["C ABI"]', 'Universal FFI baseline - most languages interface with C ABI'),
('zig', 'c', 'ffi', '["cImport", "link C libraries"]', 'Seamless C interop'),
('kotlin', 'java', 'interop', '["full bidirectional"]', 'Full Java interop'),
('typescript', 'javascript', 'superset_of', '[]', 'TypeScript is a typed superset of JavaScript');

-- ============================================================================
-- DATA: Convert Skills
-- ============================================================================

-- All documented convert-* skills from YAML profiles
INSERT OR REPLACE INTO convert_skills (id, source_language_id, target_language_id, pattern_count, status, notes) VALUES
-- Python as source (11 skills)
('python-clojure', 'python', 'clojure', 0, 'active', NULL),
('python-elixir', 'python', 'elixir', 0, 'active', NULL),
('python-elm', 'python', 'elm', 0, 'active', NULL),
('python-erlang', 'python', 'erlang', 0, 'active', NULL),
('python-fsharp', 'python', 'fsharp', 0, 'active', NULL),
('python-golang', 'python', 'golang', 0, 'active', NULL),
('python-haskell', 'python', 'haskell', 0, 'active', NULL),
('python-roc', 'python', 'roc', 0, 'active', NULL),
('python-rust', 'python', 'rust', 958, 'active', 'Has extracted patterns'),
('python-scala', 'python', 'scala', 0, 'active', NULL),
('python-typescript', 'python', 'typescript', 411, 'active', 'Has extracted patterns'),

-- TypeScript as source (2 skills)
('typescript-golang', 'typescript', 'golang', 229, 'active', 'Has extracted patterns'),
('typescript-rust', 'typescript', 'rust', 0, 'active', NULL),

-- Scala as target only (8 skills) - captured by above

-- Haskell as source (2 skills)
('haskell-roc', 'haskell', 'roc', 0, 'active', NULL),
('haskell-scala', 'haskell', 'scala', 0, 'active', NULL),

-- F# as source (3 skills)
('fsharp-haskell', 'fsharp', 'haskell', 0, 'active', NULL),
('fsharp-roc', 'fsharp', 'roc', 0, 'active', NULL),
('fsharp-scala', 'fsharp', 'scala', 0, 'active', NULL),

-- Elm as source (5 skills)
('elm-erlang', 'elm', 'erlang', 0, 'active', NULL),
('elm-fsharp', 'elm', 'fsharp', 0, 'active', NULL),
('elm-haskell', 'elm', 'haskell', 0, 'active', NULL),
('elm-roc', 'elm', 'roc', 0, 'active', NULL),
('elm-scala', 'elm', 'scala', 0, 'active', NULL),

-- Rust as target only (6 skills) - captured by above

-- C as source (2 skills)
('c-cpp', 'c', 'cpp', 268, 'active', 'Has extracted patterns'),
('c-rust', 'c', 'rust', 346, 'active', 'Has extracted patterns'),

-- C++ as source (1 skill)
('cpp-rust', 'cpp', 'rust', 0, 'active', NULL),

-- Golang as source (1 skill)
('golang-rust', 'golang', 'rust', 0, 'active', NULL),

-- Elixir as source (6 skills)
('elixir-elm', 'elixir', 'elm', 0, 'active', NULL),
('elixir-erlang', 'elixir', 'erlang', 0, 'active', NULL),
('elixir-fsharp', 'elixir', 'fsharp', 0, 'active', NULL),
('elixir-haskell', 'elixir', 'haskell', 0, 'active', NULL),
('elixir-roc', 'elixir', 'roc', 0, 'active', NULL),
('elixir-scala', 'elixir', 'scala', 0, 'active', NULL),

-- Erlang as source (4 skills)
('erlang-fsharp', 'erlang', 'fsharp', 0, 'active', NULL),
('erlang-haskell', 'erlang', 'haskell', 0, 'active', NULL),
('erlang-roc', 'erlang', 'roc', 0, 'active', NULL),
('erlang-scala', 'erlang', 'scala', 0, 'active', NULL),

-- Clojure as source (7 skills)
('clojure-elixir', 'clojure', 'elixir', 0, 'active', NULL),
('clojure-elm', 'clojure', 'elm', 0, 'active', NULL),
('clojure-erlang', 'clojure', 'erlang', 0, 'active', NULL),
('clojure-fsharp', 'clojure', 'fsharp', 0, 'active', NULL),
('clojure-haskell', 'clojure', 'haskell', 0, 'active', NULL),
('clojure-roc', 'clojure', 'roc', 0, 'active', NULL),
('clojure-scala', 'clojure', 'scala', 0, 'active', NULL),

-- Java as source (3 skills)
('java-c', 'java', 'c', 346, 'active', 'Has extracted patterns'),
('java-cpp', 'java', 'cpp', 268, 'active', 'Has extracted patterns'),
('java-rust', 'java', 'rust', 447, 'active', 'Has extracted patterns'),

-- Objective-C as source (1 skill)
('objc-swift', 'objc', 'swift', 193, 'active', 'Has extracted patterns'),

-- Roc as source (1 skill)
('roc-scala', 'roc', 'scala', 0, 'active', NULL);

-- ============================================================================
-- DATA: Concurrency Models
-- ============================================================================

INSERT OR REPLACE INTO language_concurrency (language_id, model_type, primitives, patterns, notes) VALUES
('golang', 'csp', '[{"name": "goroutine", "description": "Lightweight thread managed by Go runtime"}, {"name": "channel", "description": "Typed conduit for communication between goroutines"}, {"name": "select", "description": "Wait on multiple channel operations"}]', '["Worker pool", "Fan-in/fan-out", "Pipeline", "Context cancellation"]', 'CSP-based concurrency'),
('elixir', 'actor', '[{"name": "process", "description": "Lightweight isolated process"}, {"name": "message", "description": "Async message passing"}, {"name": "GenServer", "description": "Generic server behaviour"}, {"name": "Supervisor", "description": "Process supervisor"}]', '["Supervision trees", "GenServer state machines", "Task async/await", "Agent state management"]', 'BEAM actor model'),
('erlang', 'actor', '[{"name": "process", "description": "Lightweight isolated process (can have millions)"}, {"name": "message", "description": "Async message passing (send, receive)"}, {"name": "link", "description": "Bidirectional failure propagation"}, {"name": "monitor", "description": "Unidirectional process monitoring"}]', '["Let it crash", "Supervision trees", "Hot code reloading", "Distribution"]', 'OTP actor model'),
('clojure', 'stm', '[{"name": "atom", "description": "Synchronous, uncoordinated state"}, {"name": "ref", "description": "Synchronous, coordinated state (STM)"}, {"name": "agent", "description": "Asynchronous, uncoordinated state"}, {"name": "var", "description": "Thread-local state"}]', '["STM transactions", "core.async channels"]', 'STM + optional CSP via core.async'),
('ruby', 'mixed', '[{"name": "Thread", "description": "OS-level thread (GIL limited)"}, {"name": "Fiber", "description": "Coroutines/lightweight threads"}, {"name": "Ractor", "description": "Actor-like parallel execution (Ruby 3+)"}]', '[]', 'GIL limits true parallelism; Ractors enable parallelism');

-- ============================================================================
-- DATA: Architecture Patterns
-- ============================================================================

INSERT OR REPLACE INTO language_architecture (language_id, pattern_name, description, components) VALUES
('elm', 'The Elm Architecture (TEA)', 'Unidirectional data flow architecture for web applications', '[{"name": "Model", "description": "Application state"}, {"name": "Msg", "description": "Message type for state changes"}, {"name": "update", "description": "State transition function"}, {"name": "view", "description": "Render function"}, {"name": "subscriptions", "description": "External event sources"}]'),
('roc', 'Platform Model', 'Separates pure application from effectful platform', '[{"name": "Application", "description": "Pure code describing effects"}, {"name": "Platform", "description": "Effectful code executing effects"}]');

-- ============================================================================
-- SUMMARY STATISTICS
-- ============================================================================

-- Summary view for quick stats
DROP VIEW IF EXISTS v_schema_stats;
CREATE VIEW v_schema_stats AS
SELECT
    (SELECT COUNT(*) FROM language_versions) as version_records,
    (SELECT COUNT(DISTINCT language_id) FROM language_versions) as languages_with_versions,
    (SELECT COUNT(*) FROM language_ecosystem) as ecosystem_records,
    (SELECT COUNT(*) FROM language_relationships) as relationship_records,
    (SELECT COUNT(*) FROM convert_skills) as skill_records,
    (SELECT COUNT(*) FROM language_concurrency) as concurrency_records,
    (SELECT COUNT(*) FROM language_architecture) as architecture_records;
