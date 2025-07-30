-- =====================================================
-- AI JOB SEARCH AUTOMATION PLATFORM - PRODUCTION SCHEMA
-- Comprehensive Supabase database implementation
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- USER MANAGEMENT & AUTHENTICATION
-- =====================================================

-- User profiles (extends Supabase auth.users)
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    preferred_name VARCHAR(100),
    
    -- Professional information
    current_title VARCHAR(255),
    current_company VARCHAR(255),
    years_experience INTEGER,
    target_roles TEXT[],
    target_industries TEXT[],
    target_locations TEXT[],
    
    -- Platform settings
    notification_preferences JSONB DEFAULT '{}',
    privacy_settings JSONB DEFAULT '{}',
    subscription_tier VARCHAR(20) DEFAULT 'free',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- CORE REFERENCE TABLES
-- =====================================================

-- Companies table for normalization
CREATE TABLE companies (
    company_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    company_slug VARCHAR(255) UNIQUE,
    industry VARCHAR(100),
    company_size VARCHAR(50),
    headquarters_location VARCHAR(255),
    website_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    glassdoor_url VARCHAR(500),
    
    -- Company quality metrics
    repost_frequency DECIMAL(5,2) DEFAULT 0.0,
    total_reposts INTEGER DEFAULT 0,
    quality_flag VARCHAR(10) DEFAULT 'green', -- green, yellow, red
    avg_posting_duration DECIMAL(5,1),
    
    -- AI enrichment data
    company_description TEXT,
    culture_keywords TEXT[],
    tech_stack TEXT[],
    funding_stage VARCHAR(50),
    employee_count INTEGER,
    growth_rate DECIMAL(5,2),
    glassdoor_rating DECIMAL(3,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Locations table for normalization
CREATE TABLE locations (
    location_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'US',
    postal_code VARCHAR(20),
    location_type VARCHAR(20) DEFAULT 'on_site', -- on_site, hybrid, remote
    workplace_policy TEXT,
    is_remote_friendly BOOLEAN DEFAULT FALSE,
    
    -- Geographic classification
    is_northern_california BOOLEAN DEFAULT FALSE,
    region VARCHAR(50), -- bay_area, sacramento_valley, north_coast
    subregion VARCHAR(50), -- san_francisco, silicon_valley, east_bay
    metro_area VARCHAR(100),
    county VARCHAR(50),
    
    -- Transit and accessibility
    transit_accessible BOOLEAN DEFAULT FALSE,
    major_transit_lines TEXT[],
    commute_score DECIMAL(3,2),
    
    -- Regional market data
    regional_job_density DECIMAL(5,2),
    regional_salary_index DECIMAL(5,2),
    cost_of_living_index DECIMAL(5,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job categories for white collar classification
CREATE TABLE job_categories (
    category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_name VARCHAR(100) NOT NULL,
    parent_category_id UUID REFERENCES job_categories(category_id),
    is_white_collar BOOLEAN DEFAULT FALSE,
    classification_keywords TEXT[],
    exclusion_keywords TEXT[],
    industry_sector VARCHAR(100),
    soc_code VARCHAR(20), -- Standard Occupational Classification
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- MAIN JOBS TABLE
-- =====================================================

CREATE TABLE jobs (
    -- Core identifiers
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_job_id VARCHAR(255),
    requisition_id VARCHAR(255),
    slug VARCHAR(255),
    
    -- User association
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Basic job information
    title VARCHAR(500) NOT NULL,
    description TEXT,
    summary TEXT,
    employment_type VARCHAR(20) DEFAULT 'full_time',
    department VARCHAR(100),
    job_function VARCHAR(100),
    job_level VARCHAR(20) DEFAULT 'mid',
    
    -- Company and location references
    company_id UUID REFERENCES companies(company_id),
    company_name VARCHAR(255) NOT NULL,
    office_id VARCHAR(100),
    location_id UUID REFERENCES locations(location_id),
    
    -- Compensation
    min_salary INTEGER,
    max_salary INTEGER,
    currency VARCHAR(3) DEFAULT 'USD',
    pay_frequency VARCHAR(20) DEFAULT 'annually',
    equity_offered BOOLEAN DEFAULT FALSE,
    bonus_eligible BOOLEAN DEFAULT FALSE,
    
    -- Requirements and qualifications
    skills_required TEXT[],
    skills_preferred TEXT[],
    experience_required TEXT,
    education_required VARCHAR(100),
    certifications_required TEXT[],
    languages_required TEXT[],
    
    -- Benefits
    health_insurance BOOLEAN DEFAULT FALSE,
    dental_insurance BOOLEAN DEFAULT FALSE,
    vision_insurance BOOLEAN DEFAULT FALSE,
    retirement_plan BOOLEAN DEFAULT FALSE,
    paid_time_off BOOLEAN DEFAULT FALSE,
    flexible_schedule BOOLEAN DEFAULT FALSE,
    remote_work_option VARCHAR(20),
    professional_development BOOLEAN DEFAULT FALSE,
    
    -- Visa and relocation
    visa_sponsorship VARCHAR(20) DEFAULT 'not_available',
    relocation_assistance BOOLEAN DEFAULT FALSE,
    
    -- Posting information
    status VARCHAR(20) DEFAULT 'open',
    posted_date TIMESTAMP,
    closing_date TIMESTAMP,
    job_board_source VARCHAR(100),
    language VARCHAR(5) DEFAULT 'en',
    is_internal BOOLEAN DEFAULT FALSE,
    
    -- Application information
    application_url VARCHAR(1000),
    application_instructions TEXT,
    contact_email VARCHAR(255),
    recruiter_name VARCHAR(255),
    hiring_manager VARCHAR(255),
    application_deadline TIMESTAMP,
    expected_response_time VARCHAR(100),
    interview_process TEXT[],
    
    -- AI enhancement data
    ai_keywords TEXT[],
    tech_stack TEXT[],
    industry_tags TEXT[],
    seniority_score DECIMAL(3,2),
    complexity_score DECIMAL(3,2),
    remote_work_score DECIMAL(3,2),
    company_stage VARCHAR(50),
    team_size_estimate VARCHAR(50),
    management_scope VARCHAR(100),
    technical_depth VARCHAR(100),
    business_impact VARCHAR(100),
    
    -- White collar classification
    is_white_collar BOOLEAN DEFAULT FALSE,
    white_collar_confidence DECIMAL(3,2) DEFAULT 0.0,
    classification_method VARCHAR(50) DEFAULT 'keyword_based',
    job_category_id UUID REFERENCES job_categories(category_id),
    job_subcategory VARCHAR(100),
    industry_sector VARCHAR(100),
    occupation_code VARCHAR(20),
    key_skills TEXT[],
    education_level VARCHAR(50),
    experience_level VARCHAR(50),
    classification_keywords TEXT[],
    exclusion_keywords TEXT[],
    regional_demand_score DECIMAL(3,2),
    salary_percentile DECIMAL(3,2),
    
    -- User interaction flags
    is_flagged BOOLEAN DEFAULT FALSE,
    is_applied BOOLEAN DEFAULT FALSE,
    is_saved BOOLEAN DEFAULT FALSE,
    user_notes TEXT,
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    
    -- Metadata
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- JOB STATUS TRACKING
-- =====================================================

CREATE TABLE job_status_tracking (
    job_id UUID PRIMARY KEY REFERENCES jobs(job_id) ON DELETE CASCADE,
    
    -- Current status
    is_active BOOLEAN DEFAULT TRUE,
    last_verified_active TIMESTAMP,
    
    -- Closure tracking
    closed_date TIMESTAMP,
    closure_reason VARCHAR(50), -- expired, filled, cancelled, company_decision
    closure_detection_method VARCHAR(50), -- automated_check, manual_update, ats_api
    
    -- Verification tracking
    verification_attempts INTEGER DEFAULT 0,
    last_verification_attempt TIMESTAMP,
    verification_failures INTEGER DEFAULT 0,
    last_verification_error TEXT,
    
    -- Posting duration metrics
    posting_duration_days INTEGER,
    estimated_fill_time INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Status change history
CREATE TABLE job_status_changes (
    change_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    change_reason VARCHAR(100),
    detection_method VARCHAR(50),
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- MULTI-SOURCE TRACKING
-- =====================================================

CREATE TABLE job_sources (
    source_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    
    source_type VARCHAR(20) NOT NULL, -- primary, secondary
    source_name VARCHAR(100) NOT NULL, -- company_website, linkedin, indeed, glassdoor
    source_url VARCHAR(1000) NOT NULL,
    discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_verified TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Content comparison for delta analysis
    content_hash VARCHAR(64),
    content_differences TEXT[],
    last_content_check TIMESTAMP,
    
    -- Source-specific metadata
    source_metadata JSONB
);

-- =====================================================
-- AI SCORING & ANALYTICS
-- =====================================================

-- Job analysis and scoring
CREATE TABLE job_analyses (
    analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Analysis results
    overall_score DECIMAL(3,2) NOT NULL,
    skill_match_score DECIMAL(3,2),
    experience_match_score DECIMAL(3,2),
    culture_fit_score DECIMAL(3,2),
    compensation_score DECIMAL(3,2),
    location_score DECIMAL(3,2),
    
    -- Detailed analysis
    matching_skills TEXT[],
    missing_skills TEXT[],
    skill_gaps TEXT[],
    experience_gaps TEXT[],
    strengths TEXT[],
    concerns TEXT[],
    
    -- AI-generated insights
    summary TEXT,
    recommendations TEXT[],
    action_items TEXT[],
    
    -- Metadata
    analysis_version VARCHAR(20) DEFAULT '1.0',
    model_version VARCHAR(20),
    processing_time_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resume optimization sessions
CREATE TABLE resume_optimizations (
    optimization_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Input resume data
    original_resume JSONB,
    
    -- Optimization results
    optimized_resume JSONB,
    optimization_score DECIMAL(3,2),
    changes_made TEXT[],
    
    -- Section scores
    executive_summary_score DECIMAL(3,2),
    skills_score DECIMAL(3,2),
    experience_score DECIMAL(3,2),
    education_score DECIMAL(3,2),
    
    -- AI suggestions
    suggestions TEXT[],
    keywords_added TEXT[],
    keywords_removed TEXT[],
    
    -- User feedback
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_feedback TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- USER APPLICATIONS & TRACKING
-- =====================================================

CREATE TABLE job_applications (
    application_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Application details
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    application_method VARCHAR(50), -- direct, linkedin, indeed, company_website
    application_url VARCHAR(1000),
    
    -- Documents submitted
    resume_version JSONB,
    cover_letter TEXT,
    portfolio_url VARCHAR(500),
    additional_documents TEXT[],
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'submitted', -- submitted, under_review, interview_scheduled, rejected, offer_received
    last_status_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Interview tracking
    interview_rounds INTEGER DEFAULT 0,
    next_interview_date TIMESTAMP,
    interview_feedback TEXT,
    
    -- Outcome
    outcome VARCHAR(50), -- hired, rejected, withdrawn, expired
    outcome_date TIMESTAMP,
    outcome_reason TEXT,
    
    -- Follow-up tracking
    follow_up_dates TIMESTAMP[],
    follow_up_notes TEXT[],
    
    -- User notes and ratings
    user_notes TEXT,
    experience_rating INTEGER CHECK (experience_rating >= 1 AND experience_rating <= 5),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- PERFORMANCE INDEXES
-- =====================================================

-- Jobs table indexes
CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_company_id ON jobs(company_id);
CREATE INDEX idx_jobs_location_id ON jobs(location_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_posted_date ON jobs(posted_date);
CREATE INDEX idx_jobs_title_search ON jobs USING gin(to_tsvector('english', title));
CREATE INDEX idx_jobs_description_search ON jobs USING gin(to_tsvector('english', description));
CREATE INDEX idx_jobs_skills ON jobs USING gin(skills_required);
CREATE INDEX idx_jobs_is_flagged ON jobs(user_id, is_flagged) WHERE is_flagged = true;
CREATE INDEX idx_jobs_is_saved ON jobs(user_id, is_saved) WHERE is_saved = true;

-- Companies table indexes
CREATE INDEX idx_companies_name ON companies(company_name);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_size ON companies(company_size);

-- Locations table indexes
CREATE INDEX idx_locations_city_state ON locations(city, state);
CREATE INDEX idx_locations_region ON locations(region);
CREATE INDEX idx_locations_remote_friendly ON locations(is_remote_friendly);

-- Job analyses indexes
CREATE INDEX idx_job_analyses_user_job ON job_analyses(user_id, job_id);
CREATE INDEX idx_job_analyses_score ON job_analyses(overall_score);
CREATE INDEX idx_job_analyses_created ON job_analyses(created_at);

-- Job applications indexes
CREATE INDEX idx_job_applications_user ON job_applications(user_id);
CREATE INDEX idx_job_applications_status ON job_applications(status);
CREATE INDEX idx_job_applications_date ON job_applications(application_date);

-- Job status tracking indexes
CREATE INDEX idx_job_status_tracking_active ON job_status_tracking(is_active);
CREATE INDEX idx_job_status_changes_job_id ON job_status_changes(job_id);
CREATE INDEX idx_job_status_changes_timestamp ON job_status_changes(change_timestamp);

-- Job sources indexes
CREATE INDEX idx_job_sources_job_id ON job_sources(job_id);
CREATE INDEX idx_job_sources_source_name ON job_sources(source_name);
CREATE INDEX idx_job_sources_active ON job_sources(is_active);

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS on all user-specific tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_optimizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_applications ENABLE ROW LEVEL SECURITY;

-- User profiles: Users can only access their own profile
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Jobs: Users can only access their own jobs
CREATE POLICY "Users can view own jobs" ON jobs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own jobs" ON jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own jobs" ON jobs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own jobs" ON jobs
    FOR DELETE USING (auth.uid() = user_id);

-- Job analyses: Users can only access their own analyses
CREATE POLICY "Users can view own job analyses" ON job_analyses
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own job analyses" ON job_analyses
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Resume optimizations: Users can only access their own optimizations
CREATE POLICY "Users can view own resume optimizations" ON resume_optimizations
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own resume optimizations" ON resume_optimizations
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Job applications: Users can only access their own applications
CREATE POLICY "Users can view own job applications" ON job_applications
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own job applications" ON job_applications
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own job applications" ON job_applications
    FOR UPDATE USING (auth.uid() = user_id);

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_status_tracking_updated_at BEFORE UPDATE ON job_status_tracking
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_applications_updated_at BEFORE UPDATE ON job_applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- INITIAL DATA SEEDING
-- =====================================================

-- Insert default job categories
INSERT INTO job_categories (category_name, is_white_collar, classification_keywords, industry_sector) VALUES
('Software Engineering', true, ARRAY['software', 'engineer', 'developer', 'programming', 'coding'], 'Technology'),
('Product Management', true, ARRAY['product', 'manager', 'strategy', 'roadmap', 'requirements'], 'Technology'),
('Data Science', true, ARRAY['data', 'scientist', 'analytics', 'machine learning', 'statistics'], 'Technology'),
('Marketing', true, ARRAY['marketing', 'brand', 'campaign', 'digital', 'content'], 'Marketing'),
('Sales', true, ARRAY['sales', 'business development', 'account', 'revenue', 'client'], 'Sales'),
('Finance', true, ARRAY['finance', 'accounting', 'financial', 'budget', 'analyst'], 'Finance'),
('Human Resources', true, ARRAY['hr', 'human resources', 'recruiting', 'talent', 'people'], 'Human Resources'),
('Operations', true, ARRAY['operations', 'logistics', 'supply chain', 'process', 'efficiency'], 'Operations'),
('Design', true, ARRAY['design', 'ux', 'ui', 'creative', 'visual', 'graphic'], 'Design'),
('Consulting', true, ARRAY['consultant', 'advisory', 'strategy', 'transformation', 'implementation'], 'Consulting');

-- Create sample locations for Northern California
INSERT INTO locations (city, state, region, subregion, is_northern_california, is_remote_friendly) VALUES
('San Francisco', 'CA', 'bay_area', 'san_francisco', true, true),
('San Jose', 'CA', 'bay_area', 'silicon_valley', true, true),
('Oakland', 'CA', 'bay_area', 'east_bay', true, true),
('Palo Alto', 'CA', 'bay_area', 'silicon_valley', true, true),
('Mountain View', 'CA', 'bay_area', 'silicon_valley', true, true),
('Sunnyvale', 'CA', 'bay_area', 'silicon_valley', true, true),
('Berkeley', 'CA', 'bay_area', 'east_bay', true, true),
('Fremont', 'CA', 'bay_area', 'east_bay', true, true),
('Sacramento', 'CA', 'sacramento_valley', 'sacramento', true, false),
('Remote', 'CA', 'remote', 'remote', true, true);

COMMIT;
