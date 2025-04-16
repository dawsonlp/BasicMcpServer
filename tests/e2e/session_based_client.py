#!/usr/bin/env python3
"""
Session-based MCP client using the SDK ClientSession approach.

This provides a consistent interface for use in container and direct tests.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, List, Optional

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

logger = logging.getLogger(__name__)

class SessionBasedClient:
    """MCP client implementation using the SDK's ClientSession."""
    
    def __init__(self, sse_url: str, api_url: str = None):
        """
        Initialize the client.
        
        Args:
            sse_url: URL of the SSE endpoint
            api_url: URL for API requests (not used with ClientSession)
        """
        self.sse_url = sse_url
        self.streams = None
        self.session = None
        
    async def __aenter__(self):
        """Enter context manager."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if self.session:
            # Close the session using __aexit__ since it doesn't have aclose()
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        
        # Also close the streams if they exist
        if self.streams:
            await self.streams[0].__aexit__(exc_type, exc_val, exc_tb)
        
    async def connect(self) -> bool:
        """
        Connect to the MCP server.
        
        Returns:
            bool: True if connection succeeded
        """
        try:
            self.streams = await sse_client(self.sse_url).__aenter__()
            self.session = ClientSession(self.streams[0], self.streams[1])
            await self.session.initialize()
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {str(e)}")
            return False
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools.
        
        Returns:
            List of tool definitions
        """
        if not self.session:
            logger.error("Session not initialized")
            return []
            
        result = await self.session.list_tools()
        if hasattr(result, "tools"):
            # Convert from SDK objects to plain dictionaries
            tools = []
            for tool in result.tools:
                tool_dict = {
                    "name": tool.name
                }
                if hasattr(tool, "description"):
                    tool_dict["description"] = tool.description
                if hasattr(tool, "input_schema"):
                    tool_dict["inputSchema"] = tool.input_schema
                tools.append(tool_dict)
            return tools
        return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Call a tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        if not self.session:
            logger.error("Session not initialized")
            return None
            
        try:
            result = await self.session.call_tool(tool_name, arguments)
            # Convert to dict format for compatibility
            return {
                "result": {
                    "content": result.content if hasattr(result, "content") else [],
                    "isError": False
                }
            }
        except Exception as e:
            logger.error(f"Error calling tool: {str(e)}")
            return None
    
    async def test_tool(self, tool_name: str, arguments: Dict[str, Any], expected_prefix: str = None) -> bool:
        """
        Test a tool by calling it and validating the response.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            expected_prefix: Expected prefix in response text
            
        Returns:
            True if tool call succeeded and response matches expectations
        """
        result = await self.call_tool(tool_name, arguments)
        if not result:
            return False
            
        content = result.get("result", {}).get("content", [])
        if not content:
            return False
            
        # Extract text from content item
        if hasattr(content[0], "text"):
            text = content[0].text
        elif isinstance(content[0], dict) and "text" in content[0]:
            text = content[0]["text"]
        else:
            text = str(content[0])
            
        if expected_prefix and not text.startswith(expected_prefix):
            return False
            
        return True
