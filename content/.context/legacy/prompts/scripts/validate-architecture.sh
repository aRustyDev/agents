#!/bin/bash
# Architecture Validation Script

echo "🔍 Architecture Validation Starting..."
echo "===================================="

# Check module sizes
echo ""
echo "📏 Checking module sizes..."
echo "--------------------------"

violations=0
for file in $(find .claude/commands -name "*.md" -type f); do
    lines=$(wc -l < "$file")
    if [ $lines -gt 200 ]; then
        echo "❌ $file: $lines lines (exceeds 200)"
        ((violations++))
    elif [ $lines -gt 180 ]; then
        echo "⚠️  $file: $lines lines (warning: approaching limit)"
    fi
done

if [ $violations -eq 0 ]; then
    echo "✅ All modules within size limits!"
else
    echo "🔴 Found $violations size violations"
fi

# Check naming conventions
echo ""
echo "📝 Checking naming conventions..."
echo "--------------------------------"

naming_issues=0
for file in $(find .claude/commands -name "*.md" -type f); do
    if grep -q "^module:" "$file"; then
        module_name=$(grep "^module:" "$file" | cut -d: -f2 | xargs)
        if [[ "$module_name" =~ _ ]]; then
            echo "❌ Naming issue in $file: $module_name (contains underscore)"
            ((naming_issues++))
        fi
    fi
done

if [ $naming_issues -eq 0 ]; then
    echo "✅ All module names follow conventions!"
else
    echo "🔴 Found $naming_issues naming issues"
fi

echo ""
echo "===================================="
echo "Validation complete!"
echo "Size violations: $violations"
echo "Naming issues: $naming_issues"
