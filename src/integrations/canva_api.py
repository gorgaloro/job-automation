"""
Canva API Integration for Resume PDF Generation
Handles professional resume formatting and PDF generation using Canva's design platform
"""

import os
import logging
import requests
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import base64
import tempfile

logger = logging.getLogger(__name__)


@dataclass
class CanvaCredentials:
    """Canva API credentials"""
    client_id: str
    client_secret: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None


@dataclass
class ResumeTemplate:
    """Canva resume template configuration"""
    template_id: str
    name: str
    style: str  # 'professional', 'modern', 'creative', 'minimal'
    color_scheme: str
    suitable_for: List[str]  # job types this template works well for


@dataclass
class CanvaDesign:
    """Canva design object"""
    design_id: str
    title: str
    thumbnail_url: str
    urls: Dict[str, str]
    created_at: datetime
    updated_at: datetime


class CanvaAPIClient:
    """Canva API client for resume generation"""
    
    BASE_URL = "https://api.canva.com/rest/v1"
    
    def __init__(self, credentials: CanvaCredentials):
        self.credentials = credentials
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Setup HTTP session with authentication"""
        if self.credentials.access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.credentials.access_token}',
                'Content-Type': 'application/json'
            })
    
    def authenticate(self, code: str = None) -> bool:
        """Authenticate with Canva API using OAuth2"""
        try:
            if code:
                # Exchange authorization code for access token
                token_data = self._exchange_code_for_token(code)
            else:
                # Use client credentials flow for app-level access
                token_data = self._get_client_credentials_token()
            
            if token_data:
                self.credentials.access_token = token_data.get('access_token')
                self.credentials.refresh_token = token_data.get('refresh_token')
                
                # Calculate expiration time
                expires_in = token_data.get('expires_in', 3600)
                self.credentials.expires_at = datetime.now().timestamp() + expires_in
                
                self._setup_session()
                logger.info("Successfully authenticated with Canva API")
                return True
            
        except Exception as e:
            logger.error(f"Canva authentication failed: {e}")
        
        return False
    
    def _exchange_code_for_token(self, code: str) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        token_url = "https://api.canva.com/rest/v1/oauth/token"
        
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.credentials.client_id,
            'client_secret': self.credentials.client_secret,
            'code': code,
            'redirect_uri': 'http://localhost:8080/canva/callback'  # Configure as needed
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        return response.json()
    
    def _get_client_credentials_token(self) -> Optional[Dict]:
        """Get access token using client credentials flow"""
        token_url = "https://api.canva.com/rest/v1/oauth/token"
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.credentials.client_id,
            'client_secret': self.credentials.client_secret
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        return response.json()
    
    def refresh_access_token(self) -> bool:
        """Refresh expired access token"""
        if not self.credentials.refresh_token:
            return False
        
        try:
            token_url = "https://api.canva.com/rest/v1/oauth/token"
            
            data = {
                'grant_type': 'refresh_token',
                'client_id': self.credentials.client_id,
                'client_secret': self.credentials.client_secret,
                'refresh_token': self.credentials.refresh_token
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.credentials.access_token = token_data.get('access_token')
            
            expires_in = token_data.get('expires_in', 3600)
            self.credentials.expires_at = datetime.now().timestamp() + expires_in
            
            self._setup_session()
            return True
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return False
    
    def _ensure_valid_token(self):
        """Ensure we have a valid access token"""
        if not self.credentials.access_token:
            raise Exception("No access token available. Please authenticate first.")
        
        # Check if token is expired
        if (self.credentials.expires_at and 
            datetime.now().timestamp() >= self.credentials.expires_at - 300):  # 5 min buffer
            
            if not self.refresh_access_token():
                raise Exception("Failed to refresh expired access token")
    
    def get_user_profile(self) -> Dict[str, Any]:
        """Get current user profile"""
        self._ensure_valid_token()
        
        response = self.session.get(f"{self.BASE_URL}/me")
        response.raise_for_status()
        return response.json()
    
    def create_design_from_template(self, template_id: str, title: str = None) -> CanvaDesign:
        """Create a new design from a template"""
        self._ensure_valid_token()
        
        payload = {
            'design_type': 'DOC_A4_PORTRAIT',  # Standard resume format
        }
        
        if template_id:
            payload['template_id'] = template_id
        
        if title:
            payload['title'] = title
        
        response = self.session.post(f"{self.BASE_URL}/designs", json=payload)
        response.raise_for_status()
        
        design_data = response.json()
        return self._parse_design_response(design_data)
    
    def update_design_content(self, design_id: str, content_updates: Dict[str, Any]) -> bool:
        """Update design content with resume data"""
        self._ensure_valid_token()
        
        try:
            # Get design elements first
            elements = self.get_design_elements(design_id)
            
            # Update text elements with resume content
            for element in elements:
                if element.get('type') == 'text':
                    element_id = element.get('id')
                    current_text = element.get('text', '')
                    
                    # Map resume fields to text elements
                    updated_text = self._map_resume_content_to_text(
                        current_text, content_updates
                    )
                    
                    if updated_text != current_text:
                        self._update_text_element(design_id, element_id, updated_text)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update design content: {e}")
            return False
    
    def get_design_elements(self, design_id: str) -> List[Dict[str, Any]]:
        """Get all elements in a design"""
        self._ensure_valid_token()
        
        response = self.session.get(f"{self.BASE_URL}/designs/{design_id}/elements")
        response.raise_for_status()
        
        return response.json().get('elements', [])
    
    def _update_text_element(self, design_id: str, element_id: str, text: str):
        """Update a specific text element"""
        payload = {
            'text': text
        }
        
        response = self.session.patch(
            f"{self.BASE_URL}/designs/{design_id}/elements/{element_id}",
            json=payload
        )
        response.raise_for_status()
    
    def _map_resume_content_to_text(self, current_text: str, content: Dict[str, Any]) -> str:
        """Map resume content to text elements based on placeholders"""
        
        # Common resume field mappings
        mappings = {
            '{{name}}': content.get('personal_info', {}).get('full_name', ''),
            '{{email}}': content.get('personal_info', {}).get('email', ''),
            '{{phone}}': content.get('personal_info', {}).get('phone', ''),
            '{{location}}': content.get('personal_info', {}).get('location', ''),
            '{{linkedin}}': content.get('personal_info', {}).get('linkedin_url', ''),
            '{{summary}}': content.get('executive_summary', ''),
            '{{skills}}': ', '.join(content.get('skills', [])),
        }
        
        # Apply mappings
        updated_text = current_text
        for placeholder, value in mappings.items():
            if placeholder in updated_text:
                updated_text = updated_text.replace(placeholder, str(value))
        
        # Handle work experience
        if '{{experience}}' in updated_text:
            experience_text = self._format_work_experience(content.get('work_experience', []))
            updated_text = updated_text.replace('{{experience}}', experience_text)
        
        # Handle education
        if '{{education}}' in updated_text:
            education_text = self._format_education(content.get('education', []))
            updated_text = updated_text.replace('{{education}}', education_text)
        
        return updated_text
    
    def _format_work_experience(self, experience: List[Dict]) -> str:
        """Format work experience for resume"""
        formatted = []
        
        for job in experience:
            job_text = f"{job.get('title', '')} | {job.get('company', '')}\n"
            job_text += f"{job.get('start_date', '')} - {job.get('end_date', 'Present')}\n"
            
            bullets = job.get('bullet_points', [])
            for bullet in bullets:
                if bullet.get('selected', True):  # Only include selected bullets
                    job_text += f"• {bullet.get('text', '')}\n"
            
            formatted.append(job_text)
        
        return '\n'.join(formatted)
    
    def _format_education(self, education: List[Dict]) -> str:
        """Format education for resume"""
        formatted = []
        
        for edu in education:
            edu_text = f"{edu.get('degree', '')} | {edu.get('institution', '')}\n"
            edu_text += f"{edu.get('graduation_year', '')}\n"
            
            if edu.get('gpa') and edu.get('show_gpa', False):
                edu_text += f"GPA: {edu.get('gpa')}\n"
            
            formatted.append(edu_text)
        
        return '\n'.join(formatted)
    
    def export_design_as_pdf(self, design_id: str, filename: str = None) -> Tuple[bytes, str]:
        """Export design as PDF"""
        self._ensure_valid_token()
        
        # Request PDF export
        export_payload = {
            'format': 'PDF',
            'pages': 'all'
        }
        
        response = self.session.post(
            f"{self.BASE_URL}/designs/{design_id}/export",
            json=export_payload
        )
        response.raise_for_status()
        
        export_data = response.json()
        download_url = export_data.get('urls', {}).get('download_url')
        
        if not download_url:
            raise Exception("No download URL received from Canva")
        
        # Download the PDF
        pdf_response = requests.get(download_url)
        pdf_response.raise_for_status()
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"resume_{timestamp}.pdf"
        
        return pdf_response.content, filename
    
    def _parse_design_response(self, design_data: Dict) -> CanvaDesign:
        """Parse design response into CanvaDesign object"""
        return CanvaDesign(
            design_id=design_data.get('id'),
            title=design_data.get('title', ''),
            thumbnail_url=design_data.get('thumbnail', {}).get('url', ''),
            urls=design_data.get('urls', {}),
            created_at=datetime.fromisoformat(design_data.get('created_at', '').replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(design_data.get('updated_at', '').replace('Z', '+00:00'))
        )


class ResumeTemplateManager:
    """Manages Canva resume templates"""
    
    def __init__(self):
        self.templates = {
            'professional': ResumeTemplate(
                template_id='BAEoeNVme4w',  # Example template ID
                name='Professional Executive',
                style='professional',
                color_scheme='navy_blue',
                suitable_for=['executive', 'management', 'finance', 'consulting']
            ),
            'modern': ResumeTemplate(
                template_id='BAEoeNVme5x',  # Example template ID
                name='Modern Tech',
                style='modern',
                color_scheme='blue_accent',
                suitable_for=['technology', 'startup', 'product', 'engineering']
            ),
            'healthcare': ResumeTemplate(
                template_id='BAEoeNVme6y',  # Example template ID
                name='Healthcare Professional',
                style='professional',
                color_scheme='teal_green',
                suitable_for=['healthcare', 'medical', 'nursing', 'pharmaceutical']
            ),
            'creative': ResumeTemplate(
                template_id='BAEoeNVme7z',  # Example template ID
                name='Creative Portfolio',
                style='creative',
                color_scheme='purple_orange',
                suitable_for=['design', 'marketing', 'advertising', 'media']
            )
        }
    
    def get_template_for_job(self, job_title: str, industry: str) -> ResumeTemplate:
        """Get the best template for a specific job/industry"""
        job_title_lower = job_title.lower()
        industry_lower = industry.lower()
        
        # Healthcare roles
        if any(keyword in job_title_lower or keyword in industry_lower 
               for keyword in ['health', 'medical', 'clinical', 'hospital', 'epic']):
            return self.templates['healthcare']
        
        # Technology roles
        if any(keyword in job_title_lower or keyword in industry_lower 
               for keyword in ['tech', 'software', 'engineer', 'developer', 'ai', 'data']):
            return self.templates['modern']
        
        # Creative roles
        if any(keyword in job_title_lower or keyword in industry_lower 
               for keyword in ['design', 'creative', 'marketing', 'brand', 'content']):
            return self.templates['creative']
        
        # Default to professional
        return self.templates['professional']
    
    def list_templates(self) -> List[ResumeTemplate]:
        """List all available templates"""
        return list(self.templates.values())


class CanvaResumeGenerator:
    """High-level resume generation using Canva API"""
    
    def __init__(self, credentials: CanvaCredentials):
        self.client = CanvaAPIClient(credentials)
        self.template_manager = ResumeTemplateManager()
    
    def authenticate(self) -> bool:
        """Authenticate with Canva API"""
        return self.client.authenticate()
    
    def generate_resume_pdf(self, 
                           resume_data: Dict[str, Any], 
                           job_title: str = None,
                           industry: str = None,
                           template_style: str = None) -> Tuple[bytes, str]:
        """Generate a complete resume PDF"""
        
        try:
            # Select appropriate template
            if template_style and template_style in self.template_manager.templates:
                template = self.template_manager.templates[template_style]
            else:
                template = self.template_manager.get_template_for_job(
                    job_title or '', industry or ''
                )
            
            logger.info(f"Using template: {template.name} for {job_title}")
            
            # Create design from template
            design_title = f"Resume - {resume_data.get('personal_info', {}).get('full_name', 'Candidate')}"
            design = self.client.create_design_from_template(template.template_id, design_title)
            
            # Update design with resume content
            success = self.client.update_design_content(design.design_id, resume_data)
            
            if not success:
                raise Exception("Failed to update design content")
            
            # Export as PDF
            pdf_content, filename = self.client.export_design_as_pdf(design.design_id)
            
            logger.info(f"Successfully generated resume PDF: {filename}")
            return pdf_content, filename
            
        except Exception as e:
            logger.error(f"Resume generation failed: {e}")
            raise
    
    def save_resume_pdf(self, 
                       resume_data: Dict[str, Any], 
                       output_path: str,
                       job_title: str = None,
                       industry: str = None,
                       template_style: str = None) -> str:
        """Generate and save resume PDF to file"""
        
        pdf_content, filename = self.generate_resume_pdf(
            resume_data, job_title, industry, template_style
        )
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save PDF
        with open(output_path, 'wb') as f:
            f.write(pdf_content)
        
        logger.info(f"Resume PDF saved to: {output_path}")
        return output_path


# Utility functions

def create_canva_credentials() -> CanvaCredentials:
    """Create Canva credentials from environment variables"""
    client_id = os.getenv('CANVA_CLIENT_ID')
    client_secret = os.getenv('CANVA_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        raise ValueError("Canva API credentials not found in environment variables")
    
    return CanvaCredentials(client_id=client_id, client_secret=client_secret)


def generate_resume_pdf_from_optimizer_data(resume_data: Dict[str, Any], 
                                          job_context: Dict[str, Any] = None) -> Tuple[bytes, str]:
    """Generate resume PDF from Dynamic Resume Optimizer data"""
    
    # Create credentials and generator
    credentials = create_canva_credentials()
    generator = CanvaResumeGenerator(credentials)
    
    # Authenticate
    if not generator.authenticate():
        raise Exception("Failed to authenticate with Canva API")
    
    # Extract job context
    job_title = job_context.get('job_title') if job_context else None
    industry = job_context.get('industry') if job_context else None
    
    # Generate PDF
    return generator.generate_resume_pdf(resume_data, job_title, industry)


if __name__ == "__main__":
    # Example usage
    sample_resume_data = {
        'personal_info': {
            'full_name': 'Allen Walker',
            'email': 'allen.walker@email.com',
            'phone': '(555) 123-4567',
            'location': 'San Francisco, CA',
            'linkedin_url': 'https://linkedin.com/in/allenwalker'
        },
        'executive_summary': 'Experienced Program Manager with 15+ years in healthcare technology...',
        'skills': ['Program Management', 'Epic Systems', 'Salesforce', 'AI/ML', 'Healthcare IT'],
        'work_experience': [
            {
                'title': 'Senior Program Manager',
                'company': 'Ford Motor Company',
                'start_date': '2020',
                'end_date': 'Present',
                'bullet_points': [
                    {'text': 'Led AI platform development initiative', 'selected': True},
                    {'text': 'Managed cross-functional teams of 25+ members', 'selected': True}
                ]
            }
        ],
        'education': [
            {
                'degree': 'Bachelor of Arts in Business Economics',
                'institution': 'UCLA',
                'graduation_year': '2002',
                'gpa': '3.7',
                'show_gpa': False
            }
        ]
    }
    
    try:
        pdf_content, filename = generate_resume_pdf_from_optimizer_data(
            sample_resume_data,
            {'job_title': 'Senior Program Manager', 'industry': 'Technology'}
        )
        
        # Save to file
        with open(f'/tmp/{filename}', 'wb') as f:
            f.write(pdf_content)
        
        print(f"Resume PDF generated successfully: {filename}")
        
    except Exception as e:
        print(f"Error generating resume: {e}")
