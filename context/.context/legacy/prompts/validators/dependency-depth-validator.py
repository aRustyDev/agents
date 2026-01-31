#!/usr/bin/env python3
"""
Dependency Depth Validator
Validates dependency chains don't exceed maximum depth and visualizes dependency graphs
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
import graphviz

class DependencyDepthValidator:
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self.modules = {}
        self.dependencies = defaultdict(list)
        self.violations = []
        self.circular_deps = []
        
    def scan_modules(self, directory: str):
        """Scan directory for all modules and build dependency graph"""
        for root, dirs, files in os.walk(directory):
            # Skip test and archive directories
            if any(skip in root for skip in ['tests', 'archive', 'cache', '.git']):
                continue
                
            for file in files:
                if file.endswith(('.md', '.yaml', '.yml')):
                    filepath = os.path.join(root, file)
                    self.parse_module(filepath)
    
    def parse_module(self, filepath: str):
        """Parse a module file to extract dependencies"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Extract YAML frontmatter
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end != -1:
                    frontmatter = yaml.safe_load(content[3:yaml_end])
                    
                    module_name = frontmatter.get('module')
                    if module_name:
                        self.modules[module_name] = {
                            'file': filepath,
                            'dependencies': frontmatter.get('dependencies', []),
                            'scope': frontmatter.get('scope', 'unknown'),
                            'priority': frontmatter.get('priority', 'medium')
                        }
                        
                        # Build adjacency list
                        for dep in frontmatter.get('dependencies', []):
                            self.dependencies[module_name].append(dep)
                            
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
    
    def validate_all(self) -> Tuple[List[Dict], List[List[str]]]:
        """Validate all modules for depth violations and circular dependencies"""
        # Check for circular dependencies first
        self.circular_deps = self.find_circular_dependencies()
        
        # Check depth for each module
        for module in self.modules:
            depth = self.calculate_depth(module)
            if depth > self.max_depth:
                self.violations.append({
                    'module': module,
                    'depth': depth,
                    'excess': depth - self.max_depth,
                    'chain': self.get_longest_chain(module),
                    'file': self.modules[module]['file']
                })
        
        return self.violations, self.circular_deps
    
    def calculate_depth(self, module: str, visited: Optional[Set[str]] = None) -> int:
        """Calculate maximum dependency depth for a module"""
        if visited is None:
            visited = set()
        
        if module in visited:
            return 0  # Circular dependency, handled separately
        
        if module not in self.dependencies or not self.dependencies[module]:
            return 1
        
        visited.add(module)
        
        max_child_depth = 0
        for dep in self.dependencies[module]:
            if dep in self.modules:  # Only count existing dependencies
                child_depth = self.calculate_depth(dep, visited.copy())
                max_child_depth = max(max_child_depth, child_depth)
        
        return 1 + max_child_depth
    
    def get_longest_chain(self, module: str) -> List[str]:
        """Get the longest dependency chain starting from a module"""
        def dfs(current: str, path: List[str], visited: Set[str]) -> List[str]:
            if current in visited:
                return path
            
            visited.add(current)
            longest = path
            
            for dep in self.dependencies.get(current, []):
                if dep in self.modules:
                    child_path = dfs(dep, path + [dep], visited.copy())
                    if len(child_path) > len(longest):
                        longest = child_path
            
            return longest
        
        return dfs(module, [module], set())
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """Find all circular dependency chains"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.dependencies.get(node, []):
                if neighbor not in self.modules:
                    continue
                    
                if neighbor not in visited:
                    if dfs(neighbor, path + [neighbor]):
                        return True
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)
            
            rec_stack.remove(node)
            return False
        
        for module in self.modules:
            if module not in visited:
                dfs(module, [module])
        
        return cycles
    
    def find_missing_dependencies(self) -> Dict[str, List[str]]:
        """Find all declared dependencies that don't exist"""
        missing = defaultdict(list)
        
        for module, info in self.modules.items():
            for dep in info['dependencies']:
                if dep not in self.modules:
                    missing[module].append(dep)
        
        return dict(missing)
    
    def generate_visualization(self, output_file: str = "dependency_graph"):
        """Generate a visual representation of the dependency graph"""
        dot = graphviz.Digraph(comment='Module Dependencies')
        dot.attr(rankdir='TB')
        
        # Add nodes
        for module, info in self.modules.items():
            # Color based on scope
            color = {
                'persistent': 'lightblue',
                'context': 'lightgreen',
                'temporary': 'lightyellow'
            }.get(info['scope'], 'lightgray')
            
            # Shape based on violations
            shape = 'box'
            if any(v['module'] == module for v in self.violations):
                shape = 'box'
                color = 'lightcoral'
            
            dot.node(module, module, style='filled', fillcolor=color, shape=shape)
        
        # Add edges
        for module, deps in self.dependencies.items():
            for dep in deps:
                if dep in self.modules:
                    dot.edge(module, dep)
                else:
                    # Missing dependency
                    dot.node(dep, dep, style='filled', fillcolor='red', shape='diamond')
                    dot.edge(module, dep, style='dashed', color='red')
        
        # Highlight circular dependencies
        for cycle in self.circular_deps:
            for i in range(len(cycle) - 1):
                dot.edge(cycle[i], cycle[i + 1], color='red', penwidth='2')
        
        # Save visualization
        dot.render(output_file, format='png', cleanup=True)
        print(f"Dependency graph saved to: {output_file}.png")
    
    def generate_report(self) -> str:
        """Generate a detailed validation report"""
        report = ["# Dependency Depth Validation Report\n"]
        
        # Summary
        report.append("## Summary")
        report.append(f"- Total Modules: {len(self.modules)}")
        report.append(f"- Depth Violations: {len(self.violations)}")
        report.append(f"- Circular Dependencies: {len(self.circular_deps)}")
        report.append(f"- Maximum Allowed Depth: {self.max_depth}")
        
        missing = self.find_missing_dependencies()
        if missing:
            report.append(f"- Missing Dependencies: {sum(len(deps) for deps in missing.values())}")
        report.append("")
        
        # Circular Dependencies (Critical)
        if self.circular_deps:
            report.append("## 🔴 Circular Dependencies (Critical)\n")
            for i, cycle in enumerate(self.circular_deps, 1):
                report.append(f"### Cycle {i}")
                report.append(" → ".join(cycle))
                report.append("")
        
        # Depth Violations
        if self.violations:
            report.append("## ❌ Depth Violations\n")
            for v in sorted(self.violations, key=lambda x: x['depth'], reverse=True):
                report.append(f"### {v['module']}")
                report.append(f"- **Depth**: {v['depth']} (excess: {v['excess']})")
                report.append(f"- **File**: {v['file']}")
                report.append(f"- **Chain**: {' → '.join(v['chain'])}")
                report.append("")
        
        # Missing Dependencies
        if missing:
            report.append("## ⚠️  Missing Dependencies\n")
            for module, deps in missing.items():
                report.append(f"- **{module}**: {', '.join(deps)}")
            report.append("")
        
        # Recommendations
        if self.violations or self.circular_deps:
            report.append("## 💡 Recommendations\n")
            
            if self.circular_deps:
                report.append("### Breaking Circular Dependencies")
                report.append("1. Extract shared functionality to a new module")
                report.append("2. Use dependency injection patterns")
                report.append("3. Implement event-based communication")
                report.append("")
            
            if self.violations:
                report.append("### Reducing Dependency Depth")
                report.append("1. Flatten dependency hierarchies")
                report.append("2. Create facade modules for complex subsystems")
                report.append("3. Use composition over deep inheritance")
                report.append("4. Consider module consolidation for tightly coupled components")
        
        # Healthy Modules
        healthy_modules = [m for m in self.modules if not any(v['module'] == m for v in self.violations)]
        if healthy_modules:
            report.append("\n## ✅ Healthy Modules")
            report.append(f"- {len(healthy_modules)} modules within depth limits")
        
        return "\n".join(report)
    
    def suggest_refactoring(self, module: str) -> List[str]:
        """Suggest refactoring options for a module with depth violations"""
        suggestions = []
        
        chain = self.get_longest_chain(module)
        
        # Suggest flattening
        if len(chain) > 4:
            mid_point = len(chain) // 2
            suggestions.append(
                f"Consider making {chain[0]} directly depend on {chain[mid_point]}, "
                f"bypassing {' → '.join(chain[1:mid_point])}"
            )
        
        # Suggest facade pattern
        deep_deps = [d for d in self.dependencies[module] 
                    if self.calculate_depth(d) > 2]
        if deep_deps:
            suggestions.append(
                f"Create a facade module to wrap complex dependencies: {', '.join(deep_deps)}"
            )
        
        # Suggest consolidation
        if len(self.dependencies[module]) > 5:
            suggestions.append(
                "Consider consolidating related dependencies into a single module"
            )
        
        return suggestions


