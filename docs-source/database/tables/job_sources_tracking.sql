-- =====================================================
-- MULTI-SOURCE JOB TRACKING SCHEMA
-- Tracks jobs across primary (company career pages) and secondary sources (job boards)
-- Enables delta analysis and HR quality assessment
-- =====================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Source type enumeration
CREATE TYPE job_source_type AS ENUM (
    'primary',      -- Company career page (authoritative source)
    'secondary'     -- Job boards (LinkedIn, Indeed, etc.)
);

-- Source platform enumeration
CREATE TYPE job_source_platform AS ENUM (
    'company_careers',
    'greenhouse',
    'lever',
    'smartrecruiters',
    'workable',
    'linkedin',
    'indeed',
    'glassdoor',
    'ziprecruiter',
    'monster',
    'careerbuilder',
    'dice',
    'stackoverflow',
    'angellist',
    'builtin',
    'other'
);

-- Delta status enumeration
CREATE TYPE delta_status AS ENUM (
    'identical',        -- Content matches exactly
    'minor_differences', -- Small formatting/style differences
    'content_drift',    -- Meaningful content differences
    'major_discrepancy', -- Significant differences in requirements/details
    'outdated_secondary' -- Secondary source appears outdated
);

-- =====================================================
-- JOB SOURCES TABLE
-- Tracks all sources where a job is posted
-- =====================================================

