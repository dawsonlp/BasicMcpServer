#!/usr/bin/env python
"""
Simple test for running MCP servers.

This is a direct implementation based on direct_test.py and follows
the same pattern that is known to work without freezing.
"""

import asyncio
import sys
import logging
from typing import Any, Dict, List
from urllib.parse import urlparse

# Import the SDK client classes directly
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Constants
SERVER_URL = "http://localhost:7501/sse"
INPUT_TEXT = "Simple MCP server test"


def print_results(name: str, items: List[Any]) -> None:
    """Print items with formatting."""
    logger.info(f"\n--- {name.title()} ---")
    if items:
        for item in items:
            logger.info(f" * {item}")
    else:
        logger.info("None available")


async def test_mcp_server(sse_url: str, test_input: str) -> bool:
    """
    Test an MCP server directly using the ClientSession.
    
    This implementation uses the same pattern as direct_test.py which is
    known to work reliably without freezing.
    
    Args:
        sse_url: The SSE URL of the MCP server
        test_input: Text to use for testing the example tool
        
    Returns:
        bool: True if all tests passed
    """
    logger.info(f"Testing MCP server at {sse_url}")
    
    if urlparse(sse_url).scheme not in ("http", "https"):
        logger.error("Error: Server URL must start with http:// or https://")
        return False
    
    try:
        # Use the sse_client to establish the SSE connection within a context manager
        # This is exactly the same pattern that works in direct_test.py
        async with sse_client(sse_url) as streams:
            # Use ClientSession within a context manager
            async with ClientSession(streams[0], streams[1]) as session:
                # Initialize the session
                await session.initialize()
                logger.info(f"Connected to MCP server")
                
                # Test 1: List tools
                logger.info("Listing tools...")
                tools_result = await session.list_tools()
                if hasattr(tools_result, "tools"):
                    print_results("tools", tools_result.tools)
                    # Verify example tool exists
                    example_tool = next((t for t in tools_result.tools if t.name == "example"), None)
                    if not example_tool:
                        logger.error("Example tool not found")
                        return False
                else:
                    logger.error("Failed to get tools")
                    return False
                
                # Test 2: List resources
                logger.info("Listing resources...")
                resources_result = await session.list_resources()
                if hasattr(resources_result, "resources"):
                    print_results("resources", resources_result.resources)
                
                # Test 3: List prompts
                logger.info("Listing prompts...")
                prompts_result = await session.list_prompts()
                if hasattr(prompts_result, "prompts"):
                    print_results("prompts", prompts_result.prompts)
                
                # Test 4: Call the example tool
                logger.info(f"Calling example tool with input: {test_input}")
                tool_result = await session.call_tool("example", {"input": test_input})
                
                # Check the tool response
                if hasattr(tool_result, "content") and tool_result.content:
                    content = tool_result.content
                    if isinstance(content, list) and len(content) > 0:
                        if hasattr(content[0], "text"):
                            text = content[0].text
                        else:
                            text = str(content[0])
                            
                        logger.info(f"Result text: {text}")
                        
                        if f"Processed: {test_input}" in text:
                            logger.info("Example tool test PASSED")
                            return True
                
                logger.error("Example tool test FAILED")
                return False
                
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test MCP server")
    parser.add_argument("--host", default="localhost", help="Server hostname")
    parser.add_argument("--port", type=int, default=7501, help="Server port")
    parser.add_argument("--input", default=INPUT_TEXT, help="Input text for example tool")
    args = parser.parse_args()
    
    # Construct the server URL from arguments
    sse_url = f"http://{args.host}:{args.port}/sse"
    
    # Run the test
    logger.info("Starting MCP server test...")
    success = asyncio.run(test_mcp_server(sse_url, args.input))
    logger.info(f"\nOverall result: {'✅ PASS' if success else '❌ FAIL'}")
    sys.exit(0 if success else 1)
