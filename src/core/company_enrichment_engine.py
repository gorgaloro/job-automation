#!/usr/bin/env python3
"""
Company Enrichment & Tech Classification Engine

Core engine for enriching company profiles with tech stack classification,
funding data, culture insights, and competitive intelligence.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TechClassification:
    """Tech stack classification data"""
    primary_vertical: str
    secondary_verticals: List[str]
    tech_stack: List[str]
    programming_languages: List[str]
    frameworks: List[str]
    databases: List[str]
    cloud_platforms: List[str]
    confidence_score: float
    classification_rationale: str

@dataclass
class CompanyEnrichmentData:
    """Comprehensive company enrichment data"""
    company_id: str
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    size_range: Optional[str] = None
    employee_count: Optional[int] = None
    funding_stage: Optional[str] = None
    funding_amount: Optional[str] = None
    valuation: Optional[str] = None
    headquarters: Optional[str] = None
    founded_year: Optional[int] = None
    tech_classification: Optional[TechClassification] = None
    values: List[str] = None
    culture_summary: Optional[str] = None
    recent_news: List[Dict] = None
    key_people: List[Dict] = None
    competitors: List[str] = None
    social_links: Dict[str, str] = None
    glassdoor_rating: Optional[float] = None
    growth_stage: Optional[str] = None
    remote_policy: Optional[str] = None
    confidence_score: float = 0.0
    enrichment_timestamp: str = None
    
    def __post_init__(self):
        if self.values is None:
            self.values = []
        if self.recent_news is None:
            self.recent_news = []
        if self.key_people is None:
            self.key_people = []
        if self.competitors is None:
            self.competitors = []
        if self.social_links is None:
            self.social_links = {}
        if self.enrichment_timestamp is None:
            self.enrichment_timestamp = datetime.now().isoformat()

class CompanyEnrichmentEngine:
    """Core engine for company data enrichment and tech classification"""
    
    def __init__(self):
        self.openai_client = None
        if OpenAI and os.getenv('OPENAI_API_KEY'):
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        self.demo_mode = not self.openai_client
        
        # Load tech verticals from your existing system
        self.tech_verticals = self._load_tech_verticals()
        
        logger.info(f"Company Enrichment Engine initialized (demo_mode: {self.demo_mode})")
        logger.info(f"Loaded {len(self.tech_verticals)} tech verticals")
    
    def _load_tech_verticals(self) -> List[str]:
        """Load tech verticals from your existing classification system"""
        # In demo mode, use common tech verticals
        return [
            "fintech", "healthtech", "edtech", "proptech", "legaltech",
            "martech", "adtech", "insurtech", "regtech", "cleantech",
            "foodtech", "retailtech", "hrtech", "cybersecurity", 
            "developer-tools", "infrastructure", "ai-ml", "blockchain",
            "gaming", "media", "e-commerce", "saas", "enterprise-software"
        ]
    
    def enrich_company(self, company_name: str, domain: Optional[str] = None, 
                      existing_data: Optional[Dict] = None) -> CompanyEnrichmentData:
        """
        Enrich company data with tech classification and comprehensive insights
        
        Args:
            company_name: Company name to enrich
            domain: Company domain/website
            existing_data: Any existing company data
            
        Returns:
            CompanyEnrichmentData with enriched information
        """
        try:
            logger.info(f"Enriching company: {company_name}")
            
            # Generate unique company ID
            company_id = f"comp_{company_name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}"
            
            if self.demo_mode:
                return self._create_demo_company_data(company_id, company_name, domain)
            
            # Real enrichment with AI
            enriched_data = self._enrich_with_ai(company_name, domain, existing_data)
            
            return CompanyEnrichmentData(
                company_id=company_id,
                name=company_name,
                domain=domain,
                **enriched_data
            )
            
        except Exception as e:
            logger.error(f"Company enrichment failed for {company_name}: {e}")
            return self._create_fallback_company_data(company_name, domain)
    
    def classify_tech_stack(self, company_name: str, domain: Optional[str] = None,
                           job_description: Optional[str] = None) -> TechClassification:
        """
        Classify company's tech stack and vertical
        
        Args:
            company_name: Company name
            domain: Company domain
            job_description: Job description text for tech stack hints
            
        Returns:
            TechClassification with detailed tech analysis
        """
        try:
            logger.info(f"Classifying tech stack for: {company_name}")
            
            if self.demo_mode:
                return self._create_demo_tech_classification(company_name)
            
            # Real AI-powered tech classification
            return self._classify_tech_with_ai(company_name, domain, job_description)
            
        except Exception as e:
            logger.error(f"Tech classification failed for {company_name}: {e}")
            return self._create_fallback_tech_classification()
    
    def _enrich_with_ai(self, company_name: str, domain: Optional[str], 
                       existing_data: Optional[Dict]) -> Dict:
        """Use AI to enrich company data comprehensively"""
        
        prompt = f"""
        Analyze and enrich the following company with comprehensive business intelligence:
        
        Company Name: {company_name}
        Domain: {domain or 'Unknown'}
        Existing Data: {json.dumps(existing_data or {}, indent=2)}
        
        Available Tech Verticals: {', '.join(self.tech_verticals)}
        
        Please provide enriched company data in the following JSON format:
        {{
            "industry": "primary industry classification",
            "size_range": "startup/small/medium/large/enterprise",
            "employee_count": estimated_number_of_employees,
            "funding_stage": "pre-seed/seed/series_a/series_b/series_c/public/private",
            "funding_amount": "latest funding amount if known",
            "valuation": "company valuation if known",
            "headquarters": "city, country",
            "founded_year": year_as_integer,
            "tech_classification": {{
                "primary_vertical": "primary tech vertical from the list",
                "secondary_verticals": ["secondary", "verticals"],
                "tech_stack": ["technology1", "technology2"],
                "programming_languages": ["Python", "JavaScript"],
                "frameworks": ["React", "Django"],
                "databases": ["PostgreSQL", "MongoDB"],
                "cloud_platforms": ["AWS", "GCP"],
                "confidence_score": 0.85,
                "classification_rationale": "reasoning for classification"
            }},
            "values": ["value1", "value2", "value3"],
            "culture_summary": "brief culture and work environment description",
            "competitors": ["competitor1", "competitor2"],
            "glassdoor_rating": 4.2,
            "growth_stage": "early/growth/mature/declining",
            "remote_policy": "remote-first/hybrid/office-required/flexible",
            "confidence_score": 0.85
        }}
        
        Base your analysis on publicly available information and reasonable inferences.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Convert tech_classification dict to TechClassification object
            if "tech_classification" in result:
                tech_data = result["tech_classification"]
                result["tech_classification"] = TechClassification(**tech_data)
            
            return result
            
        except Exception as e:
            logger.error(f"AI enrichment failed: {e}")
            return self._create_fallback_enrichment_data()
    
    def _classify_tech_with_ai(self, company_name: str, domain: Optional[str],
                              job_description: Optional[str]) -> TechClassification:
        """Use AI to classify tech stack"""
        
        prompt = f"""
        Classify the tech stack and vertical for this company:
        
        Company: {company_name}
        Domain: {domain or 'Unknown'}
        Job Description Context: {job_description or 'Not provided'}
        
        Available Tech Verticals: {', '.join(self.tech_verticals)}
        
        Provide detailed tech classification in JSON format:
        {{
            "primary_vertical": "primary tech vertical from the list",
            "secondary_verticals": ["secondary", "verticals"],
            "tech_stack": ["comprehensive", "tech", "stack"],
            "programming_languages": ["Python", "JavaScript", "Go"],
            "frameworks": ["React", "Django", "Express"],
            "databases": ["PostgreSQL", "Redis", "MongoDB"],
            "cloud_platforms": ["AWS", "GCP", "Azure"],
            "confidence_score": 0.85,
            "classification_rationale": "detailed reasoning for classification"
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return TechClassification(**result)
            
        except Exception as e:
            logger.error(f"AI tech classification failed: {e}")
            return self._create_fallback_tech_classification()
    
    def _create_demo_company_data(self, company_id: str, company_name: str, 
                                 domain: Optional[str]) -> CompanyEnrichmentData:
        """Create demo company data for testing"""
        
        demo_companies = {
            "TechCorp": {
                "industry": "financial technology",
                "size_range": "medium",
                "employee_count": 250,
                "funding_stage": "series_b",
                "funding_amount": "$25M",
                "headquarters": "San Francisco, CA",
                "founded_year": 2018,
                "tech_classification": TechClassification(
                    primary_vertical="fintech",
                    secondary_verticals=["developer-tools"],
                    tech_stack=["React", "Node.js", "PostgreSQL", "AWS", "Docker"],
                    programming_languages=["JavaScript", "Python", "Go"],
                    frameworks=["React", "Express", "FastAPI"],
                    databases=["PostgreSQL", "Redis"],
                    cloud_platforms=["AWS"],
                    confidence_score=0.92,
                    classification_rationale="Fintech company with modern web stack"
                ),
                "values": ["innovation", "transparency", "customer_focus"],
                "culture_summary": "Fast-paced fintech startup with strong engineering culture and emphasis on work-life balance",
                "competitors": ["Stripe", "Square", "Plaid"],
                "glassdoor_rating": 4.3,
                "growth_stage": "growth",
                "remote_policy": "hybrid",
                "confidence_score": 0.92
            },
            "DataFlow": {
                "industry": "healthcare technology",
                "size_range": "startup",
                "employee_count": 85,
                "funding_stage": "series_a",
                "funding_amount": "$12M",
                "headquarters": "Boston, MA",
                "founded_year": 2020,
                "tech_classification": TechClassification(
                    primary_vertical="healthtech",
                    secondary_verticals=["ai-ml"],
                    tech_stack=["Python", "Django", "PostgreSQL", "GCP", "Kubernetes"],
                    programming_languages=["Python", "JavaScript", "R"],
                    frameworks=["Django", "React", "TensorFlow"],
                    databases=["PostgreSQL", "MongoDB"],
                    cloud_platforms=["GCP"],
                    confidence_score=0.88,
                    classification_rationale="Healthcare AI company with Python-heavy stack"
                ),
                "values": ["healthcare_impact", "data_privacy", "innovation"],
                "culture_summary": "Mission-driven healthtech startup focused on patient outcomes with collaborative remote-first culture",
                "competitors": ["Veracyte", "Tempus", "Flatiron Health"],
                "glassdoor_rating": 4.5,
                "growth_stage": "early",
                "remote_policy": "remote-first",
                "confidence_score": 0.88
            },
            "CloudScale": {
                "industry": "developer tools",
                "size_range": "medium",
                "employee_count": 180,
                "funding_stage": "series_b",
                "funding_amount": "$30M",
                "headquarters": "Seattle, WA",
                "founded_year": 2019,
                "tech_classification": TechClassification(
                    primary_vertical="developer-tools",
                    secondary_verticals=["infrastructure"],
                    tech_stack=["Go", "Kubernetes", "PostgreSQL", "AWS", "Terraform"],
                    programming_languages=["Go", "Python", "JavaScript"],
                    frameworks=["Gin", "React", "Terraform"],
                    databases=["PostgreSQL", "ClickHouse"],
                    cloud_platforms=["AWS", "GCP"],
                    confidence_score=0.95,
                    classification_rationale="Developer tools company with infrastructure focus"
                ),
                "values": ["developer_experience", "reliability", "open_source"],
                "culture_summary": "Engineering-first culture with focus on developer productivity and distributed systems expertise",
                "competitors": ["Datadog", "New Relic", "Honeycomb"],
                "glassdoor_rating": 4.4,
                "growth_stage": "growth",
                "remote_policy": "flexible",
                "confidence_score": 0.95
            }
        }
        
        base_data = demo_companies.get(company_name, {
            "industry": "technology",
            "size_range": "medium",
            "employee_count": 150,
            "funding_stage": "private",
            "headquarters": "San Francisco, CA",
            "founded_year": 2019,
            "tech_classification": TechClassification(
                primary_vertical="saas",
                secondary_verticals=["enterprise-software"],
                tech_stack=["JavaScript", "Python", "AWS"],
                programming_languages=["JavaScript", "Python"],
                frameworks=["React", "Django"],
                databases=["PostgreSQL"],
                cloud_platforms=["AWS"],
                confidence_score=0.75,
                classification_rationale="General SaaS company with standard web stack"
            ),
            "values": ["innovation", "collaboration", "growth"],
            "culture_summary": "Technology company with collaborative culture",
            "competitors": ["Similar SaaS companies"],
            "glassdoor_rating": 4.0,
            "growth_stage": "growth",
            "remote_policy": "hybrid",
            "confidence_score": 0.75
        })
        
        return CompanyEnrichmentData(
            company_id=company_id,
            name=company_name,
            domain=domain,
            **base_data
        )
    
    def _create_demo_tech_classification(self, company_name: str) -> TechClassification:
        """Create demo tech classification"""
        
        demo_classifications = {
            "TechCorp": TechClassification(
                primary_vertical="fintech",
                secondary_verticals=["developer-tools"],
                tech_stack=["React", "Node.js", "PostgreSQL", "AWS", "Docker"],
                programming_languages=["JavaScript", "Python", "Go"],
                frameworks=["React", "Express", "FastAPI"],
                databases=["PostgreSQL", "Redis"],
                cloud_platforms=["AWS"],
                confidence_score=0.92,
                classification_rationale="Fintech company with modern web stack"
            ),
            "DataFlow": TechClassification(
                primary_vertical="healthtech",
                secondary_verticals=["ai-ml"],
                tech_stack=["Python", "Django", "PostgreSQL", "GCP", "Kubernetes"],
                programming_languages=["Python", "JavaScript", "R"],
                frameworks=["Django", "React", "TensorFlow"],
                databases=["PostgreSQL", "MongoDB"],
                cloud_platforms=["GCP"],
                confidence_score=0.88,
                classification_rationale="Healthcare AI company with Python-heavy stack"
            )
        }
        
        return demo_classifications.get(company_name, TechClassification(
            primary_vertical="saas",
            secondary_verticals=["enterprise-software"],
            tech_stack=["JavaScript", "Python", "AWS"],
            programming_languages=["JavaScript", "Python"],
            frameworks=["React", "Django"],
            databases=["PostgreSQL"],
            cloud_platforms=["AWS"],
            confidence_score=0.75,
            classification_rationale="General SaaS company with standard web stack"
        ))
    
    def _create_fallback_company_data(self, company_name: str, 
                                    domain: Optional[str]) -> CompanyEnrichmentData:
        """Create fallback data when enrichment fails"""
        company_id = f"comp_{company_name.lower().replace(' ', '_')}_fallback"
        
        return CompanyEnrichmentData(
            company_id=company_id,
            name=company_name,
            domain=domain,
            confidence_score=0.1
        )
    
    def _create_fallback_enrichment_data(self) -> Dict:
        """Create fallback enrichment data"""
        return {
            "industry": "unknown",
            "size_range": "unknown",
            "confidence_score": 0.1,
            "tech_classification": TechClassification(
                primary_vertical="unknown",
                secondary_verticals=[],
                tech_stack=[],
                programming_languages=[],
                frameworks=[],
                databases=[],
                cloud_platforms=[],
                confidence_score=0.1,
                classification_rationale="Fallback classification due to enrichment failure"
            )
        }
    
    def _create_fallback_tech_classification(self) -> TechClassification:
        """Create fallback tech classification"""
        return TechClassification(
            primary_vertical="unknown",
            secondary_verticals=[],
            tech_stack=[],
            programming_languages=[],
            frameworks=[],
            databases=[],
            cloud_platforms=[],
            confidence_score=0.1,
            classification_rationale="Fallback classification due to analysis failure"
        )

# Demo functions
def demo_company_enrichment():
    """Demo company enrichment functionality"""
    print("=== Company Enrichment & Tech Classification Demo ===")
    
    engine = CompanyEnrichmentEngine()
    
    companies = ["TechCorp", "DataFlow", "CloudScale"]
    
    for company in companies:
        print(f"\n🏢 Enriching: {company}")
        enriched = engine.enrich_company(company)
        
        print(f"  Industry: {enriched.industry}")
        print(f"  Size: {enriched.size_range} ({enriched.employee_count} employees)")
        print(f"  Funding: {enriched.funding_stage} - {enriched.funding_amount}")
        print(f"  Tech Vertical: {enriched.tech_classification.primary_vertical}")
        print(f"  Tech Stack: {', '.join(enriched.tech_classification.tech_stack[:3])}...")
        print(f"  Culture: {enriched.culture_summary[:60]}...")
        print(f"  Confidence: {enriched.confidence_score:.1%}")

def demo_tech_classification():
    """Demo tech classification functionality"""
    print("\n=== Tech Stack Classification Demo ===")
    
    engine = CompanyEnrichmentEngine()
    
    companies = ["TechCorp", "DataFlow", "CloudScale"]
    
    for company in companies:
        print(f"\n🔧 Classifying: {company}")
        classification = engine.classify_tech_stack(company)
        
        print(f"  Primary Vertical: {classification.primary_vertical}")
        print(f"  Secondary: {', '.join(classification.secondary_verticals)}")
        print(f"  Languages: {', '.join(classification.programming_languages)}")
        print(f"  Frameworks: {', '.join(classification.frameworks)}")
        print(f"  Cloud: {', '.join(classification.cloud_platforms)}")
        print(f"  Confidence: {classification.confidence_score:.1%}")
        print(f"  Rationale: {classification.classification_rationale}")

if __name__ == "__main__":
    demo_company_enrichment()
    demo_tech_classification()