CREATE TABLE job_sources (
    source_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    
    -- Source Classification
    source_type job_source_type NOT NULL,
    source_platform job_source_platform NOT NULL,
    source_name VARCHAR(200) NOT NULL, -- e.g., "LinkedIn Jobs", "Company Careers Page"
    
    -- Source Details
    source_url TEXT NOT NULL,
    external_job_id VARCHAR(200), -- Job ID on the external platform
    requisition_id VARCHAR(100), -- Company's internal requisition ID
    
    -- Content Tracking
    title VARCHAR(500),
    description TEXT,
    requirements TEXT,
    salary_text TEXT,
    location_text VARCHAR(300),
    
    -- Content Hashes for Change Detection
    title_hash VARCHAR(64),
    description_hash VARCHAR(64),
    requirements_hash VARCHAR(64),
    content_fingerprint VARCHAR(64), -- Overall content fingerprint
    
    -- Discovery and Status
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    first_seen_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_verified_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    removed_at TIMESTAMP WITH TIME ZONE,
    
    -- Priority and Reliability
    is_primary_source BOOLEAN DEFAULT false, -- True for company career pages
    source_reliability_score DECIMAL(3,2) DEFAULT 1.00, -- 0.00-1.00
    content_freshness_score DECIMAL(3,2) DEFAULT 1.00, -- How up-to-date content appears
    
    -- Metadata
    scraping_metadata JSONB DEFAULT '{}', -- Technical scraping details
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- JOB SOURCE DELTAS TABLE
-- Tracks differences between primary and secondary sources
-- =====================================================

CREATE TABLE job_source_deltas (
    delta_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    primary_source_id UUID NOT NULL REFERENCES job_sources(source_id) ON DELETE CASCADE,
    secondary_source_id UUID NOT NULL REFERENCES job_sources(source_id) ON DELETE CASCADE,
    
    -- Delta Analysis
    delta_status delta_status NOT NULL,
    overall_similarity_score DECIMAL(3,2), -- 0.00-1.00
    
    -- Field-Level Similarities
    title_similarity DECIMAL(3,2),
    description_similarity DECIMAL(3,2),
    requirements_similarity DECIMAL(3,2),
    salary_similarity DECIMAL(3,2),
    location_similarity DECIMAL(3,2),
    
    -- Specific Differences
    title_differences TEXT[],
    description_differences TEXT[],
    requirements_differences TEXT[],
    salary_differences TEXT[],
    location_differences TEXT[],
    
    -- Analysis Metadata
    analysis_method VARCHAR(50) DEFAULT 'automated', -- automated, manual
    confidence_score DECIMAL(3,2), -- Confidence in delta analysis
    
    -- HR Quality Indicators
    indicates_outdated_secondary BOOLEAN DEFAULT false,
    indicates_poor_sync BOOLEAN DEFAULT false,
    quality_impact_score DECIMAL(3,2), -- Impact on HR quality assessment
    
    -- Timestamps
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- COMPANY SOURCE ANALYTICS TABLE
-- Company-level analytics on source management quality
-- =====================================================

CREATE TABLE company_source_analytics (
    analytics_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL,
    company_name VARCHAR(300) NOT NULL,
    
    -- Source Distribution
    total_jobs_tracked INTEGER DEFAULT 0,
    jobs_with_primary_source INTEGER DEFAULT 0,
    jobs_with_multiple_sources INTEGER DEFAULT 0,
    avg_sources_per_job DECIMAL(4,2) DEFAULT 0.00,
    
    -- Platform Usage
    platforms_used TEXT[], -- Array of platforms company posts to
    primary_platforms TEXT[], -- Platforms used as primary sources
    secondary_platforms TEXT[], -- Platforms used as secondary sources
    
    -- Content Consistency
    jobs_with_deltas INTEGER DEFAULT 0,
    avg_similarity_score DECIMAL(3,2) DEFAULT 1.00,
    content_consistency_score DECIMAL(3,2) DEFAULT 1.00, -- Overall consistency rating
    
    -- Quality Indicators
    outdated_secondary_count INTEGER DEFAULT 0,
    poor_sync_indicators INTEGER DEFAULT 0,
    hr_quality_score DECIMAL(3,2) DEFAULT 1.00, -- 0.00-1.00, higher = better
    
    -- Red Flags
    source_management_flags TEXT[], -- Array of identified issues
    
    -- Analysis Metadata
    last_analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    jobs_analyzed_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- SOURCE DISCOVERY LOG TABLE
-- Tracks how and when job sources are discovered
-- =====================================================

CREATE TABLE source_discovery_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES job_sources(source_id) ON DELETE CASCADE,
    
    -- Discovery Details
    discovery_method VARCHAR(100) NOT NULL, -- api_scrape, manual_entry, cross_reference
    discovery_trigger VARCHAR(100), -- scheduled_scan, duplicate_detection, user_submission
    
    -- Discovery Context
    discovered_from_url TEXT, -- URL that led to discovery
    discovered_via_platform VARCHAR(100), -- Platform that led to discovery
    discovery_confidence DECIMAL(3,2), -- Confidence in job matching
    
    -- Processing Details
    processing_time_ms INTEGER,
    processing_status VARCHAR(50) DEFAULT 'success', -- success, failed, partial
    processing_errors TEXT[],
    
    -- Timestamps
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Job sources indexes
CREATE INDEX idx_job_sources_job_id ON job_sources(job_id);
CREATE INDEX idx_job_sources_platform ON job_sources(source_platform);
CREATE INDEX idx_job_sources_type ON job_sources(source_type);
CREATE INDEX idx_job_sources_primary ON job_sources(is_primary_source) WHERE is_primary_source = true;
CREATE INDEX idx_job_sources_active ON job_sources(is_active) WHERE is_active = true;
CREATE INDEX idx_job_sources_url ON job_sources USING hash(source_url);
CREATE INDEX idx_job_sources_fingerprint ON job_sources(content_fingerprint);

-- Delta analysis indexes
CREATE INDEX idx_job_source_deltas_job ON job_source_deltas(job_id);
CREATE INDEX idx_job_source_deltas_primary ON job_source_deltas(primary_source_id);
CREATE INDEX idx_job_source_deltas_secondary ON job_source_deltas(secondary_source_id);
CREATE INDEX idx_job_source_deltas_status ON job_source_deltas(delta_status);
CREATE INDEX idx_job_source_deltas_similarity ON job_source_deltas(overall_similarity_score);

-- Company analytics indexes
CREATE INDEX idx_company_source_analytics_company ON company_source_analytics(company_id);
CREATE INDEX idx_company_source_analytics_quality ON company_source_analytics(hr_quality_score DESC);
CREATE INDEX idx_company_source_analytics_consistency ON company_source_analytics(content_consistency_score DESC);

-- Discovery log indexes
CREATE INDEX idx_source_discovery_log_job ON source_discovery_log(job_id);
CREATE INDEX idx_source_discovery_log_source ON source_discovery_log(source_id);
CREATE INDEX idx_source_discovery_log_method ON source_discovery_log(discovery_method);
CREATE INDEX idx_source_discovery_log_discovered_at ON source_discovery_log(discovered_at);

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

-- Triggers to automatically update updated_at
CREATE TRIGGER update_job_sources_updated_at 
    BEFORE UPDATE ON job_sources 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_source_deltas_updated_at 
    BEFORE UPDATE ON job_source_deltas 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_source_analytics_updated_at 
    BEFORE UPDATE ON company_source_analytics 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate content fingerprint
CREATE OR REPLACE FUNCTION calculate_content_fingerprint(
    p_title TEXT,
    p_description TEXT,
    p_requirements TEXT
) RETURNS VARCHAR(64) AS $$
BEGIN
    RETURN encode(
        digest(
            COALESCE(p_title, '') || '|' || 
            COALESCE(p_description, '') || '|' || 
            COALESCE(p_requirements, ''),
            'sha256'
        ),
        'hex'
    );
END;
$$ LANGUAGE plpgsql;

-- Function to identify primary source for a job
CREATE OR REPLACE FUNCTION identify_primary_source(
    p_job_id UUID
) RETURNS UUID AS $$
DECLARE
    v_primary_source_id UUID;
BEGIN
    -- First, look for explicitly marked primary sources
    SELECT source_id INTO v_primary_source_id
    FROM job_sources
    WHERE job_id = p_job_id 
    AND is_primary_source = true
    LIMIT 1;
    
    IF v_primary_source_id IS NOT NULL THEN
        RETURN v_primary_source_id;
    END IF;
    
    -- If no explicit primary, prioritize company career pages
    SELECT source_id INTO v_primary_source_id
    FROM job_sources
    WHERE job_id = p_job_id 
    AND source_type = 'primary'
    ORDER BY source_reliability_score DESC, discovered_at ASC
    LIMIT 1;
    
    IF v_primary_source_id IS NOT NULL THEN
        RETURN v_primary_source_id;
    END IF;
    
    -- Fallback to most reliable source
    SELECT source_id INTO v_primary_source_id
    FROM job_sources
    WHERE job_id = p_job_id
    ORDER BY source_reliability_score DESC, discovered_at ASC
    LIMIT 1;
    
    RETURN v_primary_source_id;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate company HR quality score
CREATE OR REPLACE FUNCTION calculate_company_hr_quality_score(
    p_company_id UUID
) RETURNS DECIMAL(3,2) AS $$
DECLARE
    v_total_jobs INTEGER;
    v_jobs_with_deltas INTEGER;
    v_avg_similarity DECIMAL(3,2);
    v_outdated_count INTEGER;
    v_quality_score DECIMAL(3,2) := 1.00;
BEGIN
    -- Get company analytics
    SELECT 
        total_jobs_tracked,
        jobs_with_deltas,
        avg_similarity_score,
        outdated_secondary_count
    INTO 
        v_total_jobs,
        v_jobs_with_deltas,
        v_avg_similarity,
        v_outdated_count
    FROM company_source_analytics
    WHERE company_id = p_company_id;
    
    -- If no data, return neutral score
    IF v_total_jobs IS NULL OR v_total_jobs = 0 THEN
        RETURN 0.75;
    END IF;
    
    -- Penalize high delta rate
    IF v_jobs_with_deltas > 0 THEN
        v_quality_score := v_quality_score - (v_jobs_with_deltas::DECIMAL / v_total_jobs * 0.3);
    END IF;
    
    -- Factor in similarity score
    IF v_avg_similarity IS NOT NULL THEN
        v_quality_score := v_quality_score * v_avg_similarity;
    END IF;
    
    -- Penalize outdated secondary sources
    IF v_outdated_count > 0 THEN
        v_quality_score := v_quality_score - (v_outdated_count::DECIMAL / v_total_jobs * 0.2);
    END IF;
    
    -- Ensure score stays within bounds
    RETURN GREATEST(0.00, LEAST(1.00, v_quality_score));
END;
$$ LANGUAGE plpgsql;

-- Function to detect potential duplicate jobs across sources
CREATE OR REPLACE FUNCTION detect_cross_source_duplicates(
    p_company_id UUID DEFAULT NULL,
    p_similarity_threshold DECIMAL(3,2) DEFAULT 0.85
) RETURNS TABLE (
    job1_id UUID,
    job2_id UUID,
    source1_id UUID,
    source2_id UUID,
    similarity_score DECIMAL(3,2),
    likely_duplicate BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH job_pairs AS (
        SELECT DISTINCT
            js1.job_id as job1_id,
            js2.job_id as job2_id,
            js1.source_id as source1_id,
            js2.source_id as source2_id,
            js1.content_fingerprint as fp1,
            js2.content_fingerprint as fp2
        FROM job_sources js1
        JOIN job_sources js2 ON js1.job_id != js2.job_id
        JOIN jobs j1 ON js1.job_id = j1.job_id
        JOIN jobs j2 ON js2.job_id = j2.job_id
        WHERE j1.company_id = j2.company_id
        AND (p_company_id IS NULL OR j1.company_id = p_company_id)
        AND js1.is_active = true
        AND js2.is_active = true
    )
    SELECT 
        jp.job1_id,
        jp.job2_id,
        jp.source1_id,
        jp.source2_id,
        CASE 
            WHEN jp.fp1 = jp.fp2 THEN 1.00
            ELSE 0.80 -- Placeholder for more sophisticated similarity calculation
        END::DECIMAL(3,2) as similarity_score,
        CASE 
            WHEN jp.fp1 = jp.fp2 THEN true
            ELSE false
        END as likely_duplicate
    FROM job_pairs jp
    WHERE jp.fp1 = jp.fp2 OR 0.80 >= p_similarity_threshold;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- SAMPLE DATA INSERTION FUNCTION
-- =====================================================

CREATE OR REPLACE FUNCTION insert_sample_multi_source_data()
RETURNS VOID AS $$
DECLARE
    sample_job_id UUID := uuid_generate_v4();
    sample_company_id UUID := uuid_generate_v4();
    primary_source_id UUID;
    secondary_source_id UUID;
BEGIN
    -- Insert sample job
    INSERT INTO jobs (job_id, company_id, company_name, title, description, status)
    VALUES (
        sample_job_id, sample_company_id, 'TechCorp Inc',
        'Senior Software Engineer', 'Sample job description...', 'active'
    );
    
    -- Insert primary source (company career page)
    INSERT INTO job_sources (
        job_id, source_type, source_platform, source_name, source_url,
        is_primary_source, title, description
    ) VALUES (
        sample_job_id, 'primary', 'company_careers', 'TechCorp Careers',
        'https://techcorp.com/careers/senior-software-engineer',
        true, 'Senior Software Engineer', 'Detailed job description from company site...'
    ) RETURNING source_id INTO primary_source_id;
    
    -- Insert secondary source (LinkedIn)
    INSERT INTO job_sources (
        job_id, source_type, source_platform, source_name, source_url,
        is_primary_source, title, description
    ) VALUES (
        sample_job_id, 'secondary', 'linkedin', 'LinkedIn Jobs',
        'https://linkedin.com/jobs/view/123456789',
        false, 'Sr Software Engineer', 'Abbreviated job description from LinkedIn...'
    ) RETURNING source_id INTO secondary_source_id;
    
    -- Insert delta analysis
    INSERT INTO job_source_deltas (
        job_id, primary_source_id, secondary_source_id, delta_status,
        overall_similarity_score, title_similarity, description_similarity
    ) VALUES (
        sample_job_id, primary_source_id, secondary_source_id, 'minor_differences',
        0.85, 0.90, 0.80
    );
    
    -- Insert company analytics
    INSERT INTO company_source_analytics (
        company_id, company_name, total_jobs_tracked, jobs_with_multiple_sources,
        platforms_used, hr_quality_score
    ) VALUES (
        sample_company_id, 'TechCorp Inc', 1, 1,
        ARRAY['company_careers', 'linkedin'], 0.85
    );
    
    RAISE NOTICE 'Sample multi-source data inserted successfully';
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTS AND DOCUMENTATION
-- =====================================================

COMMENT ON TABLE job_sources IS 'Tracks all sources where jobs are posted (primary and secondary)';
COMMENT ON TABLE job_source_deltas IS 'Analyzes differences between job descriptions across sources';
COMMENT ON TABLE company_source_analytics IS 'Company-level analytics on source management quality';
COMMENT ON TABLE source_discovery_log IS 'Audit trail of how job sources are discovered and processed';

COMMENT ON COLUMN job_sources.source_type IS 'Primary (company career page) or secondary (job board)';
COMMENT ON COLUMN job_sources.content_fingerprint IS 'SHA-256 hash of combined content for duplicate detection';
COMMENT ON COLUMN job_source_deltas.delta_status IS 'Classification of differences between sources';
COMMENT ON COLUMN company_source_analytics.hr_quality_score IS 'Overall HR quality based on source consistency (0.00-1.00)';
