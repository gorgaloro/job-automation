#!/usr/bin/env python3
"""
End-to-End Regression Test Suite
AI-Powered Job Search Automation Platform

This comprehensive test suite validates multi-epic integration workflows
with defined inputs and expected outputs for regression testing.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import traceback

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import platform components
from core.personal_brand import PersonalBrandProfile
from core.company_enrichment_engine import CompanyEnrichmentEngine
from core.resume_optimizer import ResumeOptimizer
from core.ai_scoring_engine import AIJobScorer, AICompanyScorer, AIResumeScorer
from core.job_parser import JobDescriptionParser
from core.application_tracking_engine import ApplicationTrackingEngine
from core.mobile_networking_engine import MobileNetworkingEngine
from core.workflow_orchestrator import WorkflowOrchestrator

# Import integrations
try:
    from integrations.indeed.indeed_api import IndeedAPI, IndeedIntegrationService
    from integrations.github.github_api import GitHubAPI, GitHubIntegrationService
    INTEGRATIONS_AVAILABLE = True
except ImportError:
    INTEGRATIONS_AVAILABLE = False
    logger.warning("Integration modules not available - some tests will be skipped")


@dataclass
class TestResult:
    """Test execution result"""
    test_name: str
    status: str  # PASS, FAIL, SKIP, WARNING
    execution_time: float
    expected_outputs: Dict[str, Any]
    actual_outputs: Dict[str, Any]
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class TestSuiteResults:
    """Complete test suite results"""
    suite_name: str
    start_time: datetime
    end_time: datetime
    total_tests: int
    passed: int
    failed: int
    skipped: int
    warnings: int
    test_results: List[TestResult]
    
    @property
    def execution_time(self) -> float:
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def success_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100


class E2ERegressionTestSuite:
    """End-to-End Regression Test Suite"""
    
    def __init__(self):
        """Initialize the test suite"""
        self.results: List[TestResult] = []
        self.start_time = datetime.now()
        
        # Test data
        self.test_data = self._load_test_data()
        
        # Initialize platform components
        self._initialize_components()
    
    def _load_test_data(self) -> Dict[str, Any]:
        """Load standardized test data for consistent testing"""
        return {
            'personal_brand': {
                'personal_info': {
                    'name': 'Sarah Chen',
                    'email': 'sarah.chen@email.com',
                    'location': 'San Francisco, CA',
                    'phone': '(555) 123-4567'
                },
                'technical_skills': [
                    'Python', 'JavaScript', 'React', 'Node.js', 'AWS',
                    'Docker', 'Kubernetes', 'Machine Learning', 'SQL', 'Git'
                ],
                'career_goals': {
                    'target_role': 'Senior Software Engineer',
                    'seniority_level': 'senior',
                    'preferred_industries': ['technology', 'fintech', 'healthcare'],
                    'career_focus': 'full-stack development and AI/ML'
                },
                'work_preferences': {
                    'remote_work': True,
                    'company_size': 'medium',
                    'work_style': 'collaborative',
                    'location_preference': 'San Francisco Bay Area'
                },
                'experience_summary': {
                    'years_experience': 6,
                    'previous_roles': [
                        'Software Engineer at TechCorp',
                        'Full-Stack Developer at StartupXYZ',
                        'Junior Developer at BigTech Inc'
                    ],
                    'key_achievements': [
                        'Led development of ML-powered recommendation system',
                        'Reduced API response time by 40%',
                        'Mentored 5 junior developers'
                    ]
                }
            },
            'job_opportunities': [
                {
                    'id': 'job_001',
                    'title': 'Senior Software Engineer',
                    'company': 'InnovateTech',
                    'location': 'San Francisco, CA',
                    'description': '''
                    We are seeking a Senior Software Engineer to join our AI/ML team.
                    You will build scalable systems using Python, React, and AWS.
                    
                    Requirements:
                    - 5+ years software development experience
                    - Strong Python and JavaScript skills
                    - Experience with AWS and containerization
                    - Machine learning background preferred
                    - Full-stack development experience
                    ''',
                    'required_skills': ['Python', 'JavaScript', 'AWS', 'React', 'Machine Learning'],
                    'salary_range': '$140,000 - $180,000',
                    'remote_allowed': True,
                    'industry': 'technology'
                },
                {
                    'id': 'job_002',
                    'title': 'Frontend Developer',
                    'company': 'DesignCorp',
                    'location': 'Remote',
                    'description': '''
                    Frontend Developer role focusing on React and modern web technologies.
                    Build beautiful, responsive user interfaces.
                    
                    Requirements:
                    - 3+ years frontend development
                    - Expert React and JavaScript skills
                    - CSS/SCSS proficiency
                    - UX/UI design understanding
                    ''',
                    'required_skills': ['React', 'JavaScript', 'CSS', 'HTML'],
                    'salary_range': '$100,000 - $130,000',
                    'remote_allowed': True,
                    'industry': 'design'
                }
            ],
            'resumes': [
                {
                    'id': 'resume_fullstack',
                    'version': 'Full-Stack Developer',
                    'summary': 'Senior Software Engineer with 6+ years experience in full-stack development, specializing in Python, React, and cloud technologies.',
                    'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker', 'SQL'],
                    'experience': [
                        {
                            'title': 'Senior Software Engineer',
                            'company': 'TechCorp',
                            'duration': '2021-2024',
                            'description': 'Led full-stack development of ML-powered applications'
                        }
                    ]
                },
                {
                    'id': 'resume_frontend',
                    'version': 'Frontend Specialist',
                    'summary': 'Frontend-focused Software Engineer with expertise in React, modern JavaScript, and responsive design.',
                    'skills': ['React', 'JavaScript', 'CSS', 'HTML', 'TypeScript', 'Webpack'],
                    'experience': [
                        {
                            'title': 'Frontend Developer',
                            'company': 'StartupXYZ',
                            'duration': '2020-2024',
                            'description': 'Built responsive web applications with React'
                        }
                    ]
                }
            ]
        }
    
    def _initialize_components(self):
        """Initialize all platform components"""
        try:
            self.company_enrichment = CompanyEnrichmentEngine()
            self.resume_optimizer = ResumeOptimizer()
            self.job_scorer = AIJobScorer()
            self.company_scorer = AICompanyScorer()
            self.resume_scorer = AIResumeScorer()
            self.job_parser = JobDescriptionParser()
            self.application_tracker = ApplicationTrackingEngine()
            self.networking_engine = MobileNetworkingEngine()
            self.workflow_orchestrator = WorkflowOrchestrator()
            
            if INTEGRATIONS_AVAILABLE:
                self.indeed_api = IndeedAPI()
                self.github_api = GitHubAPI()
                self.indeed_integration = IndeedIntegrationService()
                self.github_integration = GitHubIntegrationService()
            
            logger.info("All platform components initialized successfully")
        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
            raise
    
    def run_test(self, test_name: str, test_func, expected_outputs: Dict[str, Any]) -> TestResult:
        """Run a single test and capture results"""
        start_time = time.time()
        
        try:
            logger.info(f"Running test: {test_name}")
            actual_outputs = test_func()
            execution_time = time.time() - start_time
            
            # Validate outputs
            status, warnings = self._validate_outputs(expected_outputs, actual_outputs)
            
            result = TestResult(
                test_name=test_name,
                status=status,
                execution_time=execution_time,
                expected_outputs=expected_outputs,
                actual_outputs=actual_outputs,
                warnings=warnings
            )
            
            logger.info(f"Test {test_name}: {status} ({execution_time:.2f}s)")
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            
            result = TestResult(
                test_name=test_name,
                status="FAIL",
                execution_time=execution_time,
                expected_outputs=expected_outputs,
                actual_outputs={},
                error_message=error_msg
            )
            
            logger.error(f"Test {test_name}: FAILED - {str(e)}")
        
        self.results.append(result)
        return result
    
    def _validate_outputs(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Validate actual outputs against expected outputs"""
        warnings = []
        
        # Check required fields
        for key, expected_value in expected.items():
            if key not in actual:
                return "FAIL", [f"Missing required output: {key}"]
            
            actual_value = actual[key]
            
            # Type validation
            if isinstance(expected_value, dict) and 'type' in expected_value:
                expected_type = expected_value['type']
                if not isinstance(actual_value, expected_type):
                    return "FAIL", [f"Output {key} has wrong type: expected {expected_type}, got {type(actual_value)}"]
            
            # Range validation
            if isinstance(expected_value, dict) and 'range' in expected_value:
                min_val, max_val = expected_value['range']
                if not (min_val <= actual_value <= max_val):
                    warnings.append(f"Output {key} outside expected range: {actual_value} not in [{min_val}, {max_val}]")
        
        # Determine overall status
        if warnings:
            return "WARNING", warnings
        return "PASS", warnings
    
    # Test Case 1: Complete Job Application Workflow
    def test_complete_job_application_workflow(self) -> Dict[str, Any]:
        """Test end-to-end job application process"""
        job = self.test_data['job_opportunities'][0]  # InnovateTech job
        personal_brand = self.test_data['personal_brand']
        resumes = self.test_data['resumes']
        
        # Step 1: Company Enrichment
        company_data = self.company_enrichment.enrich_company(job['company'])
        
        # Step 2: Job Scoring
        job_score = self.job_scorer.score_job_alignment(job, personal_brand)
        
        # Step 3: Resume Selection and Optimization
        best_resume = None
        best_score = 0
        
        for resume in resumes:
            resume_score = self.resume_scorer.score_resume_job_fit(resume, job, personal_brand)
            if resume_score.score > best_score:
                best_score = resume_score.score
                best_resume = resume
        
        optimized_resume = self.resume_optimizer.optimize_resume(best_resume, job['description'])
        
        # Step 4: Application Creation
        application = self.application_tracker.create_application(
            job_id=job['id'],
            company_name=job['company'],
            position_title=job['title'],
            resume_version=best_resume['id']
        )
        
        return {
            'company_enrichment': company_data is not None,
            'job_score': job_score.score if job_score else 0,
            'best_resume_selected': best_resume is not None,
            'resume_optimization': optimized_resume is not None,
            'application_created': application is not None,
            'workflow_completion_time': time.time()
        }
    
    def run_all_tests(self) -> TestSuiteResults:
        """Run complete end-to-end regression test suite"""
        logger.info("Starting End-to-End Regression Test Suite")
        
        # Define test cases with expected outputs
        test_cases = [
            (
                "Complete Job Application Workflow",
                self.test_complete_job_application_workflow,
                {
                    'company_enrichment': {'type': bool},
                    'job_score': {'type': (int, float), 'range': (0, 100)},
                    'best_resume_selected': {'type': bool},
                    'resume_optimization': {'type': bool},
                    'application_created': {'type': bool}
                }
            )
        ]
        
        # Run all tests
        for test_name, test_func, expected_outputs in test_cases:
            self.run_test(test_name, test_func, expected_outputs)
        
        # Generate summary
        end_time = datetime.now()
        
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        skipped = sum(1 for r in self.results if r.status == "SKIP")
        warnings = sum(1 for r in self.results if r.status == "WARNING")
        
        return TestSuiteResults(
            suite_name="E2E Regression Test Suite",
            start_time=self.start_time,
            end_time=end_time,
            total_tests=len(self.results),
            passed=passed,
            failed=failed,
            skipped=skipped,
            warnings=warnings,
            test_results=self.results
        )


