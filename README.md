# BasicMcpServer

A minimal, production-ready MCP (Model Context Protocol) server implementation exposed via HTTP+SSE in a Docker container.

## Overview

This project implements the simplest possible [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that can be deployed in a Docker container and exposed via HTTP with Server-Sent Events (SSE). It follows best practices for environment variable management to ensure credentials are never committed to version control.

The server is designed to be:
- **Simple**: Minimal boilerplate and dependencies
- **Secure**: Proper credential management out of the box
- **Containerized**: Ready for Docker deployment
- **Performant**: Using Starlette and Uvicorn for high-performance HTTP serving

## Architecture

### Python Packages

The project uses the following key packages:

1. **MCP SDK**: The Python implementation of the Model Context Protocol
   - `mcp`: Core MCP functionality

2. **Web Framework**: Starlette
   - Lightweight ASGI framework
   - Already used in the MCP SDK's SSE implementation
   - Excellent performance characteristics

3. **ASGI Server**: Uvicorn
   - High-performance ASGI server
   - Works seamlessly with Starlette
   - Well-suited for containerized environments

4. **SSE Implementation**: sse-starlette
   - Already integrated with the MCP SDK
   - Provides Server-Sent Events functionality

5. **Configuration Management**: pydantic-settings
   - Type-safe environment variable handling
   - Validation at startup

6. **HTTP Client** (if needed): httpx
   - Async-compatible HTTP client for outbound requests

### Dependencies

These will be specified in `pyproject.toml`:

```toml
[project]
name = "basic-mcp-server"
version = "0.1.0"
description = "A minimal MCP server with HTTP+SSE in a Docker container"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.6.0",
    "starlette>=0.46.2",
    "uvicorn>=0.34.1",
    "sse-starlette>=2.2.1",
    "pydantic-settings>=2.8.1",
    "httpx>=0.28.1",
]
```

## Credential Management & Security

To ensure credentials are never committed to version control:

### Local Development

1. Create a `.env` file locally with your credentials:
   ```
   API_KEY=your_api_key_here
   OTHER_SECRET=other_secret_here
   ```

2. This file is automatically excluded from Git via the `.gitignore` file.

3. Use the included `.env.example` as a template for required variables.

### Docker Deployment

1. **Never** mount your `.env` file directly into the container.

2. Pass environment variables at runtime:
   ```bash
   docker run -e API_KEY=your_api_key_here -e OTHER_SECRET=other_secret_here basic-mcp-server
   ```

3. Or use Docker Compose with environment variables:
   ```yaml
   services:
     mcp-server:
       build: .
       environment:
         - API_KEY=${API_KEY}
         - OTHER_SECRET=${OTHER_SECRET}
   ```

4. For production, consider using Docker Swarm secrets or Kubernetes secrets.

## Project Structure

```
basic-mcp-server/
├── .gitignore            # Includes .env* patterns
├── .dockerignore         # Also excludes .env files
├── .env.example          # Template with dummy values
├── Dockerfile            # Container definition
├── docker-compose.yml    # For local development
├── pyproject.toml        # Dependencies and metadata
├── README.md             # This file
└── src/
    ├── __init__.py
    ├── main.py           # Entry point
    ├── config.py         # Environment & configuration management
    ├── server.py         # MCP server implementation
    └── tools/            # Tool implementations
        ├── __init__.py
        └── example.py    # Example tool
```

## Implementation Details

### Configuration (`src/config.py`)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Server settings
    host: str = "0.0.0.0"
    port: int = 7500
    
    # Add your API keys and credentials here
    api_key: str
    
    # Optional: Add database credentials, etc.
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
```

### Server Implementation (`src/server.py`)

```python
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
import mcp.types as types

def create_mcp_server():
    # Create an MCP server instance
    server = Server("basic-mcp-server")
    
    # Add your tools here
    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="example",
                description="An example tool",
                inputSchema={
                    "type": "object",
                    "required": ["input"],
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Input string",
                        }
                    },
                },
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        if name != "example":
            raise ValueError(f"Unknown tool: {name}")
        
        input_value = arguments.get("input", "")
        return [types.TextContent(type="text", text=f"Processed: {input_value}")]
    
    return server
```

### Main Entry Point (`src/main.py`)

```python
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount, Route

from mcp.server.sse import SseServerTransport
from .config import settings
from .server import create_mcp_server

