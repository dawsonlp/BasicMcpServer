"""
Main entry point for the MCP server.

This module sets up and runs the HTTP+SSE server with Starlette and Uvicorn.
"""

import logging
import sys

import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount, Route

from mcp.server.sse import SseServerTransport

from .config import settings
from .server import create_mcp_server


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


# Create the MCP server
mcp_server = create_mcp_server()

# Create SSE transport
sse = SseServerTransport("/messages/")


async def handle_sse(request):
    """
    Handle SSE connections from clients.
    
    Args:
        request: The Starlette request object
        
    Returns:
        An SSE response that streams messages to the client
    """
    logger.info(f"New SSE connection from {request.client}")
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_server.run(
            streams[0], streams[1], mcp_server.create_initialization_options()
        )


# Create Starlette app with routes
app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)


def start():
    """Start the Uvicorn server."""
    logger.info(f"Starting MCP server on {settings.host}:{settings.port}")
    uvicorn.run(
        app, 
        host=settings.host, 
        port=settings.port,
        log_level="info"
    )


if __name__ == "__main__":
    start()
