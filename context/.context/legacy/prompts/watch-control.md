# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important

- ALL instructions within this document MUST BE FOLLOWED, these are not optional unless explicitly stated.
- ASK FOR CLARIFICATION If you are uncertain of any of thing within the document.
- DO NOT edit more code than you have to.
- DO NOT WASTE TOKENS, be succinct and concise.

## Watch Control System

- IMPERATIVE: ANY time the user mentions "watch control", "watch-control", or similar variations, IMMEDIATELY run the watch-control command without question.
- Execute using: `bash "/path/to/project/.claude/functions/tools/watch_control.sh"` followed by the appropriate command-line options
- You MUST use the EXACT path to the script: `/path/to/project/.claude/functions/tools/watch_control.sh`
- ALWAYS convert user's natural language requests to the appropriate command-line options with double-dashes

### Command Format Translation:

- The watch-control system accepts natural language but internally converts commands to proper format
- Commands use double-dash format (e.g., `--go-home`, `--switch-tool wearfx`, `--tool-preview`)
- You should handle this conversion automatically without showing the user the technical command format
- For bracket notation in cycling commands, convert to comma-separated format with colon for delay:
  - `[watchface, wearfx] with 2s delay` → `watchface,wearfx:2`
  - `[0,1,2,3] with 1s delay` → `0,1,2,3:1`

### Example Command Execution:

- User says: "run watch control and go to home screen"
- You MUST execute: `bash "/path/to/project/.claude/functions/tools/watch_control.sh" --go-home`

### Example Command Conversions:

Basic commands:

- "switch to wearfx tool" → `bash "/path/to/project/.claude/functions/tools/watch_control.sh" --switch-tool wearfx`
- "take a screenshot" → `bash "/path/to/project/.claude/functions/tools/watch_control.sh" --watch-screenshot`
- "preview current tool" / "show tool preview" / "tool preview" → `bash "/path/to/project/.claude/functions/tools/watch_control.sh" --tool-preview true`
- "hide tool preview" / "disable tool preview" → `bash "/path/to/project/.claude/functions/tools/watch_control.sh" --tool-preview false`
- "adjust tool clockwise" → `bash "/path/to/project/.claude/functions/tools/watch_control.sh" --adjust-tool true`
- "refresh background" / "update background" / "refresh watch background" → `bash "/path/to/project/.claude/functions/tools/watch_control.sh" --refresh-background`

Complex commands:

- "cycle through tool indices [0,1,2] with 3s delay" → `bash "/path/to/project/.claude/functions/tools/watch_control.sh" --cycle-tool-indices 0,1,2:3`
- "cycle through tools [watchface, scroll, wearfx] with 3s delay" → `bash "/path/to/project/.claude/functions/tools/watch_control.sh" --cycle-tools watchface,scroll,wearfx:3`
- "record screen for 30 seconds" → `bash "/path/to/project/.claude/functions/tools/watch_control.sh" --record-wear-screen-background 30`

### Multi-step Command Examples:

These examples demonstrate advanced usage with multiple operations and command-specific delays:

1. **Tool Showcase Sequence with Variable Delays**:

   ```
   bash "/path/to/project/.claude/functions/tools/watch_control.sh" --go-home --delay 2 --tool-preview --delay 3 --switch-tool wearfx --delay 5 --cycle-tool-indices 0,1,2,3,2,1,0:2 --delay 1 --watch-screenshot
   ```

2. **Complete Testing Sequence**:

   ```
   bash "/path/to/project/.claude/functions/tools/watch_control.sh" --enable-accessibility --go-home --delay 2 --tool-preview --delay 3 --cycle-tools watchface,wearfx,scroll,favourite\ apps:3 --delay 2 --switch-tool wearfx --cycle-tool-indices 0,1,2,3,2,1,0:1 --delay 1 --watch-screenshot
   ```

3. **Recording Interactions with Variable Timing**:
   ```
   bash "/path/to/project/.claude/functions/tools/watch_control.sh" --go-home --delay 1 --record-wear-screen-background 30 --switch-tool volume --delay 2 --tool-preview --delay 3 --cycle-tool-indices 0,1,2,3,2,1,0:1
   ```

### Understanding Order and Timing:

- **Flexible Command Order**: Commands now execute in the EXACT order you specify them
  - You can take screenshots after cycling, preview tools after recording, or any other sequence
  - All operations respect the order given in your command, with no preset execution order

- **Command-specific delays**: `delay 2s` creates a pause after ONLY the preceding command
  - Example: `go to home, delay 2s, tool preview, delay 5s, switch tool to wearfx`
  - This will wait 2s after going home and 5s after showing tool preview
  - Each command can have its own unique delay length
  - This is the most flexible way to control timing

- **Between list items**: When specified with a list (tools or indices), the delay applies BETWEEN items
  - Example: `switch tools [watchface, wearfx] 2s delay` means cycle through these tools with 2 seconds between each
  - Only applies to the specific cycling operation

