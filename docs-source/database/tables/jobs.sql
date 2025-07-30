-- =====================================================
-- JOBS TABLE - Comprehensive Job Data Model
-- Supports ATS API compatibility and AI-powered analysis
-- =====================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Employment type enumeration
CREATE TYPE employment_type AS ENUM (
    'full_time',
    'part_time', 
    'contract',
    'freelance',
    'internship',
    'temporary'
);

-- Location type enumeration
CREATE TYPE location_type AS ENUM (
    'on_site',
    'hybrid',
    'remote'
);

-- Job level enumeration
CREATE TYPE job_level AS ENUM (
    'entry',
    'mid',
    'senior',
    'lead',
    'manager',
    'director',
    'vp',
    'executive'
);

-- Job status enumeration
CREATE TYPE job_status AS ENUM (
    'open',
    'closed',
    'draft',
    'archived',
    'paused'
);

-- Visa sponsorship status enumeration
CREATE TYPE visa_sponsorship_status AS ENUM (
    'available',
    'not_available',
    'case_by_case'
);

-- Pay frequency enumeration
CREATE TYPE pay_frequency AS ENUM (
    'annual',
    'hourly',
    'monthly',
    'weekly',
    'project'
);

-- =====================================================
-- MAIN JOBS TABLE
-- =====================================================

