---
module: PreCommitHookResolution
scope: context
triggers: ["create hook", "find hook", "automate check", "prevent error"]
conflicts: []
dependencies: ["IssueTracking", "PreCommitConfiguration"]
priority: high
---

# Pre-commit Hook Resolution Process

## Purpose
Find or create pre-commit hooks to solve identified recurring problems, transforming manual fixes into automated prevention through either existing solutions or custom implementations.

## Trigger
Called by RecurringProblemIdentification when a pattern is worth automating, or directly when a specific check needs automation.

## Prerequisites
- Clear problem definition from pattern analysis
- Understanding of what needs to be checked/fixed
- Pre-commit framework installed and configured

## Parameters
- Type: "find_existing" or "create_custom"
- Problem: Description of issue to solve
- Complexity: "simple", "medium", or "complex"

## Steps

### Step 1: Problem Refinement
```
1.1 Clarify the exact check needed:
    - What patterns indicate the problem?
    - What constitutes a violation?
    - Can it be automatically fixed?
    - What should error messages say?

1.2 Define success criteria:
    - Zero false positives acceptable?
    - Performance requirements (< 2 seconds?)
    - Auto-fix vs. error only?
    - Scope of files to check

1.3 Document test cases:
    - Examples that should fail
    - Examples that should pass
    - Edge cases to consider
    - Performance test scenarios
```

### Step 2: Existing Solution Search (if Type == "find_existing")
```
2.1 Search official pre-commit registry:
    - Visit pre-commit.com/hooks.html
    - Search for problem keywords
    - Check language-specific sections
    - Review hook descriptions

2.2 Search community repositories:
    GitHub searches:
    - "pre-commit hook ${problem_keywords}"
    - "pre-commit ${language} ${issue_type}"
    - Check awesome-pre-commit lists
    - Review popular pre-commit configs

2.3 Evaluate found hooks:
    For each candidate:
    - Read documentation thoroughly
    - Check maintenance status (last update)
    - Review open issues
    - Count GitHub stars/adoption
    - Test with sample files

2.4 Test promising hooks:
    Create test configuration:
    """
    repos:
      - repo: ${hook_repository}
        rev: ${latest_version}
        hooks:
          - id: ${hook_id}
            args: [${test_args}]
    """

    Run on test files:
    - Known violations
    - Known good files
    - Edge cases
    - Project samples
```

### Step 3: Hook Selection or Custom Decision
```
3.1 IF suitable_hook_found:
    3.1.1 Document findings:
        "Found: ${hook_name} from ${repository}
         Solves: ${problem_description}
         Tested: ${test_results}
         Configuration: ${recommended_config}"

    3.1.2 Integration plan:
        - Optimal configuration
        - Any exclusions needed
        - Performance impact
        - Team training needs

    3.1.3 Request approval:
        "Shall I add ${hook_name} to .pre-commit-config.yaml?
         This will ${expected_behavior}
         Preventing ${problem_frequency} issues/month"

3.2 ELSE no_suitable_hook:
    3.2.1 Document search results:
        "Searched: ${sources_checked}
         Found: ${close_matches}
         Why unsuitable: ${reasons}
         Proceeding with custom hook creation"

    3.2.2 Proceed to custom creation
```

### Step 4: Custom Hook Design (if Type == "create_custom" or no existing found)
```
4.1 Choose implementation approach:

    For simple pattern matching:
    - Use shell script with grep/sed
    - Quick to implement and test
    - Fast execution

    For file parsing:
    - Use Python with regex/AST
    - More robust checking
    - Better error messages

    For language-specific:
    - Use language's own tools
    - Leverage existing parsers
    - Native understanding

4.2 Design hook interface:
    - Input: File list from pre-commit
    - Processing: Check each file
    - Output: Exit 0 (pass) or 1 (fail)
    - Messages: Clear, actionable errors

4.3 Plan error handling:
    - File encoding issues
    - Syntax errors in checked files
    - Performance timeouts
    - Helpful error messages
```

### Step 5: Custom Hook Implementation
```
5.1 Create hook script:

    Example Python hook:
    """
    #!/usr/bin/env python3
    import sys
    import re
    from pathlib import Path

    # Hook: ${hook_purpose}
    # Prevents: ${problem_description}

    def check_file(filepath):
        '''Check single file for violations'''
        try:
            content = Path(filepath).read_text()

            # Define pattern to catch
            pattern = re.compile(r'${violation_pattern}')

            violations = []
            for i, line in enumerate(content.splitlines(), 1):
                if pattern.search(line):
                    violations.append((i, line.strip()))

            return violations

        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return []

    def main():
        '''Check all files passed as arguments'''
        exit_code = 0

        for filepath in sys.argv[1:]:
            violations = check_file(filepath)

            if violations:
                exit_code = 1
                print(f"\n❌ {filepath}")
                for line_num, content in violations:
                    print(f"  Line {line_num}: {content}")
                print(f"  Fix: ${fix_instruction}")

        if exit_code == 0:
            print("✅ All files pass ${check_name}")

        return exit_code

    if __name__ == '__main__':
        sys.exit(main())
    """

    Example shell hook:
    """
    #!/usr/bin/env bash
    # Hook: ${hook_purpose}

    EXIT_CODE=0

    for file in "$@"; do
        if grep -q "${pattern}" "$file"; then
            echo "❌ $file contains ${violation_description}"
            echo "  Lines:"
            grep -n "${pattern}" "$file" | sed 's/^/    /'
            echo "  Fix: ${fix_instruction}"
            EXIT_CODE=1
        fi
    done

    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ All files pass ${check_name}"
    fi

    exit $EXIT_CODE
    """

5.2 Add auto-fix capability (if applicable):
    """
    # Add --fix argument handling
    if '--fix' in sys.argv:
        sys.argv.remove('--fix')
        fix_mode = True

    # In check_file function
    if fix_mode and violations:
        fixed_content = re.sub(pattern, replacement, content)
        Path(filepath).write_text(fixed_content)
        print(f"🔧 Fixed {len(violations)} issues in {filepath}")
    """
```

