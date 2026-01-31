#!/usr/bin/env python3
"""
Module Size Validator
Enforces module size limits and provides splitting recommendations
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import re

class ModuleSizeValidator:
    def __init__(self, max_lines: int = 200, warning_threshold: int = 150):
        self.max_lines = max_lines
        self.warning_threshold = warning_threshold
        self.violations = []
        self.warnings = []
        
    def validate_directory(self, directory: str) -> Tuple[List[Dict], List[Dict]]:
        """Validate all modules in a directory"""
        for root, dirs, files in os.walk(directory):
            # Skip test and archive directories
            if any(skip in root for skip in ['tests', 'archive', 'cache']):
                continue
                
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    self.validate_file(filepath)
        
        return self.violations, self.warnings
    
    def validate_file(self, filepath: str) -> Dict:
        """Validate a single module file"""
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            line_count = len(lines)
            
            if line_count > self.max_lines:
                analysis = self.analyze_module(filepath, lines)
                self.violations.append({
                    'file': filepath,
                    'lines': line_count,
                    'excess': line_count - self.max_lines,
                    'analysis': analysis,
                    'recommendations': self.generate_recommendations(analysis)
                })
            elif line_count > self.warning_threshold:
                self.warnings.append({
                    'file': filepath,
                    'lines': line_count,
                    'remaining': self.max_lines - line_count
                })
            
            return {
                'file': filepath,
                'lines': line_count,
                'status': 'violation' if line_count > self.max_lines else 'warning' if line_count > self.warning_threshold else 'ok'
            }
            
        except Exception as e:
            return {
                'file': filepath,
                'error': str(e),
                'status': 'error'
            }
    
    def analyze_module(self, filepath: str, lines: List[str]) -> Dict:
        """Analyze module structure to identify splitting opportunities"""
        analysis = {
            'sections': [],
            'code_blocks': 0,
            'examples': 0,
            'largest_section': 0,
            'frontmatter_lines': 0
        }
        
        current_section = None
        section_start = 0
        in_code_block = False
        in_frontmatter = False
        
        for i, line in enumerate(lines):
            # Track frontmatter
            if line.strip() == '---':
                if i == 0:
                    in_frontmatter = True
                elif in_frontmatter:
                    in_frontmatter = False
                    analysis['frontmatter_lines'] = i + 1
                    
            # Track code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                if in_code_block:
                    analysis['code_blocks'] += 1
            
            # Track examples
            if re.match(r'^#{1,3}\s*(Example|Usage|Scenario)', line, re.IGNORECASE):
                analysis['examples'] += 1
            
            # Track sections
            if re.match(r'^#{1,3}\s+', line) and not in_code_block:
                if current_section:
                    section_size = i - section_start
                    analysis['sections'].append({
                        'title': current_section,
                        'start': section_start,
                        'end': i,
                        'size': section_size
                    })
                    analysis['largest_section'] = max(analysis['largest_section'], section_size)
                
                current_section = line.strip()
                section_start = i
        
        # Add final section
        if current_section:
            section_size = len(lines) - section_start
            analysis['sections'].append({
                'title': current_section,
                'start': section_start,
                'end': len(lines),
                'size': section_size
            })
            analysis['largest_section'] = max(analysis['largest_section'], section_size)
        
        return analysis
    
    def generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate specific recommendations for splitting the module"""
        recommendations = []
        
        # If many examples, suggest moving to separate file
        if analysis['examples'] >= 3:
            recommendations.append(
                "Move examples to a separate 'examples/' subdirectory"
            )
        
        # If many code blocks, suggest extraction
        if analysis['code_blocks'] >= 5:
            recommendations.append(
                "Extract code snippets to separate reference files"
            )
        
        # If large sections exist
        large_sections = [s for s in analysis['sections'] if s['size'] > 50]
        if large_sections:
            for section in large_sections[:3]:  # Top 3 largest
                recommendations.append(
                    f"Extract section '{section['title']}' ({section['size']} lines) to separate module"
                )
        
        # General recommendations based on content
        if len(analysis['sections']) > 8:
            recommendations.append(
                "Consider splitting into multiple focused modules by functionality"
            )
        
        # If the module appears to be a command
        if any('subcommand' in s['title'].lower() for s in analysis['sections']):
            recommendations.append(
                "Split subcommands into separate files in a subdirectory"
            )
        
        return recommendations
    
    def generate_report(self) -> str:
        """Generate a detailed report of findings"""
        report = ["# Module Size Validation Report\n"]
        
        # Summary
        report.append("## Summary")
        report.append(f"- Total Violations: {len(self.violations)}")
        report.append(f"- Total Warnings: {len(self.warnings)}")
        report.append(f"- Size Limit: {self.max_lines} lines")
        report.append(f"- Warning Threshold: {self.warning_threshold} lines\n")
        
        # Violations
        if self.violations:
            report.append("## ❌ Violations (Must Fix)\n")
            for v in sorted(self.violations, key=lambda x: x['lines'], reverse=True):
                report.append(f"### {Path(v['file']).name}")
                report.append(f"- **Size**: {v['lines']} lines (excess: {v['excess']})")
                report.append(f"- **Sections**: {len(v['analysis']['sections'])}")
                report.append(f"- **Largest Section**: {v['analysis']['largest_section']} lines")
                
                if v['recommendations']:
                    report.append("\n**Recommendations:**")
                    for rec in v['recommendations']:
                        report.append(f"- {rec}")
                
                report.append("")
        
        # Warnings
        if self.warnings:
            report.append("## ⚠️  Warnings (Approaching Limit)\n")
            for w in sorted(self.warnings, key=lambda x: x['lines'], reverse=True):
                report.append(f"- **{Path(w['file']).name}**: {w['lines']} lines (remaining: {w['remaining']})")
            report.append("")
        
        # Suggested refactoring plan
        if self.violations:
            report.append("## 🔧 Suggested Refactoring Plan\n")
            report.append("1. **Immediate Actions**:")
            for v in self.violations[:3]:  # Top 3
                report.append(f"   - Refactor {Path(v['file']).name}")
            
            report.append("\n2. **Module Splitting Strategy**:")
            report.append("   - Create subdirectories for complex modules")
            report.append("   - Extract examples and test scenarios")
            report.append("   - Separate configuration from implementation")
            report.append("   - Use module inheritance for common patterns")
        
        return "\n".join(report)
    
    def suggest_split(self, filepath: str) -> Dict[str, List[str]]:
        """Suggest how to split a large module into smaller ones"""
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        analysis = self.analyze_module(filepath, lines)
        suggestions = {}
        
        # Extract examples
        if analysis['examples'] > 0:
            suggestions['examples.md'] = self._extract_sections(
                lines, 
                [r'^#{1,3}\s*(Example|Usage|Scenario)']
            )
        
        # Extract large sections
        for section in analysis['sections']:
            if section['size'] > 70:
                section_name = re.sub(r'[^\w\s-]', '', section['title']).strip()
                section_name = re.sub(r'[-\s]+', '-', section_name).lower()
                suggestions[f"{section_name}.md"] = lines[section['start']:section['end']]
        
        return suggestions
    
    def _extract_sections(self, lines: List[str], patterns: List[str]) -> List[str]:
        """Extract lines matching section patterns"""
        extracted = []
        in_section = False
        
        for line in lines:
            if any(re.match(p, line, re.IGNORECASE) for p in patterns):
                in_section = True
            elif re.match(r'^#{1,3}\s+', line) and in_section:
                in_section = False
            
            if in_section:
                extracted.append(line)
        
        return extracted


