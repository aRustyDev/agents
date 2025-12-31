// ============================================================================
// Conversion Difficulty Matrix - Neo4j Graph Model
// ============================================================================
// Single source of truth for language pair conversion difficulty ratings.
//
// Graph Structure:
//   (Language)-[:CONVERTS_TO {scores...}]->(Language)
//   (Language)-[:RUNS_ON]->(Platform)
//   (Language)-[:HAS_TYPE_SYSTEM]->(TypeSystem)
//   (Language)-[:HAS_PARADIGM]->(Paradigm)
//   (Language)-[:HAS_MEMORY_MODEL]->(MemoryModel)
//   (Language)-[:HAS_CONCURRENCY_MODEL]->(ConcurrencyModel)
//
// Usage:
//   cat difficulty.cypher | cypher-shell -u neo4j -p password
//   OR import via Neo4j Browser
// ============================================================================

// ----------------------------------------------------------------------------
// CONSTRAINTS & INDEXES
// ----------------------------------------------------------------------------

CREATE CONSTRAINT language_name IF NOT EXISTS FOR (l:Language) REQUIRE l.name IS UNIQUE;
CREATE CONSTRAINT platform_name IF NOT EXISTS FOR (p:Platform) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT difficulty_level IF NOT EXISTS FOR (d:DifficultyLevel) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT type_system_name IF NOT EXISTS FOR (t:TypeSystem) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT paradigm_name IF NOT EXISTS FOR (p:Paradigm) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT memory_model_name IF NOT EXISTS FOR (m:MemoryModel) REQUIRE m.name IS UNIQUE;
CREATE CONSTRAINT concurrency_model_name IF NOT EXISTS FOR (c:ConcurrencyModel) REQUIRE c.name IS UNIQUE;

CREATE INDEX language_family IF NOT EXISTS FOR (l:Language) ON (l.family);

// ----------------------------------------------------------------------------
// DIFFICULTY LEVELS
// ----------------------------------------------------------------------------

CREATE (easy:DifficultyLevel {
  name: 'Easy',
  minScore: 0,
  maxScore: 2,
  expectedSkillSize: '200-400 lines',
  focusAreas: ['Idiom differences', 'Library mapping']
});

CREATE (medium:DifficultyLevel {
  name: 'Medium',
  minScore: 3,
  maxScore: 5,
  expectedSkillSize: '400-800 lines',
  focusAreas: ['Type translation', 'Paradigm shifts']
});

CREATE (hard:DifficultyLevel {
  name: 'Hard',
  minScore: 6,
  maxScore: 8,
  expectedSkillSize: '800-1200 lines',
  focusAreas: ['Memory model', 'Concurrency', 'Architecture']
});

CREATE (expert:DifficultyLevel {
  name: 'Expert',
  minScore: 9,
  maxScore: 10,
  expectedSkillSize: '1200+ lines',
  focusAreas: ['Complete paradigm shift', 'All factors differ']
});

// ----------------------------------------------------------------------------
// TYPE SYSTEMS
// ----------------------------------------------------------------------------

CREATE (:TypeSystem {name: 'Static', description: 'Compile-time type checking'});
CREATE (:TypeSystem {name: 'Dynamic', description: 'Runtime type checking'});
CREATE (:TypeSystem {name: 'Static-HM', description: 'Hindley-Milner type inference'});

// ----------------------------------------------------------------------------
// PARADIGMS
// ----------------------------------------------------------------------------

CREATE (:Paradigm {name: 'Imperative'});
CREATE (:Paradigm {name: 'OOP', description: 'Object-Oriented Programming'});
CREATE (:Paradigm {name: 'Functional'});
CREATE (:Paradigm {name: 'PureFP', description: 'Pure Functional Programming'});
CREATE (:Paradigm {name: 'Multi', description: 'Multi-paradigm'});
CREATE (:Paradigm {name: 'MultiFP', description: 'Multi-paradigm with FP focus'});
CREATE (:Paradigm {name: 'MultiOOP', description: 'Multi-paradigm with OOP focus'});

// ----------------------------------------------------------------------------
// MEMORY MODELS
// ----------------------------------------------------------------------------

CREATE (:MemoryModel {name: 'Manual', description: 'Manual memory management'});
CREATE (:MemoryModel {name: 'GC', description: 'Garbage collected'});
CREATE (:MemoryModel {name: 'Ownership', description: 'Ownership and borrowing (Rust)'});
CREATE (:MemoryModel {name: 'ARC', description: 'Automatic Reference Counting'});
CREATE (:MemoryModel {name: 'RAII', description: 'Resource Acquisition Is Initialization'});

