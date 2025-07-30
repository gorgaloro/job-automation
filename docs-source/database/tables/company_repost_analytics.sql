-- =====================================================
-- COMPANY REPOST ANALYTICS TABLE
-- Tracks company-level job reposting patterns and dysfunction indicators
-- =====================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Company quality rating enumeration
CREATE TYPE company_quality_rating AS ENUM (
    'excellent',
    'good', 
    'fair',
    'poor',
    'avoid'
);

-- =====================================================
-- COMPANY REPOST ANALYTICS TABLE
-- =====================================================

CREATE TABLE company_repost_analytics (
    analytics_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL,
    company_name VARCHAR(300) NOT NULL,
    
    -- Job Posting Statistics
    total_jobs_posted INTEGER DEFAULT 0,
    total_reposts_detected INTEGER DEFAULT 0,
    repost_rate DECIMAL(5,4) DEFAULT 0.0000, -- 0.0000-1.0000
    
    -- Repost Pattern Analysis
    total_repost_clusters INTEGER DEFAULT 0,
    avg_days_between_reposts DECIMAL(8,2) DEFAULT 0.00,
    shortest_repost_interval_days INTEGER,
    longest_repost_interval_days INTEGER,
    
    -- Dysfunction Scoring
    dysfunction_score DECIMAL(3,2) DEFAULT 0.00, -- 0.00-1.00, higher = more problematic
    quality_rating company_quality_rating DEFAULT 'excellent',
    
    -- Red Flags
    red_flags TEXT[], -- Array of identified issues
    red_flag_count INTEGER DEFAULT 0,
    
    -- Analysis Metadata
    last_analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    jobs_analyzed_count INTEGER DEFAULT 0,
    analysis_confidence DECIMAL(3,2) DEFAULT 0.00, -- 0.00-1.00
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- JOB REPOST CLUSTERS TABLE
-- =====================================================

CREATE TABLE job_repost_clusters (
    cluster_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL,
    company_name VARCHAR(300) NOT NULL,
    
    -- Cluster Information
    cluster_identifier VARCHAR(100) NOT NULL, -- Human-readable cluster ID
    original_job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    
    -- Cluster Metrics
    total_reposts INTEGER DEFAULT 0,
    first_posted_date TIMESTAMP WITH TIME ZONE,
    last_repost_date TIMESTAMP WITH TIME ZONE,
    posting_frequency_days DECIMAL(8,2) DEFAULT 0.00,
    cluster_score DECIMAL(3,2) DEFAULT 0.00, -- Dysfunction indicator for this cluster
    
    -- Job Pattern Analysis
    title_pattern VARCHAR(500), -- Normalized title pattern
    description_hash VARCHAR(64), -- Hash of normalized description
    requirements_hash VARCHAR(64), -- Hash of key requirements
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- JOB REPOST RELATIONSHIPS TABLE
-- =====================================================

CREATE TABLE job_repost_relationships (
    relationship_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cluster_id UUID NOT NULL REFERENCES job_repost_clusters(cluster_id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    
    -- Relationship Details
    is_original_job BOOLEAN DEFAULT false,
    repost_order INTEGER, -- 1st repost, 2nd repost, etc.
    
    -- Similarity Metrics
    similarity_score DECIMAL(3,2), -- Overall similarity to original
    title_similarity DECIMAL(3,2),
    description_similarity DECIMAL(3,2),
    requirements_similarity DECIMAL(3,2),
    location_similarity DECIMAL(3,2),
    salary_similarity DECIMAL(3,2),
    
    -- Detection Details
    similarity_factors TEXT[], -- Array of similarity indicators
    confidence_level VARCHAR(20), -- high, medium, low
    detection_method VARCHAR(50), -- automated_similarity, manual_flag
    
    -- Timestamps
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- COMPANY QUALITY ALERTS TABLE
-- =====================================================

CREATE TABLE company_quality_alerts (
    alert_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL,
    company_name VARCHAR(300) NOT NULL,
    
    -- Alert Details
    alert_type VARCHAR(50) NOT NULL, -- high_repost_rate, rapid_reposts, etc.
    alert_severity VARCHAR(20) NOT NULL, -- info, warning, error, critical
    alert_message TEXT NOT NULL,
    
    -- Alert Triggers
    trigger_threshold DECIMAL(5,4), -- Threshold that triggered alert
    current_value DECIMAL(5,4), -- Current value that exceeded threshold
    
    -- Alert Status
    is_active BOOLEAN DEFAULT true,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by VARCHAR(200),
    resolved_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Company analytics indexes
CREATE INDEX idx_company_repost_analytics_company_id ON company_repost_analytics(company_id);
CREATE INDEX idx_company_repost_analytics_quality_rating ON company_repost_analytics(quality_rating);
CREATE INDEX idx_company_repost_analytics_dysfunction_score ON company_repost_analytics(dysfunction_score DESC);
CREATE INDEX idx_company_repost_analytics_repost_rate ON company_repost_analytics(repost_rate DESC);

-- Cluster indexes
CREATE INDEX idx_job_repost_clusters_company_id ON job_repost_clusters(company_id);
CREATE INDEX idx_job_repost_clusters_original_job ON job_repost_clusters(original_job_id);
CREATE INDEX idx_job_repost_clusters_score ON job_repost_clusters(cluster_score DESC);

-- Relationship indexes
CREATE INDEX idx_job_repost_relationships_cluster ON job_repost_relationships(cluster_id);
CREATE INDEX idx_job_repost_relationships_job ON job_repost_relationships(job_id);
CREATE INDEX idx_job_repost_relationships_similarity ON job_repost_relationships(similarity_score DESC);

-- Alert indexes
CREATE INDEX idx_company_quality_alerts_company ON company_quality_alerts(company_id);
CREATE INDEX idx_company_quality_alerts_active ON company_quality_alerts(is_active) WHERE is_active = true;
CREATE INDEX idx_company_quality_alerts_severity ON company_quality_alerts(alert_severity);

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
CREATE TRIGGER update_company_repost_analytics_updated_at 
    BEFORE UPDATE ON company_repost_analytics 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_repost_clusters_updated_at 
    BEFORE UPDATE ON job_repost_clusters 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_quality_alerts_updated_at 
    BEFORE UPDATE ON company_quality_alerts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate company dysfunction score
CREATE OR REPLACE FUNCTION calculate_company_dysfunction_score(
    p_company_id UUID
) RETURNS DECIMAL(3,2) AS $$
DECLARE
    v_repost_rate DECIMAL(5,4);
    v_avg_frequency DECIMAL(8,2);
    v_cluster_count INTEGER;
    v_rapid_reposts INTEGER;
    v_dysfunction_score DECIMAL(3,2) := 0.00;
BEGIN
    -- Get company analytics
    SELECT repost_rate, avg_days_between_reposts, total_repost_clusters
    INTO v_repost_rate, v_avg_frequency, v_cluster_count
    FROM company_repost_analytics
    WHERE company_id = p_company_id;
    
    -- Count rapid reposts (< 14 days)
    SELECT COUNT(*)
    INTO v_rapid_reposts
    FROM job_repost_clusters
    WHERE company_id = p_company_id 
    AND posting_frequency_days > 0 
    AND posting_frequency_days < 14;
    
    -- Calculate dysfunction score
    IF v_repost_rate > 0.3 THEN
        v_dysfunction_score := v_dysfunction_score + 0.4;
    END IF;
    
    IF v_avg_frequency > 0 AND v_avg_frequency < 30 THEN
        v_dysfunction_score := v_dysfunction_score + 0.3;
    END IF;
    
    IF v_cluster_count > 5 THEN
        v_dysfunction_score := v_dysfunction_score + 0.2;
    END IF;
    
    IF v_rapid_reposts > 0 THEN
        v_dysfunction_score := v_dysfunction_score + 0.1;
    END IF;
    
    RETURN LEAST(v_dysfunction_score, 1.00);
END;
$$ LANGUAGE plpgsql;

-- Function to determine quality rating from dysfunction score
CREATE OR REPLACE FUNCTION get_quality_rating_from_score(
    p_dysfunction_score DECIMAL(3,2)
) RETURNS company_quality_rating AS $$
BEGIN
    IF p_dysfunction_score >= 0.7 THEN
        RETURN 'avoid';
    ELSIF p_dysfunction_score >= 0.5 THEN
        RETURN 'poor';
    ELSIF p_dysfunction_score >= 0.3 THEN
        RETURN 'fair';
    ELSIF p_dysfunction_score >= 0.1 THEN
        RETURN 'good';
    ELSE
        RETURN 'excellent';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to generate company quality alerts
CREATE OR REPLACE FUNCTION generate_company_quality_alerts(
    p_company_id UUID
) RETURNS INTEGER AS $$
DECLARE
    v_company_name VARCHAR(300);
    v_repost_rate DECIMAL(5,4);
    v_avg_frequency DECIMAL(8,2);
    v_cluster_count INTEGER;
    v_alerts_created INTEGER := 0;
BEGIN
    -- Get company data
    SELECT company_name, repost_rate, avg_days_between_reposts, total_repost_clusters
    INTO v_company_name, v_repost_rate, v_avg_frequency, v_cluster_count
    FROM company_repost_analytics
    WHERE company_id = p_company_id;
    
    -- High repost rate alert
    IF v_repost_rate > 0.3 THEN
        INSERT INTO company_quality_alerts (
            company_id, company_name, alert_type, alert_severity, alert_message,
            trigger_threshold, current_value
        ) VALUES (
            p_company_id, v_company_name, 'high_repost_rate', 'warning',
            'Company has high job repost rate indicating potential hiring dysfunction',
            0.3, v_repost_rate
        );
        v_alerts_created := v_alerts_created + 1;
    END IF;
    
    -- Frequent reposts alert
    IF v_avg_frequency > 0 AND v_avg_frequency < 30 THEN
        INSERT INTO company_quality_alerts (
            company_id, company_name, alert_type, alert_severity, alert_message,
            trigger_threshold, current_value
        ) VALUES (
            p_company_id, v_company_name, 'frequent_reposts', 'warning',
            'Company frequently reposts jobs within 30 days',
            30.0, v_avg_frequency
        );
        v_alerts_created := v_alerts_created + 1;
    END IF;
    
    -- Multiple clusters alert
    IF v_cluster_count > 5 THEN
        INSERT INTO company_quality_alerts (
            company_id, company_name, alert_type, alert_severity, alert_message,
            trigger_threshold, current_value
        ) VALUES (
            p_company_id, v_company_name, 'multiple_repost_clusters', 'info',
            'Company has multiple job repost clusters across different positions',
            5.0, v_cluster_count
        );
        v_alerts_created := v_alerts_created + 1;
    END IF;
    
    RETURN v_alerts_created;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- SAMPLE DATA INSERTION FUNCTION
-- =====================================================

CREATE OR REPLACE FUNCTION insert_sample_repost_data()
RETURNS VOID AS $$
DECLARE
    sample_company_id UUID := uuid_generate_v4();
    sample_cluster_id UUID := uuid_generate_v4();
    sample_job_id UUID;
BEGIN
    -- Insert sample company analytics
    INSERT INTO company_repost_analytics (
        company_id, company_name, total_jobs_posted, total_reposts_detected,
        repost_rate, total_repost_clusters, avg_days_between_reposts,
        dysfunction_score, quality_rating, red_flags
    ) VALUES (
        sample_company_id, 'TechCorp Inc', 20, 8, 0.4000, 3, 25.50,
        0.65, 'poor', ARRAY['high_repost_rate', 'frequent_reposts']
    );
    
    -- Insert sample job for reference
    INSERT INTO jobs (job_id, company_id, company_name, title, description, status)
    VALUES (
        uuid_generate_v4(), sample_company_id, 'TechCorp Inc',
        'Senior Software Engineer', 'Sample job description...', 'closed'
    ) RETURNING job_id INTO sample_job_id;
    
    -- Insert sample repost cluster
    INSERT INTO job_repost_clusters (
        cluster_id, company_id, company_name, cluster_identifier,
        original_job_id, total_reposts, posting_frequency_days, cluster_score
    ) VALUES (
        sample_cluster_id, sample_company_id, 'TechCorp Inc', 'cluster_senior_engineer',
        sample_job_id, 3, 21.0, 0.7
    );
    
    -- Generate alerts for sample company
    PERFORM generate_company_quality_alerts(sample_company_id);
    
    RAISE NOTICE 'Sample repost data inserted successfully';
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTS AND DOCUMENTATION
-- =====================================================

COMMENT ON TABLE company_repost_analytics IS 'Company-level job reposting analytics and dysfunction scoring';
COMMENT ON TABLE job_repost_clusters IS 'Groups of related job reposts indicating hiring patterns';
COMMENT ON TABLE job_repost_relationships IS 'Individual job relationships within repost clusters';
COMMENT ON TABLE company_quality_alerts IS 'Automated alerts for company hiring dysfunction indicators';

COMMENT ON COLUMN company_repost_analytics.dysfunction_score IS 'Overall company dysfunction score (0.00-1.00, higher = more problematic)';
COMMENT ON COLUMN company_repost_analytics.quality_rating IS 'Overall company quality assessment based on repost patterns';
COMMENT ON COLUMN job_repost_clusters.cluster_score IS 'Dysfunction indicator for this specific repost cluster';
COMMENT ON COLUMN job_repost_relationships.similarity_score IS 'Overall similarity score between jobs (0.00-1.00)';
