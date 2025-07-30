#!/usr/bin/env python3
"""
Resume Data Processor - Real Allen Walker Resume Data
Extracts and structures Allen Walker's actual resume data from Resume - Allen Walker.md
"""

import json
import re
from datetime import datetime

class ResumeDataProcessor:
    def __init__(self):
        self.resume_data = self.load_allen_resume_data()
    
    def load_allen_resume_data(self):
        """Load Allen's actual resume data from Resume - Allen Walker.md"""
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
                    "content": "Senior program leader and operations strategist with 15+ years transforming industries including healthcare, construction, property management, pharma, and community development. I drive change through systems thinking, infrastructure buildout, IT delivery, and hands-on execution across complex projects. Combines startup grit with enterprise discipline—leading $500M+ initiatives, streamlining RevOps delivery, and scaling high-trust systems that connect vision to execution. Trusted by C-suite and field teams alike for practical leadership and cross-functional clarity.",
                    "keywords": ["program leader", "operations strategist", "systems thinking", "IT delivery", "cross-functional", "RevOps", "enterprise"],
                    "focus": "general"
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
                    "start_date": "2024",
                    "end_date": "Present",
                    "bullets": [
                        {
                            "text": "Founded and scaled a networking organization fostering innovation and professional growth across the SF Bay Area tech ecosystem",
                            "keywords": ["founded", "scaled", "networking", "innovation", "tech ecosystem"],
                            "categories": ["leadership", "community_building", "startup"]
                        },
                        {
                            "text": "Organized monthly in-person events attracting technologists, investors, and thought leaders; grew reach through strategic marketing",
                            "keywords": ["organized", "events", "technologists", "investors", "strategic marketing"],
                            "categories": ["event_management", "marketing", "stakeholder_engagement"]
                        },
                        {
                            "text": "Built sponsorships and partnerships with high-impact stakeholders to deliver value-driven programming and collaboration",
                            "keywords": ["sponsorships", "partnerships", "stakeholders", "programming", "collaboration"],
                            "categories": ["partnership_development", "business_development"]
                        },
                        {
                            "text": "Directed event operations including logistics, speaker curation, and audience engagement, maintaining high satisfaction rates",
                            "keywords": ["directed", "operations", "logistics", "speaker curation", "audience engagement"],
                            "categories": ["operations", "event_management"]
                        },
                        {
                            "text": "Managed vision, operations, and sustainability while cultivating an inclusive, cross-sector professional community",
                            "keywords": ["managed", "vision", "operations", "sustainability", "inclusive community"],
                            "categories": ["leadership", "community_management"]
                        }
                    ]
                },
                {
                    "title": "Customer Experience Project Manager",
                    "company": "Ford Motor Company",
                    "location": "Detroit, MI",
                    "start_date": "2022",
                    "end_date": "2024",
                    "bullets": [
                        {
                            "text": "Led EVSE deployment programs for Fortune 100 fleet clients—managing onboarding, vendor coordination, and field execution to reduce fuel costs and emissions",
                            "keywords": ["EVSE deployment", "Fortune 100", "fleet clients", "onboarding", "vendor coordination"],
                            "categories": ["program_management", "customer_experience", "sustainability"]
                        },
                        {
                            "text": "Aligned with sales and RevOps teams to streamline deployment workflows, accelerate onboarding, and improve post-sale customer experience",
                            "keywords": ["sales", "RevOps", "deployment workflows", "onboarding", "customer experience"],
                            "categories": ["cross_functional", "process_improvement", "customer_success"]
                        },
                        {
                            "text": "Tracked customer data and deployment metrics in Salesforce—improving visibility across lead times, change orders, and install readiness",
                            "keywords": ["Salesforce", "customer data", "deployment metrics", "lead times", "visibility"],
                            "categories": ["data_management", "crm", "analytics"]
                        },
                        {
                            "text": "Collaborated closely with Customer Success Managers to identify process gaps, track escalations, and drive resolution of client-facing deployment issues",
                            "keywords": ["Customer Success", "process gaps", "escalations", "resolution", "deployment issues"],
                            "categories": ["collaboration", "problem_solving", "customer_support"]
                        },
                        {
                            "text": "Provided on-site support and SaaS/hardware troubleshooting to ensure smooth installations and resolve issues in real time",
                            "keywords": ["on-site support", "SaaS", "hardware troubleshooting", "installations", "real time"],
                            "categories": ["technical_support", "field_operations"]
                        },
                        {
                            "text": "Delivered customer insights to product teams—flagging field issues and proposing enhancements to improve experience and adoption",
                            "keywords": ["customer insights", "product teams", "field issues", "enhancements", "adoption"],
                            "categories": ["product_feedback", "continuous_improvement"]
                        }
                    ]
                },
                {
                    "title": "Startup Founder & Construction Manager",
                    "company": "Porchlight Inspection Services",
                    "location": "San Francisco, CA",
                    "start_date": "2019",
                    "end_date": "2022",
                    "bullets": [
                        {
                            "text": "Launched and ran a hands-on real estate services startup—delivering inspections, full-cycle property rehabs, and investor consulting services",
                            "keywords": ["launched", "startup", "real estate services", "inspections", "property rehabs"],
                            "categories": ["entrepreneurship", "real_estate", "consulting"]
                        },
                        {
                            "text": "Managed everything from architectural planning and permitting to swinging a hammer, digging foundations, and coordinating subcontractors to get projects over the finish line",
                            "keywords": ["architectural planning", "permitting", "foundations", "subcontractors", "project completion"],
                            "categories": ["project_management", "construction", "hands_on_execution"]
                        }
                    ]
                },
                {
                    "title": "Senior Program Manager",
                    "company": "Northwestern Medicine",
                    "location": "Chicago, IL",
                    "start_date": "2018",
                    "end_date": "2019",
                    "bullets": [
                        {
                            "text": "Managed Epic revenue cycle optimization across 11 hospitals—led cross-functional teams to streamline workflows and improve financial performance",
                            "keywords": ["Epic", "revenue cycle", "11 hospitals", "cross-functional teams", "financial performance"],
                            "categories": ["healthcare", "revenue_operations", "process_optimization"]
                        },
                        {
                            "text": "Introduced agile-inspired backlog hygiene practices to replace arbitrary classifications with high/medium/low tiers, enabling clearer prioritization and delivery focus",
                            "keywords": ["agile", "backlog hygiene", "prioritization", "delivery focus", "process improvement"],
                            "categories": ["agile_methodology", "process_improvement"]
                        },
                        {
                            "text": "Facilitated cross-functional issue triage and resolution between IT, Epic, and operational leaders to support business-critical workflows",
                            "keywords": ["cross-functional", "issue triage", "IT", "Epic", "business-critical workflows"],
                            "categories": ["problem_solving", "cross_functional", "healthcare_it"]
                        }
                    ]
                },
                {
                    "title": "Technical Project Manager",
                    "company": "Northwestern Medicine",
                    "location": "Chicago, IL",
                    "start_date": "2016",
                    "end_date": "2018",
                    "bullets": [
                        {
                            "text": "Deployed charge edit automation strategy with Optum Claims Manager—cutting coder workload by 50%, reducing denials, and capturing additional revenue through intelligent error detection",
                            "keywords": ["charge edit automation", "Optum Claims Manager", "50% reduction", "revenue capture", "error detection"],
                            "categories": ["automation", "healthcare_revenue", "process_improvement"]
                        },
                        {
                            "text": "Managed rapid deployment of 900+ credit card terminals across the health system—coordinated logistics, system config, and go-live in a 48-hour window",
                            "keywords": ["900+ terminals", "health system", "logistics", "system config", "48-hour deployment"],
                            "categories": ["deployment", "logistics", "healthcare_operations"]
                        }
                    ]
                },
                {
                    "title": "Technology Consultant / Epic Systems Analyst",
                    "company": "Kaiser Permanente",
                    "location": "Oakland, CA",
                    "start_date": "2014",
                    "end_date": "2016",
                    "bullets": [
                        {
                            "text": "Led Epic Resolute Professional Billing optimization across 8 regions—improved claim accuracy, reduced denials, and streamlined revenue cycle workflows",
                            "keywords": ["Epic Resolute", "Professional Billing", "8 regions", "claim accuracy", "revenue cycle"],
                            "categories": ["epic_systems", "healthcare_revenue", "process_optimization"]
                        }
                    ]
                },
                {
                    "title": "IT Application Manager",
                    "company": "Kaiser Permanente",
                    "location": "Oakland, CA",
                    "start_date": "2012",
                    "end_date": "2014",
                    "bullets": [
                        {
                            "text": "Owned ALM and production support for claims editing, submission, and routing systems supporting $60B in annual revenue across 8 regions",
                            "keywords": ["ALM", "production support", "claims systems", "$60B revenue", "8 regions"],
                            "categories": ["application_management", "healthcare_revenue", "production_support"]
                        },
                        {
                            "text": "Managed $4.4M annual budget across apps, vendor contracts, and production support staffing—led hiring, RFPs, and SLA enforcement",
                            "keywords": ["$4.4M budget", "vendor contracts", "production support", "hiring", "SLA enforcement"],
                            "categories": ["budget_management", "vendor_management", "team_leadership"]
                        }
                    ]
                },
                {
                    "title": "Revenue Cycle Project Manager",
                    "company": "Kaiser Permanente",
                    "location": "Oakland, CA",
                    "start_date": "2011",
                    "end_date": "2012",
                    "bullets": [
                        {
                            "text": "Managed implementation of Medicare Advantage Risk Adjustment reporting across 8 regions—aligning Epic build and extract logic with CMS compliance requirements",
                            "keywords": ["Medicare Advantage", "Risk Adjustment", "8 regions", "Epic build", "CMS compliance"],
                            "categories": ["healthcare_compliance", "epic_implementation", "revenue_cycle"]
                        },
                        {
                            "text": "Developed and maintained detailed project plans—managing timelines across build, testing, deployment, go-live, and post-implementation support",
                            "keywords": ["project plans", "timelines", "testing", "deployment", "go-live"],
                            "categories": ["project_management", "implementation"]
                        },
                        {
                            "text": "Led cross-functional design sessions to align stakeholders on solution changes—secured approvals for system workflows and extract configuration",
                            "keywords": ["cross-functional", "design sessions", "stakeholders", "system workflows", "configuration"],
                            "categories": ["stakeholder_management", "solution_design"]
                        },
                        {
                            "text": "Tracked and resolved risks, issues, and change requests—collaborated with PMO and technical teams to proactively clear delivery roadblocks",
                            "keywords": ["risks", "issues", "change requests", "PMO", "delivery roadblocks"],
                            "categories": ["risk_management", "problem_solving"]
                        },
                        {
                            "text": "Delivered dashboards, budget reports, and executive briefings to track performance against scope, spend, and schedule",
                            "keywords": ["dashboards", "budget reports", "executive briefings", "performance tracking", "scope management"],
                            "categories": ["reporting", "executive_communication"]
                        },
                        {
                            "text": "Built PMO SharePoint site structure and templates to standardize project documentation and team communication",
                            "keywords": ["PMO", "SharePoint", "templates", "project documentation", "team communication"],
                            "categories": ["documentation", "process_standardization"]
                        }
                    ]
                }
            ],
            
            "early_career_experience": [
                {
                    "title": "Program & Project Management",
                    "company": "Amgen, Cedars-Sinai Medical Center",
                    "location": "Los Angeles, CA",
                    "start_date": "2008",
                    "end_date": "2010",
                    "bullets": [
                        {
                            "text": "Managed 15+ workstreams in a global SAP drug manufacturing system replacement—tracking timelines, budgets, and risk escalations for executive review",
                            "keywords": ["15+ workstreams", "SAP", "drug manufacturing", "timelines", "executive review"],
                            "categories": ["program_management", "pharmaceutical", "sap_implementation"]
                        },
                        {
                            "text": "Led revision of 2,000+ SOPs and job aids impacted by legacy MES transition—hired technical writers and coordinated documentation with LMS for 15,000+ users",
                            "keywords": ["2,000+ SOPs", "MES transition", "technical writers", "LMS", "15,000+ users"],
                            "categories": ["documentation", "change_management", "training"]
                        },
                        {
                            "text": "Oversaw 26 cross-functional workstreams in an Epic EMR rollout across 200+ team members—managed a 3,500+ line project plan and tracked contractor spend and onboarding",
                            "keywords": ["26 workstreams", "Epic EMR", "200+ team members", "3,500+ line project plan", "contractor management"],
                            "categories": ["epic_implementation", "project_management", "team_coordination"]
                        },
                        {
                            "text": "Developed and maintained custom SharePoint portals and status dashboards to support large-scale stakeholder communication and project tracking",
                            "keywords": ["SharePoint portals", "status dashboards", "stakeholder communication", "project tracking"],
                            "categories": ["communication", "project_tracking", "stakeholder_management"]
                        }
                    ]
                }
            ],
            
            "additional_experience": [
                {
                    "title": "Leasing Manager & Property Operations",
                    "company": "Los Angeles Property Management",
                    "location": "Los Angeles, CA",
                    "start_date": "2003",
                    "end_date": "2008",
                    "bullets": [
                        {
                            "text": "Closed over 100 residential leases as leasing manager of a 314-unit new construction high-rise—led a team of 3 agents and coordinated full-cycle leasing and tenant onboarding",
                            "keywords": ["100+ leases", "314-unit", "leasing manager", "team of 3", "tenant onboarding"],
                            "categories": ["property_management", "team_leadership", "sales"]
                        },
                        {
                            "text": "Managed daily operations for a 130-unit downtown building—oversaw rent collection, maintenance workflows, and leasing activities using Yardi",
                            "keywords": ["130-unit", "daily operations", "rent collection", "maintenance", "Yardi"],
                            "categories": ["operations", "property_management", "systems"]
                        },
                        {
                            "text": "Supported renters through complex searches—qualifying leads, matching renters to units, and coordinating tours across properties throughout LA and Seattle",
                            "keywords": ["complex searches", "qualifying leads", "matching renters", "coordinating tours"],
                            "categories": ["customer_service", "sales", "coordination"]
                        }
                    ]
                }
            ],
            
            "community_leadership": [
                {
                    "title": "Founder & Organizer",
                    "company": "Bay Area Connectors",
                    "location": "San Francisco, CA",
                    "start_date": "2024",
                    "end_date": "Present",
                    "bullets": [
                        {
                            "text": "Built and lead an active tech ecosystem community—connecting founders, operators, and investors through curated in-person events",
                            "keywords": ["tech ecosystem", "community", "founders", "operators", "investors"],
                            "categories": ["community_building", "networking", "leadership"]
                        }
                    ]
                },
                {
                    "title": "League Commissioner",
                    "company": "River City NABA",
                    "location": "Sacramento, CA",
                    "start_date": "2022",
                    "end_date": "2024",
                    "bullets": [
                        {
                            "text": "Supported operations for a 300+ player adult baseball league—managed scheduling, team formation, rules enforcement, player disputes, and strategic planning",
                            "keywords": ["300+ players", "operations", "scheduling", "team formation", "strategic planning"],
                            "categories": ["operations", "community_management", "leadership"]
                        },
                        {
                            "text": "Led marketing and recruitment efforts to grow league membership and fill team rosters across divisions",
                            "keywords": ["marketing", "recruitment", "league membership", "team rosters"],
                            "categories": ["marketing", "growth", "community_building"]
                        }
                    ]
                },
                {
                    "title": "Founder & Executive Director",
                    "company": "JobGroup (501c3)",
                    "location": "Portland, OR",
                    "start_date": "2012",
                    "end_date": "2015",
                    "bullets": [
                        {
                            "text": "Launched and scaled a nonprofit career development community serving 1,000+ professionals with peer coaching, skills workshops, and strategic job search guidance",
                            "keywords": ["nonprofit", "career development", "1,000+ professionals", "peer coaching", "job search"],
                            "categories": ["nonprofit", "community_building", "career_development"]
                        },
                        {
                            "text": "Designed curriculum, led seminars, and oversaw marketing, finance, and community partnerships",
                            "keywords": ["curriculum", "seminars", "marketing", "finance", "partnerships"],
                            "categories": ["education", "leadership", "partnership_development"]
                        }
                    ]
                },
                {
                    "title": "Board Member – Director of Communications",
                    "company": "PMI Los Angeles Chapter",
                    "location": "Los Angeles, CA",
                    "start_date": "2008",
                    "end_date": "2009",
                    "bullets": [
                        {
                            "text": "Served on the Board of Directors for one of the largest PMI chapters in the country—oversaw chapter-wide strategic planning initiatives and drove member engagement",
                            "keywords": ["Board of Directors", "PMI chapter", "strategic planning", "member engagement"],
                            "categories": ["board_governance", "strategic_planning", "professional_development"]
                        },
                        {
                            "text": "Contributed to long-range planning efforts for the professional development of 3,000+ members",
                            "keywords": ["long-range planning", "professional development", "3,000+ members"],
                            "categories": ["strategic_planning", "professional_development", "membership"]
                        }
                    ]
                }
            ],
            
            "skills_expertise": [
                {
                    "category": "Business & Strategy",
                    "skills": ["Program Management", "Revenue Operations", "GTM Strategy", "Change Management", "Operations", "Business Development"]
                },
                {
                    "category": "Customer Experience & Delivery", 
                    "skills": ["Customer Success", "CX Ops", "Cross-functional Program Delivery"]
                },
                {
                    "category": "CRM & Systems",
                    "skills": ["Salesforce", "HubSpot", "Epic (Resolute PB/HB)", "SAP", "Yardi"]
                },
                {
                    "category": "Planning & Documentation Tools",
                    "skills": ["MS Project", "Asana", "Jira", "Confluence", "Notion", "Smartsheet", "Airtable", "Miro", "GitHub", "Google Workspace", "SharePoint"]
                },
                {
                    "category": "Data & Automation",
                    "skills": ["SQL", "PostgreSQL", "Supabase", "VBA", "Python", "R", "Data Modeling", "Entity Relationship Design"]
                },
                {
                    "category": "Execution & Ops",
                    "skills": ["Post-Sale Delivery Management", "Solution Implementation", "QA/UAT", "Cutover Planning", "Release Cycles", "Prod Support", "ALM"]
                }
            ],
            
            "education": [
                {
                    "degree": "MBA – Entrepreneurialism",
                    "institution": "California State University, Fullerton",
                    "year": "Completed",
                    "field": "Entrepreneurialism"
                },
                {
                    "degree": "BA – Economics & East Asian Languages and Cultures",
                    "institution": "University of Southern California",
                    "year": "Completed",
                    "field": "Economics & East Asian Languages and Cultures"
                }
            ],
            
            "certifications": [
                {
                    "name": "ITIL Foundations (v3)",
                    "issuer": "ITIL",
                    "status": "Active"
                },
                {
                    "name": "Epic Resolute PB & HB",
                    "issuer": "Epic Systems",
                    "status": "Expired"
                }
            ]
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
        
        # Score early career and additional experience
        optimized_early_career = []
        for job in self.resume_data.get('early_career_experience', []):
            scored_bullets = []
            for bullet in job['bullets']:
                score = self.score_content_for_job(bullet, job_keywords, job_description)
                scored_bullets.append({**bullet, 'score': score})
            
            scored_bullets.sort(key=lambda x: x['score'], reverse=True)
            optimized_early_career.append({
                **job,
                'bullets': scored_bullets,
                'avg_score': sum(b['score'] for b in scored_bullets) / len(scored_bullets) if scored_bullets else 0
            })
        
        optimized_additional = []
        for job in self.resume_data.get('additional_experience', []):
            scored_bullets = []
            for bullet in job['bullets']:
                score = self.score_content_for_job(bullet, job_keywords, job_description)
                scored_bullets.append({**bullet, 'score': score})
            
            scored_bullets.sort(key=lambda x: x['score'], reverse=True)
            optimized_additional.append({
                **job,
                'bullets': scored_bullets,
                'avg_score': sum(b['score'] for b in scored_bullets) / len(scored_bullets) if scored_bullets else 0
            })
        
        optimized_community = []
        for job in self.resume_data.get('community_leadership', []):
            scored_bullets = []
            for bullet in job['bullets']:
                score = self.score_content_for_job(bullet, job_keywords, job_description)
                scored_bullets.append({**bullet, 'score': score})
            
            scored_bullets.sort(key=lambda x: x['score'], reverse=True)
            optimized_community.append({
                **job,
                'bullets': scored_bullets,
                'avg_score': sum(b['score'] for b in scored_bullets) / len(scored_bullets) if scored_bullets else 0
            })
        
        # Calculate section scores
        section_scores = {
            'executive_summary': best_summary_score,
            'career_highlights': sum(h['score'] for h in scored_highlights[:3]) / 3 if scored_highlights else 0,
            'professional_experience': sum(job['avg_score'] for job in optimized_experience) / len(optimized_experience) if optimized_experience else 0,
            'early_career': sum(job['avg_score'] for job in optimized_early_career) / len(optimized_early_career) if optimized_early_career else 0,
            'additional_experience': sum(job['avg_score'] for job in optimized_additional) / len(optimized_additional) if optimized_additional else 0,
            'community_leadership': sum(job['avg_score'] for job in optimized_community) / len(optimized_community) if optimized_community else 0,
            'education': 0.72,  # Static for now
            'certifications': 0.85  # Static for now
        }
        
        return {
            'executive_summary': {
                'content': best_summary['content'] if best_summary else "Executive summary not available",
                'score': best_summary_score
            },
            'career_highlights': scored_highlights[:3],
            'professional_experience': optimized_experience,
            'early_career_experience': optimized_early_career,
            'additional_experience': optimized_additional,
            'community_leadership': optimized_community,
            'skills_expertise': self.resume_data['skills_expertise'],
            'education': self.resume_data['education'],
            'certifications': self.resume_data['certifications'],
            'section_scores': section_scores,
            'overall_score': sum(section_scores.values()) / len(section_scores)
        }

# Global instance
resume_processor = ResumeDataProcessor()