// ----------------------------------------------------------------------------
// CONCURRENCY MODELS
// ----------------------------------------------------------------------------

CREATE (:ConcurrencyModel {name: 'Threads', description: 'OS threads'});
CREATE (:ConcurrencyModel {name: 'Actors', description: 'Actor model (Erlang/Elixir)'});
CREATE (:ConcurrencyModel {name: 'CSP', description: 'Communicating Sequential Processes (Go)'});
CREATE (:ConcurrencyModel {name: 'STM', description: 'Software Transactional Memory'});
CREATE (:ConcurrencyModel {name: 'Async', description: 'Async/await'});
CREATE (:ConcurrencyModel {name: 'Promises', description: 'Promise-based (JavaScript)'});
CREATE (:ConcurrencyModel {name: 'GCD', description: 'Grand Central Dispatch (Apple)'});
CREATE (:ConcurrencyModel {name: 'TEA', description: 'The Elm Architecture'});
CREATE (:ConcurrencyModel {name: 'Effects', description: 'Effect system (Roc)'});

// ----------------------------------------------------------------------------
// PLATFORMS
// ----------------------------------------------------------------------------

CREATE (:Platform {name: 'Native', description: 'Compiles to native code'});
CREATE (:Platform {name: 'JVM', description: 'Java Virtual Machine'});
CREATE (:Platform {name: 'BEAM', description: 'Erlang VM'});
CREATE (:Platform {name: 'JS', description: 'JavaScript runtime'});
CREATE (:Platform {name: '.NET', description: '.NET CLR'});
CREATE (:Platform {name: 'Apple', description: 'Apple platforms (iOS, macOS)'});
CREATE (:Platform {name: 'Interpreted', description: 'Interpreted runtime'});

// ----------------------------------------------------------------------------
// LANGUAGES
// ----------------------------------------------------------------------------

// Systems Languages
CREATE (c:Language {
  name: 'C',
  family: 'Systems',
  typeSystem: 'Static',
  paradigm: 'Imperative',
  memory: 'Manual',
  concurrency: 'Threads',
  platform: 'Native'
});

CREATE (cpp:Language {
  name: 'C++',
  family: 'Systems',
  typeSystem: 'Static',
  paradigm: 'MultiOOP',
  memory: 'Manual/RAII',
  concurrency: 'Threads',
  platform: 'Native'
});

CREATE (rust:Language {
  name: 'Rust',
  family: 'Systems',
  typeSystem: 'Static',
  paradigm: 'Multi',
  memory: 'Ownership',
  concurrency: 'Async/Threads',
  platform: 'Native'
});

CREATE (go:Language {
  name: 'Go',
  family: 'Systems',
  typeSystem: 'Static',
  paradigm: 'Imperative',
  memory: 'GC',
  concurrency: 'CSP',
  platform: 'Native'
});

// JVM Languages
CREATE (java:Language {
  name: 'Java',
  family: 'JVM',
  typeSystem: 'Static',
  paradigm: 'OOP',
  memory: 'GC',
  concurrency: 'Threads',
  platform: 'JVM'
});

CREATE (scala:Language {
  name: 'Scala',
  family: 'JVM',
  typeSystem: 'Static',
  paradigm: 'MultiFP',
  memory: 'GC',
  concurrency: 'Actors/Async',
  platform: 'JVM'
});

CREATE (clojure:Language {
  name: 'Clojure',
  family: 'JVM',
  typeSystem: 'Dynamic',
  paradigm: 'Functional',
  memory: 'GC',
  concurrency: 'STM/Agents',
  platform: 'JVM',
  replCentric: true
});

// BEAM Languages
CREATE (erlang:Language {
  name: 'Erlang',
  family: 'BEAM',
  typeSystem: 'Dynamic',
  paradigm: 'Functional',
  memory: 'GC',
  concurrency: 'Actors',
  platform: 'BEAM',
  replCentric: true
});

CREATE (elixir:Language {
  name: 'Elixir',
  family: 'BEAM',
  typeSystem: 'Dynamic',
  paradigm: 'Functional',
  memory: 'GC',
  concurrency: 'Actors',
  platform: 'BEAM',
  replCentric: true
});

// Functional Languages
CREATE (haskell:Language {
  name: 'Haskell',
  family: 'Functional',
  typeSystem: 'Static-HM',
  paradigm: 'PureFP',
  memory: 'GC',
  concurrency: 'STM/Async',
  platform: 'Native',
  replCentric: true
});

CREATE (fsharp:Language {
  name: 'F#',
  family: 'Functional',
  typeSystem: 'Static',
  paradigm: 'Functional',
  memory: 'GC',
  concurrency: 'Async',
  platform: '.NET',
  replCentric: true
});

