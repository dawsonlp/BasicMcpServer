"""
MCP server implementation using FastMCP.

This module defines the MCP server and its tools/resources.
"""

from mcp.server.fastmcp import FastMCP


def create_mcp_server():
    """
    Create and configure an MCP server instance using FastMCP.
    
    Returns:
        FastMCP: A configured FastMCP server instance
    """
    # Create a FastMCP server instance with a unique name
    mcp = FastMCP("basic-mcp-server")
    
    # Add an example tool using the simpler decorator syntax
    @mcp.tool()
    def example(input: str) -> str:
        """An example tool that processes input text"""
        return f"Processed: {input}"
    
    # You can add more tools, resources, and prompts here using FastMCP's syntax:
    # 
    # @mcp.tool()
    # def another_tool(param1: str, param2: int = 0) -> dict:
    #     """Another example tool with multiple parameters"""
    #     return {"result": f"Processed {param1} with {param2}"}
    # 
    # @mcp.resource("resource://example")
    # def example_resource() -> str:
    #     """An example resource"""
    #     return "Resource content"
    # 
    # @mcp.resource("resource://{param}/data")
    # def parameterized_resource(param: str) -> str:
    #     """Resource with parameters"""
    #     return f"Data for {param}"
    
    return mcp
