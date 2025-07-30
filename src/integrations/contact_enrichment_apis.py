"""
Contact Enrichment API Integration Module

This module provides unified access to contact data enrichment APIs including:
- Hunter.io
- RocketReach
- ContactOut
- Custom contact data sources

All APIs are normalized to a common contact data format for consistent processing.
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
class ContactData:
    """Normalized contact data structure"""
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    domain: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    seniority: Optional[str] = None
    confidence_score: Optional[float] = None
    source_api: str = None
    verified: bool = False
    last_updated: Optional[datetime] = None
    raw_data: Optional[Dict] = None

class BaseContactEnrichmentAPI:
    """Base class for contact enrichment API integrations"""
    
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
            
    async def find_email(self, domain: str, first_name: str = None, last_name: str = None) -> List[ContactData]:
        """Override in subclasses"""
        raise NotImplementedError
        
    async def verify_email(self, email: str) -> bool:
        """Override in subclasses"""
        raise NotImplementedError

class HunterAPI(BaseContactEnrichmentAPI):
    """Hunter.io API Integration"""
    
    def __init__(self, api_key: str = None):
        super().__init__(
            api_key=api_key or os.getenv('HUNTER_API_KEY'),
            base_url='https://api.hunter.io/v2/'
        )
        
    async def find_email(self, domain: str, first_name: str = None, last_name: str = None) -> List[ContactData]:
        """Find email addresses using Hunter.io API"""
        if not self.api_key:
            logger.warning("Hunter.io API key not provided, skipping")
            return []
            
        try:
            params = {
                'domain': domain,
                'api_key': self.api_key
            }
            
            if first_name:
                params['first_name'] = first_name
            if last_name:
                params['last_name'] = last_name
                
            url = urljoin(self.base_url, 'email-finder')
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('data') and data['data'].get('email'):
                        contact = self.normalize_contact_data(data['data'], 'hunter')
                        return [contact]
                    else:
                        logger.info(f"No email found for {first_name} {last_name} at {domain}")
                        return []
                else:
                    logger.error(f"Hunter.io API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error finding email with Hunter.io: {e}")
            return []
            
    async def verify_email(self, email: str) -> bool:
        """Verify email address using Hunter.io"""
        if not self.api_key:
            return False
            
        try:
            params = {
                'email': email,
                'api_key': self.api_key
            }
            
            url = urljoin(self.base_url, 'email-verifier')
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get('data', {}).get('result', '')
                    return result in ['deliverable', 'risky']
                else:
                    return False
                    
        except Exception as e:
            logger.error(f"Error verifying email with Hunter.io: {e}")
            return False
            
    def normalize_contact_data(self, raw_data: Dict, source_api: str) -> ContactData:
        """Normalize Hunter.io contact data"""
        return ContactData(
            email=raw_data.get('email', ''),
            first_name=raw_data.get('first_name'),
            last_name=raw_data.get('last_name'),
            full_name=f"{raw_data.get('first_name', '')} {raw_data.get('last_name', '')}".strip(),
            title=raw_data.get('position'),
            company=raw_data.get('company'),
            domain=raw_data.get('domain'),
            phone=raw_data.get('phone_number'),
            linkedin_url=raw_data.get('linkedin_url'),
            twitter_url=raw_data.get('twitter'),
            confidence_score=raw_data.get('score', 0) / 100.0 if raw_data.get('score') else None,
            source_api=source_api,
            verified=raw_data.get('verification', {}).get('result') == 'deliverable' if raw_data.get('verification') else False,
            last_updated=datetime.now(),
            raw_data=raw_data
        )

class RocketReachAPI(BaseContactEnrichmentAPI):
    """RocketReach API Integration"""
    
    def __init__(self, api_key: str = None):
        super().__init__(
            api_key=api_key or os.getenv('ROCKETREACH_API_KEY'),
            base_url='https://api.rocketreach.co/v1/'
        )
        
    async def find_email(self, domain: str, first_name: str = None, last_name: str = None) -> List[ContactData]:
        """Find email addresses using RocketReach API"""
        if not self.api_key:
            logger.warning("RocketReach API key not provided, skipping")
            return []
            
        try:
            headers = {
                'Api-Key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # Build search query
            query_parts = []
            if first_name:
                query_parts.append(f'first_name:"{first_name}"')
            if last_name:
                query_parts.append(f'last_name:"{last_name}"')
            if domain:
                query_parts.append(f'current_employer:"{domain}"')
                
            body = {
                'query': ' AND '.join(query_parts),
                'start': 1,
                'page_size': 10
            }
            
            url = urljoin(self.base_url, 'search')
            
            async with self.session.post(url, headers=headers, json=body) as response:
                if response.status == 200:
                    data = await response.json()
                    profiles = data.get('profiles', [])
                    return [self.normalize_contact_data(profile, 'rocketreach') for profile in profiles]
                else:
                    logger.error(f"RocketReach API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error finding email with RocketReach: {e}")
            return []
            
    async def verify_email(self, email: str) -> bool:
        """RocketReach doesn't have a separate verification endpoint"""
        return True  # Assume emails from RocketReach are verified
        
    def normalize_contact_data(self, raw_data: Dict, source_api: str) -> ContactData:
        """Normalize RocketReach contact data"""
        emails = raw_data.get('emails', [])
        primary_email = emails[0].get('email') if emails else ''
        
        return ContactData(
            email=primary_email,
            first_name=raw_data.get('first_name'),
            last_name=raw_data.get('last_name'),
            full_name=raw_data.get('name'),
            title=raw_data.get('current_title'),
            company=raw_data.get('current_employer'),
            phone=raw_data.get('phones', [{}])[0].get('number') if raw_data.get('phones') else None,
            linkedin_url=raw_data.get('linkedin_url'),
            twitter_url=raw_data.get('twitter_url'),
            location=raw_data.get('location'),
            confidence_score=0.85,  # RocketReach generally has good data
            source_api=source_api,
            verified=True,  # Assume RocketReach data is verified
            last_updated=datetime.now(),
            raw_data=raw_data
        )

