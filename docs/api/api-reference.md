# 🚀 AI Job Search Automation Platform - API Reference

## Overview

The AI Job Search Automation Platform provides a comprehensive REST API for managing jobs, companies, resumes, and AI-powered scoring. Built with FastAPI, all endpoints return JSON responses and use standard HTTP status codes.

## Base URL

```text
# Development
http://localhost:8081/api/v1

# Production
https://job-automation-production.up.railway.app/api/v1
```

## Authentication

All API requests require authentication using Bearer tokens:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
     http://localhost:8081/api/v1/jobs
```

## Interactive Documentation

- **Swagger UI**: `http://localhost:8081/docs`
- **ReDoc**: `http://localhost:8081/redoc`

## Core Endpoints

### Health Check

```http
GET /health
```

**Response**: `200 OK`

```json
{
  "status": "healthy",
  "timestamp": "2025-07-30T19:56:54.614663",
  "environment": "development",
  "version": "1.0.0"
}
```

### Jobs API

#### List Jobs

```http
GET /api/v1/jobs
```

**Parameters**:

- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)
- `company` (string): Filter by company name
- `location` (string): Filter by location
- `remote` (boolean): Remote jobs only

**Response**: `200 OK`

```json
{
  "jobs": [
    {
      "id": "job_123",
      "title": "Senior Python Developer",
      "company": "TechCorp Inc",
      "location": "San Francisco, CA",
      "salary_range": "$120k - $180k",
      "remote": true,
      "posted_date": "2025-07-30",
      "description": "We are looking for a Senior Python Developer...",
      "requirements": ["5+ years Python", "FastAPI", "PostgreSQL"]
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

#### Create Job

```http
POST /api/v1/jobs
```

**Request Body**:

```json
{
  "title": "Senior Python Developer",
  "company": "TechCorp Inc",
  "location": "San Francisco, CA",
  "salary_min": 120000,
  "salary_max": 180000,
  "remote": true,
  "description": "We are looking for a Senior Python Developer...",
  "requirements": ["5+ years Python", "FastAPI", "PostgreSQL"]
}
```

**Response**: `201 Created`

```json
{
  "id": "job_123",
  "title": "Senior Python Developer",
  "company": "TechCorp Inc",
  "created_at": "2025-07-30T19:56:54Z"
}
```

#### Get Job Details

```http
GET /api/v1/jobs/{job_id}
```

**Response**: `200 OK`

```json
{
  "id": "job_123",
  "title": "Senior Python Developer",
  "company": "TechCorp Inc",
  "location": "San Francisco, CA",
  "salary_range": "$120k - $180k",
  "remote": true,
  "description": "We are looking for a Senior Python Developer...",
  "requirements": ["5+ years Python", "FastAPI", "PostgreSQL"],
  "ai_score": 85,
  "created_at": "2025-07-30T19:56:54Z"
}
```

### AI Scoring API

#### Score Job Match

```http
POST /api/v1/jobs/{job_id}/score
```

**Request Body**:

```json
{
  "resume_content": "Your resume content here...",
  "candidate_preferences": {
    "preferred_location": "San Francisco, CA",
    "salary_expectation": 150000,
    "remote_preference": true
  }
}
```

**Response**: `200 OK`

```json
{
  "overall_score": 85,
  "breakdown": {
    "skills_match": 90,
    "experience_level": 85,
    "location_fit": 95,
    "salary_alignment": 80
  },
  "rationale": "Strong match for Python skills and backend experience. Excellent location and remote work alignment.",
  "recommendations": [
    "Highlight your FastAPI experience",
    "Emphasize your PostgreSQL expertise",
    "Mention any startup experience"
  ]
}
```

### Resume Optimization API

#### Optimize Resume

```http
POST /api/v1/resume/optimize
```

**Request Body**:

```json
{
  "resume_content": "Your current resume content...",
  "target_job_description": "Job description to optimize for...",
  "optimization_level": "aggressive"
}
```

**Response**: `200 OK`

```json
{
  "optimized_resume": "Your optimized resume content...",
  "changes_made": [
    "Added relevant keywords for Python development",
    "Emphasized FastAPI experience",
    "Quantified achievements with metrics"
  ],
  "improvement_score": 25,
  "original_score": 65,
  "optimized_score": 90
}
```

### Analytics API

#### Get Dashboard Data

```http
GET /api/v1/analytics/dashboard
```

**Response**: `200 OK`

```json
{
  "total_jobs": 1250,
  "applications_sent": 45,
  "interviews_scheduled": 8,
  "offers_received": 2,
  "average_response_rate": 18.5,
  "top_companies": [
    {"name": "TechCorp", "applications": 5},
    {"name": "StartupXYZ", "applications": 3}
  ],
  "recent_activity": [
    {
      "type": "application_sent",
      "company": "TechCorp",
      "position": "Senior Python Developer",
      "date": "2025-07-30"
    }
  ]
}
```

### Company Enrichment API

#### Get Company Profile

```http
GET /api/v1/companies/{company_name}/profile
```

**Response**: `200 OK`

```json
{
  "name": "TechCorp Inc",
  "domain": "techcorp.com",
  "industry": "Technology",
  "size": "1000-5000 employees",
  "location": "San Francisco, CA",
  "culture_insights": {
    "work_life_balance": 4.2,
    "career_growth": 4.0,
    "compensation": 4.5,
    "company_culture": 4.1
  },
  "tech_stack": ["Python", "React", "PostgreSQL", "AWS"],
  "recent_news": [
    "TechCorp raises $50M Series B funding",
    "New AI initiative launched"
  ]
}
```

## Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    },
    "request_id": "req_123456789"
  }
}
```

