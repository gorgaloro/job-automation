"""
Company Enrichment API Integration Module

This module provides unified access to company data enrichment APIs including:
- Clearbit
- ZoomInfo  
- Apollo
- Custom company data sources

All APIs are normalized to a common company data format for consistent processing.
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CompanyData:
    """Normalized company data structure"""
    name: str
    domain: str
    description: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    founded_year: Optional[int] = None
    revenue: Optional[str] = None
    funding: Optional[str] = None
    technologies: Optional[List[str]] = None
    social_media: Optional[Dict[str, str]] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    source_api: str = None
    confidence_score: Optional[float] = None
    raw_data: Optional[Dict] = None

class BaseCompanyEnrichmentAPI:
    """Base class for company enrichment API integrations"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def enrich_company(self, domain: str = None, company_name: str = None) -> Optional[CompanyData]:
        """Override in subclasses"""
        raise NotImplementedError

class ClearbitAPI(BaseCompanyEnrichmentAPI):
    """Clearbit Company API Integration"""
    
    def __init__(self, api_key: str = None):
        super().__init__(
            api_key=api_key or os.getenv('CLEARBIT_API_KEY'),
            base_url='https://company.clearbit.com/v2/'
        )
        
    async def enrich_company(self, domain: str = None, company_name: str = None) -> Optional[CompanyData]:
        """Enrich company data using Clearbit API"""
        if not self.api_key:
            logger.warning("Clearbit API key not provided, skipping")
            return None
            
        if not domain and not company_name:
            logger.warning("Either domain or company_name required for Clearbit enrichment")
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Use domain if available, otherwise try company name
            query_param = f'domain={domain}' if domain else f'company={company_name}'
            url = urljoin(self.base_url, f'companies/find?{query_param}')
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    company_data = await response.json()
                    return self.normalize_company_data(company_data, 'clearbit')
                elif response.status == 404:
                    logger.info(f"Company not found in Clearbit: {domain or company_name}")
                    return None
                else:
                    logger.error(f"Clearbit API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error enriching company with Clearbit: {e}")
            return None
            
    def normalize_company_data(self, raw_data: Dict, source_api: str) -> CompanyData:
        """Normalize Clearbit company data"""
        return CompanyData(
            name=raw_data.get('name', ''),
            domain=raw_data.get('domain', ''),
            description=raw_data.get('description'),
            industry=raw_data.get('category', {}).get('industry') if raw_data.get('category') else None,
            size=raw_data.get('metrics', {}).get('employees') if raw_data.get('metrics') else None,
            location=raw_data.get('geo', {}).get('city') if raw_data.get('geo') else None,
            founded_year=raw_data.get('foundedYear'),
            revenue=raw_data.get('metrics', {}).get('annualRevenue') if raw_data.get('metrics') else None,
            funding=raw_data.get('metrics', {}).get('raised') if raw_data.get('metrics') else None,
            technologies=raw_data.get('tech', []) if raw_data.get('tech') else None,
            social_media={
                'twitter': raw_data.get('twitter', {}).get('handle') if raw_data.get('twitter') else None,
                'linkedin': raw_data.get('linkedin', {}).get('handle') if raw_data.get('linkedin') else None,
                'facebook': raw_data.get('facebook', {}).get('handle') if raw_data.get('facebook') else None,
            },
            logo_url=raw_data.get('logo'),
            website=raw_data.get('site', {}).get('url') if raw_data.get('site') else None,
            phone=raw_data.get('phone'),
            source_api=source_api,
            confidence_score=0.9,  # Clearbit generally has high quality data
            raw_data=raw_data
        )

class ZoomInfoAPI(BaseCompanyEnrichmentAPI):
    """ZoomInfo Company API Integration"""
    
    def __init__(self, api_key: str = None):
        super().__init__(
            api_key=api_key or os.getenv('ZOOMINFO_API_KEY'),
            base_url='https://api.zoominfo.com/lookup/company'
        )
        
    async def enrich_company(self, domain: str = None, company_name: str = None) -> Optional[CompanyData]:
        """Enrich company data using ZoomInfo API"""
        if not self.api_key:
            logger.warning("ZoomInfo API key not provided, skipping")
            return None
            
        if not domain and not company_name:
            logger.warning("Either domain or company_name required for ZoomInfo enrichment")
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Build request body
            body = {}
            if domain:
                body['companyDomain'] = domain
            if company_name:
                body['companyName'] = company_name
                
            async with self.session.post(self.base_url, headers=headers, json=body) as response:
                if response.status == 200:
                    company_data = await response.json()
                    return self.normalize_company_data(company_data, 'zoominfo')
                elif response.status == 404:
                    logger.info(f"Company not found in ZoomInfo: {domain or company_name}")
                    return None
                else:
                    logger.error(f"ZoomInfo API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error enriching company with ZoomInfo: {e}")
            return None
            
    def normalize_company_data(self, raw_data: Dict, source_api: str) -> CompanyData:
        """Normalize ZoomInfo company data"""
        return CompanyData(
            name=raw_data.get('companyName', ''),
            domain=raw_data.get('website', ''),
            description=raw_data.get('companyDescription'),
            industry=raw_data.get('primaryIndustry'),
            size=raw_data.get('employeeCount'),
            location=f"{raw_data.get('city', '')}, {raw_data.get('state', '')}".strip(', '),
            founded_year=raw_data.get('foundedYear'),
            revenue=raw_data.get('revenue'),
            technologies=raw_data.get('technologies', []) if raw_data.get('technologies') else None,
            website=raw_data.get('website'),
            phone=raw_data.get('phone'),
            source_api=source_api,
            confidence_score=0.85,  # ZoomInfo has good B2B data
            raw_data=raw_data
        )