def main():
    parser = argparse.ArgumentParser(description='Validate dependency depth')
    parser.add_argument('path', nargs='?', default='.claude',
                       help='Path to scan (default: .claude)')
    parser.add_argument('--max-depth', type=int, default=3,
                       help='Maximum allowed depth (default: 3)')
    parser.add_argument('--visualize', action='store_true',
                       help='Generate dependency graph visualization')
    parser.add_argument('--output', help='Save report to file')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')
    parser.add_argument('--suggest', help='Get refactoring suggestions for module')
    
    args = parser.parse_args()
    
    validator = DependencyDepthValidator(args.max_depth)
    validator.scan_modules(args.path)
    
    violations, circular = validator.validate_all()
    
    if args.suggest:
        # Show refactoring suggestions
        suggestions = validator.suggest_refactoring(args.suggest)
        print(f"Refactoring suggestions for {args.suggest}:")
        for s in suggestions:
            print(f"- {s}")
    elif args.json:
        # JSON output
        result = {
            'violations': violations,
            'circular_dependencies': circular,
            'missing_dependencies': validator.find_missing_dependencies(),
            'summary': {
                'total_modules': len(validator.modules),
                'total_violations': len(violations),
                'circular_count': len(circular),
                'max_depth': args.max_depth
            }
        }
        print(json.dumps(result, indent=2))
    else:
        # Text report
        report = validator.generate_report()
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Report saved to: {args.output}")
        else:
            print(report)
        
        if args.visualize:
            validator.generate_visualization()
    
    # Exit with error if violations found
    if violations or circular:
        sys.exit(1)


if __name__ == '__main__':
    main()