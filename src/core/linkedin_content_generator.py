"""
LinkedIn Content Generator for Recruiter Engagement
Generates data-driven LinkedIn posts targeting talent acquisition professionals
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import random

logger = logging.getLogger(__name__)


class PostType(Enum):
    MARKET_INSIGHT = "market_insight"
    HIRING_TREND = "hiring_trend"
    SALARY_ANALYSIS = "salary_analysis"
    SKILL_DEMAND = "skill_demand"
    COMPANY_SPOTLIGHT = "company_spotlight"
    INDUSTRY_ANALYSIS = "industry_analysis"
    GEOGRAPHIC_TREND = "geographic_trend"
    RECRUITER_TIP = "recruiter_tip"


class PostTone(Enum):
    PROFESSIONAL = "professional"
    ANALYTICAL = "analytical"
    CONVERSATIONAL = "conversational"
    THOUGHT_LEADERSHIP = "thought_leadership"


@dataclass
class LinkedInPost:
    """Generated LinkedIn post content"""
    post_type: PostType
    title: str
    content: str
    hashtags: List[str]
    call_to_action: str
    data_source: str
    engagement_hooks: List[str] = field(default_factory=list)
    target_audience: List[str] = field(default_factory=list)
    post_tone: PostTone = PostTone.PROFESSIONAL
    estimated_reach_score: float = 0.0
    
    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)
    data_points_used: List[str] = field(default_factory=list)
    geographic_focus: Optional[str] = None
    industry_focus: Optional[str] = None


class LinkedInContentGenerator:
    """Service for generating LinkedIn content targeting recruiters"""
    
    def __init__(self):
        # Recruiter-focused hashtags by category
        self.hashtag_categories = {
            'recruiting': [
                '#TalentAcquisition', '#Recruiting', '#HiringTrends', '#TalentStrategy',
                '#RecruiterLife', '#HiringManager', '#TalentPipeline', '#RecruitmentMarketing'
            ],
            'data_insights': [
                '#JobMarketData', '#HiringAnalytics', '#TalentMetrics', '#MarketInsights',
                '#DataDrivenRecruiting', '#WorkforceAnalytics', '#RecruitmentData'
            ],
            'industry': [
                '#TechRecruiting', '#TechTalent', '#SiliconValley', '#BayAreaJobs',
                '#TechHiring', '#StartupRecruiting', '#TechCareers'
            ],
            'skills': [
                '#SkillsGap', '#TalentShortage', '#InDemandSkills', '#FutureOfWork',
                '#SkillsDevelopment', '#TalentDevelopment'
            ],
            'location': [
                '#BayAreaTalent', '#SiliconValleyJobs', '#NorthernCaliforniaJobs',
                '#SanFranciscoJobs', '#RemoteWork', '#HybridWork'
            ]
        }
        
        # Engagement hooks to start posts
        self.engagement_hooks = {
            'question': [
                "What's your take on this hiring trend?",
                "Are you seeing this in your recruiting efforts?",
                "How is this impacting your talent strategy?",
                "What's been your experience with this trend?"
            ],
            'surprising_stat': [
                "Here's a surprising stat that caught my attention:",
                "The numbers don't lie - here's what I'm seeing:",
                "This data point stopped me in my tracks:",
                "If you're in talent acquisition, this will interest you:"
            ],
            'observation': [
                "I've been analyzing job market data and noticed something interesting:",
                "After reviewing hundreds of job postings, here's what stands out:",
                "The data is telling a clear story about talent trends:",
                "Here's what the numbers are revealing about the job market:"
            ],
            'prediction': [
                "Based on current data trends, here's what I predict for recruiting:",
                "The data suggests we're heading toward a shift in talent acquisition:",
                "If current trends continue, recruiters should prepare for:",
                "The writing is on the wall - here's what's coming in talent acquisition:"
            ]
        }
        
        # Call-to-action templates
        self.cta_templates = {
            'network': [
                "What trends are you seeing? Let's connect and share insights! 🤝",
                "I'd love to hear your perspective - let's connect! 💼",
                "Connect with me to discuss talent acquisition strategies! 📊",
                "Let's build our recruiting network - connect if you're in TA! 🌐"
            ],
            'discussion': [
                "What's your experience with this trend? Share in the comments! 💬",
                "Drop a comment - are you seeing similar patterns? 👇",
                "I'd love to hear your thoughts on this data! Comment below 📝",
                "What strategies are you using to address this? Let's discuss! 🗣️"
            ],
            'collaboration': [
                "If you're working on similar challenges, let's collaborate! 🤝",
                "Looking to connect with other talent acquisition professionals! 🔗",
                "Always interested in partnering with great recruiters! 💪",
                "Open to discussing talent strategies - reach out! 📞"
            ]
        }
        
        # Professional bio elements to weave into posts
        self.professional_context = {
            'experience': [
                "With my background in program management and data analytics,",
                "Having worked across healthcare and technology sectors,",
                "From my experience in revenue operations and customer success,",
                "Through my work in process optimization and team leadership,"
            ],
            'expertise': [
                "I'm passionate about data-driven talent strategies",
                "I believe in using analytics to improve recruiting outcomes",
                "I focus on operational excellence in talent acquisition",
                "I'm interested in the intersection of data and recruiting"
            ]
        }
    
    def generate_market_insight_post(self, job_data: List[Dict[str, Any]]) -> LinkedInPost:
        """Generate market insight post from job data"""
        
        # Analyze job data for insights
        total_jobs = len(job_data)
        tech_jobs = len([j for j in job_data if 'technology' in j.get('job_category', '').lower()])
        remote_jobs = len([j for j in job_data if 'remote' in j.get('remote_work_option', '').lower()])
        
        # Calculate percentages
        tech_percentage = (tech_jobs / total_jobs * 100) if total_jobs > 0 else 0
        remote_percentage = (remote_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        # Generate content
        hook = random.choice(self.engagement_hooks['observation'])
        context = random.choice(self.professional_context['experience'])
        
        content = f"""{hook}
        
