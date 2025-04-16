#!/bin/bash
set -e

# Configuration
PROJECT_NAME="jira-mcp-server"
BASE_DIR="$(pwd)/${PROJECT_NAME}"

# Colors for console output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Creating Jira MCP Server in ${BASE_DIR}${NC}"

# Create project directory structure
mkdir -p "${BASE_DIR}"
mkdir -p "${BASE_DIR}/src/tools"
mkdir -p "${BASE_DIR}/src/services"
mkdir -p "${BASE_DIR}/docker/scripts"
mkdir -p "${BASE_DIR}/tests/e2e"

# Create pyproject.toml
cat > "${BASE_DIR}/pyproject.toml" << 'EOL'
[build-system]
requires = ["setuptools>=68.0.0", "wheel>=0.41.0"]
build-backend = "setuptools.build_meta"

[project]
name = "jira-mcp-server"
version = "0.1.0"
description = "An MCP server for interacting with Jira"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "MCP User"}
]
dependencies = [
    "mcp>=1.6.0",
    "starlette>=0.46.2",
    "uvicorn>=0.34.1",
    "sse-starlette>=2.2.1",
    "pydantic-settings>=2.8.1",
    "httpx>=0.28.1",
    "jira>=3.5.0",
]

[project.optional-dependencies]
dev = [
    "black>=23.10.0",
    "isort>=5.12.0",
    "flake8>=6.1.0",
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
]

[tool.setuptools]
packages = ["src"]

[tool.black]
line-length = 88
target-version = ["py311"]

[tool.isort]
profile = "black"
line_length = 88
EOL

# Create .env.example
cat > "${BASE_DIR}/.env.example" << 'EOL'
# Server settings
HOST=0.0.0.0
PORT=7501

# Jira credentials
JIRA_URL=https://your-jira-instance.atlassian.net
JIRA_USERNAME=your-username@example.com
JIRA_API_TOKEN=your-api-token
EOL

# Create .gitignore
cat > "${BASE_DIR}/.gitignore" << 'EOL'
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.venv
venv/
ENV/
.idea/
.vscode/
*.swp
.DS_Store
EOL

# Create README.md
cat > "${BASE_DIR}/README.md" << 'EOL'
# Jira MCP Server

An MCP (Model Context Protocol) server for interacting with Jira. This server provides tools for querying and manipulating Jira data through the MCP protocol, allowing AI assistants to interact with your Jira instance.

## Features

- List Jira projects
- Search for issues
- Get issue details
- Create and update issues
- Add comments to issues
- Custom JQL queries

## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and fill in your Jira credentials
3. Build and run with Docker:

```bash
docker build -t jira-mcp-server .
docker run -p 7501:7501 --env-file .env jira-mcp-server
```

## Testing

Run tests with:

```bash
python -m tests.e2e.direct_test
```

## Using with an LLM Assistant

Connect your LLM assistant to this MCP server to enable Jira integration capabilities.
EOL

# Create main.py
cat > "${BASE_DIR}/src/main.py" << 'EOL'
"""
Main entry point for the Jira MCP server.

This module sets up and runs the MCP server using FastMCP.
"""

import logging
import sys

from .config import settings
from .server import create_mcp_server


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def start():
    """Start the MCP server using FastMCP's built-in functionality."""
    logger.info(f"Starting Jira MCP server on {settings.host}:{settings.port}")
    
    # Create the MCP server
    mcp_server = create_mcp_server()
    
    # Configure server settings
    mcp_server.settings.host = settings.host
    mcp_server.settings.port = settings.port
    mcp_server.settings.debug = True
    mcp_server.settings.log_level = "INFO"
    
    # Run the server with SSE transport
    mcp_server.run("sse")


# Alternative approach using the FastMCP ASGI application
def create_app():
    """Create an ASGI application for use with an external ASGI server."""
    # Create the MCP server
    mcp_server = create_mcp_server()
    
    # Configure server settings
    mcp_server.settings.debug = True
    
    # Return the ASGI app instance
    return mcp_server.sse_app()


if __name__ == "__main__":
    start()