### Step 6: Hook Testing
```
6.1 Create test fixtures:
    Good files:
    - Should pass without issues
    - Edge cases that are valid
    - Previously problematic but fixed

    Bad files:
    - Clear violations
    - Edge cases that should fail
    - Multiple violations
    - Mixed content

6.2 Test execution:
    # Direct execution
    python hook_script.py test_file_bad.py
    # Should show violations

    python hook_script.py test_file_good.py
    # Should pass cleanly

    # Performance test
    time python hook_script.py large_file.py
    # Should complete < 2 seconds

6.3 Create .pre-commit-hooks.yaml:
    """
    - id: ${hook_id}
      name: ${human_readable_name}
      description: ${what_it_prevents}
      entry: ${script_name}
      language: python
      types: [${file_types}]
      require_serial: false
    """

6.4 Integration test:
    Add to .pre-commit-config.yaml:
    """
    repos:
      - repo: local
        hooks:
          - id: ${hook_id}
            name: ${human_readable_name}
            entry: ${script_path}
            language: python
            types: [${file_types}]
    """

    Run: pre-commit run ${hook_id} --all-files
```

### Step 7: Documentation and Rollout
```
7.1 Document the hook:
    Create README for hook:
    """
    # ${hook_name}

    ## Purpose
    ${what_problem_it_solves}

    ## What it checks
    ${detailed_check_description}

    ## Usage
    Add to .pre-commit-config.yaml:
    ${configuration_example}

    ## Examples
    ### Will fail on:
    ${bad_example}

    ### Will pass on:
    ${good_example}

    ## Configuration options
    ${any_args_or_options}
    """

7.2 Update project documentation:
    - Add to development setup guide
    - Note in troubleshooting section
    - Include in onboarding docs

7.3 Communicate to team:
    Issue update:
    "Implemented pre-commit hook for ${problem}
     - Prevents: ${issues_prevented}
     - Saves: ~${time_saved}/month
     - Tested on: ${test_description}

     Action required: Run 'pre-commit install --install-hooks'
     after pulling latest changes."
```

### Step 8: Contribution Decision
```
8.1 Assess general usefulness:
    - Is problem language-specific or universal?
    - Would other projects benefit?
    - Is implementation clean and maintainable?
    - Does it handle edge cases well?

8.2 IF generally_useful:
    Execute: Process: PreCommitHookContribution
    - Generalize for broader use
    - Add comprehensive tests
    - Create full documentation
    - Submit to community
```

## Hook Examples

### Example: Hardcoded URL Detection
```python
#!/usr/bin/env python3
'''Prevent hardcoded development URLs'''
import sys
import re

DEV_URL_PATTERN = re.compile(
    r'(localhost|127\.0\.0\.1|192\.168\.|10\.0\.)\S*',
    re.IGNORECASE
)

ALLOWED_CONTEXTS = [
    'config.example',
    'docker-compose.yml',
    'README.md'
]

def main():
    exit_code = 0

    for filepath in sys.argv[1:]:
        # Skip allowed files
        if any(allowed in filepath for allowed in ALLOWED_CONTEXTS):
            continue

        with open(filepath, 'r') as f:
            for i, line in enumerate(f, 1):
                if DEV_URL_PATTERN.search(line):
                    if 'CONFIG' not in line and 'env' not in line:
                        print(f"❌ {filepath}:{i} contains hardcoded dev URL")
                        print(f"   {line.strip()}")
                        print(f"   Use configuration variables instead")
                        exit_code = 1

    return exit_code

if __name__ == '__main__':
    sys.exit(main())
```

## Integration Points

- **Called by**: Process: RecurringProblemIdentification
- **Updates**: .pre-commit-config.yaml
- **Creates**: Hook scripts and documentation
- **May trigger**: Process: PreCommitHookContribution
- **Documents in**: Issue tracker

## Best Practices

### Do's
- ✅ Start with existing hooks when possible
- ✅ Test thoroughly before deployment
- ✅ Provide clear, actionable error messages
- ✅ Make hooks fast (< 2 seconds)
- ✅ Document configuration options

### Don'ts
- ❌ Create overly strict hooks
- ❌ Ignore false positive impact
- ❌ Make hooks that require context
- ❌ Forget about performance
- ❌ Skip edge case testing

Remember: The best hook is one that developers forget exists because it quietly prevents problems without getting in the way of legitimate work.
