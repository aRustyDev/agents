# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Important

- ALL instructions within this document MUST BE FOLLOWED, these are not optional unless explicitly stated.
- DO NOT edit more code than you have to.
- DO NOT WASTE TOKENS, be succinct and concise.

## Tool Maker System Guidelines

This document provides specific guidance for creating and maintaining tools in this Wear OS project.

### Tool System Overview

A tool is an ISOLATED unit of functionality which can be selected by a user and adjusted through a gesture.

### Tool Creation Priority Rules

- IMMEDIATE EXECUTION: Launch ultra-fast Tasks immediately upon tool creation requests
- NO CLARIFICATION: Skip asking what type of tool unless absolutely critical
- ASSUME DEFAULTS: Multi-option tool unless explicitly specified as single-option
- ULTRA-FAST BY DEFAULT: Always use 9-parallel-Task method for efficiency

### When to Create a Tool

- IMPERATIVE: When user requests tool creation, IMMEDIATELY launch ultra-fast Task creation without hesitation.
- Valid requests include "make a tool", "create a tool", "build a tool", or similar direct phrasing.
- Do NOT assume a tool should be created based on watch control system commands or other requests.
- Skip clarification questions and proceed directly to ultra-fast implementation.

### Ultra-Fast Tool Creation Workflow

**IMMEDIATE EXECUTION:** Upon ANY tool creation request, instantly launch all 9 Tasks in parallel:

1. **Container**: Create ToolNameContainer.kt
2. **Broadcast**: Create ToolNameBroadcast.kt
3. **Dialling**: Create ToolNameDialling.kt
4. **Confirmation**: Create ToolNameConfirmation.kt
5. **NameMap**: Update toolNameMap.kt
6. **LoadTools**: Update loadTools.kt
7. **DiallingMap**: Update toolDiallingMap.kt
8. **Execute**: Update executeToolCommand.kt
9. **Remaining**: Update toolStateResetData.kt, getVoiceKeyTermUrl.kt, getVoiceSystemMessage.kt

### Token Optimization during Tool Design

- Strip out all comments (including block comments, inline comments, and KDoc/Javadoc) when reading code files
- Filter out all logging statements and debug information when analyzing code
- In particularly large files, ignore formatting whitespace when analyzing structure

### Tool Design Guidelines

- Create tools in the `functions/tools` directory
- Multi-option tools (default): Base on `ToolWearFxContainer.kt` (no gradient background)
- Single-option tools (rare): Base on `ToolVolumeContainer.kt` (gradient background)
- **CRITICAL**: Make MINIMAL CHANGES to template structure and indentation patterns
- **CRITICAL**: Preserve existing patterns, function signatures, and component structures
- **CRITICAL**: DO NOT rewrite or restructure code unnecessarily
- Visualization: Only text(s) on arc as seen in templates - do not deviate unless explicitly requested
- Fixed measure policy: `true` for numerical text ('01', '1234'), `false` for word text ('play', 'red')
- Do not add parameters to functions
- Do not modify aspects of other tools

### Permitted Reference Files for Tool Integration and Design

DO NOT READ ANY OTHER FILES & TIGHTLY FOLLOW THE TOOL API ARCHITECTURE:

- `adjustCurrentTool()` in `adjustCurrentTool.kt`
- `LoadTools()` in `loadTools.kt`
- `toolStateResetData` list in `toolStateResetData.kt`
- `toolNameMap()` in `toolNameMap.kt`
- `getVoiceKeyTermUrl()` in `getVoiceKeyTermUrl.kt`
- `getVoiceSystemMessage()` in `getVoiceSystemMessage.kt`

### Additional Conditionally Permitted Reference Files for Tool Integration and Design

IMPORTANT ONLY READ ONE SET, DO NOT READ BOTH SETS:

- Single option tool files: (`ToolVolumeContainer.kt`, `ToolVolumeBroadcast.kt`, `ToolVolumeDialling.kt`)
- Multi option tool files: (`ToolWearFxContainer.kt`, `ToolWearFxBroadcast.kt`, `ToolWearFxDialling.kt`)

### DO NOT Read the following files under any circumstances UNLESS EXPLICITLY asked to do so:

- `singleOptionBroadcast.kt`
- `multipleOptionBroadcast.kt`

### Ultra-Fast Execution Rules

**IMPERATIVE: ALL tool creation uses ultra-fast method by default**

#### Critical Rules:

- IMMEDIATE START: No analysis, questions, or explanations before launching tasks
- Launch ALL 9 tasks in single message
- Each task handles ONLY specified files
- Use WearFx templates for Multiple Broadcast, Volume for Single Broadcast
- Task 9 combines 3 small config files to prevent over-splitting
- **EFFICIENCY OPTIMIZATION**: Use MultiEdit tool when making multiple edits to the same file within Tasks
