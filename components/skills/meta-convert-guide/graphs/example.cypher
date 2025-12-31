// Example: Query Python to Rust conversion difficulty
// Run this after importing data with: python import.py --reset

MATCH (s:Language {name: 'Python'})-[t:TYPE_DIFF]->(e:Language {name: 'Rust'}),
      (s)-[p:PARADIGM_DIFF]->(e),
      (s)-[m:MEMORY_DIFF]->(e),
      (s)-[c:CONCURRENCY_DIFF]->(e),
      (s)-[pl:PLATFORM_DIFF]->(e)
RETURN s.name AS source, e.name AS target,
       t.score AS type, p.score AS paradigm, m.score AS memory,
       c.score AS concurrency, pl.score AS platform,
       t.score + p.score + m.score + c.score + pl.score AS totalScore;

// Example: Get challenges for Python → Rust
MATCH (s:Language {name: 'Python'})-[:HAS_CHALLENGE]->(c:Challenge)
      -[:WHEN_CONVERTING_TO]->(t:Language {name: 'Rust'})
RETURN c.category, c.text;
