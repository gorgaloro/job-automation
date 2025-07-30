#!/usr/bin/env python3
"""
Job Description Parser - Enhanced Cover Letter Detection

Analyzes job descriptions and application requirements to determine:
- Whether cover letters are required, optional, or not accepted
- Application submission format and requirements
- Company preferences for application materials

This module supports the unified Resume + Cover Letter Optimizer workflow
by intelligently detecting when cover letter generation is appropriate.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum

class CoverLetterRequirement(Enum):
    """Cover letter requirement levels"""
    REQUIRED = "required"
    OPTIONAL = "optional" 
    PREFERRED = "preferred"
    NOT_MENTIONED = "not_mentioned"
    NOT_ACCEPTED = "not_accepted"

class ApplicationFormat(Enum):
    """Application submission formats"""
    ATS_SYSTEM = "ats_system"
    EMAIL_APPLICATION = "email_application"
    COMPANY_PORTAL = "company_portal"
    THIRD_PARTY_PLATFORM = "third_party_platform"
    UNKNOWN = "unknown"

@dataclass
class CoverLetterAnalysis:
    """Analysis results for cover letter requirements"""
    requirement_level: CoverLetterRequirement
    confidence_score: float
    supporting_text: List[str]
    application_format: ApplicationFormat
    submission_instructions: str
    additional_requirements: List[str]
    recommendation: str

class JobDescriptionParser:
    """
    Enhanced job description parser with cover letter detection
    """
    
    def __init__(self):
        """Initialize parser with detection patterns"""
        self.setup_detection_patterns()
    
    def setup_detection_patterns(self):
        """Setup regex patterns for cover letter detection"""
        
        # Required patterns
        self.required_patterns = [
            r"cover letter.*required",
            r"must.*include.*cover letter",
            r"cover letter.*mandatory",
            r"application.*must.*include.*cover letter",
            r"please.*submit.*cover letter",
            r"cover letter.*necessary",
            r"include.*cover letter.*with.*application"
        ]
        
        # Optional/Preferred patterns
        self.optional_patterns = [
            r"cover letter.*optional",
            r"cover letter.*preferred",
            r"cover letter.*welcome",
            r"cover letter.*encouraged",
            r"may.*include.*cover letter",
            r"cover letter.*would be.*appreciated",
            r"cover letter.*helpful",
            r"optional.*but.*encouraged"
        ]
        
        # Not accepted patterns
        self.not_accepted_patterns = [
            r"no.*cover letter",
            r"do not.*submit.*cover letter",
            r"do not.*include.*cover letter",
            r"resume.*only",
            r"cv.*only",
            r"no.*additional.*documents"
        ]
        
        # Application format patterns
        self.format_patterns = {
            ApplicationFormat.ATS_SYSTEM: [
                r"apply.*through.*our.*system",
                r"online.*application.*system",
                r"ats.*system",
                r"workday.*application",
                r"greenhouse.*application",
                r"lever.*application"
            ],
            ApplicationFormat.EMAIL_APPLICATION: [
                r"email.*resume.*to",
                r"send.*application.*to",
                r"email.*application.*to",
                r"submit.*via.*email"
            ],
            ApplicationFormat.COMPANY_PORTAL: [
                r"company.*website",
                r"careers.*page",
                r"apply.*on.*our.*website",
                r"company.*portal"
            ]
        }
        
        # Compile patterns for efficiency
        self.compiled_required = [re.compile(pattern, re.IGNORECASE) for pattern in self.required_patterns]
        self.compiled_optional = [re.compile(pattern, re.IGNORECASE) for pattern in self.optional_patterns]
        self.compiled_not_accepted = [re.compile(pattern, re.IGNORECASE) for pattern in self.not_accepted_patterns]
        
        self.compiled_formats = {}
        for format_type, patterns in self.format_patterns.items():
            self.compiled_formats[format_type] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def analyze_cover_letter_requirements(self, job_description: str) -> CoverLetterAnalysis:
        """
        Analyze job description to determine cover letter requirements
        """
        
        # Clean and normalize text
        text = self._clean_text(job_description)
        
        # Check for explicit patterns
        required_matches = self._find_pattern_matches(text, self.compiled_required)
        optional_matches = self._find_pattern_matches(text, self.compiled_optional)
        not_accepted_matches = self._find_pattern_matches(text, self.compiled_not_accepted)
        
        # Determine requirement level and confidence
        requirement_level, confidence, supporting_text = self._determine_requirement_level(
            required_matches, optional_matches, not_accepted_matches, text
        )
        
        # Detect application format
        application_format = self._detect_application_format(text)
        
        # Extract submission instructions
        submission_instructions = self._extract_submission_instructions(text)
        
        # Find additional requirements
        additional_requirements = self._extract_additional_requirements(text)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(requirement_level, application_format)
        
        return CoverLetterAnalysis(
            requirement_level=requirement_level,
            confidence_score=confidence,
            supporting_text=supporting_text,
            application_format=application_format,
            submission_instructions=submission_instructions,
            additional_requirements=additional_requirements,
            recommendation=recommendation
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for analysis"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def _find_pattern_matches(self, text: str, compiled_patterns: List[re.Pattern]) -> List[str]:
        """Find all matches for given patterns"""
        matches = []
        for pattern in compiled_patterns:
            found = pattern.findall(text)
            matches.extend(found)
        return matches
    
    def _determine_requirement_level(
        self, 
        required_matches: List[str], 
        optional_matches: List[str], 
        not_accepted_matches: List[str],
        text: str
    ) -> Tuple[CoverLetterRequirement, float, List[str]]:
        """Determine cover letter requirement level with confidence score"""
        
        supporting_text = []
        
        # Check for explicit rejections first
        if not_accepted_matches:
            return CoverLetterRequirement.NOT_ACCEPTED, 0.9, not_accepted_matches
        
        # Check for explicit requirements
        if required_matches:
            return CoverLetterRequirement.REQUIRED, 0.9, required_matches
        
        # Check for optional/preferred
        if optional_matches:
            return CoverLetterRequirement.OPTIONAL, 0.8, optional_matches
        
        # Look for implicit indicators
        implicit_indicators = self._find_implicit_indicators(text)
        if implicit_indicators:
            supporting_text.extend(implicit_indicators)
            
            # If we found some indicators, assume optional
            if len(implicit_indicators) > 0:
                return CoverLetterRequirement.OPTIONAL, 0.6, supporting_text
        
        # Default to not mentioned with low confidence
        return CoverLetterRequirement.NOT_MENTIONED, 0.3, []
    
    def _find_implicit_indicators(self, text: str) -> List[str]:
        """Find implicit indicators that suggest cover letter acceptance"""
        
        implicit_patterns = [
            r"tell us.*why.*interested",
            r"explain.*motivation",
            r"describe.*passion",
            r"why.*want.*to.*work",
            r"what.*draws.*you",
            r"personal.*statement",
            r"motivation.*letter"
        ]
        
        matches = []
        for pattern in implicit_patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            matches.extend(found)
        
        return matches
    
    def _detect_application_format(self, text: str) -> ApplicationFormat:
        """Detect application submission format"""
        
        for format_type, patterns in self.compiled_formats.items():
            for pattern in patterns:
                if pattern.search(text):
                    return format_type
        
        return ApplicationFormat.UNKNOWN
    
    def _extract_submission_instructions(self, text: str) -> str:
        """Extract specific submission instructions"""
        
        instruction_patterns = [
            r"to apply[^.]*\.",
            r"submit.*application[^.]*\.",
            r"send.*resume[^.]*\.",
            r"apply.*by[^.]*\.",
            r"application.*process[^.]*\."
        ]
        
        instructions = []
        for pattern in instruction_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            instructions.extend(matches)
        
        return " ".join(instructions[:3])  # Limit to first 3 instructions
    
    def _extract_additional_requirements(self, text: str) -> List[str]:
        """Extract additional application requirements"""
        
        requirement_patterns = [
            r"portfolio.*required",
            r"work.*samples",
            r"references.*required",
            r"writing.*sample",
            r"code.*sample",
            r"design.*portfolio",
            r"linkedin.*profile"
        ]
        
        requirements = []
        for pattern in requirement_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            requirements.extend(matches)
        
        return list(set(requirements))  # Remove duplicates
    
    def _generate_recommendation(
        self, 
        requirement_level: CoverLetterRequirement, 
        application_format: ApplicationFormat
    ) -> str:
        """Generate recommendation for cover letter inclusion"""
        
        if requirement_level == CoverLetterRequirement.REQUIRED:
            return "✅ Generate cover letter - Required by employer"
        elif requirement_level == CoverLetterRequirement.OPTIONAL:
            return "✅ Generate cover letter - Optional but recommended for competitive advantage"
        elif requirement_level == CoverLetterRequirement.PREFERRED:
            return "✅ Generate cover letter - Preferred by employer"
        elif requirement_level == CoverLetterRequirement.NOT_ACCEPTED:
            return "❌ Skip cover letter - Not accepted by employer"
        else:
            # Not mentioned - make recommendation based on application format
            if application_format == ApplicationFormat.EMAIL_APPLICATION:
                return "✅ Generate cover letter - Email applications typically benefit from cover letters"
            elif application_format == ApplicationFormat.ATS_SYSTEM:
                return "⚠️ Consider cover letter - ATS systems may have cover letter field"
            else:
                return "⚠️ Consider cover letter - Generally recommended unless explicitly not accepted"

def demo_cover_letter_detection():
    """Demo the cover letter detection functionality"""
    
    parser = JobDescriptionParser()
    
    # Test cases
    test_cases = [
        {
            "name": "Required Cover Letter",
            "description": """
            We are seeking a Senior Software Engineer to join our team. 
            To apply, please submit your resume and cover letter to careers@company.com.
            Cover letter is required and should explain your motivation for this role.
            """
        },
        {
            "name": "Optional Cover Letter", 
            "description": """
            Join our innovative startup as a Product Manager! 
            Submit your resume through our online application system.
            Cover letter is optional but encouraged to tell us why you're passionate about our mission.
            """
        },
        {
            "name": "No Cover Letter",
            "description": """
            Data Scientist position available. Apply through our ATS system.
            Please submit resume only. Do not include cover letter or additional documents.
            We will contact qualified candidates for next steps.
            """
        },
        {
            "name": "Implicit Acceptance",
            "description": """
            Marketing Manager role at growing company. 
            Apply on our careers page with your resume.
            Tell us why you're interested in our company and what draws you to this role.
            """
        }
    ]
    
    print("🔍 Job Description Parser - Cover Letter Detection Demo")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 50)
        
        analysis = parser.analyze_cover_letter_requirements(test_case['description'])
        
        print(f"📊 Requirement Level: {analysis.requirement_level.value}")
        print(f"🎯 Confidence Score: {analysis.confidence_score:.1%}")
        print(f"📝 Application Format: {analysis.application_format.value}")
        print(f"💡 Recommendation: {analysis.recommendation}")
        
        if analysis.supporting_text:
            print(f"📄 Supporting Evidence: {analysis.supporting_text[:2]}")
        
        if analysis.additional_requirements:
            print(f"📋 Additional Requirements: {analysis.additional_requirements}")
        
        print("-" * 50)
    
    print("\n✨ Cover Letter Detection Demo Complete!")
    print("\n🎯 Key Features Demonstrated:")
    print("   ✅ Required/Optional/Not Accepted detection")
    print("   ✅ Application format identification")
    print("   ✅ Confidence scoring")
    print("   ✅ Intelligent recommendations")
    print("   ✅ Supporting evidence extraction")

if __name__ == "__main__":
    demo_cover_letter_detection()
