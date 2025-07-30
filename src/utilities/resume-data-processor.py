#!/usr/bin/env python3
"""
Resume Data Processor
Extracts and structures Allen Walker's actual resume data for dynamic optimization
"""

import json
import re
from datetime import datetime

class ResumeDataProcessor:
    def __init__(self):
        self.resume_data = self.load_allen_resume_data()
    
    def load_allen_resume_data(self):
        """Load Allen's actual resume data structured for optimization"""
        return {
            "personal_info": {
                "name": "Allen Walker",
                "location": "San Francisco, CA",
                "linkedin": "linkedin.com/in/allenwalker",
                "email": "allen.walker@email.com",
                "phone": "(555) 123-4567"
            },
            
            "executive_summaries": [
                {
                    "id": "strategic_program_leader",
                    "content": "Senior program leader and operations strategist with 15+ years transforming industries including healthcare, construction, property management, pharma, and community development. I drive change through systems thinking, infrastructure buildout, IT delivery, and hands-on execution across complex projects. Combines startup grit with enterprise discipline—leading $500M+ initiatives, streamlining RevOps delivery, and scaling high-trust systems that connect vision to execution.",
                    "keywords": ["program leader", "operations strategist", "systems thinking", "IT delivery", "cross-functional", "RevOps", "enterprise"],
                    "focus": "general"
                },
                {
                    "id": "customer_program_manager",
                    "content": "Strategic program manager with 15+ years of experience leading cross-functional teams and managing executive stakeholder relationships in complex technology implementations. Proven track record of delivering $6B+ programs while driving operational excellence and customer success. Expert in multi-stakeholder coordination, strategic planning, and program execution across healthcare and technology sectors.",
                    "keywords": ["program manager", "cross-functional teams", "executive stakeholder", "customer success", "multi-stakeholder coordination", "strategic planning"],
                    "focus": "customer_programs"
                }
            ],
            
            "career_highlights": [
                {
                    "text": "Directed a $6B Epic program for 35,000+ users—drove timelines, delivered change, and met go-live with zero critical errors",
                    "keywords": ["Epic program", "$6B", "35,000+ users", "go-live", "program management"],
                    "categories": ["healthcare", "program_management", "large_scale"],
                    "impact_metrics": {"budget": 6000000000, "users": 35000, "critical_errors": 0}
                },
                {
                    "text": "Managed an IT portfolio serving 100K+ users—led vendor management, contract execution, and SLA accountability across high-stakes production environments",
                    "keywords": ["IT portfolio", "100K+ users", "vendor management", "SLA accountability", "production"],
                    "categories": ["technology", "operations", "vendor_management"],
                    "impact_metrics": {"users": 100000}
                },
                {
                    "text": "Led RevOps and delivery for Fortune 100 clients—aligning systems and teams to improve onboarding outcomes",
                    "keywords": ["RevOps", "Fortune 100", "systems alignment", "onboarding", "delivery"],
                    "categories": ["revenue_operations", "enterprise_clients", "process_improvement"],
                    "impact_metrics": {"client_tier": "Fortune 100"}
                }
            ],
            
            "professional_experience": [
                {
                    "title": "Founder & Organizer",
                    "company": "Bay Area Connectors",
                    "location": "San Francisco, CA",
                    "start_date": "2024-01-01",
                    "end_date": None,
                    "is_current": True,
                    "bullets": [
                        {
                            "text": "Founded and scaled a networking organization fostering innovation and professional growth across the SF Bay Area tech ecosystem",
                            "keywords": ["founded", "scaled", "networking", "innovation", "tech ecosystem"],
                            "categories": ["leadership", "community_building", "entrepreneurship"]
                        },
                        {
                            "text": "Organized monthly in-person events attracting technologists, investors, and thought leaders; grew reach through strategic marketing",
                            "keywords": ["organized", "events", "technologists", "investors", "strategic marketing"],
                            "categories": ["event_management", "marketing", "stakeholder_engagement"]
                        },
                        {
                            "text": "Built sponsorships and partnerships with high-impact stakeholders to deliver value-driven programming and collaboration",
                            "keywords": ["sponsorships", "partnerships", "stakeholders", "programming", "collaboration"],
                            "categories": ["partnership_development", "stakeholder_management", "program_delivery"]
                        },
                        {
                            "text": "Directed event operations including logistics, speaker curation, and audience engagement, maintaining high satisfaction rates",
                            "keywords": ["event operations", "logistics", "speaker curation", "audience engagement"],
                            "categories": ["operations", "event_management", "customer_satisfaction"]
                        }
                    ]
                },
                {
                    "title": "Customer Experience Project Manager",
                    "company": "Ford Motor Company",
                    "location": "Dearborn, MI",
                    "start_date": "2022-01-01",
                    "end_date": "2024-01-01",
                    "is_current": False,
                    "bullets": [
                        {
                            "text": "Led EVSE deployment programs for Fortune 100 fleet clients—managing onboarding, vendor coordination, and field execution to reduce fuel costs and emissions",
                            "keywords": ["EVSE deployment", "Fortune 100", "fleet clients", "onboarding", "vendor coordination"],
                            "categories": ["program_management", "customer_onboarding", "vendor_management"]
                        },
                        {
                            "text": "Aligned with sales and RevOps teams to streamline deployment workflows, accelerate onboarding, and improve post-sale customer experience",
                            "keywords": ["sales", "RevOps", "deployment workflows", "onboarding", "customer experience"],
                            "categories": ["cross_functional", "process_improvement", "customer_success"]
                        },
                        {
                            "text": "Tracked customer data and deployment metrics in Salesforce—improving visibility across lead times, change orders, and install readiness",
                            "keywords": ["customer data", "Salesforce", "metrics", "lead times", "visibility"],
                            "categories": ["data_management", "crm", "process_tracking"]
                        },
                        {
                            "text": "Collaborated closely with Customer Success Managers to identify process gaps, track escalations, and drive resolution of client-facing deployment issues",
                            "keywords": ["Customer Success", "process gaps", "escalations", "client-facing", "resolution"],
                            "categories": ["collaboration", "problem_solving", "customer_support"]
                        }
                    ]
                },
                {
                    "title": "Startup Founder & Construction Manager",
                    "company": "Porchlight Inspection Services",
                    "location": "San Francisco, CA",
                    "start_date": "2019-01-01",
                    "end_date": "2022-01-01",
                    "is_current": False,
                    "bullets": [
                        {
                            "text": "Launched and ran a hands-on real estate services startup—delivering inspections, full-cycle property rehabs, and investor consulting services",
                            "keywords": ["launched", "startup", "real estate services", "inspections", "consulting"],
                            "categories": ["entrepreneurship", "startup_management", "real_estate"]
                        },
                        {
                            "text": "Managed everything from architectural planning and permitting to swinging a hammer, digging foundations, and coordinating subcontractors to get projects over the finish line",
                            "keywords": ["architectural planning", "permitting", "project management", "subcontractors"],
                            "categories": ["project_management", "construction", "hands_on_execution"]
                        }
                    ]
                },
                {
                    "title": "Senior Program Manager",
                    "company": "Cedars-Sinai Medical Center",
                    "location": "Los Angeles, CA",
                    "start_date": "2018-01-01",
                    "end_date": "2019-01-01",
                    "is_current": False,
                    "bullets": [
                        {
                            "text": "Led cross-functional program teams of 50+ members across IT, clinical, and administrative departments for enterprise-wide technology implementations",
                            "keywords": ["cross-functional", "program teams", "50+ members", "IT", "clinical", "enterprise-wide"],
                            "categories": ["program_management", "cross_functional_leadership", "healthcare_it"]
                        },
                        {
                            "text": "Managed executive stakeholder relationships including C-suite leadership, department heads, and external vendor partners for strategic program alignment",
                            "keywords": ["executive stakeholder", "C-suite", "department heads", "vendor partners", "strategic alignment"],
                            "categories": ["stakeholder_management", "executive_communication", "vendor_management"]
                        },
                        {
                            "text": "Introduced agile-inspired backlog hygiene practices to replace arbitrary classifications with high/medium/low tiers, enabling clearer prioritization and delivery focus",
                            "keywords": ["agile", "backlog hygiene", "prioritization", "delivery focus"],
                            "categories": ["agile_methodology", "process_improvement", "project_delivery"]
                        }
                    ]
                },
                {
                    "title": "Technical Project Manager",
                    "company": "Northwestern Medicine",
                    "location": "Chicago, IL",
                    "start_date": "2016-01-01",
                    "end_date": "2018-01-01",
                    "is_current": False,
                    "bullets": [
                        {
                            "text": "Deployed charge edit automation strategy with Optum Claims Manager—cutting coder workload by 50%, reducing denials, and capturing additional revenue through intelligent error detection",
                            "keywords": ["automation strategy", "Optum", "50% reduction", "revenue capture", "error detection"],
                            "categories": ["automation", "process_improvement", "revenue_optimization"]
                        },
                        {
                            "text": "Managed rapid deployment of 900+ credit card terminals across the health system—coordinated logistics, system config, and go-live in a 48-hour window",
                            "keywords": ["rapid deployment", "900+ terminals", "logistics", "48-hour window"],
                            "categories": ["deployment_management", "logistics", "rapid_execution"]
                        }
                    ]
                },
                {
                    "title": "Technology Consultant / Epic Systems Analyst",
                    "company": "Kaiser Permanente",
                    "location": "Oakland, CA",
                    "start_date": "2014-01-01",
                    "end_date": "2016-01-01",
                    "is_current": False,
                    "bullets": [
                        {
                            "text": "Led Epic system optimization and workflow design for revenue cycle operations across 8 regions supporting $60B in annual revenue",
                            "keywords": ["Epic system", "workflow design", "revenue cycle", "8 regions", "$60B revenue"],
                            "categories": ["epic_systems", "workflow_optimization", "revenue_cycle"]
                        }
                    ]
                },
                {
                    "title": "IT Application Manager",
                    "company": "Kaiser Permanente",
                    "location": "Oakland, CA",
                    "start_date": "2012-01-01",
                    "end_date": "2014-01-01",
                    "is_current": False,
                    "bullets": [
                        {
                            "text": "Owned ALM and production support for claims editing, submission, and routing systems supporting $60B in annual revenue across 8 regions",
                            "keywords": ["ALM", "production support", "claims systems", "$60B revenue", "8 regions"],
                            "categories": ["application_management", "production_support", "claims_processing"]
                        },
                        {
                            "text": "Managed $4.4M annual budget across apps, vendor contracts, and production support staffing—led hiring, RFPs, and SLA enforcement",
                            "keywords": ["$4.4M budget", "vendor contracts", "hiring", "RFPs", "SLA enforcement"],
                            "categories": ["budget_management", "vendor_management", "team_leadership"]
                        }
                    ]
                },
                {
                    "title": "Revenue Cycle Project Manager",
                    "company": "Kaiser Permanente",
                    "location": "Oakland, CA",
                    "start_date": "2011-01-01",
                    "end_date": "2012-01-01",
                    "is_current": False,
                    "bullets": [
                        {
                            "text": "Managed implementation of Medicare Advantage Risk Adjustment reporting across 8 regions—aligning Epic build and extract logic with CMS compliance requirements",
                            "keywords": ["Medicare Advantage", "Risk Adjustment", "8 regions", "Epic build", "CMS compliance"],
                            "categories": ["healthcare_compliance", "epic_implementation", "regulatory_reporting"]
                        },
                        {
                            "text": "Led cross-functional design sessions to align stakeholders on solution changes—secured approvals for system workflows and extract configuration",
                            "keywords": ["cross-functional", "design sessions", "stakeholders", "system workflows"],
                            "categories": ["stakeholder_alignment", "solution_design", "workflow_management"]
                        }
                    ]
                }
            ],
            
            "early_career_roles": [
                {
                    "title": "Program & Project Management Roles",
                    "companies": "Amgen, Cedars-Sinai Medical Center",
                    "location": "Los Angeles, CA",
                    "start_date": "2008-01-01",
                    "end_date": "2010-12-31",
                    "bullets": [
                        {
                            "text": "Managed 15+ workstreams in a global SAP drug manufacturing system replacement—tracking timelines, budgets, and risk escalations for executive review",
                            "keywords": ["15+ workstreams", "SAP", "drug manufacturing", "executive review"],
                            "categories": ["program_management", "pharmaceutical", "enterprise_systems"]
                        },
                        {
                            "text": "Led revision of 2,000+ SOPs and job aids impacted by legacy MES transition—hired technical writers and coordinated documentation with LMS for 15,000+ users",
                            "keywords": ["2,000+ SOPs", "MES transition", "technical writers", "15,000+ users"],
                            "categories": ["documentation_management", "change_management", "training_coordination"]
                        },
                        {
                            "text": "Oversaw 26 cross-functional workstreams in an Epic EMR rollout across 200+ team members—managed a 3,500+ line project plan and tracked contractor spend and onboarding",
                            "keywords": ["26 workstreams", "Epic EMR", "200+ team members", "3,500+ line project plan"],
                            "categories": ["epic_implementation", "large_scale_projects", "team_coordination"]
                        }
                    ]
                }
            ],
            
            "additional_experience": [
                {
                    "title": "Leasing Manager & Property Operations",
                    "companies": "Various Property Management Companies",
                    "location": "Los Angeles, CA",
                    "start_date": "2003-01-01",
                    "end_date": "2008-12-31",
                    "bullets": [
                        {
                            "text": "Closed over 100 residential leases as leasing manager of a 314-unit new construction high-rise—led a team of 3 agents and coordinated full-cycle leasing and tenant onboarding",
                            "keywords": ["100+ leases", "314-unit", "team of 3", "leasing", "tenant onboarding"],
                            "categories": ["team_leadership", "operations_management", "customer_service"]
                        },
                        {
                            "text": "Managed daily operations for a 130-unit downtown building—oversaw rent collection, maintenance workflows, and leasing activities using Yardi",
                            "keywords": ["130-unit", "daily operations", "rent collection", "Yardi"],
                            "categories": ["operations_management", "property_management", "systems_management"]
                        }
                    ]
                }
            ],
            
            "community_leadership": [
                {
                    "role": "Founder & Organizer",
                    "organization": "Bay Area Connectors",
                    "location": "San Francisco, CA",
                    "start_date": "2024-01-01",
                    "end_date": None,
                    "narrative": "Built and lead an active tech ecosystem community—connecting founders, operators, and investors through curated in-person events. Cultivate strategic sponsorships, moderate panels, and drive relationship-building across the Bay Area startup scene."
                },
                {
                    "role": "League Commissioner",
                    "organization": "River City NABA",
                    "location": "Sacramento, CA",
                    "start_date": "2022-01-01",
                    "end_date": "2024-01-01",
                    "narrative": "Supported operations for a 300+ player adult baseball league—managed scheduling, team formation, rules enforcement, player disputes, and strategic planning."
                },
                {
                    "role": "Founder & Executive Director",
                    "organization": "JobGroup (501c3)",
                    "location": "Portland, OR",
                    "start_date": "2012-01-01",
                    "end_date": "2015-01-01",
                    "narrative": "Launched and scaled a nonprofit career development community serving 1,000+ professionals with peer coaching, skills workshops, and strategic job search guidance."
                }
            ],
            
            "education": [
                {
                    "degree": "MBA",
                    "field": "Entrepreneurialism",
                    "institution": "California State University, Fullerton",
                    "graduation_year": None
                },
                {
                    "degree": "BA",
                    "field": "Economics & East Asian Languages and Cultures",
                    "institution": "University of Southern California",
                    "graduation_year": None
                }
            ],
            
            "certifications": [
                {
                    "name": "ITIL Foundations",
                    "version": "v3",
                    "issuer": "ITIL",
                    "status": "active"
                },
                {
                    "name": "Epic Resolute PB & HB",
                    "issuer": "Epic Systems",
                    "status": "expired"
                }
            ],
            
            "skills": {
                "business_strategy": ["Program Management", "Revenue Operations", "GTM Strategy", "Change Management", "Operations", "Business Development"],
                "customer_delivery": ["Customer Success", "CX Ops", "Cross-functional Program Delivery"],
                "systems": ["Salesforce", "HubSpot", "Epic (Resolute PB/HB)", "SAP", "Yardi"],
                "planning_tools": ["MS Project", "Asana", "Jira", "Confluence", "Notion", "Smartsheet", "Airtable", "Miro", "GitHub"],
                "data_automation": ["SQL", "PostgreSQL", "Supabase", "VBA", "Python", "R", "Data Modeling"],
                "execution_ops": ["Post-Sale Delivery Management", "Solution Implementation", "QA/UAT", "Cutover Planning", "Release Cycles", "Prod Support", "ALM"],
                "community": ["Strategic Events", "Sponsorship Development", "Stakeholder Engagement", "CRM/Email Campaigns"],
                "industries": ["SaaS", "AI", "EV Infrastructure", "Healthcare", "Pharma", "Real Estate", "Construction", "Property Management"],
                "methodologies": ["Agile", "Scrum", "Waterfall", "ITIL", "Lean"]
            }
        }
    
    def score_content_for_job(self, content_item, job_keywords, job_requirements):
        """Score a piece of content against job requirements"""
        content_text = content_item.get('text', '') + ' ' + ' '.join(content_item.get('keywords', []))
        content_lower = content_text.lower()
        
        keyword_matches = 0
        total_keywords = len(job_keywords)
        
        for keyword in job_keywords:
            if keyword.lower() in content_lower:
                keyword_matches += 1
        
        # Base score from keyword matching
        keyword_score = keyword_matches / max(total_keywords, 1) if total_keywords > 0 else 0
        
        # Bonus for high-impact metrics
        impact_bonus = 0
        if any(metric in content_text for metric in ['$6B', '$60B', '$4.4M', '35,000+', '100K+', '15+', '50+']):
            impact_bonus = 0.1
        
        # Bonus for leadership keywords
        leadership_bonus = 0
        leadership_terms = ['led', 'managed', 'directed', 'founded', 'launched', 'coordinated', 'oversaw']
        if any(term in content_lower for term in leadership_terms):
            leadership_bonus = 0.05
        
        final_score = min(1.0, keyword_score + impact_bonus + leadership_bonus)
        return round(final_score, 3)
    
    def optimize_resume_for_job(self, job_description, job_keywords):
        """Generate optimized resume content for a specific job"""
        
        # Score and select executive summary
        best_summary = None
        best_summary_score = 0
        
        for summary in self.resume_data['executive_summaries']:
            score = self.score_content_for_job(summary, job_keywords, job_description)
            if score > best_summary_score:
                best_summary = summary
                best_summary_score = score
        
        # Score and rank career highlights
        scored_highlights = []
        for highlight in self.resume_data['career_highlights']:
            score = self.score_content_for_job(highlight, job_keywords, job_description)
            scored_highlights.append({**highlight, 'score': score})
        
        scored_highlights.sort(key=lambda x: x['score'], reverse=True)
        
        # Score and rank employment bullets
        optimized_experience = []
        for job in self.resume_data['professional_experience']:
            scored_bullets = []
            for bullet in job['bullets']:
                score = self.score_content_for_job(bullet, job_keywords, job_description)
                scored_bullets.append({**bullet, 'score': score})
            
            scored_bullets.sort(key=lambda x: x['score'], reverse=True)
            optimized_experience.append({
                **job,
                'bullets': scored_bullets,  # Include all bullets
                'avg_score': sum(b['score'] for b in scored_bullets) / len(scored_bullets) if scored_bullets else 0
            })
        
        # Calculate section scores
        section_scores = {
            'executive_summary': best_summary_score,
            'career_highlights': sum(h['score'] for h in scored_highlights[:3]) / 3,
            'professional_experience': sum(job['avg_score'] for job in optimized_experience) / len(optimized_experience),
            'education': 0.72,  # Static for now
            'certifications': 0.85,  # Static for now
            'early_career': 0.68,  # Static for now
            'additional_experience': 0.45,  # Static for now
            'community_leadership': 0.78  # Static for now
        }
        
        return {
            'executive_summary': {
                'content': best_summary['content'],
                'score': best_summary_score
            },
            'career_highlights': scored_highlights[:3],
            'professional_experience': optimized_experience,
            'section_scores': section_scores,
            'overall_score': sum(section_scores.values()) / len(section_scores)
        }

# Global instance
resume_processor = ResumeDataProcessor()