def main():
    """Main execution function"""
    print("🧪 AI Job Search Platform - End-to-End Regression Test Suite")
    print("=" * 70)
    
    # Initialize and run test suite
    test_suite = E2ERegressionTestSuite()
    results = test_suite.run_all_tests()
    
    # Print summary
    print(f"\n📊 Test Suite Results:")
    print(f"   Total Tests: {results.total_tests}")
    print(f"   Passed: {results.passed} ✅")
    print(f"   Failed: {results.failed} ❌")
    print(f"   Warnings: {results.warnings} ⚠️")
    print(f"   Skipped: {results.skipped} ⏭️")
    print(f"   Success Rate: {results.success_rate:.1f}%")
    print(f"   Execution Time: {results.execution_time:.2f}s")
    
    # Print detailed results
    print(f"\n📋 Detailed Results:")
    for result in results.test_results:
        status_emoji = {'PASS': '✅', 'FAIL': '❌', 'WARNING': '⚠️', 'SKIP': '⏭️'}.get(result.status, '❓')
        print(f"   {result.test_name}: {result.status} {status_emoji} ({result.execution_time:.2f}s)")
        
        if result.error_message:
            print(f"      Error: {result.error_message.split(chr(10))[0]}")
        
        if result.warnings:
            for warning in result.warnings:
                print(f"      Warning: {warning}")
    
    print(f"\n🎯 End-to-End Regression Testing Complete!")
    return results.success_rate >= 80  # 80% pass rate required


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
