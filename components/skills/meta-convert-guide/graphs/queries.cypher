// =============================================================================
// Reusable Cypher Queries for Language Conversion Difficulty Analysis
// =============================================================================
// These queries work with KuzuDB after importing data from difficulty.json.
// Copy-paste into your KuzuDB session or use programmatically.
//
// Total Score Calculation:
//   totalScore = TYPE_DIFF + PARADIGM_DIFF + MEMORY_DIFF + CONCURRENCY_DIFF + PLATFORM_DIFF
//   (Each score: 0-2, Total: 0-10)
//
// Difficulty Levels:
//   Easy:   0-2   | Medium: 3-5   | Hard: 6-8   | Expert: 9-10
// =============================================================================


// -----------------------------------------------------------------------------
// BASIC QUERIES
// -----------------------------------------------------------------------------

// --- List all languages with their properties ---
// Q01_ALL_LANGUAGES
MATCH (l:Language)
RETURN l.name, l.family, l.typeSystem, l.paradigm, l.memory, l.concurrency
ORDER BY l.name;

// --- List all platforms ---
// Q02_ALL_PLATFORMS
MATCH (p:Platform)
RETURN p.name, p.description;

// --- List languages by family ---
// Q03_LANGUAGES_BY_FAMILY
MATCH (l:Language)
RETURN l.family, collect(l.name) AS languages
ORDER BY l.family;

// --- Languages that are REPL-centric ---
// Q04_REPL_CENTRIC_LANGUAGES
MATCH (l:Language)
WHERE l.replCentric = true
RETURN l.name, l.family;


// -----------------------------------------------------------------------------
// DIFFICULTY ANALYSIS
// -----------------------------------------------------------------------------

