"""
MCP client for testing.

This module provides a simple client for the Model Context Protocol that can be
used for testing MCP servers.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, Optional, List, Callable, AsyncGenerator
import logging

import aiohttp
import sseclient

logger = logging.getLogger(__name__)


class McpClient:
    """A simple client for testing MCP servers."""

    def __init__(self, base_url: str):
        """
        Initialize the MCP client.
        
        Args:
            base_url: Base URL of the MCP server, including the /sse endpoint
        """
        self.base_url = base_url
        self.session_id = str(uuid.uuid4())
        self.messages_url = f"{base_url.replace('/sse', '')}/messages/?session_id={self.session_id}"
        self.session = None
        self.client_id = str(uuid.uuid4())
        self.tools_info = {}
        
    async def __aenter__(self):
        """Create session for context manager."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close session for context manager."""
        if self.session:
            await self.session.close()
            
    async def connect(self) -> bool:
        """
        Connect to the MCP server and initialize the session.
        
        Returns:
            bool: True if connection and initialization succeeded
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            # Start SSE connection in a separate task
            sse_task = asyncio.create_task(self._listen_for_sse_messages())
            
            # Send initialization message
            init_message = {
                "type": "initialize",
                "requestId": str(uuid.uuid4()),
                "content": {
                    "clientInfo": {
                        "clientType": "test",
                        "clientVersion": "1.0.0"
                    },
                    "capabilities": {
                        "receiveText": True,
                        "receiveImage": False
                    }
                }
            }
            
            response = await self._send_message(init_message)
            logger.debug(f"Initialization response: {response}")
            
            # Request available tools
            tools_response = await self.list_tools()
            if not tools_response:
                logger.error("Failed to retrieve tools")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {str(e)}")
            return False
            
    async def _listen_for_sse_messages(self):
        """Listen for SSE messages from the server."""
        try:
            async with self.session.get(self.base_url) as response:
                if response.status != 200:
                    logger.error(f"Failed to connect to SSE endpoint: {response.status}")
                    return
                    
                # Using aiohttp to stream the SSE response
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        try:
                            message = json.loads(data)
                            logger.debug(f"Received SSE message: {message}")
                            
                            # Process message based on type
                            if message.get('type') == 'toolResult':
                                logger.info(f"Tool result: {message}")
                                
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse SSE message: {data}")
                            
        except Exception as e:
            logger.error(f"Error in SSE connection: {str(e)}")
            
    async def _send_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a message to the MCP server.
        
        Args:
            message: The message to send
            
        Returns:
            Optional response JSON
        """
        try:
            async with self.session.post(self.messages_url, json=message) as response:
                if response.status != 200:
                    logger.error(f"Failed to send message: {response.status}")
                    return None
                    
                return await response.json()
                
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return None
            
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        Request the list of available tools from the server.
        
        Returns:
            List of tool definitions
        """
        request_id = str(uuid.uuid4())
        message = {
            "type": "listTools",
            "requestId": request_id
        }
        
        response = await self._send_message(message)
        if not response:
            return []
            
        # Extract tools from response
        tools = []
        if response.get('type') == 'toolList':
            tools = response.get('content', {}).get('tools', [])
            # Store tools for later reference
            self.tools_info = {tool['name']: tool for tool in tools}
            
        return tools
        
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool result if successful, None otherwise
        """
        if tool_name not in self.tools_info:
            logger.error(f"Unknown tool: {tool_name}")
            return None
            
        request_id = str(uuid.uuid4())
        message = {
            "type": "callTool",
            "requestId": request_id,
            "content": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self._send_message(message)
        if not response:
            return None
            
        return response
        
    async def test_tool(self, tool_name: str, arguments: Dict[str, Any], expected_prefix: str = None) -> bool:
        """
        Test a tool by calling it and validating the response.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            expected_prefix: Optional prefix to check in the response
            
        Returns:
            True if tool call was successful and response matches expected format
        """
        result = await self.call_tool(tool_name, arguments)
        if not result:
            return False
            
        # Check if the result is a tool result
        if result.get('type') != 'toolResult':
            logger.error(f"Expected toolResult, got {result.get('type')}")
            return False
            
        # Get the content from the result
        content = result.get('content', [])
        if not content:
            logger.error("Tool result has no content")
            return False
            
        # If we have an expected prefix, validate the response
        if expected_prefix and isinstance(content[0], dict):
            text_content = content[0].get('text', '')
            if not text_content.startswith(expected_prefix):
                logger.error(f"Expected response to start with '{expected_prefix}', got '{text_content}'")
                return False
                
        return True
