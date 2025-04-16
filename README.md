# BasicMcpServer: MCP Server Implementation Resources

This repository serves three primary purposes:

1. **Simple Example MCP Server**: A basic reference implementation that you can clone and modify for your own needs
2. **Docker Containerization Demo**: Shows how to set up an MCP server in Docker with end-to-end testing
3. **Setup Automation**: Provides a script to generate more complex MCP servers (like the Jira integration)

## MCP References

Key resources that informed this implementation:

- [MCP Documentation](https://modelcontextprotocol.io/introduction) - Official documentation and introduction to the Model Context Protocol
- [Python SDK Repository](https://github.com/modelcontextprotocol/python-sdk) - The official Python SDK for MCP
- [MCP HTTP Client Example](https://github.com/slavashvets/mcp-http-client-example) - Reference implementation that helped develop the test code in this repository

## Contents

1. **Base MCP Server**: Simple reference implementation with a basic tool
2. **Docker Configuration**: Containerization setup with multi-stage builds
3. **End-to-End Tests**: Demonstration of proper MCP server testing
4. **`setup_jira_mcp_server.sh`**: Script for generating a Jira-integrated MCP server
5. **`mcp_server_implementation_guide.md`**: Comprehensive guide to MCP server implementation

## Getting Started

### Option 1: Use the Basic MCP Server as a Template

The simplest approach is to clone this repository and modify it for your needs:

```bash
# Clone the repository
git clone https://github.com/yourusername/BasicMcpServer.git my-mcp-server
cd my-mcp-server

# Modify src/server.py to implement your custom tools and resources
# Update config.py with your required environment variables
# Run with Docker or directly with Python
```

### Option 2: Learn Docker-Based MCP Server Implementation

Study the Docker configuration and end-to-end tests to understand:
- Multi-stage Docker builds for efficient images
- Container configuration best practices
- Testing patterns for MCP servers

### Option 3: Generate a Jira MCP Server

To create a complete Jira MCP server project structure:

1. Make the setup script executable (already done):
   ```bash
   chmod +x setup_jira_mcp_server.sh
   ```

2. Run the script:
   ```bash
   ./setup_jira_mcp_server.sh
   ```

   **Command-line options:**
   ```
   Usage: ./setup_jira_mcp_server.sh [OPTIONS]

   Options:
     -n, --name NAME     Specify project name (default: jira-mcp-server)
     --no-git            Skip Git repository initialization
     --no-github         Skip GitHub repository creation
     -h, --help          Show help message
   ```

3. Follow the instructions that appear after the script runs:
   - Navigate to the newly created project directory
   - Configure your Jira credentials in the `.env` file
   - Build and run the Docker container

The script automatically:
- Creates the complete project structure with all necessary files
- Initializes a Git repository (unless `--no-git` is specified)
- Creates a GitHub repository and pushes the code (if GitHub CLI is installed and authenticated)
- Makes all necessary scripts executable

This will create a more complex MCP server example that integrates with Jira, allowing AI assistants to interact with your Jira instance through the MCP protocol.

### Option 4: Understand MCP Server Implementation

If you want to learn more about how MCP servers work and how to implement them:

1. Read the comprehensive guide in `mcp_server_implementation_guide.md`
2. The guide covers:
   - Project structure and setup
   - Implementing MCP servers with FastMCP
   - Docker containerization
   - Testing strategies
   - Deployment options
   - Best practices

## Customizing for Other Services

The Jira MCP server can be used as a template for creating MCP servers for other services:

1. Generate the Jira MCP server project using the setup script
2. Replace the Jira-specific code with code for your target service:
   - Modify `src/services/` to implement your service integration
   - Update `src/server.py` to define tools and resources for your service
   - Update `src/config.py` to include the necessary configuration variables
   - Update `.env.example` with appropriate environment variables

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is a standard for communication between AI assistants and external services. It enables AI assistants to:

- Discover and call tools that perform actions
- Access resources that provide information
- Interact with external systems through a standardized interface

By implementing an MCP server, you can extend the capabilities of AI assistants by giving them access to your services and data. This repository uses the [official Python SDK](https://github.com/modelcontextprotocol/python-sdk) and follows best practices for MCP server implementation.

## Prerequisites

- Python 3.11 or higher
- Docker (for containerized deployment)
- Service-specific API credentials

## License

This project is provided under the MIT License.
