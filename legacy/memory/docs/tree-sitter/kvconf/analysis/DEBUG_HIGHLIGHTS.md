# Debugging Zed Highlights Issue

## The Problem
- Error: "Query error at 26:2. Invalid node type bool"
- Our highlights.scm only has 12 lines
- The error persists even after:
  - Clearing all caches
  - Restarting Zed
  - Using correct grammar repository

## What We Know
1. Our grammar only defines these node types:
   - comment
   - variable
   - identifier
   - value
   - Various punctuation tokens

2. Our highlights.scm references only existing types:
   ```scheme
   ; Comments
   (comment) @comment
   
   ; Variable names (keys)
   (variable
     name: (identifier) @variable.parameter)
   
   ; All values as strings
   (value) @string
   
   ; Operators
   "=" @operator
   ```

3. The error mentions line 26, but our file only has 12 lines

## Hypothesis
Zed might be:
1. Using a built-in env language definition
2. Merging highlights from multiple sources
3. Caching compiled queries somewhere we haven't found

## Next Steps
1. Check if Zed has a built-in env language
2. Try renaming the language to avoid conflicts
3. Contact Zed support/community about this issue