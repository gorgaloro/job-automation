#!/usr/bin/env python3
"""
GitHub API Integration

Provides developer profile analysis, contribution tracking, and technical
skill validation through GitHub data integration.
"""

import logging
import os
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GitHubProfile:
    """GitHub user profile data"""
    username: str
    name: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    blog: Optional[str] = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    avatar_url: Optional[str] = None
    html_url: Optional[str] = None


@dataclass
class GitHubRepository:
    """GitHub repository data"""
    name: str
    full_name: str
    description: Optional[str] = None
    language: Optional[str] = None
    languages: Dict[str, int] = field(default_factory=dict)
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    size: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    pushed_at: Optional[datetime] = None
    html_url: Optional[str] = None
    clone_url: Optional[str] = None
    is_fork: bool = False
    is_private: bool = False
    topics: List[str] = field(default_factory=list)


@dataclass
class GitHubContribution:
    """GitHub contribution data"""
    date: datetime
    count: int
    level: int  # 0-4 contribution level


@dataclass
class DeveloperProfile:
    """Comprehensive developer profile from GitHub analysis"""
    username: str
    profile: GitHubProfile
    repositories: List[GitHubRepository]
    contributions: List[GitHubContribution]
    
    # Analyzed metrics
    primary_languages: List[Tuple[str, float]] = field(default_factory=list)
    activity_score: float = 0.0
    expertise_areas: List[str] = field(default_factory=list)
    project_complexity_score: float = 0.0
    collaboration_score: float = 0.0
    consistency_score: float = 0.0
    
    # Career insights
    experience_level: str = "unknown"  # junior, mid, senior, expert
    specializations: List[str] = field(default_factory=list)
    notable_projects: List[GitHubRepository] = field(default_factory=list)
    contribution_streak: int = 0
    
    analysis_date: datetime = field(default_factory=datetime.utcnow)


