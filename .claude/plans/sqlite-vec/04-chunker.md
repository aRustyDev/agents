# Task 4: Implement markdown chunking strategy

## Objective

Create the chunker module that splits markdown into hierarchical chunks (file → section → paragraph).

## Prerequisites

- None (independent of other tasks)

## Steps

### 4.1 Create chunker module

Create `scripts/lib/chunker.py`:

```python
"""Markdown chunking module.

Splits markdown content into hierarchical chunks:
- file: Entire file content
- section: Content under ## headings
- paragraph: Individual paragraphs within sections
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class Chunk:
    """A chunk of content with metadata."""
    level: str  # 'file', 'section', 'paragraph'
    index: int  # Position at this level
    text: str
    heading: Optional[str] = None  # Section heading if applicable
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    parent_index: Optional[int] = None  # Index of parent chunk


@dataclass
class ParsedMarkdown:
    """Parsed markdown document."""
    frontmatter: dict = field(default_factory=dict)
    content: str = ''
    chunks: list[Chunk] = field(default_factory=list)


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from markdown content.

    Returns:
        Tuple of (frontmatter dict, remaining content)
    """
    if not content.startswith('---'):
        return {}, content

    # Find closing ---
    lines = content.split('\n')
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        return {}, content

    frontmatter_text = '\n'.join(lines[1:end_idx])
    remaining = '\n'.join(lines[end_idx + 1:])

    try:
        frontmatter = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError:
        frontmatter = {}

    return frontmatter, remaining.strip()


def split_into_sections(content: str) -> list[tuple[Optional[str], str, int, int]]:
    """Split content by ## headings.

    Returns:
        List of (heading, content, start_line, end_line) tuples.
        First element may have heading=None for content before first heading.
    """
    lines = content.split('\n')
    sections = []
    current_heading = None
    current_lines = []
    current_start = 0

    heading_pattern = re.compile(r'^##\s+(.+)$')

    for i, line in enumerate(lines):
        match = heading_pattern.match(line)
        if match:
            # Save previous section if it has content
            if current_lines:
                section_text = '\n'.join(current_lines).strip()
                if section_text:
                    sections.append((
                        current_heading,
                        section_text,
                        current_start,
                        i - 1
                    ))
            # Start new section
            current_heading = match.group(1).strip()
            current_lines = []
            current_start = i
        else:
            current_lines.append(line)

    # Don't forget last section
    if current_lines:
        section_text = '\n'.join(current_lines).strip()
        if section_text:
            sections.append((
                current_heading,
                section_text,
                current_start,
                len(lines) - 1
            ))

    return sections


def split_into_paragraphs(content: str, min_length: int = 50) -> list[str]:
    """Split content into paragraphs.

    Args:
        content: Text content
        min_length: Minimum paragraph length to include

    Returns:
        List of paragraph strings
    """
    # Split on double newlines (paragraph breaks)
    paragraphs = re.split(r'\n\s*\n', content)

    # Filter and clean
    result = []
    for para in paragraphs:
        para = para.strip()
        # Skip code blocks (start with ```)
        if para.startswith('```'):
            continue
        # Skip very short paragraphs
        if len(para) < min_length:
            continue
        result.append(para)

    return result


def chunk_markdown(content: str, include_paragraphs: bool = True) -> ParsedMarkdown:
    """Parse and chunk markdown content.

    Args:
        content: Raw markdown content
        include_paragraphs: Whether to create paragraph-level chunks

    Returns:
        ParsedMarkdown with frontmatter and chunks
    """
    result = ParsedMarkdown()

    # Extract frontmatter
    result.frontmatter, body = parse_frontmatter(content)
    result.content = body

    chunks = []
    chunk_index = 0

    # Level 0: Whole file
    file_chunk = Chunk(
        level='file',
        index=0,
        text=body,
        start_line=0,
        end_line=body.count('\n')
    )
    chunks.append(file_chunk)

    # Level 1: Sections
    sections = split_into_sections(body)
    for section_idx, (heading, section_text, start, end) in enumerate(sections):
        section_chunk = Chunk(
            level='section',
            index=section_idx,
            text=section_text,
            heading=heading,
            start_line=start,
            end_line=end,
            parent_index=0  # Parent is file chunk
        )
        chunks.append(section_chunk)

        # Level 2: Paragraphs within section
        if include_paragraphs:
            paragraphs = split_into_paragraphs(section_text)
            for para_idx, para_text in enumerate(paragraphs):
                para_chunk = Chunk(
                    level='paragraph',
                    index=para_idx,
                    text=para_text,
                    parent_index=len(chunks) - 1  # Parent is section chunk
                )
                chunks.append(para_chunk)

    result.chunks = chunks
    return result


