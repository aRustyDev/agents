#!/bin/bash

echo "🔍 Verifying Module Dependencies"
echo "================================"

errors=0

# Check dependencies for Phase 1 modules only
for module_dir in plan report command; do
    echo -e "\n📂 Checking $module_dir modules..."
    
    for file in $(find .claude/commands/$module_dir -name "*.md" -type f 2>/dev/null); do
        # Skip template files in subdirectories
        if [[ "$file" == *"/templates/"* ]]; then
            continue
        fi
        
        # Extract dependencies
        deps=$(grep -A20 "^dependencies:" "$file" 2>/dev/null | grep "^  - " | sed 's/^  - //')
        
        if [ -z "$deps" ]; then
            echo "  ✅ $file (no dependencies)"
            continue
        fi
        
        has_error=false
        for dep in $deps; do
            # Build the full path for the dependency
            dep_dir=$(dirname "$file")
            dep_path="$dep_dir/$dep"
            
            # Also check in the parent commands directory
            alt_path=".claude/commands/$dep"
            
            if [[ -f "$dep_path" ]] || [[ -f "$alt_path" ]]; then
                :  # Dependency exists
            else
                echo "  ❌ $file → Missing dependency: $dep"
                has_error=true
                ((errors++))
            fi
        done
        
        if [ "$has_error" = false ]; then
            echo "  ✅ $file (all dependencies valid)"
        fi
    done
done

echo -e "\n================================"
if [ $errors -eq 0 ]; then
    echo "✅ All dependencies are valid!"
    exit 0
else
    echo "❌ Found $errors dependency errors"
    exit 1
fi