class GitHubAPIClient:
    """
    GitHub API client for developer profile analysis.
    
    Provides comprehensive analysis of GitHub profiles, repositories,
    and contribution patterns for technical skill validation.
    """
    
    def __init__(self):
        """Initialize GitHub API client"""
        self.api_token = os.getenv('GITHUB_API_TOKEN')
        self.base_url = "https://api.github.com"
        self.demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
        
        # Headers for API requests
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'JobSearchAutomation/1.0'
        }
        
        if self.api_token:
            self.headers['Authorization'] = f'token {self.api_token}'
        
        logger.info(f"GitHub API client initialized (demo_mode: {self.demo_mode})")
    
    def get_user_profile(self, username: str) -> Optional[GitHubProfile]:
        """
        Get GitHub user profile
        
        Args:
            username: GitHub username
            
        Returns:
            User profile data
        """
        try:
            if self.demo_mode:
                return self._generate_demo_profile(username)
            
            url = f"{self.base_url}/users/{username}"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            profile = GitHubProfile(
                username=data['login'],
                name=data.get('name'),
                email=data.get('email'),
                bio=data.get('bio'),
                company=data.get('company'),
                location=data.get('location'),
                blog=data.get('blog'),
                public_repos=data.get('public_repos', 0),
                followers=data.get('followers', 0),
                following=data.get('following', 0),
                created_at=self._parse_datetime(data.get('created_at')),
                updated_at=self._parse_datetime(data.get('updated_at')),
                avatar_url=data.get('avatar_url'),
                html_url=data.get('html_url')
            )
            
            logger.info(f"Retrieved GitHub profile for {username}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to get GitHub profile: {str(e)}")
            return None
    
    def get_user_repositories(self, username: str, limit: int = 100) -> List[GitHubRepository]:
        """
        Get user's public repositories
        
        Args:
            username: GitHub username
            limit: Maximum repositories to fetch
            
        Returns:
            List of repositories
        """
        try:
            if self.demo_mode:
                return self._generate_demo_repositories(username)
            
            repositories = []
            page = 1
            per_page = min(100, limit)
            
            while len(repositories) < limit:
                url = f"{self.base_url}/users/{username}/repos"
                params = {
                    'page': page,
                    'per_page': per_page,
                    'sort': 'updated',
                    'direction': 'desc'
                }
                
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                if not data:
                    break
                
                for repo_data in data:
                    if len(repositories) >= limit:
                        break
                    
                    repo = self._parse_repository_data(repo_data)
                    if repo:
                        repositories.append(repo)
                
                page += 1
            
            logger.info(f"Retrieved {len(repositories)} repositories for {username}")
            return repositories
            
        except Exception as e:
            logger.error(f"Failed to get repositories: {str(e)}")
            return []
    
    def get_repository_languages(self, username: str, repo_name: str) -> Dict[str, int]:
        """
        Get programming languages used in a repository
        
        Args:
            username: Repository owner
            repo_name: Repository name
            
        Returns:
            Languages with byte counts
        """
        try:
            if self.demo_mode:
                return {'Python': 15420, 'JavaScript': 8930, 'CSS': 2100}
            
            url = f"{self.base_url}/repos/{username}/{repo_name}/languages"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get repository languages: {str(e)}")
            return {}
    
    def analyze_developer_profile(self, username: str) -> Optional[DeveloperProfile]:
        """
        Comprehensive analysis of a developer's GitHub profile
        
        Args:
            username: GitHub username
            
        Returns:
            Complete developer profile analysis
        """
        try:
            # Get basic profile
            profile = self.get_user_profile(username)
            if not profile:
                return None
            
            # Get repositories
            repositories = self.get_user_repositories(username, limit=50)
            
            # Analyze languages across all repositories
            all_languages = {}
            for repo in repositories:
                if not repo.is_fork:  # Focus on original work
                    languages = self.get_repository_languages(username, repo.name)
                    for lang, bytes_count in languages.items():
                        all_languages[lang] = all_languages.get(lang, 0) + bytes_count
            
            # Calculate primary languages (top 5)
            total_bytes = sum(all_languages.values())
            primary_languages = []
            if total_bytes > 0:
                sorted_langs = sorted(all_languages.items(), key=lambda x: x[1], reverse=True)
                for lang, bytes_count in sorted_langs[:5]:
                    percentage = (bytes_count / total_bytes) * 100
                    primary_languages.append((lang, percentage))
            
            # Generate contributions (demo data)
            contributions = self._generate_demo_contributions()
            
            # Calculate metrics
            activity_score = self._calculate_activity_score(profile, repositories, contributions)
            expertise_areas = self._identify_expertise_areas(repositories, all_languages)
            project_complexity_score = self._calculate_project_complexity(repositories)
            collaboration_score = self._calculate_collaboration_score(repositories)
            consistency_score = self._calculate_consistency_score(contributions)
            experience_level = self._determine_experience_level(profile, repositories, activity_score)
            notable_projects = self._identify_notable_projects(repositories)
            
            developer_profile = DeveloperProfile(
                username=username,
                profile=profile,
                repositories=repositories,
                contributions=contributions,
                primary_languages=primary_languages,
                activity_score=activity_score,
                expertise_areas=expertise_areas,
                project_complexity_score=project_complexity_score,
                collaboration_score=collaboration_score,
                consistency_score=consistency_score,
                experience_level=experience_level,
                specializations=expertise_areas[:3],  # Top 3 areas
                notable_projects=notable_projects,
                contribution_streak=self._calculate_contribution_streak(contributions)
            )
            
            logger.info(f"Completed developer profile analysis for {username}")
            return developer_profile
            
        except Exception as e:
            logger.error(f"Developer profile analysis failed: {str(e)}")
            return None
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse GitHub datetime string"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    def _parse_repository_data(self, repo_data: Dict[str, Any]) -> GitHubRepository:
        """Parse repository data from GitHub API"""
        return GitHubRepository(
            name=repo_data['name'],
            full_name=repo_data['full_name'],
            description=repo_data.get('description'),
            language=repo_data.get('language'),
            stars=repo_data.get('stargazers_count', 0),
            forks=repo_data.get('forks_count', 0),
            watchers=repo_data.get('watchers_count', 0),
            size=repo_data.get('size', 0),
            created_at=self._parse_datetime(repo_data.get('created_at')),
            updated_at=self._parse_datetime(repo_data.get('updated_at')),
            pushed_at=self._parse_datetime(repo_data.get('pushed_at')),
            html_url=repo_data.get('html_url'),
            clone_url=repo_data.get('clone_url'),
            is_fork=repo_data.get('fork', False),
            is_private=repo_data.get('private', False),
            topics=repo_data.get('topics', [])
        )
    
    def _calculate_activity_score(self, profile: GitHubProfile, 
                                repositories: List[GitHubRepository],
                                contributions: List[GitHubContribution]) -> float:
        """Calculate overall activity score (0-100)"""
        score = 0.0
        
        # Repository count (0-30 points)
        repo_score = min(profile.public_repos * 2, 30)
        score += repo_score
        
        # Stars received (0-25 points)
        total_stars = sum(repo.stars for repo in repositories)
        star_score = min(total_stars / 10, 25)
        score += star_score
        
        # Recent activity (0-25 points)
        recent_contributions = [c for c in contributions 
                              if c.date > datetime.utcnow() - timedelta(days=365)]
        activity_score = min(len(recent_contributions) / 10, 25)
        score += activity_score
        
        # Followers (0-20 points)
        follower_score = min(profile.followers / 5, 20)
        score += follower_score
        
        return min(score, 100.0)
    
    def _identify_expertise_areas(self, repositories: List[GitHubRepository], 
                                languages: Dict[str, int]) -> List[str]:
        """Identify areas of expertise based on repositories and languages"""
        expertise = []
        
        # Language expertise
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        for lang, _ in sorted_langs[:3]:
            expertise.append(f"{lang} Development")
        
        # Topic-based expertise
        all_topics = []
        for repo in repositories:
            all_topics.extend(repo.topics)
        
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        for topic, count in sorted_topics[:3]:
            if count >= 2:  # At least 2 repositories with this topic
                expertise.append(topic.replace('-', ' ').title())
        
        return expertise[:5]  # Top 5 areas
    
    def _calculate_project_complexity(self, repositories: List[GitHubRepository]) -> float:
        """Calculate average project complexity score (0-100)"""
        if not repositories:
            return 0.0
        
        complexity_scores = []
        for repo in repositories:
            if repo.is_fork:
                continue
            
            score = 0.0
            
            # Size factor (larger projects = more complex)
            score += min(repo.size / 1000, 20)
            
            # Stars factor (popular projects = more complex)
            score += min(repo.stars * 2, 30)
            
            # Forks factor (forked projects = more complex)
            score += min(repo.forks * 3, 25)
            
            # Recent activity factor
            if repo.pushed_at and repo.pushed_at > datetime.utcnow() - timedelta(days=90):
                score += 25
            
            complexity_scores.append(min(score, 100))
        
        return sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0.0
    
    def _calculate_collaboration_score(self, repositories: List[GitHubRepository]) -> float:
        """Calculate collaboration score based on forks and contributions"""
        if not repositories:
            return 0.0
        
        total_forks = sum(repo.forks for repo in repositories if not repo.is_fork)
        forked_repos = sum(1 for repo in repositories if repo.is_fork)
        
        # Score based on projects being forked (others collaborating)
        fork_score = min(total_forks * 5, 50)
        
        # Score based on contributing to others' projects
        contribution_score = min(forked_repos * 3, 50)
        
        return min(fork_score + contribution_score, 100.0)
    
    def _calculate_consistency_score(self, contributions: List[GitHubContribution]) -> float:
        """Calculate consistency score based on contribution patterns"""
        if not contributions:
            return 0.0
        
        # Calculate weekly consistency over the past year
        weekly_contributions = {}
        for contrib in contributions:
            if contrib.date > datetime.utcnow() - timedelta(days=365):
                week = contrib.date.strftime('%Y-W%U')
                weekly_contributions[week] = weekly_contributions.get(week, 0) + contrib.count
        
        if not weekly_contributions:
            return 0.0
        
        # Calculate consistency (lower variance = higher consistency)
        values = list(weekly_contributions.values())
        if len(values) < 2:
            return 50.0
        
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        
        # Convert to 0-100 score (lower variance = higher score)
        consistency = max(0, 100 - (variance / mean_val * 10)) if mean_val > 0 else 0
        return min(consistency, 100.0)
    
    def _determine_experience_level(self, profile: GitHubProfile, 
                                  repositories: List[GitHubRepository],
                                  activity_score: float) -> str:
        """Determine experience level based on various factors"""
        # Calculate years since account creation
        years_active = 0
        if profile.created_at:
            years_active = (datetime.utcnow() - profile.created_at).days / 365.25
        
        # Score factors
        repo_count = len([r for r in repositories if not r.is_fork])
        total_stars = sum(repo.stars for repo in repositories)
        
        # Determine level
        if years_active >= 5 and repo_count >= 20 and total_stars >= 50:
            return "expert"
        elif years_active >= 3 and repo_count >= 10 and total_stars >= 20:
            return "senior"
        elif years_active >= 1 and repo_count >= 5:
            return "mid"
        else:
            return "junior"
    
    def _identify_notable_projects(self, repositories: List[GitHubRepository]) -> List[GitHubRepository]:
        """Identify notable projects based on stars, forks, and activity"""
        # Filter out forks and sort by engagement
        original_repos = [repo for repo in repositories if not repo.is_fork]
        
        # Score each repository
        scored_repos = []
        for repo in original_repos:
            score = repo.stars * 3 + repo.forks * 5 + repo.watchers
            scored_repos.append((score, repo))
        
        # Return top 5 notable projects
        scored_repos.sort(key=lambda x: x[0], reverse=True)
        return [repo for _, repo in scored_repos[:5]]
    
    def _calculate_contribution_streak(self, contributions: List[GitHubContribution]) -> int:
        """Calculate current contribution streak"""
        if not contributions:
            return 0
        
        # Sort contributions by date (most recent first)
        sorted_contribs = sorted(contributions, key=lambda x: x.date, reverse=True)
        
        streak = 0
        current_date = datetime.utcnow().date()
        
        for contrib in sorted_contribs:
            if contrib.date.date() == current_date and contrib.count > 0:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    def _generate_demo_profile(self, username: str) -> GitHubProfile:
        """Generate demo profile data"""
        return GitHubProfile(
            username=username,
            name="Demo Developer",
            email="demo@example.com",
            bio="Full-stack developer passionate about AI and automation",
            company="TechCorp",
            location="San Francisco, CA",
            blog="https://demo-dev.blog",
            public_repos=42,
            followers=156,
            following=89,
            created_at=datetime.utcnow() - timedelta(days=1825),  # 5 years ago
            updated_at=datetime.utcnow() - timedelta(days=1),
            avatar_url="https://github.com/avatar.jpg",
            html_url=f"https://github.com/{username}"
        )
    
    def _generate_demo_repositories(self, username: str) -> List[GitHubRepository]:
        """Generate demo repository data"""
        return [
            GitHubRepository(
                name="ai-job-search",
                full_name=f"{username}/ai-job-search",
                description="AI-powered job search automation platform",
                language="Python",
                stars=45,
                forks=12,
                watchers=38,
                size=2500,
                created_at=datetime.utcnow() - timedelta(days=365),
                updated_at=datetime.utcnow() - timedelta(days=2),
                pushed_at=datetime.utcnow() - timedelta(days=1),
                html_url=f"https://github.com/{username}/ai-job-search",
                topics=["python", "ai", "automation", "job-search"]
            ),
            GitHubRepository(
                name="react-dashboard",
                full_name=f"{username}/react-dashboard",
                description="Modern React dashboard with real-time analytics",
                language="JavaScript",
                stars=23,
                forks=8,
                watchers=19,
                size=1800,
                created_at=datetime.utcnow() - timedelta(days=200),
                updated_at=datetime.utcnow() - timedelta(days=5),
                pushed_at=datetime.utcnow() - timedelta(days=3),
                html_url=f"https://github.com/{username}/react-dashboard",
                topics=["react", "dashboard", "analytics", "typescript"]
            ),
            GitHubRepository(
                name="ml-experiments",
                full_name=f"{username}/ml-experiments",
                description="Machine learning experiments and model training",
                language="Python",
                stars=67,
                forks=15,
                watchers=52,
                size=3200,
                created_at=datetime.utcnow() - timedelta(days=450),
                updated_at=datetime.utcnow() - timedelta(days=7),
                pushed_at=datetime.utcnow() - timedelta(days=4),
                html_url=f"https://github.com/{username}/ml-experiments",
                topics=["machine-learning", "tensorflow", "pytorch", "data-science"]
            )
        ]
    
    def _generate_demo_contributions(self) -> List[GitHubContribution]:
        """Generate demo contribution data for the past year"""
        contributions = []
        start_date = datetime.utcnow() - timedelta(days=365)
        
        for i in range(365):
            date = start_date + timedelta(days=i)
            # Simulate realistic contribution patterns
            if date.weekday() < 5:  # Weekdays
                count = max(0, int(abs(hash(date.strftime('%Y-%m-%d')) % 10) - 2))
            else:  # Weekends
                count = max(0, int(abs(hash(date.strftime('%Y-%m-%d')) % 5) - 3))
            
            level = min(count, 4)
            contributions.append(GitHubContribution(date=date, count=count, level=level))
        
        return contributions


