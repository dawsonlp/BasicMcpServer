# Port Usage Tracking

This document keeps track of port usage in the BasicMcpServer project to avoid conflicts and ensure consistent port assignment as the project grows.

## Currently Assigned Ports

| Port | Service | Description |
|------|---------|-------------|
| 7500 | MCP HTTP+SSE Server (low-level implementation) | Previous MCP server with HTTP and SSE endpoints |
| 7501 | MCP HTTP+SSE Server (FastMCP implementation) | Current MCP server with HTTP and SSE endpoints |

## Port Range Allocation

The project uses ports in the range 7500-7600 to avoid conflicts with other common services.

## Guidelines for Adding New Services

When adding new services to this project that require port assignments:

1. Check this document first to avoid port conflicts
2. Use the next available port in the 7500-7600 range
3. Update this document with the new port assignment
4. Update any relevant configuration files (docker-compose.yml, .env.example, etc.)

## Reserved Ports

Some ports may be reserved for future use:

- 7510: Reserved for metrics/monitoring (future)
- 7520: Reserved for admin interface (future)
