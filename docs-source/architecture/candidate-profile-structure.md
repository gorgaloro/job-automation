# Candidate Profile Data Structure & Storage Architecture

## Overview

This document defines the structured data format for candidate profiles in the AI Job Search Platform. The structure separates content from presentation, enabling flexible frontend development, API integration, and data persistence.

## Core Principles

1. **Separation of Concerns** - Data structure independent of UI presentation
2. **API-First Design** - JSON-based format for easy API consumption
3. **Version Control** - Track profile evolution over time
4. **Modular Components** - Each section can be updated independently
5. **Export Flexibility** - Support multiple output formats (HTML, PDF, JSON)

---

## Data Structure Schema

### 1. Profile Metadata

```json
{
  "profile_metadata": {
    "profile_id": "allen_walker_001",
    "user_id": "user_12345",
    "profile_version": "1.2.0",
    "profile_status": "active",
    "created_at": "2025-07-25T15:00:00Z",
    "updated_at": "2025-07-25T15:47:00Z",
    "last_ai_coaching_session": "2025-07-20T10:30:00Z",
    "last_job_search": "2025-07-25T14:00:00Z",
    "profile_completeness": 0.92,
    "ai_confidence_score": 0.88
  }
}
```

### 2. Personal Information

```json
{
  "personal_info": {
    "full_name": "Allen Walker",
    "preferred_name": "Allen",
    "title": "Senior Program Manager & Operations Strategist",
    "location": {
      "current": "San Francisco, CA",
      "timezone": "America/Los_Angeles",
      "willing_to_relocate": false
    },
    "contact": {
      "email": "contact@example.com",
      "phone": "+1-555-0123",
      "linkedin": "linkedin.com/in/allenwalker",
      "website": "https://allenwalker.dev",
      "github": "github.com/allenwalker"
    },
    "availability": {
      "status": "actively_looking",
      "start_date": "2025-08-01",
      "notice_period": "2_weeks"
    }
  }
}
```

### 3. Professional Summary

```json
{
  "professional_summary": {
    "elevator_pitch": "Senior program leader and operations strategist with 15+ years transforming industries including healthcare, construction, property management, pharma, and community development.",
    "detailed_summary": "I drive change through systems thinking, infrastructure buildout, IT delivery, and hands-on execution across complex projects. Combines startup grit with enterprise discipline—leading $500M+ initiatives, streamlining RevOps delivery, and scaling high-trust systems that connect vision to execution.",
    "unique_value_proposition": "Combines deep healthcare domain knowledge with technology delivery expertise to drive large-scale transformational programs",
    "years_experience": 15,
    "experience_level": "senior",
    "management_experience": true,
    "team_sizes_managed": [5, 50],
    "budget_responsibility": 6000000000,
    "last_updated": "2025-07-25T15:47:00Z",
    "editable": true
  }
}
```

### 4. Skills & Expertise

```json
{
  "skills": {
    "core_skills": [
      {
        "skill": "Program Management",
        "proficiency": "expert",
        "years_experience": 15,
        "category": "business_strategy",
        "keywords": ["program", "management", "delivery", "execution"]
      },
      {
        "skill": "Revenue Operations",
        "proficiency": "expert",
        "years_experience": 8,
        "category": "business_strategy",
        "keywords": ["revenue", "operations", "revops", "sales"]
      }
    ],
    "technical_skills": [
      {
        "skill": "Salesforce",
        "proficiency": "advanced",
        "years_experience": 10,
        "category": "crm_systems",
        "certifications": ["Salesforce Admin", "Advanced Administrator"]
      },
      {
        "skill": "Epic Systems",
        "proficiency": "expert",
        "years_experience": 8,
        "category": "healthcare_systems",
        "certifications": ["Epic Resolute PB", "Epic HB"]
      }
    ],
    "soft_skills": [
      {
        "skill": "Leadership",
        "proficiency": "expert",
        "evidence": ["Led teams of 50+", "Managed $6B program"]
      },
      {
        "skill": "Cross-functional Collaboration",
        "proficiency": "expert",
        "evidence": ["Fortune 100 client delivery", "Multi-department coordination"]
      }
    ],
    "skill_categories": {
      "business_strategy": ["Program Management", "Revenue Operations", "GTM Strategy"],
      "customer_delivery": ["Customer Success", "CX Operations", "Implementation"],
      "technology_systems": ["Salesforce", "HubSpot", "Epic Systems", "SQL"],
      "industries": ["Healthcare", "SaaS", "AI/ML", "Real Estate", "Automotive"]
    }
  }
}
```