{context} I've been tracking job market trends in Northern California, and the data reveals some fascinating patterns:

📊 Key Insights from {total_jobs:,} job postings:
• Technology roles represent {tech_percentage:.0f}% of white-collar positions
• {remote_percentage:.0f}% of jobs now offer remote work options
• Bay Area continues to dominate tech hiring with concentrated opportunities

The shift toward flexible work arrangements is reshaping how companies attract talent, and smart recruiters are adapting their strategies accordingly.

For talent acquisition professionals: This data suggests candidates are prioritizing flexibility and tech companies are leading the charge in innovative hiring practices."""

        hashtags = (
            self.hashtag_categories['recruiting'][:2] +
            self.hashtag_categories['data_insights'][:2] +
            self.hashtag_categories['location'][:2]
        )
        
        cta = random.choice(self.cta_templates['discussion'])
        
        return LinkedInPost(
            post_type=PostType.MARKET_INSIGHT,
            title="Northern California Job Market Insights",
            content=content,
            hashtags=hashtags,
            call_to_action=cta,
            data_source=f"Analysis of {total_jobs:,} job postings",
            engagement_hooks=["market data", "percentages", "geographic focus"],
            target_audience=["recruiters", "talent acquisition", "hiring managers"],
            geographic_focus="Northern California",
            data_points_used=[f"total_jobs: {total_jobs}", f"tech_percentage: {tech_percentage:.1f}%", f"remote_percentage: {remote_percentage:.1f}%"]
        )
    
    def generate_hiring_trend_post(self, trend_data: Dict[str, Any]) -> LinkedInPost:
        """Generate hiring trend analysis post"""
        
        hook = random.choice(self.engagement_hooks['surprising_stat'])
        
        content = f"""{hook}
        
After analyzing hiring patterns across {trend_data.get('companies_analyzed', 100)} companies in the Bay Area, here's what's emerging:

🔍 Hiring Trend Alert:
• {trend_data.get('trend_description', 'Companies are shifting hiring strategies')}
• {trend_data.get('percentage_change', 25)}% change in posting frequency over the last quarter
• {trend_data.get('top_sector', 'Technology')} sector leading the trend

This shift indicates {trend_data.get('implication', 'a strategic pivot in talent acquisition approaches')}. 

