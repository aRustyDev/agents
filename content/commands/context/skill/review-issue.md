---
description: Work an open issue with 'review' and 'skills' labels from Backlog - analyze, fix, and submit PR
---

# Review Skill Issue

Work an open issue from `aRustyDev/agents` that has both the `review` and `skills` labels AND is in the **Backlog** status of the AI Components project.

## Phase 1: Issue Discovery

1. Find issues with `review` AND `skills` labels that are in **Backlog** status:

   ```bash
   # List issues with review+skills labels
   gh issue list --repo aRustyDev/agents --label review --label skills --state open --json number,title,createdAt
   ```

2. For each candidate issue, check if it's in Backlog status:

   ```bash
   # Get project item ID and status for an issue
   gh api graphql -f query='
   query($owner: String!, $repo: String!, $issueNumber: Int!) {
     repository(owner: $owner, name: $repo) {
       issue(number: $issueNumber) {
         projectItems(first: 10) {
           nodes {
             id
             project { title number }
             fieldValueByName(name: "Status") {
               ... on ProjectV2ItemFieldSingleSelectValue {
                 name
                 optionId
               }
             }
           }
         }
       }
     }
   }' -f owner=aRustyDev -f repo=ai -F issueNumber=<ISSUE_NUMBER>
   ```

3. Select ONE issue that is in **Backlog** status (prefer older issues)

4. Read the full issue to understand:
   - Which skill needs refinement
   - What specific gaps/problems were identified
   - Any linked issues or PRs

## Phase 2: Claim Issue (Set to In Progress)

1. **Immediately update project status to "In progress"**:

   ```bash
   # Get the project item ID from Phase 1, then update status
   gh api graphql -f query='
   mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
     updateProjectV2ItemFieldValue(input: {
       projectId: $projectId
       itemId: $itemId
       fieldId: $fieldId
       value: { singleSelectOptionId: $optionId }
     }) {
       projectV2Item { id }
     }
   }' \
   -f projectId="PVT_kwHOAiotK84BLoKg" \
   -f itemId="<PROJECT_ITEM_ID>" \
   -f fieldId="PVTSSF_lAHOAiotK84BLoKgzg7JRok" \
   -f optionId="47fc9ee4"
   ```

   Note: Status option IDs:
   - Backlog: `f75ad846`
   - Ready: `e18bf179`
   - In progress: `47fc9ee4`
   - In review: `aba860b9`
   - Done: `98236657`

2. Add a comment to the issue claiming it:

   ```markdown
   🤖 Starting work on this issue.

   **Plan:**

   - [ ] Create worktree for isolated work
   - [ ] Run /refine-skill analysis
   - [ ] Run /validate-lang-conversion-skill (if applicable)
   - [ ] Apply fixes
   - [ ] Submit PR
   ```

## Phase 3: Setup Worktree

1. Create a feature branch in a worktree:

   ```bash
   ISSUE_NUM=<issue-number>
   SKILL_NAME=<skill-name-from-issue>
   git -C /Users/arustydev/repos/configs/ai worktree add \
     /private/tmp/ai-worktrees/review-${SKILL_NAME}-${ISSUE_NUM} \
     -b feat/review-${SKILL_NAME}-${ISSUE_NUM}
   ```

2. Change working context to the worktree (read files from there)

## Phase 4: Analysis

1. **Run /refine-skill** against the identified skill:
   - Analyze token budget (< 500 lines pass)
   - Check description quality for trigger words
   - Validate progressive disclosure pattern
   - Review directory structure
   - Generate improvement recommendations

2. **If skill is `convert-*` or `lang-*-dev`**, also run /validate-lang-conversion-skill:
   - Check 8-pillar coverage
   - Validate cross-references
   - Check bidirectional consistency (if reverse skill exists)