CREATE (elm:Language {
  name: 'Elm',
  family: 'Functional',
  typeSystem: 'Static',
  paradigm: 'PureFP',
  memory: 'GC',
  concurrency: 'TEA',
  platform: 'JS'
});

CREATE (roc:Language {
  name: 'Roc',
  family: 'Functional',
  typeSystem: 'Static',
  paradigm: 'PureFP',
  memory: 'GC',
  concurrency: 'Effects',
  platform: 'Native'
});

// Scripting / Multi-paradigm
CREATE (python:Language {
  name: 'Python',
  family: 'Scripting',
  typeSystem: 'Dynamic',
  paradigm: 'Multi',
  memory: 'GC',
  concurrency: 'Async/Threads',
  platform: 'Interpreted'
});

CREATE (typescript:Language {
  name: 'TypeScript',
  family: 'Scripting',
  typeSystem: 'Static',
  paradigm: 'Multi',
  memory: 'GC',
  concurrency: 'Promises',
  platform: 'JS'
});

// Apple Platform
CREATE (objc:Language {
  name: 'Objective-C',
  family: 'Apple',
  typeSystem: 'Static',
  paradigm: 'OOP',
  memory: 'ARC',
  concurrency: 'GCD',
  platform: 'Apple'
});

CREATE (swift:Language {
  name: 'Swift',
  family: 'Apple',
  typeSystem: 'Static',
  paradigm: 'Multi',
  memory: 'ARC',
  concurrency: 'GCD/Async',
  platform: 'Apple'
});

// ----------------------------------------------------------------------------
// LANGUAGE -> PLATFORM RELATIONSHIPS
// ----------------------------------------------------------------------------

MATCH (l:Language), (p:Platform) WHERE l.platform = p.name
CREATE (l)-[:RUNS_ON]->(p);

// ----------------------------------------------------------------------------
// CONVERSION RELATIONSHIPS - Functional Language Family
// ----------------------------------------------------------------------------

// Clojure conversions
MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Platform migration', 'STM to Actors']
}]->(tgt);

MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Dynamic to static', 'Pure FP shift']
}]->(tgt);

MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Platform migration', 'STM to Actors']
}]->(tgt);

MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Dynamic to static', 'Platform migration']
}]->(tgt);

MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Dynamic to static', 'Pure FP']
}]->(tgt);

MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Dynamic to static', 'Effects system']
}]->(tgt);

MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 0,
  totalScore: 1, level: 'Easy', challenges: ['Same platform (JVM)']
}]->(tgt);

// Elixir conversions
MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Platform migration', 'Actors to STM']
}]->(tgt);

MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Dynamic to static', 'Platform migration']
}]->(tgt);

MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 0, platformScore: 0,
  totalScore: 0, level: 'Easy', challenges: ['Same platform (BEAM)']
}]->(tgt);

MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Platform migration', 'Actors to Async']
}]->(tgt);

MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Dynamic to static', 'Pure FP']
}]->(tgt);

MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 2, platformScore: 2,
  totalScore: 6, level: 'Hard', challenges: ['Actors to Effects', 'BEAM to Native']
}]->(tgt);

MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Platform migration', 'BEAM to JVM']
}]->(tgt);

// Erlang conversions
MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Actors to STM', 'BEAM to JVM']
}]->(tgt);

MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 0, platformScore: 0,
  totalScore: 0, level: 'Easy', challenges: ['Same platform (BEAM)']
}]->(tgt);

MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Dynamic to static', 'Platform migration']
}]->(tgt);

MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Platform migration', 'Actors to Async']
}]->(tgt);

MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Dynamic to static', 'Pure FP']
}]->(tgt);

MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 2, platformScore: 2,
  totalScore: 6, level: 'Hard', challenges: ['Actors to Effects', 'BEAM to Native']
}]->(tgt);

MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['BEAM to JVM']
}]->(tgt);

// Elm conversions
MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Static to dynamic', 'Platform migration']
}]->(tgt);

MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Static to dynamic', 'TEA to Actors']
}]->(tgt);

MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Static to dynamic', 'Platform migration']
}]->(tgt);

MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 3, level: 'Medium', challenges: ['Platform migration']
}]->(tgt);

MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 3, level: 'Medium', challenges: ['Platform migration', 'Similar pure FP']
}]->(tgt);

MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 0, platformScore: 2,
  totalScore: 2, level: 'Easy', challenges: ['Both pure FP']
}]->(tgt);

MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Pure to multi-paradigm']
}]->(tgt);