EOL

# Create config.py
cat > "${BASE_DIR}/src/config.py" << 'EOL'
"""
Configuration module for the Jira MCP server.

This module handles loading and validating environment variables using pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Server settings and configuration loaded from environment variables.
    
    Environment variables can be set directly or loaded from a .env file.
    """
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 7501
    
    # Jira credentials
    jira_url: str
    jira_username: str
    jira_api_token: str
    
    # Configure settings to load from .env file
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Create a settings instance for importing in other modules
settings = Settings()
EOL

# Create jira_service.py
cat > "${BASE_DIR}/src/services/jira_service.py" << 'EOL'
"""
Service for interacting with the Jira API.

This module provides a wrapper around the Jira Python library.
"""

import logging
from typing import Any, Dict, List, Optional

from jira import JIRA
from jira.exceptions import JIRAError

from ..config import settings

logger = logging.getLogger(__name__)


class JiraService:
    """Service for interacting with Jira."""
    
    def __init__(self):
        """Initialize the Jira service with credentials from settings."""
        self._client = None
        
    def _get_client(self) -> JIRA:
        """
        Get a Jira client instance, creating one if it doesn't exist.
        
        Returns:
            JIRA: A Jira client instance
        """
        if not self._client:
            logger.info(f"Connecting to Jira at {settings.jira_url}")
            self._client = JIRA(
                server=settings.jira_url,
                basic_auth=(settings.jira_username, settings.jira_api_token)
            )
        return self._client
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get a list of projects.
        
        Returns:
            List[Dict[str, Any]]: List of project dictionaries
        """
        try:
            client = self._get_client()
            projects = client.projects()
            return [
                {
                    "id": project.id,
                    "key": project.key,
                    "name": project.name,
                    "lead": getattr(project, "lead", {}).get("displayName", "Unknown"),
                }
                for project in projects
            ]
        except JIRAError as e:
            logger.error(f"Error getting projects: {e}")
            raise
    
    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Get issue details by key.
        
        Args:
            issue_key: The issue key (e.g., "PROJ-123")
            
        Returns:
            Dict[str, Any]: Issue details dictionary
        """
        try:
            client = self._get_client()
            issue = client.issue(issue_key)
            
            # Extract fields
            fields = issue.fields
            
            return {
                "id": issue.id,
                "key": issue.key,
                "summary": fields.summary,
                "description": fields.description or "",
                "status": fields.status.name,
                "assignee": getattr(fields.assignee, "displayName", None),
                "reporter": getattr(fields.reporter, "displayName", None),
                "created": fields.created,
                "updated": fields.updated,
                "priority": getattr(fields.priority, "name", None),
                "issuetype": fields.issuetype.name,
                "project": {
                    "key": fields.project.key,
                    "name": fields.project.name,
                },
            }
        except JIRAError as e:
            logger.error(f"Error getting issue {issue_key}: {e}")
            raise
    
    def search_issues(
        self, 
        jql: str,
        max_results: int = 50,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for issues using JQL.
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results to return
            fields: List of fields to include (optional)
            
        Returns:
            List[Dict[str, Any]]: List of issue dictionaries
        """
        try:
            client = self._get_client()
            issues = client.search_issues(
                jql_str=jql,
                maxResults=max_results,
                fields=fields or '*navigable'
            )
            
            return [
                {
                    "id": issue.id,
                    "key": issue.key,
                    "summary": issue.fields.summary,
                    "status": issue.fields.status.name,
                    "assignee": getattr(issue.fields.assignee, "displayName", None),
                    "issuetype": issue.fields.issuetype.name,
                    "project": issue.fields.project.key,
                    "updated": issue.fields.updated,
                }
                for issue in issues
            ]
        except JIRAError as e:
            logger.error(f"Error searching issues with JQL '{jql}': {e}")
            raise
    
    def create_issue(
        self,
        project_key: str,
        summary: str,
        issue_type: str = "Task",
        description: Optional[str] = None,
        assignee: Optional[str] = None,
        **fields
    ) -> Dict[str, Any]:
        """
        Create a new issue.
        
        Args:
            project_key: The project key (e.g., "PROJ")
            summary: Issue summary/title
            issue_type: Issue type (e.g., "Task", "Bug", "Story")
            description: Issue description (optional)
            assignee: Assignee username (optional)
            **fields: Additional fields to set
            
        Returns:
            Dict[str, Any]: Created issue details
        """
        try:
            client = self._get_client()
            
            # Prepare issue fields
            issue_dict = {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": issue_type},
            }
            
            if description:
                issue_dict["description"] = description
                
            # Add any additional fields
            issue_dict.update(fields)
            
            # Create the issue
            issue = client.create_issue(fields=issue_dict)
            
            # Assign if specified
            if assignee:
                issue.update(assignee={"name": assignee})
            
            # Return created issue
            return self.get_issue(issue.key)
        except JIRAError as e:
            logger.error(f"Error creating issue in project {project_key}: {e}")
            raise
    
    def update_issue(self, issue_key: str, **fields) -> Dict[str, Any]:
        """
        Update an existing issue.
        
        Args:
            issue_key: The issue key (e.g., "PROJ-123")
            **fields: Fields to update
            
        Returns:
            Dict[str, Any]: Updated issue details
        """
        try:
            client = self._get_client()
            issue = client.issue(issue_key)
            
            # Update the issue
            issue.update(fields=fields)
            
            # Return updated issue
            return self.get_issue(issue_key)
        except JIRAError as e:
            logger.error(f"Error updating issue {issue_key}: {e}")
            raise
    
    def add_comment(self, issue_key: str, body: str) -> Dict[str, Any]:
        """
        Add a comment to an issue.
        
        Args:
            issue_key: The issue key (e.g., "PROJ-123")
            body: Comment text
            
        Returns:
            Dict[str, Any]: Comment details
        """
        try:
            client = self._get_client()
            comment = client.add_comment(issue_key, body)
            
            return {
                "id": comment.id,
                "body": comment.body,
                "author": getattr(comment, "author", {}).get("displayName", "Unknown"),
                "created": getattr(comment, "created", None),
                "updated": getattr(comment, "updated", None),
                "issue_key": issue_key,
            }
        except JIRAError as e:
            logger.error(f"Error adding comment to issue {issue_key}: {e}")
            raise
EOL

# Create __init__.py in services directory 
cat > "${BASE_DIR}/src/services/__init__.py" << 'EOL'
from .jira_service import JiraService

__all__ = ["JiraService"]
EOL

# Create __init__.py in tools directory
cat > "${BASE_DIR}/src/tools/__init__.py" << 'EOL'
# Import tools here if needed
EOL

# Create __init__.py in src directory
cat > "${BASE_DIR}/src/__init__.py" << 'EOL'
"""
Jira MCP Server Package
"""
EOL

# Create server.py
cat > "${BASE_DIR}/src/server.py" << 'EOL'
"""
MCP server implementation using FastMCP.

This module defines the MCP server and its tools/resources.
"""

import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .services.jira_service import JiraService

logger = logging.getLogger(__name__)


def create_mcp_server():
    """
    Create and configure an MCP server instance using FastMCP.
    
    Returns:
        FastMCP: A configured FastMCP server instance
    """
    # Create a FastMCP server instance with a unique name
    mcp = FastMCP("jira-mcp-server")
    
    # Create service instances
    jira_service = JiraService()
    
    # Projects
    @mcp.tool()
    def list_projects() -> List[Dict[str, Any]]:
        """
        List all accessible Jira projects.
        
        Returns:
            List of projects with key, name, and other metadata
        """
        return jira_service.get_projects()
    
    # Issues
    @mcp.tool()
    def get_issue(issue_key: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific Jira issue.
        
        Args:
            issue_key: The Jira issue key (e.g., "PROJ-123")
            
        Returns:
            Issue details including summary, description, status, and assignee
        """
        return jira_service.get_issue(issue_key)
    
    @mcp.tool()
    def search_issues(
        jql: str,
        max_results: int = 50,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for Jira issues using JQL (Jira Query Language).
        
        Args:
            jql: JQL query string (e.g., "project = PROJ AND status = 'In Progress'")
            max_results: Maximum number of results to return
            fields: Optional list of fields to include
            
        Returns:
            List of matching issues with key, summary, status, and other metadata
        """
        return jira_service.search_issues(jql, max_results, fields)
    
    @mcp.tool()
    def create_issue(
        project_key: str,
        summary: str,
        issue_type: str = "Task",
        description: Optional[str] = None,
        assignee: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Jira issue.
        
        Args:
            project_key: The project key (e.g., "PROJ")
            summary: Issue summary/title
            issue_type: Issue type (default: "Task")
            description: Issue description (optional)
            assignee: Assignee username (optional)
            
        Returns:
            Created issue details
        """
        return jira_service.create_issue(
            project_key=project_key,
            summary=summary,
            issue_type=issue_type,
            description=description,
            assignee=assignee
        )
    
    @mcp.tool()
    def update_issue(
        issue_key: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        assignee: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing Jira issue.
        
        Args:
            issue_key: The issue key (e.g., "PROJ-123")
            summary: New summary (optional)
            description: New description (optional)
            assignee: New assignee username (optional)
            status: New status (optional)
            
        Returns:
            Updated issue details
        """
        fields = {}
        if summary:
            fields["summary"] = summary
        if description:
            fields["description"] = description
        if assignee:
            fields["assignee"] = {"name": assignee}
        if status:
            fields["status"] = {"name": status}
            
        return jira_service.update_issue(issue_key, **fields)
    
    @mcp.tool()
    def add_comment(issue_key: str, body: str) -> Dict[str, Any]:
        """
        Add a comment to a Jira issue.
        
        Args:
            issue_key: The issue key (e.g., "PROJ-123")
            body: Comment text
            
        Returns:
            Comment details
        """
        return jira_service.add_comment(issue_key, body)
    
    # Add resources
    @mcp.resource("resource://jira/project/{project_key}")
    def project_resource(project_key: str) -> Dict[str, Any]:
        """
        Resource for accessing a specific project.
        
        Args:
            project_key: The project key
            
        Returns:
            Project information
        """
        projects = jira_service.get_projects()
        for project in projects:
            if project["key"] == project_key:
                return project
        return {"error": f"Project {project_key} not found"}
    
    @mcp.resource("resource://jira/issue/{issue_key}")
    def issue_resource(issue_key: str) -> Dict[str, Any]:
        """
        Resource for accessing a specific issue.
        
        Args:
            issue_key: The issue key
            
        Returns:
            Issue information
        """
        return jira_service.get_issue(issue_key)
    
    return mcp
EOL

# Create Dockerfile
cat > "${BASE_DIR}/docker/Dockerfile" << 'EOL'
# Stage 1: Builder
FROM python:3.11-slim AS builder

# Set build-time environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /build

# Copy only what's needed for installation
COPY pyproject.toml README.md ./
COPY ./src ./src

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev \
    && pip install --upgrade pip \
    && pip install build wheel \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Build wheel package
RUN pip wheel --no-deps --wheel-dir /wheels -e .

# Stage 2: Runtime
FROM python:3.11-slim AS runtime

# Set runtime environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Copy wheel from builder stage
COPY --from=builder /wheels /wheels

# Copy application code
COPY ./src ./src

# Install dependencies and app
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

# Add metadata
LABEL maintainer="MCP User" \
      version="0.1.0" \
      description="Jira MCP Server - An MCP server for interacting with Jira"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import http.client; conn = http.client.HTTPConnection('localhost:7501'); conn.request('GET', '/health'); response = conn.getresponse(); exit(0 if response.status == 200 else 1)"

# Expose the port
EXPOSE 7501

# Command to run the application
CMD ["python", "-m", "src.main"]
EOL

# Create entrypoint.sh
cat > "${BASE_DIR}/docker/scripts/entrypoint.sh" << 'EOL'
#!/bin/bash
set -e

# Health check endpoint setup if needed
if [[ "$1" == "healthcheck" ]]; then
  python -c "import http.client; conn = http.client.HTTPConnection('localhost:7501'); conn.request('GET', '/health'); response = conn.getresponse(); exit(0 if response.status == 200 else 1)"
  exit $?
fi

# Run the application
exec python -m src.main
EOL

# Make entrypoint script executable
chmod +x "${BASE_DIR}/docker/scripts/entrypoint.sh"

# Create run.sh
cat > "${BASE_DIR}/docker/scripts/run.sh" << 'EOL'
#!/bin/bash
set -e

# Build the Docker image
docker build -t jira-mcp-server -f docker/Dockerfile .

# Run the Docker container
docker run -p 7501:7501 \
  --env-file .env \
  --name jira-mcp-server \
  jira-mcp-server
EOL

# Make run script executable
chmod +x "${BASE_DIR}/docker/scripts/run.sh"

# Create test script
cat > "${BASE_DIR}/tests/e2e/direct_test.py" << 'EOL'
#!/usr/bin/env python3
"""
Direct MCP test for the Jira MCP server.

This script provides a simple test for the MCP server without any abstraction layers.
"""

import asyncio
import sys
import logging
import json
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
    logger.info(f"Testing Jira MCP server at {SERVER_URL}")
    
    if urlparse(SERVER_URL).scheme not in ("http", "https"):
        logger.error("Error: Server URL must start with http:// or https://")
        return False
    
    try:
        # Use the sse_client to establish the SSE connection
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
                
                # Test listing projects
                try:
                    logger.info("Testing list_projects tool")
                    projects_result = await session.call_tool("list_projects", {})
                    if hasattr(projects_result, "content") and projects_result.content:
                        projects = json.loads(projects_result.content[0].text)
                        logger.info(f"Found {len(projects)} projects")
                        if projects:
                            logger.info(f"First project: {projects[0]}")
                except Exception as e:
                    logger.error(f"Error testing list_projects: {str(e)}")
                    
                return True
                
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Direct test for Jira MCP server")
    parser.add_argument("--host", default="localhost", help="Server hostname")
    parser.add_argument("--port", type=int, default=7501, help="Server port")
    args = parser.parse_args()
    
    # Update constants based on command-line arguments
    SERVER_URL = f"http://{args.host}:{args.port}/sse"
    
    # Run the test
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
EOL

# Create README.md for tests
cat > "${BASE_DIR}/tests/e2e/README.md" << 'EOL'
# End-to-End Tests for Jira MCP Server

This directory contains end-to-end tests for the Jira MCP server implementation.

## Overview

The tests in this directory verify that the MCP server works correctly by:
1. Testing the MCP protocol connections
2. Testing tool discovery and execution
3. Verifying responses from Jira API calls

## Running Tests

### Direct Test

The primary test script that uses the SDK directly:

```bash
python tests/e2e/direct_test.py
```

This test:
- Connects to a running MCP server
- Lists available tools, resources, and prompts
- Tests the list_projects tool

Options:
- `--host` - Server hostname (default: localhost)
- `--port` - Server port (default: 7501)

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

## Dependencies

Required dependencies are listed in `requirements.txt`.
EOL

# Create requirements.txt for tests
cat > "${BASE_DIR}/tests/e2e/requirements.txt" << 'EOL'
mcp>=1.6.0
jira>=3.5.0
httpx>=0.28.1
pytest>=7.4.0
pytest-asyncio>=0.21.0
EOL

echo -e "${GREEN}Project structure created successfully at ${BASE_DIR}${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Navigate to the project directory: cd ${PROJECT_NAME}"
echo "2. Create a .env file with your Jira credentials: cp .env.example .env"
echo "3. Edit the .env file with your actual Jira credentials"
echo "4. Build and run the Docker container: ./docker/scripts/run.sh"
echo ""
echo -e "${BLUE}Testing:${NC}"
echo "Run the test script after starting the server: python tests/e2e/direct_test.py"

# Make script executable
chmod +x "${BASE_DIR}/docker/scripts/run.sh"
