# Dynamic Resume Optimizer - Database Schema Documentation

## Overview
This document provides comprehensive documentation for the Supabase PostgreSQL database schema used by the Dynamic Resume Optimizer. The schema is designed to support granular resume optimization, multi-dimensional scoring, and intelligent content management.

## Database Architecture Principles

### **1. User-Centric Design**
- All tables include `user_id` for multi-user support
- Row Level Security (RLS) policies ensure data isolation
- Comprehensive user preference tracking

### **2. Granular Control**
- Individual bullet points, achievements, and content elements are separately tracked
- Checkbox selections stored per resume/job combination
- Fine-grained scoring and relevance tracking

### **3. Intelligent Optimization**
- Multi-dimensional scoring algorithms for each content type
- Version tracking for iterative improvement
- Performance analytics and usage tracking

### **4. Production Scalability**
- Proper indexing for performance
- Normalized data structure
- Comprehensive foreign key relationships

---

## Core Resume Sections

### 1. Personal Information
```sql
-- Core user contact and profile information
CREATE TABLE personal_info (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    location TEXT,
    linkedin_url TEXT,
    github_url TEXT,
    portfolio_url TEXT,
    twitter_url TEXT,
    facebook_url TEXT,
    other_profiles JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User preferences for social media display
CREATE TABLE resume_personal_info_selections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    show_email BOOLEAN DEFAULT true,
    show_phone BOOLEAN DEFAULT true,
    show_location BOOLEAN DEFAULT true,
    show_linkedin BOOLEAN DEFAULT true,
    show_github BOOLEAN DEFAULT true,
    show_portfolio BOOLEAN DEFAULT true,
    show_twitter BOOLEAN DEFAULT false,
    show_facebook BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. Executive Summaries (Versioned)
```sql
-- Versioned executive summaries with intelligent reuse
CREATE TABLE executive_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    parent_summary_id UUID REFERENCES executive_summaries(id),
    content TEXT NOT NULL CHECK (char_length(content) <= 700),
    target_role TEXT,
    target_industry TEXT,
    target_company_size TEXT,
    keywords TEXT[],
    tone_style TEXT,
    quality_score DECIMAL(3,2),
    ai_assessment TEXT,
    keyword_density DECIMAL(3,2),
    readability_score DECIMAL(3,2),
    impact_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- Multi-dimensional scoring for executive summaries
