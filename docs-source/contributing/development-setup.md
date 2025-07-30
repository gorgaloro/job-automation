# 🤝 Contributing to Job Search Automation Platform

Thank you for your interest in contributing to the Job Search Automation Platform! This document provides guidelines and information for contributors.

## 🌟 Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful, constructive, and professional in all interactions.

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Git
- Docker (optional but recommended)
- Supabase account (for database access)
- HubSpot developer account (for CRM integration)
- OpenAI API key (for AI features)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/job-search-automation.git
   cd job-search-automation
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Set Up Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

5. **Configure Environment**
   ```bash
   cp .env.template .env
   # Edit .env with your development credentials
   ```

6. **Run Tests**
   ```bash
   pytest
   ```

## 📋 Development Workflow

### Branch Naming Convention

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test improvements

### Commit Message Format

```
type(scope): brief description

Detailed explanation of changes (if needed)

Closes #issue-number
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Maintenance tasks

**Examples:**
```
feat(resume): add AI-powered resume optimization
fix(scoring): resolve job matching algorithm bug
docs(api): update API reference documentation
```

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_resume_optimizer.py

# Run tests with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the source code structure
- Use descriptive test names
- Include both positive and negative test cases
- Mock external API calls

**Example Test:**
```python
import pytest
from unittest.mock import Mock, patch
from src.resume_optimizer import ResumeOptimizer

class TestResumeOptimizer:
    def setup_method(self):
        self.optimizer = ResumeOptimizer()
    
    def test_optimize_resume_success(self):
        # Arrange
        resume_data = {"experience": ["Python developer"]}
        job_data = {"requirements": ["Python", "Django"]}
        
        # Act
        result = self.optimizer.optimize(resume_data, job_data)
        
        # Assert
        assert result["score"] > 0
        assert "optimized_content" in result
    
    @patch('src.resume_optimizer.openai_client')
    def test_optimize_resume_api_error(self, mock_openai):
        # Arrange
        mock_openai.side_effect = Exception("API Error")
        
        # Act & Assert
        with pytest.raises(Exception):
            self.optimizer.optimize({}, {})
```

## 📝 Code Style Guidelines

### Python Style

We follow PEP 8 with some modifications:

- Line length: 88 characters (Black default)
- Use type hints for all functions
- Use docstrings for all public functions and classes
- Prefer f-strings for string formatting

### Code Formatting

We use automated formatting tools:

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy .
```

### Documentation Style

```python
def optimize_resume(resume_data: dict, job_data: dict) -> dict:
    """
    Optimize a resume for a specific job posting.
    
    Args:
        resume_data: Dictionary containing resume content and metadata
        job_data: Dictionary containing job description and requirements
        
    Returns:
        Dictionary containing optimized resume and scoring information
        
    Raises:
        ValueError: If resume_data or job_data is invalid
        APIError: If external API calls fail
        
    Example:
        >>> resume = {"experience": ["Python developer"]}
        >>> job = {"requirements": ["Python", "Django"]}
        >>> result = optimize_resume(resume, job)
        >>> print(result["score"])
        85
    """
```

## 🏗️ Architecture Guidelines

### Project Structure

```
src/
├── core/                   # Core business logic
│   ├── models/            # Data models
│   ├── services/          # Business services
│   └── utils/             # Utility functions
├── integrations/          # External API integrations
│   ├── hubspot/          # HubSpot CRM integration
│   ├── openai/           # OpenAI API integration
│   └── supabase/         # Database integration
├── api/                   # API endpoints
│   ├── routes/           # Route definitions
│   ├── middleware/       # Custom middleware
│   └── schemas/          # Request/response schemas
└── tests/                 # Test files
```

### Design Principles

1. **Single Responsibility**: Each class/function should have one reason to change
2. **Dependency Injection**: Use dependency injection for external services
3. **Error Handling**: Implement comprehensive error handling
4. **Logging**: Add appropriate logging for debugging and monitoring
5. **Configuration**: Use environment variables for configuration

### Database Guidelines

- Use migrations for schema changes
- Include proper indexes for performance
- Use transactions for data consistency
- Implement soft deletes where appropriate