// F# conversions
MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Static to dynamic', '.NET to JVM']
}]->(tgt);

MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Async to Actors', '.NET to BEAM']
}]->(tgt);

MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 3, level: 'Medium', challenges: ['Platform migration']
}]->(tgt);

MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Static to dynamic', '.NET to BEAM']
}]->(tgt);

MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 3, level: 'Medium', challenges: ['Platform migration']
}]->(tgt);

MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 3, level: 'Medium', challenges: ['Async to Effects']
}]->(tgt);

MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 3, level: 'Medium', challenges: ['.NET to JVM']
}]->(tgt);

// Haskell conversions
MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Static to dynamic', 'Pure to practical FP']
}]->(tgt);

MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Static to dynamic', 'STM to Actors']
}]->(tgt);

MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 3, level: 'Medium', challenges: ['Platform migration']
}]->(tgt);

MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Static to dynamic', 'STM to Actors']
}]->(tgt);

MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 3, level: 'Medium', challenges: ['Platform migration']
}]->(tgt);

MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 0,
  totalScore: 1, level: 'Easy', challenges: ['Similar pure FP', 'STM to Effects']
}]->(tgt);

MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Pure to multi-paradigm']
}]->(tgt);

// Roc conversions
MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Static to dynamic', 'Effects to STM']
}]->(tgt);

MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 2, platformScore: 2,
  totalScore: 6, level: 'Hard', challenges: ['Effects to Actors', 'Native to BEAM']
}]->(tgt);

MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 0, platformScore: 2,
  totalScore: 2, level: 'Easy', challenges: ['Both pure FP']
}]->(tgt);

MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 2, platformScore: 2,
  totalScore: 6, level: 'Hard', challenges: ['Effects to Actors', 'Native to BEAM']
}]->(tgt);

MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 3, level: 'Medium', challenges: ['Effects to Async']
}]->(tgt);

MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 0,
  totalScore: 1, level: 'Easy', challenges: ['Similar pure FP']
}]->(tgt);

MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Pure to multi-paradigm']
}]->(tgt);

// Scala conversions
MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 0,
  totalScore: 1, level: 'Easy', challenges: ['Same platform (JVM)']
}]->(tgt);

MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['JVM to BEAM']
}]->(tgt);

MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Multi to pure FP']
}]->(tgt);

MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['JVM to BEAM']
}]->(tgt);

MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 3, level: 'Medium', challenges: ['JVM to .NET']
}]->(tgt);

MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Multi to pure FP']
}]->(tgt);

MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Multi to pure FP']
}]->(tgt);

// ----------------------------------------------------------------------------
// CONVERSION RELATIONSHIPS - Python
// ----------------------------------------------------------------------------

MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Multi to functional', 'Interpreted to JVM']
}]->(tgt);

MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 1, memoryScore: 0, concurrencyScore: 2, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Asyncio to Actors', 'Interpreted to BEAM']
}]->(tgt);

MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 2, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 6, level: 'Hard', challenges: ['Dynamic to static', 'Multi to pure FP']
}]->(tgt);

MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 1, memoryScore: 0, concurrencyScore: 2, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Asyncio to Actors']
}]->(tgt);

MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Dynamic to static']
}]->(tgt);

MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Go'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 0, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Dynamic to static']
}]->(tgt);

MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 2, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 6, level: 'Hard', challenges: ['Dynamic to static', 'Multi to pure FP']
}]->(tgt);

MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 2, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 6, level: 'Hard', challenges: ['Dynamic to static', 'Multi to pure FP']
}]->(tgt);

MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Rust'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 2, concurrencyScore: 1, platformScore: 2,
  totalScore: 7, level: 'Hard', challenges: ['GC to Ownership', 'Dynamic to static']
}]->(tgt);

MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 1, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 5, level: 'Medium', challenges: ['Dynamic to static']
}]->(tgt);

MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'TypeScript'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 0, platformScore: 1,
  totalScore: 1, level: 'Easy', challenges: ['Similar multi-paradigm']
}]->(tgt);

// ----------------------------------------------------------------------------
// CONVERSION RELATIONSHIPS - TypeScript
// ----------------------------------------------------------------------------

MATCH (src:Language {name: 'TypeScript'}), (tgt:Language {name: 'Go'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 1, memoryScore: 0, concurrencyScore: 1, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['Promises to CSP']
}]->(tgt);

MATCH (src:Language {name: 'TypeScript'}), (tgt:Language {name: 'Python'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 0, platformScore: 1,
  totalScore: 1, level: 'Easy', challenges: ['Similar multi-paradigm']
}]->(tgt);

