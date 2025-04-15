# Design Decisions

This document logs important design decisions made during the development of BasicMcpServer.

## 2025-04-15: Migration from Low-Level Server to FastMCP

### Decision

We have decided to migrate the BasicMcpServer from using the low-level `mcp.server.lowlevel.Server` class to the more ergonomic `mcp.server.fastmcp.FastMCP` class.

### Context

The MCP Python SDK provides two main approaches for implementing MCP servers:

1. **Low-Level Server API**: Direct access to the MCP protocol with more manual implementation
2. **FastMCP API**: Higher-level, more ergonomic API with simplified abstractions

Our initial implementation used the low-level Server API, which required more boilerplate code and manual handling of various MCP protocol aspects.

### Reasoning

The migration to FastMCP offers several significant benefits:

1. **Reduced Boilerplate**: FastMCP dramatically reduces the amount of code needed to implement the same functionality
2. **Type Safety**: Automatic type validation and conversion using Python type hints
3. **Automatic Schema Generation**: Input schemas are generated automatically from function signatures
4. **Simplified Error Handling**: Errors from tools are properly formatted and returned to clients
5. **Better Developer Experience**: More intuitive API that's easier to understand and maintain
6. **Access to Advanced Features**: Easier access to MCP capabilities like logging and progress reporting

The previous implementation required:
- Manual definition of tool schemas
- Explicit validation of input arguments
- Manually formatting responses
- Significant boilerplate for server setup

With FastMCP, these aspects are handled automatically, resulting in more maintainable code.

### Implementation Notes

The migration involved:

1. Replacing the low-level Server instantiation with FastMCP
2. Converting tool implementations to use FastMCP's decorator pattern
3. Updating the server execution logic to use FastMCP's built-in functionality
4. Adding support for future extensions like resources and prompts

### Tradeoffs

- **Pros**: Less code, better maintainability, easier access to advanced features
- **Cons**: Slightly higher level of abstraction (less direct control of the protocol)

The tradeoffs heavily favor FastMCP for our use case. The minimal loss of direct control is far outweighed by the significant reduction in code complexity and improved developer experience.

### References

- [FastMCP vs Low-Level Server Implementation](readme_fastmcp.md)
- [MCP Python SDK Documentation](https://modelcontextprotocol.io)
