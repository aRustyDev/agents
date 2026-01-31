- update 'justfile' to use .env/direnv
  - make ENV based file lookup (.claude/help/$CATEGORY/$PROJECT/INDEX.md)
- test reliability of the CLAUDE.md contents
- strategy docs/guides/templates for
  - docs
    - debug & analysis reports
    - what should go here vs in `help`
- review 'checklist' usage/presence
- extract examples from the 'plans' and expand on them in the 'examples' directory
- raw values should not consume inline comments
- "^key===value" should be error or "^key=<raw_value/string>"
- need well documented example kv file, to show what should be seen and why it should be seen that way. (last item before PR)
- how to tell if a highlighting issue is a parser issue vs a zed theme issue vs a zed extension issue
- url/uri should be special color
  - if in string '"', the '"' is green, the url is blue, any string interpolation is its standard color, and anything inside the interpolation is its standard color
  - if just raw, then it is blue, any string interpolation is its standard color, and anything inside the interpolation is its standard color


.claude/tests/tree-sitter/kvconf/phase1-verification.env
- all VALUES seem to be green now, except
  - line 38: url is pink
  - line 48: bool is orange
  - line 49: number is orange
  - line 50: url is pink
- line 57: the '===value' is all green

.claude/tests/tree-sitter/kvconf/phase2-verification.env
- all KEYS have turned to green
- all interpolated ENVVARS have turned to white
- escaped chars are now pink
- line 74: "This is actually raw_value not a string" is now green

.claude/tests/tree-sitter/kvconf/phase3-test.env
- line 15: VALUE is white
- line 16: VALUE is white
- line 17: "true" is orange, "val" is white
- line 18: "123" is orange, "abc" is white
- line 31: "6.022" is orange, but "e23" is white

.claude/tests/tree-sitter/kvconf/phase4-verification.env
- line 95: the "," following the URL is also pink

.claude/tests/tree-sitter/kvconf/phase5-edge-cases.env
- line 35: color code is a comment (greyed out)

.claude/tests/tree-sitter/kvconf/phase6-floats.env
- line 76: "abc123          # Should be white (raw_value)" is white
- line 92: 'v3.14       # "v" white, "3.14" might be orange or error' is white
- line 93: '$99.99   # "$" white, "99.99" might be orange or error' is white
- line 109: 'e10             # Should be white (raw_value)' is white
- line 110: 'E23                # Should be white (raw_value)' is white
- line 114: '.          # Should be white (raw_value)' is white
