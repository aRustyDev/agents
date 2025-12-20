#!/bin/bash
# security-scan.sh - Scan for hardcoded secrets and sensitive data

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Security patterns to check
declare -A PATTERNS=(
    ["password"]='[Pp]assword[[:space:]]*[=:][[:space:]]*["\047][^"\047]+["\047]'
    ["api_key"]='[Aa][Pp][Ii][_-]?[Kk][Ee][Yy][[:space:]]*[=:][[:space:]]*["\047][^"\047]+["\047]'
    ["token"]='[Tt]oken[[:space:]]*[=:][[:space:]]*["\047][^"\047]+["\047]'
    ["secret"]='[Ss]ecret[[:space:]]*[=:][[:space:]]*["\047][^"\047]+["\047]'
    ["private_key"]='BEGIN[[:space:]]+(RSA|DSA|EC|OPENSSH|PRIVATE)[[:space:]]+KEY'
    ["aws_creds"]='(aws_access_key_id|aws_secret_access_key)[[:space:]]*[=:]'
    ["connection_string"]='(mongodb|postgres|mysql|redis)://[^[:space:]]+'
)

# Whitelist patterns (false positives)
WHITELIST_PATTERNS=(
    'password.*=.*["\047]\$\{.*\}["\047]'  # ${variable} syntax
    'example\.com'
    'placeholder'
    'your[_-]?api[_-]?key'
    'your[_-]?password'
    '<.*>'  # Placeholder syntax
    '\[.*\]'  # Bracket placeholders
)

# Check if any files were passed
if [ $# -eq 0 ]; then
    echo "No files to check"
    exit 0
fi

# Track findings
FAILED=0
SECURITY_ISSUES=()

# Function to check if line is whitelisted
is_whitelisted() {
    local line=$1
    
    for pattern in "${WHITELIST_PATTERNS[@]}"; do
        if echo "$line" | grep -qE "$pattern"; then
            return 0
        fi
    done
    
    return 1
}

# Check each file
for file in "$@"; do
    # Skip if file doesn't exist (deleted)
    if [ ! -f "$file" ]; then
        continue
    fi
    
    # Skip binary files
    if ! file "$file" | grep -q "text"; then
        continue
    fi
    
    echo -e "${YELLOW}Security scan for: $(basename "$file")${NC}"
    file_clean=true
    
    # Check each security pattern
    for pattern_name in "${!PATTERNS[@]}"; do
        pattern="${PATTERNS[$pattern_name]}"
        
        # Search for pattern
        matches=$(grep -nE "$pattern" "$file" 2>/dev/null || true)
        
        if [ -n "$matches" ]; then
            # Check each match against whitelist
            while IFS= read -r match; do
                line_num=$(echo "$match" | cut -d: -f1)
                line_content=$(echo "$match" | cut -d: -f2-)
                
                if ! is_whitelisted "$line_content"; then
                    echo -e "  ${RED}✗ Potential $pattern_name found at line $line_num${NC}"
                    echo -e "    ${RED}$line_content${NC}"
                    SECURITY_ISSUES+=("$file:$line_num - Potential $pattern_name")
                    file_clean=false
                    FAILED=1
                fi
            done <<< "$matches"
        fi
    done
    
    # Additional checks
    
    # Check for email addresses (PII)
    if grep -qE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' "$file"; then
        if ! grep -qE '(example\.com|test\.com|your[_-]?email)' "$file"; then
            echo -e "  ${YELLOW}⚠ Potential email address found (PII)${NC}"
            file_clean=false
        fi
    fi
    
    # Check for IP addresses
    if grep -qE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' "$file"; then
        # Allow common private/example IPs
        if ! grep -qE '(127\.0\.0\.1|localhost|0\.0\.0\.0|192\.168\.|10\.|172\.16\.)' "$file"; then
            echo -e "  ${YELLOW}⚠ Potential IP address found${NC}"
            file_clean=false
        fi
    fi
    
    if $file_clean; then
        echo -e "  ${GREEN}✓ No security issues found${NC}"
    fi
done

# Report overall results
echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Security scan passed - no secrets detected${NC}"
    exit 0
else
    echo -e "${RED}❌ Security issues detected:${NC}"
    for issue in "${SECURITY_ISSUES[@]}"; do
        echo -e "${RED}   - $issue${NC}"
    done
    echo ""
    echo -e "${YELLOW}Please remove hardcoded secrets and use:${NC}"
    echo "  - Environment variables: \${ENV_VAR}"
    echo "  - Configuration files (not in repo)"
    echo "  - Secret management systems"
    echo "  - Placeholder values in examples"
    exit 1
fi