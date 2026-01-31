# ADR-004: Zed Extension Hash Synchronization Issues

**Date**: 2025-09-01
**Status**: Accepted
**Context**: Recurring failures with Zed extension installation due to commit hash mismatches

## Problem Statement

Throughout Phases 1-3, we've repeatedly encountered the error:
```
failed to fetch revision <hash> in directory '/path/to/grammars/env'
```

This happens because:
1. The assistant provides truncated commit hashes
2. The assistant uses outdated commit hashes
3. The phase plans lack explicit verification steps

## Root Cause Analysis

### 1. Hash Length Confusion
- Git accepts short hashes (7+ chars) for most operations
- Zed requires FULL 40-character hashes for remote fetching
- The assistant often truncates hashes to common lengths (7, 12, or 16 chars)

### 2. Timing Issues
- Changes are pushed to GitHub
- Extension.toml is updated with a hash
- The hash used might be from a local commit, not the pushed one
- Or the assistant copies an old hash from memory

### 3. Insufficient Instructions
Current phase plans say:
```
Update extension.toml with full commit hash
```

This is ambiguous and doesn't specify:
- HOW to get the full hash
- WHEN to get it (after pushing)
- HOW to verify it's correct

## Decision

All phase plans and checkpoint reviews MUST include explicit Zed extension synchronization verification:

### Mandatory Steps
```bash
# 1. Get the EXACT commit hash after pushing
cd /path/to/tree-sitter-dotenv
git push origin feature/typed-values
FULL_HASH=$(git log -1 --format="%H")
echo "Full commit hash: $FULL_HASH"
echo "Hash length: ${#FULL_HASH}"  # MUST be 40

# 2. Verify the hash is on GitHub
git ls-remote origin | grep "$FULL_HASH"

# 3. Update extension.toml with EXACT hash
cd /path/to/zed-env
sed -i '' "s/commit = \".*\"/commit = \"$FULL_HASH\"/" extension.toml

# 4. Verify the update
grep "commit = " extension.toml
# MUST show: commit = "<40-character-hash>"

# 5. Test fetch manually before installation
cd grammars
git init temp-test
cd temp-test
git remote add origin https://github.com/aRustyDev/tree-sitter-dotenv
git fetch origin "$FULL_HASH" --depth 1
cd ../..
rm -rf grammars/temp-test
```

### Checkpoint Review Requirements

Every checkpoint MUST verify:
- [ ] Commit hash in extension.toml is EXACTLY 40 characters
- [ ] Hash matches the latest pushed commit
- [ ] Manual fetch test passes
- [ ] Extension installs without errors
- [ ] Highlighting works in test file

## Consequences

### Positive
- Eliminates recurring installation failures
- Makes checkpoints truly verifiable
- Reduces debugging time
- Improves user trust

### Negative
- Adds ~2 minutes to each checkpoint
- More verbose phase plans
- Requires explicit command execution

## Implementation

Update all remaining phase plans (4-7) to include:
1. Explicit hash verification section
2. Manual fetch testing
3. Failure recovery steps
4. Clear error messages for hash mismatches

## Lessons Learned

The assistant's tendency to truncate or misremember hashes stems from:
1. Training on git workflows where short hashes are common
2. Not understanding Zed's specific requirements
3. Lack of explicit verification steps in instructions

This ADR ensures future phases won't suffer from this issue.