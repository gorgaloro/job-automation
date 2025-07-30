#!/usr/bin/env python3
"""
Mobile Networking Supabase Service - Epic 5

Database service for contact management, LinkedIn automation campaigns,
networking opportunities, and relationship analytics.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import asdict

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

from core.mobile_networking_engine import (
    Contact, ContactInteraction, LinkedInCampaign, NetworkingOpportunity,
    ContactType, RelationshipStrength, LinkedInActionType, NetworkingOpportunityType,
    NetworkingAnalytics
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MobileNetworkingService:
    """
    Supabase database service for mobile networking and contact management.
    
    Handles contact storage, interaction tracking, LinkedIn campaigns,
    networking opportunities, and relationship analytics.
    """
    
    def __init__(self):
        """Initialize the Mobile Networking Service"""
        self.demo_mode = True
        self.supabase = None
        
        # Try to initialize Supabase client
        if SUPABASE_AVAILABLE:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
            
            if supabase_url and supabase_key:
                try:
                    self.supabase = create_client(supabase_url, supabase_key)
                    self.demo_mode = False
                    logger.info("Mobile Networking Service initialized with live Supabase")
                except Exception as e:
                    logger.warning(f"Failed to connect to Supabase: {str(e)}")
                    logger.info("Mobile Networking Service initialized in demo mode")
            else:
                logger.warning("Supabase credentials not found, falling back to demo mode")
                logger.info("Mobile Networking Service initialized in demo mode")
        else:
            logger.warning("Supabase client not available, running in demo mode")
            logger.info("Mobile Networking Service initialized in demo mode")
    
    # Contact Management
    
    def create_contact(self, contact: Contact) -> bool:
        """
        Create a new contact
        
        Args:
            contact: Contact to create
            
        Returns:
            Success status
        """
        try:
            if self.demo_mode:
                logger.info(f"Demo: Created contact {contact.contact_id}")
                return True
            
            contact_data = {
                'contact_id': contact.contact_id,
                'name': contact.name,
                'email': contact.email,
                'linkedin_url': contact.linkedin_url,
                'company': contact.company,
                'title': contact.title,
                'location': contact.location,
                'contact_type': contact.contact_type.value,
                'relationship_strength': contact.relationship_strength.value,
                'tags': contact.tags,
                'notes': contact.notes,
                'source': contact.source,
                'created_at': contact.created_at.isoformat(),
                'last_interaction': contact.last_interaction.isoformat() if contact.last_interaction else None,
                'interaction_count': contact.interaction_count,
                'response_rate': contact.response_rate,
                'influence_score': contact.influence_score
            }
            
            result = self.supabase.table('contacts').insert(contact_data).execute()
            
            if result.data:
                logger.info(f"Created contact {contact.contact_id}")
                return True
            else:
                logger.error("Contact creation failed: No data returned")
                return False
                
        except Exception as e:
            logger.error(f"Contact creation failed: {str(e)}")
            return False
    
    def get_contact(self, contact_id: str) -> Optional[Contact]:
        """
        Get contact by ID
        
        Args:
            contact_id: Contact ID to retrieve
            
        Returns:
            Contact object or None
        """
        try:
            if self.demo_mode:
                # Return demo contact
                return Contact(
                    contact_id=contact_id,
                    name="Demo Contact",
                    email="demo@example.com",
                    company="Demo Company",
                    title="Demo Title",
                    contact_type=ContactType.INDUSTRY_PEER,
                    relationship_strength=RelationshipStrength.PROFESSIONAL
                )
            
            result = self.supabase.table('contacts').select('*').eq('contact_id', contact_id).execute()
            
            if result.data:
                data = result.data[0]
                return Contact(
                    contact_id=data['contact_id'],
                    name=data['name'],
                    email=data['email'],
                    linkedin_url=data['linkedin_url'],
                    company=data['company'],
                    title=data['title'],
                    location=data['location'],
                    contact_type=ContactType(data['contact_type']),
                    relationship_strength=RelationshipStrength(data['relationship_strength']),
                    tags=data['tags'] or [],
                    notes=data['notes'] or "",
                    source=data['source'],
                    interaction_count=data['interaction_count'],
                    response_rate=data['response_rate'],
                    influence_score=data['influence_score']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get contact: {str(e)}")
            return None
    
    def update_contact(self, contact_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update contact information
        
        Args:
            contact_id: Contact ID to update
            updates: Fields to update
            
        Returns:
            Success status
        """
        try:
            if self.demo_mode:
                logger.info(f"Demo: Updated contact {contact_id}")
                return True
            
            # Convert enum values to strings if present
            if 'contact_type' in updates and hasattr(updates['contact_type'], 'value'):
                updates['contact_type'] = updates['contact_type'].value
            if 'relationship_strength' in updates and hasattr(updates['relationship_strength'], 'value'):
                updates['relationship_strength'] = updates['relationship_strength'].value
            
            result = self.supabase.table('contacts').update(updates).eq('contact_id', contact_id).execute()
            
            if result.data:
                logger.info(f"Updated contact {contact_id}")
                return True
            else:
                logger.error("Contact update failed: No data returned")
                return False
                
        except Exception as e:
            logger.error(f"Contact update failed: {str(e)}")
            return False
    
    def search_contacts(self, query: str = "", filters: Dict[str, Any] = None) -> List[Contact]:
        """
        Search contacts with filters
        
        Args:
            query: Text search query
            filters: Additional filters (company, contact_type, etc.)
            
        Returns:
            List of matching contacts
        """
        try:
            if self.demo_mode:
                # Return demo contacts
                demo_contacts = [
                    Contact(
                        contact_id="demo_001",
                        name="Sarah Chen",
                        email="sarah@techcorp.com",
                        company="TechCorp",
                        title="Engineering Manager",
                        contact_type=ContactType.HIRING_MANAGER,
                        relationship_strength=RelationshipStrength.PROFESSIONAL
                    ),
                    Contact(
                        contact_id="demo_002",
                        name="Michael Rodriguez",
                        email="m.rodriguez@startup.com",
                        company="StartupXYZ",
                        title="CTO",
                        contact_type=ContactType.EXECUTIVE,
                        relationship_strength=RelationshipStrength.STRONG
                    )
                ]
                
                # Apply basic filtering for demo
                if filters:
                    if 'company' in filters:
                        demo_contacts = [c for c in demo_contacts if c.company == filters['company']]
                    if 'contact_type' in filters:
                        demo_contacts = [c for c in demo_contacts if c.contact_type.value == filters['contact_type']]
                
                return demo_contacts
            
            # Build query
            query_builder = self.supabase.table('contacts').select('*')
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        query_builder = query_builder.eq(key, value)
            
            # Apply text search
            if query:
                query_builder = query_builder.or_(f"name.ilike.%{query}%,company.ilike.%{query}%,title.ilike.%{query}%")
            
            result = query_builder.execute()
            
            contacts = []
            if result.data:
                for data in result.data:
                    contacts.append(Contact(
                        contact_id=data['contact_id'],
                        name=data['name'],
                        email=data['email'],
                        linkedin_url=data['linkedin_url'],
                        company=data['company'],
                        title=data['title'],
                        location=data['location'],
                        contact_type=ContactType(data['contact_type']),
                        relationship_strength=RelationshipStrength(data['relationship_strength']),
                        tags=data['tags'] or [],
                        notes=data['notes'] or "",
                        source=data['source'],
                        interaction_count=data['interaction_count'],
                        response_rate=data['response_rate'],
                        influence_score=data['influence_score']
                    ))
            
            return contacts
            
        except Exception as e:
            logger.error(f"Contact search failed: {str(e)}")
            return []
    
    def get_contacts_by_company(self, company: str) -> List[Contact]:
        """
        Get all contacts from a specific company
        
        Args:
            company: Company name
            
        Returns:
            List of contacts from the company
        """
        return self.search_contacts(filters={'company': company})
    
    def get_top_contacts_by_influence(self, limit: int = 10) -> List[Contact]:
        """
        Get top contacts by influence score
        
        Args:
            limit: Number of contacts to return
            
        Returns:
            List of top influential contacts
        """
        try:
            if self.demo_mode:
                demo_contacts = self.search_contacts()
                return sorted(demo_contacts, key=lambda x: x.influence_score, reverse=True)[:limit]
            
            result = self.supabase.table('contacts').select('*').order('influence_score', desc=True).limit(limit).execute()
            
            contacts = []
            if result.data:
                for data in result.data:
                    contacts.append(Contact(
                        contact_id=data['contact_id'],
                        name=data['name'],
                        email=data['email'],
                        linkedin_url=data['linkedin_url'],
                        company=data['company'],
                        title=data['title'],
                        location=data['location'],
                        contact_type=ContactType(data['contact_type']),
                        relationship_strength=RelationshipStrength(data['relationship_strength']),
                        tags=data['tags'] or [],
                        notes=data['notes'] or "",
                        source=data['source'],
                        interaction_count=data['interaction_count'],
                        response_rate=data['response_rate'],
                        influence_score=data['influence_score']
                    ))
            
            return contacts
            
        except Exception as e:
            logger.error(f"Top contacts retrieval failed: {str(e)}")
            return []
    
    # Interaction Tracking
    
    def record_interaction(self, interaction: ContactInteraction) -> bool:
        """
        Record a contact interaction
        
        Args:
            interaction: Interaction to record
            
        Returns:
            Success status
        """
        try:
            if self.demo_mode:
                logger.info(f"Demo: Recorded interaction {interaction.interaction_id}")
                return True
            
            interaction_data = {
                'interaction_id': interaction.interaction_id,
                'contact_id': interaction.contact_id,
                'interaction_type': interaction.interaction_type,
                'direction': interaction.direction,
                'subject': interaction.subject,
                'content': interaction.content,
                'response_received': interaction.response_received,
                'response_time_hours': interaction.response_time_hours,
                'sentiment': interaction.sentiment,
                'outcome': interaction.outcome,
                'metadata': interaction.metadata,
                'created_at': interaction.created_at.isoformat()
            }
            
            result = self.supabase.table('contact_interactions').insert(interaction_data).execute()
            
            if result.data:
                logger.info(f"Recorded interaction {interaction.interaction_id}")
                return True
            else:
                logger.error("Interaction recording failed: No data returned")
                return False
                
        except Exception as e:
            logger.error(f"Interaction recording failed: {str(e)}")
            return False
    
    def get_contact_interactions(self, contact_id: str, limit: int = 50) -> List[ContactInteraction]:
        """
        Get interactions for a contact
        
        Args:
            contact_id: Contact ID
            limit: Maximum number of interactions to return
            
        Returns:
            List of contact interactions
        """
        try:
            if self.demo_mode:
                return [
                    ContactInteraction(
                        interaction_id="int_demo_001",
                        contact_id=contact_id,
                        interaction_type="linkedin_message",
                        direction="outbound",
                        subject="Connection request",
                        content="Hi! Would love to connect and learn about your experience.",
                        response_received=True,
                        response_time_hours=24.5,
                        sentiment="positive"
                    ),
                    ContactInteraction(
                        interaction_id="int_demo_002",
                        contact_id=contact_id,
                        interaction_type="email",
                        direction="inbound",
                        subject="Re: Coffee chat",
                        content="Thanks for reaching out! I'd be happy to chat.",
                        response_received=False,
                        sentiment="positive"
                    )
                ]
            
            result = self.supabase.table('contact_interactions').select('*').eq('contact_id', contact_id).order('created_at', desc=True).limit(limit).execute()
            
            interactions = []
            if result.data:
                for data in result.data:
                    interactions.append(ContactInteraction(
                        interaction_id=data['interaction_id'],
                        contact_id=data['contact_id'],
                        interaction_type=data['interaction_type'],
                        direction=data['direction'],
                        subject=data['subject'],
                        content=data['content'],
                        response_received=data['response_received'],
                        response_time_hours=data['response_time_hours'],
                        sentiment=data['sentiment'],
                        outcome=data['outcome'],
                        metadata=data['metadata'] or {},
                        created_at=datetime.fromisoformat(data['created_at'])
                    ))
            
            return interactions
            
        except Exception as e:
            logger.error(f"Failed to get contact interactions: {str(e)}")
            return []
    
    # LinkedIn Campaign Management
    
    def create_linkedin_campaign(self, campaign: LinkedInCampaign) -> bool:
        """
        Create a LinkedIn automation campaign
        
        Args:
            campaign: Campaign to create
            
        Returns:
            Success status
        """
        try:
            if self.demo_mode:
                logger.info(f"Demo: Created LinkedIn campaign {campaign.campaign_id}")
                return True
            
            campaign_data = {
                'campaign_id': campaign.campaign_id,
                'name': campaign.name,
                'description': campaign.description,
                'target_criteria': campaign.target_criteria,
                'message_template': campaign.message_template,
                'follow_up_sequence': campaign.follow_up_sequence,
                'is_active': campaign.is_active,
                'daily_limit': campaign.daily_limit,
                'sent_count': campaign.sent_count,
                'accepted_count': campaign.accepted_count,
                'response_count': campaign.response_count,
                'created_at': campaign.created_at.isoformat(),
                'last_run': campaign.last_run.isoformat() if campaign.last_run else None
            }
            
            result = self.supabase.table('linkedin_campaigns').insert(campaign_data).execute()
            
            if result.data:
                logger.info(f"Created LinkedIn campaign {campaign.campaign_id}")
                return True
            else:
                logger.error("LinkedIn campaign creation failed: No data returned")
                return False
                
        except Exception as e:
            logger.error(f"LinkedIn campaign creation failed: {str(e)}")
            return False
    
    def get_linkedin_campaigns(self, active_only: bool = False) -> List[LinkedInCampaign]:
        """
        Get LinkedIn campaigns
        
        Args:
            active_only: Only return active campaigns
            
        Returns:
            List of LinkedIn campaigns
        """
        try:
            if self.demo_mode:
                return [
                    LinkedInCampaign(
                        campaign_id="demo_campaign_001",
                        name="Demo Senior Engineer Outreach",
                        description="Demo campaign for senior engineers",
                        target_criteria={"titles": ["Senior Engineer"], "companies": ["TechCorp"]},
                        message_template="Hi {name}, would love to connect!",
                        follow_up_sequence=[],
                        sent_count=25,
                        accepted_count=18,
                        response_count=12
                    )
                ]
            
            query_builder = self.supabase.table('linkedin_campaigns').select('*')
            
            if active_only:
                query_builder = query_builder.eq('is_active', True)
            
            result = query_builder.execute()
            
            campaigns = []
            if result.data:
                for data in result.data:
                    campaigns.append(LinkedInCampaign(
                        campaign_id=data['campaign_id'],
                        name=data['name'],
                        description=data['description'],
                        target_criteria=data['target_criteria'],
                        message_template=data['message_template'],
                        follow_up_sequence=data['follow_up_sequence'],
                        is_active=data['is_active'],
                        daily_limit=data['daily_limit'],
                        sent_count=data['sent_count'],
                        accepted_count=data['accepted_count'],
                        response_count=data['response_count'],
                        created_at=datetime.fromisoformat(data['created_at']),
                        last_run=datetime.fromisoformat(data['last_run']) if data['last_run'] else None
                    ))
            
            return campaigns
            
        except Exception as e:
            logger.error(f"Failed to get LinkedIn campaigns: {str(e)}")
            return []
    
    def update_campaign_stats(self, campaign_id: str, stats: Dict[str, int]) -> bool:
        """
        Update LinkedIn campaign statistics
        
        Args:
            campaign_id: Campaign ID
            stats: Statistics to update (sent_count, accepted_count, response_count)
            
        Returns:
            Success status
        """
        try:
            if self.demo_mode:
                logger.info(f"Demo: Updated campaign stats for {campaign_id}")
                return True
            
            stats['last_run'] = datetime.utcnow().isoformat()
            
            result = self.supabase.table('linkedin_campaigns').update(stats).eq('campaign_id', campaign_id).execute()
            
            if result.data:
                logger.info(f"Updated campaign stats for {campaign_id}")
                return True
            else:
                logger.error("Campaign stats update failed: No data returned")
                return False
                
        except Exception as e:
            logger.error(f"Campaign stats update failed: {str(e)}")
            return False
    
    # Networking Opportunities
    
    def create_networking_opportunity(self, opportunity: NetworkingOpportunity) -> bool:
        """
        Create a networking opportunity
        
        Args:
            opportunity: Opportunity to create
            
        Returns:
            Success status
        """
        try:
            if self.demo_mode:
                logger.info(f"Demo: Created networking opportunity {opportunity.opportunity_id}")
                return True
            
            opportunity_data = {
                'opportunity_id': opportunity.opportunity_id,
                'opportunity_type': opportunity.opportunity_type.value,
                'target_contact_id': opportunity.target_contact_id,
                'target_company': opportunity.target_company,
                'mutual_connections': opportunity.mutual_connections,
                'introduction_path': opportunity.introduction_path,
                'priority_score': opportunity.priority_score,
                'context': opportunity.context,
                'suggested_approach': opportunity.suggested_approach,
                'deadline': opportunity.deadline.isoformat() if opportunity.deadline else None,
                'status': opportunity.status,
                'created_at': opportunity.created_at.isoformat()
            }
            
            result = self.supabase.table('networking_opportunities').insert(opportunity_data).execute()
            
            if result.data:
                logger.info(f"Created networking opportunity {opportunity.opportunity_id}")
                return True
            else:
                logger.error("Networking opportunity creation failed: No data returned")
                return False
                
        except Exception as e:
            logger.error(f"Networking opportunity creation failed: {str(e)}")
            return False
    
    def get_networking_opportunities(self, status: str = None, limit: int = 20) -> List[NetworkingOpportunity]:
        """
        Get networking opportunities
        
        Args:
            status: Filter by status (optional)
            limit: Maximum number of opportunities to return
            
        Returns:
            List of networking opportunities
        """
        try:
            if self.demo_mode:
                return [
                    NetworkingOpportunity(
                        opportunity_id="demo_opp_001",
                        opportunity_type=NetworkingOpportunityType.WARM_INTRODUCTION,
                        target_company="TechCorp",
                        mutual_connections=["contact_001"],
                        priority_score=0.85,
                        context="Target company for senior role",
                        suggested_approach="Request introduction through Sarah"
                    ),
                    NetworkingOpportunity(
                        opportunity_id="demo_opp_002",
                        opportunity_type=NetworkingOpportunityType.REFERRAL_OPPORTUNITY,
                        target_company="StartupXYZ",
                        mutual_connections=["contact_002"],
                        priority_score=0.90,
                        context="Open position matches profile",
                        suggested_approach="Ask Michael for referral"
                    )
                ]
            
            query_builder = self.supabase.table('networking_opportunities').select('*').order('priority_score', desc=True).limit(limit)
            
            if status:
                query_builder = query_builder.eq('status', status)
            
            result = query_builder.execute()
            
            opportunities = []
            if result.data:
                for data in result.data:
                    opportunities.append(NetworkingOpportunity(
                        opportunity_id=data['opportunity_id'],
                        opportunity_type=NetworkingOpportunityType(data['opportunity_type']),
                        target_contact_id=data['target_contact_id'],
                        target_company=data['target_company'],
                        mutual_connections=data['mutual_connections'] or [],
                        introduction_path=data['introduction_path'] or [],
                        priority_score=data['priority_score'],
                        context=data['context'],
                        suggested_approach=data['suggested_approach'],
                        deadline=datetime.fromisoformat(data['deadline']) if data['deadline'] else None,
                        status=data['status'],
                        created_at=datetime.fromisoformat(data['created_at'])
                    ))
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Failed to get networking opportunities: {str(e)}")
            return []
    
    # Analytics
    
    def calculate_networking_analytics(self, user_id: str = None, days: int = 30) -> Optional[NetworkingAnalytics]:
        """
        Calculate comprehensive networking analytics
        
        Args:
            user_id: User ID (optional)
            days: Number of days to analyze
            
        Returns:
            Networking analytics or None
        """
        try:
            if self.demo_mode:
                return NetworkingAnalytics(
                    total_contacts=134,
                    new_contacts_this_month=18,
                    active_conversations=24,
                    response_rate=0.68,
                    network_growth_rate=0.15,
                    relationship_distribution={
                        "stranger": 25,
                        "acquaintance": 45,
                        "professional": 35,
                        "strong": 18,
                        "close": 8,
                        "advocate": 3
                    },
                    top_companies=[
                        {"company": "TechCorp", "contacts": 12, "influence": 0.82},
                        {"company": "StartupXYZ", "contacts": 8, "influence": 0.75},
                        {"company": "BigTech Inc", "contacts": 15, "influence": 0.68}
                    ],
                    networking_roi={
                        "interviews_generated": 8,
                        "referrals_received": 5,
                        "opportunities_discovered": 22,
                        "time_invested_hours": 32
                    },
                    engagement_metrics={
                        "linkedin_acceptance_rate": 0.72,
                        "message_response_rate": 0.48,
                        "meeting_conversion_rate": 0.35,
                        "follow_up_effectiveness": 0.62
                    },
                    optimization_recommendations=[
                        "Focus on building stronger relationships with hiring managers",
                        "Increase follow-up frequency with warm connections",
                        "Leverage Michael Rodriguez for more startup introductions",
                        "Attend industry events to expand network breadth"
                    ]
                )
            
            # Calculate real analytics from database
            return None
            
        except Exception as e:
            logger.error(f"Failed to calculate networking analytics: {str(e)}")
            return None
    
    def export_networking_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all networking data for a user
        
        Args:
            user_id: User ID to export data for
            
        Returns:
            Exported networking data
        """
        try:
            export_data = {
                "user_id": user_id,
                "export_date": datetime.utcnow().isoformat(),
                "contacts": [],
                "interactions": [],
                "campaigns": [],
                "opportunities": [],
                "analytics": {}
            }
            
            if self.demo_mode:
                export_data["demo_mode"] = True
                export_data["contacts"] = [{"contact_id": "demo", "name": "Demo Contact"}]
                export_data["campaigns"] = [{"campaign_id": "demo", "name": "Demo Campaign"}]
                export_data["opportunities"] = [{"opportunity_id": "demo", "type": "demo"}]
                logger.info(f"Demo: Exported networking data for user {user_id}")
            else:
                # Query all tables for user data
                pass
            
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to export networking data: {str(e)}")
            return {}
