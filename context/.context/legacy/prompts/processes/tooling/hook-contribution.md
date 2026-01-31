---
name: Pre-commit Hook Contribution Process
module_type: process
scope: context
priority: medium
triggers: ["contribute hook", "share hook", "upstream contribution", "hook to community", "generalize hook"]
dependencies: ["processes/issue-tracking/issue-creation.md", "processes/security/data-sanitization.md", "processes/version-control/commit-standards.md"]
conflicts: []
version: 1.0.0
---

# Pre-commit Hook Contribution Process

## Purpose
Share custom pre-commit hooks that solve general problems back to the community repository, transforming local solutions into reusable tools that benefit developers everywhere.

## Trigger
When a custom hook has proven valuable locally and could benefit other projects facing similar issues.

## Prerequisites
- Custom hook running successfully for at least 5 commits
- Hook solves a generalizable problem
- Hook is well-tested and documented
- Time available for contribution process

## Process Steps

### 1. Hook Generalization
**Goal**: Transform project-specific hook into universally applicable tool

**Actions**:
1. Remove project-specific logic:
   - Hardcoded paths or names
   - Project-specific conventions
   - Internal terminology
   - Custom business logic

2. Add configuration options:
   ```python
   # Original project-specific:
   if 'src/api' in filepath:
       special_check()
   
   # Generalized configurable:
   parser.add_argument('--include-paths', nargs='*',
                      help='Paths requiring special checks')
   ```

3. Ensure cross-platform compatibility:
   - Path separators: Use pathlib or os.path
   - Line endings: Handle both \n and \r\n
   - Shell commands: Avoid platform-specific
   - File permissions: Test on Windows/Mac/Linux

4. Add sensible defaults:
   - Work out-of-box for common cases
   - Make configuration optional
   - Provide example configurations

**Checks**:
- [ ] No hardcoded project references
- [ ] Configurable for different use cases
- [ ] Cross-platform compatible
- [ ] Works with zero configuration

### 2. Comprehensive Documentation
**Goal**: Create clear, helpful documentation for users

**Actions**:
1. Write detailed README:
   ```markdown
   # ${hook_name}
   
   ## What it does
   ${clear_one_paragraph_description}
   
   ## Why you need it
   ${problem_it_solves_with_examples}
   
   ## Installation
   Add to your `.pre-commit-config.yaml`:
   ```yaml
   - repo: https://github.com/aRustyDev/pre-commit-hooks
     rev: main
     hooks:
       - id: ${hook_id}
   ```
   
   ## Examples
   
   ### What it catches
   ❌ This will fail:
   ```${language}
   ${bad_example_code}
   ```
   
   ✅ This will pass:
   ```${language}
   ${good_example_code}
   ```
   ```

2. Document all configuration options
3. Include troubleshooting section
4. Add performance considerations

**Checks**:
- [ ] Clear problem statement
- [ ] Installation instructions
- [ ] Usage examples
- [ ] Configuration documented
- [ ] Edge cases covered

### 3. Issue Creation in Target Repository
**Goal**: Get maintainer approval before implementing

**Actions**:
1. Navigate to: https://github.com/aRustyDev/pre-commit-hooks
2. Search for existing similar issues
3. Create detailed proposal issue:
   
   Title: "New Hook: ${descriptive_hook_name}"
   
   Body:
   ```markdown
   ## Hook Proposal: ${hook_name}
   
   ### Problem it solves
   ${detailed_problem_description}
   
   ### How the hook works
   ${high_level_algorithm_description}
   
   ### Why it's generally useful
   ${explanation_of_broad_applicability}
   
   ### Testing
   Used in production for ${timeframe} with:
   - ${number} issues caught
   - Zero false positives
   
   Ready to submit PR with full implementation.
   ```

4. Record issue number for tracking
5. Wait for maintainer feedback

**Checks**:
- [ ] Issue clearly describes value
- [ ] No duplicate functionality
- [ ] Maintainer approval received
- [ ] Implementation approach agreed

### 4. Fork and Implementation
**Goal**: Implement hook following repository standards

**Actions**:
1. Fork repository:
   ```bash
   git clone https://github.com/${your_username}/pre-commit-hooks
   cd pre-commit-hooks
   git checkout -b add-${hook_name}-hook
   ```

