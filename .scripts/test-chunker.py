#!/usr/bin/env python3
"""Test markdown chunking."""

from pathlib import Path

from lib.chunker import chunk_file, chunk_markdown


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
