#!/usr/bin/env python3
"""
End-to-end test for the MCP server container.

This script tests the MCP server by:
1. Building and starting the Docker container
2. Testing connectivity to the server
3. Testing the MCP protocol
4. Testing the example tool
5. Cleaning up resources
"""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Optional

import docker
import requests

from mcp_client import McpClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Constants
CONTAINER_NAME = "mcp_test_container"
IMAGE_NAME = "basic-mcp-server:test"
HOST_PORT = 7500
CONTAINER_PORT = 7500
SERVER_URL = f"http://localhost:{HOST_PORT}"
SSE_URL = f"{SERVER_URL}/sse"

# Timeouts
BUILD_TIMEOUT = 300  # seconds
START_TIMEOUT = 30   # seconds
REQUEST_TIMEOUT = 10  # seconds


class McpServerTest:
    """Test harness for MCP server container testing."""

    def __init__(self):
        """Initialize the test harness."""
        self.docker_client = docker.from_env()
        self.container = None
        self.test_results = {
            "build": False,
            "start": False,
            "connectivity": False,
            "protocol": False,
            "tool": False,
        }

    def build_image(self) -> bool:
        """
        Build the Docker image for the MCP server.
        
        Returns:
            bool: True if build succeeded
        """
        logger.info("Building Docker image...")
        try:
            # Get the project root directory (parent of tests directory)
            project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            
            # Build the image with the Dockerfile from the docker directory
            image, logs = self.docker_client.images.build(
                path=project_dir,
                dockerfile="docker/Dockerfile",
                tag=IMAGE_NAME,
                quiet=False
            )
            
            logger.info(f"Built image: {image.id}")
            self.test_results["build"] = True
            return True
            
        except docker.errors.BuildError as e:
            logger.error(f"Build error: {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"Error building image: {str(e)}")
            return False

    def start_container(self) -> bool:
        """
        Start the Docker container with the MCP server.
        
        Returns:
            bool: True if container started successfully
        """
        logger.info("Starting container...")
        try:
            # First remove any existing container with the same name
            try:
                old_container = self.docker_client.containers.get(CONTAINER_NAME)
                logger.info(f"Removing existing container: {old_container.id}")
                old_container.remove(force=True)
            except docker.errors.NotFound:
                # No existing container, that's fine
                pass
                
            # Start the container
            self.container = self.docker_client.containers.run(
                IMAGE_NAME,
                name=CONTAINER_NAME,
                ports={f"{CONTAINER_PORT}/tcp": HOST_PORT},
                environment={
                    "API_KEY": "test_key",
                    "OTHER_SECRET": "test_secret"
                },
                detach=True
            )
            
            logger.info(f"Started container: {self.container.id}")
            
            # Wait for container to be ready
            for _ in range(START_TIMEOUT):
                self.container.reload()
                if self.container.status == "running":
                    time.sleep(2)  # Give the server a moment to start
                    self.test_results["start"] = True
                    return True
                time.sleep(1)
                
            logger.error("Container did not start within timeout")
            return False
            
        except Exception as e:
            logger.error(f"Error starting container: {str(e)}")
            return False

    def test_connectivity(self) -> bool:
        """
        Test HTTP connectivity to the server.
        
        Returns:
            bool: True if connectivity test passed
        """
        logger.info("Testing connectivity...")
        try:
            # Test base endpoint
            try:
                response = requests.get(SERVER_URL, timeout=REQUEST_TIMEOUT)
                logger.info(f"Base URL status: {response.status_code}")
            except requests.RequestException as e:
                logger.warning(f"Base URL request failed (this may be expected): {str(e)}")
                
            # Test SSE endpoint (with stream=True)
            response = requests.get(SSE_URL, stream=True, timeout=REQUEST_TIMEOUT)
            logger.info(f"SSE endpoint status: {response.status_code}")
            
            # Check content type
            content_type = response.headers.get("Content-Type", "")
            logger.info(f"Content-Type: {content_type}")
            
            # Success criteria: SSE endpoint returns 200 with text/event-stream content type
            success = (
                response.status_code == 200 and
                "text/event-stream" in content_type.lower()
            )
            
            self.test_results["connectivity"] = success
            return success
            
        except requests.RequestException as e:
            logger.error(f"Error connecting to server: {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error in connectivity test: {str(e)}")
            return False

    async def test_mcp_protocol(self) -> bool:
        """
        Test the MCP protocol by connecting and listing tools.
        
        Returns:
            bool: True if protocol test passed
        """
        logger.info("Testing MCP protocol...")
        try:
            async with McpClient(SSE_URL) as client:
                # Connect to the server
                connected = await client.connect()
                if not connected:
                    logger.error("Failed to connect to MCP server")
                    return False
                    
                # List tools
                tools = await client.list_tools()
                logger.info(f"Available tools: {json.dumps(tools, indent=2)}")
                
                # Verify example tool is available
                example_tool = next((t for t in tools if t["name"] == "example"), None)
                if not example_tool:
                    logger.error("Example tool not found")
                    return False
                    
                logger.info("MCP protocol test passed")
                self.test_results["protocol"] = True
                return True
                
        except Exception as e:
            logger.error(f"Error in MCP protocol test: {str(e)}")
            return False

    async def test_example_tool(self) -> bool:
        """
        Test the example tool functionality.
        
        Returns:
            bool: True if tool test passed
        """
        logger.info("Testing example tool...")
        try:
            async with McpClient(SSE_URL) as client:
                # Connect to the server
                connected = await client.connect()
                if not connected:
                    logger.error("Failed to connect to MCP server")
                    return False
                    
                # Test the example tool
                test_input = "Hello MCP World!"
                success = await client.test_tool(
                    "example",
                    {"input": test_input},
                    expected_prefix=f"Processed: {test_input}"
                )
                
                if success:
                    logger.info("Example tool test passed")
                    self.test_results["tool"] = True
                    return True
                else:
                    logger.error("Example tool test failed")
                    return False
                    
        except Exception as e:
            logger.error(f"Error in example tool test: {str(e)}")
            return False

    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up resources...")
        if self.container:
            try:
                self.container.stop()
                self.container.remove()
                logger.info("Container stopped and removed")
            except Exception as e:
                logger.error(f"Error cleaning up container: {str(e)}")

    def print_results(self):
        """Print test results."""
        logger.info("Test Results:")
        for test, result in self.test_results.items():
            logger.info(f"  {test.ljust(12)}: {'✅ PASS' if result else '❌ FAIL'}")
            
        all_passed = all(self.test_results.values())
        logger.info(f"Overall Result: {'✅ PASS' if all_passed else '❌ FAIL'}")
        return all_passed

    def run_tests(self) -> bool:
        """
        Run all tests.
        
        Returns:
            bool: True if all tests passed
        """
        try:
            # Stage 1: Build and start container
            if not self.build_image():
                logger.error("Image build failed, aborting tests")
                return False
                
            if not self.start_container():
                logger.error("Container start failed, aborting tests")
                return False
                
            # Stage 2: Test connectivity
            if not self.test_connectivity():
                logger.error("Connectivity test failed, aborting tests")
                return False
                
            # Stage 3: Test MCP protocol and tools (async)
            asyncio.run(self.run_async_tests())
                
            # Print results and return overall status
            return self.print_results()
            
        finally:
            self.cleanup()

    async def run_async_tests(self):
        """Run async tests for MCP protocol and tools."""
        # Test MCP protocol
        protocol_ok = await self.test_mcp_protocol()
        if not protocol_ok:
            logger.error("MCP protocol test failed, skipping tool test")
            return
            
        # Test example tool
        await self.test_example_tool()


if __name__ == "__main__":
    test = McpServerTest()
    success = test.run_tests()
    sys.exit(0 if success else 1)
