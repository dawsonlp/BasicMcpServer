FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY ./src ./src

# Install dependencies globally
RUN pip install -e .

# Run with a non-root user
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Expose the port
EXPOSE 7500

# Run the application
CMD ["python", "-m", "src.main"]
