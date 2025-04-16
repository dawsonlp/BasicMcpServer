#!/usr/bin/env python3
"""
Direct MCP test using the exact same pattern as client_using_session.py,
which is known to work correctly.

This script provides a simple test for the MCP server without any abstraction layers.
"""

import asyncio
import sys
import logging
from typing import Any
from urllib.parse import urlparse

# Import the SDK client classes directly
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Constants
SERVER_URL = "http://localhost:7501/sse"
INPUT_TEXT = "Direct test of MCP server"


def print_items(name: str, result: Any) -> None:
    """Print items with formatting."""
    logger.info(f"Available {name}:")
    items = getattr(result, name, [])
    if items:
        for item in items:
            logger.info(f" * {item}")
    else:
        logger.info("No items available")


async def test_mcp_server():
    """
    Test the MCP server using the ClientSession approach.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Testing MCP server at {SERVER_URL}")
    
    if urlparse(SERVER_URL).scheme not in ("http", "https"):
        logger.error("Error: Server URL must start with http:// or https://")
        return False
    
    try:
        # Use the sse_client to establish the SSE connection
        # This is the exact same pattern that works in client_using_session.py
        async with sse_client(SERVER_URL) as streams:
            # Use ClientSession to wrap the streams and simplify interactions
            async with ClientSession(streams[0], streams[1]) as session:
                # Initialize the session
                await session.initialize()
                logger.info(f"Connected to MCP server at {SERVER_URL}")
                
                # List available tools, resources, and prompts
                tools_result = await session.list_tools()
                print_items("tools", tools_result)
                
                resources_result = await session.list_resources()
                print_items("resources", resources_result)
                
                prompts_result = await session.list_prompts()
                print_items("prompts", prompts_result)
                
                # Call the example tool
                logger.info(f"Calling example tool with input: {INPUT_TEXT}")
                tool_result = await session.call_tool("example", {"input": INPUT_TEXT})
                
                # Process the tool result
                logger.info(f"Tool result: {tool_result}")
                
                # Extract the content from the result
                if hasattr(tool_result, "content") and tool_result.content:
                    content = tool_result.content
                    if isinstance(content, list) and len(content) > 0:
                        if hasattr(content[0], "text"):
                            text = content[0].text
                        else:
                            text = str(content[0])
                            
                        logger.info(f"Result text: {text}")
                        
                        if "Processed:" in text:
                            logger.info("Test successful: received expected response format")
                            return True
                
                logger.error("Test failed: Unexpected result format")
                return False
                
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Direct test for MCP server")
    parser.add_argument("--host", default="localhost", help="Server hostname")
    parser.add_argument("--port", type=int, default=7501, help="Server port")
    parser.add_argument("--input", default=INPUT_TEXT, help="Input text for example tool")
    args = parser.parse_args()
    
    # Update constants based on command-line arguments
    SERVER_URL = f"http://{args.host}:{args.port}/sse"
    INPUT_TEXT = args.input
    
    # Run the test
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
