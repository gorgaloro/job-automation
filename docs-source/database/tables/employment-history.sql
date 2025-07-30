-- =====================================================
-- ENHANCED EMPLOYMENT SCHEMA - BULLET POINT OPTIMIZATION
-- Granular scoring at the individual bullet point level
-- =====================================================

-- =====================================================
-- ENHANCED EMPLOYMENT HISTORY WITH BULLET POINTS
-- =====================================================

-- Drop existing employment_history table and recreate with bullet point structure
DROP TABLE IF EXISTS employment_history CASCADE;

CREATE TABLE employment_history (
    employment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    
    -- Basic Job Information
    company VARCHAR(200) NOT NULL,
    job_title VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT false,
    
    -- Job Context
    location VARCHAR(100),
    employment_type VARCHAR(20), -- full_time, part_time, contract, consultant
    department VARCHAR(100),
    reporting_manager VARCHAR(100),
    team_size_managed INTEGER,
    budget_managed BIGINT,
    
    -- High-level Job Summary
    job_summary TEXT, -- 1-2 sentence overview of the role
    key_technologies TEXT[], -- primary technologies used in this role
    primary_industries TEXT[], -- industries served in this role
    
    -- Metadata
    display_order INTEGER DEFAULT 0, -- for resume ordering
    is_featured BOOLEAN DEFAULT true, -- include in standard resumes
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDIVIDUAL BULLET POINTS TABLE
-- =====================================================

CREATE TABLE employment_bullet_points (
    bullet_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employment_id UUID NOT NULL REFERENCES employment_history(employment_id) ON DELETE CASCADE,
    
    -- Bullet Point Content
    bullet_text TEXT NOT NULL, -- the actual bullet point content
    bullet_category VARCHAR(50), -- responsibility, achievement, leadership, technical, impact
    
    -- Impact & Metrics
    has_quantified_impact BOOLEAN DEFAULT false,
    impact_metrics JSONB, -- e.g., {"percentage_improvement": 25, "dollar_amount": 500000, "users_affected": 1000}
    impact_description TEXT, -- narrative description of impact
    
    -- Skills & Technologies Demonstrated
    skills_demonstrated TEXT[] NOT NULL, -- skills showcased in this bullet
    technologies_used TEXT[], -- specific technologies mentioned
    methodologies_used TEXT[], -- agile, waterfall, lean, etc.
    
    -- Categorization for Matching
    bullet_type VARCHAR(30) NOT NULL, -- achievement, responsibility, leadership, technical_delivery, process_improvement, team_building
    complexity_level VARCHAR(20), -- junior, mid, senior, executive
    leadership_component BOOLEAN DEFAULT false,
    cross_functional_component BOOLEAN DEFAULT false,
    
    -- Keywords for Job Matching
    primary_keywords TEXT[] NOT NULL, -- main keywords for matching
    secondary_keywords TEXT[], -- supporting/related keywords
    industry_keywords TEXT[], -- industry-specific terms
    role_keywords TEXT[], -- role-specific terms
    
    -- Scoring & Weighting
    base_importance_weight DECIMAL(3,2) DEFAULT 1.0, -- base importance of this bullet (0.1 to 2.0)
    recency_weight DECIMAL(3,2) DEFAULT 1.0, -- weight based on how recent this experience is
    uniqueness_score DECIMAL(3,2) DEFAULT 1.0, -- how unique/differentiating this bullet is
    
    -- Display & Ordering
    display_order INTEGER DEFAULT 0, -- order within the job
    is_featured BOOLEAN DEFAULT true, -- include in standard resumes
    is_quantified BOOLEAN DEFAULT false, -- has specific numbers/metrics
    
    -- Evidence & Validation
    supporting_evidence TEXT, -- additional context or proof points
    related_projects TEXT[], -- projects that support this bullet
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- JOB BULLET POINT MATCHING & SCORING
-- =====================================================

CREATE TABLE job_bullet_matches (
    match_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    bullet_id UUID NOT NULL REFERENCES employment_bullet_points(bullet_id) ON DELETE CASCADE,
    employment_id UUID NOT NULL REFERENCES employment_history(employment_id) ON DELETE CASCADE,
    
    -- Matching Scores
    relevance_score DECIMAL(4,3) NOT NULL, -- 0.000 to 1.000 - how relevant to job requirements
    keyword_match_score DECIMAL(4,3) NOT NULL, -- keyword alignment score
    skill_match_score DECIMAL(4,3) NOT NULL, -- skills alignment score
    impact_score DECIMAL(4,3) NOT NULL, -- impact/achievement relevance
    
    -- Composite Scores
    overall_match_score DECIMAL(4,3) NOT NULL, -- weighted combination of above scores
    weighted_importance DECIMAL(4,3) NOT NULL, -- match score * importance weight
    
    -- Match Context
    matched_job_requirements TEXT[], -- specific job requirements this bullet addresses
    matched_keywords TEXT[] NOT NULL, -- keywords that matched
    match_reasoning TEXT, -- AI explanation of why this bullet is relevant
    match_confidence DECIMAL(4,3) NOT NULL, -- confidence in the match
    
    -- Match Type Classification
    match_type VARCHAR(30) NOT NULL, -- exact_match, strong_alignment, related_experience, transferable_skill
    requirement_type VARCHAR(30), -- required_skill, preferred_skill, responsibility, qualification
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- DYNAMIC RESUME BULLET SELECTION
-- =====================================================

CREATE TABLE resume_bullet_selections (
    selection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID NOT NULL REFERENCES generated_resumes(resume_id) ON DELETE CASCADE,
    employment_id UUID NOT NULL REFERENCES employment_history(employment_id) ON DELETE CASCADE,
    bullet_id UUID NOT NULL REFERENCES employment_bullet_points(bullet_id) ON DELETE CASCADE,
    
    -- Selection Metadata
    selection_rank INTEGER NOT NULL, -- rank of this bullet for this job (1 = highest)
    selection_score DECIMAL(4,3) NOT NULL, -- final score used for selection
    inclusion_reason VARCHAR(100), -- why this bullet was selected
    
    -- Display Information
    display_order INTEGER NOT NULL, -- order within the job section
    is_primary_bullet BOOLEAN DEFAULT false, -- one of the top bullets for this job
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- ENHANCED FUNCTIONS FOR BULLET-LEVEL OPTIMIZATION
-- =====================================================

-- Function to get top matching bullet points for a specific job at a specific company
CREATE OR REPLACE FUNCTION get_top_matching_bullets_for_job(
    p_profile_id UUID,
    p_job_id UUID,
    p_employment_id UUID,
    p_max_bullets INTEGER DEFAULT 5
)
RETURNS TABLE (
    bullet_id UUID,
    bullet_text TEXT,
    overall_match_score DECIMAL,
    matched_keywords TEXT[],
    bullet_category VARCHAR,
    impact_metrics JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ebp.bullet_id,
        ebp.bullet_text,
        jbm.overall_match_score,
        jbm.matched_keywords,
        ebp.bullet_category,
        ebp.impact_metrics
    FROM employment_bullet_points ebp
    JOIN job_bullet_matches jbm ON ebp.bullet_id = jbm.bullet_id
    WHERE jbm.profile_id = p_profile_id 
    AND jbm.job_id = p_job_id
    AND ebp.employment_id = p_employment_id
    AND ebp.is_featured = true
    ORDER BY jbm.weighted_importance DESC, jbm.overall_match_score DESC
    LIMIT p_max_bullets;
END;
$$ LANGUAGE plpgsql;

-- Function to get optimized resume structure with selected bullets
CREATE OR REPLACE FUNCTION generate_optimized_resume_structure(
    p_profile_id UUID,
    p_job_id UUID,
    p_max_bullets_per_job INTEGER DEFAULT 5
)
RETURNS TABLE (
    employment_id UUID,
    company VARCHAR,
    job_title VARCHAR,
    start_date DATE,
    end_date DATE,
    selected_bullets JSONB -- array of selected bullet points with scores
) AS $$
BEGIN
    RETURN QUERY
    WITH ranked_bullets AS (
        SELECT 
            eh.employment_id,
            eh.company,
            eh.job_title,
            eh.start_date,
            eh.end_date,
            jsonb_agg(
                jsonb_build_object(
                    'bullet_id', ebp.bullet_id,
                    'bullet_text', ebp.bullet_text,
                    'match_score', jbm.overall_match_score,
                    'matched_keywords', jbm.matched_keywords,
                    'category', ebp.bullet_category,
                    'impact_metrics', ebp.impact_metrics,
                    'rank', ROW_NUMBER() OVER (PARTITION BY eh.employment_id ORDER BY jbm.weighted_importance DESC)
                )
                ORDER BY jbm.weighted_importance DESC
            ) FILTER (WHERE rn <= p_max_bullets_per_job) as selected_bullets
        FROM employment_history eh
        JOIN employment_bullet_points ebp ON eh.employment_id = ebp.employment_id
        JOIN job_bullet_matches jbm ON ebp.bullet_id = jbm.bullet_id
        JOIN (
            SELECT 
                ebp2.bullet_id,
                ROW_NUMBER() OVER (PARTITION BY ebp2.employment_id ORDER BY jbm2.weighted_importance DESC) as rn
            FROM employment_bullet_points ebp2
            JOIN job_bullet_matches jbm2 ON ebp2.bullet_id = jbm2.bullet_id
            WHERE jbm2.profile_id = p_profile_id AND jbm2.job_id = p_job_id
        ) ranked ON ebp.bullet_id = ranked.bullet_id
        WHERE eh.profile_id = p_profile_id
        AND jbm.job_id = p_job_id
        AND ebp.is_featured = true
        AND ranked.rn <= p_max_bullets_per_job
        GROUP BY eh.employment_id, eh.company, eh.job_title, eh.start_date, eh.end_date
        ORDER BY eh.start_date DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate employment relevance score based on bullet matches
CREATE OR REPLACE FUNCTION calculate_employment_relevance_score(
    p_employment_id UUID,
    p_job_id UUID
)
RETURNS DECIMAL AS $$
DECLARE
    avg_bullet_score DECIMAL;
    bullet_count INTEGER;
    relevance_score DECIMAL;
BEGIN
    -- Get average score and count of matching bullets for this employment
    SELECT 
        COALESCE(AVG(overall_match_score), 0),
        COUNT(*)
    INTO avg_bullet_score, bullet_count
    FROM job_bullet_matches jbm
    JOIN employment_bullet_points ebp ON jbm.bullet_id = ebp.bullet_id
    WHERE ebp.employment_id = p_employment_id 
    AND jbm.job_id = p_job_id;
    
    -- Calculate relevance score (average score weighted by number of matching bullets)
    -- More matching bullets = higher relevance
    relevance_score := avg_bullet_score * (1 + (bullet_count * 0.1));
    
    -- Cap at 1.0
    IF relevance_score > 1.0 THEN
        relevance_score := 1.0;
    END IF;
    
    RETURN relevance_score;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INDEXES FOR BULLET-LEVEL PERFORMANCE
-- =====================================================

-- Employment and bullet point indexes
CREATE INDEX idx_employment_history_profile_id ON employment_history(profile_id);
CREATE INDEX idx_employment_history_dates ON employment_history(start_date DESC, end_date DESC);
CREATE INDEX idx_employment_history_featured ON employment_history(is_featured);

CREATE INDEX idx_employment_bullets_employment_id ON employment_bullet_points(employment_id);
CREATE INDEX idx_employment_bullets_keywords ON employment_bullet_points USING GIN(primary_keywords);
CREATE INDEX idx_employment_bullets_skills ON employment_bullet_points USING GIN(skills_demonstrated);
CREATE INDEX idx_employment_bullets_category ON employment_bullet_points(bullet_category);
CREATE INDEX idx_employment_bullets_type ON employment_bullet_points(bullet_type);
CREATE INDEX idx_employment_bullets_featured ON employment_bullet_points(is_featured);
CREATE INDEX idx_employment_bullets_order ON employment_bullet_points(employment_id, display_order);

-- Bullet matching indexes
CREATE INDEX idx_job_bullet_matches_profile_job ON job_bullet_matches(profile_id, job_id);
CREATE INDEX idx_job_bullet_matches_bullet_id ON job_bullet_matches(bullet_id);
CREATE INDEX idx_job_bullet_matches_employment_id ON job_bullet_matches(employment_id);
CREATE INDEX idx_job_bullet_matches_overall_score ON job_bullet_matches(overall_match_score DESC);
CREATE INDEX idx_job_bullet_matches_weighted_importance ON job_bullet_matches(weighted_importance DESC);

-- Resume selection indexes
CREATE INDEX idx_resume_bullet_selections_resume_id ON resume_bullet_selections(resume_id);
CREATE INDEX idx_resume_bullet_selections_employment_id ON resume_bullet_selections(employment_id);
CREATE INDEX idx_resume_bullet_selections_rank ON resume_bullet_selections(selection_rank);

-- =====================================================
-- ROW LEVEL SECURITY FOR NEW TABLES
-- =====================================================

ALTER TABLE employment_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE employment_bullet_points ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_bullet_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_bullet_selections ENABLE ROW LEVEL SECURITY;

-- Policies for employment data
CREATE POLICY "Users can manage own employment history" ON employment_history FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own bullet points" ON employment_bullet_points FOR ALL USING (
    employment_id IN (
        SELECT employment_id FROM employment_history 
        WHERE profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
    )
);

CREATE POLICY "Users can view own bullet matches" ON job_bullet_matches FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own resume selections" ON resume_bullet_selections FOR ALL USING (
    resume_id IN (
        SELECT resume_id FROM generated_resumes 
        WHERE profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
    )
);

-- =====================================================
-- SAMPLE DATA STRUCTURE FOR ALLEN WALKER
-- =====================================================

-- Example: How Allen's employment data would be structured

/*
-- Employment Record
INSERT INTO employment_history (profile_id, company, job_title, start_date, is_current, location, employment_type, job_summary, key_technologies) VALUES
('allen_profile_id', 'Current Healthcare System', 'Senior Program Manager & AI Innovation Lead', '2022-01-01', true, 'San Francisco, CA', 'full_time', 
'Lead Epic implementation programs and drive AI-powered automation initiatives across enterprise healthcare systems.', 
ARRAY['Epic Systems', 'Salesforce', 'Python', 'OpenAI', 'FastAPI']);

-- Bullet Points for this job
INSERT INTO employment_bullet_points (employment_id, bullet_text, bullet_category, skills_demonstrated, primary_keywords, bullet_type, base_importance_weight) VALUES

-- AI Platform Development (NEW - highest weight)
('employment_id', 'Architected and deployed comprehensive AI-powered job search automation platform with 10 integrated systems, 6 API integrations, and 99.9% uptime in 4 weeks', 'achievement', 
ARRAY['AI/ML Integration', 'Python Development', 'System Architecture', 'Cloud Deployment'], 
ARRAY['ai', 'platform', 'architecture', 'deployment', 'automation', 'integration'], 'technical_delivery', 2.0),

-- Epic Program Leadership
('employment_id', 'Directed $6B Epic program implementation for 35,000+ users, achieving zero critical errors at go-live', 'achievement',
ARRAY['Program Management', 'Epic Systems', 'Change Management', 'Leadership'],
ARRAY['epic', 'program', 'implementation', 'leadership', 'healthcare'], 'leadership', 1.8),

-- Technical Innovation
('employment_id', 'Integrated OpenAI GPT-4 for automated resume optimization and job matching with 87% compatibility accuracy', 'achievement',
ARRAY['AI/ML Integration', 'OpenAI', 'Automation', 'Technical Leadership'],
ARRAY['openai', 'ai', 'automation', 'integration', 'gpt'], 'technical_delivery', 1.9),

-- And so on for each bullet point...
*/