CREATE TABLE jobs (
    -- Core Identifiers
    job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_job_id VARCHAR(200),
    requisition_id VARCHAR(100),
    slug VARCHAR(200),
    
    -- Basic Job Information
    title VARCHAR(300) NOT NULL,
    description TEXT NOT NULL,
    summary TEXT,
    employment_type employment_type DEFAULT 'full_time',
    department VARCHAR(200),
    job_function VARCHAR(200),
    job_level job_level DEFAULT 'mid',
    
    -- Company Information
    company_id UUID,
    company_name VARCHAR(300) NOT NULL,
    office_id UUID,
    
    -- Location Information
    location_city VARCHAR(100),
    location_state VARCHAR(100),
    location_country VARCHAR(100),
    location_postal_code VARCHAR(20),
    location_type location_type DEFAULT 'on_site',
    workplace_policy TEXT,
    remote_locations TEXT[], -- Array of acceptable remote locations
    is_remote_friendly BOOLEAN DEFAULT false,
    
    -- Compensation
    min_salary DECIMAL(12,2),
    max_salary DECIMAL(12,2),
    currency VARCHAR(10) DEFAULT 'USD',
    pay_frequency pay_frequency DEFAULT 'annual',
    bonus_info TEXT,
    equity_info TEXT,
    commission_info TEXT,
    
    -- Visa and Relocation
    visa_sponsorship visa_sponsorship_status DEFAULT 'not_available',
    relocation_assistance BOOLEAN DEFAULT false,
    
    -- Posting Information
    status job_status DEFAULT 'open',
    posted_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closing_date TIMESTAMP WITH TIME ZONE,
    job_board_source VARCHAR(100),
    language VARCHAR(10) DEFAULT 'en',
    is_internal BOOLEAN DEFAULT false,
    
    -- Application Information
    application_url TEXT,
    application_instructions TEXT,
    contact_email VARCHAR(200),
    recruiter_name VARCHAR(200),
    hiring_manager VARCHAR(200),
    application_deadline TIMESTAMP WITH TIME ZONE,
    expected_response_time VARCHAR(100),
    
    -- Job Status Monitoring Fields
    is_active BOOLEAN DEFAULT true,
    last_verified_active TIMESTAMP WITH TIME ZONE,
    closed_date TIMESTAMP WITH TIME ZONE,
    closure_reason VARCHAR(50), -- expired, filled, cancelled, company_decision
    closure_detection_method VARCHAR(50), -- automated_check, manual_update, ats_api
    verification_attempts INTEGER DEFAULT 0,
    last_verification_attempt TIMESTAMP WITH TIME ZONE,
    verification_failures INTEGER DEFAULT 0,
    last_verification_error TEXT,
    posting_duration_days INTEGER,
    estimated_fill_time INTEGER,
    status_changes JSONB DEFAULT '[]', -- Array of status change history
    
    -- Job Repost Detection Fields
    is_repost BOOLEAN DEFAULT false,
    original_job_id UUID REFERENCES jobs(job_id) ON DELETE SET NULL,
    repost_cluster_id VARCHAR(100),
    repost_detection_score DECIMAL(3,2), -- 0.00-1.00 similarity score
    repost_detection_method VARCHAR(50), -- automated_similarity, manual_flag
    repost_detected_at TIMESTAMP WITH TIME ZONE,
    similarity_factors TEXT[], -- Array of similarity indicators
    
    -- Job Classification & Analytics Fields
    is_white_collar BOOLEAN DEFAULT NULL, -- NULL = unclassified, TRUE/FALSE = classified
    job_category VARCHAR(100), -- Technology, Finance, Healthcare, Marketing, etc.
    job_sector VARCHAR(100), -- Tech, Financial Services, Healthcare, etc.
    occupation_code VARCHAR(20), -- SOC code or similar standardized occupation code
    seniority_level VARCHAR(50), -- entry, mid, senior, executive, c_suite
    
    -- White Collar Classification Keywords
    classification_keywords TEXT[], -- Keywords used for white collar determination
    sector_keywords TEXT[], -- Keywords indicating sector/industry
    skill_keywords TEXT[], -- Required skills extracted from description
    
    -- Geographic Analytics
    region VARCHAR(100), -- Northern California, Bay Area, etc.
    metro_area VARCHAR(100), -- San Francisco-Oakland-Berkeley, San Jose-Sunnyvale-Santa Clara
    county VARCHAR(100), -- Santa Clara, San Francisco, Alameda, etc.
    is_target_region BOOLEAN DEFAULT false, -- Flag for target geographic area
    
    -- Workforce Analytics Fields
    education_level VARCHAR(50), -- bachelors, masters, phd, high_school, etc.
    experience_years_min INTEGER, -- Minimum years experience required
    experience_years_max INTEGER, -- Maximum years experience required
    remote_work_option VARCHAR(50), -- remote, hybrid, onsite, flexible
    
    -- Industry & Sector Classification
    industry_primary VARCHAR(100), -- Primary industry classification
    industry_secondary VARCHAR(100), -- Secondary industry if applicable
    company_size_category VARCHAR(50), -- startup, small, medium, large, enterprise
    
    -- Job Market Analytics
    posting_frequency_score DECIMAL(3,2), -- How frequently this type of job is posted
    market_demand_indicator VARCHAR(50), -- high, medium, low demand
    salary_competitiveness_score DECIMAL(3,2), -- 0.00-1.00 compared to market
    
    -- Metadata
    tags TEXT[], -- Array of tags/keywords
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- JOB REQUIREMENTS TABLE
-- =====================================================

CREATE TABLE job_requirements (
    requirement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    
    -- Requirement Details
    requirement_type VARCHAR(50) NOT NULL, -- skill_required, skill_preferred, qualification_required, etc.
    requirement_text TEXT NOT NULL,
    category VARCHAR(100), -- technical, soft_skill, education, certification, etc.
    importance_level INTEGER DEFAULT 3, -- 1=critical, 2=important, 3=preferred
    
    -- AI Analysis
    keyword_extracted BOOLEAN DEFAULT false,
    skill_category VARCHAR(100),
    proficiency_level VARCHAR(50), -- beginner, intermediate, advanced, expert
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- JOB BENEFITS TABLE
-- =====================================================

CREATE TABLE job_benefits (
    benefit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    
    -- Benefit Details
    benefit_type VARCHAR(100) NOT NULL, -- health_insurance, retirement_401k, etc.
    benefit_description TEXT,
    is_available BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- JOB AI ENRICHMENT TABLE
-- =====================================================

CREATE TABLE job_ai_enrichment (
    enrichment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    
    -- AI-Extracted Data
    keywords TEXT[], -- Array of extracted keywords
    tech_stack TEXT[], -- Array of technologies mentioned
    industry_tags TEXT[], -- Array of industry classifications
    role_category VARCHAR(100),
    
    -- AI Scoring
    seniority_score DECIMAL(3,2), -- 0.00 to 1.00
    complexity_score DECIMAL(3,2), -- 0.00 to 1.00
    growth_potential_score DECIMAL(3,2), -- 0.00 to 1.00
    
    -- Company Analysis
    culture_keywords TEXT[],
    company_stage VARCHAR(50), -- startup, growth, enterprise
    team_size_estimate VARCHAR(50),
    management_scope VARCHAR(100),
    technical_depth VARCHAR(50),
    business_impact VARCHAR(100),
    
    -- Processing Metadata
    ai_model_version VARCHAR(50),
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    confidence_score DECIMAL(3,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INTERVIEW PROCESS TABLE
-- =====================================================

CREATE TABLE job_interview_process (
    process_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    
    -- Interview Stage Details
    stage_order INTEGER NOT NULL,
    stage_name VARCHAR(200) NOT NULL, -- phone_screen, technical_interview, onsite, etc.
    stage_description TEXT,
    estimated_duration VARCHAR(50),
    interviewer_role VARCHAR(100),
    
    -- Stage Requirements
    preparation_notes TEXT,
    materials_needed TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Primary search indexes
CREATE INDEX idx_jobs_title ON jobs USING GIN (to_tsvector('english', title));
CREATE INDEX idx_jobs_description ON jobs USING GIN (to_tsvector('english', description));
CREATE INDEX idx_jobs_company_name ON jobs(company_name);
CREATE INDEX idx_jobs_location_city ON jobs(location_city);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_posted_date ON jobs(posted_date DESC);
CREATE INDEX idx_jobs_closing_date ON jobs(closing_date) WHERE closing_date IS NOT NULL;

-- Salary range indexes
CREATE INDEX idx_jobs_salary_range ON jobs(min_salary, max_salary) WHERE min_salary IS NOT NULL OR max_salary IS NOT NULL;

-- Location and remote work indexes
CREATE INDEX idx_jobs_location_type ON jobs(location_type);
CREATE INDEX idx_jobs_remote_friendly ON jobs(is_remote_friendly) WHERE is_remote_friendly = true;

-- Tags and metadata indexes
CREATE INDEX idx_jobs_tags ON jobs USING GIN (tags);
CREATE INDEX idx_jobs_metadata ON jobs USING GIN (metadata);

-- AI enrichment indexes
CREATE INDEX idx_job_ai_keywords ON job_ai_enrichment USING GIN (keywords);
CREATE INDEX idx_job_ai_tech_stack ON job_ai_enrichment USING GIN (tech_stack);
CREATE INDEX idx_job_ai_seniority_score ON job_ai_enrichment(seniority_score) WHERE seniority_score IS NOT NULL;

-- Requirements indexes
CREATE INDEX idx_job_requirements_type ON job_requirements(requirement_type);
CREATE INDEX idx_job_requirements_category ON job_requirements(category);
CREATE INDEX idx_job_requirements_importance ON job_requirements(importance_level);

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_jobs_updated_at 
    BEFORE UPDATE ON jobs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_ai_enrichment_updated_at 
    BEFORE UPDATE ON job_ai_enrichment 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Function to generate slug from title
CREATE OR REPLACE FUNCTION generate_job_slug(job_title TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN lower(regexp_replace(regexp_replace(job_title, '[^\w\s-]', '', 'g'), '[-\s]+', '-', 'g'));
END;
$$ LANGUAGE plpgsql;

-- Function to check if job is remote eligible
CREATE OR REPLACE FUNCTION is_job_remote_eligible(job_row jobs)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN job_row.location_type IN ('remote', 'hybrid') OR job_row.is_remote_friendly = true;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- SAMPLE DATA INSERTION FUNCTION
-- =====================================================

CREATE OR REPLACE FUNCTION insert_sample_job_data()
RETURNS VOID AS $$
DECLARE
    sample_job_id UUID;
BEGIN
    -- Insert sample job
    INSERT INTO jobs (
        title, description, company_name, location_city, location_state, 
        location_type, min_salary, max_salary, employment_type, job_level,
        application_url, tags
    ) VALUES (
        'Senior Software Engineer',
        'We are looking for a Senior Software Engineer to join our growing team...',
        'TechCorp Inc',
        'San Francisco',
        'CA',
        'hybrid',
        150000,
        200000,
        'full_time',
        'senior',
        'https://techcorp.com/careers/senior-engineer',
        ARRAY['python', 'react', 'aws', 'microservices']
    ) RETURNING job_id INTO sample_job_id;
    
    -- Insert sample requirements
    INSERT INTO job_requirements (job_id, requirement_type, requirement_text, category, importance_level) VALUES
    (sample_job_id, 'skill_required', 'Python programming', 'technical', 1),
    (sample_job_id, 'skill_required', 'React.js', 'technical', 1),
    (sample_job_id, 'skill_preferred', 'AWS experience', 'technical', 2),
    (sample_job_id, 'qualification_required', 'Bachelor''s degree in Computer Science', 'education', 2);
    
    -- Insert sample benefits
    INSERT INTO job_benefits (job_id, benefit_type, benefit_description) VALUES
    (sample_job_id, 'health_insurance', 'Comprehensive health, dental, and vision coverage'),
    (sample_job_id, 'retirement_401k', '401(k) with company matching up to 6%'),
    (sample_job_id, 'flexible_schedule', 'Flexible working hours and remote work options');
    
    -- Insert sample AI enrichment
    INSERT INTO job_ai_enrichment (
        job_id, keywords, tech_stack, industry_tags, role_category,
        seniority_score, complexity_score, company_stage
    ) VALUES (
        sample_job_id,
        ARRAY['software engineering', 'full stack', 'scalability', 'team leadership'],
        ARRAY['Python', 'React', 'AWS', 'Docker', 'PostgreSQL'],
        ARRAY['technology', 'saas', 'b2b'],
        'software_engineering',
        0.85,
        0.78,
        'growth'
    );
    
    RAISE NOTICE 'Sample job data inserted successfully with job_id: %', sample_job_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTS AND DOCUMENTATION
-- =====================================================

COMMENT ON TABLE jobs IS 'Comprehensive job postings with ATS compatibility and AI enrichment support';
COMMENT ON TABLE job_requirements IS 'Detailed job requirements and qualifications with AI categorization';
COMMENT ON TABLE job_benefits IS 'Job benefits and perks offered by employers';
COMMENT ON TABLE job_ai_enrichment IS 'AI-generated insights and analysis for job postings';
COMMENT ON TABLE job_interview_process IS 'Interview process stages and requirements for jobs';

COMMENT ON COLUMN jobs.external_job_id IS 'External ATS or job board identifier';
COMMENT ON COLUMN jobs.slug IS 'URL-safe identifier generated from job title';
COMMENT ON COLUMN jobs.metadata IS 'Flexible JSON storage for additional job attributes';
COMMENT ON COLUMN job_ai_enrichment.confidence_score IS 'AI model confidence in the enrichment data (0.00-1.00)';
COMMENT ON COLUMN job_requirements.importance_level IS 'Requirement importance: 1=critical, 2=important, 3=preferred';
