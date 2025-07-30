#!/usr/bin/env python3
"""
Application Submission Module

Handles the final stage of job application pipeline, transforming optimized content
into submission-ready formats for both API-based and manual workflows.

Key Features:
- Content validation and constraint checking
- Graphic template generation (PDF)
- API-based job board submissions
- Manual file export for desktop workflow
- Brand consistency across all documents
- Real-time template fitting validation
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
from datetime import datetime
import tempfile
from pathlib import Path

# PDF generation imports
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import black, blue, gray
    REPORTLAB_AVAILABLE = True
except ImportError:
    print("ReportLab not installed. Install with: pip install reportlab")
    REPORTLAB_AVAILABLE = False

class SubmissionMethod(Enum):
    """Application submission methods"""
    API = "api"
    MANUAL = "manual"
    HYBRID = "hybrid"

class TemplateType(Enum):
    """Document template types"""
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    EXECUTIVE = "executive"

class DocumentFormat(Enum):
    """Output document formats"""
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    TXT = "txt"

@dataclass
class ContentConstraints:
    """Content fitting constraints for templates"""
    max_pages: int
    sections: Dict[str, Dict]
    character_limits: Dict[str, int]
    line_limits: Dict[str, int]
    
    @classmethod
    def get_resume_constraints(cls, template_type: TemplateType):
        """Get resume constraints for specific template"""
        constraints = {
            TemplateType.PROFESSIONAL: {
                "max_pages": 2,
                "sections": {
                    "executive_summary": {"max_chars": 400, "max_lines": 6},
                    "professional_experience": {"max_jobs": 4, "max_bullets_per_job": 4},
                    "skills": {"max_items": 12, "display_format": "grid"},
                    "education": {"max_items": 3, "condensed": True},
                    "certifications": {"max_items": 6, "priority_sort": True}
                },
                "character_limits": {"total": 2000, "per_section": 500},
                "line_limits": {"total": 80, "per_section": 20}
            },
            TemplateType.CREATIVE: {
                "max_pages": 2,
                "sections": {
                    "executive_summary": {"max_chars": 350, "max_lines": 5},
                    "professional_experience": {"max_jobs": 3, "max_bullets_per_job": 3},
                    "skills": {"max_items": 10, "display_format": "visual"},
                    "education": {"max_items": 2, "condensed": True},
                    "certifications": {"max_items": 4, "priority_sort": True}
                },
                "character_limits": {"total": 1800, "per_section": 450},
                "line_limits": {"total": 70, "per_section": 18}
            }
        }
        
        template_constraints = constraints.get(template_type, constraints[TemplateType.PROFESSIONAL])
        return cls(
            max_pages=template_constraints["max_pages"],
            sections=template_constraints["sections"],
            character_limits=template_constraints["character_limits"],
            line_limits=template_constraints["line_limits"]
        )

@dataclass
class ValidationResult:
    """Content validation results"""
    is_valid: bool
    warnings: List[str]
    errors: List[str]
    suggestions: List[str]
    character_usage: Dict[str, Dict]
    line_usage: Dict[str, Dict]

@dataclass
class ApplicationPackage:
    """Complete application package for submission"""
    job_id: str
    job_title: str
    company: str
    platform: str
    resume_content: Dict
    cover_letter_content: Optional[Dict]
    portfolio_content: Optional[Dict]
    metadata: Dict
    submission_preferences: Dict
    created_timestamp: str
    
    def get_file_prefix(self) -> str:
        """Generate file naming prefix"""
        # Clean job title and company for filename
        clean_title = "".join(c for c in self.job_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_company = "".join(c for c in self.company if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        # Replace spaces with underscores
        clean_title = clean_title.replace(' ', '_')
        clean_company = clean_company.replace(' ', '_')
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        return f"Allen_Walker_{clean_title}_{clean_company}_{date_str}"

@dataclass
class SubmissionResult:
    """Application submission result"""
    success: bool
    method: SubmissionMethod
    files_created: List[str]
    api_response: Optional[Dict]
    error_message: Optional[str]
    submission_timestamp: str
    tracking_id: Optional[str]

class ContentValidator:
    """Validates content against template constraints"""
    
    def __init__(self):
        pass
    
    def validate_resume(self, resume_content: Dict, template_type: TemplateType) -> ValidationResult:
        """Validate resume content against template constraints"""
        constraints = ContentConstraints.get_resume_constraints(template_type)
        
        warnings = []
        errors = []
        suggestions = []
        character_usage = {}
        line_usage = {}
        
        # Validate executive summary
        exec_summary = resume_content.get('executive_summary', '')
        exec_chars = len(exec_summary)
        exec_lines = len(exec_summary.split('\n'))
        
        exec_constraints = constraints.sections.get('executive_summary', {})
        max_chars = exec_constraints.get('max_chars', 400)
        max_lines = exec_constraints.get('max_lines', 6)
        
        character_usage['executive_summary'] = {
            'used': exec_chars,
            'limit': max_chars,
            'percentage': min((exec_chars / max_chars) * 100, 100)
        }
        
        line_usage['executive_summary'] = {
            'used': exec_lines,
            'limit': max_lines,
            'percentage': min((exec_lines / max_lines) * 100, 100)
        }
        
        if exec_chars > max_chars:
            errors.append(f"Executive summary exceeds {max_chars} characters ({exec_chars} used)")
        elif exec_chars > max_chars * 0.9:
            warnings.append(f"Executive summary near character limit ({exec_chars}/{max_chars})")
        
        if exec_lines > max_lines:
            errors.append(f"Executive summary exceeds {max_lines} lines ({exec_lines} used)")
        
        # Validate professional experience
        experience = resume_content.get('professional_experience', [])
        exp_constraints = constraints.sections.get('professional_experience', {})
        max_jobs = exp_constraints.get('max_jobs', 4)
        max_bullets = exp_constraints.get('max_bullets_per_job', 4)
        
        if len(experience) > max_jobs:
            warnings.append(f"Too many jobs for template ({len(experience)} jobs, {max_jobs} max)")
            suggestions.append("Consider consolidating similar roles or moving older positions to 'Additional Experience'")
        
        total_bullets = 0
        for job in experience:
            bullets = job.get('bullets', [])
            total_bullets += len(bullets)
            if len(bullets) > max_bullets:
                warnings.append(f"Job '{job.get('title', 'Unknown')}' has {len(bullets)} bullets (max {max_bullets})")
        
        character_usage['professional_experience'] = {
            'used': sum(len(str(job)) for job in experience),
            'limit': constraints.character_limits.get('per_section', 500),
            'jobs': len(experience),
            'bullets': total_bullets
        }
        
        # Validate skills
        skills = resume_content.get('skills', [])
        skills_constraints = constraints.sections.get('skills', {})
        max_skills = skills_constraints.get('max_items', 12)
        
        if len(skills) > max_skills:
            warnings.append(f"Too many skills for template ({len(skills)} skills, {max_skills} max)")
            suggestions.append("Focus on the most relevant skills for the target role")
        
        character_usage['skills'] = {
            'used': len(skills),
            'limit': max_skills,
            'percentage': min((len(skills) / max_skills) * 100, 100)
        }
        
        # Overall validation
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            warnings=warnings,
            errors=errors,
            suggestions=suggestions,
            character_usage=character_usage,
            line_usage=line_usage
        )
    
    def validate_cover_letter(self, cover_letter_content: Dict, template_type: TemplateType) -> ValidationResult:
        """Validate cover letter content against template constraints"""
        warnings = []
        errors = []
        suggestions = []
        
        # Get total content
        sections = cover_letter_content.get('sections', [])
        total_chars = sum(len(section.get('content', '')) for section in sections)
        total_lines = sum(len(section.get('content', '').split('\n')) for section in sections)
        
        # Template-specific limits
        if template_type == TemplateType.PROFESSIONAL:
            max_chars = 1200
            max_lines = 25
        else:
            max_chars = 1300
            max_lines = 29
        
        character_usage = {
            'total': {
                'used': total_chars,
                'limit': max_chars,
                'percentage': min((total_chars / max_chars) * 100, 100)
            }
        }
        
        line_usage = {
            'total': {
                'used': total_lines,
                'limit': max_lines,
                'percentage': min((total_lines / max_lines) * 100, 100)
            }
        }
        
        if total_chars > max_chars:
            errors.append(f"Cover letter exceeds {max_chars} characters ({total_chars} used)")
        elif total_chars > max_chars * 0.9:
            warnings.append(f"Cover letter near character limit ({total_chars}/{max_chars})")
        
        if total_lines > max_lines:
            errors.append(f"Cover letter exceeds {max_lines} lines ({total_lines} used)")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            warnings=warnings,
            errors=errors,
            suggestions=suggestions,
            character_usage=character_usage,
            line_usage=line_usage
        )

class TemplateEngine:
    """Generates formatted documents from content"""
    
    def __init__(self):
        self.template_cache = {}
    
    def generate_resume_pdf(self, resume_content: Dict, template_type: TemplateType, output_path: str) -> bool:
        """Generate resume PDF using template"""
        if not REPORTLAB_AVAILABLE:
            print("ReportLab not available. Cannot generate PDF.")
            return False
        
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            name = resume_content.get('personal_info', {}).get('name', 'Allen Walker')
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Center
            )
            story.append(Paragraph(name, title_style))
            
            # Contact info
            contact = resume_content.get('personal_info', {})
            contact_text = f"{contact.get('email', '')} | {contact.get('phone', '')} | {contact.get('location', '')}"
            story.append(Paragraph(contact_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Executive Summary
            if 'executive_summary' in resume_content:
                story.append(Paragraph("EXECUTIVE SUMMARY", styles['Heading2']))
                story.append(Paragraph(resume_content['executive_summary'], styles['Normal']))
                story.append(Spacer(1, 15))
            
            # Professional Experience
            if 'professional_experience' in resume_content:
                story.append(Paragraph("PROFESSIONAL EXPERIENCE", styles['Heading2']))
                for job in resume_content['professional_experience']:
                    # Job header
                    job_title = f"<b>{job.get('title', '')}</b> | {job.get('company', '')} | {job.get('location', '')} | {job.get('dates', '')}"
                    story.append(Paragraph(job_title, styles['Normal']))
                    
                    # Job bullets
                    for bullet in job.get('bullets', []):
                        bullet_text = f"• {bullet.get('text', bullet if isinstance(bullet, str) else '')}"
                        story.append(Paragraph(bullet_text, styles['Normal']))
                    
                    story.append(Spacer(1, 10))
            
            # Skills
            if 'skills' in resume_content:
                story.append(Paragraph("SKILLS & EXPERTISE", styles['Heading2']))
                skills_text = " • ".join(resume_content['skills'])
                story.append(Paragraph(skills_text, styles['Normal']))
                story.append(Spacer(1, 15))
            
            # Education
            if 'education' in resume_content:
                story.append(Paragraph("EDUCATION", styles['Heading2']))
                for edu in resume_content['education']:
                    edu_text = f"<b>{edu.get('degree', '')}</b> | {edu.get('school', '')} | {edu.get('year', '')}"
                    story.append(Paragraph(edu_text, styles['Normal']))
                story.append(Spacer(1, 15))
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating resume PDF: {e}")
            return False
    
    def generate_cover_letter_pdf(self, cover_letter_content: Dict, template_type: TemplateType, output_path: str) -> bool:
        """Generate cover letter PDF using template"""
        if not REPORTLAB_AVAILABLE:
            print("ReportLab not available. Cannot generate PDF.")
            return False
        
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Header
            story.append(Paragraph("Allen Walker", styles['Heading1']))
            story.append(Paragraph("allen.walker@email.com | (555) 123-4567", styles['Normal']))
            story.append(Spacer(1, 30))
            
            # Date and company info
            today = datetime.now().strftime("%B %d, %Y")
            story.append(Paragraph(today, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Cover letter content
            sections = cover_letter_content.get('sections', [])
            for section in sections:
                content = section.get('content', '')
                if content:
                    story.append(Paragraph(content, styles['Normal']))
                    story.append(Spacer(1, 12))
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating cover letter PDF: {e}")
            return False

class FileExporter:
    """Handles file export for manual submission"""
    
    def __init__(self, output_directory: str = None):
        self.output_directory = output_directory or tempfile.gettempdir()
        Path(self.output_directory).mkdir(parents=True, exist_ok=True)
    
    def export_application_package(self, package: ApplicationPackage, template_type: TemplateType) -> List[str]:
        """Export complete application package as files"""
        exported_files = []
        file_prefix = package.get_file_prefix()
        
        template_engine = TemplateEngine()
        
        # Export resume
        if package.resume_content:
            resume_path = os.path.join(self.output_directory, f"{file_prefix}_Resume.pdf")
            if template_engine.generate_resume_pdf(package.resume_content, template_type, resume_path):
                exported_files.append(resume_path)
        
        # Export cover letter
        if package.cover_letter_content:
            cover_letter_path = os.path.join(self.output_directory, f"{file_prefix}_CoverLetter.pdf")
            if template_engine.generate_cover_letter_pdf(package.cover_letter_content, template_type, cover_letter_path):
                exported_files.append(cover_letter_path)
        
        # Export portfolio (placeholder)
        if package.portfolio_content:
            portfolio_path = os.path.join(self.output_directory, f"{file_prefix}_Portfolio.pdf")
            # Portfolio PDF generation would go here
            # exported_files.append(portfolio_path)
        
        return exported_files

class ApplicationSubmissionManager:
    """Main application submission manager"""
    
    def __init__(self, output_directory: str = None):
        self.content_validator = ContentValidator()
        self.template_engine = TemplateEngine()
        self.file_exporter = FileExporter(output_directory)
        self.submission_history = []
    
    def create_application_package(
        self,
        job_data: Dict,
        resume_content: Dict,
        cover_letter_content: Optional[Dict] = None,
        portfolio_content: Optional[Dict] = None,
        submission_preferences: Optional[Dict] = None
    ) -> ApplicationPackage:
        """Create application package from content"""
        
        return ApplicationPackage(
            job_id=job_data.get('id', 'unknown'),
            job_title=job_data.get('title', 'Unknown Position'),
            company=job_data.get('company', 'Unknown Company'),
            platform=job_data.get('platform', 'manual'),
            resume_content=resume_content,
            cover_letter_content=cover_letter_content,
            portfolio_content=portfolio_content,
            metadata=job_data,
            submission_preferences=submission_preferences or {},
            created_timestamp=datetime.now().isoformat()
        )
    
    def validate_package(self, package: ApplicationPackage, template_type: TemplateType) -> Dict[str, ValidationResult]:
        """Validate entire application package"""
        results = {}
        
        # Validate resume
        if package.resume_content:
            results['resume'] = self.content_validator.validate_resume(
                package.resume_content, template_type
            )
        
        # Validate cover letter
        if package.cover_letter_content:
            results['cover_letter'] = self.content_validator.validate_cover_letter(
                package.cover_letter_content, template_type
            )
        
        return results
    
    def submit_application(
        self,
        package: ApplicationPackage,
        method: SubmissionMethod = SubmissionMethod.MANUAL,
        template_type: TemplateType = TemplateType.PROFESSIONAL
    ) -> SubmissionResult:
        """Submit application package"""
        
        # Validate package first
        validation_results = self.validate_package(package, template_type)
        
        # Check for validation errors
        has_errors = any(result.errors for result in validation_results.values())
        if has_errors:
            error_messages = []
            for doc_type, result in validation_results.items():
                if result.errors:
                    error_messages.extend([f"{doc_type}: {error}" for error in result.errors])
            
            return SubmissionResult(
                success=False,
                method=method,
                files_created=[],
                api_response=None,
                error_message="; ".join(error_messages),
                submission_timestamp=datetime.now().isoformat(),
                tracking_id=None
            )
        
        # Process submission based on method
        if method == SubmissionMethod.MANUAL:
            return self._submit_manual(package, template_type)
        elif method == SubmissionMethod.API:
            return self._submit_api(package, template_type)
        else:  # HYBRID
            return self._submit_hybrid(package, template_type)
    
    def _submit_manual(self, package: ApplicationPackage, template_type: TemplateType) -> SubmissionResult:
        """Handle manual file export submission"""
        try:
            exported_files = self.file_exporter.export_application_package(package, template_type)
            
            result = SubmissionResult(
                success=len(exported_files) > 0,
                method=SubmissionMethod.MANUAL,
                files_created=exported_files,
                api_response=None,
                error_message=None if exported_files else "No files were exported",
                submission_timestamp=datetime.now().isoformat(),
                tracking_id=f"manual_{package.job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            self.submission_history.append(result)
            return result
            
        except Exception as e:
            return SubmissionResult(
                success=False,
                method=SubmissionMethod.MANUAL,
                files_created=[],
                api_response=None,
                error_message=str(e),
                submission_timestamp=datetime.now().isoformat(),
                tracking_id=None
            )
    
    def _submit_api(self, package: ApplicationPackage, template_type: TemplateType) -> SubmissionResult:
        """Handle API-based submission (placeholder)"""
        # This would integrate with actual job board APIs
        return SubmissionResult(
            success=False,
            method=SubmissionMethod.API,
            files_created=[],
            api_response={"error": "API submission not yet implemented"},
            error_message="API submission feature under development",
            submission_timestamp=datetime.now().isoformat(),
            tracking_id=None
        )
    
    def _submit_hybrid(self, package: ApplicationPackage, template_type: TemplateType) -> SubmissionResult:
        """Handle hybrid submission (API with manual fallback)"""
        # Try API first, fallback to manual
        api_result = self._submit_api(package, template_type)
        if api_result.success:
            return api_result
        else:
            return self._submit_manual(package, template_type)
    
    def get_submission_history(self) -> List[SubmissionResult]:
        """Get submission history"""
        return self.submission_history.copy()

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    submission_manager = ApplicationSubmissionManager()
    
    # Sample job data
    job_data = {
        'id': 'job_123',
        'title': 'Senior Product Manager',
        'company': 'Coactive AI',
        'platform': 'manual'
    }
    
    # Sample resume content
    resume_content = {
        'personal_info': {
            'name': 'Allen Walker',
            'email': 'allen.walker@email.com',
            'phone': '(555) 123-4567',
            'location': 'San Francisco, CA'
        },
        'executive_summary': 'Experienced product manager with 7+ years of AI/ML product development experience.',
        'professional_experience': [
            {
                'title': 'Senior Product Manager',
                'company': 'TechCorp',
                'location': 'San Francisco, CA',
                'dates': '2020-Present',
                'bullets': [
                    {'text': 'Led development of AI-powered features increasing user engagement by 40%'},
                    {'text': 'Managed cross-functional team of 12 engineers and designers'},
                    {'text': 'Launched 3 successful ML products generating $2M ARR'}
                ]
            }
        ],
        'skills': ['Product Management', 'AI/ML', 'Data Analysis', 'Leadership', 'Strategy'],
        'education': [
            {
                'degree': 'MBA',
                'school': 'Stanford University',
                'year': '2018'
            }
        ]
    }
    
    # Sample cover letter content
    cover_letter_content = {
        'sections': [
            {
                'name': 'opening_hook',
                'content': 'I am excited to apply for the Senior Product Manager position at Coactive AI.'
            },
            {
                'name': 'value_proposition',
                'content': 'With 7+ years of AI/ML product experience, I have successfully launched multiple products that generated significant revenue and user growth.'
            },
            {
                'name': 'company_connection',
                'content': 'Your mission to democratize AI technology aligns perfectly with my passion for building impactful AI products.'
            },
            {
                'name': 'future_impact',
                'content': 'I am eager to bring my product leadership experience to help Coactive AI scale its platform and expand market reach.'
            },
            {
                'name': 'professional_close',
                'content': 'I would welcome the opportunity to discuss how my experience can contribute to your continued success.'
            }
        ]
    }
    
    # Create application package
    package = submission_manager.create_application_package(
        job_data=job_data,
        resume_content=resume_content,
        cover_letter_content=cover_letter_content
    )
    
    # Validate package
    validation_results = submission_manager.validate_package(package, TemplateType.PROFESSIONAL)
    
    print("Validation Results:")
    print("=" * 50)
    for doc_type, result in validation_results.items():
        print(f"\n{doc_type.upper()}:")
        print(f"Valid: {result.is_valid}")
        if result.warnings:
            print("Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"  - {error}")
        if result.suggestions:
            print("Suggestions:")
            for suggestion in result.suggestions:
                print(f"  - {suggestion}")
    
    # Submit application
    submission_result = submission_manager.submit_application(
        package=package,
        method=SubmissionMethod.MANUAL,
        template_type=TemplateType.PROFESSIONAL
    )
    
    print(f"\nSubmission Result:")
    print("=" * 50)
    print(f"Success: {submission_result.success}")
    print(f"Method: {submission_result.method.value}")
    print(f"Files Created: {len(submission_result.files_created)}")
    for file_path in submission_result.files_created:
        print(f"  - {file_path}")
    print(f"Tracking ID: {submission_result.tracking_id}")
    
    if submission_result.error_message:
        print(f"Error: {submission_result.error_message}")
