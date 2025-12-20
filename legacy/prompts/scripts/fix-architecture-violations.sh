#!/bin/bash
# Architecture Violation Fixes - Automated Script
# Created: January 9, 2025
# Purpose: Fix module size and naming violations

set -e  # Exit on error

echo "🏗️  Architecture Violation Fixes Starting..."
echo "================================================"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base directory
BASE_DIR=".claude/commands"

# Create directories
echo -e "${YELLOW}📁 Creating required directories...${NC}"
mkdir -p "$BASE_DIR/plan/scripts"
mkdir -p "$BASE_DIR/plan/templates"
mkdir -p "$BASE_DIR/report/examples"
mkdir -p "$BASE_DIR/report/templates"

# Function to extract content between line numbers
extract_lines() {
    local file=$1
    local start=$2
    local end=$3
    local output=$4
    
    sed -n "${start},${end}p" "$file" > "$output"
    echo -e "${GREEN}✓ Extracted lines $start-$end from $(basename $file) to $(basename $output)${NC}"
}

# Function to fix module name in frontmatter
fix_module_name() {
    local file=$1
    local old_name=$2
    local new_name=$3
    
    if grep -q "module: $old_name" "$file"; then
        sed -i.bak "s/module: $old_name/module: $new_name/" "$file"
        echo -e "${GREEN}✓ Fixed module name in $(basename $file): $old_name → $new_name${NC}"
        rm "${file}.bak"
    fi
}

echo ""
echo -e "${YELLOW}🔧 Stage 1: Fixing Module Size Violations${NC}"
echo "================================================"

# Fix plan/cleanup.md (291 lines)
if [ -f "$BASE_DIR/plan/cleanup.md" ]; then
    echo "Processing plan/cleanup.md..."
    
    # Check if scripts already extracted
    if [ ! -f "$BASE_DIR/plan/scripts/cleanup_session.sh" ]; then
        # Extract cleanup session script
        cat > "$BASE_DIR/plan/scripts/cleanup_session.sh" << 'EOF'
#!/bin/bash
# Cleanup session script extracted from cleanup.md

cleanup_session() {
  local session_id=$1
  local session_dir=".plan/sessions/$session_id"
  
  if [ ! -d "$session_dir" ]; then
    echo "❌ Session not found: $session_id"
    return 1
  fi
  
  # Confirm deletion
  echo "⚠️  This will permanently delete session: $session_id"
  echo "Files to be removed:"
  ls -la "$session_dir"
  echo ""
  read -p "Are you sure? (yes/no): " confirm
  
  if [ "$confirm" = "yes" ]; then
    rm -rf "$session_dir"
    echo "✅ Session deleted: $session_id"
  else
    echo "❌ Cleanup cancelled"
  fi
}
EOF
        chmod +x "$BASE_DIR/plan/scripts/cleanup_session.sh"
        echo -e "${GREEN}✓ Created cleanup_session.sh${NC}"
    fi
    
    # TODO: Manually update cleanup.md to reference the extracted script
    echo -e "${YELLOW}⚠️  TODO: Manually update cleanup.md to reference scripts/cleanup_session.sh${NC}"
fi

# Fix plan/_core.md (285 lines)
if [ -f "$BASE_DIR/plan/_core.md" ]; then
    echo "Processing plan/_core.md..."
    
    # Create session structure template
    if [ ! -f "$BASE_DIR/plan/templates/session-structure.yaml" ]; then
        cat > "$BASE_DIR/plan/templates/session-structure.yaml" << 'EOF'
# Session Directory Structure Template
session_structure:
  root: .plan/sessions/{session_id}/
  files:
    - requirements.md
    - task-breakdown.yaml
    - dependencies.md
    - mvp-scope.md
    - issues.json
    - milestones.json
    - projects.json
    - labels.json
    - execute_plan.sh
    - summary.md
  directories:
    - backups/
    - artifacts/
EOF
        echo -e "${GREEN}✓ Created session-structure.yaml${NC}"
    fi
    
    # Create error codes template
    if [ ! -f "$BASE_DIR/plan/templates/error-codes.yaml" ]; then
        cat > "$BASE_DIR/plan/templates/error-codes.yaml" << 'EOF'
# Error codes for plan command
error_codes:
  ERR_NO_GH_CLI: 1
  ERR_NOT_GIT_REPO: 2
  ERR_NO_GH_AUTH: 3
  ERR_NO_REPO_ACCESS: 4
  ERR_INVALID_SUBCOMMAND: 5
  ERR_SESSION_NOT_FOUND: 6
  ERR_FILE_NOT_FOUND: 7
EOF
        echo -e "${GREEN}✓ Created error-codes.yaml${NC}"
    fi
fi

echo ""
echo -e "${YELLOW}🏷️  Stage 2: Fixing Naming Conventions${NC}"
echo "================================================"

# Fix module names
fix_module_name "$BASE_DIR/plan/_core.md" "Plan_core" "PlanCore"
fix_module_name "$BASE_DIR/report/_interactive.md" "Report_interactive" "ReportInteractive"
fix_module_name "$BASE_DIR/report/_templates.md" "Report_templates" "ReportTemplates"
fix_module_name "$BASE_DIR/report/audit.md" "Reportaudit" "ReportAudit"

echo ""
echo -e "${YELLOW}📋 Stage 3: Creating Validation Script${NC}"
echo "================================================"

# Create validation script
cat > validate-architecture.sh << 'EOF'
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
EOF

chmod +x validate-architecture.sh
echo -e "${GREEN}✓ Created validate-architecture.sh${NC}"

echo ""
echo "================================================"
echo -e "${GREEN}🎉 Initial fixes complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Run ./validate-architecture.sh to check current status"
echo "2. Manually update the large modules to reference extracted files"
echo "3. Continue with remaining fixes in architecture-implementation-tasks.md"
echo ""
echo "Files created:"
echo "- plan/scripts/cleanup_session.sh"
echo "- plan/templates/session-structure.yaml"
echo "- plan/templates/error-codes.yaml"
echo "- validate-architecture.sh"
echo ""
echo "Module names fixed:"
echo "- Plan_core → PlanCore"
echo "- Report_interactive → ReportInteractive"
echo "- Report_templates → ReportTemplates"
echo "- Reportaudit → ReportAudit"