For recruiters: Understanding these patterns helps you anticipate client needs and position candidates more effectively. The companies adapting fastest to these trends are seeing better hiring outcomes."""

        hashtags = (
            self.hashtag_categories['recruiting'][:3] +
            self.hashtag_categories['industry'][:2]
        )
        
        cta = random.choice(self.cta_templates['network'])
        
        return LinkedInPost(
            post_type=PostType.HIRING_TREND,
            title="Emerging Hiring Trend Analysis",
            content=content,
            hashtags=hashtags,
            call_to_action=cta,
            data_source=f"Analysis of {trend_data.get('companies_analyzed', 100)} companies",
            engagement_hooks=["trend alert", "percentage change", "sector analysis"],
            target_audience=["recruiters", "talent acquisition", "hiring managers"],
            industry_focus=trend_data.get('top_sector', 'Technology')
        )
    
    def generate_salary_analysis_post(self, salary_data: Dict[str, Any]) -> LinkedInPost:
        """Generate salary trend analysis post"""
        
        hook = random.choice(self.engagement_hooks['prediction'])
        context = random.choice(self.professional_context['expertise'])
        
        content = f"""{hook}
        
{context}, and the compensation data is telling a clear story:

💰 Salary Trend Analysis:
• {salary_data.get('role_type', 'Senior Software Engineer')} roles: ${salary_data.get('avg_salary', 150000):,} average
• {salary_data.get('salary_change', 8)}% increase compared to last year
• Remote positions commanding {salary_data.get('remote_premium', 5)}% premium

The talent market is rewarding flexibility and specialized skills. Companies that understand these compensation trends are winning the talent war.

Recruiting insight: Candidates are more informed about market rates than ever. Transparent, competitive compensation packages are becoming table stakes for attracting top talent."""

        hashtags = (
            self.hashtag_categories['recruiting'][:2] +
            self.hashtag_categories['data_insights'][:2] +
            ['#SalaryTrends', '#CompensationStrategy']
        )
        
        cta = random.choice(self.cta_templates['collaboration'])
        
        return LinkedInPost(
            post_type=PostType.SALARY_ANALYSIS,
            title="Compensation Trends Analysis",
            content=content,
            hashtags=hashtags,
            call_to_action=cta,
            data_source="Salary data analysis",
            engagement_hooks=["salary trends", "percentage increase", "market rates"],
            target_audience=["recruiters", "compensation analysts", "hiring managers"]
        )
    
    def generate_skill_demand_post(self, skills_data: List[Dict[str, Any]]) -> LinkedInPost:
        """Generate in-demand skills analysis post"""
        
        top_skills = skills_data[:5] if len(skills_data) >= 5 else skills_data
        
        hook = random.choice(self.engagement_hooks['question'])
        
        content = f"""{hook}
        
I've been tracking skill requirements across thousands of job postings, and the demand patterns are fascinating:

🔥 Most In-Demand Skills Right Now:
{chr(10).join([f"• {skill['name']} - {skill['demand_score']:.0f}% of postings" for skill in top_skills])}

The data shows a clear shift toward {skills_data[0]['category'] if skills_data else 'technical skills'} expertise. Companies are prioritizing candidates who can bridge technical and business requirements.

For talent acquisition teams: These skills should be your search keywords. Candidates with these competencies are in high demand and likely have multiple opportunities."""

        hashtags = (
            self.hashtag_categories['skills'][:3] +
            self.hashtag_categories['recruiting'][:2]
        )
        
        cta = random.choice(self.cta_templates['discussion'])
        
        return LinkedInPost(
            post_type=PostType.SKILL_DEMAND,
            title="In-Demand Skills Analysis",
            content=content,
            hashtags=hashtags,
            call_to_action=cta,
            data_source="Skills demand analysis",
            engagement_hooks=["skill demand", "search keywords", "candidate competencies"],
            target_audience=["recruiters", "talent acquisition", "sourcing specialists"]
        )
    
    def generate_company_spotlight_post(self, company_data: Dict[str, Any]) -> LinkedInPost:
        """Generate company hiring spotlight post"""
        
        hook = random.choice(self.engagement_hooks['observation'])
        
        content = f"""{hook}
        
{company_data.get('company_name', 'TechCorp')} is making some interesting hiring moves:

