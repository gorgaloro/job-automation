-- =====================================================
-- AI JOB SEARCH AUTOMATION PLATFORM - DATABASE SCHEMA
-- =====================================================
-- Comprehensive PostgreSQL schema for Supabase backend
-- Supports multi-user job search automation with AI scoring
-- Row Level Security (RLS) enabled for data isolation
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- =====================================================
-- CORE REFERENCE TABLES
-- =====================================================

-- Geographic locations for job filtering
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL DEFAULT 'United States',
    region VARCHAR(100), -- e.g., 'Bay Area', 'Northern California'
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(city, state, country)
);

-- Job categories and industries
CREATE TABLE job_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    parent_category_id UUID REFERENCES job_categories(id),
    description TEXT,
    keywords TEXT[], -- Array of relevant keywords
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Companies and organizations
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    domain VARCHAR(100), -- Company website domain
    industry VARCHAR(100),
    size_category VARCHAR(50), -- 'startup', 'small', 'medium', 'large', 'enterprise'
    employee_count_min INTEGER,
    employee_count_max INTEGER,
    headquarters_location_id UUID REFERENCES locations(id),
    description TEXT,
    culture_keywords TEXT[],
    glassdoor_rating DECIMAL(3,2),
    linkedin_url VARCHAR(500),
    careers_page_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(name, domain)
);

-- =====================================================
-- CORE JOBS TABLE
-- =====================================================

-- Main jobs table with comprehensive job data
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- References auth.users
    
    -- Basic job information
    title VARCHAR(200) NOT NULL,
    company_id UUID REFERENCES companies(id),
    company_name VARCHAR(200) NOT NULL, -- Denormalized for performance
    location_id UUID REFERENCES locations(id),
    location_text VARCHAR(200), -- Original location string from posting
    
    -- Job details
    description TEXT NOT NULL,
    requirements TEXT,
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(3) DEFAULT 'USD',
    employment_type VARCHAR(50), -- 'full-time', 'part-time', 'contract', 'internship'
    experience_level VARCHAR(50), -- 'entry', 'mid', 'senior', 'executive'
    remote_type VARCHAR(50), -- 'on-site', 'remote', 'hybrid'
    
    -- Source and tracking
    source VARCHAR(100) NOT NULL, -- 'indeed', 'linkedin', 'company_website', etc.
    source_job_id VARCHAR(200), -- Original ID from source
    source_url VARCHAR(1000) NOT NULL,
    posting_date DATE,
    discovered_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Job status and tracking
    status VARCHAR(50) DEFAULT 'discovered', -- 'discovered', 'interested', 'applied', 'interviewing', 'rejected', 'withdrawn', 'offer'
    application_date TIMESTAMP WITH TIME ZONE,
    last_status_change TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- AI scoring and analysis
    relevance_score DECIMAL(5,3), -- 0.000 to 1.000
    match_score DECIMAL(5,3), -- Overall job-candidate match
    salary_score DECIMAL(5,3), -- Salary competitiveness
    location_score DECIMAL(5,3), -- Location preference match
    company_score DECIMAL(5,3), -- Company attractiveness
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    is_duplicate BOOLEAN DEFAULT false,
    duplicate_of_job_id UUID REFERENCES jobs(id),
    notes TEXT,
    tags TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_salary_range CHECK (salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max),
    CONSTRAINT valid_relevance_score CHECK (relevance_score IS NULL OR (relevance_score >= 0 AND relevance_score <= 1)),
    CONSTRAINT valid_match_score CHECK (match_score IS NULL OR (match_score >= 0 AND match_score <= 1))
);

-- =====================================================
-- JOB APPLICATION TRACKING
-- =====================================================

-- Track job applications and their status
CREATE TABLE job_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- References auth.users
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    
    -- Application details
    application_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    application_method VARCHAR(100), -- 'company_website', 'indeed', 'linkedin', 'email', 'referral'
    cover_letter_used BOOLEAN DEFAULT false,
    resume_version VARCHAR(100), -- Version/variant of resume used
    
    -- Application status tracking
    status VARCHAR(50) DEFAULT 'submitted', -- 'submitted', 'under_review', 'phone_screen', 'interview_scheduled', 'interviewed', 'offer', 'rejected', 'withdrawn'
    status_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Contact and follow-up
    contact_person VARCHAR(200),
    contact_email VARCHAR(200),
    contact_phone VARCHAR(50),
    follow_up_date DATE,
    last_contact_date DATE,
    
    -- Interview tracking
    interview_rounds INTEGER DEFAULT 0,
    next_interview_date TIMESTAMP WITH TIME ZONE,
    interview_type VARCHAR(100), -- 'phone', 'video', 'in_person', 'technical', 'panel'
    
    -- Outcome tracking
    rejection_reason TEXT,
    offer_amount INTEGER,
    offer_currency VARCHAR(3) DEFAULT 'USD',
    offer_date DATE,
    response_deadline DATE,
    
    -- Notes and feedback
    notes TEXT,
    interview_feedback TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, job_id) -- One application per user per job
);

-- =====================================================
-- AI SCORING AND ANALYTICS
-- =====================================================

-- Detailed AI scoring for job-candidate matching
CREATE TABLE job_scoring (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- References auth.users
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    
    -- Overall scoring
    overall_score DECIMAL(5,3) NOT NULL, -- 0.000 to 1.000
    confidence_level DECIMAL(5,3), -- AI confidence in the scoring
    
    -- Detailed scoring dimensions
    skills_match_score DECIMAL(5,3),
    experience_match_score DECIMAL(5,3),
    education_match_score DECIMAL(5,3),
    location_preference_score DECIMAL(5,3),
    salary_expectation_score DECIMAL(5,3),
    company_culture_score DECIMAL(5,3),
    career_growth_score DECIMAL(5,3),
    
    -- Keyword and semantic analysis
    matched_keywords TEXT[],
    missing_keywords TEXT[],
    semantic_similarity_score DECIMAL(5,3),
    
    -- AI analysis and recommendations
    strengths TEXT[], -- Areas where candidate is strong
    gaps TEXT[], -- Areas where candidate may be weak
    recommendations TEXT[], -- AI suggestions for improvement
    
    -- Scoring metadata
    ai_model_version VARCHAR(50),
    scoring_algorithm_version VARCHAR(50),
    scored_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, job_id) -- One scoring per user per job
);

-- Resume optimization sessions and results
CREATE TABLE resume_optimization_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- References auth.users
    job_id UUID REFERENCES jobs(id), -- Optional: specific job optimization
    
    -- Session details
    session_name VARCHAR(200),
    optimization_type VARCHAR(100), -- 'job_specific', 'general', 'industry_focused'
    
    -- Input data
    original_resume_content TEXT,
    target_job_description TEXT,
    optimization_goals TEXT[],
    
    -- AI optimization results
    optimized_resume_content TEXT,
    optimization_score DECIMAL(5,3), -- How much improvement was achieved
    
    -- Detailed changes and suggestions
    content_changes JSONB, -- Structured data about what was changed
    ai_suggestions TEXT[],
    keyword_improvements TEXT[],
    formatting_changes TEXT[],
    
    -- Performance metrics
    processing_time_seconds INTEGER,
    ai_model_used VARCHAR(100),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);