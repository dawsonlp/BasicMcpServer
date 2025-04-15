# Docker Setup for BasicMcpServer

This directory contains all Docker-related files for the BasicMcpServer project, following the separation of concerns principle by isolating containerization from application functionality.

## Directory Structure

```
docker/
├── Dockerfile         # Optimized multi-stage Dockerfile
├── .dockerignore      # Files excluded from build context
└── scripts/           # Container helper scripts
    ├── entrypoint.sh  # Container startup script
    └── run.sh         # Script to replace docker-compose functionality
```

## Quick Start

### Build the Docker image
```bash
./docker/scripts/run.sh build
```

### Run the server
```bash
./docker/scripts/run.sh run
```

### Run with hot reload for development
```bash
./docker/scripts/run.sh dev
```

### Run tests in container
```bash
./docker/scripts/run.sh test
```

### Clean up resources
```bash
./docker/scripts/run.sh clean
```

## Configuration

The container uses the following environment variables:
- `HOST`: Host to bind the server to (default: 0.0.0.0)
- `PORT`: Port to run the server on (default: 7501)
- `API_KEY`: API key for authentication
- `OTHER_SECRET`: Additional secret configuration

Set these environment variables before running the container or use a `.env` file.

## Design Decisions

### Why a Single Dockerfile Instead of Docker Compose?

For a single-container application like BasicMcpServer, using Docker Compose adds unnecessary complexity. By using a standalone Dockerfile and helper scripts, we:

1. Simplify the containerization process
2. Reduce the configuration overhead
3. Make the development workflow more straightforward
4. Maintain the same functionality with less complexity

### Multi-stage Build Benefits

Our Dockerfile uses a multi-stage build approach which:

1. Reduces the final image size by excluding build dependencies
2. Improves security by having a minimal runtime environment
3. Speeds up build times through better layer caching
4. Separates build concerns from runtime concerns

### Python 3.13

We use Python 3.13 (latest version) to benefit from:
1. Performance improvements
2. Security updates
3. New language features
4. Better compatibility with modern packages

### Security Considerations

The Docker configuration includes several security best practices:
1. Running as a non-root user (appuser)
2. Minimizing installed packages in the runtime image
3. Using specific image tags rather than 'latest'
4. Including health checks to monitor container health
5. Proper handling of environment variables

## Continuous Integration

For CI/CD pipelines, use the run.sh script with the appropriate commands. For example:

```yaml
# Example CI/CD workflow
steps:
  - name: Build Docker image
    run: ./docker/scripts/run.sh build
    
  - name: Run tests
    run: ./docker/scripts/run.sh test
