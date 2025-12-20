#!/usr/bin/env python3
"""
Trend Analyzer for Claude Repository Audits
Analyzes metrics over time to identify trends and patterns
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import statistics

class TrendAnalyzer:
    def __init__(self, baseline_path: str, current_path: str):
        self.baseline = self._load_json(baseline_path)
        self.current = self._load_json(current_path)
        self.trends = {}
        
    def _load_json(self, path: str) -> Dict:
        """Load JSON file"""
        with open(path, 'r') as f:
            return json.load(f)
    
    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze all trends"""
        self.trends = {
            'summary': self._analyze_summary(),
            'modules': self._analyze_module_trends(),
            'quality': self._analyze_quality_trends(),
            'dependencies': self._analyze_dependency_trends(),
            'issues': self._analyze_issue_trends(),
            'health': self._analyze_health_trends(),
            'recommendations': self._generate_recommendations()
        }
        return self.trends
    
    def _analyze_summary(self) -> Dict:
        """Generate summary statistics"""
        return {
            'analysis_date': datetime.now().isoformat(),
            'baseline_date': self.baseline.get('baseline_date'),
            'current_date': self.current.get('audit_date', datetime.now().isoformat()),
            'overall_trend': self._calculate_overall_trend()
        }
    
    def _analyze_module_trends(self) -> Dict:
        """Analyze module-related trends"""
        baseline_modules = self.baseline.get('modules', {})
        current_modules = self.current.get('modules', {})
        
        total_change = current_modules.get('total', 0) - baseline_modules.get('total', 0)
        avg_size_change = current_modules.get('average_size_lines', 0) - baseline_modules.get('average_size_lines', 0)
        
        return {
            'total_change': {
                'value': total_change,
                'percentage': self._calculate_percentage(baseline_modules.get('total', 1), total_change),
                'trend': 'increasing' if total_change > 0 else 'decreasing' if total_change < 0 else 'stable'
            },
            'average_size': {
                'baseline': baseline_modules.get('average_size_lines', 0),
                'current': current_modules.get('average_size_lines', 0),
                'change': avg_size_change,
                'trend': 'growing' if avg_size_change > 10 else 'shrinking' if avg_size_change < -10 else 'stable'
            },
            'empty_files': {
                'baseline': baseline_modules.get('empty_files', 0),
                'current': current_modules.get('empty_files', 0),
                'improved': current_modules.get('empty_files', 0) < baseline_modules.get('empty_files', 0)
            }
        }
    
    def _analyze_quality_trends(self) -> Dict:
        """Analyze quality metric trends"""
        baseline_quality = self.baseline.get('quality_metrics', {})
        current_quality = self.current.get('quality_metrics', {})
        
        metrics = {}
        for metric in ['modules_with_tests', 'modules_with_examples', 'documented_modules']:
            baseline_val = baseline_quality.get(metric, 0)
            current_val = current_quality.get(metric, 0)
            change = current_val - baseline_val
            
            metrics[metric] = {
                'baseline': baseline_val,
                'current': current_val,
                'change': change,
                'percentage_change': self._calculate_percentage(baseline_val, change),
                'improved': change > 0
            }
        
        return metrics
    
    def _analyze_dependency_trends(self) -> Dict:
        """Analyze dependency-related trends"""
        baseline_deps = self.baseline.get('dependencies', {})
        current_deps = self.current.get('dependencies', {})
        
        return {
            'total_dependencies': {
                'baseline': baseline_deps.get('total_declared', 0),
                'current': current_deps.get('total_declared', 0),
                'change': current_deps.get('total_declared', 0) - baseline_deps.get('total_declared', 0)
            },
            'missing_dependencies': {
                'baseline': baseline_deps.get('missing', 0),
                'current': current_deps.get('missing', 0),
                'improved': current_deps.get('missing', 0) <= baseline_deps.get('missing', 0)
            },
            'circular_dependencies': {
                'baseline': baseline_deps.get('circular', 0),
                'current': current_deps.get('circular', 0),
                'resolved': baseline_deps.get('circular', 0) > 0 and current_deps.get('circular', 0) == 0
            },
            'depth_metrics': {
                'max_depth': {
                    'baseline': baseline_deps.get('max_depth', 0),
                    'current': current_deps.get('max_depth', 0),
                    'within_limit': current_deps.get('max_depth', 0) <= 3
                },
                'average_depth': {
                    'baseline': baseline_deps.get('average_depth', 0),
                    'current': current_deps.get('average_depth', 0)
                }
            }
        }
    
    def _analyze_issue_trends(self) -> Dict:
        """Analyze issue trends"""
        baseline_issues = self.baseline.get('issues', {})
        current_issues = self.current.get('issues', {})
        
        total_baseline = sum(baseline_issues.values())
        total_current = sum(current_issues.values())
        
        return {
            'total_issues': {
                'baseline': total_baseline,
                'current': total_current,
                'change': total_current - total_baseline,
                'improved': total_current < total_baseline
            },
            'by_type': {
                issue_type: {
                    'baseline': baseline_issues.get(issue_type, 0),
                    'current': current_issues.get(issue_type, 0),
                    'resolved': baseline_issues.get(issue_type, 0) > 0 and current_issues.get(issue_type, 0) == 0
                }
                for issue_type in set(list(baseline_issues.keys()) + list(current_issues.keys()))
            }
        }
    
    def _analyze_health_trends(self) -> Dict:
        """Analyze overall health trends"""
        baseline_health = self.baseline.get('health_score', 50)
        current_health = self.current.get('health_score', 50)
        health_change = current_health - baseline_health
        
        baseline_debt = self.baseline.get('technical_debt_hours', 0)
        current_debt = self.current.get('technical_debt_hours', 0)
        debt_change = current_debt - baseline_debt
        
        return {
            'health_score': {
                'baseline': baseline_health,
                'current': current_health,
                'change': health_change,
                'trend': 'improving' if health_change > 5 else 'declining' if health_change < -5 else 'stable',
                'target_met': current_health >= 85
            },
            'technical_debt': {
                'baseline_hours': baseline_debt,
                'current_hours': current_debt,
                'change_hours': debt_change,
                'trend': 'increasing' if debt_change > 5 else 'decreasing' if debt_change < -5 else 'stable'
            }
        }
    
    def _calculate_overall_trend(self) -> str:
        """Calculate overall repository trend"""
        positive_indicators = 0
        negative_indicators = 0
        
        # Check various indicators
        health_change = self.current.get('health_score', 50) - self.baseline.get('health_score', 50)
        if health_change > 0:
            positive_indicators += 2  # Health score is double weighted
        elif health_change < 0:
            negative_indicators += 2
        
        # Check issues
        baseline_issues = sum(self.baseline.get('issues', {}).values())
        current_issues = sum(self.current.get('issues', {}).values())
        if current_issues < baseline_issues:
            positive_indicators += 1
        elif current_issues > baseline_issues:
            negative_indicators += 1
        
        # Check dependencies
        if self.current.get('dependencies', {}).get('missing', 0) == 0:
            positive_indicators += 1
        if self.current.get('dependencies', {}).get('circular', 0) == 0:
            positive_indicators += 1
        
        # Determine overall trend
        if positive_indicators > negative_indicators + 2:
            return "significantly improving"
        elif positive_indicators > negative_indicators:
            return "improving"
        elif negative_indicators > positive_indicators + 2:
            return "significantly declining"
        elif negative_indicators > positive_indicators:
            return "declining"
        else:
            return "stable"
    
    def _calculate_percentage(self, base: float, change: float) -> float:
        """Calculate percentage change"""
        if base == 0:
            return 0.0
        return round((change / base) * 100, 1)
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate actionable recommendations based on trends"""
        recommendations = []
        
        # Check module size trend
        module_trends = self.trends.get('modules', {})
        if module_trends.get('average_size', {}).get('trend') == 'growing':
            recommendations.append({
                'priority': 'high',
                'category': 'modules',
                'recommendation': 'Module sizes are increasing. Consider splitting large modules.',
                'action': 'Run module size analysis and refactor modules over 150 lines.'
            })
        
        # Check quality metrics
        quality_trends = self.trends.get('quality', {})
        if quality_trends.get('modules_with_tests', {}).get('current', 0) < 50:
            recommendations.append({
                'priority': 'high',
                'category': 'testing',
                'recommendation': 'Test coverage is low. Increase module testing.',
                'action': 'Add test scenarios to all critical modules.'
            })
        
        # Check dependencies
        dep_trends = self.trends.get('dependencies', {})
        if dep_trends.get('missing_dependencies', {}).get('current', 0) > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'dependencies',
                'recommendation': 'Missing dependencies detected.',
                'action': 'Create missing dependency modules or update references.'
            })
        
        # Check health score
        health_trends = self.trends.get('health', {})
        if health_trends.get('health_score', {}).get('current', 0) < 70:
            recommendations.append({
                'priority': 'high',
                'category': 'overall',
                'recommendation': 'Repository health score is below target.',
                'action': 'Focus on resolving high-priority issues to improve health score.'
            })
        
        return recommendations
    
    def save_trends(self, output_path: str):
        """Save trends analysis to file"""
        with open(output_path, 'w') as f:
            json.dump(self.trends, f, indent=2)
        print(f"Trends analysis saved to: {output_path}")
    
    def print_summary(self):
        """Print a human-readable summary"""
        print("\n📊 TREND ANALYSIS SUMMARY")
        print("=" * 50)
        print(f"Overall Trend: {self.trends['summary']['overall_trend'].upper()}")
        print(f"Health Score: {self.trends['health']['health_score']['baseline']} → {self.trends['health']['health_score']['current']}")
        print(f"Technical Debt: {self.trends['health']['technical_debt']['baseline_hours']}h → {self.trends['health']['technical_debt']['current_hours']}h")
        
        print("\n📈 Key Metrics:")
        print(f"- Total Modules: {self.trends['modules']['total_change']['value']:+d}")
        print(f"- Average Size: {self.trends['modules']['average_size']['change']:+.1f} lines")
        print(f"- Total Issues: {self.trends['issues']['total_issues']['change']:+d}")
        
        print("\n💡 Top Recommendations:")
        for rec in self.trends['recommendations'][:3]:
            print(f"- [{rec['priority'].upper()}] {rec['recommendation']}")


def main():
    parser = argparse.ArgumentParser(description='Analyze trends in Claude repository audits')
    parser.add_argument('--baseline', required=True, help='Path to baseline metrics JSON')
    parser.add_argument('--current', required=True, help='Path to current audit JSON')
    parser.add_argument('--output', required=True, help='Path to save trends analysis')
    parser.add_argument('--verbose', action='store_true', help='Print detailed output')
    
    args = parser.parse_args()
    
    # Run analysis
    analyzer = TrendAnalyzer(args.baseline, args.current)
    analyzer.analyze_trends()
    analyzer.save_trends(args.output)
    
    if args.verbose:
        analyzer.print_summary()
    
    # Exit with appropriate code
    health_trend = analyzer.trends['health']['health_score']['trend']
    if health_trend == 'declining':
        exit(1)  # Non-zero exit if health is declining
    else:
        exit(0)


if __name__ == '__main__':
    main()