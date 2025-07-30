-- =====================================================
-- SUPABASE CANDIDATE PROFILE SCHEMA
-- Dynamic Resume Generation with Job-Specific Scoring
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- CORE PROFILE TABLE
-- =====================================================

CREATE TABLE candidate_profiles (
    profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    profile_version VARCHAR(10) NOT NULL DEFAULT '1.0.0',
    profile_status VARCHAR(20) NOT NULL DEFAULT 'active',
    
    -- Basic Information
    full_name VARCHAR(100) NOT NULL,
    preferred_name VARCHAR(50),
    current_title VARCHAR(200),
    email VARCHAR(255),
    phone VARCHAR(20),
    linkedin_url VARCHAR(255),
    website_url VARCHAR(255),
    github_url VARCHAR(255),
    
    -- Location & Availability
    current_location VARCHAR(100),
    timezone VARCHAR(50),
    willing_to_relocate BOOLEAN DEFAULT false,
    availability_status VARCHAR(20) DEFAULT 'actively_looking',
    start_date DATE,
    notice_period VARCHAR(20),
    
    -- Professional Summary
    elevator_pitch TEXT,
    detailed_summary TEXT,
    unique_value_proposition TEXT,
    years_experience INTEGER,
    experience_level VARCHAR(20),
    management_experience BOOLEAN DEFAULT false,
    budget_responsibility BIGINT,
    
    -- Metadata
    profile_completeness DECIMAL(3,2) DEFAULT 0.0,
    ai_confidence_score DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- SKILLS & EXPERTISE TABLES
-- =====================================================

CREATE TABLE skill_categories (
    category_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_name VARCHAR(100) NOT NULL UNIQUE,
    category_description TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE candidate_skills (
    skill_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    category_id UUID REFERENCES skill_categories(category_id),
    
    -- Skill Details
    skill_name VARCHAR(100) NOT NULL,
    proficiency_level VARCHAR(20) NOT NULL, -- beginner, intermediate, advanced, expert
    years_experience INTEGER,
    
    -- Skill Context
    skill_type VARCHAR(20) NOT NULL, -- core, technical, soft, emerging
    is_featured BOOLEAN DEFAULT false,
    is_recent BOOLEAN DEFAULT false, -- for highlighting new skills
    
    -- Evidence & Validation
    certifications TEXT[], -- array of certification names
    recent_projects TEXT[], -- array of project names
    frameworks TEXT[], -- related frameworks/tools
    keywords TEXT[] NOT NULL, -- searchable keywords for matching
    
    -- Scoring Metadata
    base_weight DECIMAL(3,2) DEFAULT 1.0, -- importance weight for this skill
    last_used_date DATE,
    skill_evidence TEXT, -- specific evidence/examples
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- CAREER HIGHLIGHTS & ACHIEVEMENTS
-- =====================================================

CREATE TABLE career_highlights (
    highlight_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    
    -- Highlight Details
    title VARCHAR(200) NOT NULL,
    organization VARCHAR(200),
    timeframe VARCHAR(100),
    description TEXT NOT NULL,
    
    -- Impact Metrics (stored as JSONB for flexibility)
    impact_metrics JSONB, -- e.g., {"budget": 6000000000, "users_affected": 35000, "timeline": "24_months"}
    
    -- Categorization
    highlight_category VARCHAR(50) NOT NULL, -- major_program, technical_innovation, operations_leadership, etc.
    complexity_level VARCHAR(20), -- junior, mid, senior, executive, enterprise
    leadership_role VARCHAR(50), -- individual_contributor, team_lead, technical_lead, program_manager, etc.
    
    -- Skills & Technologies
    skills_demonstrated TEXT[] NOT NULL, -- skills showcased in this highlight
    technologies_used TEXT[], -- specific technologies/tools
    business_value TEXT, -- business impact description
    
    -- Scoring & Matching
    keywords TEXT[] NOT NULL, -- keywords for job matching
    industries TEXT[], -- relevant industries
    role_types TEXT[], -- relevant role types
    base_weight DECIMAL(3,2) DEFAULT 1.0, -- importance weight
    
    -- Status
    is_featured BOOLEAN DEFAULT false,
    is_recent BOOLEAN DEFAULT false,
    status VARCHAR(20) DEFAULT 'active',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- EMPLOYMENT HISTORY
-- =====================================================

CREATE TABLE employment_history (
    employment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    
    -- Job Details
    company VARCHAR(200) NOT NULL,
    position VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT false,
    location VARCHAR(100),
    employment_type VARCHAR(20), -- full_time, part_time, contract, consultant
    
    -- Responsibilities & Achievements
    key_responsibilities TEXT[],
    key_achievements TEXT[],
    technologies_used TEXT[],
    team_size_managed INTEGER,
    budget_managed BIGINT,
    
    -- Matching Keywords
    keywords TEXT[],
    industries TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- JOB PREFERENCES & TARGETING
-- =====================================================

CREATE TABLE job_preferences (
    preference_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    
    -- Target Roles
    primary_job_titles TEXT[] NOT NULL,
    alternative_job_titles TEXT[],
    excluded_job_titles TEXT[],
    role_types TEXT[], -- individual_contributor, manager, director, etc.
    management_preference VARCHAR(50),
    
    -- Compensation
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(3) DEFAULT 'USD',
    equity_preference VARCHAR(20), -- not_important, preferred, strongly_preferred, required
    benefits_priorities TEXT[],
    
    -- Location & Work Style
    preferred_locations TEXT[],
    remote_preference VARCHAR(20), -- on_site, hybrid, remote, flexible
    willing_to_relocate BOOLEAN DEFAULT false,
    travel_tolerance VARCHAR(10), -- 0%, 25%, 50%, 75%, 100%
    timezone_preference VARCHAR(50),
    
    -- Company Preferences
    company_sizes TEXT[], -- startup, small, medium, large, enterprise
    company_stages TEXT[], -- seed, early, growth, public
    company_types TEXT[], -- b2b_saas, healthcare, fintech, etc.
    culture_priorities TEXT[],
    
    -- Industry Targeting
    preferred_industries TEXT[] NOT NULL,
    excluded_industries TEXT[],
    industry_experience_weight DECIMAL(3,2) DEFAULT 0.8,
    
    -- Search Keywords
    required_keywords TEXT[] NOT NULL,
    preferred_keywords TEXT[],
    excluded_keywords TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- JOB MATCHING & SCORING TABLES
-- =====================================================

CREATE TABLE job_postings (
    job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Job Details
    external_job_id VARCHAR(200), -- ID from job board
    job_board_source VARCHAR(50) NOT NULL, -- indeed, greenhouse, lever, etc.
    company VARCHAR(200) NOT NULL,
    position_title VARCHAR(200) NOT NULL,
    job_description TEXT NOT NULL,
    
    -- Job Requirements (extracted/parsed)
    required_skills TEXT[],
    preferred_skills TEXT[],
    experience_level VARCHAR(20),
    location VARCHAR(100),
    salary_range_min INTEGER,
    salary_range_max INTEGER,
    remote_option BOOLEAN,
    
    -- Metadata
    job_url VARCHAR(500),
    posted_date DATE,
    application_deadline DATE,
    job_status VARCHAR(20) DEFAULT 'active',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE job_skill_matches (
    match_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES candidate_skills(skill_id) ON DELETE CASCADE,
    
    -- Matching Details
    match_type VARCHAR(20) NOT NULL, -- exact, partial, related, inferred
    match_score DECIMAL(4,3) NOT NULL, -- 0.000 to 1.000
    match_confidence DECIMAL(4,3) NOT NULL,
    
    -- Context
    job_requirement_text TEXT, -- the specific requirement that matched
    skill_evidence TEXT, -- evidence from candidate's profile
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE job_highlight_matches (
    match_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    highlight_id UUID NOT NULL REFERENCES career_highlights(highlight_id) ON DELETE CASCADE,
    
    -- Matching Details
    relevance_score DECIMAL(4,3) NOT NULL, -- 0.000 to 1.000
    match_reasons TEXT[], -- array of reasons why this highlight is relevant
    matched_keywords TEXT[], -- specific keywords that matched
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- DYNAMIC RESUME GENERATION
-- =====================================================

CREATE TABLE generated_resumes (
    resume_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    job_id UUID REFERENCES job_postings(job_id) ON DELETE SET NULL,
    
    -- Resume Configuration
    resume_type VARCHAR(20) NOT NULL, -- job_specific, general, portfolio
    target_role VARCHAR(200),
    target_company VARCHAR(200),
    
    -- Selected Content (references to included items)
    selected_skills UUID[] NOT NULL, -- array of skill_ids
    selected_highlights UUID[] NOT NULL, -- array of highlight_ids
    selected_employment UUID[], -- array of employment_ids
    
    -- Resume Metadata
    overall_match_score DECIMAL(4,3),
    skills_match_score DECIMAL(4,3),
    experience_match_score DECIMAL(4,3),
    
    -- Generated Content
    tailored_summary TEXT,
    resume_html TEXT,
    resume_pdf_url VARCHAR(500),
    
    -- Status
    generation_status VARCHAR(20) DEFAULT 'draft', -- draft, generated, sent, archived
    generated_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- AI COACHING & INSIGHTS
-- =====================================================

CREATE TABLE ai_coaching_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    
    -- Session Details
    session_type VARCHAR(50) NOT NULL, -- career_strategy, skill_development, interview_prep, etc.
    duration_minutes INTEGER,
    topics_covered TEXT[],
    ai_confidence DECIMAL(3,2),
    
    -- Insights & Recommendations
    strengths_identified TEXT[],
    development_areas TEXT[],
    career_recommendations TEXT[],
    skill_recommendations TEXT[],
    networking_recommendations TEXT[],
    job_search_recommendations TEXT[],
    
    -- Market Analysis
    market_demand_assessment TEXT,
    salary_impact_analysis TEXT,
    competitive_advantage TEXT,
    target_companies TEXT[],
    
    -- Session Data
    session_data JSONB, -- full session context and responses
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- ACTIVITY TRACKING
-- =====================================================

CREATE TABLE job_applications (
    application_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    job_id UUID REFERENCES job_postings(job_id) ON DELETE SET NULL,
    resume_id UUID REFERENCES generated_resumes(resume_id) ON DELETE SET NULL,
    
    -- Application Details
    external_application_id VARCHAR(200),
    company VARCHAR(200) NOT NULL,
    position VARCHAR(200) NOT NULL,
    application_status VARCHAR(50) NOT NULL DEFAULT 'applied',
    
    -- Application Context
    application_source VARCHAR(50), -- job_board, referral, direct, etc.
    cover_letter_used TEXT,
    notes TEXT,
    
    -- Timeline
    applied_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_status_update TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE profile_activity_log (
    activity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    
    -- Activity Details
    activity_type VARCHAR(50) NOT NULL, -- profile_update, skill_added, job_applied, resume_generated, etc.
    activity_description TEXT,
    affected_section VARCHAR(50), -- skills, highlights, preferences, etc.
    
    -- Context
    activity_data JSONB, -- additional context data
    user_initiated BOOLEAN DEFAULT true,
    ai_triggered BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Profile lookups
CREATE INDEX idx_candidate_profiles_user_id ON candidate_profiles(user_id);
CREATE INDEX idx_candidate_profiles_status ON candidate_profiles(profile_status);

-- Skills matching
CREATE INDEX idx_candidate_skills_profile_id ON candidate_skills(profile_id);
CREATE INDEX idx_candidate_skills_keywords ON candidate_skills USING GIN(keywords);
CREATE INDEX idx_candidate_skills_type ON candidate_skills(skill_type);
CREATE INDEX idx_candidate_skills_featured ON candidate_skills(is_featured);

-- Career highlights matching
CREATE INDEX idx_career_highlights_profile_id ON career_highlights(profile_id);
CREATE INDEX idx_career_highlights_keywords ON career_highlights USING GIN(keywords);
CREATE INDEX idx_career_highlights_category ON career_highlights(highlight_category);
CREATE INDEX idx_career_highlights_featured ON career_highlights(is_featured);

-- Job matching
CREATE INDEX idx_job_postings_source ON job_postings(job_board_source);
CREATE INDEX idx_job_postings_status ON job_postings(job_status);
CREATE INDEX idx_job_postings_skills ON job_postings USING GIN(required_skills);

-- Matching tables
CREATE INDEX idx_job_skill_matches_profile_job ON job_skill_matches(profile_id, job_id);
CREATE INDEX idx_job_skill_matches_score ON job_skill_matches(match_score DESC);
CREATE INDEX idx_job_highlight_matches_profile_job ON job_highlight_matches(profile_id, job_id);
CREATE INDEX idx_job_highlight_matches_score ON job_highlight_matches(relevance_score DESC);

-- Activity tracking
CREATE INDEX idx_job_applications_profile_id ON job_applications(profile_id);
CREATE INDEX idx_job_applications_status ON job_applications(application_status);
CREATE INDEX idx_profile_activity_log_profile_id ON profile_activity_log(profile_id);
CREATE INDEX idx_profile_activity_log_type ON profile_activity_log(activity_type);

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE candidate_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE candidate_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_highlights ENABLE ROW LEVEL SECURITY;
ALTER TABLE employment_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_coaching_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_activity_log ENABLE ROW LEVEL SECURITY;

-- Policies: Users can only access their own data
CREATE POLICY "Users can view own profile" ON candidate_profiles FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own profile" ON candidate_profiles FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own profile" ON candidate_profiles FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can manage own skills" ON candidate_skills FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own highlights" ON career_highlights FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own employment" ON employment_history FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own preferences" ON job_preferences FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own resumes" ON generated_resumes FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own coaching" ON ai_coaching_sessions FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own applications" ON job_applications FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own activity" ON profile_activity_log FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

-- Job postings are readable by all authenticated users
CREATE POLICY "Authenticated users can view jobs" ON job_postings FOR SELECT TO authenticated USING (true);

-- Skill and highlight categories are readable by all
CREATE POLICY "Anyone can view skill categories" ON skill_categories FOR SELECT USING (true);

-- =====================================================
-- FUNCTIONS FOR DYNAMIC RESUME GENERATION
-- =====================================================

-- Function to get top matching skills for a job
CREATE OR REPLACE FUNCTION get_top_matching_skills(
    p_profile_id UUID,
    p_job_id UUID,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    skill_id UUID,
    skill_name VARCHAR,
    match_score DECIMAL,
    proficiency_level VARCHAR,
    years_experience INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cs.skill_id,
        cs.skill_name,
        jsm.match_score,
        cs.proficiency_level,
        cs.years_experience
    FROM candidate_skills cs
    JOIN job_skill_matches jsm ON cs.skill_id = jsm.skill_id
    WHERE cs.profile_id = p_profile_id 
    AND jsm.job_id = p_job_id
    ORDER BY jsm.match_score DESC, cs.base_weight DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to get top matching career highlights for a job
CREATE OR REPLACE FUNCTION get_top_matching_highlights(
    p_profile_id UUID,
    p_job_id UUID,
    p_limit INTEGER DEFAULT 3
)
RETURNS TABLE (
    highlight_id UUID,
    title VARCHAR,
    description TEXT,
    relevance_score DECIMAL,
    impact_metrics JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ch.highlight_id,
        ch.title,
        ch.description,
        jhm.relevance_score,
        ch.impact_metrics
    FROM career_highlights ch
    JOIN job_highlight_matches jhm ON ch.highlight_id = jhm.highlight_id
    WHERE ch.profile_id = p_profile_id 
    AND jhm.job_id = p_job_id
    ORDER BY jhm.relevance_score DESC, ch.base_weight DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate overall profile-job match score
CREATE OR REPLACE FUNCTION calculate_profile_job_match(
    p_profile_id UUID,
    p_job_id UUID
)
RETURNS DECIMAL AS $$
DECLARE
    skills_score DECIMAL;
    highlights_score DECIMAL;
    overall_score DECIMAL;
BEGIN
    -- Calculate average skills match score
    SELECT COALESCE(AVG(match_score), 0) INTO skills_score
    FROM job_skill_matches
    WHERE profile_id = p_profile_id AND job_id = p_job_id;
    
    -- Calculate average highlights relevance score
    SELECT COALESCE(AVG(relevance_score), 0) INTO highlights_score
    FROM job_highlight_matches
    WHERE profile_id = p_profile_id AND job_id = p_job_id;
    
    -- Weighted average (skills 60%, highlights 40%)
    overall_score := (skills_score * 0.6) + (highlights_score * 0.4);
    
    RETURN overall_score;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- SAMPLE DATA INSERTION
-- =====================================================

-- Insert skill categories
INSERT INTO skill_categories (category_name, category_description, display_order) VALUES
('AI/ML Development', 'Artificial Intelligence and Machine Learning skills', 1),
('Backend Development', 'Server-side development and API skills', 2),
('Cloud Infrastructure', 'Cloud platforms and DevOps skills', 3),
('Program Management', 'Project and program management capabilities', 4),
('Healthcare Systems', 'Healthcare technology and systems expertise', 5),
('CRM Systems', 'Customer relationship management platforms', 6),
('Frontend Development', 'User interface and frontend technologies', 7),
('Data Management', 'Database and data handling skills', 8);

-- Note: Actual profile data would be inserted via API calls
-- This schema supports the full dynamic resume generation workflow
