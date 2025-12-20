#!/usr/bin/env python3
"""
Pattern Analysis Tool - Identifies common patterns in the codebase
"""

import os
import re
from collections import Counter, defaultdict
from pathlib import Path

class PatternAnalyzer:
    def __init__(self):
        self.patterns = {
            'error_handling': {
                'echo_error': r'echo\s+["\'].*[Ee]rror.*["\']',
                'stderr_redirect': r'>&2',
                'exit_code': r'exit\s+\d+',
                'error_var': r'\$\?|PIPESTATUS',
                'handle_error_func': r'handle_error\s*\(',
                'try_catch': r'try\s*{|catch\s*{',
            },
            'validation': {
                'file_exists': r'-[ef]\s+["\']?\$?\w+',
                'var_empty': r'-z\s+["\']?\$\w+',
                'var_not_empty': r'-n\s+["\']?\$\w+',
                'validate_func': r'validate_\w+\s*\(',
                'check_func': r'check_\w+\s*\(',
                'verify_func': r'verify_\w+\s*\(',
                'regex_match': r'=~\s+["\'].*["\']',
            },
            'git_operations': {
                'git_command': r'git\s+\w+',
                'gh_command': r'gh\s+\w+',
                'branch_check': r'git\s+branch.*-r|--remote',
                'status_check': r'git\s+status',
                'commit_op': r'git\s+commit',
                'push_pull': r'git\s+(push|pull)',
            },
            'process_loading': {
                'load_command': r'!load\s+\S+',
                'source_command': r'source\s+\S+|\.\s+\S+',
                'import_pattern': r'import\s+\S+|from\s+\S+\s+import',
            }
        }
        
    def analyze_file(self, filepath):
        """Analyze patterns in a single file"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
        except:
            return {}
            
        results = defaultdict(list)
        
        for category, patterns in self.patterns.items():
            for pattern_name, regex in patterns.items():
                matches = re.findall(regex, content, re.MULTILINE)
                if matches:
                    results[category].extend(matches)
                    
        return results
        
    def analyze_directory(self, directory):
        """Analyze all files in a directory"""
        all_results = defaultdict(Counter)
        file_count = 0
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    file_results = self.analyze_file(filepath)
                    file_count += 1
                    
                    for category, matches in file_results.items():
                        all_results[category].update(matches)
                        
        return all_results, file_count
        
    def generate_report(self, results, file_count):
        """Generate analysis report"""
        report = []
        report.append(f"# Pattern Analysis Report\n")
        report.append(f"Analyzed {file_count} files\n")
        
        for category, counter in results.items():
            report.append(f"\n## {category.replace('_', ' ').title()}")
            report.append(f"Total instances: {sum(counter.values())}")
            report.append(f"Unique patterns: {len(counter)}\n")
            
            # Top 10 most common
            report.append("### Most Common Patterns:")
            for pattern, count in counter.most_common(10):
                report.append(f"- `{pattern}`: {count} occurrences")
                
        return '\n'.join(report)
        
    def identify_extraction_candidates(self, results):
        """Identify patterns that are good candidates for extraction"""
        candidates = []
        
        for category, counter in results.items():
            # Find patterns that appear more than 5 times
            common_patterns = [(p, c) for p, c in counter.items() if c > 5]
            
            if common_patterns:
                candidates.append({
                    'category': category,
                    'patterns': common_patterns,
                    'total_occurrences': sum(c for _, c in common_patterns)
                })
                
        return candidates

def main():
    analyzer = PatternAnalyzer()
    
    # Analyze commands directory
    print("Analyzing .claude/commands/ directory...")
    results, file_count = analyzer.analyze_directory('.claude/commands/')
    
    # Generate report
    report = analyzer.generate_report(results, file_count)
    
    # Save report
    with open('analysis/pattern-analysis-report.md', 'w') as f:
        f.write(report)
    
    print(f"\nAnalysis complete! Analyzed {file_count} files.")
    print("Report saved to: analysis/pattern-analysis-report.md")
    
    # Identify extraction candidates
    candidates = analyzer.identify_extraction_candidates(results)
    
    print("\n## Extraction Candidates:")
    for candidate in candidates:
        print(f"\n{candidate['category']}:")
        print(f"  Total occurrences: {candidate['total_occurrences']}")
        print(f"  Patterns to extract: {len(candidate['patterns'])}")

if __name__ == "__main__":
    main()