# End-to-End Tests for BasicMcpServer

This directory contains end-to-end tests for the BasicMcpServer implementation.

## Overview

The tests in this directory verify that the MCP server works correctly by:
1. Testing the MCP protocol connections
2. Testing tool discovery and execution
3. Verifying responses from the example tool

## Working Test Scripts

### 1. Direct Test

The primary recommended test script that uses the SDK directly:

```bash
python tests/e2e/direct_test.py
```

This test:
- Connects to a running MCP server
- Lists available tools, resources, and prompts
- Calls the example tool and validates its response

Options:
- `--host` - Server hostname (default: localhost)
- `--port` - Server port (default: 7501)
- `--input` - Input text for example tool test

### 2. Running Server Test

A simplified test script that uses the same reliable pattern:

```bash
python tests/e2e/running_server_test.py
```

This is optimized for testing against a server that's already running.

## Implementation Details

### Key Pattern for Success

The reliable pattern for testing MCP servers is using nested context managers directly with the SDK:

```python
async with sse_client(sse_url) as streams:
    async with ClientSession(streams[0], streams[1]) as session:
        await session.initialize()
        # Test operations here
```

This ensures proper context management and cleanup of async resources.

## Best Practices

1. **Direct SDK Usage**: Use the SDK's classes directly rather than building abstractions

2. **Context Managers**: Always use proper context managers for reliable connection cleanup

3. **Testing Flow**: For reliable testing:
   - Start the server (manually or in a separate process)
   - Run the tests against the running server
   - This separation avoids issues with async operations and container management

## Dependencies

Required dependencies are listed in `requirements.txt` and include:
- The MCP SDK
- Requests (for HTTP connectivity tests)
- Other supporting packages
