# Troubleshooting

Common issues and solutions for this plugin.

## Common Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| Command not found | Plugin not installed | Run `just install-plugin go-projects` |
| MCP server timeout | Server not running | Run `just enable-mcp go-projects` |
| Permission denied | Missing file permissions | Check file ownership and permissions |

## Detailed Solutions

### Issue: Plugin Installation Fails

**Symptoms:**
- Error during `just install-plugin`
- Missing dependencies

**Solution:**
1. Ensure Homebrew is installed: `brew --version`
2. Install plugin dependencies: `cd context/plugins/go-projects && brew bundle`
3. Retry installation: `just install-plugin go-projects`

### Issue: MCP Server Connection Failed

**Symptoms:**
- "Cannot connect to MCP server" error
- Timeout when using MCP-dependent features

**Solution:**
1. Check if server is running: `ps aux | grep <server-name>`
2. Restart the server: `just restart-mcp go-projects`
3. Check server logs for errors
4. Verify `.mcp.json` configuration

### Issue: Command Returns Unexpected Results

**Symptoms:**
- Output doesn't match expectations
- Missing data in response

**Solution:**
1. Check command arguments: `/<command> --help`
2. Verify input format matches expected schema
3. Check for recent changes in [CHANGELOG](../CHANGELOG.md)

## FAQ

### Q: How do I update the plugin?

A: Run `just update-plugin go-projects` to fetch the latest version.

### Q: Can I use this plugin with other plugins?

A: Yes, this plugin is designed to work alongside other plugins. Check the [Usage](./USAGE.md) guide for integration details.

### Q: How do I contribute a fix?

A: See [CONTRIBUTING](../CONTRIBUTING.md) for contribution guidelines.

## Debug Mode

Enable debug output for troubleshooting:

```bash
# Set debug environment variable
export CLAUDE_DEBUG=1

# Run command with verbose output
/<command> --verbose
```

### Viewing Logs

```bash
# Check Claude Code logs
tail -f ~/.claude/logs/claude.log

# Check MCP server logs
tail -f ~/.claude/logs/mcp-<server-name>.log
```

## Getting Help

If you can't resolve your issue:

1. **Search existing issues**: [GitHub Issues](https://github.com/aRustyDev/ai/issues?q=is%3Aissue+label%3Abug)
2. **Ask in Discussions**: [GitHub Discussions Q&A](https://github.com/aRustyDev/ai/discussions/categories/q-a)
3. **Report a bug**: [Bug Report](https://github.com/aRustyDev/ai/issues/new?template=bug-report.yml)

When reporting, include:
- Plugin version (from `plugin.json`)
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Claude Code version)

## Share Your Success

Had a great experience with this plugin? We'd love to hear about it!

- **Share a success story**: [Show and Tell](https://github.com/aRustyDev/ai/discussions/categories/show-and-tell)
- **Suggest improvements**: [Ideas](https://github.com/aRustyDev/ai/discussions/categories/ideas)

Use the `/feedback` command or the `feedback-submission` output style to format your feedback.
