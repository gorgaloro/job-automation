-- =====================================================
-- EXECUTIVE SUMMARY SCHEMA - VERSIONED & SCORED SUMMARIES
-- Dynamic, job-tailored summaries with intelligent reuse
-- =====================================================

-- =====================================================
-- EXECUTIVE SUMMARIES TABLE
-- =====================================================

CREATE TABLE executive_summaries (
    summary_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    
    -- Summary Content
    summary_text TEXT NOT NULL,
    summary_length INTEGER NOT NULL, -- character count for quick filtering
    word_count INTEGER NOT NULL, -- word count for analysis
    
    -- Summary Metadata
    summary_type VARCHAR(30) NOT NULL, -- ai_generated, user_edited, hybrid, template_based
    generation_method VARCHAR(30), -- openai_gpt4, claude, user_written, template_customized
    summary_version VARCHAR(10) DEFAULT '1.0', -- version tracking for edits
    
    -- Target Context (what this summary was optimized for)
    target_job_title VARCHAR(200), -- specific job title this was created for
    target_company VARCHAR(200), -- specific company if applicable
    target_industry VARCHAR(100), -- industry focus
    target_role_type VARCHAR(50), -- program_manager, technical_lead, director, etc.
    target_seniority VARCHAR(20), -- junior, mid, senior, executive
    
    -- Content Analysis
    primary_themes TEXT[] NOT NULL, -- main themes/topics covered
    emphasized_skills TEXT[] NOT NULL, -- skills highlighted in this summary
    emphasized_achievements TEXT[], -- specific achievements mentioned
    tone VARCHAR(20) DEFAULT 'professional', -- professional, dynamic, technical, executive
    
    -- Keywords & Matching
    primary_keywords TEXT[] NOT NULL, -- main keywords for job matching
    secondary_keywords TEXT[], -- supporting keywords
    technical_keywords TEXT[], -- technology-specific terms
    industry_keywords TEXT[], -- industry-specific terminology
    role_keywords TEXT[], -- role-specific terms
    
    -- Performance Tracking
    usage_count INTEGER DEFAULT 0, -- how many times this summary has been used
    success_rate DECIMAL(3,2) DEFAULT 0.0, -- success rate when used (if trackable)
    last_used_date TIMESTAMP WITH TIME ZONE,
    
    -- Quality Metrics
    ai_quality_score DECIMAL(3,2), -- AI assessment of summary quality (0.0-1.0)
    keyword_density_score DECIMAL(3,2), -- keyword optimization score
    readability_score DECIMAL(3,2), -- readability assessment
    impact_score DECIMAL(3,2), -- assessment of impact/achievement emphasis
    
    -- Versioning & Editing
    parent_summary_id UUID REFERENCES executive_summaries(summary_id), -- if this is an edited version
    is_active BOOLEAN DEFAULT true, -- whether this summary is available for use
    is_template BOOLEAN DEFAULT false, -- whether this can be used as a template
    edit_reason TEXT, -- reason for creating this version (if edited)
    
    -- Status & Metadata
    summary_status VARCHAR(20) DEFAULT 'active', -- active, archived, draft, deprecated
    created_by VARCHAR(20) DEFAULT 'ai', -- ai, user, hybrid
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- JOB-SUMMARY RELEVANCE SCORING
-- =====================================================

CREATE TABLE job_summary_relevance (
    relevance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    summary_id UUID NOT NULL REFERENCES executive_summaries(summary_id) ON DELETE CASCADE,
    
    -- Multi-dimensional Relevance Scores
    keyword_alignment_score DECIMAL(4,3) NOT NULL, -- 0.000 to 1.000 - keyword match with job
    skill_emphasis_score DECIMAL(4,3) NOT NULL, -- how well emphasized skills match job requirements
    industry_alignment_score DECIMAL(4,3) NOT NULL, -- industry terminology alignment
    role_alignment_score DECIMAL(4,3) NOT NULL, -- role type and seniority alignment
    tone_appropriateness_score DECIMAL(4,3) NOT NULL, -- tone match for company/role
    achievement_relevance_score DECIMAL(4,3) NOT NULL, -- relevance of highlighted achievements
    
    -- Composite Scores
    overall_relevance_score DECIMAL(4,3) NOT NULL, -- weighted combination of above scores
    contextual_fit_score DECIMAL(4,3) NOT NULL, -- how well this summary fits the specific context
    final_selection_score DECIMAL(4,3) NOT NULL, -- final score including quality metrics
    
    -- Match Analysis
    matched_job_keywords TEXT[] NOT NULL, -- job keywords found in summary
    matched_requirements TEXT[], -- specific job requirements addressed
    missing_keywords TEXT[], -- important job keywords not in summary
    relevance_reasoning TEXT, -- AI explanation of relevance assessment
    
    -- Match Confidence & Type
    match_confidence DECIMAL(4,3) NOT NULL, -- confidence in the relevance assessment
    match_type VARCHAR(30) NOT NULL, -- exact_match, strong_fit, good_fit, adaptable, needs_editing
    
    -- Improvement Suggestions
    suggested_improvements TEXT[], -- specific suggestions for better alignment
    edit_priority VARCHAR(20), -- high, medium, low, none
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- SUMMARY USAGE TRACKING
-- =====================================================

CREATE TABLE summary_usage_history (
    usage_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    summary_id UUID NOT NULL REFERENCES executive_summaries(summary_id) ON DELETE CASCADE,
    job_id UUID REFERENCES job_postings(job_id) ON DELETE SET NULL,
    resume_id UUID REFERENCES generated_resumes(resume_id) ON DELETE SET NULL,
    
    -- Usage Context
    usage_type VARCHAR(30) NOT NULL, -- resume_generation, application_submission, profile_display
    selection_reason VARCHAR(100), -- why this summary was selected
    selection_score DECIMAL(4,3), -- score that led to selection
    
    -- Performance Tracking (if available)
    application_outcome VARCHAR(30), -- applied, interview_request, rejection, no_response
    response_time_days INTEGER, -- days to get a response (if any)
    feedback_received TEXT, -- any feedback about the summary
    
    -- Usage Metadata
    used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    outcome_updated_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- SUMMARY TEMPLATES & VARIATIONS
-- =====================================================

CREATE TABLE summary_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    
    -- Template Information
    template_name VARCHAR(100) NOT NULL,
    template_description TEXT,
    template_text TEXT NOT NULL, -- template with placeholders like {SKILL}, {ACHIEVEMENT}
    
    -- Template Context
    target_industries TEXT[], -- industries this template works for
    target_roles TEXT[], -- roles this template works for
    target_seniority_levels TEXT[], -- seniority levels appropriate for this template
    
    -- Template Variables
    required_placeholders TEXT[] NOT NULL, -- placeholders that must be filled
    optional_placeholders TEXT[], -- placeholders that can be filled
    
    -- Template Performance
    usage_count INTEGER DEFAULT 0,
    average_score DECIMAL(3,2) DEFAULT 0.0, -- average relevance score when used
    
    -- Template Status
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false, -- default template for certain contexts
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- FUNCTIONS FOR SUMMARY SELECTION & GENERATION
-- =====================================================

-- Function to get the best matching summary for a job
CREATE OR REPLACE FUNCTION get_best_matching_summary(
    p_profile_id UUID,
    p_job_id UUID,
    p_min_score DECIMAL DEFAULT 0.7
)
RETURNS TABLE (
    summary_id UUID,
    summary_text TEXT,
    relevance_score DECIMAL,
    match_type VARCHAR,
    needs_editing BOOLEAN,
    suggested_improvements TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        es.summary_id,
        es.summary_text,
        jsr.final_selection_score,
        jsr.match_type,
        CASE WHEN jsr.edit_priority IN ('high', 'medium') THEN true ELSE false END as needs_editing,
        jsr.suggested_improvements
    FROM executive_summaries es
    JOIN job_summary_relevance jsr ON es.summary_id = jsr.summary_id
    WHERE jsr.profile_id = p_profile_id 
    AND jsr.job_id = p_job_id
    AND es.is_active = true
    AND jsr.final_selection_score >= p_min_score
    ORDER BY jsr.final_selection_score DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function to find similar summaries for reuse/editing
CREATE OR REPLACE FUNCTION find_similar_summaries(
    p_profile_id UUID,
    p_target_keywords TEXT[],
    p_target_industry VARCHAR DEFAULT NULL,
    p_target_role VARCHAR DEFAULT NULL,
    p_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
    summary_id UUID,
    summary_text TEXT,
    similarity_score DECIMAL,
    usage_count INTEGER,
    last_used_date TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        es.summary_id,
        es.summary_text,
        -- Simple similarity calculation (would be enhanced with vector similarity)
        CASE 
            WHEN array_length(es.primary_keywords & p_target_keywords, 1) IS NULL THEN 0.0
            ELSE (array_length(es.primary_keywords & p_target_keywords, 1)::DECIMAL / 
                  GREATEST(array_length(es.primary_keywords, 1), array_length(p_target_keywords, 1)))
        END as similarity_score,
        es.usage_count,
        es.last_used_date
    FROM executive_summaries es
    WHERE es.profile_id = p_profile_id
    AND es.is_active = true
    AND (p_target_industry IS NULL OR es.target_industry = p_target_industry)
    AND (p_target_role IS NULL OR es.target_role_type = p_target_role)
    ORDER BY similarity_score DESC, es.usage_count DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate summary performance metrics
CREATE OR REPLACE FUNCTION calculate_summary_performance(
    p_summary_id UUID
)
RETURNS TABLE (
    total_usage INTEGER,
    success_rate DECIMAL,
    average_response_time DECIMAL,
    most_successful_context VARCHAR
) AS $$
DECLARE
    total_uses INTEGER;
    successful_uses INTEGER;
    avg_response DECIMAL;
    top_context VARCHAR;
BEGIN
    -- Get total usage count
    SELECT COUNT(*) INTO total_uses
    FROM summary_usage_history
    WHERE summary_id = p_summary_id;
    
    -- Get successful usage count (interviews or positive responses)
    SELECT COUNT(*) INTO successful_uses
    FROM summary_usage_history
    WHERE summary_id = p_summary_id
    AND application_outcome IN ('interview_request', 'positive_response');
    
    -- Get average response time
    SELECT AVG(response_time_days) INTO avg_response
    FROM summary_usage_history
    WHERE summary_id = p_summary_id
    AND response_time_days IS NOT NULL;
    
    -- Get most successful usage context
    SELECT usage_type INTO top_context
    FROM summary_usage_history
    WHERE summary_id = p_summary_id
    AND application_outcome IN ('interview_request', 'positive_response')
    GROUP BY usage_type
    ORDER BY COUNT(*) DESC
    LIMIT 1;
    
    RETURN QUERY
    SELECT 
        total_uses,
        CASE WHEN total_uses > 0 THEN (successful_uses::DECIMAL / total_uses) ELSE 0.0 END,
        COALESCE(avg_response, 0.0),
        COALESCE(top_context, 'none');
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Executive summaries indexes
CREATE INDEX idx_executive_summaries_profile_id ON executive_summaries(profile_id);
CREATE INDEX idx_executive_summaries_keywords ON executive_summaries USING GIN(primary_keywords);
CREATE INDEX idx_executive_summaries_skills ON executive_summaries USING GIN(emphasized_skills);
CREATE INDEX idx_executive_summaries_target_role ON executive_summaries(target_role_type);
CREATE INDEX idx_executive_summaries_target_industry ON executive_summaries(target_industry);
CREATE INDEX idx_executive_summaries_active ON executive_summaries(is_active);
CREATE INDEX idx_executive_summaries_usage_count ON executive_summaries(usage_count DESC);
CREATE INDEX idx_executive_summaries_quality ON executive_summaries(ai_quality_score DESC);

-- Relevance scoring indexes
CREATE INDEX idx_job_summary_relevance_profile_job ON job_summary_relevance(profile_id, job_id);
CREATE INDEX idx_job_summary_relevance_summary_id ON job_summary_relevance(summary_id);
CREATE INDEX idx_job_summary_relevance_final_score ON job_summary_relevance(final_selection_score DESC);
CREATE INDEX idx_job_summary_relevance_match_type ON job_summary_relevance(match_type);

-- Usage tracking indexes
CREATE INDEX idx_summary_usage_history_summary_id ON summary_usage_history(summary_id);
CREATE INDEX idx_summary_usage_history_job_id ON summary_usage_history(job_id);
CREATE INDEX idx_summary_usage_history_outcome ON summary_usage_history(application_outcome);
CREATE INDEX idx_summary_usage_history_used_at ON summary_usage_history(used_at DESC);

-- Template indexes
CREATE INDEX idx_summary_templates_profile_id ON summary_templates(profile_id);
CREATE INDEX idx_summary_templates_industries ON summary_templates USING GIN(target_industries);
CREATE INDEX idx_summary_templates_roles ON summary_templates USING GIN(target_roles);
CREATE INDEX idx_summary_templates_active ON summary_templates(is_active);

-- =====================================================
-- ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE executive_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_summary_relevance ENABLE ROW LEVEL SECURITY;
ALTER TABLE summary_usage_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE summary_templates ENABLE ROW LEVEL SECURITY;

-- Policies for executive summaries
CREATE POLICY "Users can manage own summaries" ON executive_summaries FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can view own summary relevance" ON job_summary_relevance FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can view own usage history" ON summary_usage_history FOR ALL USING (
    summary_id IN (
        SELECT summary_id FROM executive_summaries 
        WHERE profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
    )
);

CREATE POLICY "Users can manage own templates" ON summary_templates FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

-- =====================================================
-- SAMPLE DATA STRUCTURE FOR ALLEN WALKER'S SUMMARIES
-- =====================================================

-- Example: How Allen's executive summaries would be structured

/*
-- AI-Focused Executive Summary
INSERT INTO executive_summaries (
    profile_id, summary_text, summary_type, generation_method,
    target_job_title, target_industry, target_role_type, target_seniority,
    primary_themes, emphasized_skills, emphasized_achievements,
    primary_keywords, technical_keywords, industry_keywords,
    ai_quality_score, keyword_density_score, impact_score
) VALUES (
    'allen_profile_id',
    'Senior program leader and AI-powered automation strategist with 15+ years transforming industries through technology innovation. Recently architected and deployed a comprehensive AI job search platform, demonstrating expertise in modern development workflows, AI/ML integration, and end-to-end system delivery. Combines healthcare domain knowledge with cutting-edge technology development—leading $6B+ programs while personally building production-ready AI platforms.',
    'ai_generated',
    'openai_gpt4',
    'AI Platform Manager',
    'AI/ML & Automation',
    'technical_manager',
    'senior',
    ARRAY['AI Innovation', 'Technical Leadership', 'Platform Development', 'Program Management'],
    ARRAY['AI/ML Integration', 'Python Development', 'System Architecture', 'Program Management', 'Technical Leadership'],
    ARRAY['AI Platform Development', '$6B Epic Program', 'Production Deployment'],
    ARRAY['ai', 'platform', 'automation', 'integration', 'technical leadership', 'program management'],
    ARRAY['python', 'fastapi', 'openai', 'gpt-4', 'machine learning', 'cloud deployment'],
    ARRAY['ai', 'automation', 'technology', 'innovation', 'platform'],
    0.95,
    0.88,
    0.92
);

-- Healthcare-Focused Executive Summary
INSERT INTO executive_summaries (
    profile_id, summary_text, summary_type, generation_method,
    target_job_title, target_industry, target_role_type, target_seniority,
    primary_themes, emphasized_skills, emphasized_achievements,
    primary_keywords, industry_keywords,
    ai_quality_score, keyword_density_score, impact_score
) VALUES (
    'allen_profile_id',
    'Senior program management leader with 15+ years driving transformational healthcare initiatives. Directed a $6B Epic implementation for 35,000+ users, achieving zero critical errors at go-live through exceptional change management and cross-functional leadership. Combines deep healthcare domain expertise with innovative technology integration, recently developing AI-powered automation platforms that enhance operational efficiency.',
    'ai_generated',
    'openai_gpt4',
    'Healthcare Program Manager',
    'Healthcare Technology',
    'program_manager',
    'senior',
    ARRAY['Healthcare Leadership', 'Epic Implementation', 'Change Management', 'Program Management'],
    ARRAY['Program Management', 'Epic Systems', 'Change Management', 'Healthcare IT', 'Leadership'],
    ARRAY['$6B Epic Program', 'Healthcare Implementation', 'Change Management'],
    ARRAY['healthcare', 'epic', 'program management', 'implementation', 'change management'],
    ARRAY['healthcare', 'epic', 'implementation', 'clinical', 'patient care'],
    0.93,
    0.85,
    0.96
);

-- General Executive Summary (Template-based)
INSERT INTO executive_summaries (
    profile_id, summary_text, summary_type, generation_method,
    target_role_type, target_seniority,
    primary_themes, emphasized_skills,
    primary_keywords,
    ai_quality_score, is_template
) VALUES (
    'allen_profile_id',
    'Senior program management executive with 15+ years leading large-scale transformational initiatives across healthcare, technology, and operations. Proven track record of delivering complex programs on time and under budget, with expertise in change management, cross-functional leadership, and innovative technology integration. Combines strategic vision with hands-on execution to drive measurable business results.',
    'template_based',
    'user_written',
    'program_manager',
    'senior',
    ARRAY['Program Management', 'Leadership', 'Transformation', 'Execution'],
    ARRAY['Program Management', 'Leadership', 'Change Management', 'Cross-functional Collaboration'],
    ARRAY['program management', 'leadership', 'transformation', 'execution', 'results'],
    0.88,
    true
);
*/
