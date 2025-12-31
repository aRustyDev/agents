// ============================================================================
// Conversion Difficulty Matrix - Neo4j Graph Model
// ============================================================================
// Single source of truth for language pair conversion difficulty ratings.
//
// Graph Structure:
//   Score Relationships (direct):
//     (Language)-[:TYPE_DIFF {score: n}]->(Language)
//     (Language)-[:PARADIGM_DIFF {score: n}]->(Language)
//     (Language)-[:MEMORY_DIFF {score: n}]->(Language)
//     (Language)-[:CONCURRENCY_DIFF {score: n}]->(Language)
//     (Language)-[:PLATFORM_DIFF {score: n}]->(Language)
//
//   Challenge Mini-Hub:
//     (Language)-[:FACES]->(Challenge)-[:FOR]->(Language)
//
//   Language Characteristics:
//     (Language)-[:RUNS_ON]->(Platform)
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
CREATE CONSTRAINT challenge_id IF NOT EXISTS FOR (c:Challenge) REQUIRE c.id IS UNIQUE;

CREATE INDEX language_family IF NOT EXISTS FOR (l:Language) ON (l.family);
CREATE INDEX challenge_category IF NOT EXISTS FOR (c:Challenge) ON (c.category);

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
// HELPER: Create conversion scores and challenges
// ----------------------------------------------------------------------------
//
// This section creates:
//   1. Five direct score relationships per conversion pair
//   2. Challenge nodes connected via FACES/FOR relationships
//
// Score relationships: TYPE_DIFF, PARADIGM_DIFF, MEMORY_DIFF, CONCURRENCY_DIFF, PLATFORM_DIFF
// Challenge pattern: (src)-[:FACES]->(Challenge)-[:FOR]->(tgt)

// ============================================================================
// CLOJURE CONVERSIONS
// ============================================================================