CREATE TABLE job_summary_relevance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    summary_id UUID REFERENCES executive_summaries(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    keyword_alignment_score DECIMAL(3,2),
    skill_emphasis_score DECIMAL(3,2),
    industry_alignment_score DECIMAL(3,2),
    role_alignment_score DECIMAL(3,2),
    tone_appropriateness_score DECIMAL(3,2),
    achievement_relevance_score DECIMAL(3,2),
    composite_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance tracking for summaries
CREATE TABLE summary_usage_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    summary_id UUID REFERENCES executive_summaries(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    application_date TIMESTAMP WITH TIME ZONE,
    response_received BOOLEAN DEFAULT false,
    response_time_days INTEGER,
    interview_secured BOOLEAN DEFAULT false,
    user_feedback TEXT,
    success_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3. Strategic Impact (Career Highlights)
```sql
-- Career highlights with relevance scoring
CREATE TABLE strategic_impact (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT,
    impact_metrics TEXT,
    quantified_results TEXT,
    skills_demonstrated TEXT[],
    industries_relevant TEXT[],
    roles_relevant TEXT[],
    display_order INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Job-specific relevance scoring for strategic impact
CREATE TABLE job_strategic_impact_relevance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    strategic_impact_id UUID REFERENCES strategic_impact(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    relevance_score DECIMAL(3,2),
    impact_alignment_score DECIMAL(3,2),
    skill_match_score DECIMAL(3,2),
    industry_relevance_score DECIMAL(3,2),
    role_relevance_score DECIMAL(3,2),
    composite_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. Professional Experience
```sql
-- Core employment history
CREATE TABLE employment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_title TEXT NOT NULL,
    company_name TEXT NOT NULL,
    location TEXT,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT false,
    company_description TEXT,
    role_summary TEXT,
    section_type TEXT DEFAULT 'professional_experience',
    display_order INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Individual bullet points with granular scoring
CREATE TABLE employment_bullets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    employment_id UUID REFERENCES employment_history(id) ON DELETE CASCADE,
    bullet_text TEXT NOT NULL,
    category TEXT,
    skills_used TEXT[],
    quantified_impact TEXT,
    keywords TEXT[],
    display_order INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Job-specific bullet scoring
CREATE TABLE job_bullet_relevance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    bullet_id UUID REFERENCES employment_bullets(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    relevance_score DECIMAL(3,2),
    keyword_match_score DECIMAL(3,2),
    skill_alignment_score DECIMAL(3,2),
    impact_relevance_score DECIMAL(3,2),
    composite_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 5. Skills & Expertise
```sql
-- Comprehensive skills tracking
CREATE TABLE skills_expertise (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    skill_name TEXT NOT NULL,
    category TEXT,
    proficiency_level TEXT,
    years_experience INTEGER,
    last_used_date DATE,
    is_core_skill BOOLEAN DEFAULT false,
    endorsements_count INTEGER DEFAULT 0,
    certifications_related TEXT[],
    projects_used TEXT[],
    display_order INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Job-specific skill relevance
CREATE TABLE job_skill_relevance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills_expertise(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    relevance_score DECIMAL(3,2),
    requirement_level TEXT,
    skill_gap_analysis TEXT,
    priority_ranking INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 6. Education
```sql
-- Academic background with smart display
CREATE TABLE education (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    institution_name TEXT NOT NULL,
    degree_type TEXT,
    degree_name TEXT,
    field_of_study TEXT,
    start_date DATE,
    end_date DATE,
    gpa DECIMAL(3,2),
    gpa_scale DECIMAL(3,2) DEFAULT 4.0,
    honors TEXT[],
    class_rank TEXT,
    thesis_title TEXT,
    thesis_description TEXT,
    relevant_coursework TEXT[],
    research_projects TEXT[],
    publications TEXT[],
    academic_achievements TEXT[],
    skills_acquired TEXT[],
    programming_languages TEXT[],
    methodologies_learned TEXT[],
    industry_relevance TEXT[],
    display_order INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Individual academic achievements
CREATE TABLE education_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    education_id UUID REFERENCES education(id) ON DELETE CASCADE,
    achievement_type TEXT,
    achievement_name TEXT NOT NULL,
    description TEXT,
    date_achieved DATE,
    professional_relevance_score DECIMAL(3,2),
    display_order INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Resume-specific education display configuration
CREATE TABLE resume_education_selections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    education_id UUID REFERENCES education(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    show_gpa BOOLEAN DEFAULT false,
    show_honors BOOLEAN DEFAULT true,
    show_coursework BOOLEAN DEFAULT false,
    show_thesis BOOLEAN DEFAULT false,
    show_achievements BOOLEAN DEFAULT true,
    display_format TEXT DEFAULT 'standard',
    max_coursework_items INTEGER DEFAULT 3,
    max_activities_items INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Multi-dimensional education relevance scoring
CREATE TABLE job_education_relevance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    education_id UUID REFERENCES education(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    degree_relevance_score DECIMAL(3,2),
    field_alignment_score DECIMAL(3,2),
    institution_prestige_score DECIMAL(3,2),
    skills_alignment_score DECIMAL(3,2),
    coursework_relevance_score DECIMAL(3,2),
    composite_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 7. Certifications
```sql
-- Professional certifications with expiration tracking
CREATE TABLE certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    certification_name TEXT NOT NULL,
    certification_code TEXT,
    issuing_organization TEXT NOT NULL,
    certification_type TEXT,
    certification_level TEXT,
    issue_date DATE,
    expiration_date DATE,
    renewal_date DATE,
    renewal_requirements TEXT,
    continuing_education_credits INTEGER,
    credential_id TEXT,
    verification_url TEXT,
    digital_badge_url TEXT,
    certificate_file_url TEXT,
    skills_validated TEXT[],
    competency_levels TEXT[],
    industry_relevance TEXT[],
    exam_score INTEGER,
    passing_score INTEGER,
    specializations TEXT[],
    status TEXT DEFAULT 'active',
    display_order INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Individual certification achievements
CREATE TABLE certification_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    certification_id UUID REFERENCES certifications(id) ON DELETE CASCADE,
    achievement_type TEXT,
    achievement_name TEXT NOT NULL,
    description TEXT,
    date_achieved DATE,
    recognition_level TEXT,
    display_order INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Resume-specific certification display configuration
CREATE TABLE resume_certification_selections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    certification_id UUID REFERENCES certifications(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    show_expiration_date BOOLEAN DEFAULT true,
    show_credential_id BOOLEAN DEFAULT false,
    show_exam_score BOOLEAN DEFAULT false,
    show_specializations BOOLEAN DEFAULT true,
    display_format TEXT DEFAULT 'standard',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Multi-dimensional certification relevance scoring
CREATE TABLE job_certification_relevance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    certification_id UUID REFERENCES certifications(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    skill_alignment_score DECIMAL(3,2),
    industry_relevance_score DECIMAL(3,2),
    role_relevance_score DECIMAL(3,2),
    vendor_alignment_score DECIMAL(3,2),
    compliance_value_score DECIMAL(3,2),
    composite_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 8. Community Leadership & Networks
```sql
-- Professional-style community leadership tracking
CREATE TABLE community_leadership (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    organization TEXT NOT NULL,
    location TEXT,
    start_date DATE,
    end_date DATE,
    is_ongoing BOOLEAN DEFAULT false,
    narrative TEXT NOT NULL,
    leadership_level TEXT,
    team_size INTEGER,
    budget_responsibility DECIMAL(12,2),
    organization_type TEXT,
    geographic_reach TEXT,
    display_order INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Individual community leadership achievements
CREATE TABLE community_leadership_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    community_leadership_id UUID REFERENCES community_leadership(id) ON DELETE CASCADE,
    achievement_description TEXT NOT NULL,
    impact_metrics TEXT,
    quantified_results TEXT,
    skills_demonstrated TEXT[],
    network_value TEXT,
    display_order INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Resume-specific community leadership selections
CREATE TABLE resume_community_leadership_selections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    community_leadership_id UUID REFERENCES community_leadership(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    include_in_resume BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Multi-dimensional community leadership relevance scoring
CREATE TABLE job_community_leadership_relevance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    community_leadership_id UUID REFERENCES community_leadership(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    leadership_skills_score DECIMAL(3,2),
    industry_relevance_score DECIMAL(3,2),
    network_value_score DECIMAL(3,2),
    cultural_fit_score DECIMAL(3,2),
    professional_development_score DECIMAL(3,2),
    composite_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## Optimization & Analytics Tables

### Job Analysis & Scoring
```sql
-- Job description analysis results
CREATE TABLE job_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL UNIQUE,
    job_title TEXT,
    company_name TEXT,
    location TEXT,
    salary_range TEXT,
    job_description TEXT,
    company_summary TEXT,
    position_summary TEXT,
    job_summary TEXT,
    matched_keywords TEXT[],
    missing_keywords TEXT[],
    overall_match_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Section-level scoring per job
CREATE TABLE section_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    section_name TEXT NOT NULL,
    score_percentage DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User checkbox selections per resume/job
CREATE TABLE resume_selections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    section_name TEXT NOT NULL,
    item_id UUID NOT NULL,
    item_type TEXT NOT NULL,
    is_selected BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### AI Suggestions & Performance
```sql
-- AI-generated suggestions with performance tracking
CREATE TABLE ai_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_id TEXT NOT NULL,
    section_name TEXT NOT NULL,
    parent_item_id UUID,
    suggestion_text TEXT NOT NULL,
    suggestion_type TEXT,
    relevance_score DECIMAL(3,2),
    usage_count INTEGER DEFAULT 0,
    acceptance_rate DECIMAL(3,2),
    performance_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE
);
```

---

## Security & Access Control

### Row Level Security (RLS) Policies
All tables include comprehensive RLS policies to ensure users can only access their own data:

```sql
-- Example RLS policy (applied to all tables)
ALTER TABLE personal_info ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only access their own personal info"
ON personal_info FOR ALL
USING (auth.uid() = user_id);

-- Similar policies applied to all user-specific tables
```

### Indexes for Performance
```sql
-- Core performance indexes
CREATE INDEX idx_employment_history_user_id ON employment_history(user_id);
CREATE INDEX idx_employment_bullets_employment_id ON employment_bullets(employment_id);
CREATE INDEX idx_job_analyses_job_id ON job_analyses(job_id);
CREATE INDEX idx_section_scores_job_id ON section_scores(job_id);
CREATE INDEX idx_resume_selections_job_id ON resume_selections(job_id);

-- Additional indexes for common queries
CREATE INDEX idx_executive_summaries_user_active ON executive_summaries(user_id, is_active);
CREATE INDEX idx_certifications_status ON certifications(user_id, status);
CREATE INDEX idx_skills_core ON skills_expertise(user_id, is_core_skill);
```

---

## Database Functions & Procedures

### Smart Recommendation Functions
```sql
-- Get best matching executive summary for a job
CREATE OR REPLACE FUNCTION get_best_matching_summary(p_user_id UUID, p_job_id TEXT)
RETURNS UUID AS $$
BEGIN
    RETURN (
        SELECT es.id
        FROM executive_summaries es
        JOIN job_summary_relevance jsr ON es.id = jsr.summary_id
        WHERE es.user_id = p_user_id 
        AND jsr.job_id = p_job_id
        AND es.is_active = true
        ORDER BY jsr.composite_score DESC
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql;

-- Calculate overall education section value for resume
CREATE OR REPLACE FUNCTION calculate_education_resume_value(p_user_id UUID, p_job_id TEXT)
RETURNS DECIMAL(3,2) AS $$
BEGIN
    RETURN (
        SELECT AVG(jer.composite_score)
        FROM education e
        JOIN job_education_relevance jer ON e.id = jer.education_id
        WHERE e.user_id = p_user_id 
        AND jer.job_id = p_job_id
    );
END;
$$ LANGUAGE plpgsql;
```

---

## Migration & Deployment

### Database Setup Script
```sql
-- Complete database setup (supabase_resume_tables.sql)
-- 1. Create all tables with proper relationships
-- 2. Enable RLS on all tables
-- 3. Create user-specific policies
-- 4. Add performance indexes
-- 5. Create helper functions
-- 6. Insert sample data for testing
```

### Data Migration Strategy
1. **Export existing data** from local files/servers
2. **Transform data** to match new schema structure
3. **Import data** into Supabase tables with proper user associations
4. **Validate data integrity** and relationships
5. **Update frontend** to use Supabase REST API endpoints
6. **Test end-to-end functionality** with production database

---

## API Integration

### Supabase REST API Endpoints
The frontend will interact with Supabase using standard REST API calls:

```javascript
// Example API calls
const { data: personalInfo } = await supabase
  .from('personal_info')
  .select('*')
  .eq('user_id', user.id)
  .single();

const { data: employmentHistory } = await supabase
  .from('employment_history')
  .select(`
    *,
    employment_bullets (*)
  `)
  .eq('user_id', user.id)
  .order('start_date', { ascending: false });
```

### Real-time Subscriptions
Supabase real-time subscriptions will enable live updates:

```javascript
// Real-time updates for resume changes
const subscription = supabase
  .channel('resume_changes')
  .on('postgres_changes', 
    { event: '*', schema: 'public', table: 'employment_bullets' },
    (payload) => updateUI(payload)
  )
  .subscribe();
```

---

## Monitoring & Analytics

### Performance Tracking
- Query performance monitoring
- User interaction analytics
- AI suggestion effectiveness metrics
- System reliability monitoring

### Business Intelligence
- Resume optimization success rates
- Most effective content patterns
- User behavior analysis
- Feature usage statistics

---

This comprehensive database schema provides the foundation for a production-ready Dynamic Resume Optimizer with enterprise-grade scalability, security, and performance.