// --- Get all conversion scores between two languages ---
// Q10_CONVERSION_SCORES
// Replace $source and $target with language names
MATCH (s:Language {name: $source})-[t:TYPE_DIFF]->(e:Language {name: $target}),
      (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
RETURN s.name AS source, e.name AS target,
       t.score AS type, p.score AS paradigm, m.score AS memory,
       c.score AS concurrency, pl.score AS platform,
       t.score + p.score + m.score + c.score + pl.score AS totalScore;

// --- Get difficulty level for a conversion ---
// Q11_DIFFICULTY_LEVEL
// Replace $source and $target with language names
MATCH (s:Language {name: $source})-[t:TYPE_DIFF]->(e:Language {name: $target}),
      (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
WITH s.name AS source, e.name AS target,
     t.score + p.score + m.score + c.score + pl.score AS totalScore
MATCH (d:DifficultyLevel)
WHERE totalScore >= d.minScore AND totalScore <= d.maxScore
RETURN source, target, totalScore, d.name AS difficulty, d.expectedSkillSize;

// --- All conversions ranked by difficulty ---
// Q12_ALL_CONVERSIONS_RANKED
MATCH (s:Language)-[t:TYPE_DIFF]->(e:Language),
      (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
WITH s.name AS source, e.name AS target,
     t.score + p.score + m.score + c.score + pl.score AS totalScore
RETURN source, target, totalScore,
       CASE
         WHEN totalScore <= 2 THEN 'Easy'
         WHEN totalScore <= 5 THEN 'Medium'
         WHEN totalScore <= 8 THEN 'Hard'
         ELSE 'Expert'
       END AS difficulty
ORDER BY totalScore DESC;

// --- Easiest conversions (score <= 2) ---
// Q13_EASY_CONVERSIONS
MATCH (s:Language)-[t:TYPE_DIFF]->(e:Language),
      (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
WITH s.name AS source, e.name AS target,
     t.score + p.score + m.score + c.score + pl.score AS totalScore
WHERE totalScore <= 2
RETURN source, target, totalScore
ORDER BY totalScore, source, target;

// --- Hardest conversions (score >= 6) ---
// Q14_HARD_CONVERSIONS
MATCH (s:Language)-[t:TYPE_DIFF]->(e:Language),
      (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
WITH s.name AS source, e.name AS target,
     t.score + p.score + m.score + c.score + pl.score AS totalScore
WHERE totalScore >= 6
RETURN source, target, totalScore
ORDER BY totalScore DESC;


// -----------------------------------------------------------------------------
// CHALLENGE ANALYSIS
// -----------------------------------------------------------------------------

// --- Get challenges for a specific conversion ---
// Q20_CHALLENGES_FOR_CONVERSION
// Replace $source and $target with language names
MATCH (s:Language {name: $source})-[:HAS_CHALLENGE]->(c:Challenge)-[:WHEN_CONVERTING_TO]->(t:Language {name: $target})
RETURN s.name AS source, t.name AS target, c.text, c.category;

// --- Challenges by category ---
// Q21_CHALLENGES_BY_CATEGORY
MATCH (c:Challenge)
RETURN c.category, count(c) AS challengeCount, collect(c.text) AS examples
ORDER BY challengeCount DESC;

// --- Most common challenges ---
// Q22_COMMON_CHALLENGES
MATCH (c:Challenge)
RETURN c.category, c.text, count(c) AS occurrences
ORDER BY occurrences DESC
LIMIT 10;

// --- Languages with memory-related challenges ---
// Q23_MEMORY_CHALLENGES
MATCH (s:Language)-[:HAS_CHALLENGE]->(c:Challenge)-[:WHEN_CONVERTING_TO]->(t:Language)
WHERE c.category = 'Memory'
RETURN s.name AS source, t.name AS target, c.text
ORDER BY source, target;


// -----------------------------------------------------------------------------
// FACTOR-SPECIFIC ANALYSIS
// -----------------------------------------------------------------------------

// --- Conversions with high memory difficulty ---
// Q30_HIGH_MEMORY_DIFF
MATCH (s:Language)-[m:MEMORY_DIFF]->(t:Language)
WHERE m.score = 2
RETURN s.name AS source, t.name AS target, m.score AS memoryScore;

// --- Conversions with high concurrency difficulty ---
// Q31_HIGH_CONCURRENCY_DIFF
MATCH (s:Language)-[c:CONCURRENCY_DIFF]->(t:Language)
WHERE c.score = 2
RETURN s.name AS source, t.name AS target, c.score AS concurrencyScore;

// --- Conversions with platform changes ---
// Q32_PLATFORM_CHANGES
MATCH (s:Language)-[p:PLATFORM_DIFF]->(t:Language)
WHERE p.score > 0
RETURN s.name AS source, s.platform AS sourcePlatform,
       t.name AS target, t.platform AS targetPlatform,
       p.score AS platformScore
ORDER BY p.score DESC;

// --- Type system transitions (dynamic <-> static) ---
// Q33_TYPE_SYSTEM_TRANSITIONS
MATCH (s:Language)-[t:TYPE_DIFF]->(e:Language)
WHERE t.score > 0
RETURN s.name AS source, s.typeSystem AS sourceType,
       e.name AS target, e.typeSystem AS targetType,
       t.score AS typeScore
ORDER BY t.score DESC;


// -----------------------------------------------------------------------------
// FAMILY & PLATFORM ANALYSIS
// -----------------------------------------------------------------------------

// --- Conversions within the same family ---
// Q40_SAME_FAMILY_CONVERSIONS
MATCH (s:Language)-[t:TYPE_DIFF]->(e:Language)
WHERE s.family = e.family
MATCH (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
RETURN s.name AS source, e.name AS target, s.family AS family,
       t.score + p.score + m.score + c.score + pl.score AS totalScore
ORDER BY family, totalScore;

// --- Conversions across families ---
// Q41_CROSS_FAMILY_CONVERSIONS
MATCH (s:Language)-[t:TYPE_DIFF]->(e:Language)
WHERE s.family <> e.family
MATCH (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
RETURN s.family AS sourceFamily, e.family AS targetFamily,
       count(*) AS conversionCount,
       avg(t.score + p.score + m.score + c.score + pl.score) AS avgDifficulty
ORDER BY avgDifficulty DESC;

// --- Platform migration paths ---
// Q42_PLATFORM_MIGRATIONS
MATCH (s:Language)-[:RUNS_ON]->(sp:Platform),
      (s)-[pl:PLATFORM_DIFF]->(t:Language)-[:RUNS_ON]->(tp:Platform)
WHERE sp <> tp
RETURN sp.name AS sourcePlatform, tp.name AS targetPlatform,
       count(*) AS pathCount
ORDER BY pathCount DESC;


// -----------------------------------------------------------------------------
// SKILL PLANNING QUERIES
// -----------------------------------------------------------------------------

// --- Conversions FROM a specific language ---
// Q50_FROM_LANGUAGE
// Replace $language with the source language name
MATCH (s:Language {name: $language})-[t:TYPE_DIFF]->(e:Language),
      (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
WITH e.name AS target,
     t.score + p.score + m.score + c.score + pl.score AS totalScore
RETURN target, totalScore,
       CASE
         WHEN totalScore <= 2 THEN 'Easy'
         WHEN totalScore <= 5 THEN 'Medium'
         WHEN totalScore <= 8 THEN 'Hard'
         ELSE 'Expert'
       END AS difficulty
ORDER BY totalScore;

// --- Conversions TO a specific language ---
// Q51_TO_LANGUAGE
// Replace $language with the target language name
MATCH (s:Language)-[t:TYPE_DIFF]->(e:Language {name: $language}),
      (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
WITH s.name AS source,
     t.score + p.score + m.score + c.score + pl.score AS totalScore
RETURN source, totalScore,
       CASE
         WHEN totalScore <= 2 THEN 'Easy'
         WHEN totalScore <= 5 THEN 'Medium'
         WHEN totalScore <= 8 THEN 'Hard'
         ELSE 'Expert'
       END AS difficulty
ORDER BY totalScore;

// --- Skill creation priority (high impact conversions) ---
// Q52_SKILL_PRIORITY
// Find conversions that are common (popular languages) but hard
MATCH (s:Language)-[t:TYPE_DIFF]->(e:Language),
      (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
WITH s.name AS source, e.name AS target,
     t.score + p.score + m.score + c.score + pl.score AS totalScore
WHERE totalScore >= 5
RETURN source, target, totalScore
ORDER BY totalScore DESC;


// -----------------------------------------------------------------------------
// STATISTICS
// -----------------------------------------------------------------------------

// --- Summary statistics ---
// Q60_SUMMARY_STATS
MATCH (l:Language)
WITH count(l) AS languageCount
MATCH ()-[r:TYPE_DIFF]->()
WITH languageCount, count(r) AS conversionCount
MATCH (c:Challenge)
WITH languageCount, conversionCount, count(c) AS challengeCount
RETURN languageCount, conversionCount, challengeCount;

// --- Difficulty distribution ---
// Q61_DIFFICULTY_DISTRIBUTION
MATCH (s:Language)-[t:TYPE_DIFF]->(e:Language),
      (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
WITH t.score + p.score + m.score + c.score + pl.score AS totalScore
WITH CASE
       WHEN totalScore <= 2 THEN 'Easy'
       WHEN totalScore <= 5 THEN 'Medium'
       WHEN totalScore <= 8 THEN 'Hard'
       ELSE 'Expert'
     END AS difficulty
RETURN difficulty, count(*) AS count
ORDER BY count DESC;

// --- Average difficulty by source language ---
// Q62_AVG_DIFFICULTY_BY_SOURCE
MATCH (s:Language)-[t:TYPE_DIFF]->(e:Language),
      (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
WITH s.name AS source,
     avg(t.score + p.score + m.score + c.score + pl.score) AS avgDifficulty
RETURN source, round(avgDifficulty * 100) / 100 AS avgDifficulty
ORDER BY avgDifficulty DESC;

// --- Average difficulty by target language ---
// Q63_AVG_DIFFICULTY_BY_TARGET
MATCH (s:Language)-[t:TYPE_DIFF]->(e:Language),
      (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
WITH e.name AS target,
     avg(t.score + p.score + m.score + c.score + pl.score) AS avgDifficulty
RETURN target, round(avgDifficulty * 100) / 100 AS avgDifficulty
ORDER BY avgDifficulty DESC;