## 🔧 API Development

### Endpoint Guidelines

- Use RESTful conventions
- Include proper HTTP status codes
- Implement request validation
- Add comprehensive error responses
- Include rate limiting

### Example Endpoint

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

class JobCreate(BaseModel):
    title: str
    company_id: str
    description: str
    requirements: List[str]

class JobResponse(BaseModel):
    id: str
    title: str
    company_name: str
    created_at: datetime

@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new job posting."""
    try:
        job = await job_service.create_job(job_data, current_user.id)
        return JobResponse(**job.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## 🤖 AI/ML Guidelines

### OpenAI Integration

- Use structured prompts with clear instructions
- Implement retry logic with exponential backoff
- Cache responses when appropriate
- Monitor token usage and costs

### Example AI Service

```python
import openai
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    async def score_resume_job_fit(
        self, 
        resume_content: str, 
        job_description: str
    ) -> Dict[str, Any]:
        """Score how well a resume fits a job description."""
        
        prompt = f"""
        Analyze the following resume and job description to determine fit score.
        
        Resume:
        {resume_content}
        
        Job Description:
        {job_description}
        
        Provide a JSON response with:
        - score: integer from 0-100
        - rationale: brief explanation
        - missing_skills: list of missing requirements
        - strengths: list of matching qualifications
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"AI scoring failed: {e}")
            raise AIServiceError(f"Failed to score resume: {e}")
```

## 📊 Performance Guidelines

### Database Optimization

- Use appropriate indexes
- Implement query optimization
- Use connection pooling
- Monitor slow queries

### Caching Strategy

- Cache expensive computations
- Use Redis for session storage
- Implement cache invalidation
- Monitor cache hit rates

### API Performance

- Implement pagination for large datasets
- Use async/await for I/O operations
- Add request/response compression
- Monitor response times

## 🔒 Security Guidelines

### Authentication & Authorization

- Use JWT tokens for authentication
- Implement role-based access control
- Validate all user inputs
- Use HTTPS for all communications

### Data Protection

- Encrypt sensitive data at rest
- Use environment variables for secrets
- Implement audit logging
- Follow GDPR compliance requirements

### API Security

- Implement rate limiting
- Use CORS appropriately
- Validate request schemas
- Sanitize user inputs

## 📚 Documentation Guidelines

### Code Documentation

- Write clear docstrings for all public functions
- Include type hints
- Provide usage examples
- Document complex algorithms

### API Documentation

- Use OpenAPI/Swagger specifications
- Include request/response examples
- Document error responses
- Provide SDK examples

### User Documentation

- Write clear setup instructions
- Include troubleshooting guides
- Provide usage examples
- Keep documentation up to date

## 🚀 Deployment Guidelines

### Environment Management

- Use separate environments (dev, staging, prod)
- Implement proper secret management
- Use infrastructure as code
- Monitor deployment health

### CI/CD Pipeline

- Run tests on all pull requests
- Implement automated deployments
- Use blue-green deployments
- Monitor deployment metrics

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Detailed steps to reproduce the bug
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, Python version, dependencies
6. **Logs**: Relevant error messages or logs

## 💡 Feature Requests

When requesting features, please include:

1. **Problem Statement**: What problem does this solve?
2. **Proposed Solution**: How should it work?
3. **Use Cases**: Who would use this feature?
4. **Alternatives**: Other solutions considered
5. **Implementation Ideas**: Technical approach (if applicable)

## 📋 Pull Request Process

1. **Create Feature Branch**: Branch from `main`
2. **Implement Changes**: Follow coding guidelines
3. **Write Tests**: Ensure good test coverage
4. **Update Documentation**: Update relevant docs
5. **Run Tests**: Ensure all tests pass
6. **Submit PR**: Create pull request with clear description
7. **Code Review**: Address reviewer feedback
8. **Merge**: Maintainer will merge after approval

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated existing tests

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributor graphs
- Special mentions for outstanding contributions

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Email**: For security issues or private matters
- **Documentation**: Check docs/ directory first

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to the Job Search Automation Platform! Your contributions help make job searching more efficient and effective for everyone. 🚀
