# Stage 1: Builder
FROM python:3.13-slim AS builder

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
FROM python:3.13-slim AS runtime

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
      description="BasicMcpServer - A minimal MCP server"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import http.client; conn = http.client.HTTPConnection('localhost:7501'); conn.request('GET', '/health'); response = conn.getresponse(); exit(0 if response.status == 200 else 1)"

# Expose the port
EXPOSE 7501

# Command to run the application
CMD ["python", "-m", "src.main"]