### Common Error Codes

- `400 BAD_REQUEST`: Invalid request parameters
- `401 UNAUTHORIZED`: Invalid or missing authentication
- `403 FORBIDDEN`: Insufficient permissions
- `404 NOT_FOUND`: Resource not found
- `429 RATE_LIMITED`: Too many requests
- `500 INTERNAL_ERROR`: Server error

## Rate Limiting

- **Development**: Unlimited requests
- **Production**: 1000 requests per hour per API key
- **Enterprise**: Custom limits available

Rate limit headers are included in all responses:

```text
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## SDKs and Integration

### Python SDK

```bash
pip install job-search-automation-sdk
```

```python
from job_search_automation import Client

client = Client(api_key="your_api_key", base_url="http://localhost:8081")

# Get job recommendations
jobs = client.jobs.list(remote=True, location="San Francisco")

# Score a job match
score = client.scoring.score_job(
    job_id="job_123",
    resume_content="Your resume...",
    preferences={"remote": True}
)

# Optimize resume
optimized = client.resume.optimize(
    content="Your resume...",
    target_job="Job description..."
)
```

### JavaScript/TypeScript SDK

```bash
npm install @job-automation/sdk
```

```typescript
import { JobAutomationClient } from '@job-automation/sdk';

const client = new JobAutomationClient({
  apiKey: 'your_api_key',
  baseUrl: 'http://localhost:8081'
});

// Get jobs
const jobs = await client.jobs.list({ remote: true });

// Score job match
const score = await client.scoring.scoreJob('job_123', {
  resumeContent: 'Your resume...',
  preferences: { remote: true }
});
```

## Webhooks

Configure webhooks to receive real-time notifications:

### Webhook Events

- `job.created` - New job added to system
- `application.status_changed` - Application status updated
- `score.calculated` - AI scoring completed
- `resume.optimized` - Resume optimization completed

### Webhook Configuration

```http
POST /api/v1/webhooks
```

**Request Body**:

```json
{
  "url": "https://your-app.com/webhooks/job-automation",
  "events": ["job.created", "score.calculated"],
  "secret": "your_webhook_secret"
}
```

### Webhook Payload Example

```json
{
  "event": "job.created",
  "data": {
    "job_id": "job_123",
    "title": "Senior Python Developer",
    "company": "TechCorp Inc",
    "created_at": "2025-07-30T19:56:54Z"
  },
  "webhook_id": "wh_123456789",
  "timestamp": "2025-07-30T19:56:54Z"
}
```

## Getting Started

1. **Start the development server**:
   ```bash
   cd /Users/allenwalker/Desktop/job-automation-clean
   python main.py
   ```

2. **Access interactive documentation**:
   - Open `http://localhost:8081/docs` in your browser
   - Explore and test all endpoints interactively

3. **Test the health endpoint**:
   ```bash
   curl http://localhost:8081/health
   ```

4. **View analytics dashboard**:
   ```bash
   curl http://localhost:8081/api/v1/analytics/dashboard
   ```

## Support

- **Documentation**: [Full Documentation](../README.md)
- **Issues**: [GitHub Issues](https://github.com/gorgaloro/job-automation/issues)
- **API Status**: [Status Page](https://job-automation-production.up.railway.app/health)

---

**Built with FastAPI, Python 3.9+, and enterprise-grade architecture principles.**
