// =============================================================================
// KuzuDB Schema for Language Conversion Difficulty
// =============================================================================
// This schema defines the graph structure for analyzing language conversion
// difficulty. Data is loaded from data/difficulty.json using import.py.
//
// Usage: kuzu -i schema.cypher <database_path>
// =============================================================================

// -----------------------------------------------------------------------------
// NODE TABLES
// -----------------------------------------------------------------------------

// Language node - represents a programming language
CREATE NODE TABLE Language (
    name STRING,
    family STRING,
    typeSystem STRING,
    paradigm STRING,
    memory STRING,
    concurrency STRING,
    platform STRING,
    replCentric BOOL DEFAULT false,
    PRIMARY KEY (name)
);

// Platform node - represents a runtime platform
CREATE NODE TABLE Platform (
    name STRING,
    description STRING,
    PRIMARY KEY (name)
);

// DifficultyLevel node - represents a difficulty category
CREATE NODE TABLE DifficultyLevel (
    name STRING,
    minScore INT64,
    maxScore INT64,
    expectedSkillSize STRING,
    PRIMARY KEY (name)
);

// Challenge node - represents a specific challenge in a conversion
CREATE NODE TABLE Challenge (
    id STRING,
    text STRING,
    category STRING,
    PRIMARY KEY (id)
);

// -----------------------------------------------------------------------------
// RELATIONSHIP TABLES
// -----------------------------------------------------------------------------

// Language RUNS_ON Platform
CREATE REL TABLE RUNS_ON (
    FROM Language TO Platform
);

// Direct score relationships between languages
// Each represents one of the 5 difficulty factors

CREATE REL TABLE TYPE_DIFF (
    FROM Language TO Language,
    score INT64
);

CREATE REL TABLE PARADIGM_DIFF (
    FROM Language TO Language,
    score INT64
);

CREATE REL TABLE MEMORY_DIFF (
    FROM Language TO Language,
    score INT64
);

CREATE REL TABLE CONCURRENCY_DIFF (
    FROM Language TO Language,
    score INT64
);

CREATE REL TABLE PLATFORM_DIFF (
    FROM Language TO Language,
    score INT64
);

// Challenge Mini-Hub pattern:
// (Source)-[:HAS_CHALLENGE]->(Challenge)-[:WHEN_CONVERTING_TO]->(Target)
CREATE REL TABLE HAS_CHALLENGE (
    FROM Language TO Challenge
);

CREATE REL TABLE WHEN_CONVERTING_TO (
    FROM Challenge TO Language
);

// DifficultyLevel relationships (assigned at query time, not stored)
// These would be computed by queries, not stored relationships
