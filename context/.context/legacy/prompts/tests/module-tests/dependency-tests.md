# Module Dependency Tests
## Advanced Dependency Analysis and Validation

---

## Dependency Graph Builder

```python
# dependency_graph.py
import yaml
import os
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple

class DependencyGraph:
    def __init__(self, module_dir: str = ".claude"):
        self.module_dir = module_dir
        self.graph = defaultdict(list)
        self.modules = {}
        self.build_graph()
    
    def build_graph(self):
        """Build dependency graph from all modules"""
        for root, dirs, files in os.walk(self.module_dir):
            for file in files:
                if file.endswith(('.md', '.yaml', '.yml')):
                    filepath = os.path.join(root, file)
                    self.parse_module(filepath)
    
    def parse_module(self, filepath: str):
        """Parse a module file for dependencies"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Extract YAML frontmatter
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end != -1:
                    frontmatter = yaml.safe_load(content[3:yaml_end])
                    module_name = frontmatter.get('module')
                    dependencies = frontmatter.get('dependencies', [])
                    
                    if module_name:
                        self.modules[module_name] = filepath
                        self.graph[module_name] = dependencies
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
```

---

## Circular Dependency Detection

```python
def detect_circular_dependencies(graph: DependencyGraph) -> List[List[str]]:
    """Detect all circular dependencies in the graph"""
    cycles = []
    visited = set()
    rec_stack = set()
    
    def dfs(node: str, path: List[str]) -> bool:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph.graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, path.copy()):
                    return True
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)
        
        path.pop()
        rec_stack.remove(node)
        return False
    
    for node in graph.modules:
        if node not in visited:
            dfs(node, [])
    
    return cycles
```

---

## Dependency Depth Analysis

```python
def analyze_dependency_depth(graph: DependencyGraph) -> Dict[str, int]:
    """Calculate maximum dependency depth for each module"""
    depths = {}
    
    def get_depth(module: str, visited: Set[str] = None) -> int:
        if visited is None:
            visited = set()
            
        if module in depths:
            return depths[module]
            
        if module in visited:
            return 0  # Circular dependency, handled elsewhere
            
        visited.add(module)
        
        deps = graph.graph.get(module, [])
        if not deps:
            depth = 1
        else:
            depth = 1 + max(get_depth(dep, visited.copy()) for dep in deps)
        
        depths[module] = depth
        return depth
    
    for module in graph.modules:
        get_depth(module)
    
    return depths
```

---

## Missing Dependency Detection

```python
def find_missing_dependencies(graph: DependencyGraph) -> Dict[str, List[str]]:
    """Find all declared dependencies that don't exist"""
    missing = defaultdict(list)
    
    for module, deps in graph.graph.items():
        for dep in deps:
            if dep not in graph.modules:
                missing[module].append(dep)
    
    return dict(missing)
```

---

## Dependency Conflict Detection

```python
def detect_dependency_conflicts(graph: DependencyGraph) -> List[Dict]:
    """Detect modules with conflicting dependencies"""
    conflicts = []
    
    # Load conflict data from modules
    module_conflicts = {}
    for module, filepath in graph.modules.items():
        with open(filepath, 'r') as f:
            content = f.read()
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end != -1:
                    frontmatter = yaml.safe_load(content[3:yaml_end])
                    module_conflicts[module] = frontmatter.get('conflicts', [])
    
    # Check for violations
    for module, deps in graph.graph.items():
        for dep in deps:
            if dep in module_conflicts:
                for conflict in module_conflicts[dep]:
                    if conflict in deps:
                        conflicts.append({
                            'module': module,
                            'dependency': dep,
                            'conflicts_with': conflict,
                            'reason': f"{dep} conflicts with {conflict}"
                        })
    
    return conflicts
```

---

## Dependency Test Scenarios

### Scenario 1: Simple Linear Dependencies
```yaml
# Test modules
ModuleA:
  dependencies: []
  
ModuleB:
  dependencies: ["ModuleA"]
  
ModuleC:
  dependencies: ["ModuleB"]

# Expected: All pass, max depth = 3
```

### Scenario 2: Circular Dependency
```yaml
# Test modules
ModuleX:
  dependencies: ["ModuleY"]
  
ModuleY:
  dependencies: ["ModuleZ"]
  
ModuleZ:
  dependencies: ["ModuleX"]

# Expected: Circular dependency detected [X->Y->Z->X]
```

### Scenario 3: Missing Dependencies
```yaml
# Test module
ModuleTest:
  dependencies: ["NonExistentModule", "AnotherMissing"]

# Expected: Missing dependencies reported
```

### Scenario 4: Depth Violation
```yaml
# Test modules creating depth > 3
Module1:
  dependencies: ["Module2"]
Module2:
  dependencies: ["Module3"]
Module3:
  dependencies: ["Module4"]
Module4:
  dependencies: []

# Expected: Depth violation for Module1 (depth=4)
```

---

## Test Execution Script

```bash
#!/bin/bash
# run_dependency_tests.sh

echo "🔍 Running Dependency Tests..."

# Run Python dependency analyzer
python3 << 'EOF'
import sys
sys.path.append('.claude/tests')

from dependency_tests import *

# Initialize graph
graph = DependencyGraph()

# Test 1: Circular Dependencies
print("\n[TEST] Checking for circular dependencies...")
cycles = detect_circular_dependencies(graph)
if cycles:
    print(f"❌ Found {len(cycles)} circular dependencies:")
    for cycle in cycles:
        print(f"   {' -> '.join(cycle)}")
    sys.exit(1)
else:
    print("✅ No circular dependencies found")

# Test 2: Dependency Depth
print("\n[TEST] Checking dependency depths...")
depths = analyze_dependency_depth(graph)
violations = {m: d for m, d in depths.items() if d > 3}
if violations:
    print(f"❌ Found {len(violations)} depth violations:")
    for module, depth in violations.items():
        print(f"   {module}: depth={depth} (max=3)")
    sys.exit(1)
else:
    print("✅ All modules within depth limit")

# Test 3: Missing Dependencies
print("\n[TEST] Checking for missing dependencies...")
missing = find_missing_dependencies(graph)
if missing:
    print(f"❌ Found {len(missing)} modules with missing dependencies:")
    for module, deps in missing.items():
        print(f"   {module}: missing {deps}")
    sys.exit(1)
else:
    print("✅ All dependencies exist")

# Test 4: Dependency Conflicts
print("\n[TEST] Checking for dependency conflicts...")
conflicts = detect_dependency_conflicts(graph)
if conflicts:
    print(f"❌ Found {len(conflicts)} dependency conflicts:")
    for conflict in conflicts:
        print(f"   {conflict['module']}: {conflict['reason']}")
    sys.exit(1)
else:
    print("✅ No dependency conflicts found")

print("\n✅ All dependency tests passed!")
EOF
```

---

## Integration with CI/CD

```yaml
# .github/workflows/dependency-tests.yml
name: Dependency Tests

on:
  push:
    paths:
      - '.claude/**/*.md'
      - '.claude/**/*.yaml'
      - '.claude/**/*.yml'
  pull_request:
    paths:
      - '.claude/**/*.md'
      - '.claude/**/*.yaml'
      - '.claude/**/*.yml'

jobs:
  test-dependencies:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install pyyaml
      
      - name: Run dependency tests
        run: |
          chmod +x .claude/tests/run_dependency_tests.sh
          .claude/tests/run_dependency_tests.sh
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: dependency-test-results
          path: .claude/tests/results/
```