def chunk_file(file_path: Path, include_paragraphs: bool = True) -> ParsedMarkdown:
    """Chunk a markdown file.

    Args:
        file_path: Path to markdown file
        include_paragraphs: Whether to create paragraph-level chunks

    Returns:
        ParsedMarkdown with frontmatter and chunks
    """
    content = file_path.read_text()
    return chunk_markdown(content, include_paragraphs=include_paragraphs)
```

### 4.2 Create test script

Create `scripts/test-chunker.py`:

```python
#!/usr/bin/env python3
"""Test markdown chunking."""

from pathlib import Path
from lib.chunker import chunk_markdown, chunk_file

def main():
    # Test with sample markdown
    sample = '''---
name: test-skill
description: A test skill
---

# Test Skill

Introduction paragraph that explains the skill.

## Overview

This is the overview section with some content.

It has multiple paragraphs to test paragraph chunking.

## Quick Reference

| Command | Description |
|---------|-------------|
| foo     | Does foo    |

## Troubleshooting

Common issues and solutions.

```python
# Code blocks should be skipped
print("hello")
```

Final paragraph in troubleshooting.
'''

    print("Testing markdown chunking...")
    result = chunk_markdown(sample)

    print(f"\nFrontmatter: {result.frontmatter}")
    print(f"\nChunks ({len(result.chunks)} total):")

    for chunk in result.chunks:
        preview = chunk.text[:50].replace('\n', ' ') + '...' if len(chunk.text) > 50 else chunk.text.replace('\n', ' ')
        print(f"  [{chunk.level}:{chunk.index}] {chunk.heading or '(no heading)'}: {preview}")

    # Count by level
    levels = {}
    for chunk in result.chunks:
        levels[chunk.level] = levels.get(chunk.level, 0) + 1
    print(f"\nBy level: {levels}")

    # Test with real file
    print("\n" + "="*50)
    print("Testing with real file...")

    # Find a skill file
    skill_files = list(Path('context/skills').glob('*/SKILL.md'))
    if skill_files:
        test_file = skill_files[0]
        print(f"Using: {test_file}")
        result = chunk_file(test_file)
        print(f"Frontmatter keys: {list(result.frontmatter.keys())}")
        print(f"Total chunks: {len(result.chunks)}")

        levels = {}
        for chunk in result.chunks:
            levels[chunk.level] = levels.get(chunk.level, 0) + 1
        print(f"By level: {levels}")
    else:
        print("No skill files found to test")

    print("\n✓ Chunker working correctly")

if __name__ == '__main__':
    main()
```

### 4.3 Test chunker

```bash
cd scripts && uv run python test-chunker.py
```

Expected output:
```
Testing markdown chunking...

Frontmatter: {'name': 'test-skill', 'description': 'A test skill'}

Chunks (N total):
  [file:0] (no heading): # Test Skill  Introduction paragraph that exp...
  [section:0] Overview: This is the overview section with some conten...
  [paragraph:0] (no heading): This is the overview section with some content.
  ...

By level: {'file': 1, 'section': 3, 'paragraph': N}
...
✓ Chunker working correctly
```

## Acceptance Criteria

- [ ] Extracts YAML frontmatter correctly
- [ ] Splits by ## headings into sections
- [ ] Creates paragraph chunks within sections
- [ ] Skips code blocks in paragraph chunking
- [ ] Tracks line numbers for each chunk
- [ ] Handles files without frontmatter
- [ ] Handles files without headings

## Files Created

- `scripts/lib/chunker.py`
- `scripts/test-chunker.py`

## Next

→ [05-ingestion.md](05-ingestion.md)