// Clojure -> Elixir (Total: 4, Medium)
MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Elixir'})
CREATE (ch1:Challenge {id: 'clojure-elixir-1', text: 'Platform migration (JVM to BEAM)', category: 'Platform'}),
       (ch2:Challenge {id: 'clojure-elixir-2', text: 'STM to Actors concurrency model', category: 'Concurrency'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Clojure -> Elm (Total: 5, Medium)
MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Elm'})
CREATE (ch1:Challenge {id: 'clojure-elm-1', text: 'Dynamic to static typing', category: 'Type'}),
       (ch2:Challenge {id: 'clojure-elm-2', text: 'Shift to pure functional paradigm', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Clojure -> Erlang (Total: 4, Medium)
MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Erlang'})
CREATE (ch1:Challenge {id: 'clojure-erlang-1', text: 'Platform migration (JVM to BEAM)', category: 'Platform'}),
       (ch2:Challenge {id: 'clojure-erlang-2', text: 'STM to Actors concurrency model', category: 'Concurrency'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Clojure -> F# (Total: 4, Medium)
MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'F#'})
CREATE (ch1:Challenge {id: 'clojure-fsharp-1', text: 'Dynamic to static typing', category: 'Type'}),
       (ch2:Challenge {id: 'clojure-fsharp-2', text: 'Platform migration (JVM to .NET)', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Clojure -> Haskell (Total: 5, Medium)
MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Haskell'})
CREATE (ch1:Challenge {id: 'clojure-haskell-1', text: 'Dynamic to static typing with HM inference', category: 'Type'}),
       (ch2:Challenge {id: 'clojure-haskell-2', text: 'Practical FP to pure FP', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Clojure -> Roc (Total: 5, Medium)
MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Roc'})
CREATE (ch1:Challenge {id: 'clojure-roc-1', text: 'Dynamic to static typing', category: 'Type'}),
       (ch2:Challenge {id: 'clojure-roc-2', text: 'Effects system adaptation', category: 'Concurrency'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Clojure -> Scala (Total: 1, Easy)
MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 0}]->(tgt);
MATCH (src:Language {name: 'Clojure'}), (tgt:Language {name: 'Scala'})
CREATE (ch1:Challenge {id: 'clojure-scala-1', text: 'Same JVM platform simplifies migration', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// ============================================================================
// ELIXIR CONVERSIONS
// ============================================================================

// Elixir -> Clojure (Total: 4, Medium)
MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Clojure'})
CREATE (ch1:Challenge {id: 'elixir-clojure-1', text: 'Platform migration (BEAM to JVM)', category: 'Platform'}),
       (ch2:Challenge {id: 'elixir-clojure-2', text: 'Actors to STM concurrency model', category: 'Concurrency'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Elixir -> Elm (Total: 5, Medium)
MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Elm'})
CREATE (ch1:Challenge {id: 'elixir-elm-1', text: 'Dynamic to static typing', category: 'Type'}),
       (ch2:Challenge {id: 'elixir-elm-2', text: 'Platform migration (BEAM to JS)', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Elixir -> Erlang (Total: 0, Easy)
MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 0}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 0}]->(tgt);
MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Erlang'})
CREATE (ch1:Challenge {id: 'elixir-erlang-1', text: 'Same BEAM platform - mostly syntactic', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Elixir -> F# (Total: 4, Medium)
MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'F#'})
CREATE (ch1:Challenge {id: 'elixir-fsharp-1', text: 'Platform migration (BEAM to .NET)', category: 'Platform'}),
       (ch2:Challenge {id: 'elixir-fsharp-2', text: 'Actors to Async concurrency', category: 'Concurrency'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Elixir -> Haskell (Total: 5, Medium)
MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Haskell'})
CREATE (ch1:Challenge {id: 'elixir-haskell-1', text: 'Dynamic to static typing with HM', category: 'Type'}),
       (ch2:Challenge {id: 'elixir-haskell-2', text: 'Practical FP to pure FP', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Elixir -> Roc (Total: 6, Hard)
MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 2}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Roc'})
CREATE (ch1:Challenge {id: 'elixir-roc-1', text: 'Actors to Effects system', category: 'Concurrency'}),
       (ch2:Challenge {id: 'elixir-roc-2', text: 'BEAM to Native platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Elixir -> Scala (Total: 4, Medium)
MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Elixir'}), (tgt:Language {name: 'Scala'})
CREATE (ch1:Challenge {id: 'elixir-scala-1', text: 'Platform migration (BEAM to JVM)', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// ============================================================================
// ERLANG CONVERSIONS
// ============================================================================

// Erlang -> Clojure (Total: 4, Medium)
MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Clojure'})
CREATE (ch1:Challenge {id: 'erlang-clojure-1', text: 'Actors to STM concurrency model', category: 'Concurrency'}),
       (ch2:Challenge {id: 'erlang-clojure-2', text: 'BEAM to JVM platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Erlang -> Elixir (Total: 0, Easy)
MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 0}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 0}]->(tgt);
MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Elixir'})
CREATE (ch1:Challenge {id: 'erlang-elixir-1', text: 'Same BEAM platform - mostly syntactic', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Erlang -> Elm (Total: 5, Medium)
MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Elm'})
CREATE (ch1:Challenge {id: 'erlang-elm-1', text: 'Dynamic to static typing', category: 'Type'}),
       (ch2:Challenge {id: 'erlang-elm-2', text: 'Platform migration (BEAM to JS)', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Erlang -> F# (Total: 4, Medium)
MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'F#'})
CREATE (ch1:Challenge {id: 'erlang-fsharp-1', text: 'Platform migration (BEAM to .NET)', category: 'Platform'}),
       (ch2:Challenge {id: 'erlang-fsharp-2', text: 'Actors to Async concurrency', category: 'Concurrency'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Erlang -> Haskell (Total: 5, Medium)
MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Haskell'})
CREATE (ch1:Challenge {id: 'erlang-haskell-1', text: 'Dynamic to static typing', category: 'Type'}),
       (ch2:Challenge {id: 'erlang-haskell-2', text: 'Practical FP to pure FP', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Erlang -> Roc (Total: 6, Hard)
MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 2}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Roc'})
CREATE (ch1:Challenge {id: 'erlang-roc-1', text: 'Actors to Effects system', category: 'Concurrency'}),
       (ch2:Challenge {id: 'erlang-roc-2', text: 'BEAM to Native platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Erlang -> Scala (Total: 4, Medium)
MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Erlang'}), (tgt:Language {name: 'Scala'})
CREATE (ch1:Challenge {id: 'erlang-scala-1', text: 'BEAM to JVM platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// ============================================================================
// ELM CONVERSIONS
// ============================================================================

// Elm -> Clojure (Total: 5, Medium)
MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Clojure'})
CREATE (ch1:Challenge {id: 'elm-clojure-1', text: 'Static to dynamic typing', category: 'Type'}),
       (ch2:Challenge {id: 'elm-clojure-2', text: 'Platform migration (JS to JVM)', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Elm -> Elixir (Total: 5, Medium)
MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Elixir'})
CREATE (ch1:Challenge {id: 'elm-elixir-1', text: 'Static to dynamic typing', category: 'Type'}),
       (ch2:Challenge {id: 'elm-elixir-2', text: 'TEA to Actors concurrency', category: 'Concurrency'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Elm -> Erlang (Total: 5, Medium)
MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Erlang'})
CREATE (ch1:Challenge {id: 'elm-erlang-1', text: 'Static to dynamic typing', category: 'Type'}),
       (ch2:Challenge {id: 'elm-erlang-2', text: 'Platform migration (JS to BEAM)', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Elm -> F# (Total: 3, Medium)
MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'F#'})
CREATE (ch1:Challenge {id: 'elm-fsharp-1', text: 'Platform migration (JS to .NET)', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Elm -> Haskell (Total: 3, Medium)
MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Haskell'})
CREATE (ch1:Challenge {id: 'elm-haskell-1', text: 'Platform migration (JS to Native)', category: 'Platform'}),
       (ch2:Challenge {id: 'elm-haskell-2', text: 'Similar pure FP - mostly syntactic', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Elm -> Roc (Total: 2, Easy)
MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 0}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Roc'})
CREATE (ch1:Challenge {id: 'elm-roc-1', text: 'Both pure FP - very similar concepts', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Elm -> Scala (Total: 4, Medium)
MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Elm'}), (tgt:Language {name: 'Scala'})
CREATE (ch1:Challenge {id: 'elm-scala-1', text: 'Pure to multi-paradigm', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// ============================================================================
// F# CONVERSIONS
// ============================================================================

// F# -> Clojure (Total: 4, Medium)
MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Clojure'})
CREATE (ch1:Challenge {id: 'fsharp-clojure-1', text: 'Static to dynamic typing', category: 'Type'}),
       (ch2:Challenge {id: 'fsharp-clojure-2', text: '.NET to JVM platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// F# -> Elixir (Total: 4, Medium)
MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Elixir'})
CREATE (ch1:Challenge {id: 'fsharp-elixir-1', text: 'Async to Actors concurrency', category: 'Concurrency'}),
       (ch2:Challenge {id: 'fsharp-elixir-2', text: '.NET to BEAM platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// F# -> Elm (Total: 3, Medium)
MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Elm'})
CREATE (ch1:Challenge {id: 'fsharp-elm-1', text: 'Platform migration (.NET to JS)', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// F# -> Erlang (Total: 4, Medium)
MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Erlang'})
CREATE (ch1:Challenge {id: 'fsharp-erlang-1', text: 'Static to dynamic typing', category: 'Type'}),
       (ch2:Challenge {id: 'fsharp-erlang-2', text: '.NET to BEAM platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// F# -> Haskell (Total: 3, Medium)
MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Haskell'})
CREATE (ch1:Challenge {id: 'fsharp-haskell-1', text: 'Platform migration (.NET to Native)', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// F# -> Roc (Total: 3, Medium)
MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Roc'})
CREATE (ch1:Challenge {id: 'fsharp-roc-1', text: 'Async to Effects system', category: 'Concurrency'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// F# -> Scala (Total: 3, Medium)
MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'F#'}), (tgt:Language {name: 'Scala'})
CREATE (ch1:Challenge {id: 'fsharp-scala-1', text: '.NET to JVM platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// ============================================================================
// HASKELL CONVERSIONS
// ============================================================================

// Haskell -> Clojure (Total: 5, Medium)
MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Clojure'})
CREATE (ch1:Challenge {id: 'haskell-clojure-1', text: 'Static to dynamic typing', category: 'Type'}),
       (ch2:Challenge {id: 'haskell-clojure-2', text: 'Pure to practical FP', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Haskell -> Elixir (Total: 5, Medium)
MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Elixir'})
CREATE (ch1:Challenge {id: 'haskell-elixir-1', text: 'Static to dynamic typing', category: 'Type'}),
       (ch2:Challenge {id: 'haskell-elixir-2', text: 'STM to Actors concurrency', category: 'Concurrency'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Haskell -> Elm (Total: 3, Medium)
MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Elm'})
CREATE (ch1:Challenge {id: 'haskell-elm-1', text: 'Platform migration (Native to JS)', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Haskell -> Erlang (Total: 5, Medium)
MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Erlang'})
CREATE (ch1:Challenge {id: 'haskell-erlang-1', text: 'Static to dynamic typing', category: 'Type'}),
       (ch2:Challenge {id: 'haskell-erlang-2', text: 'STM to Actors concurrency', category: 'Concurrency'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Haskell -> F# (Total: 3, Medium)
MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'F#'})
CREATE (ch1:Challenge {id: 'haskell-fsharp-1', text: 'Platform migration (Native to .NET)', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Haskell -> Roc (Total: 1, Easy)
MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 0}]->(tgt);
MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Roc'})
CREATE (ch1:Challenge {id: 'haskell-roc-1', text: 'Similar pure FP - STM to Effects', category: 'Concurrency'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Haskell -> Scala (Total: 4, Medium)
MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Haskell'}), (tgt:Language {name: 'Scala'})
CREATE (ch1:Challenge {id: 'haskell-scala-1', text: 'Pure to multi-paradigm', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// ============================================================================
// ROC CONVERSIONS
// ============================================================================

// Roc -> Clojure (Total: 5, Medium)
MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Clojure'})
CREATE (ch1:Challenge {id: 'roc-clojure-1', text: 'Static to dynamic typing', category: 'Type'}),
       (ch2:Challenge {id: 'roc-clojure-2', text: 'Effects to STM concurrency', category: 'Concurrency'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Roc -> Elixir (Total: 6, Hard)
MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 2}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Elixir'})
CREATE (ch1:Challenge {id: 'roc-elixir-1', text: 'Effects to Actors concurrency', category: 'Concurrency'}),
       (ch2:Challenge {id: 'roc-elixir-2', text: 'Native to BEAM platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Roc -> Elm (Total: 2, Easy)
MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 0}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Elm'})
CREATE (ch1:Challenge {id: 'roc-elm-1', text: 'Both pure FP - very similar concepts', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Roc -> Erlang (Total: 6, Hard)
MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 2}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Erlang'})
CREATE (ch1:Challenge {id: 'roc-erlang-1', text: 'Effects to Actors concurrency', category: 'Concurrency'}),
       (ch2:Challenge {id: 'roc-erlang-2', text: 'Native to BEAM platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Roc -> F# (Total: 3, Medium)
MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'F#'})
CREATE (ch1:Challenge {id: 'roc-fsharp-1', text: 'Effects to Async concurrency', category: 'Concurrency'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Roc -> Haskell (Total: 1, Easy)
MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 0}]->(tgt);
MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Haskell'})
CREATE (ch1:Challenge {id: 'roc-haskell-1', text: 'Similar pure FP concepts', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Roc -> Scala (Total: 4, Medium)
MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Roc'}), (tgt:Language {name: 'Scala'})
CREATE (ch1:Challenge {id: 'roc-scala-1', text: 'Pure to multi-paradigm', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// ============================================================================
// SCALA CONVERSIONS
// ============================================================================

// Scala -> Clojure (Total: 1, Easy)
MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 0}]->(tgt);
MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Clojure'})
CREATE (ch1:Challenge {id: 'scala-clojure-1', text: 'Same JVM platform simplifies migration', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Scala -> Elixir (Total: 4, Medium)
MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Elixir'})
CREATE (ch1:Challenge {id: 'scala-elixir-1', text: 'JVM to BEAM platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Scala -> Elm (Total: 4, Medium)
MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Elm'})
CREATE (ch1:Challenge {id: 'scala-elm-1', text: 'Multi to pure FP paradigm', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Scala -> Erlang (Total: 4, Medium)
MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Erlang'})
CREATE (ch1:Challenge {id: 'scala-erlang-1', text: 'JVM to BEAM platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Scala -> F# (Total: 3, Medium)
MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'F#'})
CREATE (ch1:Challenge {id: 'scala-fsharp-1', text: 'JVM to .NET platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Scala -> Haskell (Total: 4, Medium)
MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Haskell'})
CREATE (ch1:Challenge {id: 'scala-haskell-1', text: 'Multi to pure FP paradigm', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Scala -> Roc (Total: 4, Medium)
MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Scala'}), (tgt:Language {name: 'Roc'})
CREATE (ch1:Challenge {id: 'scala-roc-1', text: 'Multi to pure FP paradigm', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// ============================================================================
// PYTHON CONVERSIONS
// ============================================================================

// Python -> Clojure (Total: 4, Medium)
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Clojure'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Clojure'})
CREATE (ch1:Challenge {id: 'python-clojure-1', text: 'Multi to functional paradigm', category: 'Paradigm'}),
       (ch2:Challenge {id: 'python-clojure-2', text: 'Interpreted to JVM platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Python -> Elixir (Total: 5, Medium)
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Elixir'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 2}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Elixir'})
CREATE (ch1:Challenge {id: 'python-elixir-1', text: 'Asyncio to Actors concurrency', category: 'Concurrency'}),
       (ch2:Challenge {id: 'python-elixir-2', text: 'Interpreted to BEAM platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Python -> Elm (Total: 6, Hard)
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Elm'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 2}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Elm'})
CREATE (ch1:Challenge {id: 'python-elm-1', text: 'Dynamic to static typing', category: 'Type'}),
       (ch2:Challenge {id: 'python-elm-2', text: 'Multi to pure FP paradigm', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Python -> Erlang (Total: 5, Medium)
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Erlang'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 2}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Erlang'})
CREATE (ch1:Challenge {id: 'python-erlang-1', text: 'Asyncio to Actors concurrency', category: 'Concurrency'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Python -> F# (Total: 5, Medium)
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'F#'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'F#'})
CREATE (ch1:Challenge {id: 'python-fsharp-1', text: 'Dynamic to static typing', category: 'Type'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Python -> Go (Total: 4, Medium)
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Go'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Go'})
CREATE (ch1:Challenge {id: 'python-go-1', text: 'Dynamic to static typing', category: 'Type'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Python -> Haskell (Total: 6, Hard)
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Haskell'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 2}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Haskell'})
CREATE (ch1:Challenge {id: 'python-haskell-1', text: 'Dynamic to static typing with HM', category: 'Type'}),
       (ch2:Challenge {id: 'python-haskell-2', text: 'Multi to pure FP paradigm', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Python -> Roc (Total: 6, Hard)
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Roc'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 2}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Roc'})
CREATE (ch1:Challenge {id: 'python-roc-1', text: 'Dynamic to static typing', category: 'Type'}),
       (ch2:Challenge {id: 'python-roc-2', text: 'Multi to pure FP paradigm', category: 'Paradigm'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Python -> Rust (Total: 7, Hard)
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Rust'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 2}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Rust'})
CREATE (ch1:Challenge {id: 'python-rust-1', text: 'GC to Ownership memory model', category: 'Memory'}),
       (ch2:Challenge {id: 'python-rust-2', text: 'Dynamic to static typing', category: 'Type'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Python -> Scala (Total: 5, Medium)
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Scala'})
CREATE (src)-[:TYPE_DIFF {score: 1}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'Scala'})
CREATE (ch1:Challenge {id: 'python-scala-1', text: 'Dynamic to static typing', category: 'Type'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Python -> TypeScript (Total: 1, Easy)
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'TypeScript'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 0}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 1}]->(tgt);
MATCH (src:Language {name: 'Python'}), (tgt:Language {name: 'TypeScript'})
CREATE (ch1:Challenge {id: 'python-typescript-1', text: 'Similar multi-paradigm - mostly platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// ============================================================================
// TYPESCRIPT CONVERSIONS
// ============================================================================

// TypeScript -> Go (Total: 4, Medium)
MATCH (src:Language {name: 'TypeScript'}), (tgt:Language {name: 'Go'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'TypeScript'}), (tgt:Language {name: 'Go'})
CREATE (ch1:Challenge {id: 'typescript-go-1', text: 'Promises to CSP concurrency', category: 'Concurrency'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// TypeScript -> Python (Total: 1, Easy)
MATCH (src:Language {name: 'TypeScript'}), (tgt:Language {name: 'Python'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 0}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 1}]->(tgt);
MATCH (src:Language {name: 'TypeScript'}), (tgt:Language {name: 'Python'})
CREATE (ch1:Challenge {id: 'typescript-python-1', text: 'Similar multi-paradigm - mostly platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// TypeScript -> Rust (Total: 6, Hard)
MATCH (src:Language {name: 'TypeScript'}), (tgt:Language {name: 'Rust'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 2}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'TypeScript'}), (tgt:Language {name: 'Rust'})
CREATE (ch1:Challenge {id: 'typescript-rust-1', text: 'GC to Ownership memory model', category: 'Memory'}),
       (ch2:Challenge {id: 'typescript-rust-2', text: 'Platform migration (JS to Native)', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// ============================================================================
// SYSTEMS LANGUAGE CONVERSIONS
// ============================================================================

// C -> C++ (Total: 0, Easy)
MATCH (src:Language {name: 'C'}), (tgt:Language {name: 'C++'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 0}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 0}]->(tgt);
MATCH (src:Language {name: 'C'}), (tgt:Language {name: 'C++'})
CREATE (ch1:Challenge {id: 'c-cpp-1', text: 'Same language family', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// C -> Rust (Total: 3, Medium)
MATCH (src:Language {name: 'C'}), (tgt:Language {name: 'Rust'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 1}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 0}]->(tgt);
MATCH (src:Language {name: 'C'}), (tgt:Language {name: 'Rust'})
CREATE (ch1:Challenge {id: 'c-rust-1', text: 'Manual to Ownership memory model', category: 'Memory'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// C++ -> Rust (Total: 1, Easy)
MATCH (src:Language {name: 'C++'}), (tgt:Language {name: 'Rust'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 1}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 0}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 0}]->(tgt);
MATCH (src:Language {name: 'C++'}), (tgt:Language {name: 'Rust'})
CREATE (ch1:Challenge {id: 'cpp-rust-1', text: 'Similar RAII memory models', category: 'Memory'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Go -> Rust (Total: 3, Medium)
MATCH (src:Language {name: 'Go'}), (tgt:Language {name: 'Rust'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 2}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 0}]->(tgt);
MATCH (src:Language {name: 'Go'}), (tgt:Language {name: 'Rust'})
CREATE (ch1:Challenge {id: 'go-rust-1', text: 'GC to Ownership memory model', category: 'Memory'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Java -> C (Total: 6, Hard)
MATCH (src:Language {name: 'Java'}), (tgt:Language {name: 'C'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 2}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Java'}), (tgt:Language {name: 'C'})
CREATE (ch1:Challenge {id: 'java-c-1', text: 'GC to Manual memory management', category: 'Memory'}),
       (ch2:Challenge {id: 'java-c-2', text: 'JVM to Native platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// Java -> C++ (Total: 4, Medium)
MATCH (src:Language {name: 'Java'}), (tgt:Language {name: 'C++'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 2}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 0}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Java'}), (tgt:Language {name: 'C++'})
CREATE (ch1:Challenge {id: 'java-cpp-1', text: 'GC to Manual/RAII memory', category: 'Memory'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// Java -> Rust (Total: 6, Hard)
MATCH (src:Language {name: 'Java'}), (tgt:Language {name: 'Rust'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 1}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 2}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 1}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 2}]->(tgt);
MATCH (src:Language {name: 'Java'}), (tgt:Language {name: 'Rust'})
CREATE (ch1:Challenge {id: 'java-rust-1', text: 'GC to Ownership memory model', category: 'Memory'}),
       (ch2:Challenge {id: 'java-rust-2', text: 'JVM to Native platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt),
       (src)-[:FACES]->(ch2)-[:FOR]->(tgt);

// ============================================================================
// PLATFORM-SPECIFIC CONVERSIONS
// ============================================================================

// Objective-C -> Swift (Total: 0, Easy)
MATCH (src:Language {name: 'Objective-C'}), (tgt:Language {name: 'Swift'})
CREATE (src)-[:TYPE_DIFF {score: 0}]->(tgt),
       (src)-[:PARADIGM_DIFF {score: 0}]->(tgt),
       (src)-[:MEMORY_DIFF {score: 0}]->(tgt),
       (src)-[:CONCURRENCY_DIFF {score: 0}]->(tgt),
       (src)-[:PLATFORM_DIFF {score: 0}]->(tgt);
MATCH (src:Language {name: 'Objective-C'}), (tgt:Language {name: 'Swift'})
CREATE (ch1:Challenge {id: 'objc-swift-1', text: 'Same Apple platform', category: 'Platform'}),
       (src)-[:FACES]->(ch1)-[:FOR]->(tgt);

// ============================================================================
// USEFUL QUERIES
// ============================================================================

// Get totalScore and level for a specific pair
// MATCH (src:Language {name: 'Python'})-[r]->(tgt:Language {name: 'Rust'})
// WHERE type(r) IN ['TYPE_DIFF', 'PARADIGM_DIFF', 'MEMORY_DIFF', 'CONCURRENCY_DIFF', 'PLATFORM_DIFF']
// WITH src, tgt, sum(r.score) AS totalScore
// RETURN
//   src.name AS source,
//   tgt.name AS target,
//   totalScore,
//   CASE
//     WHEN totalScore <= 2 THEN 'Easy'
//     WHEN totalScore <= 5 THEN 'Medium'
//     WHEN totalScore <= 8 THEN 'Hard'
//     ELSE 'Expert'
//   END AS level;

// Get full breakdown with individual scores
// MATCH (src:Language {name: 'Python'})-[r]->(tgt:Language {name: 'Rust'})
// WHERE type(r) IN ['TYPE_DIFF', 'PARADIGM_DIFF', 'MEMORY_DIFF', 'CONCURRENCY_DIFF', 'PLATFORM_DIFF']
// WITH src, tgt, type(r) AS factor, r.score AS score
// ORDER BY factor
// WITH src, tgt, collect({factor: factor, score: score}) AS scores, sum(score) AS totalScore
// RETURN
//   src.name AS source,
//   tgt.name AS target,
//   scores,
//   totalScore,
//   CASE
//     WHEN totalScore <= 2 THEN 'Easy'
//     WHEN totalScore <= 5 THEN 'Medium'
//     WHEN totalScore <= 8 THEN 'Hard'
//     ELSE 'Expert'
//   END AS level;

// Get all conversions sorted by difficulty
// MATCH (src:Language)-[r]->(tgt:Language)
// WHERE type(r) IN ['TYPE_DIFF', 'PARADIGM_DIFF', 'MEMORY_DIFF', 'CONCURRENCY_DIFF', 'PLATFORM_DIFF']
// WITH src, tgt, sum(r.score) AS totalScore
// RETURN
//   src.name AS source,
//   tgt.name AS target,
//   totalScore,
//   CASE
//     WHEN totalScore <= 2 THEN 'Easy'
//     WHEN totalScore <= 5 THEN 'Medium'
//     WHEN totalScore <= 8 THEN 'Hard'
//     ELSE 'Expert'
//   END AS level
// ORDER BY totalScore DESC, source, target;

// Find challenges for a conversion pair
// MATCH (src:Language {name: 'Python'})-[:FACES]->(ch:Challenge)-[:FOR]->(tgt:Language {name: 'Rust'})
// RETURN ch.text AS challenge, ch.category AS category
// ORDER BY ch.category;

// Find all Hard conversions with their challenges
// MATCH (src:Language)-[r]->(tgt:Language)
// WHERE type(r) IN ['TYPE_DIFF', 'PARADIGM_DIFF', 'MEMORY_DIFF', 'CONCURRENCY_DIFF', 'PLATFORM_DIFF']
// WITH src, tgt, sum(r.score) AS totalScore
// WHERE totalScore >= 6 AND totalScore <= 8
// OPTIONAL MATCH (src)-[:FACES]->(ch:Challenge)-[:FOR]->(tgt)
// WITH src, tgt, totalScore, collect(ch.text) AS challenges
// RETURN
//   src.name AS source,
//   tgt.name AS target,
//   totalScore,
//   challenges
// ORDER BY totalScore DESC;

// Find conversions by challenge category
// MATCH (src:Language)-[:FACES]->(ch:Challenge {category: 'Memory'})-[:FOR]->(tgt:Language)
// RETURN src.name AS source, tgt.name AS target, ch.text AS challenge;

// Aggregate difficulty statistics
// MATCH (src:Language)-[r]->(tgt:Language)
// WHERE type(r) IN ['TYPE_DIFF', 'PARADIGM_DIFF', 'MEMORY_DIFF', 'CONCURRENCY_DIFF', 'PLATFORM_DIFF']
// WITH src, tgt, sum(r.score) AS totalScore
// WITH CASE
//   WHEN totalScore <= 2 THEN 'Easy'
//   WHEN totalScore <= 5 THEN 'Medium'
//   WHEN totalScore <= 8 THEN 'Hard'
//   ELSE 'Expert'
// END AS level
// RETURN level AS difficulty, count(*) AS count
// ORDER BY CASE level
//   WHEN 'Easy' THEN 1
//   WHEN 'Medium' THEN 2
//   WHEN 'Hard' THEN 3
//   WHEN 'Expert' THEN 4
// END;

// Find conversion path between two languages
// MATCH path = shortestPath((src:Language {name: 'Python'})-[:TYPE_DIFF|PARADIGM_DIFF|MEMORY_DIFF|CONCURRENCY_DIFF|PLATFORM_DIFF*]->(tgt:Language {name: 'Rust'}))
// RETURN path;

// Find all conversions from a language, sorted by difficulty
// MATCH (src:Language {name: 'Python'})-[r]->(tgt:Language)
// WHERE type(r) IN ['TYPE_DIFF', 'PARADIGM_DIFF', 'MEMORY_DIFF', 'CONCURRENCY_DIFF', 'PLATFORM_DIFF']
// WITH src, tgt, sum(r.score) AS totalScore
// OPTIONAL MATCH (src)-[:FACES]->(ch:Challenge)-[:FOR]->(tgt)
// WITH src, tgt, totalScore, collect(ch.text) AS challenges
// RETURN
//   tgt.name AS target,
//   totalScore,
//   CASE
//     WHEN totalScore <= 2 THEN 'Easy'
//     WHEN totalScore <= 5 THEN 'Medium'
//     WHEN totalScore <= 8 THEN 'Hard'
//     ELSE 'Expert'
//   END AS level,
//   challenges
// ORDER BY totalScore;

// Find languages by platform
// MATCH (l:Language)-[:RUNS_ON]->(p:Platform {name: 'JVM'})
// RETURN l.name, l.paradigm, l.typeSystem;

// Find REPL-centric languages
// MATCH (l:Language) WHERE l.replCentric = true
// RETURN l.name, l.platform;