2. Study repository structure:
   - Hook organization
   - Naming conventions
   - Test framework
   - Documentation standards

3. Add hook implementation:
   - Create hook file
   - Update .pre-commit-hooks.yaml
   - Follow existing patterns

4. Add tests if framework exists
5. Update repository documentation

**Checks**:
- [ ] Follows repository conventions
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No regressions

### 5. Testing and Validation
**Goal**: Ensure hook works reliably across projects

**Actions**:
1. Test from your fork:
   ```yaml
   repos:
     - repo: https://github.com/${your_username}/pre-commit-hooks
       rev: ${your_branch}
       hooks:
         - id: ${hook_id}
   ```

2. Test on multiple projects:
   - Different languages
   - Different sizes
   - Different configurations

3. Run repository test suite
4. Verify documentation accuracy

**Checks**:
- [ ] Works on 3+ different projects
- [ ] All configurations tested
- [ ] Performance acceptable
- [ ] No false positives

### 6. Pull Request Submission
**Goal**: Submit high-quality PR for review

**Actions**:
1. Commit changes:
   ```
   feat: add ${hook_name} hook
   
   Implements detection for ${problem_description}.
   Tested on multiple projects with zero false positives.
   
   Resolves #${issue_number}
   ```

2. Push to fork
3. Create pull request:
   - Reference issue
   - Summarize implementation
   - Show example usage
   - Note testing done

**Checks**:
- [ ] Clean commit history
- [ ] PR links to issue
- [ ] CI/CD passes
- [ ] Documentation complete

### 7. Review Process Management
**Goal**: Successfully navigate code review

**Actions**:
1. Monitor PR for feedback
2. Address review comments promptly
3. Make requested changes
4. Maintain CI/CD compliance

**Decision Point**:
```
Review feedback requires major changes?
├─ Yes → Discuss approach with maintainer
├─ No → Implement requested changes
└─ Unclear → Ask for clarification
```

**Checks**:
- [ ] All feedback addressed
- [ ] CI/CD remains green
- [ ] Maintainer approves
- [ ] Ready to merge

### 8. Post-Merge Activities
**Goal**: Complete contribution cycle

**Actions**:
1. Update local projects to use official version
2. Document contribution in issue tracker
3. Close tracking issue
4. Announce to team

**Checks**:
- [ ] Local usage updated
- [ ] Issue documentation complete
- [ ] Team informed
- [ ] Success celebrated

### 9. Maintenance and Support
**Goal**: Support contributed hook

**Actions**:
1. Monitor for issues
2. Provide usage support
3. Track adoption metrics
4. Plan improvements if needed

**Checks**:
- [ ] No critical bugs reported
- [ ] Questions answered
- [ ] Usage growing
- [ ] Quality maintained

## Output
- Hook available in official repository
- Documentation for users
- Local configuration updated
- Community benefit documented

## Integration Points
- **Triggered by**: Custom hook proving valuable
- **Executes**: Process: DataSanitization (for public content)
- **Executes**: Process: IssueUpdate (for tracking)
- **Results in**: Community-available tool

## Best Practices

### DO
- ✅ Generalize thoroughly before contributing
- ✅ Test on diverse projects
- ✅ Document comprehensively
- ✅ Respond quickly to feedback
- ✅ Support after merge

### DON'T
- ❌ Submit project-specific logic
- ❌ Skip cross-project testing
- ❌ Ignore maintainer guidelines
- ❌ Abandon during review
- ❌ Forget local updates

## Troubleshooting

### Hook Too Specific
- Extract configuration options
- Find common patterns
- Consider plugin architecture
- Split into multiple hooks

### Performance Issues
- Profile on large codebases
- Add file filtering options
- Consider parallelization
- Document limitations

### Maintainer Concerns
- Discuss alternative approaches
- Provide more examples
- Clarify value proposition
- Consider splitting PR

## Success Metrics
- Merged within 2 weeks
- Positive maintainer feedback
- Adopted by 5+ projects in first month
- No major bug reports
- Time saved > time invested

---
*Contributing hooks back to the community multiplies their value and improves everyone's development experience.*