- **Global function delay**: `function-delay 2` adds a 2-second pause after EVERY operation
  - Only use this when you want all operations to have the same delay
  - Command-specific delays will override this for individual commands

### Tool Index Range Constraints:

- **CRITICAL**: By default, tool indices should be within the range of 0-3 unless specifically instructed otherwise
- Only use higher indices (like 0-100) when the user explicitly requests or specifies them
- Example safe range: `switch tool index [0,1,2,3,2,1,0]`
- Example user-specified range: `switch tool index [0,1,5,10,100]` (only when requested)
- Using indices outside the safe range without user specification may cause errors
- Different tools may have different valid index ranges; when uncertain, stay within 0-3

### IMPORTANT RULES:

- DO NOT create new tools when using the watch control command
- If a command references a non-existent tool like "rotate chair", inform the user and suggest existing tools
- DO NOT question or ask for clarification when running watch-control - just execute it immediately
- Watch control commands should NEVER be interpreted as requests to create tools
- Always accept natural language descriptions and convert to appropriate command syntax
- For recording, use `record-wear-screen-background` by default unless specifically requested otherwise
- Tool preview can be requested in multiple ways (preview tool, show preview, tool preview, etc.) - recognize all variations
- When cycling through tools or indices, use the bracket notation in the command but understand it's converted internally
- When the user specifies delays, ALWAYS use command-specific delays (`delay Ns`) after each command rather than global function delay
- Recognize delay commands in various formats: "delay 2s", "wait 2 seconds", "pause for 2s", etc.
- The ORDER of operations in your command is exactly the order they will execute - this is very powerful!

### Tool Type-Specific Operations:

- IMPORTANT: Tools are categorized in toolNameMap.kt as either Single Broadcast or Multiple Broadcast
- You MUST dynamically check the current categorization from toolNameMap.kt whenever handling watch-control commands
- DO NOT rely on hardcoded lists of tools - always check the current categorization

**Process for handling tool operations:**

1. When a user requests a watch-control command, check the current tool categorization:
   - Read toolNameMap.kt to see which tools are marked as "Single Broadcast" vs "Multiple Broadcast"
   - OR use `--list-tools` to get the current list of available tools, then refer to toolNameMap.kt for categorization

2. For **Single Broadcast** tools (currently: volume, scene, brightness, hue, saturation, scroll):
   - These tools have a single index with a value that can be adjusted up/down
   - IMPORTANT: Tools are NOT necessarily at index 0 - they may be at any position from previous adjustments
   - TRANSLATE index operations to adjustment operations:
     - For `--change-tool-index N`, use multiple `--adjust-tool` calls in the appropriate direction
     - For incrementing values, use `--adjust-tool true` (clockwise)
     - For decrementing values, use `--adjust-tool false` (counter-clockwise)
     - Each adjustment changes the value by one increment
   - Example: For volume tool, to increase by approximately 5 increments:
     ```
     --adjust-tool true --delay 0.1 --adjust-tool true --delay 0.1 --adjust-tool true --delay 0.1 --adjust-tool true --delay 0.1 --adjust-tool true
     ```
   - RESET OPTION: If the user explicitly requests to reset tools to 0th position, add a reset sequence
     - This is only done when the user explicitly requests it
     - Reset sequence: switch to each tool and apply multiple adjust-tool false operations
     - Example reset for volume: `--switch-tool volume --adjust-tool false --delay 0.1 [...repeat 10+ times...]`

3. For **Multiple Broadcast** tools (currently: wearfx, watchface, favourite apps, media actions):
   - These tools have multiple distinct indices (options) to select between
   - Use index operations normally:
     - `--change-tool-index N` works correctly to select a specific option
     - `--cycle-tool-indices` works correctly to cycle through options

YOU are responsible for this translation when constructing watch-control commands

### Optional Tool Reset:

- Only perform a tool reset sequence when the user EXPLICITLY requests it with phrases like:
  - "Reset all tools to 0"
  - "Zero out the tools"
  - "Reset tool positions"
- IMPORTANT: Reset operations must be done BEFORE all other operations if requested
- CRITICAL: Only reset the Single Broadcast tools that will be USED in the subsequent operations
- The reset operation consists of:
  1. Identify which Single Broadcast tools will be used in the upcoming operations
  2. For each of these tools (EXCEPT scroll):
     a. Switch to the tool
     b. Apply multiple adjust-tool false operations (10+ times) to ensure it reaches 0th position
     c. Add a small delay between adjustments
- DO NOT include scroll tool in the reset operations
- DO NOT reset tools that won't be used in the subsequent operations
- Example reset sequence for operations that will use volume and brightness:
  ```
  --switch-tool volume --adjust-tool false --delay 0.1 [repeat 10+ times]
  --switch-tool brightness --adjust-tool false --delay 0.1 [repeat 10+ times]
  --go-home [then continue with other operations]
  ```
- This is OPTIONAL and only used when specifically requested