class ApolloAPI(BaseCompanyEnrichmentAPI):
    """Apollo Company API Integration"""
    
    def __init__(self, api_key: str = None):
        super().__init__(
            api_key=api_key or os.getenv('APOLLO_API_KEY'),
            base_url='https://api.apollo.io/v1/'
        )
        
    async def enrich_company(self, domain: str = None, company_name: str = None) -> Optional[CompanyData]:
        """Enrich company data using Apollo API"""
        if not self.api_key:
            logger.warning("Apollo API key not provided, skipping")
            return None
            
        if not domain and not company_name:
            logger.warning("Either domain or company_name required for Apollo enrichment")
            return None
            
        try:
            headers = {
                'Cache-Control': 'no-cache',
                'Content-Type': 'application/json',
                'X-Api-Key': self.api_key
            }
            
            # Build query parameters
            params = {}
            if domain:
                params['domain'] = domain
            if company_name:
                params['name'] = company_name
                
            url = urljoin(self.base_url, 'organizations/enrich')
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    response_data = await response.json()
                    company_data = response_data.get('organization', {})
                    return self.normalize_company_data(company_data, 'apollo')
                elif response.status == 404:
                    logger.info(f"Company not found in Apollo: {domain or company_name}")
                    return None
                else:
                    logger.error(f"Apollo API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error enriching company with Apollo: {e}")
            return None
            
    def normalize_company_data(self, raw_data: Dict, source_api: str) -> CompanyData:
        """Normalize Apollo company data"""
        return CompanyData(
            name=raw_data.get('name', ''),
            domain=raw_data.get('website_url', ''),
            description=raw_data.get('short_description'),
            industry=raw_data.get('industry'),
            size=raw_data.get('estimated_num_employees'),
            location=f"{raw_data.get('city', '')}, {raw_data.get('state', '')}".strip(', '),
            founded_year=raw_data.get('founded_year'),
            revenue=raw_data.get('annual_revenue'),
            technologies=raw_data.get('technologies', []) if raw_data.get('technologies') else None,
            social_media={
                'linkedin': raw_data.get('linkedin_url'),
                'twitter': raw_data.get('twitter_url'),
                'facebook': raw_data.get('facebook_url'),
            },
            logo_url=raw_data.get('logo_url'),
            website=raw_data.get('website_url'),
            phone=raw_data.get('phone'),
            source_api=source_api,
            confidence_score=0.8,  # Apollo has decent coverage
            raw_data=raw_data
        )

class CompanyEnrichmentService:
    """Main service for company data enrichment using multiple APIs"""
    
    def __init__(self):
        self.apis = [
            ClearbitAPI(),
            ZoomInfoAPI(),
            ApolloAPI()
        ]
        
    async def enrich_company(self, domain: str = None, company_name: str = None) -> Optional[CompanyData]:
        """Try to enrich company data using multiple APIs in priority order"""
        
        for api in self.apis:
            try:
                async with api:
                    result = await api.enrich_company(domain=domain, company_name=company_name)
                    if result:
                        logger.info(f"Successfully enriched company using {result.source_api}")
                        return result
            except Exception as e:
                logger.error(f"Error with {api.__class__.__name__}: {e}")
                continue
                
        logger.warning(f"Could not enrich company: {domain or company_name}")
        return None
        
    async def batch_enrich_companies(self, companies: List[Dict[str, str]]) -> List[Optional[CompanyData]]:
        """Batch enrich multiple companies"""
        results = []
        
        for company in companies:
            domain = company.get('domain')
            name = company.get('name')
            result = await self.enrich_company(domain=domain, company_name=name)
            results.append(result)
            
        return results

# Demo/Testing Functions
async def demo_company_enrichment():
    """Demo function to test company enrichment"""
    print("🏢 Testing Company Enrichment APIs...")
    
    service = CompanyEnrichmentService()
    
    # Test companies
    test_companies = [
        {'domain': 'stripe.com', 'name': 'Stripe'},
        {'domain': 'openai.com', 'name': 'OpenAI'},
        {'domain': 'github.com', 'name': 'GitHub'},
    ]
    
    print(f"\n📊 Testing {len(test_companies)} companies...")
    
    for company in test_companies:
        print(f"\n🔍 Enriching: {company['name']} ({company['domain']})")
        
        result = await service.enrich_company(
            domain=company['domain'],
            company_name=company['name']
        )
        
        if result:
            print(f"✅ Success via {result.source_api}")
            print(f"   Industry: {result.industry}")
            print(f"   Size: {result.size}")
            print(f"   Location: {result.location}")
            print(f"   Founded: {result.founded_year}")
        else:
            print("❌ No data found")
            
    return test_companies

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_company_enrichment())
