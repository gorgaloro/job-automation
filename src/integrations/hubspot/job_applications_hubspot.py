#!/usr/bin/env python3
"""
HubSpot Integration for Job Applications

Real HubSpot CRM integration for creating deals, updating stages,
and syncing job application data with HubSpot CRM.
"""

import os
import sys
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from core.job_applications_engine import JobApplication, ApplicationStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobApplicationsHubSpotService:
    """HubSpot CRM integration for job applications"""
    
    def __init__(self):
        self.api_key = os.getenv('HUBSPOT_API_KEY')
        self.base_url = "https://api.hubapi.com"
        self.demo_mode = not self.api_key or os.getenv('DEMO_MODE', 'false').lower() == 'true'
        
        if self.demo_mode:
            logger.info("HubSpot service initialized in demo mode")
        else:
            logger.info("HubSpot service initialized with live API")
            self.headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
    
    def create_deal_for_application(self, application: JobApplication) -> Optional[str]:
        """Create a HubSpot deal for a job application"""
        try:
            if self.demo_mode:
                deal_id = f"deal_{application.application_id}"
                logger.info(f"Demo: Would create HubSpot deal {deal_id}")
                return deal_id
            
            # Create deal data
            deal_data = {
                "properties": {
                    "dealname": f"{application.job_title} - {application.company_name}",
                    "dealstage": self._get_hubspot_stage(application.status),
                    "amount": "0",  # Could be estimated salary
                    "closedate": self._get_close_date(application),
                    "pipeline": "default",
                    "dealtype": "newbusiness",
                    # Custom properties for job applications
                    "job_title": application.job_title,
                    "company_name": application.company_name,
                    "application_id": application.application_id,
                    "application_method": application.application_method.value,
                    "application_url": application.application_url or "",
                    "resume_version": application.resume_version_id,
                    "source": application.source or "",
                    "notes": application.notes or ""
                }
            }
            
            # Create deal via HubSpot API
            response = requests.post(
                f"{self.base_url}/crm/v3/objects/deals",
                headers=self.headers,
                json=deal_data
            )
            
            if response.status_code == 201:
                deal = response.json()
                deal_id = deal['id']
                logger.info(f"Created HubSpot deal {deal_id} for {application.job_title}")
                
                # Associate with company if exists
                self._associate_with_company(deal_id, application.company_name)
                
                return deal_id
            else:
                logger.error(f"Failed to create HubSpot deal: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"HubSpot deal creation failed: {e}")
            return None
    
    def update_deal_stage(self, deal_id: str, new_status: ApplicationStatus, 
                         notes: Optional[str] = None) -> bool:
        """Update HubSpot deal stage based on application status"""
        try:
            if self.demo_mode:
                logger.info(f"Demo: Would update deal {deal_id} to stage {new_status.value}")
                return True
            
            # Update deal stage
            update_data = {
                "properties": {
                    "dealstage": self._get_hubspot_stage(new_status),
                    "hs_lastmodifieddate": datetime.now().isoformat()
                }
            }
            
            # Add notes if provided
            if notes:
                update_data["properties"]["notes"] = notes
            
            response = requests.patch(
                f"{self.base_url}/crm/v3/objects/deals/{deal_id}",
                headers=self.headers,
                json=update_data
            )
            
            if response.status_code == 200:
                logger.info(f"Updated HubSpot deal {deal_id} stage to {new_status.value}")
                
                # Add note as engagement if provided
                if notes:
                    self._add_deal_note(deal_id, notes)
                
                return True
            else:
                logger.error(f"Failed to update HubSpot deal: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"HubSpot deal update failed: {e}")
            return False
    
    def get_deal_info(self, deal_id: str) -> Optional[Dict]:
        """Get HubSpot deal information"""
        try:
            if self.demo_mode:
                return {
                    "id": deal_id,
                    "properties": {
                        "dealname": "Demo Job Application",
                        "dealstage": "appointmentscheduled",
                        "amount": "0",
                        "closedate": "2024-02-01"
                    }
                }
            
            response = requests.get(
                f"{self.base_url}/crm/v3/objects/deals/{deal_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get HubSpot deal: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"HubSpot deal retrieval failed: {e}")
            return None
    
    def search_deals_by_application(self, application_id: str) -> List[Dict]:
        """Search for deals by application ID"""
        try:
            if self.demo_mode:
                return [{
                    "id": f"deal_{application_id}",
                    "properties": {
                        "dealname": "Demo Application Deal",
                        "application_id": application_id
                    }
                }]
            
            # Search for deals with matching application_id
            search_data = {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "application_id",
                        "operator": "EQ",
                        "value": application_id
                    }]
                }]
            }
            
            response = requests.post(
                f"{self.base_url}/crm/v3/objects/deals/search",
                headers=self.headers,
                json=search_data
            )
            
            if response.status_code == 200:
                return response.json().get('results', [])
            else:
                logger.error(f"Failed to search HubSpot deals: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"HubSpot deal search failed: {e}")
            return []
    
    def get_application_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics for job applications"""
        try:
            if self.demo_mode:
                return {
                    "total_deals": 25,
                    "by_stage": {
                        "qualifiedtobuy": 10,  # Submitted
                        "presentationscheduled": 5,  # In Review
                        "appointmentscheduled": 3,  # Interview Scheduled
                        "contractsent": 1,  # Offer Extended
                        "closedwon": 1,  # Accepted
                        "closedlost": 5  # Rejected
                    },
                    "total_value": 0,
                    "avg_deal_age": 7.5
                }
            
            # Get all job application deals
            search_data = {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "dealtype",
                        "operator": "EQ",
                        "value": "newbusiness"
                    }]
                }],
                "properties": ["dealstage", "createdate", "amount"]
            }
            
            response = requests.post(
                f"{self.base_url}/crm/v3/objects/deals/search",
                headers=self.headers,
                json=search_data
            )
            
            if response.status_code == 200:
                deals = response.json().get('results', [])
                return self._calculate_pipeline_stats(deals)
            else:
                logger.error(f"Failed to get pipeline stats: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Pipeline stats retrieval failed: {e}")
            return {}
    
    def _get_hubspot_stage(self, status: ApplicationStatus) -> str:
        """Map application status to HubSpot deal stage"""
        stage_mapping = {
            ApplicationStatus.SUBMITTED: "qualifiedtobuy",
            ApplicationStatus.IN_REVIEW: "presentationscheduled", 
            ApplicationStatus.INTERVIEW_SCHEDULED: "appointmentscheduled",
            ApplicationStatus.INTERVIEW_COMPLETED: "decisionmakerboughtin",
            ApplicationStatus.OFFER_EXTENDED: "contractsent",
            ApplicationStatus.REJECTED: "closedlost",
            ApplicationStatus.WITHDRAWN: "closedlost",
            ApplicationStatus.NO_RESPONSE: "closedlost",
            ApplicationStatus.GHOSTED: "closedlost"
        }
        return stage_mapping.get(status, "qualifiedtobuy")
    
    def _get_close_date(self, application: JobApplication) -> str:
        """Get estimated close date for deal"""
        # Estimate 30 days from submission
        from datetime import datetime, timedelta
        try:
            submitted_date = datetime.fromisoformat(application.submitted_at.replace('Z', '+00:00'))
            close_date = submitted_date + timedelta(days=30)
            return close_date.strftime('%Y-%m-%d')
        except:
            return (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    def _associate_with_company(self, deal_id: str, company_name: str) -> bool:
        """Associate deal with company record"""
        try:
            # Search for existing company
            search_data = {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "name",
                        "operator": "EQ",
                        "value": company_name
                    }]
                }]
            }
            
            response = requests.post(
                f"{self.base_url}/crm/v3/objects/companies/search",
                headers=self.headers,
                json=search_data
            )
            
            if response.status_code == 200:
                companies = response.json().get('results', [])
                if companies:
                    company_id = companies[0]['id']
                    
                    # Create association
                    association_data = {
                        "inputs": [{
                            "from": {"id": deal_id},
                            "to": {"id": company_id},
                            "type": "deal_to_company"
                        }]
                    }
                    
                    assoc_response = requests.post(
                        f"{self.base_url}/crm/v3/associations/deals/companies/batch/create",
                        headers=self.headers,
                        json=association_data
                    )
                    
                    if assoc_response.status_code == 201:
                        logger.info(f"Associated deal {deal_id} with company {company_name}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Company association failed: {e}")
            return False
    
    def _add_deal_note(self, deal_id: str, note_text: str) -> bool:
        """Add note to deal as engagement"""
        try:
            note_data = {
                "properties": {
                    "hs_note_body": note_text,
                    "hs_timestamp": datetime.now().isoformat()
                },
                "associations": [{
                    "to": {"id": deal_id},
                    "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 214}]
                }]
            }
            
            response = requests.post(
                f"{self.base_url}/crm/v3/objects/notes",
                headers=self.headers,
                json=note_data
            )
            
            if response.status_code == 201:
                logger.info(f"Added note to deal {deal_id}")
                return True
            else:
                logger.error(f"Failed to add note: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Note creation failed: {e}")
            return False
    
    def _calculate_pipeline_stats(self, deals: List[Dict]) -> Dict[str, Any]:
        """Calculate pipeline statistics from deals"""
        total_deals = len(deals)
        by_stage = {}
        total_value = 0
        
        for deal in deals:
            stage = deal['properties'].get('dealstage', 'unknown')
            by_stage[stage] = by_stage.get(stage, 0) + 1
            
            amount = deal['properties'].get('amount', '0')
            try:
                total_value += float(amount) if amount else 0
            except:
                pass
        
        return {
            "total_deals": total_deals,
            "by_stage": by_stage,
            "total_value": total_value,
            "avg_deal_age": 7.5  # Would calculate from actual dates
        }

# Demo functions
def demo_hubspot_integration():
    """Demo HubSpot integration functionality"""
    print("=== HubSpot Job Applications Integration Demo ===")
    
    service = JobApplicationsHubSpotService()
    
    # Create demo application
    from core.job_applications_engine import JobApplication, ApplicationStatus, ApplicationMethod
    
    demo_app = JobApplication(
        application_id="app_hubspot_demo",
        job_id="job_001",
        company_id="comp_001",
        user_id="demo_user",
        job_title="Senior Software Engineer",
        company_name="TechCorp",
        resume_version_id="resume_v1",
        application_method=ApplicationMethod.AUTO_APPLY,
        status=ApplicationStatus.SUBMITTED,
        application_url="https://techcorp.com/jobs/senior-engineer",
        source="company_website",
        notes="Auto-submitted via AI automation"
    )
    
    print("\n1. Creating HubSpot Deal...")
    deal_id = service.create_deal_for_application(demo_app)
    if deal_id:
        print(f"  SUCCESS: Created deal {deal_id}")
        print(f"  Deal Name: {demo_app.job_title} - {demo_app.company_name}")
        print(f"  Stage: {service._get_hubspot_stage(demo_app.status)}")
    
    print("\n2. Updating Deal Stage...")
    if deal_id:
        success = service.update_deal_stage(
            deal_id,
            ApplicationStatus.INTERVIEW_SCHEDULED,
            "Phone screen scheduled for next week"
        )
        if success:
            print(f"  SUCCESS: Updated to interview_scheduled")
            print(f"  Notes: Phone screen scheduled for next week")
    
    print("\n3. Getting Deal Info...")
    if deal_id:
        deal_info = service.get_deal_info(deal_id)
        if deal_info:
            print(f"  Deal ID: {deal_info['id']}")
            print(f"  Deal Name: {deal_info['properties'].get('dealname', 'N/A')}")
            print(f"  Stage: {deal_info['properties'].get('dealstage', 'N/A')}")
    
    print("\n4. Pipeline Statistics...")
    stats = service.get_application_pipeline_stats()
    if stats:
        print(f"  Total Deals: {stats['total_deals']}")
        print(f"  By Stage:")
        for stage, count in stats['by_stage'].items():
            print(f"    {stage}: {count}")
        print(f"  Average Deal Age: {stats['avg_deal_age']} days")
    
    print("\n5. Searching Deals...")
    deals = service.search_deals_by_application("app_hubspot_demo")
    print(f"  Found {len(deals)} deals for application")
    
    print("\n✅ HubSpot Integration Demo Complete!")

if __name__ == "__main__":
    demo_hubspot_integration()
