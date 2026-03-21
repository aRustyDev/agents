# Troubleshooting

Common issues and solutions for the design-to-code plugin.

## Common Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| Command not found | Plugin not installed | Run `just install-plugin design-to-code` |
| MCP server timeout | Server not running | Run `just enable-mcp design-to-code` |
| Figma API error | Invalid or expired token | Refresh `FIGMA_ACCESS_TOKEN` |
| Sketch file not found | Sketch app not installed | Install Sketch from Mac App Store |
| Penpot connection failed | MCP server not running | Start Penpot MCP server |

## Detailed Solutions

### Issue: Figma Authentication Failed

**Symptoms:**

- "Invalid access token" error
- 401 Unauthorized responses

**Solution:**

1. Generate a new token at <https://www.figma.com/developers/api#access-tokens>
2. Set the environment variable:

   ```bash
   export FIGMA_ACCESS_TOKEN="your-new-token"
   ```

3. Restart Claude Code

### Issue: Penpot MCP Server Not Running

**Symptoms:**

- "Cannot connect to Penpot MCP server" error
- Timeout when extracting from Penpot

**Solution:**

1. Clone and build the server:

   ```bash
   git clone https://github.com/penpot/penpot-mcp.git
   cd penpot-mcp
   npm install && npm run bootstrap
   ```

2. Start the server:

   ```bash
   npm start
   ```

3. Load the plugin in Penpot from `http://localhost:4400/manifest.json`

### Issue: Sketch File Access Denied

**Symptoms:**

- "Cannot read Sketch file" error
- Empty component list

**Solution:**

1. Ensure Sketch app is installed
2. Open Sketch at least once to accept permissions
3. Check file exists and is not corrupted
4. Try running: `npx sketch-context-mcp --local-file=/path/to/file.sketch`

### Issue: Token Extraction Returns Empty

**Symptoms:**

- No tokens extracted from design file
- Missing colors, fonts, or spacing

**Solution:**

1. Verify the design file has defined styles (not just local colors)
2. Check that components are properly named
3. Use structured design tokens in your design tool
4. Try extracting from a specific frame/component

### Issue: Generated Code Doesn't Match Design

**Symptoms:**

- Colors or spacing are incorrect
- Layout doesn't match design

**Solution:**

1. Re-extract tokens to ensure latest values
2. Check if design uses relative vs absolute values
3. Verify the correct output format is selected
4. Use `/compare-design` to identify discrepancies

## FAQ

### Q: How do I update the plugin?

A: Run `just update-plugin design-to-code` to fetch the latest version.

### Q: Can I use multiple design tools together?

A: Yes, you can configure multiple MCP servers in `.mcp.json` and switch between them.

### Q: What design token format is recommended?

A: Use W3C Design Tokens format (JSON) for maximum compatibility. Convert to platform-specific formats as needed.

### Q: How do I contribute a fix?

A: See [CONTRIBUTING](../../CONTRIBUTING.md) for contribution guidelines.

## Debug Mode

Enable debug output for troubleshooting:

```bash
# Set debug environment variable
export CLAUDE_DEBUG=1

# Run command with verbose output
/extract-tokens --verbose
```

### Viewing Logs

```bash
# Check Claude Code logs
tail -f ~/.claude/logs/claude.log

# Check MCP server logs
tail -f ~/.claude/logs/mcp-figma.log
tail -f ~/.claude/logs/mcp-sketch-context.log
```

## Getting Help

If you can't resolve your issue:

1. **Search existing issues**: [GitHub Issues](https://github.com/aRustyDev/agents/issues?q=is%3Aissue+label%3Abug)
2. **Ask in Discussions**: [GitHub Discussions Q&A](https://github.com/aRustyDev/agents/discussions/categories/q-a)
3. **Report a bug**: [Bug Report](https://github.com/aRustyDev/agents/issues/new?template=bug-report.yml)

When reporting, include:

- Plugin version (from `plugin.json`)
- Design tool and version (Figma/Sketch/Penpot)
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Claude Code version)

## Share Your Success

Had a great experience with this plugin? We'd love to hear about it!

- **Share a success story**: [Show and Tell](https://github.com/aRustyDev/agents/discussions/categories/show-and-tell)
- **Suggest improvements**: [Ideas](https://github.com/aRustyDev/agents/discussions/categories/ideas)

Use the `/feedback` command or the `feedback-submission` output style to format your feedback.
