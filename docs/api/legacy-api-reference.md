# 📚 API Reference

## Overview

The Job Search Automation Platform provides a comprehensive REST API for managing jobs, companies, resumes, and AI-powered scoring. All endpoints return JSON responses and use standard HTTP status codes.

## Base URL
```
https://api.job-search-automation.com/v1
```

## Authentication

All API requests require authentication using Bearer tokens:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
     https://api.job-search-automation.com/v1/jobs
```

## Rate Limiting

- **Standard Users**: 1000 requests per hour
- **Premium Users**: 5000 requests per hour
- **Enterprise**: Custom limits

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Companies API

### List Companies
```http
GET /companies
```

**Parameters:**
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)
- `industry` (string): Filter by industry
- `size` (string): Filter by company size (startup, small, medium, large, enterprise)

**Response:**
```json
{
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "TechCorp Inc",
      "domain": "techcorp.com",
      "website": "https://techcorp.com",
      "industry": "Technology",
      "employees": 5000,
      "city": "San Francisco",
      "state": "CA",
      "country": "US",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
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

### Create Company
```http
POST /companies
```

**Request Body:**
```json
{
  "name": "TechCorp Inc",
  "domain": "techcorp.com",
  "website": "https://techcorp.com",
  "industry": "Technology",
  "employees": 5000,
  "city": "San Francisco",
  "state": "CA",
  "country": "US"
}
```

**Response:** `201 Created`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "TechCorp Inc",
  "domain": "techcorp.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Company
```http
GET /companies/{id}
```

**Response:** `200 OK`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "TechCorp Inc",
  "domain": "techcorp.com",
  "website": "https://techcorp.com",
  "industry": "Technology",
  "employees": 5000,
  "jobs_count": 15,
  "tech_stack": ["Python", "React", "PostgreSQL"],
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Jobs API

### List Jobs
```http
GET /jobs
```

**Parameters:**
- `page` (integer): Page number
- `limit` (integer): Items per page
- `company_id` (uuid): Filter by company
- `title` (string): Search in job titles
- `location` (string): Filter by location
- `salary_min` (integer): Minimum salary
- `salary_max` (integer): Maximum salary
- `remote` (boolean): Remote jobs only

**Response:**
```json
{
  "data": [
    {
      "id": "456e7890-e89b-12d3-a456-426614174001",
      "title": "Senior Python Developer",
      "company": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "TechCorp Inc",
        "domain": "techcorp.com"
      },
      "location": "San Francisco, CA",
      "salary_min": 120000,
      "salary_max": 180000,
      "remote": true,
      "job_board_url": "https://techcorp.com/careers/senior-python",
      "description": "We are looking for a Senior Python Developer...",
      "requirements": ["5+ years Python", "Django/Flask", "PostgreSQL"],
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 500,
    "pages": 25
  }
}
```

### Create Job
```http
POST /jobs
```

**Request Body:**
```json
{
  "title": "Senior Python Developer",
  "company_id": "123e4567-e89b-12d3-a456-426614174000",
  "location": "San Francisco, CA",
  "salary_min": 120000,
  "salary_max": 180000,
  "remote": true,
  "job_board_url": "https://techcorp.com/careers/senior-python",
  "description": "We are looking for a Senior Python Developer...",
  "requirements": ["5+ years Python", "Django/Flask", "PostgreSQL"]
}
```

**Response:** `201 Created`

### Parse Job from URL
```http
POST /jobs/parse
```

**Request Body:**
```json
{
  "url": "https://techcorp.com/careers/senior-python",
  "auto_create": true
}
```

**Response:** `200 OK`
```json
{
  "job": {
    "title": "Senior Python Developer",
    "company_name": "TechCorp Inc",
    "location": "San Francisco, CA",
    "description": "Parsed job description...",
    "requirements": ["Extracted requirements..."]
  },
  "confidence": 0.95,
  "created": true,
  "job_id": "456e7890-e89b-12d3-a456-426614174001"
}
```

## Resumes API

### List Resumes
```http
GET /resumes
```

**Response:**
```json
{
  "data": [
    {
      "id": "789e0123-e89b-12d3-a456-426614174002",
      "version": "software-engineer-v1",
      "title": "Software Engineer Resume",
      "tags": ["python", "backend", "api"],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Upload Resume
```http
POST /resumes
```

**Request:** `multipart/form-data`
- `file`: Resume file (PDF, DOCX, or TXT)
- `version`: Version identifier
- `tags`: Comma-separated tags

**Response:** `201 Created`
```json
{
  "id": "789e0123-e89b-12d3-a456-426614174002",
  "version": "software-engineer-v1",
  "parsed_content": {
    "name": "John Doe",
    "email": "john@example.com",
    "experience": [...],
    "skills": [...],
    "education": [...]
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Optimize Resume for Job
```http
POST /resumes/{id}/optimize
```

**Request Body:**
```json
{
  "job_id": "456e7890-e89b-12d3-a456-426614174001",
  "optimization_level": "aggressive",
  "preserve_sections": ["contact", "education"]
}
```

**Response:** `200 OK`
```json
{
  "optimized_resume": {
    "id": "789e0123-e89b-12d3-a456-426614174003",
    "version": "software-engineer-v1-optimized",
    "changes": [
      {
        "section": "experience",
        "change_type": "bullet_rewrite",
        "original": "Developed web applications",
        "optimized": "Built scalable Python web applications serving 10k+ users"
      }
    ]
  },
  "score_improvement": 15,
  "processing_time": 2.3
}
```

## AI Scoring API

### Score Resume Against Job
```http
POST /scoring/resume-job
```

**Request Body:**
```json
{
  "resume_id": "789e0123-e89b-12d3-a456-426614174002",
  "job_id": "456e7890-e89b-12d3-a456-426614174001"
}
```

**Response:** `200 OK`
```json
{
  "score": 85,
  "rationale": "Strong match for Python skills and backend experience. Missing some DevOps requirements.",
  "breakdown": {
    "skills_match": 90,
    "experience_level": 85,
    "industry_fit": 80,
    "location_preference": 95
  },
  "recommendations": [
    "Highlight Docker/Kubernetes experience",
    "Emphasize API development projects"
  ],
  "processing_time": 1.2
}
```

### Score Company Culture Fit
```http
POST /scoring/company-culture
```

**Request Body:**
```json
{
  "company_id": "123e4567-e89b-12d3-a456-426614174000",
  "brand_profile_id": "abc12345-e89b-12d3-a456-426614174003"
}
```

**Response:** `200 OK`
```json
{
  "score": 78,
  "rationale": "Good alignment with innovation focus and startup culture preferences.",
  "factors": {
    "company_size": 85,
    "industry_alignment": 90,
    "values_match": 70,
    "growth_stage": 80
  }
}
```

## Brand Profile API

### Create Brand Profile
```http
POST /brand-profiles
```

**Request Body:**
```json
{
  "interview_responses": [
    {
      "question": "What type of work environment energizes you?",
      "response": "I thrive in collaborative, fast-paced environments..."
    }
  ],
  "voice_recording_url": "https://storage.com/interview.mp3"
}
```

**Response:** `201 Created`
```json
{
  "id": "abc12345-e89b-12d3-a456-426614174003",
  "version": 1,
  "profile": {
    "summary": "Innovative software engineer passionate about...",
    "preferred_industries": ["Technology", "Healthcare"],
    "work_style": "collaborative",
    "motivators": ["innovation", "impact", "growth"],
    "deal_breakers": ["micromanagement", "legacy_tech"]
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Recommendations
```http
GET /brand-profiles/{id}/recommendations
```

**Parameters:**
- `type` (string): "jobs" or "companies"
- `limit` (integer): Number of recommendations

**Response:** `200 OK`
```json
{
  "recommendations": [
    {
      "item": {
        "id": "456e7890-e89b-12d3-a456-426614174001",
        "title": "Senior Python Developer",
        "company": "TechCorp Inc"
      },
      "score": 92,
      "rationale": "Perfect match for your Python expertise and startup preference"
    }
  ]
}
```

## Application Tracking API

### Track Application
```http
POST /applications
```

**Request Body:**
```json
{
  "job_id": "456e7890-e89b-12d3-a456-426614174001",
  "resume_id": "789e0123-e89b-12d3-a456-426614174002",
  "application_method": "direct",
  "application_url": "https://techcorp.com/apply/12345",
  "cover_letter": "Dear Hiring Manager...",
  "notes": "Applied through company website"
}
```

**Response:** `201 Created`
```json
{
  "id": "def45678-e89b-12d3-a456-426614174004",
  "status": "applied",
  "applied_at": "2024-01-15T10:30:00Z",
  "hubspot_deal_id": "12345678"
}
```

### Update Application Status
```http
PATCH /applications/{id}
```

**Request Body:**
```json
{
  "status": "interview_scheduled",
  "notes": "Phone screen scheduled for Friday",
  "interview_date": "2024-01-20T14:00:00Z"
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

## SDKs and Libraries

### Python SDK
```bash
pip install job-search-automation-sdk
```

```python
from job_search_automation import Client

client = Client(api_key="your_api_key")

# Create a job
job = client.jobs.create({
    "title": "Senior Python Developer",
    "company_id": "123e4567-e89b-12d3-a456-426614174000"
})

# Score resume against job
score = client.scoring.resume_job(
    resume_id="789e0123-e89b-12d3-a456-426614174002",
    job_id=job.id
)
```

### JavaScript SDK
```bash
npm install job-search-automation-js
```

```javascript
import { JobSearchClient } from 'job-search-automation-js';

const client = new JobSearchClient({ apiKey: 'your_api_key' });

// Upload resume
const resume = await client.resumes.upload({
  file: resumeFile,
  version: 'software-engineer-v1'
});

// Get recommendations
const recommendations = await client.brandProfiles.getRecommendations(
  profileId,
  { type: 'jobs', limit: 10 }
);
```

## Webhooks

Configure webhooks to receive real-time notifications:

### Webhook Events
- `application.status_changed`
- `job.created`
- `resume.optimized`
- `score.calculated`

### Webhook Payload Example
```json
{
  "event": "application.status_changed",
  "data": {
    "application_id": "def45678-e89b-12d3-a456-426614174004",
    "old_status": "applied",
    "new_status": "interview_scheduled",
    "changed_at": "2024-01-15T10:30:00Z"
  },
  "webhook_id": "wh_123456789"
}
```