class ContactOutAPI(BaseContactEnrichmentAPI):
    """ContactOut API Integration"""
    
    def __init__(self, api_key: str = None):
        super().__init__(
            api_key=api_key or os.getenv('CONTACTOUT_API_KEY'),
            base_url='https://api.contactout.com/v1/'
        )
        
    async def find_email(self, domain: str, first_name: str = None, last_name: str = None) -> List[ContactData]:
        """Find email addresses using ContactOut API"""
        if not self.api_key:
            logger.warning("ContactOut API key not provided, skipping")
            return []
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # ContactOut typically works with LinkedIn URLs, so we'll search by name and company
            params = {
                'first_name': first_name,
                'last_name': last_name,
                'company_domain': domain
            }
            
            url = urljoin(self.base_url, 'search')
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    contacts = data.get('contacts', [])
                    return [self.normalize_contact_data(contact, 'contactout') for contact in contacts]
                else:
                    logger.error(f"ContactOut API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error finding email with ContactOut: {e}")
            return []
            
    async def verify_email(self, email: str) -> bool:
        """ContactOut doesn't have a separate verification endpoint"""
        return True  # Assume emails from ContactOut are verified
        
    def normalize_contact_data(self, raw_data: Dict, source_api: str) -> ContactData:
        """Normalize ContactOut contact data"""
        return ContactData(
            email=raw_data.get('email', ''),
            first_name=raw_data.get('first_name'),
            last_name=raw_data.get('last_name'),
            full_name=f"{raw_data.get('first_name', '')} {raw_data.get('last_name', '')}".strip(),
            title=raw_data.get('title'),
            company=raw_data.get('company'),
            domain=raw_data.get('company_domain'),
            phone=raw_data.get('phone'),
            linkedin_url=raw_data.get('linkedin_url'),
            location=raw_data.get('location'),
            department=raw_data.get('department'),
            seniority=raw_data.get('seniority'),
            confidence_score=raw_data.get('confidence_score', 0.8),
            source_api=source_api,
            verified=True,  # Assume ContactOut data is verified
            last_updated=datetime.now(),
            raw_data=raw_data
        )

class ContactEnrichmentService:
    """Main service for contact data enrichment using multiple APIs"""
    
    def __init__(self):
        self.apis = [
            HunterAPI(),
            RocketReachAPI(),
            ContactOutAPI()
        ]
        
    async def find_contact_email(self, domain: str, first_name: str = None, last_name: str = None) -> List[ContactData]:
        """Try to find contact email using multiple APIs"""
        all_contacts = []
        
        for api in self.apis:
            try:
                async with api:
                    contacts = await api.find_email(domain=domain, first_name=first_name, last_name=last_name)
                    if contacts:
                        all_contacts.extend(contacts)
                        logger.info(f"Found {len(contacts)} contacts using {api.__class__.__name__}")
            except Exception as e:
                logger.error(f"Error with {api.__class__.__name__}: {e}")
                continue
                
        # Deduplicate by email
        unique_contacts = {}
        for contact in all_contacts:
            if contact.email and contact.email not in unique_contacts:
                unique_contacts[contact.email] = contact
                
        return list(unique_contacts.values())
        
    async def verify_contact_email(self, email: str) -> bool:
        """Verify email using available APIs"""
        hunter_api = HunterAPI()
        
        try:
            async with hunter_api:
                return await hunter_api.verify_email(email)
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            return False
            
    async def batch_find_contacts(self, contact_requests: List[Dict[str, str]]) -> List[List[ContactData]]:
        """Batch find multiple contacts"""
        results = []
        
        for request in contact_requests:
            domain = request.get('domain')
            first_name = request.get('first_name')
            last_name = request.get('last_name')
            
            contacts = await self.find_contact_email(
                domain=domain,
                first_name=first_name,
                last_name=last_name
            )
            results.append(contacts)
            
        return results

# Demo/Testing Functions
async def demo_contact_enrichment():
    """Demo function to test contact enrichment"""
    print("📧 Testing Contact Enrichment APIs...")
    
    service = ContactEnrichmentService()
    
    # Test contacts
    test_contacts = [
        {'domain': 'stripe.com', 'first_name': 'Patrick', 'last_name': 'Collison'},
        {'domain': 'openai.com', 'first_name': 'Sam', 'last_name': 'Altman'},
        {'domain': 'github.com', 'first_name': 'Nat', 'last_name': 'Friedman'},
    ]
    
    print(f"\n📊 Testing {len(test_contacts)} contacts...")
    
    for contact_request in test_contacts:
        print(f"\n🔍 Finding: {contact_request['first_name']} {contact_request['last_name']} at {contact_request['domain']}")
        
        contacts = await service.find_contact_email(
            domain=contact_request['domain'],
            first_name=contact_request['first_name'],
            last_name=contact_request['last_name']
        )
        
        if contacts:
            print(f"✅ Found {len(contacts)} contact(s)")
            for contact in contacts:
                print(f"   📧 {contact.email} ({contact.source_api})")
                print(f"   💼 {contact.title} at {contact.company}")
                if contact.confidence_score:
                    print(f"   📊 Confidence: {contact.confidence_score:.2f}")
        else:
            print("❌ No contacts found")
            
    return test_contacts

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_contact_enrichment())