MATCH (src:Language {name: 'TypeScript'}), (tgt:Language {name: 'Rust'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 1, memoryScore: 2, concurrencyScore: 1, platformScore: 2,
  totalScore: 6, level: 'Hard', challenges: ['GC to Ownership', 'Platform migration']
}]->(tgt);

// ----------------------------------------------------------------------------
// CONVERSION RELATIONSHIPS - Systems Languages
// ----------------------------------------------------------------------------

MATCH (src:Language {name: 'C'}), (tgt:Language {name: 'C++'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 0, platformScore: 0,
  totalScore: 0, level: 'Easy', challenges: ['Same family']
}]->(tgt);

MATCH (src:Language {name: 'C'}), (tgt:Language {name: 'Rust'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 1, memoryScore: 1, concurrencyScore: 1, platformScore: 0,
  totalScore: 3, level: 'Medium', challenges: ['Manual to Ownership']
}]->(tgt);

MATCH (src:Language {name: 'C++'}), (tgt:Language {name: 'Rust'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 1, concurrencyScore: 0, platformScore: 0,
  totalScore: 1, level: 'Easy', challenges: ['Similar memory models (RAII)']
}]->(tgt);

MATCH (src:Language {name: 'Go'}), (tgt:Language {name: 'Rust'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 2, concurrencyScore: 1, platformScore: 0,
  totalScore: 3, level: 'Medium', challenges: ['GC to Ownership']
}]->(tgt);

MATCH (src:Language {name: 'Java'}), (tgt:Language {name: 'C'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 1, memoryScore: 2, concurrencyScore: 1, platformScore: 2,
  totalScore: 6, level: 'Hard', challenges: ['GC to Manual', 'JVM to Native']
}]->(tgt);

MATCH (src:Language {name: 'Java'}), (tgt:Language {name: 'C++'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 2, concurrencyScore: 0, platformScore: 2,
  totalScore: 4, level: 'Medium', challenges: ['GC to Manual/RAII']
}]->(tgt);

MATCH (src:Language {name: 'Java'}), (tgt:Language {name: 'Rust'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 1, memoryScore: 2, concurrencyScore: 1, platformScore: 2,
  totalScore: 6, level: 'Hard', challenges: ['GC to Ownership', 'JVM to Native']
}]->(tgt);

// ----------------------------------------------------------------------------
// CONVERSION RELATIONSHIPS - Platform-Specific
// ----------------------------------------------------------------------------

MATCH (src:Language {name: 'Objective-C'}), (tgt:Language {name: 'Swift'})
CREATE (src)-[:CONVERTS_TO {
  typeScore: 0, paradigmScore: 0, memoryScore: 0, concurrencyScore: 0, platformScore: 0,
  totalScore: 0, level: 'Easy', challenges: ['Same platform (Apple)']
}]->(tgt);

// ----------------------------------------------------------------------------
// USEFUL QUERIES
// ----------------------------------------------------------------------------

// Find all Easy conversions
// MATCH (src:Language)-[c:CONVERTS_TO {level: 'Easy'}]->(tgt:Language)
// RETURN src.name AS source, tgt.name AS target, c.totalScore AS score
// ORDER BY c.totalScore;

// Find all Hard conversions
// MATCH (src:Language)-[c:CONVERTS_TO]->(tgt:Language)
// WHERE c.totalScore >= 6
// RETURN src.name AS source, tgt.name AS target, c.totalScore AS score, c.challenges
// ORDER BY c.totalScore DESC;

// Find conversion path between two languages
// MATCH path = shortestPath((src:Language {name: 'Python'})-[:CONVERTS_TO*]->(tgt:Language {name: 'Rust'}))
// RETURN path;

// Find all conversions from a language, sorted by difficulty
// MATCH (src:Language {name: 'Python'})-[c:CONVERTS_TO]->(tgt:Language)
// RETURN tgt.name AS target, c.totalScore AS score, c.level, c.challenges
// ORDER BY c.totalScore;

// Find languages by platform
// MATCH (l:Language)-[:RUNS_ON]->(p:Platform {name: 'JVM'})
// RETURN l.name, l.paradigm, l.typeSystem;

// Find REPL-centric languages
// MATCH (l:Language) WHERE l.replCentric = true
// RETURN l.name, l.platform;

// Aggregate difficulty statistics
// MATCH ()-[c:CONVERTS_TO]->()
// RETURN c.level AS difficulty, count(*) AS count
// ORDER BY CASE c.level
//   WHEN 'Easy' THEN 1
//   WHEN 'Medium' THEN 2
//   WHEN 'Hard' THEN 3
//   WHEN 'Expert' THEN 4
// END;
