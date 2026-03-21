#!/usr/bin/env python3
"""
Pattern Clustering and Gap Analysis for convert-* skills.

Task 0.2: Cluster patterns into Universal, Family-specific, Language-specific, Inherited
Task 0.3: Analyze gaps - lossy conversions, human decisions, impossible conversions

Usage:
    python cluster_and_analyze.py
"""

import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Language family mappings
LANGUAGE_FAMILIES = {
    # ML-FP family
    "haskell": "ml-fp",
    "elm": "ml-fp",
    "fsharp": "ml-fp",
    "ocaml": "ml-fp",
    "scala": "ml-fp",
    "roc": "ml-fp",
    "purescript": "ml-fp",

    # BEAM family
    "erlang": "beam",
    "elixir": "beam",
    "gleam": "beam",

    # LISP family
    "clojure": "lisp",
    "racket": "lisp",
    "scheme": "lisp",

    # Systems family
    "rust": "systems",
    "c": "systems",
    "cpp": "systems",
    "zig": "systems",

    # Managed OOP family
    "java": "managed",
    "kotlin": "managed",
    "csharp": "managed",

    # Dynamic family
    "python": "dynamic",
    "ruby": "dynamic",
    "javascript": "dynamic",
    "typescript": "dynamic",

    # Apple family
    "swift": "apple",
    "objc": "apple",

    # Go (its own category)
    "golang": "go",
}


@dataclass
class ClusterResult:
    """Result of pattern clustering."""
    cluster: str  # universal, family, language, inherited
    reason: str
    family: str | None = None  # For family-specific patterns
    languages: list[str] = field(default_factory=list)  # For language-specific


@dataclass
class GapAnalysis:
    """Gap analysis result."""
    gap_type: str  # lossy, human_decision, impossible, negative
    description: str
    severity: str  # low, medium, high, critical
    source_lang: str
    target_lang: str
    mitigation: str = ""


