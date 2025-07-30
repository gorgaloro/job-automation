-- =====================================================
-- ENHANCED CAREER HIGHLIGHTS SCHEMA - GRANULAR RELEVANCE SCORING
-- Individual highlight scoring and dynamic selection for resumes
-- =====================================================

-- =====================================================
-- ENHANCED CAREER HIGHLIGHTS TABLE
-- =====================================================

-- Drop existing career_highlights table and recreate with enhanced structure
DROP TABLE IF EXISTS career_highlights CASCADE;

CREATE TABLE career_highlights (
    highlight_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    
    -- Highlight Core Information
    title VARCHAR(200) NOT NULL,
    organization VARCHAR(200),
    timeframe VARCHAR(100),
    description TEXT NOT NULL,
    
    -- Detailed Context
    project_duration VARCHAR(50), -- "4 weeks", "2 years", "ongoing"
    team_size INTEGER, -- number of people involved
    budget_involved BIGINT, -- dollar amount if applicable
    users_impacted INTEGER, -- number of users/stakeholders affected
    
    -- Impact Metrics (structured for better querying)
    quantified_impact JSONB, -- {"budget": 6000000000, "users": 35000, "timeline": "24_months", "success_rate": "100%"}
    business_value TEXT, -- narrative description of business impact
    roi_description TEXT, -- return on investment details
    
    -- Categorization & Classification
    highlight_category VARCHAR(50) NOT NULL, -- major_program, technical_innovation, operations_leadership, process_improvement, team_building, cost_savings
    complexity_level VARCHAR(20) NOT NULL, -- junior, mid, senior, executive, enterprise
    leadership_component VARCHAR(30), -- individual_contributor, team_lead, technical_lead, program_manager, director, vp
    innovation_level VARCHAR(20), -- incremental, significant, breakthrough, industry_first
    
    -- Skills & Technologies Demonstrated
    primary_skills_demonstrated TEXT[] NOT NULL, -- main skills showcased
    secondary_skills_demonstrated TEXT[], -- supporting skills
    technologies_used TEXT[], -- specific technologies/platforms
    methodologies_applied TEXT[], -- agile, lean, six_sigma, etc.
    
    -- Industry & Role Context
    industries_relevant TEXT[] NOT NULL, -- healthcare, technology, finance, etc.
    role_types_relevant TEXT[] NOT NULL, -- program_manager, technical_lead, operations_manager, etc.
    company_sizes_relevant TEXT[], -- startup, small, medium, large, enterprise
    company_stages_relevant TEXT[], -- seed, early, growth, mature, public
    
    -- Keywords for Matching (multi-layered)
    primary_keywords TEXT[] NOT NULL, -- core keywords for job matching
    secondary_keywords TEXT[], -- supporting/related keywords
    technical_keywords TEXT[], -- technology-specific terms
    business_keywords TEXT[], -- business/strategy terms
    industry_keywords TEXT[], -- industry-specific terminology
    
    -- Scoring & Weighting Factors
    base_importance_weight DECIMAL(3,2) DEFAULT 1.0, -- base importance (0.1 to 3.0)
    recency_weight DECIMAL(3,2) DEFAULT 1.0, -- weight based on how recent
    uniqueness_score DECIMAL(3,2) DEFAULT 1.0, -- how unique/differentiating
    achievement_magnitude DECIMAL(3,2) DEFAULT 1.0, -- scale of achievement (0.5 to 2.0)
    
    -- Evidence & Validation
    supporting_evidence TEXT[], -- additional proof points or context
    related_projects TEXT[], -- other projects that support this highlight
    external_recognition TEXT[], -- awards, press, testimonials
    measurable_outcomes TEXT[], -- specific measurable results
    
    -- Display & Selection
    is_featured BOOLEAN DEFAULT true, -- include in standard resumes
    is_signature_achievement BOOLEAN DEFAULT false, -- one of top 3 career defining moments
    display_priority INTEGER DEFAULT 0, -- higher number = higher priority
    
    -- Status & Metadata
    highlight_status VARCHAR(20) DEFAULT 'active', -- active, archived, draft
    last_updated_evidence DATE, -- when supporting evidence was last refreshed
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- CAREER HIGHLIGHT COMPONENTS (SUB-ACHIEVEMENTS)
-- =====================================================

-- Break down complex highlights into component achievements
CREATE TABLE highlight_components (
    component_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    highlight_id UUID NOT NULL REFERENCES career_highlights(highlight_id) ON DELETE CASCADE,
    
    -- Component Details
    component_title VARCHAR(200) NOT NULL,
    component_description TEXT NOT NULL,
    component_type VARCHAR(30) NOT NULL, -- leadership, technical, process, financial, strategic
    
    -- Component-specific Impact
    component_metrics JSONB, -- specific metrics for this component
    component_skills TEXT[] NOT NULL, -- skills demonstrated in this component
    component_keywords TEXT[] NOT NULL, -- keywords specific to this component
    
    -- Weighting within the highlight
    component_weight DECIMAL(3,2) DEFAULT 1.0, -- importance within the parent highlight
    display_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- JOB-HIGHLIGHT RELEVANCE SCORING
-- =====================================================

CREATE TABLE job_highlight_relevance (
    relevance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    highlight_id UUID NOT NULL REFERENCES career_highlights(highlight_id) ON DELETE CASCADE,
    
    -- Multi-dimensional Relevance Scores
    keyword_relevance_score DECIMAL(4,3) NOT NULL, -- 0.000 to 1.000 - keyword alignment
    skill_relevance_score DECIMAL(4,3) NOT NULL, -- skills alignment with job requirements
    industry_relevance_score DECIMAL(4,3) NOT NULL, -- industry alignment
    role_relevance_score DECIMAL(4,3) NOT NULL, -- role type alignment
    complexity_relevance_score DECIMAL(4,3) NOT NULL, -- complexity level match
    impact_relevance_score DECIMAL(4,3) NOT NULL, -- achievement magnitude relevance
    
    -- Composite Scores
    overall_relevance_score DECIMAL(4,3) NOT NULL, -- weighted combination of above
    weighted_importance DECIMAL(4,3) NOT NULL, -- relevance * importance weight
    final_selection_score DECIMAL(4,3) NOT NULL, -- final score for ranking
    
    -- Match Context & Reasoning
    matched_job_requirements TEXT[], -- specific job requirements this highlight addresses
    matched_keywords TEXT[] NOT NULL, -- keywords that created the match
    matched_skills TEXT[] NOT NULL, -- skills that aligned
    relevance_reasoning TEXT, -- AI explanation of why this highlight is relevant
    match_confidence DECIMAL(4,3) NOT NULL, -- confidence in the relevance assessment
    
    -- Match Classification
    relevance_type VARCHAR(30) NOT NULL, -- direct_experience, transferable_skill, leadership_example, technical_achievement, scale_demonstration
    requirement_alignment VARCHAR(30), -- required_experience, preferred_experience, nice_to_have, leadership_requirement
    
    -- Component-level Matches (if applicable)
    relevant_components UUID[], -- array of component_ids that are particularly relevant
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- DYNAMIC HIGHLIGHT SELECTION FOR RESUMES
-- =====================================================

CREATE TABLE resume_highlight_selections (
    selection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID NOT NULL REFERENCES generated_resumes(resume_id) ON DELETE CASCADE,
    highlight_id UUID NOT NULL REFERENCES career_highlights(highlight_id) ON DELETE CASCADE,
    
    -- Selection Metadata
    selection_rank INTEGER NOT NULL, -- rank of this highlight for this job (1 = highest)
    selection_score DECIMAL(4,3) NOT NULL, -- final score used for selection
    selection_reason VARCHAR(100), -- why this highlight was selected
    
    -- Display Configuration
    display_order INTEGER NOT NULL, -- order in the highlights section
    is_primary_highlight BOOLEAN DEFAULT false, -- one of the top highlights
    display_format VARCHAR(30) DEFAULT 'full', -- full, summary, bullet_point
    
    -- Selected Components (if highlight has components)
    selected_components UUID[], -- which components to include
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- FUNCTIONS FOR HIGHLIGHT RELEVANCE & SELECTION
-- =====================================================

-- Function to get top matching highlights for a specific job
CREATE OR REPLACE FUNCTION get_top_matching_highlights(
    p_profile_id UUID,
    p_job_id UUID,
    p_max_highlights INTEGER DEFAULT 3
)
RETURNS TABLE (
    highlight_id UUID,
    title VARCHAR,
    description TEXT,
    overall_relevance_score DECIMAL,
    matched_keywords TEXT[],
    highlight_category VARCHAR,
    quantified_impact JSONB,
    selection_reasoning TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ch.highlight_id,
        ch.title,
        ch.description,
        jhr.overall_relevance_score,
        jhr.matched_keywords,
        ch.highlight_category,
        ch.quantified_impact,
        jhr.relevance_reasoning as selection_reasoning
    FROM career_highlights ch
    JOIN job_highlight_relevance jhr ON ch.highlight_id = jhr.highlight_id
    WHERE jhr.profile_id = p_profile_id 
    AND jhr.job_id = p_job_id
    AND ch.is_featured = true
    ORDER BY jhr.final_selection_score DESC, ch.display_priority DESC
    LIMIT p_max_highlights;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate highlight relevance score for a job
CREATE OR REPLACE FUNCTION calculate_highlight_job_relevance(
    p_highlight_id UUID,
    p_job_id UUID,
    p_profile_id UUID
)
RETURNS DECIMAL AS $$
DECLARE
    keyword_score DECIMAL := 0;
    skill_score DECIMAL := 0;
    industry_score DECIMAL := 0;
    role_score DECIMAL := 0;
    complexity_score DECIMAL := 0;
    impact_score DECIMAL := 0;
    final_score DECIMAL := 0;
    highlight_weight DECIMAL := 1.0;
BEGIN
    -- Get highlight importance weight
    SELECT base_importance_weight * recency_weight * uniqueness_score * achievement_magnitude
    INTO highlight_weight
    FROM career_highlights
    WHERE highlight_id = p_highlight_id;
    
    -- Calculate keyword relevance (30% weight)
    -- This would be implemented with more sophisticated text matching
    keyword_score := 0.8; -- Placeholder - would use actual keyword matching algorithm
    
    -- Calculate skill relevance (25% weight)
    skill_score := 0.85; -- Placeholder - would compare skills_demonstrated with job requirements
    
    -- Calculate industry relevance (15% weight)
    industry_score := 0.9; -- Placeholder - would match industries_relevant with job industry
    
    -- Calculate role relevance (15% weight)
    role_score := 0.8; -- Placeholder - would match role_types_relevant with job role
    
    -- Calculate complexity relevance (10% weight)
    complexity_score := 0.9; -- Placeholder - would match complexity_level with job seniority
    
    -- Calculate impact relevance (5% weight)
    impact_score := 0.95; -- Placeholder - would assess achievement magnitude vs job scope
    
    -- Calculate weighted final score
    final_score := (
        (keyword_score * 0.30) +
        (skill_score * 0.25) +
        (industry_score * 0.15) +
        (role_score * 0.15) +
        (complexity_score * 0.10) +
        (impact_score * 0.05)
    ) * highlight_weight;
    
    -- Cap at 1.0
    IF final_score > 1.0 THEN
        final_score := 1.0;
    END IF;
    
    RETURN final_score;
END;
$$ LANGUAGE plpgsql;

-- Function to get optimized highlights for resume generation
CREATE OR REPLACE FUNCTION generate_optimized_highlights_for_resume(
    p_profile_id UUID,
    p_job_id UUID,
    p_max_highlights INTEGER DEFAULT 3,
    p_include_components BOOLEAN DEFAULT false
)
RETURNS TABLE (
    highlight_id UUID,
    title VARCHAR,
    description TEXT,
    timeframe VARCHAR,
    organization VARCHAR,
    quantified_impact JSONB,
    relevance_score DECIMAL,
    matched_requirements TEXT[],
    selected_components JSONB -- if p_include_components is true
) AS $$
BEGIN
    RETURN QUERY
    WITH ranked_highlights AS (
        SELECT 
            ch.highlight_id,
            ch.title,
            ch.description,
            ch.timeframe,
            ch.organization,
            ch.quantified_impact,
            jhr.final_selection_score,
            jhr.matched_job_requirements,
            ROW_NUMBER() OVER (ORDER BY jhr.final_selection_score DESC) as rank
        FROM career_highlights ch
        JOIN job_highlight_relevance jhr ON ch.highlight_id = jhr.highlight_id
        WHERE jhr.profile_id = p_profile_id 
        AND jhr.job_id = p_job_id
        AND ch.is_featured = true
    ),
    component_data AS (
        SELECT 
            hc.highlight_id,
            jsonb_agg(
                jsonb_build_object(
                    'component_id', hc.component_id,
                    'title', hc.component_title,
                    'description', hc.component_description,
                    'type', hc.component_type,
                    'metrics', hc.component_metrics
                )
                ORDER BY hc.display_order
            ) as components
        FROM highlight_components hc
        WHERE p_include_components = true
        GROUP BY hc.highlight_id
    )
    SELECT 
        rh.highlight_id,
        rh.title,
        rh.description,
        rh.timeframe,
        rh.organization,
        rh.quantified_impact,
        rh.final_selection_score,
        rh.matched_job_requirements,
        COALESCE(cd.components, '[]'::jsonb) as selected_components
    FROM ranked_highlights rh
    LEFT JOIN component_data cd ON rh.highlight_id = cd.highlight_id
    WHERE rh.rank <= p_max_highlights
    ORDER BY rh.final_selection_score DESC;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Career highlights indexes
CREATE INDEX idx_career_highlights_profile_id ON career_highlights(profile_id);
CREATE INDEX idx_career_highlights_category ON career_highlights(highlight_category);
CREATE INDEX idx_career_highlights_keywords ON career_highlights USING GIN(primary_keywords);
CREATE INDEX idx_career_highlights_skills ON career_highlights USING GIN(primary_skills_demonstrated);
CREATE INDEX idx_career_highlights_industries ON career_highlights USING GIN(industries_relevant);
CREATE INDEX idx_career_highlights_featured ON career_highlights(is_featured);
CREATE INDEX idx_career_highlights_signature ON career_highlights(is_signature_achievement);
CREATE INDEX idx_career_highlights_priority ON career_highlights(display_priority DESC);

-- Highlight components indexes
CREATE INDEX idx_highlight_components_highlight_id ON highlight_components(highlight_id);
CREATE INDEX idx_highlight_components_type ON highlight_components(component_type);
CREATE INDEX idx_highlight_components_order ON highlight_components(highlight_id, display_order);

-- Relevance scoring indexes
CREATE INDEX idx_job_highlight_relevance_profile_job ON job_highlight_relevance(profile_id, job_id);
CREATE INDEX idx_job_highlight_relevance_highlight_id ON job_highlight_relevance(highlight_id);
CREATE INDEX idx_job_highlight_relevance_overall_score ON job_highlight_relevance(overall_relevance_score DESC);
CREATE INDEX idx_job_highlight_relevance_final_score ON job_highlight_relevance(final_selection_score DESC);
CREATE INDEX idx_job_highlight_relevance_weighted ON job_highlight_relevance(weighted_importance DESC);

-- Resume selection indexes
CREATE INDEX idx_resume_highlight_selections_resume_id ON resume_highlight_selections(resume_id);
CREATE INDEX idx_resume_highlight_selections_highlight_id ON resume_highlight_selections(highlight_id);
CREATE INDEX idx_resume_highlight_selections_rank ON resume_highlight_selections(selection_rank);

-- =====================================================
-- ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE career_highlights ENABLE ROW LEVEL SECURITY;
ALTER TABLE highlight_components ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_highlight_relevance ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_highlight_selections ENABLE ROW LEVEL SECURITY;

-- Policies for career highlights
CREATE POLICY "Users can manage own highlights" ON career_highlights FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own highlight components" ON highlight_components FOR ALL USING (
    highlight_id IN (
        SELECT highlight_id FROM career_highlights 
        WHERE profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
    )
);

CREATE POLICY "Users can view own highlight relevance" ON job_highlight_relevance FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own highlight selections" ON resume_highlight_selections FOR ALL USING (
    resume_id IN (
        SELECT resume_id FROM generated_resumes 
        WHERE profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
    )
);

-- =====================================================
-- SAMPLE DATA STRUCTURE FOR ALLEN WALKER'S HIGHLIGHTS
-- =====================================================

-- Example: How Allen's career highlights would be structured

/*
-- AI Platform Development Highlight (NEW - highest importance)
INSERT INTO career_highlights (
    profile_id, title, organization, timeframe, description,
    highlight_category, complexity_level, leadership_component, innovation_level,
    primary_skills_demonstrated, technologies_used,
    industries_relevant, role_types_relevant,
    primary_keywords, technical_keywords, business_keywords,
    base_importance_weight, recency_weight, uniqueness_score, achievement_magnitude,
    quantified_impact, is_signature_achievement
) VALUES (
    'allen_profile_id',
    'AI-Powered Job Search Automation Platform',
    'Independent Innovation Project',
    'July 2025 (4 weeks)',
    'Independently conceived, architected, and deployed a comprehensive AI-powered job search automation platform from concept to production. Integrated 10+ complex systems including OpenAI GPT-4, multiple job board APIs, personal brand profiling, and automated workflow orchestration.',
    'technical_innovation',
    'enterprise',
    'technical_lead',
    'breakthrough',
    ARRAY['AI/ML Integration', 'Full-Stack Development', 'System Architecture', 'Cloud Deployment', 'Technical Leadership'],
    ARRAY['Python', 'FastAPI', 'OpenAI GPT-4', 'PostgreSQL', 'Supabase', 'Railway', 'HTML/CSS/JS', 'Git', 'Docker'],
    ARRAY['AI/ML & Automation', 'Technology', 'SaaS', 'Developer Tools'],
    ARRAY['Technical Program Manager', 'AI Platform Manager', 'Senior Program Manager', 'Technical Lead'],
    ARRAY['ai', 'platform', 'automation', 'integration', 'development', 'deployment', 'architecture'],
    ARRAY['python', 'fastapi', 'openai', 'gpt-4', 'postgresql', 'railway', 'docker'],
    ARRAY['innovation', 'leadership', 'delivery', 'execution', 'strategy'],
    2.0, -- highest base importance
    2.0, -- maximum recency weight (brand new)
    1.8, -- very unique achievement
    1.9, -- high achievement magnitude
    '{"systems_integrated": 10, "apis_connected": 6, "lines_of_code": 15000, "uptime": "99.9%", "development_timeline": "4_weeks", "match_accuracy": "87%"}',
    true -- signature achievement
);

-- $6B Epic Program Highlight
INSERT INTO career_highlights (
    profile_id, title, organization, timeframe, description,
    highlight_category, complexity_level, leadership_component, innovation_level,
    primary_skills_demonstrated, technologies_used,
    industries_relevant, role_types_relevant,
    primary_keywords, business_keywords,
    base_importance_weight, achievement_magnitude,
    quantified_impact, is_signature_achievement
) VALUES (
    'allen_profile_id',
    '$6B Epic Program Leadership',
    'Healthcare System Implementation',
    '2022-2024',
    'Directed a $6B Epic program for 35,000+ users—drove timelines, delivered change, and met go-live with zero critical errors.',
    'major_program',
    'enterprise',
    'program_manager',
    'significant',
    ARRAY['Program Management', 'Epic Systems', 'Change Management', 'Leadership', 'Healthcare IT'],
    ARRAY['Epic Systems', 'Healthcare IT', 'Project Management Tools'],
    ARRAY['Healthcare', 'Healthcare Technology', 'Enterprise Software'],
    ARRAY['Program Manager', 'Healthcare Program Manager', 'Implementation Manager', 'Director'],
    ARRAY['epic', 'program', 'implementation', 'healthcare', 'leadership', 'change management'],
    ARRAY['program management', 'leadership', 'delivery', 'execution', 'transformation'],
    1.8, -- very high importance
    2.0, -- maximum achievement magnitude
    '{"budget": 6000000000, "users_affected": 35000, "timeline": "24_months", "success_rate": "100%", "critical_errors": 0}',
    true -- signature achievement
);

-- Add components for the AI Platform highlight
INSERT INTO highlight_components (highlight_id, component_title, component_description, component_type, component_skills, component_keywords, component_weight) VALUES
('ai_platform_highlight_id', 'System Architecture & Design', 'Architected scalable AI platform with 10 integrated systems and microservices architecture', 'technical', ARRAY['System Architecture', 'AI/ML Integration', 'Microservices'], ARRAY['architecture', 'design', 'scalability'], 1.5),
('ai_platform_highlight_id', 'Production Deployment', 'Successfully deployed to Railway cloud platform achieving 99.9% uptime', 'technical', ARRAY['Cloud Deployment', 'DevOps', 'Production Systems'], ARRAY['deployment', 'cloud', 'production', 'uptime'], 1.3),
('ai_platform_highlight_id', 'API Integration Leadership', 'Integrated 6 job board APIs with custom query optimization and error handling', 'technical', ARRAY['API Development', 'Integration', 'Technical Leadership'], ARRAY['api', 'integration', 'optimization'], 1.2);
*/
