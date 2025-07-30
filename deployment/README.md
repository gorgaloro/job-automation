# Deployment

This directory contains deployment configurations and scripts for various platforms.

## Structure

- **[Railway](railway/)** - Railway deployment configuration
- **[Docker](docker/)** - Docker containerization files
- **[Production](production/)** - Production deployment scripts and guides

## Deployment Platforms

### Railway
- **`railway.json`** - Railway service configuration
- **`Procfile`** - Process definitions for Railway
- **`main.py`** - Railway entry point

### Docker
- **`Dockerfile`** - Docker image configuration
- **`docker-compose.yml`** - Multi-service orchestration

### Production
- Production deployment scripts and documentation

## Quick Deployment

### Railway
```bash
# Deploy to Railway (requires Railway CLI)
railway deploy
```

### Docker
```bash
# Build and run locally
docker-compose up --build

# Build for production
docker build -t job-search-automation .
```

## Environment Variables

All deployment platforms require proper environment variable configuration. See `config/env/` for templates.
