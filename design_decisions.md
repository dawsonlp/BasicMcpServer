# Design Decisions

This document logs important design decisions made during the development of BasicMcpServer.

## 2025-04-15: Separation of Docker Containerization from Application Functionality

### Decision

We've restructured the project to separate Docker containerization concerns from application functionality by:
1. Creating a dedicated `docker/` directory for all Docker-related files
2. Replacing Docker Compose with a single Dockerfile and helper scripts
3. Upgrading to Python 3.13 from Python 3.11
4. Implementing multi-stage builds for better optimization

### Context

The previous setup had containerization concerns tightly coupled with application code, using Docker Compose for a single container, and running on Python 3.11 instead of 3.13.

### Reasoning

This separation offers several benefits:
1. **Clear Separation of Concerns**: Containerization details are isolated from application code
2. **Simplified Workflow**: A single container doesn't require Docker Compose's complexity
3. **Version Upgrades**: Moving to Python 3.13 keeps us current with the latest language features
4. **Optimized Builds**: Multi-stage builds reduce image size and improve security
5. **Improved Maintainability**: Changes to containerization can be made independently of application code

### Implementation Notes

The implementation involved:
1. Creating a new `docker/` directory with an optimized Dockerfile
2. Adding helper scripts to replace Docker Compose functionality
3. Upgrading Python version to 3.13
4. Implementing security best practices like non-root user and health checks
5. Providing comprehensive documentation in `docker/README.md`

### Tradeoffs

- **Pros**: Better separation of concerns, simplified workflow, optimized container, better security
- **Cons**: Slightly more complex directory structure, need to maintain helper scripts

The tradeoffs heavily favor the new approach as it provides better maintainability, security, and follows the principle of separation of concerns.

### References

- [Docker Best Practices Documentation](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Python 3.13 Release Notes](https://www.python.org/downloads/)

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
