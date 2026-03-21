#!/usr/bin/env python3
"""
Pattern Extractor for convert-* skills.

Extracts structured patterns from convert-* SKILL.md files:
- Type mappings from markdown tables
- Idiom translations from code blocks
- Scope boundaries from "Does NOT Cover" sections
- Guidelines from "When Converting" sections
- Negative patterns from "Common Pitfalls"
- Tool recommendations from "Tooling" sections

Usage:
    python extract_patterns.py [--skill SKILL_NAME] [--output-dir DIR]
"""

import argparse
import hashlib
import json
import re
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Pattern:
    """Extracted pattern from a convert-* skill."""
    skill_name: str
    pattern_type: str  # type_mapping, idiom, gap, negative, guideline, scope_boundary, error, concurrency, tool
    source_pattern: str
    target_pattern: str = ""
    notes: str = ""
    category: str = ""  # For idioms: error-handling, concurrency, data-structure, etc.
    confidence: str = "high"  # high, medium, low
    is_bidirectional: bool = False
    direction: str = ""  # e.g., "python-to-rust" or "rust-to-python"
    section_source: str = ""  # Which markdown section this came from

    @property
    def id(self) -> str:
        """Generate unique ID for pattern."""
        content = f"{self.skill_name}:{self.pattern_type}:{self.source_pattern}:{self.direction}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]


@dataclass
class SkillMetadata:
    """Metadata about a convert-* skill."""
    name: str
    source_lang: str
    target_lang: str
    is_bidirectional: bool = False
    extends: str = "meta-convert-dev"
    description: str = ""


