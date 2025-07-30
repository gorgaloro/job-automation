"""
LinkedIn Contact Extraction Module

This module provides multiple methods for extracting LinkedIn contact information
while respecting LinkedIn's Terms of Service and API limitations.

Methods:
1. Official LinkedIn API (recommended)
2. Data export file processing
3. Browser automation (use with caution)
4. Integration with existing CRM systems
"""

import os
import csv
import json
import requests
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LinkedIn API Configuration
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

@dataclass
class LinkedInContact:
    """LinkedIn contact data structure"""
    first_name: str
    last_name: str
    headline: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    profile_url: Optional[str] = None
    connection_date: Optional[datetime] = None
    mutual_connections: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export"""
        return {
            "full_name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "headline": self.headline,
            "company": self.company,
            "position": self.position,
            "location": self.location,
            "industry": self.industry,
            "profile_url": self.profile_url,
            "connection_date": self.connection_date.isoformat() if self.connection_date else None,
            "mutual_connections": self.mutual_connections,
            "email": self.email,
            "phone": self.phone,
            "notes": self.notes
        }

class LinkedInContactExtractor:
    """LinkedIn contact extraction service"""
    
    def __init__(self):
        self.client_id = LINKEDIN_CLIENT_ID
        self.client_secret = LINKEDIN_CLIENT_SECRET
        self.access_token = LINKEDIN_ACCESS_TOKEN
        
    def extract_from_data_export(self, csv_file_path: str) -> List[LinkedInContact]:
        """
        Extract contacts from LinkedIn's official data export CSV
        
        Args:
            csv_file_path: Path to LinkedIn connections CSV export
            
        Returns:
            List of LinkedInContact objects
        """
        contacts = []
        
        try:
            logger.info(f"Processing LinkedIn data export: {csv_file_path}")
            
            # Read CSV file
            df = pd.read_csv(csv_file_path)
            
            # Expected columns in LinkedIn export:
            # First Name, Last Name, Email Address, Company, Position, Connected On
            
            for _, row in df.iterrows():
                contact = LinkedInContact(
                    first_name=row.get("First Name", ""),
                    last_name=row.get("Last Name", ""),
                    company=row.get("Company", ""),
                    position=row.get("Position", ""),
                    email=row.get("Email Address", ""),
                    connection_date=self._parse_connection_date(row.get("Connected On", ""))
                )
                contacts.append(contact)
            
            logger.info(f"✅ Extracted {len(contacts)} contacts from data export")
            return contacts
            
        except Exception as e:
            logger.error(f"❌ Failed to process data export: {e}")
            return []
    
    def extract_via_api(self, limit: int = 500) -> List[LinkedInContact]:
        """
        Extract contacts using LinkedIn API (requires proper authentication)
        
        Args:
            limit: Maximum number of connections to retrieve
            
        Returns:
            List of LinkedInContact objects
        """
        if not self.access_token:
            logger.error("LinkedIn access token not configured")
            return []
        
        contacts = []
        
        try:
            # LinkedIn API endpoint for connections
            url = "https://api.linkedin.com/v2/connections"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "count": min(limit, 500),  # LinkedIn API limit
                "start": 0
            }
            
            logger.info(f"Fetching connections via LinkedIn API (limit: {limit})")
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])
                
                for element in elements:
                    # Parse LinkedIn API response
                    contact = self._parse_api_contact(element)
                    if contact:
                        contacts.append(contact)
                
                logger.info(f"✅ Extracted {len(contacts)} contacts via API")
            else:
                logger.error(f"❌ LinkedIn API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Failed to extract via API: {e}")
        
        return contacts
    
    def enrich_contacts_with_company_data(self, contacts: List[LinkedInContact]) -> List[LinkedInContact]:
        """
        Enrich contacts with additional company information
        
        Args:
            contacts: List of contacts to enrich
            
        Returns:
            Enriched contacts with company data
        """
        logger.info(f"Enriching {len(contacts)} contacts with company data")
        
        for contact in contacts:
            if contact.company:
                # Add company enrichment logic here
                # This could integrate with your existing company enrichment engine
                try:
                    # Example: Get company size, industry, etc.
                    company_info = self._get_company_info(contact.company)
                    if company_info:
                        contact.industry = company_info.get("industry")
                        # Add other enriched fields as needed
                except Exception as e:
                    logger.warning(f"Failed to enrich company data for {contact.company}: {e}")
        
        return contacts
    
    def filter_contacts_by_criteria(self, contacts: List[LinkedInContact], 
                                  criteria: Dict[str, Any]) -> List[LinkedInContact]:
        """
        Filter contacts based on job search criteria
        
        Args:
            contacts: List of contacts to filter
            criteria: Filtering criteria (companies, industries, positions, etc.)
            
        Returns:
            Filtered list of contacts
        """
        filtered = []
        
        target_companies = criteria.get("companies", [])
        target_industries = criteria.get("industries", [])
        target_positions = criteria.get("positions", [])
        
        for contact in contacts:
            include = True
            
            # Filter by company
            if target_companies and contact.company:
                if not any(company.lower() in contact.company.lower() 
                          for company in target_companies):
                    include = False
            
            # Filter by industry
            if target_industries and contact.industry:
                if not any(industry.lower() in contact.industry.lower() 
                          for industry in target_industries):
                    include = False
            
            # Filter by position
            if target_positions and contact.position:
                if not any(position.lower() in contact.position.lower() 
                          for position in target_positions):
                    include = False
            
            if include:
                filtered.append(contact)
        
        logger.info(f"Filtered {len(contacts)} contacts down to {len(filtered)} matches")
        return filtered
    
    def export_contacts(self, contacts: List[LinkedInContact], 
                       output_file: str, format: str = "csv") -> bool:
        """
        Export contacts to file
        
        Args:
            contacts: List of contacts to export
            output_file: Output file path
            format: Export format ("csv", "json", "excel")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if format.lower() == "csv":
                self._export_to_csv(contacts, output_file)
            elif format.lower() == "json":
                self._export_to_json(contacts, output_file)
            elif format.lower() == "excel":
                self._export_to_excel(contacts, output_file)
            else:
                logger.error(f"Unsupported export format: {format}")
                return False
            
            logger.info(f"✅ Exported {len(contacts)} contacts to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export contacts: {e}")
            return False
    
    def _parse_connection_date(self, date_str: str) -> Optional[datetime]:
        """Parse connection date from various formats"""
        if not date_str:
            return None
        
        try:
            # Try common date formats
            for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%d %b %Y"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        except Exception:
            pass
        
        return None
    
    def _parse_api_contact(self, element: Dict[str, Any]) -> Optional[LinkedInContact]:
        """Parse contact from LinkedIn API response"""
        try:
            # Extract data from LinkedIn API response structure
            # Note: Actual structure depends on LinkedIn API version and permissions
            
            first_name = element.get("firstName", {}).get("localized", {}).get("en_US", "")
            last_name = element.get("lastName", {}).get("localized", {}).get("en_US", "")
            
            contact = LinkedInContact(
                first_name=first_name,
                last_name=last_name,
                headline=element.get("headline", {}).get("localized", {}).get("en_US", ""),
                profile_url=element.get("publicProfileUrl", "")
            )
            
            return contact
            
        except Exception as e:
            logger.warning(f"Failed to parse API contact: {e}")
            return None
    
    def _get_company_info(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Get company information for enrichment"""
        # This would integrate with your existing company enrichment engine
        # For now, return None - implement based on your existing services
        return None
    
    def _export_to_csv(self, contacts: List[LinkedInContact], output_file: str):
        """Export contacts to CSV"""
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            if not contacts:
                return
            
            fieldnames = contacts[0].to_dict().keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for contact in contacts:
                writer.writerow(contact.to_dict())
    
    def _export_to_json(self, contacts: List[LinkedInContact], output_file: str):
        """Export contacts to JSON"""
        data = [contact.to_dict() for contact in contacts]
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
    
    def _export_to_excel(self, contacts: List[LinkedInContact], output_file: str):
        """Export contacts to Excel"""
        data = [contact.to_dict() for contact in contacts]
        df = pd.DataFrame(data)
        df.to_excel(output_file, index=False)

class LinkedInNetworkAnalyzer:
    """Analyze LinkedIn network for job search opportunities"""
    
    def __init__(self, contacts: List[LinkedInContact]):
        self.contacts = contacts
    
    def find_target_company_connections(self, target_companies: List[str]) -> Dict[str, List[LinkedInContact]]:
        """Find connections at target companies"""
        company_connections = {}
        
        for company in target_companies:
            connections = [
                contact for contact in self.contacts
                if contact.company and company.lower() in contact.company.lower()
            ]
            if connections:
                company_connections[company] = connections
        
        return company_connections
    
    def find_referral_opportunities(self, job_companies: List[str]) -> List[Dict[str, Any]]:
        """Find potential referral opportunities"""
        opportunities = []
        
        for company in job_companies:
            connections = [
                contact for contact in self.contacts
                if contact.company and company.lower() in contact.company.lower()
            ]
            
            for contact in connections:
                opportunities.append({
                    "company": company,
                    "contact": contact,
                    "referral_potential": self._calculate_referral_potential(contact),
                    "suggested_approach": self._suggest_approach(contact)
                })
        
        # Sort by referral potential
        opportunities.sort(key=lambda x: x["referral_potential"], reverse=True)
        return opportunities
    
    def _calculate_referral_potential(self, contact: LinkedInContact) -> float:
        """Calculate referral potential score (0-1)"""
        score = 0.5  # Base score
        
        # Higher score for recent connections
        if contact.connection_date:
            days_since_connection = (datetime.now() - contact.connection_date).days
            if days_since_connection < 365:  # Connected within last year
                score += 0.2
        
        # Higher score for senior positions
        if contact.position:
            senior_keywords = ["director", "manager", "lead", "senior", "vp", "chief"]
            if any(keyword in contact.position.lower() for keyword in senior_keywords):
                score += 0.2
        
        # Higher score for mutual connections
        if contact.mutual_connections and contact.mutual_connections > 5:
            score += 0.1
        
        return min(score, 1.0)
    
    def _suggest_approach(self, contact: LinkedInContact) -> str:
        """Suggest approach for reaching out"""
        if contact.connection_date and (datetime.now() - contact.connection_date).days < 90:
            return "Recent connection - casual check-in message"
        elif "manager" in contact.position.lower() or "director" in contact.position.lower():
            return "Professional inquiry about team opportunities"
        else:
            return "Informational interview request"

# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = LinkedInContactExtractor()
    
    # Method 1: Process LinkedIn data export
    print("Processing LinkedIn data export...")
    contacts = extractor.extract_from_data_export("linkedin_connections.csv")
    
    # Method 2: Extract via API (if configured)
    # contacts = extractor.extract_via_api(limit=1000)
    
    # Enrich with company data
    contacts = extractor.enrich_contacts_with_company_data(contacts)
    
    # Filter for job search targets
    criteria = {
        "companies": ["Google", "Microsoft", "Apple", "Meta", "Amazon"],
        "industries": ["Technology", "Software"],
        "positions": ["Product Manager", "Engineering Manager", "Director"]
    }
    
    filtered_contacts = extractor.filter_contacts_by_criteria(contacts, criteria)
    
    # Export results
    extractor.export_contacts(filtered_contacts, "target_contacts.csv", "csv")
    extractor.export_contacts(filtered_contacts, "target_contacts.json", "json")
    
    # Analyze network for opportunities
    analyzer = LinkedInNetworkAnalyzer(contacts)
    
    target_companies = ["Stripe", "Notion", "Figma", "Airbnb"]
    company_connections = analyzer.find_target_company_connections(target_companies)
    
    print(f"\nTarget company connections found:")
    for company, connections in company_connections.items():
        print(f"- {company}: {len(connections)} connections")
    
    # Find referral opportunities
    referral_ops = analyzer.find_referral_opportunities(target_companies)
    
    print(f"\nTop 5 referral opportunities:")
    for i, opp in enumerate(referral_ops[:5]):
        contact = opp["contact"]
        print(f"{i+1}. {contact.full_name} at {opp['company']} ({contact.position})")
        print(f"   Potential: {opp['referral_potential']:.2f} - {opp['suggested_approach']}")