3. **Update the issue** with analysis findings:

   ```markdown
   ## Analysis Complete

   ### /refine-skill Results

   - Token budget: X/500 lines [PASS/WARN/FAIL]
   - Description quality: [GOOD/NEEDS IMPROVEMENT]
   - Progressive disclosure: [YES/NO]

   ### /validate-lang-conversion-skill Results (if applicable)

   - Pillar coverage: X/8
   - Missing pillars: [list]
   - Cross-references: [VALID/MISSING]

   ### Planned Fixes

   1. [Fix 1]
   2. [Fix 2]
   ...
   ```

## Phase 5: Implementation

1. Apply fixes identified in analysis:
   - Expand missing sections
   - Fix structural issues
   - Add missing cross-references
   - Improve examples

2. For each significant change, use atomic commits:

   ```bash
   git -C <worktree-path> add <files>
   git -C <worktree-path> commit -m "fix(skills): <description>"
   ```

3. **Update the issue** with implementation progress as you work

## Phase 6: Validation

1. Re-run /refine-skill to confirm improvements
2. Re-run /validate-lang-conversion-skill (if applicable)
3. Verify all checklist items from original issue are addressed

## Phase 7: Submit PR & Set to In Review

1. Push the branch:

   ```bash
   git -C <worktree-path> push -u origin feat/review-${SKILL_NAME}-${ISSUE_NUM}
   ```

2. Create PR with:
   - Title: `fix(skills): address review feedback for ${SKILL_NAME}`
   - Body: Summary of changes, link to issue with "Closes #X"
   - Reference the analysis and validation results

3. **Update project status to "In review"**:

   ```bash
   gh api graphql -f query='
   mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
     updateProjectV2ItemFieldValue(input: {
       projectId: $projectId
       itemId: $itemId
       fieldId: $fieldId
       value: { singleSelectOptionId: $optionId }
     }) {
       projectV2Item { id }
     }
   }' \
   -f projectId="PVT_kwHOAiotK84BLoKg" \
   -f itemId="<PROJECT_ITEM_ID>" \
   -f fieldId="PVTSSF_lAHOAiotK84BLoKgzg7JRok" \
   -f optionId="aba860b9"
   ```

4. **Add final comment to issue**:

   ```markdown
   ## Work Complete

   PR submitted: #XXX

   ### Changes Made

   - [Change 1]
   - [Change 2]

   ### Validation Results

   - /refine-skill: PASS
   - /validate-lang-conversion-skill: X/8 pillars

   This issue will be closed when the PR is merged.
   ```

## Phase 8: Cleanup

1. After PR is created, note the worktree location for later cleanup:

   ```bash
   # After PR merge, run:
   git -C /Users/arustydev/repos/configs/ai worktree remove /private/tmp/ai-worktrees/review-${SKILL_NAME}-${ISSUE_NUM}
   ```

## Project Status Reference

| Status | Option ID | When to Set |
|--------|-----------|-------------|
| Backlog | `f75ad846` | Issue waiting to be worked |
| Ready | `e18bf179` | Issue prepared, not started |
| In progress | `47fc9ee4` | **Set immediately when claiming** |
| In review | `aba860b9` | **Set when PR is submitted** |
| Done | `98236657` | Set automatically when PR merges |

## Decision Points

**If no issues are in Backlog:**

- Check Ready status issues as alternatives
- Report that no Backlog issues are available

**If multiple Backlog issues exist:**

- Prioritize by age (oldest first)
- Prioritize by blocking status (check if other issues reference it)
- Prioritize `lang-*-dev` skills over `convert-*` skills (foundational)

**If /refine-skill identifies many issues:**

- Focus on Critical and Warning items first
- Suggestions can be deferred to follow-up issues
- Document deferred items in the PR

**If skill has severe structural problems:**

- Consider whether a full rewrite is needed
- If so, update the issue with recommendation and ask for user input before proceeding

## Do NOT

- Work multiple issues in parallel (focus on one)
- Skip the analysis phase
- Forget to update the issue with progress
- Create commits directly on main
- Close issues manually (use "Closes #X" in PR)
- **Forget to update project status at start and end**