🏢 Company Spotlight:
• {company_data.get('active_jobs', 15)} active positions across {company_data.get('departments', 5)} departments
• {company_data.get('growth_rate', 25)}% increase in hiring over the last quarter
• Focus on {company_data.get('key_skills', 'AI/ML and cloud technologies')}

What caught my attention: {company_data.get('unique_insight', 'Their emphasis on remote-first culture and professional development')}

This hiring pattern suggests {company_data.get('company_stage', 'rapid growth phase')} and could signal great opportunities for candidates in {company_data.get('target_roles', 'technical roles')}.

Recruiters take note: Companies with this hiring velocity often have streamlined processes and competitive packages."""

        hashtags = (
            self.hashtag_categories['recruiting'][:2] +
            self.hashtag_categories['industry'][:2] +
            ['#CompanySpotlight', '#HiringNews']
        )
        
        cta = random.choice(self.cta_templates['network'])
        
        return LinkedInPost(
            post_type=PostType.COMPANY_SPOTLIGHT,
            title=f"{company_data.get('company_name', 'Company')} Hiring Spotlight",
            content=content,
            hashtags=hashtags,
            call_to_action=cta,
            data_source="Company hiring analysis",
            engagement_hooks=["company spotlight", "hiring velocity", "growth phase"],
            target_audience=["recruiters", "talent acquisition", "candidates"]
        )
    
    def generate_recruiter_tip_post(self, tip_data: Dict[str, Any]) -> LinkedInPost:
        """Generate recruiter tip based on data insights"""
        
        context = random.choice(self.professional_context['experience'])
        
        content = f"""💡 Recruiter Tip Tuesday:
        
{context} here's a data-driven insight that can improve your recruiting outcomes:

🎯 {tip_data.get('tip_title', 'Optimize Your Job Posting Timing')}

The data shows: {tip_data.get('data_insight', 'Jobs posted on Tuesday-Thursday get 40% more qualified applications')}

Why this matters: {tip_data.get('explanation', 'Candidates are most active in job searching mid-week when they have mental bandwidth to evaluate opportunities')}

Action item: {tip_data.get('action_item', 'Schedule your high-priority job postings for Tuesday-Thursday to maximize visibility and engagement')}

This small optimization can significantly impact your candidate pipeline quality and time-to-fill metrics."""

        hashtags = (
            self.hashtag_categories['recruiting'][:3] +
            ['#RecruiterTips', '#TalentStrategy']
        )
        
        cta = random.choice(self.cta_templates['discussion'])
        
        return LinkedInPost(
            post_type=PostType.RECRUITER_TIP,
            title="Data-Driven Recruiter Tip",
            content=content,
            hashtags=hashtags,
            call_to_action=cta,
            data_source="Recruiting best practices analysis",
            engagement_hooks=["recruiter tip", "data insight", "action item"],
            target_audience=["recruiters", "talent acquisition", "hiring managers"],
            post_tone=PostTone.CONVERSATIONAL
        )
    
    def generate_geographic_trend_post(self, geo_data: Dict[str, Any]) -> LinkedInPost:
        """Generate geographic hiring trend post"""
        
        hook = random.choice(self.engagement_hooks['surprising_stat'])
        
        content = f"""{hook}
        
The geographic distribution of job opportunities in Northern California is shifting:

🗺️ Geographic Hiring Trends:
• Bay Area: {geo_data.get('bay_area_percentage', 65)}% of total opportunities
• Sacramento Valley: {geo_data.get('sacramento_percentage', 20)}% growth in tech roles
• Remote positions: {geo_data.get('remote_percentage', 35)}% of all postings

Key insight: {geo_data.get('key_insight', 'Companies are expanding beyond traditional tech hubs while maintaining competitive compensation')}

For recruiters: This geographic diversification creates new talent pools and reduces competition for Bay Area-based candidates. Consider expanding your search radius for remote-friendly roles."""

        hashtags = (
            self.hashtag_categories['location'][:3] +
            self.hashtag_categories['recruiting'][:2]
        )
        
        cta = random.choice(self.cta_templates['network'])
        
        return LinkedInPost(
            post_type=PostType.GEOGRAPHIC_TREND,
            title="Northern California Geographic Hiring Trends",
            content=content,
            hashtags=hashtags,
            call_to_action=cta,
            data_source="Geographic hiring analysis",
            engagement_hooks=["geographic trends", "talent pools", "search radius"],
            target_audience=["recruiters", "talent acquisition", "regional hiring managers"],
            geographic_focus="Northern California"
        )
    
    def format_linkedin_post(self, post: LinkedInPost) -> str:
        """Format complete LinkedIn post for publishing"""
        
        formatted_post = f"""{post.content}

