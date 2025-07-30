# 🚀 Deployment Guide

## Overview

This guide covers deploying the Job Search Automation Platform across different environments, from local development to production-ready deployments.

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Node.js 18+ (for frontend)
- Git
- Access to required services (Supabase, HubSpot, OpenAI)

## Environment Setup

### 1. Environment Variables

Create environment files for each deployment stage:

#### `.env.development`
```bash
# Database
SUPABASE_URL=http://localhost:54321
SUPABASE_KEY=your_local_supabase_key
SUPABASE_SERVICE_ROLE_KEY=your_local_service_role_key

# External APIs
HUBSPOT_API_KEY=your_hubspot_test_key
OPENAI_API_KEY=your_openai_key

# Application
DEBUG=true
LOG_LEVEL=debug
ENVIRONMENT=development
```

#### `.env.staging`
```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_staging_supabase_key
SUPABASE_SERVICE_ROLE_KEY=your_staging_service_role_key

# External APIs
HUBSPOT_API_KEY=your_hubspot_staging_key
OPENAI_API_KEY=your_openai_key

# Application
DEBUG=false
LOG_LEVEL=info
ENVIRONMENT=staging
```

#### `.env.production`
```bash
# Database
SUPABASE_URL=https://your-prod-project.supabase.co
SUPABASE_KEY=your_production_supabase_key
SUPABASE_SERVICE_ROLE_KEY=your_production_service_role_key

# External APIs
HUBSPOT_API_KEY=your_hubspot_production_key
OPENAI_API_KEY=your_openai_key

# Application
DEBUG=false
LOG_LEVEL=warning
ENVIRONMENT=production
SENTRY_DSN=your_sentry_dsn
```

## Local Development

### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/gorgaloro/job-search-automation.git
cd job-search-automation

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run database migrations
python scripts/migrate.py

# Start the application
python main.py
```

## Docker Deployment

### Building Images

```bash
# Build the main application image
docker build -t job-search-automation:latest .

# Build with specific tag
docker build -t job-search-automation:v1.0.0 .

# Build for different architectures
docker buildx build --platform linux/amd64,linux/arm64 -t job-search-automation:latest .
```

### Docker Compose for Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    image: job-search-automation:latest
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env.production
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  redis_data:
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name job-search-automation

# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster job-search-automation \
  --service-name job-search-app \
  --task-definition job-search-automation:1 \
  --desired-count 2
```

#### Task Definition (task-definition.json)
```json
{
  "family": "job-search-automation",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "job-search-app",
      "image": "your-account.dkr.ecr.region.amazonaws.com/job-search-automation:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "SUPABASE_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:supabase-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/job-search-automation",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Platform

#### Using Cloud Run

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/job-search-automation

# Deploy to Cloud Run
gcloud run deploy job-search-automation \
  --image gcr.io/PROJECT_ID/job-search-automation \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production
```

### Heroku Deployment

```bash
# Login to Heroku
heroku login

# Create application
heroku create job-search-automation

# Set environment variables
heroku config:set SUPABASE_URL=your_supabase_url
heroku config:set SUPABASE_KEY=your_supabase_key
heroku config:set HUBSPOT_API_KEY=your_hubspot_key
heroku config:set OPENAI_API_KEY=your_openai_key

# Deploy
git push heroku main

# Scale dynos
heroku ps:scale web=2
```

## Kubernetes Deployment

### Namespace and ConfigMap

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: job-search-automation

---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: job-search-automation
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "info"
```

### Secrets

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: job-search-automation
type: Opaque
data:
  SUPABASE_KEY: <base64-encoded-key>
  HUBSPOT_API_KEY: <base64-encoded-key>
  OPENAI_API_KEY: <base64-encoded-key>
```

### Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: job-search-automation
  namespace: job-search-automation
spec:
  replicas: 3
  selector:
    matchLabels:
      app: job-search-automation
  template:
    metadata:
      labels:
        app: job-search-automation
    spec:
      containers:
      - name: app
        image: job-search-automation:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service and Ingress

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: job-search-automation-service
  namespace: job-search-automation
