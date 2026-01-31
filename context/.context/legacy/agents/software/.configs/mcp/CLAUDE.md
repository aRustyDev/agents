# Claude Development Guidelines for MCP Projects

This document contains critical guidelines and requirements for Claude when working on MCP (Model Context Protocol) server projects.

## Development Workflow

### MCP-Specific Considerations

**Protocol compliance** - Validate all MCP messages against schema
**Tool isolation** - Each tool should be independent and testable
**Resource management** - Properly handle client connections and cleanup
**Error responses** - Return proper MCP error codes and messages
**Streaming support** - Implement SSE for long-running operations
**Security** - Validate all inputs and implement proper auth when needed
