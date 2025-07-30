#!/usr/bin/env python3
"""
Company Enrichment Database Service

Supabase integration for storing and managing enriched company data
and tech stack classifications.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.integrations.supabase.supabase_client import get_supabase_client
from src.core.company_enrichment_engine import CompanyEnrichmentEngine, CompanyEnrichmentData, TechClassification

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompanyEnrichmentDatabaseService:
    """Database service for company enrichment data"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.enrichment_engine = CompanyEnrichmentEngine()
        self.demo_mode = not self.supabase
        
        logger.info(f"Company Enrichment DB Service initialized (demo_mode: {self.demo_mode})")
    
    def store_enriched_company(self, enriched_data: CompanyEnrichmentData) -> Optional[str]:
        """
        Store enriched company data in Supabase
        
        Args:
            enriched_data: CompanyEnrichmentData object
            
        Returns:
            Company ID if successful, None if failed
        """
        try:
            if self.demo_mode:
                logger.info(f"Demo mode: Would store enriched data for {enriched_data.name}")
                return enriched_data.company_id
            
            # Prepare data for database storage
            company_record = {
                "id": enriched_data.company_id,
                "name": enriched_data.name,
                "domain": enriched_data.domain,
                "industry": enriched_data.industry,
                "size_range": enriched_data.size_range,
                "employee_count": enriched_data.employee_count,
                "funding_stage": enriched_data.funding_stage,
                "funding_amount": enriched_data.funding_amount,
                "valuation": enriched_data.valuation,
                "headquarters": enriched_data.headquarters,
                "founded_year": enriched_data.founded_year,
                "values": enriched_data.values,
                "culture_summary": enriched_data.culture_summary,
                "competitors": enriched_data.competitors,
                "glassdoor_rating": enriched_data.glassdoor_rating,
                "growth_stage": enriched_data.growth_stage,
                "remote_policy": enriched_data.remote_policy,
                "confidence_score": enriched_data.confidence_score,
                "enrichment_timestamp": enriched_data.enrichment_timestamp,
                "social_links": enriched_data.social_links,
                "recent_news": enriched_data.recent_news,
                "key_people": enriched_data.key_people
            }
            
            # Store main company record
            result = self.supabase.table("enriched_companies").upsert(company_record).execute()
            
            # Store tech classification separately
            if enriched_data.tech_classification:
                self._store_tech_classification(enriched_data.company_id, enriched_data.tech_classification)
            
            logger.info(f"Stored enriched company data for {enriched_data.name}")
            return enriched_data.company_id
            
        except Exception as e:
            logger.error(f"Failed to store enriched company data: {e}")
            return None
    
    def _store_tech_classification(self, company_id: str, tech_classification: TechClassification):
        """Store tech classification data"""
        try:
            tech_record = {
                "company_id": company_id,
                "primary_vertical": tech_classification.primary_vertical,
                "secondary_verticals": tech_classification.secondary_verticals,
                "tech_stack": tech_classification.tech_stack,
                "programming_languages": tech_classification.programming_languages,
                "frameworks": tech_classification.frameworks,
                "databases": tech_classification.databases,
                "cloud_platforms": tech_classification.cloud_platforms,
                "confidence_score": tech_classification.confidence_score,
                "classification_rationale": tech_classification.classification_rationale,
                "classification_timestamp": datetime.now().isoformat()
            }
            
            self.supabase.table("company_tech_classifications").upsert(tech_record).execute()
            logger.info(f"Stored tech classification for company {company_id}")
            
        except Exception as e:
            logger.error(f"Failed to store tech classification: {e}")
    
    def get_enriched_company(self, company_id: str) -> Optional[Dict]:
        """
        Retrieve enriched company data
        
        Args:
            company_id: Company ID to retrieve
            
        Returns:
            Company data dictionary or None
        """
        try:
            if self.demo_mode:
                return self._get_demo_company_data(company_id)
            
            # Get main company data
            company_result = self.supabase.table("enriched_companies").select("*").eq("id", company_id).execute()
            
            if not company_result.data:
                return None
            
            company_data = company_result.data[0]
            
            # Get tech classification
            tech_result = self.supabase.table("company_tech_classifications").select("*").eq("company_id", company_id).execute()
            
            if tech_result.data:
                company_data["tech_classification"] = tech_result.data[0]
            
            return company_data
            
        except Exception as e:
            logger.error(f"Failed to retrieve company data: {e}")
            return None
    
    def search_companies_by_tech_vertical(self, vertical: str, limit: int = 10) -> List[Dict]:
        """
        Search companies by tech vertical
        
        Args:
            vertical: Tech vertical to search for
            limit: Maximum number of results
            
        Returns:
            List of company data dictionaries
        """
        try:
            if self.demo_mode:
                return self._get_demo_companies_by_vertical(vertical, limit)
            
            # Search by primary vertical
            primary_result = self.supabase.table("company_tech_classifications")\
                .select("*, enriched_companies(*)")\
                .eq("primary_vertical", vertical)\
                .limit(limit)\
                .execute()
            
            # Search by secondary verticals
            secondary_result = self.supabase.table("company_tech_classifications")\
                .select("*, enriched_companies(*)")\
                .contains("secondary_verticals", [vertical])\
                .limit(limit)\
                .execute()
            
            # Combine and deduplicate results
            all_results = primary_result.data + secondary_result.data
            seen_companies = set()
            unique_results = []
            
            for result in all_results:
                company_id = result.get("company_id")
                if company_id not in seen_companies:
                    seen_companies.add(company_id)
                    unique_results.append(result)
            
            return unique_results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search companies by tech vertical: {e}")
            return []
    
    def get_tech_vertical_stats(self) -> Dict[str, Any]:
        """
        Get statistics about tech verticals in the database
        
        Returns:
            Dictionary with tech vertical statistics
        """
        try:
            if self.demo_mode:
                return self._get_demo_tech_stats()
            
            # Get all tech classifications
            result = self.supabase.table("company_tech_classifications").select("primary_vertical, secondary_verticals").execute()
            
            if not result.data:
                return {"total_companies": 0, "verticals": {}}
            
            # Count verticals
            vertical_counts = {}
            total_companies = len(result.data)
            
            for record in result.data:
                primary = record.get("primary_vertical")
                if primary:
                    vertical_counts[primary] = vertical_counts.get(primary, 0) + 1
                
                secondaries = record.get("secondary_verticals", [])
                for secondary in secondaries:
                    vertical_counts[secondary] = vertical_counts.get(secondary, 0) + 1
            
            return {
                "total_companies": total_companies,
                "verticals": vertical_counts,
                "top_verticals": sorted(vertical_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            }
            
        except Exception as e:
            logger.error(f"Failed to get tech vertical stats: {e}")
            return {"total_companies": 0, "verticals": {}, "error": str(e)}
    
    def enrich_and_store_company(self, company_name: str, domain: Optional[str] = None,
                                existing_data: Optional[Dict] = None) -> Optional[str]:
        """
        Enrich company data and store in database
        
        Args:
            company_name: Company name to enrich
            domain: Company domain
            existing_data: Any existing company data
            
        Returns:
            Company ID if successful, None if failed
        """
        try:
            logger.info(f"Enriching and storing company: {company_name}")
            
            # Enrich company data
            enriched_data = self.enrichment_engine.enrich_company(company_name, domain, existing_data)
            
            # Store in database
            company_id = self.store_enriched_company(enriched_data)
            
            if company_id:
                logger.info(f"Successfully enriched and stored {company_name} with ID: {company_id}")
            
            return company_id
            
        except Exception as e:
            logger.error(f"Failed to enrich and store company {company_name}: {e}")
            return None
    
    def batch_enrich_companies(self, companies: List[Dict]) -> Dict[str, Any]:
        """
        Batch enrich multiple companies
        
        Args:
            companies: List of company dictionaries with 'name' and optional 'domain'
            
        Returns:
            Dictionary with batch processing results
        """
        try:
            logger.info(f"Batch enriching {len(companies)} companies")
            
            results = {
                "successful": [],
                "failed": [],
                "total_processed": len(companies),
                "success_rate": 0.0
            }
            
            for company_info in companies:
                company_name = company_info.get("name")
                domain = company_info.get("domain")
                
                if not company_name:
                    results["failed"].append({"company": company_info, "error": "Missing company name"})
                    continue
                
                company_id = self.enrich_and_store_company(company_name, domain)
                
                if company_id:
                    results["successful"].append({
                        "company_name": company_name,
                        "company_id": company_id,
                        "domain": domain
                    })
                else:
                    results["failed"].append({
                        "company": company_info,
                        "error": "Enrichment failed"
                    })
            
            results["success_rate"] = len(results["successful"]) / len(companies) if companies else 0.0
            
            logger.info(f"Batch enrichment complete: {len(results['successful'])}/{len(companies)} successful")
            return results
            
        except Exception as e:
            logger.error(f"Batch enrichment failed: {e}")
            return {
                "successful": [],
                "failed": companies,
                "total_processed": len(companies),
                "success_rate": 0.0,
                "error": str(e)
            }
    
    def update_company_from_hubspot(self, hubspot_company_data: Dict) -> Optional[str]:
        """
        Update company enrichment data from HubSpot
        
        Args:
            hubspot_company_data: Company data from HubSpot
            
        Returns:
            Company ID if successful, None if failed
        """
        try:
            company_name = hubspot_company_data.get("name")
            domain = hubspot_company_data.get("domain")
            
            if not company_name:
                logger.error("No company name in HubSpot data")
                return None
            
            # Check if company already exists
            existing_company = self.get_enriched_company_by_name(company_name)
            
            if existing_company:
                # Update existing company with HubSpot data
                logger.info(f"Updating existing company: {company_name}")
                return self._update_existing_company(existing_company["id"], hubspot_company_data)
            else:
                # Enrich new company
                logger.info(f"Enriching new company from HubSpot: {company_name}")
                return self.enrich_and_store_company(company_name, domain, hubspot_company_data)
                
        except Exception as e:
            logger.error(f"Failed to update company from HubSpot: {e}")
            return None
    
    def get_enriched_company_by_name(self, company_name: str) -> Optional[Dict]:
        """Get enriched company by name"""
        try:
            if self.demo_mode:
                return self._get_demo_company_by_name(company_name)
            
            result = self.supabase.table("enriched_companies").select("*").eq("name", company_name).execute()
            
            if result.data:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get company by name: {e}")
            return None
    
    def _update_existing_company(self, company_id: str, hubspot_data: Dict) -> str:
        """Update existing company with HubSpot data"""
        try:
            # Merge HubSpot data with existing enrichment
            update_data = {
                "hubspot_data": hubspot_data,
                "last_hubspot_sync": datetime.now().isoformat()
            }
            
            if not self.demo_mode:
                self.supabase.table("enriched_companies").update(update_data).eq("id", company_id).execute()
            
            logger.info(f"Updated company {company_id} with HubSpot data")
            return company_id
            
        except Exception as e:
            logger.error(f"Failed to update existing company: {e}")
            return company_id
    
    # Demo mode methods
    def _get_demo_company_data(self, company_id: str) -> Dict:
        """Get demo company data"""
        return {
            "id": company_id,
            "name": "Demo Company",
            "industry": "technology",
            "confidence_score": 0.85,
            "tech_classification": {
                "primary_vertical": "saas",
                "confidence_score": 0.80
            }
        }
    
    def _get_demo_companies_by_vertical(self, vertical: str, limit: int) -> List[Dict]:
        """Get demo companies by vertical"""
        demo_companies = [
            {"name": f"Demo {vertical.title()} Company {i}", "primary_vertical": vertical}
            for i in range(1, min(limit + 1, 4))
        ]
        return demo_companies
    
    def _get_demo_tech_stats(self) -> Dict:
        """Get demo tech statistics"""
        return {
            "total_companies": 25,
            "verticals": {
                "fintech": 8,
                "healthtech": 6,
                "saas": 5,
                "developer-tools": 4,
                "ai-ml": 2
            },
            "top_verticals": [
                ("fintech", 8),
                ("healthtech", 6),
                ("saas", 5)
            ]
        }
    
    def _get_demo_company_by_name(self, company_name: str) -> Dict:
        """Get demo company by name"""
        return {
            "id": f"demo_{company_name.lower().replace(' ', '_')}",
            "name": company_name,
            "industry": "technology",
            "confidence_score": 0.85
        }

# Demo functions
def demo_company_enrichment_service():
    """Demo the company enrichment database service"""
    print("=== Company Enrichment Database Service Demo ===")
    
    service = CompanyEnrichmentDatabaseService()
    
    # Demo 1: Enrich and store companies
    print("\n1. Enriching and storing companies...")
    companies = ["TechCorp", "DataFlow", "CloudScale"]
    
    for company in companies:
        company_id = service.enrich_and_store_company(company)
        print(f"  ✅ {company} -> {company_id}")
    
    # Demo 2: Search by tech vertical
    print("\n2. Searching companies by tech vertical...")
    fintech_companies = service.search_companies_by_tech_vertical("fintech")
    print(f"  Found {len(fintech_companies)} fintech companies")
    
    # Demo 3: Get tech vertical statistics
    print("\n3. Tech vertical statistics...")
    stats = service.get_tech_vertical_stats()
    print(f"  Total companies: {stats['total_companies']}")
    print(f"  Top verticals: {stats.get('top_verticals', [])[:3]}")
    
    # Demo 4: Batch enrichment
    print("\n4. Batch enrichment...")
    batch_companies = [
        {"name": "StartupX", "domain": "startupx.com"},
        {"name": "ScaleY", "domain": "scaley.io"},
        {"name": "GrowthZ"}
    ]
    
    batch_results = service.batch_enrich_companies(batch_companies)
    print(f"  Batch success rate: {batch_results['success_rate']:.1%}")
    print(f"  Successful: {len(batch_results['successful'])}")
    print(f"  Failed: {len(batch_results['failed'])}")

if __name__ == "__main__":
    demo_company_enrichment_service()