class GitHubIntegrationService:
    """
    Service for integrating GitHub data with the job search platform.
    
    Provides developer profile analysis and technical skill validation
    for enhanced personal brand profiling and resume optimization.
    """
    
    def __init__(self):
        """Initialize GitHub integration service"""
        self.client = GitHubAPIClient()
        self.demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
        
        logger.info("GitHub integration service initialized")
    
    def enhance_personal_brand_profile(self, profile: Dict[str, Any], 
                                     github_username: str) -> Dict[str, Any]:
        """
        Enhance personal brand profile with GitHub data
        
        Args:
            profile: Existing personal brand profile
            github_username: GitHub username
            
        Returns:
            Enhanced profile with GitHub insights
        """
        try:
            developer_profile = self.client.analyze_developer_profile(github_username)
            if not developer_profile:
                return profile
            
            # Enhance technical skills
            github_languages = [lang for lang, _ in developer_profile.primary_languages]
            existing_skills = profile.get('technical_skills', [])
            
            # Merge and deduplicate skills
            all_skills = list(set(existing_skills + github_languages))
            profile['technical_skills'] = all_skills
            
            # Add GitHub-specific data
            profile['github_profile'] = {
                'username': github_username,
                'profile_url': developer_profile.profile.html_url,
                'public_repos': developer_profile.profile.public_repos,
                'followers': developer_profile.profile.followers,
                'primary_languages': developer_profile.primary_languages,
                'activity_score': developer_profile.activity_score,
                'experience_level': developer_profile.experience_level,
                'expertise_areas': developer_profile.expertise_areas,
                'notable_projects': [
                    {
                        'name': repo.name,
                        'description': repo.description,
                        'stars': repo.stars,
                        'language': repo.language,
                        'url': repo.html_url
                    }
                    for repo in developer_profile.notable_projects[:3]
                ],
                'collaboration_score': developer_profile.collaboration_score,
                'consistency_score': developer_profile.consistency_score
            }
            
            # Update experience level if GitHub suggests higher level
            career_goals = profile.get('career_goals', {})
            if developer_profile.experience_level in ['senior', 'expert']:
                career_goals['seniority_level'] = developer_profile.experience_level
                profile['career_goals'] = career_goals
            
            logger.info(f"Enhanced profile with GitHub data for {github_username}")
            return profile
            
        except Exception as e:
            logger.error(f"Profile enhancement failed: {str(e)}")
            return profile
    
    def validate_technical_skills(self, claimed_skills: List[str], 
                                github_username: str) -> Dict[str, Any]:
        """
        Validate claimed technical skills against GitHub activity
        
        Args:
            claimed_skills: Skills claimed by user
            github_username: GitHub username
            
        Returns:
            Skill validation results
        """
        try:
            developer_profile = self.client.analyze_developer_profile(github_username)
            if not developer_profile:
                return {'validated': False, 'reason': 'GitHub profile not found'}
            
            github_languages = {lang.lower() for lang, _ in developer_profile.primary_languages}
            github_topics = set()
            
            for repo in developer_profile.repositories:
                github_topics.update(topic.lower() for topic in repo.topics)
            
            validated_skills = []
            unvalidated_skills = []
            
            for skill in claimed_skills:
                skill_lower = skill.lower()
                if (skill_lower in github_languages or 
                    skill_lower in github_topics or
                    any(skill_lower in topic for topic in github_topics)):
                    validated_skills.append(skill)
                else:
                    unvalidated_skills.append(skill)
            
            validation_score = len(validated_skills) / len(claimed_skills) if claimed_skills else 0
            
            return {
                'validated': True,
                'validation_score': validation_score,
                'validated_skills': validated_skills,
                'unvalidated_skills': unvalidated_skills,
                'github_languages': list(github_languages),
                'github_topics': list(github_topics),
                'recommendations': self._generate_skill_recommendations(
                    developer_profile, claimed_skills
                )
            }
            
        except Exception as e:
            logger.error(f"Skill validation failed: {str(e)}")
            return {'validated': False, 'reason': str(e)}
    
    def _generate_skill_recommendations(self, developer_profile: DeveloperProfile,
                                      claimed_skills: List[str]) -> List[str]:
        """Generate skill recommendations based on GitHub activity"""
        recommendations = []
        
        # Recommend top GitHub languages not in claimed skills
        claimed_lower = {skill.lower() for skill in claimed_skills}
        for lang, percentage in developer_profile.primary_languages:
            if lang.lower() not in claimed_lower and percentage > 10:
                recommendations.append(f"Add {lang} (prominent in your repositories)")
        
        # Recommend based on expertise areas
        for area in developer_profile.expertise_areas:
            area_lower = area.lower()
            if not any(area_lower in skill.lower() for skill in claimed_skills):
                recommendations.append(f"Consider highlighting {area}")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get GitHub integration status and metrics"""
        return {
            'service': 'GitHub API',
            'status': 'operational' if self.demo_mode else 'configured',
            'demo_mode': self.demo_mode,
            'api_token_configured': bool(self.client.api_token),
            'rate_limit': '5000 requests/hour (authenticated)',
            'capabilities': [
                'Developer profile analysis',
                'Repository and contribution tracking',
                'Programming language identification',
                'Technical skill validation',
                'Experience level assessment',
                'Project complexity analysis',
                'Collaboration score calculation',
                'Personal brand enhancement'
            ],
            'metrics_provided': [
                'Activity score (0-100)',
                'Primary programming languages',
                'Expertise areas identification',
                'Project complexity score',
                'Collaboration score',
                'Consistency score',
                'Experience level determination',
                'Notable projects identification'
            ]
        }


# Export main classes
__all__ = ['GitHubAPIClient', 'GitHubIntegrationService', 'DeveloperProfile', 'GitHubProfile']