spec:
  selector:
    app: job-search-automation
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: job-search-automation-ingress
  namespace: job-search-automation
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.job-search-automation.com
    secretName: job-search-automation-tls
  rules:
  - host: api.job-search-automation.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: job-search-automation-service
            port:
              number: 80
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t job-search-automation:${{ github.sha }} .
        docker tag job-search-automation:${{ github.sha }} job-search-automation:latest
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push job-search-automation:${{ github.sha }}
        docker push job-search-automation:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      run: |
        # Add your deployment commands here
        echo "Deploying to production..."
```

## Monitoring and Logging

### Application Monitoring

```python
# monitoring.py
import logging
from prometheus_client import Counter, Histogram, generate_latest
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

# Sentry setup
sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR
)

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[sentry_logging],
    traces_sample_rate=1.0,
)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
```

### Health Checks

```python
# health.py
from fastapi import APIRouter
from supabase import create_client
import redis

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.get("/ready")
async def readiness_check():
    """Readiness check with dependency validation"""
    checks = {}
    
    # Check database
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        supabase.table("companies").select("id").limit(1).execute()
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
    
    # Check Redis
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"
    
    # Check external APIs
    try:
        # Add API health checks here
        checks["external_apis"] = "healthy"
    except Exception as e:
        checks["external_apis"] = f"unhealthy: {str(e)}"
    
    all_healthy = all(status == "healthy" for status in checks.values())
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "timestamp": datetime.utcnow()
    }
```

## Database Migrations

### Migration Scripts

```python
# scripts/migrate.py
import os
from supabase import create_client

def run_migrations():
    """Run database migrations"""
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    )
    
    migrations = [
        "001_create_companies_table.sql",
        "002_create_jobs_table.sql",
        "003_create_resumes_table.sql",
        "004_create_brand_profiles_table.sql",
        "005_create_job_scores_table.sql"
    ]
    
    for migration in migrations:
        with open(f"migrations/{migration}", "r") as f:
            sql = f.read()
            supabase.rpc("execute_sql", {"sql": sql}).execute()
            print(f"Applied migration: {migration}")

if __name__ == "__main__":
    run_migrations()
```

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# scripts/backup.sh

# Backup Supabase database
pg_dump $SUPABASE_DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Upload to S3
aws s3 cp backup_*.sql s3://your-backup-bucket/database/

# Clean up old backups (keep last 30 days)
find . -name "backup_*.sql" -mtime +30 -delete
```

### Disaster Recovery

```bash
#!/bin/bash
# scripts/restore.sh

# Download latest backup
aws s3 cp s3://your-backup-bucket/database/latest.sql ./restore.sql

# Restore database
psql $SUPABASE_DATABASE_URL < restore.sql

# Verify restoration
python scripts/verify_restore.py
```

## Performance Optimization

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_jobs_company_id ON jobs(company_id);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_job_scores_job_id ON job_scores(job_id);
CREATE INDEX idx_job_scores_resume_id ON job_scores(resume_id);

-- Optimize queries
EXPLAIN ANALYZE SELECT * FROM jobs WHERE company_id = 'uuid';
```

### Caching Strategy

```python
# caching.py
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            
            return result
        return wrapper
    return decorator
```

## Security Considerations

### SSL/TLS Configuration

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name api.job-search-automation.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Security Headers

```python
# security.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://job-search-automation.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.job-search-automation.com"]
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check Supabase connection
   python -c "from supabase import create_client; print('Connected')"
   ```

2. **Memory Issues**
   ```bash
   # Monitor memory usage
   docker stats
   
   # Increase memory limits
   docker run -m 2g job-search-automation
   ```

3. **API Rate Limits**
   ```python
   # Implement exponential backoff
   import time
   import random
   
   def retry_with_backoff(func, max_retries=3):
       for attempt in range(max_retries):
           try:
               return func()
           except RateLimitError:
               wait_time = (2 ** attempt) + random.uniform(0, 1)
               time.sleep(wait_time)
       raise Exception("Max retries exceeded")
   ```

### Logs and Debugging

```bash
# View application logs
docker logs job-search-automation

# Follow logs in real-time
docker logs -f job-search-automation

# Check specific service logs
kubectl logs -f deployment/job-search-automation -n job-search-automation
```
