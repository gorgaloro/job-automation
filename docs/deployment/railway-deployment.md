# Railway Production Deployment Guide
## AI Job Search Automation Platform

### 🎯 **Overview**

This guide provides step-by-step instructions for deploying the AI Job Search Automation Platform to Railway, showcasing enterprise-grade deployment practices and production-ready configuration.

---

## 🚀 **Pre-Deployment Checklist**

### **1. Environment Configuration**
- [ ] Copy `config/environments/.env.template` to `.env`
- [ ] Configure all required API keys and database credentials
- [ ] Verify Supabase database is set up and accessible
- [ ] Test OpenAI API key functionality
- [ ] Validate external API integrations (HubSpot, Indeed, GitHub, Canva)

### **2. Code Quality Validation**
- [ ] Run comprehensive test suite: `pytest tests/`
- [ ] Validate code formatting: `black src/ && flake8 src/`
- [ ] Type checking: `mypy src/`
- [ ] Security scan: Review for hardcoded secrets

### **3. Database Preparation**
- [ ] Supabase project created and configured
- [ ] Database schema deployed (see `docs/database/`)
- [ ] Row Level Security policies enabled
- [ ] Service key permissions validated

---

## 🏗️ **Railway Deployment Process**

### **Step 1: Railway Project Setup**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to existing project or create new
railway link
# OR
railway init
```

### **Step 2: Environment Variables Configuration**
Configure the following environment variables in Railway dashboard:

#### **Database Configuration**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
```

#### **AI Services**
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-1106-preview
OPENAI_MAX_TOKENS=4000
```

#### **External Integrations**
```
HUBSPOT_API_KEY=your-hubspot-key
INDEED_PUBLISHER_ID=your-indeed-id
GITHUB_TOKEN=ghp_...
CANVA_CLIENT_ID=your-canva-client-id
CANVA_CLIENT_SECRET=your-canva-secret
```

#### **Application Configuration**
```
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false
JWT_SECRET_KEY=your-secure-jwt-secret
PORT=8080
```

### **Step 3: Deploy Application**
```bash
# Deploy to Railway
railway up

# Monitor deployment
railway logs

# Check deployment status
railway status
```

### **Step 4: Post-Deployment Validation**
```bash
# Test health endpoint
curl https://your-app.up.railway.app/health

# Test API documentation
curl https://your-app.up.railway.app/docs

# Validate core endpoints
curl https://your-app.up.railway.app/api/v1/users/profile
```

---

## 🔧 **Configuration Details**

### **Railway Configuration (`railway.json`)**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn src.api.production_app:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300
  }
}
```

### **Production Dependencies**
The `requirements.txt` includes:
- **FastAPI & Uvicorn:** High-performance async web framework
- **Supabase & AsyncPG:** Database connectivity and ORM
- **OpenAI:** AI integration for scoring and optimization
- **Security:** JWT authentication and password hashing
- **Monitoring:** Logging and metrics collection

---

## 📊 **Monitoring & Observability**

### **Health Checks**
- **Endpoint:** `/health`
- **Timeout:** 300 seconds
- **Restart Policy:** On failure with max 10 retries

### **Logging**
```python
# Structured logging with context
logger.info("API request processed", extra={
    "user_id": user_id,
    "endpoint": "/api/v1/jobs/analyze",
    "response_time": response_time,
    "status_code": 200
})
```

### **Performance Metrics**
- Response time monitoring
- Database query performance
- AI API call latency
- Error rate tracking

---

## 🔒 **Security Best Practices**

### **Environment Security**
- All secrets stored in Railway environment variables
- No hardcoded credentials in source code
- Secure JWT token generation and validation
- CORS properly configured for production domains

### **Database Security**
- Row Level Security (RLS) enabled on all tables
- Service key used only for server-side operations
- Input validation and SQL injection prevention
- Encrypted connections to database

### **API Security**
- JWT-based authentication for all protected endpoints
- Input validation using Pydantic models
- Rate limiting and request throttling
- Comprehensive error handling without information leakage

---

## 🚨 **Troubleshooting**

### **Common Deployment Issues**

#### **Module Import Errors**
```bash
# Ensure proper Python path configuration
export PYTHONPATH="${PYTHONPATH}:/app"
```

#### **Database Connection Issues**
```bash
# Verify database URL format
DATABASE_URL=postgresql://user:password@host:port/database

# Test connection
python -c "import asyncpg; print('AsyncPG available')"
```

#### **Environment Variable Issues**
```bash
# List all environment variables
railway variables

# Set missing variables
railway variables set OPENAI_API_KEY=sk-...
```

### **Performance Optimization**
- Use connection pooling for database operations
- Implement caching for frequently accessed data
- Optimize AI API calls with batching
- Monitor memory usage and optimize as needed

---

## 📈 **Scaling Considerations**

### **Horizontal Scaling**
- Railway auto-scaling based on CPU/memory usage
- Stateless application design for easy scaling
- Database connection pooling for concurrent requests

### **Performance Optimization**
- Async/await patterns for I/O operations
- Background task processing for heavy operations
- Caching strategies for frequently accessed data
- Database query optimization

---

## ✅ **Deployment Success Criteria**

- [ ] Application starts successfully without errors
- [ ] Health check endpoint returns 200 OK
- [ ] API documentation accessible at `/docs`
- [ ] Database connectivity verified
- [ ] All external API integrations functional
- [ ] Authentication system working
- [ ] Core business logic endpoints operational
- [ ] Monitoring and logging active

---

**This deployment guide demonstrates enterprise-grade DevOps practices, showcasing professional deployment workflows and production-ready system architecture.**
