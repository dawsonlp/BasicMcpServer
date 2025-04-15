# MCP Server End-to-End Tests

This directory contains end-to-end tests for the MCP server deployed in a Docker container.

## Overview

The tests verify that:

1. The MCP server can be built and deployed as a Docker container
2. The server responds correctly to HTTP requests
3. The MCP protocol works as expected
4. The example tool functions correctly

## Requirements

- Python 3.10+
- Docker
- pip packages listed in `requirements.txt`

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Tests

From this directory, run:

```bash
python mcp_container_test.py
```

The test script will:

1. Build a Docker image from the project
2. Start a container from that image
3. Test HTTP connectivity to the server
4. Test the MCP protocol by connecting and listing tools
5. Test the example tool functionality
6. Clean up resources (stop and remove container)

## Test Output

The test will output logs showing the progress and results of each test stage:

```
2025-04-15 10:45:00 - root - INFO - Building Docker image...
2025-04-15 10:45:30 - root - INFO - Built image: sha256:1234...
2025-04-15 10:45:30 - root - INFO - Starting container...
2025-04-15 10:45:35 - root - INFO - Started container: abcd1234...
...
2025-04-15 10:46:00 - root - INFO - Test Results:
2025-04-15 10:46:00 - root - INFO -   build       : ✅ PASS
2025-04-15 10:46:00 - root - INFO -   start       : ✅ PASS
2025-04-15 10:46:00 - root - INFO -   connectivity: ✅ PASS
2025-04-15 10:46:00 - root - INFO -   protocol    : ✅ PASS
2025-04-15 10:46:00 - root - INFO -   tool        : ✅ PASS
2025-04-15 10:46:00 - root - INFO - Overall Result: ✅ PASS
```

The exit code will be 0 for success and 1 for failure.

## Components

- `mcp_container_test.py`: Main test script
- `mcp_client.py`: MCP client implementation for testing
- `requirements.txt`: Dependencies for the tests

## Adding New Tests

To add new tests for additional tools:

1. Add a new test method in `McpServerTest` class
2. Add the test result to the `test_results` dictionary
3. Call the test method from `run_async_tests()` method

## Troubleshooting

If tests fail, check:

1. Docker is running and has sufficient resources
2. Port 7500 is available and not used by another service
3. The project can be built successfully
4. The MCP server starts correctly in the container (check logs)
