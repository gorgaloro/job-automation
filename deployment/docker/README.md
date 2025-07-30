# Docker Deployment

This directory contains Docker-specific deployment files.

## Files

- **Dockerfile** - Docker image configuration (in project root)
- **docker-compose.yml** - Multi-service configuration (in project root)

## Usage

```bash
# Build and run with Docker Compose
docker-compose up --build

# Build Docker image
docker build -t job-search-automation .
```
