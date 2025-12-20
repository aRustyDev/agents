#!/usr/bin/env python3
"""Validate YAML frontmatter in all markdown files."""

import os
import sys
import yaml
from pathlib import Path

def validate_yaml_frontmatter(file_path):
    """Validate YAML frontmatter in a markdown file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        if not content.startswith('---'):
            return False, "No YAML frontmatter found"
            
        # Extract frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False, "Invalid frontmatter format"
            
        frontmatter = parts[1]
        
        try:
            data = yaml.safe_load(frontmatter)
            
            # Check required fields
            required_fields = ['module', 'scope', 'priority']
            missing = [field for field in required_fields if field not in data]
            
            if missing:
                return False, f"Missing required fields: {', '.join(missing)}"
                
            return True, "Valid"
            
        except yaml.YAMLError as e:
            return False, f"YAML parsing error: {str(e)}"
            
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def main():
    """Main function to validate all markdown files."""
    base_path = Path('.claude/commands')
    total_files = 0
    valid_files = 0
    invalid_files = []
    
    print("🔍 Validating YAML Frontmatter in Module Files")
    print("=" * 50)
    
    for md_file in base_path.rglob('*.md'):
        if md_file.name.startswith('.'):
            continue
            
        total_files += 1
        is_valid, message = validate_yaml_frontmatter(md_file)
        
        if is_valid:
            valid_files += 1
            print(f"✅ {md_file.relative_to('.')}")
        else:
            invalid_files.append((md_file, message))
            print(f"❌ {md_file.relative_to('.')}: {message}")
    
    print("\n" + "=" * 50)
    print(f"Total files checked: {total_files}")
    print(f"Valid files: {valid_files}")
    print(f"Invalid files: {len(invalid_files)}")
    
    if invalid_files:
        print("\n❌ Invalid files summary:")
        for file_path, error in invalid_files:
            print(f"  - {file_path.relative_to('.')}: {error}")
        sys.exit(1)
    else:
        print("\n✅ All YAML frontmatter is valid!")
        sys.exit(0)

if __name__ == "__main__":
    main()