class PatternExtractor:
    """Extract patterns from convert-* skill files."""

    def __init__(self, skills_dir: Path, output_dir: Path):
        self.skills_dir = skills_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.progress_dir = output_dir / "extraction-progress"
        self.progress_dir.mkdir(exist_ok=True)

        self.patterns: list[Pattern] = []
        self.completed: set[str] = set()
        self.failed: dict[str, str] = {}

        self._load_progress()

    def _load_progress(self):
        """Load extraction progress from checkpoint files."""
        completed_file = self.progress_dir / "completed.txt"
        if completed_file.exists():
            self.completed = set(completed_file.read_text().strip().split("\n"))

    def _save_progress(self):
        """Save extraction progress to checkpoint files."""
        completed_file = self.progress_dir / "completed.txt"
        completed_file.write_text("\n".join(sorted(self.completed)))

        if self.failed:
            failed_file = self.progress_dir / "failed.txt"
            lines = [f"{k}: {v}" for k, v in self.failed.items()]
            failed_file.write_text("\n".join(lines))

    def extract_all(self, force: bool = False):
        """Extract patterns from all convert-* skills."""
        skill_dirs = sorted(self.skills_dir.glob("convert-*/"))

        for skill_dir in skill_dirs:
            skill_name = skill_dir.name

            if not force and skill_name in self.completed:
                print(f"Skipping {skill_name} (already processed)")
                continue

            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                self.failed[skill_name] = "SKILL.md not found"
                continue

            try:
                self.extract_skill(skill_name, skill_file)
                self.completed.add(skill_name)
                print(f"✓ Extracted {skill_name}")
            except Exception as e:
                self.failed[skill_name] = str(e)
                print(f"✗ Failed {skill_name}: {e}")

            self._save_progress()

        print(f"\nCompleted: {len(self.completed)}, Failed: {len(self.failed)}")

    def extract_skill(self, skill_name: str, skill_file: Path):
        """Extract patterns from a single skill file."""
        content = skill_file.read_text()

        # Parse metadata
        metadata = self._parse_metadata(skill_name, content)

        # Extract patterns from different sections
        self._extract_type_mappings(content, metadata)
        self._extract_scope_boundaries(content, metadata)
        self._extract_guidelines(content, metadata)
        self._extract_pitfalls(content, metadata)
        self._extract_tooling(content, metadata)
        self._extract_idioms(content, metadata)
        self._extract_error_handling(content, metadata)
        self._extract_concurrency(content, metadata)

        # Save intermediate results
        self._save_skill_patterns(skill_name)

    def _parse_metadata(self, skill_name: str, content: str) -> SkillMetadata:
        """Parse skill metadata from frontmatter and content."""
        # Extract source and target from skill name
        match = re.match(r"convert-(\w+)-(\w+)", skill_name)
        if not match:
            raise ValueError(f"Invalid skill name format: {skill_name}")

        source_lang, target_lang = match.groups()

        # Check if bidirectional
        is_bidirectional = any(marker in content.lower() for marker in [
            "bidirectional",
            "both directions",
            "↔",
            f"{target_lang} to {source_lang}",
            f"{target_lang} → {source_lang}",
        ])

        # Extract description from frontmatter
        description = ""
        desc_match = re.search(r"description:\s*['\"]?(.+?)['\"]?\s*\n", content)
        if desc_match:
            description = desc_match.group(1).strip()

        return SkillMetadata(
            name=skill_name,
            source_lang=source_lang,
            target_lang=target_lang,
            is_bidirectional=is_bidirectional,
            description=description,
        )

    def _extract_type_mappings(self, content: str, metadata: SkillMetadata):
        """Extract type mappings from markdown tables."""
        # Find tables with type-like headers
        table_pattern = r"\|(.+)\|\s*\n\|[-| ]+\|\s*\n((?:\|.+\|\s*\n)+)"

        for match in re.finditer(table_pattern, content):
            header = match.group(1)
            rows = match.group(2)

            # Check if this looks like a type mapping table
            header_lower = header.lower()
            if not any(kw in header_lower for kw in ["type", "python", "rust", "java", "source", "target", metadata.source_lang, metadata.target_lang]):
                continue

            # Parse header columns
            columns = [c.strip() for c in header.split("|") if c.strip()]
            if len(columns) < 2:
                continue

            # Find source and target column indices
            source_idx = None
            target_idx = None
            notes_idx = None

            for i, col in enumerate(columns):
                col_lower = col.lower()
                if metadata.source_lang in col_lower or col_lower == "source":
                    source_idx = i
                elif metadata.target_lang in col_lower or col_lower == "target":
                    target_idx = i
                elif "note" in col_lower:
                    notes_idx = i

            # Default to first two columns if not found
            if source_idx is None:
                source_idx = 0
            if target_idx is None:
                target_idx = 1 if len(columns) > 1 else 0

            # Parse rows
            for row in rows.strip().split("\n"):
                cells = [c.strip() for c in row.split("|") if c.strip()]
                if len(cells) < 2:
                    continue

                source_type = cells[source_idx] if source_idx < len(cells) else ""
                target_type = cells[target_idx] if target_idx < len(cells) else ""
                notes = cells[notes_idx] if notes_idx and notes_idx < len(cells) else ""

                if source_type and target_type:
                    # Primary direction
                    self.patterns.append(Pattern(
                        skill_name=metadata.name,
                        pattern_type="type_mapping",
                        source_pattern=source_type,
                        target_pattern=target_type,
                        notes=notes,
                        is_bidirectional=metadata.is_bidirectional,
                        direction=f"{metadata.source_lang}-to-{metadata.target_lang}",
                        section_source="type_mapping_table",
                    ))

                    # Reverse direction for bidirectional skills
                    if metadata.is_bidirectional:
                        self.patterns.append(Pattern(
                            skill_name=metadata.name,
                            pattern_type="type_mapping",
                            source_pattern=target_type,
                            target_pattern=source_type,
                            notes=notes,
                            is_bidirectional=True,
                            direction=f"{metadata.target_lang}-to-{metadata.source_lang}",
                            section_source="type_mapping_table",
                        ))

    def _extract_scope_boundaries(self, content: str, metadata: SkillMetadata):
        """Extract scope boundaries from 'Does NOT Cover' section."""
        # Find the section
        section_match = re.search(
            r"##\s+This Skill Does NOT Cover\s*\n(.*?)(?=\n##|\Z)",
            content,
            re.DOTALL | re.IGNORECASE
        )

        if not section_match:
            return

        section_content = section_match.group(1)

        # Extract list items
        for item_match in re.finditer(r"^[-*]\s+(.+?)(?:\s*-\s*see\s+`?([^`\n]+)`?)?$", section_content, re.MULTILINE):
            excluded = item_match.group(1).strip()
            see_instead = item_match.group(2).strip() if item_match.group(2) else ""

            self.patterns.append(Pattern(
                skill_name=metadata.name,
                pattern_type="scope_boundary",
                source_pattern=excluded,
                target_pattern=see_instead,
                notes="",
                is_bidirectional=metadata.is_bidirectional,
                direction=f"{metadata.source_lang}-to-{metadata.target_lang}",
                section_source="does_not_cover",
            ))

    def _extract_guidelines(self, content: str, metadata: SkillMetadata):
        """Extract guidelines from 'When Converting' section."""
        section_match = re.search(
            r"##\s+When Converting.*?\s*\n(.*?)(?=\n##|\Z)",
            content,
            re.DOTALL | re.IGNORECASE
        )

        if not section_match:
            return

        section_content = section_match.group(1)

        # Extract numbered items
        for item_match in re.finditer(r"^\d+\.\s+\*\*(.+?)\*\*\s*[-–—]?\s*(.+?)$", section_content, re.MULTILINE):
            action = item_match.group(1).strip()
            rationale = item_match.group(2).strip()

            self.patterns.append(Pattern(
                skill_name=metadata.name,
                pattern_type="guideline",
                source_pattern=action,
                target_pattern="",
                notes=rationale,
                is_bidirectional=metadata.is_bidirectional,
                direction=f"{metadata.source_lang}-to-{metadata.target_lang}",
                section_source="when_converting",
            ))

    def _extract_pitfalls(self, content: str, metadata: SkillMetadata):
        """Extract negative patterns from 'Common Pitfalls' section."""
        section_match = re.search(
            r"##\s+Common Pitfalls\s*\n(.*?)(?=\n##|\Z)",
            content,
            re.DOTALL | re.IGNORECASE
        )

        if not section_match:
            return

        section_content = section_match.group(1)

        # Extract pitfall sections (### N. Title)
        pitfall_pattern = r"###\s+\d+\.\s+(.+?)\s*\n(.*?)(?=###\s+\d+\.|\Z)"

        for match in re.finditer(pitfall_pattern, section_content, re.DOTALL):
            title = match.group(1).strip()
            body = match.group(2).strip()

            # Extract Problem and Solution
            problem = ""
            solution = ""

            problem_match = re.search(r"\*\*Problem[:\*]*\*\*\s*(.+?)(?=\*\*Solution|\*\*$|\Z)", body, re.DOTALL)
            if problem_match:
                problem = problem_match.group(1).strip()

            solution_match = re.search(r"\*\*Solution[:\*]*\*\*\s*(.+?)(?=\*\*|\Z)", body, re.DOTALL)
            if solution_match:
                solution = solution_match.group(1).strip()

            self.patterns.append(Pattern(
                skill_name=metadata.name,
                pattern_type="negative",
                source_pattern=title,
                target_pattern=solution,
                notes=problem,
                is_bidirectional=metadata.is_bidirectional,
                direction=f"{metadata.source_lang}-to-{metadata.target_lang}",
                section_source="common_pitfalls",
            ))

    def _extract_tooling(self, content: str, metadata: SkillMetadata):
        """Extract tool recommendations from 'Tooling' section."""
        section_match = re.search(
            r"##\s+Tooling\s*\n(.*?)(?=\n##|\Z)",
            content,
            re.DOTALL | re.IGNORECASE
        )

        if not section_match:
            return

        section_content = section_match.group(1)

        # Find tooling tables
        table_pattern = r"\|(.+)\|\s*\n\|[-| ]+\|\s*\n((?:\|.+\|\s*\n)+)"

        for match in re.finditer(table_pattern, section_content):
            header = match.group(1)
            rows = match.group(2)

            columns = [c.strip() for c in header.split("|") if c.strip()]
            if len(columns) < 2:
                continue

            for row in rows.strip().split("\n"):
                cells = [c.strip() for c in row.split("|") if c.strip()]
                if len(cells) < 2:
                    continue

                tool = cells[0]
                purpose = cells[1] if len(cells) > 1 else ""
                notes = cells[2] if len(cells) > 2 else ""

                self.patterns.append(Pattern(
                    skill_name=metadata.name,
                    pattern_type="tool",
                    source_pattern=tool,
                    target_pattern=purpose,
                    notes=notes,
                    is_bidirectional=metadata.is_bidirectional,
                    direction=f"{metadata.source_lang}-to-{metadata.target_lang}",
                    section_source="tooling",
                ))

    def _extract_idioms(self, content: str, metadata: SkillMetadata):
        """Extract idiom translations from 'Idiom Translation' section."""
        section_match = re.search(
            r"##\s+Idiom Translation\s*\n(.*?)(?=\n##\s+[A-Z]|\Z)",
            content,
            re.DOTALL | re.IGNORECASE
        )

        if not section_match:
            return

        section_content = section_match.group(1)

        # Find pattern/pillar sections
        pattern_pattern = r"###\s+(?:Pattern|Pillar)\s+\d+[:.]\s*(.+?)\s*\n(.*?)(?=###\s+(?:Pattern|Pillar)|\Z)"

        for match in re.finditer(pattern_pattern, section_content, re.DOTALL):
            name = match.group(1).strip()
            body = match.group(2).strip()

            # Extract "Why this translation" explanation
            explanation = ""
            why_match = re.search(r"\*\*Why this translation[:\*]*\*\*\s*(.+?)(?=\n\n---|\Z)", body, re.DOTALL)
            if why_match:
                explanation = why_match.group(1).strip()

            # Determine category from name
            category = self._categorize_idiom(name)

            self.patterns.append(Pattern(
                skill_name=metadata.name,
                pattern_type="idiom",
                source_pattern=name,
                target_pattern="",
                notes=explanation[:500] if explanation else "",  # Truncate long explanations
                category=category,
                is_bidirectional=metadata.is_bidirectional,
                direction=f"{metadata.source_lang}-to-{metadata.target_lang}",
                section_source="idiom_translation",
            ))

    def _extract_error_handling(self, content: str, metadata: SkillMetadata):
        """Extract error handling patterns."""
        section_match = re.search(
            r"##\s+Error Handling\s*\n(.*?)(?=\n##|\Z)",
            content,
            re.DOTALL | re.IGNORECASE
        )

        if not section_match:
            return

        section_content = section_match.group(1)

        # Find tables mapping error handling approaches
        table_pattern = r"\|(.+)\|\s*\n\|[-| ]+\|\s*\n((?:\|.+\|\s*\n)+)"

        for match in re.finditer(table_pattern, section_content):
            header = match.group(1)
            rows = match.group(2)

            columns = [c.strip() for c in header.split("|") if c.strip()]
            if len(columns) < 2:
                continue

            for row in rows.strip().split("\n"):
                cells = [c.strip() for c in row.split("|") if c.strip()]
                if len(cells) < 2:
                    continue

                source_approach = cells[0]
                target_approach = cells[1] if len(cells) > 1 else ""
                notes = cells[2] if len(cells) > 2 else ""

                self.patterns.append(Pattern(
                    skill_name=metadata.name,
                    pattern_type="error",
                    source_pattern=source_approach,
                    target_pattern=target_approach,
                    notes=notes,
                    is_bidirectional=metadata.is_bidirectional,
                    direction=f"{metadata.source_lang}-to-{metadata.target_lang}",
                    section_source="error_handling",
                ))

    def _extract_concurrency(self, content: str, metadata: SkillMetadata):
        """Extract concurrency patterns."""
        section_match = re.search(
            r"##\s+Concurrency Patterns?\s*\n(.*?)(?=\n##|\Z)",
            content,
            re.DOTALL | re.IGNORECASE
        )

        if not section_match:
            return

        section_content = section_match.group(1)

        # Find tables mapping concurrency approaches
        table_pattern = r"\|(.+)\|\s*\n\|[-| ]+\|\s*\n((?:\|.+\|\s*\n)+)"

        for match in re.finditer(table_pattern, section_content):
            header = match.group(1)
            rows = match.group(2)

            columns = [c.strip() for c in header.split("|") if c.strip()]
            if len(columns) < 2:
                continue

            for row in rows.strip().split("\n"):
                cells = [c.strip() for c in row.split("|") if c.strip()]
                if len(cells) < 2:
                    continue

                source_model = cells[0]
                target_model = cells[1] if len(cells) > 1 else ""
                notes = cells[2] if len(cells) > 2 else ""

                self.patterns.append(Pattern(
                    skill_name=metadata.name,
                    pattern_type="concurrency",
                    source_pattern=source_model,
                    target_pattern=target_model,
                    notes=notes,
                    is_bidirectional=metadata.is_bidirectional,
                    direction=f"{metadata.source_lang}-to-{metadata.target_lang}",
                    section_source="concurrency",
                ))

    def _categorize_idiom(self, name: str) -> str:
        """Categorize an idiom based on its name."""
        name_lower = name.lower()

        categories = {
            "error": ["error", "exception", "result", "try", "catch", "panic"],
            "concurrency": ["async", "await", "thread", "spawn", "channel", "actor", "concurrent", "parallel"],
            "data-structure": ["list", "map", "dict", "array", "collection", "tuple", "struct", "class", "record"],
            "control-flow": ["loop", "match", "pattern", "guard", "if", "switch", "iteration"],
            "memory": ["ownership", "borrow", "lifetime", "reference", "pointer", "gc", "allocation"],
            "function": ["function", "closure", "lambda", "callback", "method"],
            "module": ["module", "import", "export", "namespace", "package"],
            "type": ["type", "generic", "trait", "interface", "protocol"],
        }

        for category, keywords in categories.items():
            if any(kw in name_lower for kw in keywords):
                return category

        return "general"

    def _save_skill_patterns(self, skill_name: str):
        """Save patterns for a skill to intermediate file."""
        skill_patterns = [p for p in self.patterns if p.skill_name == skill_name]
        output_file = self.progress_dir / f"{skill_name}.json"

        with open(output_file, "w") as f:
            json.dump([asdict(p) for p in skill_patterns], f, indent=2)

    def save_all(self):
        """Save all patterns to output files."""
        # Save as JSON
        json_file = self.output_dir / "patterns.json"
        with open(json_file, "w") as f:
            json.dump([asdict(p) for p in self.patterns], f, indent=2)

        # Save as SQL
        self._save_sql()

        # Save summary
        self._save_summary()

        print(f"\nSaved {len(self.patterns)} patterns to {self.output_dir}")

    def _save_sql(self):
        """Save patterns to SQLite database and SQL dump."""
        db_file = self.output_dir / "patterns.db"
        sql_file = self.output_dir / "patterns.sql"

        # Create database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id TEXT PRIMARY KEY,
                skill_name TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                source_pattern TEXT NOT NULL,
                target_pattern TEXT,
                notes TEXT,
                category TEXT,
                confidence TEXT DEFAULT 'high',
                is_bidirectional BOOLEAN DEFAULT FALSE,
                direction TEXT,
                section_source TEXT
            )
        """)

        # Insert patterns
        for p in self.patterns:
            cursor.execute("""
                INSERT OR REPLACE INTO patterns
                (id, skill_name, pattern_type, source_pattern, target_pattern,
                 notes, category, confidence, is_bidirectional, direction, section_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p.id, p.skill_name, p.pattern_type, p.source_pattern, p.target_pattern,
                p.notes, p.category, p.confidence, p.is_bidirectional, p.direction, p.section_source
            ))

        conn.commit()

        # Dump to SQL
        with open(sql_file, "w") as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")

        conn.close()

    def _save_summary(self):
        """Save extraction summary."""
        summary_file = self.output_dir / "extraction-summary.md"

        # Count patterns by type
        type_counts = {}
        for p in self.patterns:
            type_counts[p.pattern_type] = type_counts.get(p.pattern_type, 0) + 1

        # Count patterns by skill
        skill_counts = {}
        for p in self.patterns:
            skill_counts[p.skill_name] = skill_counts.get(p.skill_name, 0) + 1

        # Count bidirectional extractions
        bidirectional_count = len([p for p in self.patterns if p.is_bidirectional])

        content = f"""# Pattern Extraction Summary

## Overview

- **Total patterns extracted**: {len(self.patterns)}
- **Skills processed**: {len(self.completed)}
- **Skills failed**: {len(self.failed)}
- **Bidirectional patterns**: {bidirectional_count}

## Patterns by Type

| Type | Count |
|------|-------|
"""
        for ptype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            content += f"| {ptype} | {count} |\n"

        content += """
## Patterns by Skill

| Skill | Count |
|-------|-------|
"""
        for skill, count in sorted(skill_counts.items(), key=lambda x: -x[1])[:20]:
            content += f"| {skill} | {count} |\n"

        if len(skill_counts) > 20:
            content += "| ... | ... |\n"

        if self.failed:
            content += """
## Failed Extractions

| Skill | Error |
|-------|-------|
"""
            for skill, error in self.failed.items():
                content += f"| {skill} | {error} |\n"

        summary_file.write_text(content)


def main():
    parser = argparse.ArgumentParser(description="Extract patterns from convert-* skills")
    parser.add_argument("--skills-dir", type=Path, default=Path("context/skills"),
                        help="Directory containing skills")
    parser.add_argument("--output-dir", type=Path, default=Path(".claude/plans/merge-convert-skills/data"),
                        help="Output directory for extracted patterns")
    parser.add_argument("--skill", type=str, help="Extract from single skill only")
    parser.add_argument("--force", action="store_true", help="Force re-extraction")

    args = parser.parse_args()

    extractor = PatternExtractor(args.skills_dir, args.output_dir)

    if args.skill:
        skill_file = args.skills_dir / args.skill / "SKILL.md"
        if skill_file.exists():
            extractor.extract_skill(args.skill, skill_file)
            extractor.save_all()
        else:
            print(f"Skill not found: {args.skill}")
    else:
        extractor.extract_all(force=args.force)
        extractor.save_all()


if __name__ == "__main__":
    main()