class PatternAnalyzer:
    """Analyze extracted patterns for clustering and gaps."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.patterns = self._load_patterns()
        self.clusters = {}
        self.gaps = []

    def _load_patterns(self) -> list[dict]:
        """Load extracted patterns."""
        patterns_file = self.data_dir / "patterns.json"
        if patterns_file.exists():
            return json.loads(patterns_file.read_text())

        # Fall back to parsing SQL
        sql_file = self.data_dir / "patterns.sql"
        if sql_file.exists():
            return self._parse_sql(sql_file)

        raise FileNotFoundError("No patterns file found")

    def _parse_sql(self, sql_file: Path) -> list[dict]:
        """Parse patterns from SQL dump."""
        content = sql_file.read_text()
        patterns = []

        # Find INSERT statements
        insert_pattern = r"INSERT INTO patterns VALUES\(([^)]+)\)"
        for match in re.finditer(insert_pattern, content):
            values = match.group(1)
            # Parse values (simplified)
            parts = [p.strip().strip("'") for p in values.split(",")]
            if len(parts) >= 11:
                patterns.append({
                    "id": parts[0],
                    "skill_name": parts[1],
                    "pattern_type": parts[2],
                    "source_pattern": parts[3],
                    "target_pattern": parts[4],
                    "notes": parts[5],
                    "category": parts[6],
                    "confidence": parts[7],
                    "is_bidirectional": parts[8] == "1",
                    "direction": parts[9],
                    "section_source": parts[10],
                })

        return patterns

    def cluster_patterns(self):
        """Cluster patterns into Universal, Family, Language, Inherited."""
        # Group patterns by source_pattern (normalized)
        pattern_groups = defaultdict(list)
        for p in self.patterns:
            key = self._normalize_pattern(p["source_pattern"])
            pattern_groups[key].append(p)

        for key, group in pattern_groups.items():
            cluster = self._determine_cluster(group)
            self.clusters[key] = {
                "count": len(group),
                "cluster": cluster.cluster,
                "reason": cluster.reason,
                "family": cluster.family,
                "languages": cluster.languages,
                "sample_pattern": group[0]["source_pattern"],
                "pattern_type": group[0]["pattern_type"],
                "skills": list(set(p["skill_name"] for p in group)),
            }

    def _normalize_pattern(self, pattern: str) -> str:
        """Normalize pattern for grouping."""
        # Remove backticks, normalize whitespace
        normalized = pattern.replace("`", "").strip().lower()
        # Remove common prefixes/suffixes
        normalized = re.sub(r"^(python|rust|java|etc\.?)\s*", "", normalized)
        return normalized[:50]  # Truncate for grouping

    def _determine_cluster(self, group: list[dict]) -> ClusterResult:
        """Determine cluster for a group of patterns."""
        # Get unique languages involved
        languages = set()
        families = set()

        for p in group:
            direction = p.get("direction", "")
            if "-to-" in direction:
                source, target = direction.split("-to-")
                languages.add(source)
                languages.add(target)
                if source in LANGUAGE_FAMILIES:
                    families.add(LANGUAGE_FAMILIES[source])
                if target in LANGUAGE_FAMILIES:
                    families.add(LANGUAGE_FAMILIES[target])

        # Determine cluster
        num_patterns = len(group)
        num_languages = len(languages)
        num_families = len(families)

        # Universal: appears in 5+ language pairs across 3+ families
        if num_patterns >= 5 and num_families >= 3:
            return ClusterResult(
                cluster="universal",
                reason=f"Appears in {num_patterns} patterns across {num_families} families",
                languages=list(languages),
            )

        # Family-specific: appears only within one family
        if num_families == 1 and num_patterns >= 2:
            family = list(families)[0] if families else "unknown"
            return ClusterResult(
                cluster="family",
                reason=f"Specific to {family} family ({num_patterns} patterns)",
                family=family,
                languages=list(languages),
            )

        # Language-specific: appears in only 1-2 language pairs
        if num_patterns <= 2:
            return ClusterResult(
                cluster="language",
                reason=f"Specific to {list(languages)} ({num_patterns} patterns)",
                languages=list(languages),
            )

        # Default to family if multiple families but not universal
        if num_families >= 2:
            return ClusterResult(
                cluster="family",
                reason=f"Shared across {num_families} families ({num_patterns} patterns)",
                languages=list(languages),
            )

        return ClusterResult(
            cluster="language",
            reason=f"Limited occurrence ({num_patterns} patterns)",
            languages=list(languages),
        )

    def analyze_gaps(self):
        """Analyze gaps in conversions."""
        # Analyze negative patterns
        negative_patterns = [p for p in self.patterns if p["pattern_type"] == "negative"]
        for p in negative_patterns:
            direction = p.get("direction", "")
            source, target = ("unknown", "unknown")
            if "-to-" in direction:
                source, target = direction.split("-to-")

            self.gaps.append(GapAnalysis(
                gap_type="negative",
                description=p["source_pattern"],
                severity="medium",
                source_lang=source,
                target_lang=target,
                mitigation=p.get("target_pattern", "") or p.get("notes", ""),
            ))

        # Analyze scope boundaries for impossible/lossy
        scope_patterns = [p for p in self.patterns if p["pattern_type"] == "scope_boundary"]
        for p in scope_patterns:
            direction = p.get("direction", "")
            source, target = ("unknown", "unknown")
            if "-to-" in direction:
                source, target = direction.split("-to-")

            # Determine if lossy or impossible
            notes = (p.get("notes", "") + " " + p.get("source_pattern", "")).lower()
            if any(kw in notes for kw in ["cannot", "impossible", "not supported", "no equivalent"]):
                gap_type = "impossible"
                severity = "critical"
            elif any(kw in notes for kw in ["lossy", "loss", "approximate", "partial"]):
                gap_type = "lossy"
                severity = "high"
            else:
                gap_type = "human_decision"
                severity = "medium"

            self.gaps.append(GapAnalysis(
                gap_type=gap_type,
                description=p["source_pattern"],
                severity=severity,
                source_lang=source,
                target_lang=target,
                mitigation=p.get("target_pattern", ""),
            ))

        # Analyze type mappings for lossy conversions
        type_patterns = [p for p in self.patterns if p["pattern_type"] == "type_mapping"]
        for p in type_patterns:
            notes = (p.get("notes", "") or "").lower()
            if any(kw in notes for kw in ["lossy", "loss", "truncat", "overflow", "precision"]):
                direction = p.get("direction", "")
                source, target = ("unknown", "unknown")
                if "-to-" in direction:
                    source, target = direction.split("-to-")

                self.gaps.append(GapAnalysis(
                    gap_type="lossy",
                    description=f"{p['source_pattern']} → {p['target_pattern']}",
                    severity="medium",
                    source_lang=source,
                    target_lang=target,
                    mitigation=notes,
                ))

    def save_results(self):
        """Save clustering and gap analysis results."""
        # Save clusters
        clusters_file = self.data_dir / "pattern-clusters.json"

        # Aggregate cluster statistics
        cluster_stats = defaultdict(lambda: {"count": 0, "patterns": 0})
        for key, data in self.clusters.items():
            cluster = data["cluster"]
            cluster_stats[cluster]["count"] += 1
            cluster_stats[cluster]["patterns"] += data["count"]

        clusters_output = {
            "summary": {
                "total_unique_patterns": len(self.clusters),
                "total_pattern_instances": sum(d["count"] for d in self.clusters.values()),
                "by_cluster": dict(cluster_stats),
            },
            "clusters": self.clusters,
        }

        clusters_file.write_text(json.dumps(clusters_output, indent=2))
        print(f"Saved clusters to {clusters_file}")

        # Save gaps
        gaps_file = self.data_dir / "gap-analysis.json"

        gap_stats = defaultdict(lambda: {"count": 0, "by_severity": defaultdict(int)})
        for gap in self.gaps:
            gap_stats[gap.gap_type]["count"] += 1
            gap_stats[gap.gap_type]["by_severity"][gap.severity] += 1

        gaps_output = {
            "summary": {
                "total_gaps": len(self.gaps),
                "by_type": {k: dict(v) for k, v in gap_stats.items()},
            },
            "gaps": [asdict(g) for g in self.gaps],
        }

        gaps_file.write_text(json.dumps(gaps_output, indent=2))
        print(f"Saved gap analysis to {gaps_file}")

        # Generate analysis report
        self._generate_report()

    def _generate_report(self):
        """Generate analysis report."""
        report_file = self.data_dir.parent / "analysis" / "clustering-and-gaps.md"

        # Cluster statistics
        cluster_counts = Counter(d["cluster"] for d in self.clusters.values())

        # Gap statistics
        gap_type_counts = Counter(g.gap_type for g in self.gaps)
        gap_severity_counts = Counter(g.severity for g in self.gaps)

        # Family coverage
        family_patterns = defaultdict(int)
        for data in self.clusters.values():
            if data["family"]:
                family_patterns[data["family"]] += data["count"]

        content = f"""# Pattern Clustering and Gap Analysis

