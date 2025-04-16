# Creating MCP Servers: A Comprehensive Guide

This guide provides detailed instructions on how to implement a Model Context Protocol (MCP) server that can integrate with external APIs and services. The examples focus on creating a Jira MCP server, but the patterns can be applied to any API or service integration.

## Key References

This guide builds upon these important resources:

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/introduction) - The official MCP documentation which provides the foundation for understanding the protocol
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - The official SDK used in this implementation
- [MCP HTTP Client Example](https://github.com/slavashvets/mcp-http-client-example) - A reference implementation that informed the testing approach

## Table of Contents

1. [Introduction to MCP Servers](#introduction-to-mcp-servers)
2. [Project Setup](#project-setup)
3. [Implementing an MCP Server](#implementing-an-mcp-server)
   - [Core Components](#core-components)
   - [Configuration Management](#configuration-management)
   - [Service Implementations](#service-implementations)
   - [Tools and Resources](#tools-and-resources)
4. [Docker Containerization](#docker-containerization)
5. [Testing](#testing)
6. [Deployment](#deployment)
7. [Best Practices](#best-practices)
8. [Setup Script Reference](#setup-script-reference)

## Introduction to MCP Servers

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is a standard for communication between AI assistants and external services. An MCP server exposes capabilities as "tools" and "resources" that can be discovered and used by AI assistants, allowing them to perform actions and access data that would otherwise be unavailable to them.

Key concepts:
- **Tools**: Functions that perform actions or return data
- **Resources**: Data sources that provide information
- **Server**: The system that hosts tools and resources
- **Client**: The AI assistant or system that uses the server

## Project Setup

Setting up an MCP server project involves creating a specific directory structure and configuring the necessary files.

### Directory Structure

```
mcp-server/
├── src/
│   ├── __init__.py
│   ├── main.py           # Entry point
│   ├── config.py         # Configuration management
│   ├── server.py         # MCP server definition
│   ├── services/         # Service integrations
│   │   ├── __init__.py
│   │   └── service.py    # Service implementation
│   └── tools/            # Optional tool implementations
│       └── __init__.py
├── docker/
│   ├── Dockerfile
│   └── scripts/
│       ├── entrypoint.sh
│       └── run.sh
├── tests/
│   └── e2e/              # End-to-end tests
│       ├── direct_test.py
│       └── README.md
├── pyproject.toml        # Package definition
├── README.md
└── .env.example          # Example environment variables
```

### Dependencies

The key dependencies for an MCP server are:

1. **MCP Framework**: The MCP Python library (`mcp>=1.6.0`)
2. **Web Framework**: Typically Starlette (`starlette>=0.46.2`)
3. **ASGI Server**: Such as Uvicorn (`uvicorn>=0.34.1`)
4. **SSE Support**: For Server-Sent Events (`sse-starlette>=2.2.1`)
5. **Settings Management**: For configuration (`pydantic-settings>=2.8.1`)
6. **HTTP Client**: For API calls (`httpx>=0.28.1`)
7. **Service-Specific Libraries**: Like `jira>=3.5.0` for Jira integration

These dependencies are specified in `pyproject.toml`:

```toml
[project]
dependencies = [
    "mcp>=1.6.0",
    "starlette>=0.46.2",
    "uvicorn>=0.34.1",
    "sse-starlette>=2.2.1",
    "pydantic-settings>=2.8.1",
    "httpx>=0.28.1",
    # Service-specific dependencies
    "jira>=3.5.0",
]
```

## Implementing an MCP Server

### Core Components

An MCP server implementation consists of several key components:

1. **Main Entry Point (`main.py`)**: Sets up and runs the server
2. **Configuration (`config.py`)**: Manages settings and environment variables
3. **Server Definition (`server.py`)**: Defines the MCP server, tools, and resources
4. **Service Integration**: Implements the integration with external services

### Configuration Management

Configuration is typically managed using environment variables, loaded with `pydantic-settings`:

```python
# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Server settings
    host: str = "0.0.0.0"
    port: int = 7501
    
    # Service credentials
    service_url: str
    service_username: str
    service_api_token: str
    
    # Load from .env file
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=False
    )

settings = Settings()
```

### Service Implementations

Service classes encapsulate the integration with external APIs:

```python
# services/service.py
class ApiService:
    def __init__(self):
        self._client = None
        
    def _get_client(self):
        if not self._client:
            # Initialize client with credentials from settings
            pass
        return self._client
    
    def method_a(self, param):
        # Implement API method
        pass
        
    def method_b(self, param):
        # Implement another API method
        pass
```

### Tools and Resources

Tools and resources are defined in the server module using decorators:

```python
# server.py
from mcp.server.fastmcp import FastMCP
from .services.service import ApiService

def create_mcp_server():
    mcp = FastMCP("my-mcp-server")
    
    # Create service instance
    api_service = ApiService()
    
    # Define tool
    @mcp.tool()
    def example_tool(param: str) -> dict:
        """Tool description that appears in documentation"""
        return api_service.method_a(param)
    
    # Define resource
    @mcp.resource("resource://api/item/{item_id}")
    def item_resource(item_id: str) -> dict:
        """Resource description"""
        return api_service.method_b(item_id)
    
    return mcp
```

## Docker Containerization

MCP servers are typically deployed as Docker containers for consistency and isolation.

### Dockerfile

A multi-stage Dockerfile optimizes the build process:

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY pyproject.toml README.md ./
COPY ./src ./src

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev \
    && pip install --upgrade pip \
    && pip install build wheel \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip wheel --no-deps --wheel-dir /wheels -e .

# Stage 2: Runtime
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY ./src ./src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

# Security: Run as non-root user
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 7501

CMD ["python", "-m", "src.main"]
```

### Runtime Configuration

Environment variables are passed to the container at runtime:

```bash
docker run -p 7501:7501 \
  --env-file .env \
  --name my-mcp-server \
  my-mcp-server
```

## Testing

Testing MCP servers focuses on two key areas:

1. **Tool and Resource Testing**: Verifying that tools and resources work correctly
2. **Protocol Testing**: Ensuring that the MCP protocol is implemented correctly

### Direct Testing Approach

The recommended testing pattern uses the MCP SDK directly:

```python
async def test_mcp_server():
    async with sse_client(SERVER_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            
            # Test listing tools
            tools_result = await session.list_tools()
            
            # Test calling a tool
            tool_result = await session.call_tool("example_tool", {"param": "value"})
            
            # Validate the result
            # ...
```

## Deployment

MCP servers can be deployed in various environments:

1. **Local Development**: Running directly with Python
2. **Docker Containers**: Using Docker or Docker Compose
3. **Kubernetes**: For scaling and high availability
4. **Cloud Services**: AWS, GCP, Azure, etc.

The recommended approach is to use Docker containers for consistency across environments.

## Best Practices

When implementing MCP servers, follow these best practices:

1. **Separate Concerns**:
   - Keep service logic separate from MCP implementation
   - Use classes to encapsulate external API interactions

2. **Handle Errors Gracefully**:
   - Catch and log service-specific exceptions
   - Return clear error messages to clients

3. **Document Everything**:
   - Provide clear docstrings for all tools and resources
   - Include parameter descriptions and return types

4. **Use Proper Types**:
   - Leverage Python type annotations
   - Define clear input/output schemas

5. **Implement Health Checks**:
   - Add health check endpoints
   - Monitor server status

6. **Security Considerations**:
   - Never hardcode credentials
   - Use environment variables for sensitive information
   - Run as non-root user in Docker

7. **Testing Approach**:
   - Test tools and resources directly
   - Use the recommended MCP SDK patterns for integration tests

## Setup Script Reference

For convenience, this repository includes a setup script (`setup_jira_mcp_server.sh`) that creates a complete Jira MCP server project structure. This can be used as a template for creating other MCP servers.

To use the script:

1. Make it executable: `chmod +x setup_jira_mcp_server.sh`
2. Run it: `./setup_jira_mcp_server.sh`
3. Navigate to the created directory: `cd jira-mcp-server`
4. Configure your `.env` file: `cp .env.example .env`
5. Edit the `.env` file with your credentials
6. Build and run the Docker container: `./docker/scripts/run.sh`

This script can be customized to create MCP servers for other service integrations by modifying the service class and tool/resource definitions.

## Conclusion

Building MCP servers allows you to extend the capabilities of AI assistants by integrating with external services and APIs. By following the patterns and practices in this guide, you can create robust, secure, and maintainable MCP servers that provide valuable tools and resources to AI assistants.

The example Jira MCP server demonstrates these principles by providing a complete implementation that can be used as a reference for other service integrations.