def main():
    parser = argparse.ArgumentParser(description='Validate module sizes')
    parser.add_argument('path', nargs='?', default='.claude', 
                       help='Path to validate (default: .claude)')
    parser.add_argument('--max-lines', type=int, default=200,
                       help='Maximum allowed lines (default: 200)')
    parser.add_argument('--warning-threshold', type=int, default=150,
                       help='Warning threshold (default: 150)')
    parser.add_argument('--suggest-split', help='Suggest split for specific file')
    parser.add_argument('--output', help='Save report to file')
    parser.add_argument('--json', action='store_true', 
                       help='Output results as JSON')
    
    args = parser.parse_args()
    
    validator = ModuleSizeValidator(args.max_lines, args.warning_threshold)
    
    if args.suggest_split:
        # Suggest split for specific file
        suggestions = validator.suggest_split(args.suggest_split)
        print(f"Suggested split for {args.suggest_split}:")
        for filename, content in suggestions.items():
            print(f"\n{filename} ({len(content)} lines)")
            print("-" * 40)
            print("".join(content[:10]))  # First 10 lines
            if len(content) > 10:
                print("...")
    else:
        # Validate directory
        violations, warnings = validator.validate_directory(args.path)
        
        if args.json:
            import json
            print(json.dumps({
                'violations': violations,
                'warnings': warnings,
                'summary': {
                    'total_violations': len(violations),
                    'total_warnings': len(warnings),
                    'max_lines': args.max_lines,
                    'warning_threshold': args.warning_threshold
                }
            }, indent=2))
        else:
            report = validator.generate_report()
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(report)
                print(f"Report saved to: {args.output}")
            else:
                print(report)
        
        # Exit with error if violations found
        if violations:
            sys.exit(1)


if __name__ == '__main__':
    main()