## Clustering Summary

### Cluster Distribution

| Cluster | Unique Patterns | Pattern Instances |
|---------|-----------------|-------------------|
| Universal | {sum(1 for d in self.clusters.values() if d['cluster'] == 'universal')} | {sum(d['count'] for d in self.clusters.values() if d['cluster'] == 'universal')} |
| Family-specific | {sum(1 for d in self.clusters.values() if d['cluster'] == 'family')} | {sum(d['count'] for d in self.clusters.values() if d['cluster'] == 'family')} |
| Language-specific | {sum(1 for d in self.clusters.values() if d['cluster'] == 'language')} | {sum(d['count'] for d in self.clusters.values() if d['cluster'] == 'language')} |
| **Total** | **{len(self.clusters)}** | **{sum(d['count'] for d in self.clusters.values())}** |

### Family-Specific Pattern Counts

| Family | Pattern Instances |
|--------|-------------------|
"""
        for family, count in sorted(family_patterns.items(), key=lambda x: -x[1]):
            content += f"| {family} | {count} |\n"

        content += f"""
### Cluster Classification Criteria

- **Universal**: Appears in 5+ patterns across 3+ language families
- **Family-specific**: Appears within a single language family
- **Language-specific**: Appears in only 1-2 language pairs

## Gap Analysis Summary

### Gap Types

