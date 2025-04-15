#!/bin/bash
# Helper script to replace docker-compose functionality

# Build the Docker image
function build() {
  echo "Building Docker image..."
  docker build -t basic-mcp-server:latest -f docker/Dockerfile .
}

# Run the container
function run() {
  echo "Running container..."
  docker run --rm -it \
    -p 7501:7501 \
    -e HOST=${HOST:-0.0.0.0} \
    -e PORT=${PORT:-7501} \
    -e API_KEY=${API_KEY} \
    -e OTHER_SECRET=${OTHER_SECRET} \
    --name basic-mcp-server \
    basic-mcp-server:latest
}

# Development mode with hot reload
function dev() {
  echo "Starting development container with hot reload..."
  docker run --rm -it \
    -p 7501:7501 \
    -e HOST=${HOST:-0.0.0.0} \
    -e PORT=${PORT:-7501} \
    -e API_KEY=${API_KEY} \
    -e OTHER_SECRET=${OTHER_SECRET} \
    -v "$(pwd)/src:/app/src" \
    --name basic-mcp-server-dev \
    basic-mcp-server:latest \
    python -m uvicorn src.main:create_app --host 0.0.0.0 --port 7501 --reload
}

# Run tests in container
function test() {
  echo "Running tests in container..."
  docker run --rm -it \
    -v "$(pwd)/tests:/app/tests" \
    -v "$(pwd)/src:/app/src" \
    basic-mcp-server:latest \
    python -m pytest tests/
}

# Clean up resources
function clean() {
  echo "Cleaning up Docker resources..."
  docker stop basic-mcp-server 2>/dev/null || true
  docker stop basic-mcp-server-dev 2>/dev/null || true
  docker rm basic-mcp-server 2>/dev/null || true
  docker rm basic-mcp-server-dev 2>/dev/null || true
  docker image prune -f
}

# Parse arguments
case "$1" in
  build)
    build
    ;;
  run)
    run
    ;;
  dev)
    dev
    ;;
  test)
    test
    ;;
  clean)
    clean
    ;;
  *)
    echo "Usage: $0 {build|run|dev|test|clean}"
    exit 1
    ;;
esac
