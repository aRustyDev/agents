#!/usr/bin/env python3
"""
Merge bidirectional convert-X-Y skills.

For each pair (convert-A-B and convert-B-A), this script:
1. Updates the kept skill's frontmatter to indicate bidirectional capability
2. Removes the "Reverse conversion" reference
3. Deletes the reverse skill directory
"""

import re
import shutil
from pathlib import Path


def parse_skill_name(name: str) -> tuple[str, str] | tuple[None, None]:
    """Parse convert-X-Y into (X, Y)."""
    match = re.match(r"convert-([a-z0-9+#-]+)-([a-z0-9+#-]+)$", name)
    if match:
        return match.group(1), match.group(2)
    return None, None


def find_bidirectional_pairs(skills_dir: Path) -> list[dict]:
    """Find all bidirectional pairs."""
    convert_skills = sorted(
        [d.name for d in skills_dir.iterdir() if d.is_dir() and d.name.startswith("convert-")]
    )

    pairs = []
    seen = set()

    for skill in convert_skills:
        src, tgt = parse_skill_name(skill)
        if not src:
            continue

        reverse = f"convert-{tgt}-{src}"
        pair_key = tuple(sorted([skill, reverse]))

        if reverse in convert_skills and pair_key not in seen:
            seen.add(pair_key)
            # Keep alphabetically first
            keep = min(skill, reverse)
            delete = max(skill, reverse)
            pairs.append(
                {
                    "keep": keep,
                    "delete": delete,
                    "lang1": min(src, tgt),
                    "lang2": max(src, tgt),
                }
            )

    return pairs


def update_skill_frontmatter(skill_path: Path, lang1: str, lang2: str) -> str:
    """Update the SKILL.md frontmatter to indicate bidirectional capability."""
    content = skill_path.read_text()

    new_desc = (
        f"description: Bidirectional conversion between {lang1.title()} and {lang2.title()}. "
        f"Use when migrating projects between these languages in either direction. "
        f"Extends meta-convert-dev with {lang1.title()}↔{lang2.title()} specific patterns."
    )

    # Pattern 1: "Convert X code to idiomatic Y."
    pattern1 = rf"(description: )Convert {lang1} code to idiomatic {lang2}\."
    # Pattern 2: "Converts X code to idiomatic Y" (with Converts, no period)
    pattern2 = rf"(description: )Converts {lang1} code to idiomatic {lang2}"
    # Pattern 3: Generic conversion description
    pattern3 = r"(description: )(Converts?|Convert) .+ code to idiomatic .+"

    if re.search(pattern1, content, re.IGNORECASE):
        content = re.sub(pattern1, rf"\1{new_desc}", content, flags=re.IGNORECASE)
    elif re.search(pattern2, content, re.IGNORECASE):
        # Replace the entire description line
        content = re.sub(
            r"description: Converts .+?\n",
            f"description: {new_desc}\n",
            content,
            count=1,
        )
    elif re.search(pattern3, content, re.IGNORECASE):
        content = re.sub(
            r"description: (Converts?|Convert) .+?\n",
            f"description: {new_desc}\n",
            content,
            count=1,
        )

    return content


def update_skill_title(content: str, lang1: str, lang2: str) -> str:
    """Update the main title to indicate bidirectional."""
    new_title = f"# {lang1.title()} ↔ {lang2.title()} Conversion"

    # Pattern 1: "# Convert X to Y"
    pattern1 = rf"# Convert {lang1.title()} to {lang2.title()}"
    # Pattern 2: "# X to Y Conversion"
    pattern2 = rf"# {lang1.title()} to {lang2.title()} Conversion"

    if re.search(pattern1, content, re.IGNORECASE):
        content = re.sub(pattern1, new_title, content, flags=re.IGNORECASE)
    elif re.search(pattern2, content, re.IGNORECASE):
        content = re.sub(pattern2, new_title, content, flags=re.IGNORECASE)

    return content


def update_skill_intro(content: str, lang1: str, lang2: str) -> str:
    """Update the intro paragraph."""
    new_intro = (
        f"Bidirectional conversion between {lang1.title()} and {lang2.title()}. "
        f"This skill extends `meta-convert-dev` with {lang1.title()}↔{lang2.title()} specific"
    )

    # Pattern 1: Standard intro with meta-convert-dev reference
    pattern1 = (
        rf"Convert {lang1.title()} code to idiomatic {lang2.title()}\. "
        rf"This skill extends `meta-convert-dev` with {lang1.title()}-to-{lang2.title()} specific"
    )
    if re.search(pattern1, content, re.IGNORECASE):
        content = re.sub(pattern1, new_intro, content, flags=re.IGNORECASE)

    return content


def remove_reverse_reference(content: str, reverse_skill: str) -> str:
    """Remove the 'Reverse conversion' line from 'This Skill Does NOT Cover'."""
    pattern = rf"- Reverse conversion \([^)]+\) - see `{reverse_skill}`\n?"
    content = re.sub(pattern, "", content)
    return content


def update_see_also(content: str, reverse_skill: str) -> str:
    """Update See Also section to remove reverse reference."""
    pattern = rf"- `{reverse_skill}` - .*?\n"
    content = re.sub(pattern, "", content)
    return content


def merge_skill(skills_dir: Path, pair: dict, dry_run: bool = False) -> None:
    """Merge a bidirectional skill pair."""
    keep_dir = skills_dir / pair["keep"]
    delete_dir = skills_dir / pair["delete"]
    skill_path = keep_dir / "SKILL.md"

    if not skill_path.exists():
        print(f"  SKIP: {skill_path} not found")
        return

    # Determine language order from the kept skill name
    src, tgt = parse_skill_name(pair["keep"])
    reverse_skill = pair["delete"]

    # Read and update content
    content = skill_path.read_text()
    original_content = content

    # Apply updates
    content = update_skill_frontmatter(skill_path, src, tgt)
    content = update_skill_title(content, src, tgt)
    content = update_skill_intro(content, src, tgt)
    content = remove_reverse_reference(content, reverse_skill)
    content = update_see_also(content, reverse_skill)

    if dry_run:
        if content != original_content:
            print(f"  Would update: {skill_path}")
        print(f"  Would delete: {delete_dir}")
    else:
        # Write updated content
        if content != original_content:
            skill_path.write_text(content)
            print(f"  Updated: {skill_path}")

        # Delete reverse skill directory
        if delete_dir.exists():
            shutil.rmtree(delete_dir)
            print(f"  Deleted: {delete_dir}")


def main():
    import sys

    dry_run = "--dry-run" in sys.argv
    skills_dir = Path("context/skills")

    if not skills_dir.exists():
        print(f"Error: {skills_dir} not found")
        sys.exit(1)

    pairs = find_bidirectional_pairs(skills_dir)
    print(f"Found {len(pairs)} bidirectional pairs to merge")
    if dry_run:
        print("DRY RUN - no changes will be made\n")
    print()

    for i, pair in enumerate(pairs, 1):
        print(f"{i:2}. Merging {pair['keep']} ← {pair['delete']}")
        merge_skill(skills_dir, pair, dry_run=dry_run)
        print()

    if not dry_run:
        print(f"Done! Merged {len(pairs)} pairs.")
        print(f"Skills reduced from 78 to {78 - len(pairs)}")


if __name__ == "__main__":
    main()