| Gap Type | Count | Description |
|----------|-------|-------------|
| negative | {gap_type_counts.get('negative', 0)} | Anti-patterns (what NOT to do) |
| human_decision | {gap_type_counts.get('human_decision', 0)} | Requires manual choice |
| lossy | {gap_type_counts.get('lossy', 0)} | Information loss in conversion |
| impossible | {gap_type_counts.get('impossible', 0)} | Cannot be translated |
| **Total** | **{len(self.gaps)}** | |

### Gap Severity Distribution

| Severity | Count |
|----------|-------|
| critical | {gap_severity_counts.get('critical', 0)} |
| high | {gap_severity_counts.get('high', 0)} |
| medium | {gap_severity_counts.get('medium', 0)} |
| low | {gap_severity_counts.get('low', 0)} |

## Key Findings

### Universal Patterns (apply to most conversions)

These patterns are good candidates for core IR constructs:

"""
        # List top universal patterns
        universal = [d for d in self.clusters.values() if d["cluster"] == "universal"]
        universal.sort(key=lambda x: -x["count"])
        for i, data in enumerate(universal[:10]):
            content += f"{i+1}. **{data['sample_pattern']}** ({data['count']} occurrences)\n"

        content += """
### Family-Specific Patterns

Patterns that are shared within language families but not universal:

"""
        # Group by family
        family_specific = [d for d in self.clusters.values() if d["cluster"] == "family" and d["family"]]
        families_grouped = defaultdict(list)
        for data in family_specific:
            families_grouped[data["family"]].append(data)

        for family, patterns in sorted(families_grouped.items()):
            content += f"#### {family.upper()} Family\n\n"
            for data in sorted(patterns, key=lambda x: -x["count"])[:5]:
                content += f"- {data['sample_pattern']} ({data['count']} patterns)\n"
            content += "\n"

        content += """
### Critical Gaps

Conversions that cannot be performed automatically:

"""
        critical_gaps = [g for g in self.gaps if g.severity == "critical"]
        for gap in critical_gaps[:15]:
            content += f"- **{gap.source_lang} → {gap.target_lang}**: {gap.description}\n"

        if len(critical_gaps) > 15:
            content += f"- ... and {len(critical_gaps) - 15} more\n"

        content += """
### Negative Patterns (Anti-patterns)

What NOT to do during conversion:

"""
        negative_gaps = [g for g in self.gaps if g.gap_type == "negative"]
        for gap in negative_gaps[:10]:
            content += f"- **{gap.source_lang} → {gap.target_lang}**: {gap.description}\n"
            if gap.mitigation:
                content += f"  - Instead: {gap.mitigation[:100]}...\n"

        content += """
## Recommendations for IR Design

Based on the clustering analysis:

1. **Core IR should support universal patterns first** - These have the widest applicability
2. **Family extensions for family-specific patterns** - ML-FP, BEAM, Systems families have distinct patterns
3. **Language annotations for unique features** - Ownership (Rust), Actors (BEAM), etc.
4. **Gap registry** - Track impossible/lossy conversions to warn users

## Data Files

- `pattern-clusters.json` - Full clustering data
- `gap-analysis.json` - Full gap analysis data
"""

        report_file.write_text(content)
        print(f"Saved report to {report_file}")


def main():
    data_dir = Path(".claude/plans/merge-convert-skills/data")

    analyzer = PatternAnalyzer(data_dir)

    print("Clustering patterns...")
    analyzer.cluster_patterns()

    print("Analyzing gaps...")
    analyzer.analyze_gaps()

    print("Saving results...")
    analyzer.save_results()

    # Print summary
    cluster_counts = Counter(d["cluster"] for d in analyzer.clusters.values())
    print("\nClustering complete:")
    print(f"  - Universal: {cluster_counts.get('universal', 0)}")
    print(f"  - Family-specific: {cluster_counts.get('family', 0)}")
    print(f"  - Language-specific: {cluster_counts.get('language', 0)}")

    gap_counts = Counter(g.gap_type for g in analyzer.gaps)
    print("\nGap analysis complete:")
    print(f"  - Negative patterns: {gap_counts.get('negative', 0)}")
    print(f"  - Human decisions: {gap_counts.get('human_decision', 0)}")
    print(f"  - Lossy conversions: {gap_counts.get('lossy', 0)}")
    print(f"  - Impossible: {gap_counts.get('impossible', 0)}")


if __name__ == "__main__":
    main()