### 5. Work Experience & Achievements

```json
{
  "experience": {
    "career_highlights": [
      {
        "id": "epic_program_2023",
        "title": "$6B Epic Program Leadership",
        "organization": "Healthcare System Implementation",
        "timeframe": "2022-2024",
        "description": "Directed a $6B Epic program for 35,000+ users—drove timelines, delivered change, and met go-live with zero critical errors.",
        "impact_metrics": {
          "budget": 6000000000,
          "users_affected": 35000,
          "timeline": "24_months",
          "success_rate": "100%"
        },
        "skills_used": ["Program Management", "Change Management", "Epic Systems"],
        "category": "major_program"
      },
      {
        "id": "it_portfolio_2021",
        "title": "IT Portfolio Management",
        "organization": "Enterprise Technology Operations",
        "timeframe": "2020-2022",
        "description": "Managed an IT portfolio serving 100K+ users—led vendor management, contract execution, and SLA accountability across high-stakes production environments.",
        "impact_metrics": {
          "users_served": 100000,
          "uptime": "99.9%",
          "cost_savings": 2000000
        },
        "skills_used": ["Vendor Management", "SLA Management", "Operations"],
        "category": "operations_leadership"
      }
    ],
    "employment_history": [
      {
        "company": "Current Healthcare System",
        "position": "Senior Program Manager",
        "start_date": "2022-01-01",
        "end_date": null,
        "current": true,
        "location": "San Francisco, CA",
        "employment_type": "full_time",
        "key_responsibilities": [
          "Lead Epic implementation programs",
          "Manage cross-functional delivery teams",
          "Drive change management initiatives"
        ]
      }
    ],
    "industry_experience": [
      {
        "industry": "Healthcare",
        "years": 8,
        "roles": ["Program Manager", "Implementation Manager"],
        "key_systems": ["Epic", "Cerner", "MEDITECH"]
      },
      {
        "industry": "Technology/SaaS",
        "years": 7,
        "roles": ["Revenue Operations", "Customer Success"],
        "key_systems": ["Salesforce", "HubSpot", "Gainsight"]
      }
    ]
  }
}
```

### 6. Job Search Preferences

```json
{
  "job_preferences": {
    "target_roles": {
      "primary_titles": [
        "Senior Program Manager",
        "Revenue Operations Manager",
        "Customer Experience Manager",
        "Technical Project Manager",
        "Healthcare IT Manager"
      ],
      "alternative_titles": [
        "Program Director",
        "Operations Director",
        "Delivery Manager",
        "Customer Success Manager"
      ],
      "excluded_titles": [
        "Junior",
        "Associate",
        "Intern",
        "Entry Level"
      ],
      "role_types": ["individual_contributor", "manager", "director"],
      "management_preference": "people_and_program_management"
    },
    "compensation": {
      "salary_range": {
        "min": 150000,
        "max": 250000,
        "currency": "USD",
        "range_category": "150k_200k"
      },
      "equity_preference": "preferred",
      "benefits_priorities": ["health_insurance", "retirement_401k", "pto", "professional_development"],
      "compensation_negotiable": true
    },
    "location_work_style": {
      "preferred_locations": [
        "San Francisco, CA",
        "Bay Area, CA",
        "Remote",
        "California"
      ],
      "remote_preference": "hybrid",
      "willing_to_relocate": false,
      "travel_tolerance": "25%",
      "timezone_preference": "PST"
    },
    "company_preferences": {
      "company_sizes": ["medium", "large", "enterprise"],
      "company_stages": ["growth", "public"],
      "company_types": ["b2b_saas", "healthcare", "fintech"],
      "culture_priorities": ["work_life_balance", "innovation", "diversity", "growth_opportunities"]
    },
    "industry_targeting": {
      "preferred_industries": [
        "Healthcare",
        "Technology",
        "SaaS",
        "Fintech",
        "Real Estate",
        "Automotive",
        "AI/ML"
      ],
      "excluded_industries": [
        "Gambling",
        "Tobacco",
        "Weapons"
      ],
      "industry_experience_weight": 0.8
    },
    "search_keywords": {
      "required_keywords": [
        "program management",
        "revenue operations",
        "customer experience",
        "epic",
        "salesforce",
        "healthcare",
        "implementation"
      ],
      "preferred_keywords": [
        "cross-functional",
        "strategy",
        "change management",
        "delivery",
        "operations",
        "technology"
      ],
      "excluded_keywords": [
        "junior",
        "entry",
        "intern",
        "associate"
      ],
      "keyword_weights": {
        "program management": 1.5,
        "revenue operations": 1.4,
        "epic": 1.3,
        "salesforce": 1.2,
        "healthcare": 1.1
      }
    }
  }
}
```

