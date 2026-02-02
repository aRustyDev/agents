## Lua Formula Patterns

> **Recommended:** Use `language: "make"` — Lua projects typically have a simple Makefile.

### Overview

Lua projects are rarely packaged as Homebrew formulas directly. Most Lua code is distributed via LuaRocks. For CLI tools written in Lua, use `language: "make"` with a wrapper script.

### Dependencies

```text
depends_on "lua"  # or luajit
```

### Example Pattern

```text
def install
  bin.install "mytool.lua" => "mytool"
end
```

### Common Issues

- **LuaRocks:** Consider if the tool is better installed via `luarocks install`
- **Lua version:** Check compatibility with Lua 5.3 vs 5.4 vs LuaJIT
- **C modules:** Lua C modules need compilation — add system deps
