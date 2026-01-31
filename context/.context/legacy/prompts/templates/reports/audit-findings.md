# Repository Audit Report

**Repository**: ${repository_name}  
**Audit Date**: ${audit_date}  
**Auditor**: ${auditor_role}  
**Version**: ${report_version}

---

## Executive Summary

### Overview
${executive_summary}

### Key Metrics
| Metric | Value | Status |
|--------|-------|--------|
| Total Files Analyzed | ${total_files} | - |
| Critical Issues | ${critical_issues} | ${critical_status} |
| High Priority Issues | ${high_issues} | ${high_status} |
| Medium Priority Issues | ${medium_issues} | ${medium_status} |
| Improvement Opportunities | ${opportunities} | - |

### Overall Health Score
**${health_score}/100** - ${health_rating}

---

## Critical Findings

${if critical_findings}
${foreach finding in critical_findings}
### 🚨 ${finding.title}
**Type**: ${finding.type}  
**Severity**: Critical  
**Location**: ${finding.location}  

**Description**: ${finding.description}

**Evidence**:
${finding.evidence}

**Impact**: ${finding.impact}

**Recommended Action**: ${finding.action}

---
${/foreach}
${else}
✅ No critical issues found.
${/if}

---

## Analysis Results

### 1. Repository Structure Analysis

#### Overview
${structure_summary}

#### Statistics
- **Directories**: ${directory_count}
- **Markdown Files**: ${md_file_count}
- **YAML Files**: ${yaml_file_count}
- **Shell Scripts**: ${shell_script_count}
- **Total Size**: ${repository_size}

#### Largest Components
${foreach component in largest_components}
- ${component.path}: ${component.size}
${/foreach}

#### Structure Issues
${foreach issue in structure_issues}
- ⚠️ ${issue.description}
${/foreach}

### 2. Duplication Analysis

#### Summary
- **Exact Duplicates**: ${exact_duplicates_count}
- **Near Duplicates**: ${near_duplicates_count}  
- **Pattern Duplications**: ${pattern_duplicates_count}
- **Potential Space Saving**: ${space_saving_potential}

#### Critical Duplications
${foreach dup in critical_duplications}
**Files**: ${dup.file1} ↔ ${dup.file2}
- **Similarity**: ${dup.similarity}%
- **Size**: ${dup.size}
- **Recommendation**: ${dup.recommendation}
${/foreach}

### 3. Gap Analysis

#### Component Coverage
| Component Type | Expected | Found | Gap |
|----------------|----------|-------|-----|
| Commands | ${expected_commands} | ${found_commands} | ${gap_commands} |
| Processes | ${expected_processes} | ${found_processes} | ${gap_processes} |
| Patterns | ${expected_patterns} | ${found_patterns} | ${gap_patterns} |
| Templates | ${expected_templates} | ${found_templates} | ${gap_templates} |

#### Missing Critical Components
${foreach component in missing_critical}
- ❌ **${component.type}**: ${component.name}
  - **Purpose**: ${component.purpose}
  - **Impact**: ${component.impact}
${/foreach}

#### Documentation Gaps
- **Files without headers**: ${files_without_headers}
- **Files without examples**: ${files_without_examples}
- **Missing README files**: ${missing_readmes}

### 4. Dead Context Analysis

#### Aged TODOs
${if aged_todos}
Found ${aged_todos_count} TODOs older than 90 days:
${foreach todo in aged_todos}
- 📌 ${todo.file}:${todo.line} (${todo.age} days old)
  - Content: `${todo.content}`
${/foreach}
${else}
✅ No aged TODOs found.
${/if}

#### Unreferenced Files
${if unreferenced_files}
Found ${unreferenced_files_count} potentially unused files:
${foreach file in unreferenced_files}
- 📄 ${file.path} (last modified: ${file.last_modified})
${/foreach}
${else}
✅ All files are referenced.
${/if}

### 5. Modularization Opportunities

#### Large Files Needing Split
${foreach file in large_files}
**File**: ${file.path}
- **Size**: ${file.lines} lines
- **Complexity Score**: ${file.complexity}
- **Suggested Modules**: ${file.suggested_splits}
- **Effort**: ${file.split_effort}
${/foreach}

#### Refactoring Opportunities
${foreach opportunity in refactoring_opportunities}
- **Pattern**: ${opportunity.pattern}
- **Occurrences**: ${opportunity.count}
- **Potential Modules**: ${opportunity.modules}
- **Benefit**: ${opportunity.benefit}
${/foreach}

---

## Recommendations

### Immediate Actions (Priority: Critical)
${foreach action in immediate_actions}
${action.number}. **${action.title}**
   - **What**: ${action.description}
   - **Why**: ${action.rationale}
   - **How**: ${action.implementation}
   - **Effort**: ${action.effort}
${/foreach}

### Short-term Improvements (1-2 weeks)
${foreach improvement in short_term}
${improvement.number}. **${improvement.title}**
   - **Impact**: ${improvement.impact}
   - **Effort**: ${improvement.effort}
   - **Dependencies**: ${improvement.dependencies}
${/foreach}

### Long-term Enhancements (1-3 months)
${foreach enhancement in long_term}
${enhancement.number}. **${enhancement.title}**
   - **Strategic Value**: ${enhancement.value}
   - **Complexity**: ${enhancement.complexity}
${/foreach}

---

## Action Plan

### Phase 1: Critical Fixes (Week 1)
${foreach task in phase1_tasks}
- [ ] ${task.description} (${task.effort})
${/foreach}

### Phase 2: Consolidation (Week 2-3)
${foreach task in phase2_tasks}
- [ ] ${task.description} (${task.effort})
${/foreach}

### Phase 3: Optimization (Week 4+)
${foreach task in phase3_tasks}
- [ ] ${task.description} (${task.effort})
${/foreach}

---

## Appendices

### A. Detailed File Analysis
${if include_file_details}
[Detailed analysis of each file is available in the supplementary report]
${/if}

### B. Dependency Graph
${if include_dependency_graph}
[Visual dependency graph available separately]
${/if}

### C. Automation Scripts
The following scripts can help with remediation:
${foreach script in automation_scripts}
- `${script.name}`: ${script.purpose}
${/foreach}

---

## Report Metadata

- **Analysis Duration**: ${analysis_duration}
- **Tools Used**: ${tools_list}
- **Confidence Level**: ${confidence_level}%
- **Next Review Date**: ${next_review_date}

---

*This report was generated using the Prompt Repository Auditor role v${auditor_version}*