{post.call_to_action}

{' '.join(post.hashtags)}

---
Data source: {post.data_source}"""
        
        return formatted_post
    
    def generate_content_calendar(self, job_data: List[Dict[str, Any]], 
                                 days: int = 7) -> List[LinkedInPost]:
        """Generate a content calendar for multiple days"""
        
        posts = []
        post_types = list(PostType)
        
        for day in range(days):
            # Rotate through different post types
            post_type = post_types[day % len(post_types)]
            
            if post_type == PostType.MARKET_INSIGHT:
                post = self.generate_market_insight_post(job_data)
            elif post_type == PostType.HIRING_TREND:
                trend_data = {'companies_analyzed': 150, 'trend_description': 'Increased focus on AI/ML roles', 'percentage_change': 35, 'top_sector': 'Technology'}
                post = self.generate_hiring_trend_post(trend_data)
            elif post_type == PostType.SALARY_ANALYSIS:
                salary_data = {'role_type': 'Senior Software Engineer', 'avg_salary': 165000, 'salary_change': 12, 'remote_premium': 8}
                post = self.generate_salary_analysis_post(salary_data)
            elif post_type == PostType.SKILL_DEMAND:
                skills_data = [
                    {'name': 'Python', 'demand_score': 78, 'category': 'Programming'},
                    {'name': 'AWS', 'demand_score': 65, 'category': 'Cloud'},
                    {'name': 'React', 'demand_score': 58, 'category': 'Frontend'},
                    {'name': 'Machine Learning', 'demand_score': 52, 'category': 'AI/ML'},
                    {'name': 'Kubernetes', 'demand_score': 45, 'category': 'DevOps'}
                ]
                post = self.generate_skill_demand_post(skills_data)
            elif post_type == PostType.RECRUITER_TIP:
                tip_data = {'tip_title': 'Optimize Response Time', 'data_insight': 'Recruiters who respond within 24 hours get 60% higher acceptance rates', 'explanation': 'Candidates appreciate quick communication and it signals company efficiency', 'action_item': 'Set up automated acknowledgments and aim for same-day responses'}
                post = self.generate_recruiter_tip_post(tip_data)
            else:
                # Default to market insight
                post = self.generate_market_insight_post(job_data)
            
            posts.append(post)
        
        return posts


# Utility functions for integration

def generate_weekly_linkedin_content(job_data: List[Dict[str, Any]]) -> List[str]:
    """Generate a week's worth of LinkedIn content"""
    generator = LinkedInContentGenerator()
    posts = generator.generate_content_calendar(job_data, days=7)
    
    formatted_posts = []
    for i, post in enumerate(posts, 1):
        formatted = f"=== Day {i}: {post.title} ===\n\n"
        formatted += generator.format_linkedin_post(post)
        formatted_posts.append(formatted)
    
    return formatted_posts


def create_recruiter_engagement_report(posts: List[LinkedInPost]) -> Dict[str, Any]:
    """Create report on recruiter engagement potential"""
    
    post_type_dist = {}
    for post in posts:
        post_type_dist[post.post_type.value] = post_type_dist.get(post.post_type.value, 0) + 1
    
    total_hashtags = sum(len(post.hashtags) for post in posts)
    avg_hashtags = total_hashtags / len(posts) if posts else 0
    
    return {
        'total_posts_generated': len(posts),
        'post_type_distribution': post_type_dist,
        'average_hashtags_per_post': avg_hashtags,
        'target_audiences': list(set([audience for post in posts for audience in post.target_audience])),
        'geographic_focus_posts': len([p for p in posts if p.geographic_focus]),
        'industry_focus_posts': len([p for p in posts if p.industry_focus]),
        'engagement_strategies': list(set([hook for post in posts for hook in post.engagement_hooks]))
    }