### 7. AI Career Coaching Data

```json
{
  "ai_coaching": {
    "latest_session": {
      "session_id": "coaching_session_20250720_001",
      "date": "2025-07-20T10:30:00Z",
      "duration_minutes": 45,
      "session_type": "career_strategy",
      "topics_covered": ["career_goals", "skill_development", "market_positioning"],
      "ai_confidence": 0.89
    },
    "career_insights": {
      "strengths": [
        "Large-scale program management expertise",
        "Healthcare domain knowledge",
        "Cross-functional leadership",
        "Technology implementation experience"
      ],
      "development_areas": [
        "AI/ML knowledge expansion",
        "Product management skills",
        "Data analytics capabilities"
      ],
      "career_trajectory": "senior_leadership",
      "market_positioning": "Healthcare technology transformation leader"
    },
    "recommendations": {
      "skill_development": [
        "Complete AI/ML certification",
        "Gain product management experience",
        "Expand data analytics skills"
      ],
      "networking_strategy": [
        "Attend healthcare IT conferences",
        "Join RevOps communities",
        "Connect with Epic consultants"
      ],
      "job_search_strategy": [
        "Target healthcare technology companies",
        "Focus on transformation roles",
        "Highlight Epic expertise"
      ]
    },
    "personality_assessment": {
      "work_style": ["collaborative", "strategic", "hands_on"],
      "leadership_style": "servant_leader",
      "communication_style": "direct_collaborative",
      "decision_making": "data_driven_consensus"
    }
  }
}
```

### 8. Activity Tracking

```json
{
  "activity_tracking": {
    "job_applications": {
      "applied": [
        {
          "job_id": "stripe_pm_001",
          "company": "Stripe",
          "position": "Senior Program Manager",
          "applied_date": "2025-07-20T09:00:00Z",
          "status": "pending",
          "source": "greenhouse"
        }
      ],
      "saved": ["uber_ops_002", "salesforce_revops_003"],
      "rejected": ["junior_pm_001"],
      "interviews": [
        {
          "job_id": "stripe_pm_001",
          "stage": "phone_screen",
          "scheduled_date": "2025-07-28T14:00:00Z",
          "interviewer": "Sarah Johnson",
          "notes": "Technical program management focus"
        }
      ]
    },
    "search_history": {
      "last_search_date": "2025-07-25T14:00:00Z",
      "searches_this_week": 5,
      "total_jobs_viewed": 45,
      "average_match_score": 0.87
    },
    "profile_updates": [
      {
        "date": "2025-07-25T15:47:00Z",
        "section": "professional_summary",
        "change_type": "edit",
        "user_initiated": true
      },
      {
        "date": "2025-07-20T10:30:00Z",
        "section": "ai_coaching",
        "change_type": "add_session",
        "user_initiated": false
      }
    ]
  }
}
```

---

## Storage Architecture

### Database Schema (PostgreSQL/Supabase)

```sql
-- Main profile table
CREATE TABLE candidate_profiles (
    profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    profile_version VARCHAR(10) NOT NULL DEFAULT '1.0.0',
    profile_status VARCHAR(20) NOT NULL DEFAULT 'active',
    profile_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Profile history for version tracking
CREATE TABLE profile_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id),
    version VARCHAR(10) NOT NULL,
    changes JSONB NOT NULL,
    change_reason VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI coaching sessions
CREATE TABLE ai_coaching_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id),
    session_data JSONB NOT NULL,
    session_type VARCHAR(50) NOT NULL,
    duration_minutes INTEGER,
    ai_confidence DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Job applications tracking
CREATE TABLE job_applications (
    application_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id),
    job_id VARCHAR(100) NOT NULL,
    company VARCHAR(100) NOT NULL,
    position VARCHAR(200) NOT NULL,
    status VARCHAR(50) NOT NULL,
    source VARCHAR(50) NOT NULL,
    applied_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    application_data JSONB
);
```

### API Endpoints