# Create the MCP server
mcp_server = create_mcp_server()

# Create SSE transport
sse = SseServerTransport("/messages/")

# SSE handler for clients to connect
async def handle_sse(request):
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_server.run(
            streams[0], streams[1], mcp_server.create_initialization_options()
        )

# Create Starlette app
app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)

if __name__ == "__main__":
    print(f"Starting MCP server on {settings.host}:{settings.port}")
    uvicorn.run(app, host=settings.host, port=settings.port)
```

## Docker Implementation

### Dockerfile

```dockerfile
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Install dependencies
RUN pip install uv
COPY pyproject.toml .
RUN uv pip install -e .

# Copy application code
COPY ./src ./src

# Run with a non-root user
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Expose the port
EXPOSE 7500

# Run the application
CMD ["python", "-m", "src.main"]
```

### Docker Compose

```yaml
services:
  mcp-server:
    build: .
    ports:
      - "7500:7500"
    environment:
      - API_KEY=${API_KEY}
    volumes:
      - ./src:/app/src
```

## Getting Started

### Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and update with your credentials
3. Install dependencies:
   ```bash
   pip install uv
   uv pip install -e .
   ```

### Run Locally

```bash
python -m src.main
```

### Build and Run with Docker

```bash
docker build -t basic-mcp-server .
docker run -p 7500:7500 -e API_KEY=your_api_key basic-mcp-server
```

Or with Docker Compose:

```bash
docker compose up
```

## Testing Your MCP Server

### Manual Testing

#### Using the MCP SDK CLI

If you have the MCP SDK CLI installed, you can use it to test your server:

```bash
mcp dev http://localhost:7500/sse
```

#### Using Claude

To test with Claude:

1. Update Claude's MCP settings file with:
   ```json
   {
     "mcpServers": {
       "basic-mcp-server": {
         "url": "http://localhost:7500/sse",
         "disabled": false,
         "autoApprove": ["example"]
       }
     }
   }
   ```

2. In Claude, use the tool:
   ```
   <use_mcp_tool>
   <server_name>basic-mcp-server</server_name>
   <tool_name>example</tool_name>
   <arguments>
   {
     "input": "Hello MCP World!"
   }
   </arguments>
   </use_mcp_tool>
   ```

3. You should receive: "Processed: Hello MCP World!"

#### Using HTTP Requests

You can also test your server with HTTP requests:

1. Connect to the SSE endpoint:
   ```bash
   curl -N http://localhost:7500/sse
   ```

2. In another terminal, send a message to the server:
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"type":"initialize","requestId":"test-123","content":{"clientInfo":{"clientType":"test","clientVersion":"1.0.0"},"capabilities":{"receiveText":true,"receiveImage":false}}}' http://localhost:7500/messages/?session_id=test-session-id
   ```

### Automated End-to-End Testing

We provide automated tests that verify the MCP server works correctly when deployed as a container:

1. Install test dependencies:
   ```bash
   cd tests/e2e
   pip install -r requirements.txt
   ```

2. Run the test:
   ```bash
   python mcp_container_test.py
   ```

The test script will:
- Build and start a Docker container with the MCP server
- Test HTTP connectivity to the server
- Test the MCP protocol (initialization, tool listing)
- Test the example tool functionality
- Clean up all resources when done

See `tests/e2e/README.md` for more details on the end-to-end tests.

### Troubleshooting

If you encounter issues:

1. **Connection refused:**
   - Ensure the container is running: `docker ps | grep mcp-server`
   - Verify port mapping: `docker port [container-id]`

2. **"Not connected" error in Claude:**
   - Ensure the URL includes the `/sse` path: `http://localhost:7500/sse`
   - Check container logs: `docker logs [container-id]`
   - Try restarting the VSCode window

3. **Timeout or no response:**
   - Examine server logs for errors
   - Check if another service is using port 7500

## Reference Implementation

This project is based on the Model Context Protocol (MCP) Python SDK. For more details on the MCP specification and SDK, refer to the [original project README](https://github.com/modelcontextprotocol/python-sdk/blob/main/README.md).

## Next Steps

1. Add more tools to make your MCP server useful
2. Implement authentication for the HTTP endpoints
3. Add monitoring and logging
4. Deploy to your preferred cloud provider

---

This implementation provides a minimal but production-ready MCP server. You can extend it by adding more tools, resources, or custom functionality as needed.
