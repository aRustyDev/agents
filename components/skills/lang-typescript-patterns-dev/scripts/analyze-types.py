#!/usr/bin/env python3
"""
TypeScript Type Analysis Script

Analyzes TypeScript files for type patterns, any usage, and type coverage.

Usage:
    python3 scripts/analyze-types.py [path] [--strict] [--report]

Arguments:
    path        Directory or file to analyze (default: current directory)
    --strict    Flag any usage of 'any' as an error
    --report    Generate detailed markdown report
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import NamedTuple


class TypeIssue(NamedTuple):
    file: str
    line: int
    category: str
    message: str
    severity: str  # 'error', 'warning', 'info'


def find_typescript_files(path: Path) -> list[Path]:
    """Find all TypeScript files in path."""
    if path.is_file():
        return [path] if path.suffix in ('.ts', '.tsx') else []

    files = []
    for pattern in ('**/*.ts', '**/*.tsx'):
        files.extend(path.glob(pattern))

    # Exclude common directories
    exclude = {'node_modules', 'dist', 'build', '.next', 'coverage'}
    return [f for f in files if not any(ex in f.parts for ex in exclude)]


def analyze_file(file_path: Path, strict: bool = False) -> list[TypeIssue]:
    """Analyze a single TypeScript file for type issues."""
    issues = []
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        # Check for explicit 'any' usage
        if re.search(r'\bany\b', line) and not re.search(r'//.*any|/\*.*any', line):
            issues.append(TypeIssue(
                file=str(file_path),
                line=line_num,
                category='any-usage',
                message='Explicit use of "any" type',
                severity='error' if strict else 'warning'
            ))

        # Check for type assertions
        if re.search(r'\bas\s+\w+', line):
            issues.append(TypeIssue(
                file=str(file_path),
                line=line_num,
                category='type-assertion',
                message='Type assertion detected - prefer type guards',
                severity='info'
            ))

        # Check for @ts-ignore or @ts-expect-error without comment
        if re.search(r'@ts-(ignore|expect-error)\s*$', line):
            issues.append(TypeIssue(
                file=str(file_path),
                line=line_num,
                category='ts-ignore',
                message='@ts-ignore/expect-error without explanation',
                severity='warning'
            ))

        # Check for non-null assertions
        if re.search(r'!\s*[.;)\]]', line) and '!==' not in line and '!=' not in line:
            issues.append(TypeIssue(
                file=str(file_path),
                line=line_num,
                category='non-null-assertion',
                message='Non-null assertion (!) - consider explicit null check',
                severity='info'
            ))

        # Check for Object type
        if re.search(r':\s*Object\b', line):
            issues.append(TypeIssue(
                file=str(file_path),
                line=line_num,
                category='object-type',
                message='Use "object" (lowercase) or specific type instead of "Object"',
                severity='warning'
            ))

        # Check for Function type
        if re.search(r':\s*Function\b', line):
            issues.append(TypeIssue(
                file=str(file_path),
                line=line_num,
                category='function-type',
                message='Use specific function signature instead of "Function"',
                severity='warning'
            ))

    return issues


def generate_report(issues: list[TypeIssue], files_analyzed: int) -> str:
    """Generate a markdown report from issues."""
    report = ["# TypeScript Type Analysis Report\n"]
    report.append(f"**Files analyzed:** {files_analyzed}\n")
    report.append(f"**Total issues:** {len(issues)}\n")

    # Summary by category
    categories = Counter(issue.category for issue in issues)
    severity_counts = Counter(issue.severity for issue in issues)

    report.append("\n## Summary by Severity\n")
    report.append(f"- Errors: {severity_counts['error']}")
    report.append(f"- Warnings: {severity_counts['warning']}")
    report.append(f"- Info: {severity_counts['info']}")

    report.append("\n## Summary by Category\n")
    for category, count in categories.most_common():
        report.append(f"- {category}: {count}")

    # Group issues by file
    issues_by_file: dict[str, list[TypeIssue]] = {}
    for issue in issues:
        issues_by_file.setdefault(issue.file, []).append(issue)

    report.append("\n## Issues by File\n")
    for file, file_issues in sorted(issues_by_file.items()):
        report.append(f"\n### `{file}`\n")
        report.append("| Line | Severity | Category | Message |")
        report.append("|------|----------|----------|---------|")
        for issue in sorted(file_issues, key=lambda i: i.line):
            report.append(f"| {issue.line} | {issue.severity} | {issue.category} | {issue.message} |")

    return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(description='Analyze TypeScript files for type issues')
    parser.add_argument('path', nargs='?', default='.', help='Path to analyze')
    parser.add_argument('--strict', action='store_true', help='Treat any usage as error')
    parser.add_argument('--report', action='store_true', help='Generate markdown report')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path '{path}' does not exist", file=sys.stderr)
        return 1

    files = find_typescript_files(path)
    if not files:
        print(f"No TypeScript files found in '{path}'", file=sys.stderr)
        return 0

    all_issues = []
    for file in files:
        try:
            issues = analyze_file(file, args.strict)
            all_issues.extend(issues)
        except Exception as e:
            print(f"Error analyzing {file}: {e}", file=sys.stderr)

    if args.json:
        output = {
            'files_analyzed': len(files),
            'total_issues': len(all_issues),
            'issues': [issue._asdict() for issue in all_issues]
        }
        print(json.dumps(output, indent=2))
    elif args.report:
        print(generate_report(all_issues, len(files)))
    else:
        # Simple output
        print(f"Analyzed {len(files)} files, found {len(all_issues)} issues\n")

        for issue in all_issues:
            icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[issue.severity]
            print(f"{icon} {issue.file}:{issue.line} [{issue.category}] {issue.message}")

        # Exit with error if any errors found
        if any(i.severity == 'error' for i in all_issues):
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