```yaml
# Profile Management
GET    /api/profiles/{profile_id}           # Get complete profile
PUT    /api/profiles/{profile_id}           # Update profile
POST   /api/profiles                        # Create new profile
DELETE /api/profiles/{profile_id}           # Delete profile

# Profile Sections
GET    /api/profiles/{profile_id}/summary   # Get professional summary
PUT    /api/profiles/{profile_id}/summary   # Update summary
GET    /api/profiles/{profile_id}/skills    # Get skills data
PUT    /api/profiles/{profile_id}/skills    # Update skills
GET    /api/profiles/{profile_id}/preferences # Get job preferences
PUT    /api/profiles/{profile_id}/preferences # Update preferences

# AI Coaching
POST   /api/profiles/{profile_id}/coaching  # Start coaching session
GET    /api/profiles/{profile_id}/coaching  # Get coaching history
PUT    /api/profiles/{profile_id}/coaching/{session_id} # Update session

# Job Search Integration
POST   /api/profiles/{profile_id}/search    # Run job search
GET    /api/profiles/{profile_id}/matches   # Get job matches
POST   /api/profiles/{profile_id}/apply     # Apply to job

# Export Functions
GET    /api/profiles/{profile_id}/export/json    # Export as JSON
GET    /api/profiles/{profile_id}/export/html    # Export as HTML
GET    /api/profiles/{profile_id}/export/pdf     # Export as PDF
GET    /api/profiles/{profile_id}/export/resume  # Export resume format
```

### File Storage Structure

```
/candidate_profiles/
├── {profile_id}/
│   ├── profile.json                 # Main profile data
│   ├── versions/
│   │   ├── v1.0.0.json             # Version history
│   │   ├── v1.1.0.json
│   │   └── v1.2.0.json
│   ├── coaching_sessions/
│   │   ├── session_001.json        # AI coaching data
│   │   └── session_002.json
│   ├── exports/
│   │   ├── resume.pdf              # Generated exports
│   │   ├── about_me.html
│   │   └── profile_summary.json
│   └── attachments/
│       ├── resume.pdf              # Uploaded files
│       └── portfolio_items/
```

---

## Frontend Integration

### React Component Structure

```jsx
// Main profile dashboard
<CandidateProfileDashboard profileId={profileId}>
  <ProfileTabs>
    <WhoIAmTab>
      <ProfessionalSummary editable={true} />
      <SkillsGrid categories={skillCategories} />
      <ExperienceTimeline highlights={careerHighlights} />
      <ExportSection />
    </WhoIAmTab>
    
    <WhatImLookingForTab>
      <JobPreferencesForm onSave={updatePreferences} />
      <CompensationSettings />
      <LocationPreferences />
      <IndustrySelector />
    </WhatImLookingForTab>
  </ProfileTabs>
  
  <ProfileActions>
    <AICoachButton onClick={launchCoaching} />
    <JobSearchButton onClick={runSearch} />
    <ExportButton onClick={exportProfile} />
  </ProfileActions>
</CandidateProfileDashboard>
```

### State Management (Redux/Context)

```javascript
// Profile state structure
const profileState = {
  profile: {
    metadata: { ... },
    personalInfo: { ... },
    summary: { ... },
    skills: { ... },
    experience: { ... },
    preferences: { ... },
    coaching: { ... },
    activity: { ... }
  },
  ui: {
    activeTab: 'who-i-am',
    editingSection: null,
    loading: false,
    lastSaved: '2025-07-25T15:47:00Z'
  },
  actions: {
    updateSummary,
    updatePreferences,
    launchCoaching,
    runJobSearch,
    exportProfile
  }
};
```

---

## Implementation Priorities

### Phase 1: Core Data Structure
1. ✅ Define JSON schema
2. ✅ Create database tables
3. ✅ Build API endpoints
4. ⏳ Implement data validation

### Phase 2: Frontend Integration
1. ⏳ Build React components
2. ⏳ Implement state management
3. ⏳ Add real-time updates
4. ⏳ Create export functions

### Phase 3: Advanced Features
1. ⏳ Version control system
2. ⏳ AI coaching integration
3. ⏳ Job search automation
4. ⏳ Analytics dashboard

---

## Benefits of This Structure

1. **Flexibility** - Easy to add new fields or sections
2. **Scalability** - Supports multiple users and profiles
3. **API-First** - Ready for mobile apps and integrations
4. **Version Control** - Track profile evolution over time
5. **Export Ready** - Multiple output formats supported
6. **Search Optimized** - Structured data for job matching algorithms

This architecture provides a solid foundation for your candidate profile system while maintaining flexibility for future enhancements and integrations.
