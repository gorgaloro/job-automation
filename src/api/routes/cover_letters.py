#!/usr/bin/env python3
"""
Cover Letter Optimizer API Routes

FastAPI routes for the Cover Letter Optimizer module, providing endpoints for:
- Cover letter generation and optimization
- Integration with Resume Optimizer
- Template and tone management
- Performance analytics and tracking
- Export functionality
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import os
import json
import uuid

# Import core modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.cover_letter_optimizer import (
    CoverLetterOptimizer,
    JobPosting,
    ResumeData, 
    CoverLetterContent,
    CoverLetterTone,
    TemplateType,
    create_job_posting_from_description,
    create_resume_data_from_optimizer
)

# Create router
router = APIRouter(prefix="/api/cover-letters", tags=["cover-letters"])

# Pydantic models for API
class JobPostingRequest(BaseModel):
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    description: str = Field(..., description="Full job description")
    industry: Optional[str] = Field("", description="Industry category")
    role_type: Optional[str] = Field("", description="Role type (technical, management, etc.)")
    requirements: Optional[List[str]] = Field([], description="Explicit requirements")
    preferred_qualifications: Optional[List[str]] = Field([], description="Preferred qualifications")

class CoverLetterGenerateRequest(BaseModel):
    job_posting: JobPostingRequest
    resume_version_id: Optional[str] = Field(None, description="Resume version ID from Resume Optimizer")
    resume_data: Optional[Dict] = Field(None, description="Direct resume data if no version ID")
    template_type: str = Field("technology", description="Template type to use")
    tone: str = Field("professional", description="Tone preference")
    custom_instructions: Optional[str] = Field("", description="Additional customization instructions")

class CoverLetterUpdateRequest(BaseModel):
    opening_paragraph: Optional[str] = None
    body_paragraphs: Optional[List[str]] = None
    closing_paragraph: Optional[str] = None

class CoverLetterResponse(BaseModel):
    id: str
    job_posting: JobPostingRequest
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class CoverLetterSuggestionRequest(BaseModel):
    section_type: str = Field(..., description="Section to enhance: opening, body, closing")
    enhancement_focus: Optional[str] = Field("", description="Specific focus for enhancement")

class ExportRequest(BaseModel):
    format: str = Field("pdf", description="Export format: pdf, docx, txt, email")
    include_resume: bool = Field(False, description="Include optimized resume in export")

# Global optimizer instance
optimizer = None

def get_optimizer():
    """Get or create Cover Letter Optimizer instance"""
    global optimizer
    if optimizer is None:
        openai_key = os.getenv('OPENAI_API_KEY')
        optimizer = CoverLetterOptimizer(openai_api_key=openai_key)
    return optimizer

# In-memory storage for demo (replace with database in production)
cover_letters_db = {}
performance_db = {}

@router.post("/generate", response_model=CoverLetterResponse)
async def generate_cover_letter(request: CoverLetterGenerateRequest):
    """
    Generate a new cover letter optimized for the specific job posting.
    
    Integrates with Resume Optimizer data to create personalized, compelling cover letters
    that align with the optimized resume content.
    """
    try:
        # Get optimizer instance
        opt = get_optimizer()
        
        # Create job posting object
        job_posting = JobPosting(
            title=request.job_posting.title,
            company=request.job_posting.company,
            description=request.job_posting.description,
            requirements=request.job_posting.requirements,
            preferred_qualifications=request.job_posting.preferred_qualifications,
            industry=request.job_posting.industry,
            role_type=request.job_posting.role_type
        )
        
        # Get resume data
        if request.resume_version_id:
            # In production, fetch from Resume Optimizer API
            resume_data = await fetch_resume_data(request.resume_version_id)
        elif request.resume_data:
            resume_data = create_resume_data_from_optimizer(request.resume_data)
        else:
            raise HTTPException(
                status_code=400, 
                detail="Either resume_version_id or resume_data must be provided"
            )
        
        # Parse template and tone
        try:
            template_type = TemplateType(request.template_type.lower())
        except ValueError:
            template_type = TemplateType.TECHNOLOGY
            
        try:
            tone = CoverLetterTone(request.tone.lower())
        except ValueError:
            tone = CoverLetterTone.PROFESSIONAL
        
        # Generate cover letter
        cover_letter = opt.generate_cover_letter(
            job_posting=job_posting,
            resume_data=resume_data,
            template_type=template_type,
            tone=tone,
            custom_instructions=request.custom_instructions
        )
        
        # Create response
        cover_letter_id = str(uuid.uuid4())
        now = datetime.now()
        
        response_data = {
            "id": cover_letter_id,
            "job_posting": request.job_posting,
            "content": {
                "opening_paragraph": cover_letter.opening_paragraph,
                "body_paragraphs": cover_letter.body_paragraphs,
                "closing_paragraph": cover_letter.closing_paragraph
            },
            "metadata": {
                "word_count": cover_letter.word_count,
                "effectiveness_score": cover_letter.effectiveness_score,
                "tone_score": cover_letter.tone_score,
                "keyword_density": cover_letter.keyword_density,
                "template_type": template_type.value,
                "tone": tone.value,
                "resume_version_id": request.resume_version_id
            },
            "created_at": now,
            "updated_at": now
        }
        
        # Store in database
        cover_letters_db[cover_letter_id] = {
            "data": response_data,
            "job_posting_obj": job_posting,
            "resume_data_obj": resume_data,
            "cover_letter_obj": cover_letter
        }
        
        return CoverLetterResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cover letter generation failed: {str(e)}")

@router.get("/{cover_letter_id}", response_model=CoverLetterResponse)
async def get_cover_letter(cover_letter_id: str):
    """Get a specific cover letter by ID"""
    
    if cover_letter_id not in cover_letters_db:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    return CoverLetterResponse(**cover_letters_db[cover_letter_id]["data"])

@router.put("/{cover_letter_id}/content")
async def update_cover_letter_content(cover_letter_id: str, request: CoverLetterUpdateRequest):
    """Update cover letter content with user edits"""
    
    if cover_letter_id not in cover_letters_db:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    # Get existing data
    stored_data = cover_letters_db[cover_letter_id]["data"]
    
    # Update content
    if request.opening_paragraph is not None:
        stored_data["content"]["opening_paragraph"] = request.opening_paragraph
    
    if request.body_paragraphs is not None:
        stored_data["content"]["body_paragraphs"] = request.body_paragraphs
    
    if request.closing_paragraph is not None:
        stored_data["content"]["closing_paragraph"] = request.closing_paragraph
    
    # Recalculate metadata
    full_text = f"{stored_data['content']['opening_paragraph']} {' '.join(stored_data['content']['body_paragraphs'])} {stored_data['content']['closing_paragraph']}"
    stored_data["metadata"]["word_count"] = len(full_text.split())
    stored_data["updated_at"] = datetime.now()
    
    return {"message": "Cover letter updated successfully", "id": cover_letter_id}

@router.post("/{cover_letter_id}/suggestions")
async def generate_ai_suggestions(cover_letter_id: str, request: CoverLetterSuggestionRequest):
    """Generate AI suggestions for improving specific sections"""
    
    if cover_letter_id not in cover_letters_db:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    try:
        # Get stored objects
        stored = cover_letters_db[cover_letter_id]
        job_posting = stored["job_posting_obj"]
        resume_data = stored["resume_data_obj"]
        
        # Generate suggestions based on section type
        opt = get_optimizer()
        
        if request.section_type == "opening":
            suggestions = await generate_opening_suggestions(
                opt, job_posting, resume_data, request.enhancement_focus
            )
        elif request.section_type == "body":
            suggestions = await generate_body_suggestions(
                opt, job_posting, resume_data, request.enhancement_focus
            )
        elif request.section_type == "closing":
            suggestions = await generate_closing_suggestions(
                opt, job_posting, resume_data, request.enhancement_focus
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid section_type")
        
        return {
            "cover_letter_id": cover_letter_id,
            "section_type": request.section_type,
            "suggestions": suggestions,
            "enhancement_focus": request.enhancement_focus
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestion generation failed: {str(e)}")

@router.get("/{cover_letter_id}/export")
async def export_cover_letter(cover_letter_id: str, format: str = "pdf", include_resume: bool = False):
    """Export cover letter in various formats"""
    
    if cover_letter_id not in cover_letters_db:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    try:
        stored_data = cover_letters_db[cover_letter_id]["data"]
        
        if format == "txt":
            # Generate plain text version
            content = stored_data["content"]
            text_content = f"{content['opening_paragraph']}\n\n"
            text_content += "\n\n".join(content['body_paragraphs'])
            text_content += f"\n\n{content['closing_paragraph']}"
            
            # Save to temporary file
            filename = f"cover_letter_{cover_letter_id}.txt"
            filepath = f"/tmp/{filename}"
            
            with open(filepath, 'w') as f:
                f.write(text_content)
            
            return FileResponse(
                path=filepath,
                filename=filename,
                media_type='text/plain'
            )
        
        elif format == "json":
            # Return JSON format
            return stored_data
        
        elif format == "email":
            # Generate email template
            content = stored_data["content"]
            job_info = stored_data["job_posting"]
            
            email_template = {
                "subject": f"Application for {job_info['title']} Position",
                "body": f"Dear Hiring Manager,\n\n{content['opening_paragraph']}\n\n" + 
                       "\n\n".join(content['body_paragraphs']) + 
                       f"\n\n{content['closing_paragraph']}\n\nBest regards,\n[Your Name]",
                "attachments": ["resume.pdf"] if include_resume else []
            }
            
            return email_template
        
        else:
            # For PDF/DOCX, return placeholder (implement with actual document generation)
            return {
                "message": f"Export to {format} format",
                "download_url": f"/api/cover-letters/{cover_letter_id}/download?format={format}",
                "include_resume": include_resume
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/analytics/performance")
async def get_performance_analytics(period: str = "monthly"):
    """Get cover letter performance analytics"""
    
    # Mock analytics data (replace with actual database queries)
    analytics = {
        "period": period,
        "total_letters_generated": len(cover_letters_db),
        "average_effectiveness_score": 0.87,
        "most_popular_template": "technology",
        "most_popular_tone": "professional",
        "top_performing_combinations": [
            {"template": "healthcare", "tone": "professional", "avg_score": 0.92},
            {"template": "technology", "tone": "analytical", "avg_score": 0.89},
            {"template": "startup", "tone": "enthusiastic", "avg_score": 0.85}
        ],
        "keyword_effectiveness": {
            "ai": 0.94,
            "healthcare": 0.91,
            "management": 0.88,
            "leadership": 0.86
        },
        "improvement_suggestions": [
            "Consider using healthcare template for medical technology roles",
            "Analytical tone performs well for technical positions",
            "Include more industry-specific keywords for better alignment"
        ]
    }
    
    return analytics

@router.post("/sync-resume")
async def sync_with_resume_optimizer(cover_letter_id: str, resume_version_id: str):
    """Sync cover letter with updated resume data from Resume Optimizer"""
    
    if cover_letter_id not in cover_letters_db:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    try:
        # Fetch updated resume data
        updated_resume_data = await fetch_resume_data(resume_version_id)
        
        # Get existing cover letter data
        stored = cover_letters_db[cover_letter_id]
        job_posting = stored["job_posting_obj"]
        
        # Regenerate cover letter with updated resume data
        opt = get_optimizer()
        template_type = TemplateType(stored["data"]["metadata"]["template_type"])
        tone = CoverLetterTone(stored["data"]["metadata"]["tone"])
        
        updated_cover_letter = opt.generate_cover_letter(
            job_posting=job_posting,
            resume_data=updated_resume_data,
            template_type=template_type,
            tone=tone
        )
        
        # Update stored data
        stored["data"]["content"] = {
            "opening_paragraph": updated_cover_letter.opening_paragraph,
            "body_paragraphs": updated_cover_letter.body_paragraphs,
            "closing_paragraph": updated_cover_letter.closing_paragraph
        }
        stored["data"]["metadata"].update({
            "word_count": updated_cover_letter.word_count,
            "effectiveness_score": updated_cover_letter.effectiveness_score,
            "tone_score": updated_cover_letter.tone_score,
            "keyword_density": updated_cover_letter.keyword_density,
            "resume_version_id": resume_version_id
        })
        stored["data"]["updated_at"] = datetime.now()
        stored["resume_data_obj"] = updated_resume_data
        stored["cover_letter_obj"] = updated_cover_letter
        
        return {
            "message": "Cover letter synced with updated resume",
            "cover_letter_id": cover_letter_id,
            "resume_version_id": resume_version_id,
            "new_effectiveness_score": updated_cover_letter.effectiveness_score
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.get("/templates")
async def get_available_templates():
    """Get list of available cover letter templates"""
    
    templates = [
        {
            "id": "technology",
            "name": "Technology",
            "description": "Modern, results-focused template for tech roles",
            "best_for": ["Software Engineer", "Product Manager", "Data Scientist"],
            "tone_recommendations": ["professional", "analytical"]
        },
        {
            "id": "healthcare", 
            "name": "Healthcare",
            "description": "Professional template emphasizing patient care and compliance",
            "best_for": ["Healthcare IT", "Clinical Manager", "Medical Device"],
            "tone_recommendations": ["professional", "formal"]
        },
        {
            "id": "startup",
            "name": "Startup",
            "description": "Entrepreneurial template highlighting adaptability and growth",
            "best_for": ["Startup Roles", "Growth Manager", "Business Development"],
            "tone_recommendations": ["enthusiastic", "conversational"]
        },
        {
            "id": "enterprise",
            "name": "Enterprise", 
            "description": "Formal template for large corporation roles",
            "best_for": ["Enterprise Sales", "Program Manager", "Executive"],
            "tone_recommendations": ["formal", "professional"]
        }
    ]
    
    return {"templates": templates}

@router.get("/tones")
async def get_available_tones():
    """Get list of available cover letter tones"""
    
    tones = [
        {
            "id": "professional",
            "name": "Professional",
            "description": "Balanced, professional tone suitable for most roles",
            "characteristics": ["Clear", "Confident", "Respectful"]
        },
        {
            "id": "enthusiastic",
            "name": "Enthusiastic", 
            "description": "Energetic tone showing passion and excitement",
            "characteristics": ["Energetic", "Passionate", "Engaging"]
        },
        {
            "id": "analytical",
            "name": "Analytical",
            "description": "Data-focused tone emphasizing logic and results",
            "characteristics": ["Logical", "Results-driven", "Precise"]
        },
        {
            "id": "formal",
            "name": "Formal",
            "description": "Traditional, formal tone for conservative industries",
            "characteristics": ["Traditional", "Respectful", "Conservative"]
        },
        {
            "id": "conversational",
            "name": "Conversational",
            "description": "Friendly, approachable tone for modern companies",
            "characteristics": ["Friendly", "Approachable", "Personal"]
        }
    ]
    
    return {"tones": tones}

# Helper functions
async def fetch_resume_data(resume_version_id: str) -> ResumeData:
    """Fetch resume data from Resume Optimizer (mock implementation)"""
    
    # In production, this would call the Resume Optimizer API
    # For demo, return sample data
    return ResumeData(
        executive_summary="Sample executive summary from Resume Optimizer",
        selected_experience=[
            {"title": "Sample Role", "company": "Sample Company", "description": "Sample description"}
        ],
        selected_skills=["Python", "AI/ML", "Project Management"],
        selected_achievements=["Sample achievement 1", "Sample achievement 2"],
        ai_suggestions=[{"text": "Sample AI suggestion", "relevance_score": 0.9}],
        optimization_score=0.85
    )

async def generate_opening_suggestions(optimizer, job_posting, resume_data, focus):
    """Generate suggestions for opening paragraph"""
    
    suggestions = [
        {
            "text": f"I am excited to apply for the {job_posting.title} position at {job_posting.company}, where I can leverage my expertise in {resume_data.selected_skills[0] if resume_data.selected_skills else 'relevant areas'}.",
            "reasoning": "Emphasizes enthusiasm and relevant expertise",
            "effectiveness_score": 0.88
        },
        {
            "text": f"With {len(resume_data.selected_experience)} years of experience in {job_posting.industry}, I am well-positioned to contribute to {job_posting.company}'s {job_posting.title} role.",
            "reasoning": "Highlights experience and industry alignment",
            "effectiveness_score": 0.85
        },
        {
            "text": f"Your {job_posting.title} opportunity at {job_posting.company} perfectly aligns with my background in {resume_data.selected_skills[0] if resume_data.selected_skills else 'technology'} and passion for {job_posting.industry}.",
            "reasoning": "Shows alignment between role and candidate background",
            "effectiveness_score": 0.90
        }
    ]
    
    return suggestions

async def generate_body_suggestions(optimizer, job_posting, resume_data, focus):
    """Generate suggestions for body paragraphs"""
    
    suggestions = [
        {
            "text": f"In my previous role, I {resume_data.selected_achievements[0] if resume_data.selected_achievements else 'delivered significant results'}, which directly relates to the requirements outlined in your job posting.",
            "reasoning": "Connects past achievements to job requirements",
            "effectiveness_score": 0.92
        },
        {
            "text": f"My expertise in {', '.join(resume_data.selected_skills[:3])} positions me well to tackle the challenges facing {job_posting.company} in the {job_posting.industry} sector.",
            "reasoning": "Highlights relevant skills and industry knowledge",
            "effectiveness_score": 0.87
        }
    ]
    
    return suggestions

async def generate_closing_suggestions(optimizer, job_posting, resume_data, focus):
    """Generate suggestions for closing paragraph"""
    
    suggestions = [
        {
            "text": f"I would welcome the opportunity to discuss how my experience in {resume_data.selected_skills[0] if resume_data.selected_skills else 'relevant areas'} can contribute to {job_posting.company}'s continued success.",
            "reasoning": "Professional closing with specific value proposition",
            "effectiveness_score": 0.89
        },
        {
            "text": f"Thank you for considering my application. I look forward to the possibility of bringing my {job_posting.industry} expertise to the {job_posting.title} role at {job_posting.company}.",
            "reasoning": "Grateful and forward-looking closing",
            "effectiveness_score": 0.86
        }
    ]
    
    return suggestions
