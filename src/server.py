"""
MCP server implementation.

This module defines the MCP server and its tools/resources.
"""

import mcp.types as types
from mcp.server.lowlevel import Server


def create_mcp_server():
    """
    Create and configure an MCP server instance.
    
    Returns:
        Server: A configured MCP server instance
    """
    # Create an MCP server instance with a unique name
    server = Server("basic-mcp-server")
    
    # Add tools
    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        """
        List all available tools provided by this server.
        """
        return [
            types.Tool(
                name="example",
                description="An example tool that processes input text",
                inputSchema={
                    "type": "object",
                    "required": ["input"],
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Input string to process",
                        }
                    },
                },
            )
        ]
    
    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        Handle tool invocation.
        
        Args:
            name: The name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            A list of content objects with the tool's response
            
        Raises:
            ValueError: If the tool name is unknown or arguments are invalid
        """
        if name != "example":
            raise ValueError(f"Unknown tool: {name}")
        
        # Validate arguments
        if "input" not in arguments:
            raise ValueError("Missing required argument 'input'")
        
        input_value = arguments["input"]
        
        # Process the input (in a real application, this would do something useful)
        processed_result = f"Processed: {input_value}"
        
        # Return the result as text content
        return [types.TextContent(type="text", text=processed_result)]
    
    # You can add more handlers here for resources, prompts, etc.
    
    return server
