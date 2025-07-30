-- =====================================================
-- COMMUNITY LEADERSHIP & NETWORKS SCHEMA
-- Professional-style structure for community involvement, leadership roles, and networking activities
-- =====================================================

-- =====================================================
-- COMMUNITY LEADERSHIP & NETWORKS TABLE
-- =====================================================

CREATE TABLE community_leadership (
    leadership_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    
    -- Core Information (matching Professional Experience structure)
    role VARCHAR(200) NOT NULL, -- leadership position or involvement type
    organization VARCHAR(200) NOT NULL, -- organization, group, or network name
    location VARCHAR(100), -- city, state or "Virtual/Remote"
    start_date DATE NOT NULL,
    end_date DATE, -- NULL for ongoing roles
    
    -- Role Details & Context
    narrative TEXT NOT NULL, -- detailed description of role and contributions
    role_type VARCHAR(50) NOT NULL, -- board_member, volunteer_leader, committee_chair, mentor, advisor, member
    organization_type VARCHAR(50), -- nonprofit, professional_association, community_group, industry_network, alumni_network
    organization_size VARCHAR(30), -- local, regional, national, international
    
    -- Leadership & Impact
    leadership_level VARCHAR(30), -- executive, board, committee, team_lead, member, participant
    team_size INTEGER, -- number of people led or worked with
    budget_responsibility DECIMAL(12,2), -- budget managed (if applicable)
    key_achievements TEXT[], -- specific accomplishments or contributions
    impact_metrics TEXT[], -- quantified results or outcomes
    
    -- Skills & Competencies Demonstrated
    leadership_skills TEXT[] NOT NULL, -- leadership skills demonstrated
    professional_skills TEXT[], -- professional skills applied or developed
    soft_skills TEXT[], -- interpersonal and communication skills
    industry_knowledge TEXT[], -- industry or domain expertise applied
    
    -- Network & Relationships
    network_connections TEXT[], -- types of professionals connected with
    industry_exposure TEXT[], -- industries or sectors engaged with
    geographic_reach VARCHAR(50), -- local, regional, national, international
    networking_value TEXT, -- how this role enhances professional network
    
    -- Professional Relevance
    career_relevance TEXT, -- how this relates to professional goals
    transferable_skills TEXT[], -- skills that transfer to professional roles
    demonstrates_qualities TEXT[], -- personal/professional qualities shown
    industry_alignment TEXT[], -- industries where this experience is valuable
    
    -- Keywords for Matching
    primary_keywords TEXT[] NOT NULL, -- main keywords for job matching
    leadership_keywords TEXT[], -- leadership-specific terms
    industry_keywords TEXT[], -- industry or sector keywords
    skill_keywords TEXT[], -- skill-based keywords
    
    -- Display & Inclusion Control
    default_include BOOLEAN DEFAULT false, -- include by default on resumes
    include_for_leadership_roles BOOLEAN DEFAULT true, -- include for leadership positions
    include_for_nonprofit_roles BOOLEAN DEFAULT false, -- include for nonprofit sector roles
    include_for_community_focused_roles BOOLEAN DEFAULT true, -- include for community-oriented positions
    include_for_network_building BOOLEAN DEFAULT true, -- include to show networking abilities
    
    -- Display Configuration
    display_order INTEGER DEFAULT 0, -- order among community leadership roles
    display_format VARCHAR(30) DEFAULT 'narrative', -- narrative, bullet_points, condensed
    highlight_achievements BOOLEAN DEFAULT true, -- emphasize key achievements
    show_metrics BOOLEAN DEFAULT true, -- display quantified results
    
    -- Status & Metadata
    role_status VARCHAR(20) DEFAULT 'active', -- active, completed, ongoing, archived
    is_featured BOOLEAN DEFAULT false, -- highlight this role when included
    visibility VARCHAR(20) DEFAULT 'public', -- public, professional_only, private
    notes TEXT, -- internal notes about when/why to include
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- COMMUNITY LEADERSHIP ACHIEVEMENTS
-- =====================================================

CREATE TABLE community_leadership_achievements (
    achievement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    leadership_id UUID NOT NULL REFERENCES community_leadership(leadership_id) ON DELETE CASCADE,
    
    -- Achievement Details
    achievement_text TEXT NOT NULL,
    achievement_category VARCHAR(50) NOT NULL, -- leadership, fundraising, program_development, community_impact, networking, mentorship
    
    -- Impact & Results
    has_quantified_impact BOOLEAN DEFAULT false,
    impact_metrics JSONB, -- specific metrics (funds raised, people served, etc.)
    impact_description TEXT, -- narrative description of impact
    timeframe VARCHAR(50), -- when this achievement occurred
    
    -- Skills & Qualities Demonstrated
    skills_demonstrated TEXT[] NOT NULL, -- skills shown in this achievement
    leadership_qualities TEXT[], -- leadership qualities demonstrated
    professional_relevance TEXT, -- how this relates to professional capabilities
    
    -- Professional Value
    demonstrates_capability TEXT[], -- professional capabilities this achievement shows
    transferable_to_roles TEXT[], -- types of roles where this achievement is relevant
    industry_relevance TEXT[], -- industries where this achievement adds value
    
    -- Keywords for Matching
    primary_keywords TEXT[] NOT NULL, -- main keywords
    achievement_keywords TEXT[], -- achievement-specific terms
    skill_keywords TEXT[], -- skills demonstrated
    
    -- Display & Selection
    display_order INTEGER DEFAULT 0, -- order within the leadership role
    is_featured BOOLEAN DEFAULT false, -- highlight this achievement
    show_by_default BOOLEAN DEFAULT true, -- include in standard display
    professional_relevance_score DECIMAL(3,2) DEFAULT 0.5, -- how professionally relevant (0-1)
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- RESUME COMMUNITY LEADERSHIP SELECTIONS
-- =====================================================

CREATE TABLE resume_community_leadership_selections (
    selection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID NOT NULL REFERENCES generated_resumes(resume_id) ON DELETE CASCADE,
    leadership_id UUID NOT NULL REFERENCES community_leadership(leadership_id) ON DELETE CASCADE,
    
    -- Selection Decision
    is_included BOOLEAN NOT NULL DEFAULT false, -- checkbox state
    inclusion_reason VARCHAR(100), -- why this leadership role was included
    selection_type VARCHAR(30), -- manual, automatic, recommended
    
    -- Display Configuration
    display_order INTEGER, -- order in community leadership section
    display_format VARCHAR(30) DEFAULT 'narrative', -- how to display this role
    selected_achievements UUID[], -- specific achievements to highlight
    max_achievements INTEGER DEFAULT 3, -- limit achievements shown
    
    -- Context & Value
    adds_value_because TEXT, -- explanation of why this role adds value
    demonstrates_qualities TEXT[], -- specific qualities this role demonstrates
    professional_relevance TEXT, -- how this enhances professional profile
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- JOB-COMMUNITY LEADERSHIP RELEVANCE SCORING
-- =====================================================

CREATE TABLE job_community_leadership_relevance (
    relevance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    leadership_id UUID NOT NULL REFERENCES community_leadership(leadership_id) ON DELETE CASCADE,
    
    -- Relevance Scores
    leadership_skills_score DECIMAL(4,3) NOT NULL, -- leadership skills alignment
    industry_relevance_score DECIMAL(4,3) NOT NULL, -- industry/sector relevance
    network_value_score DECIMAL(4,3) NOT NULL, -- networking and relationship value
    cultural_fit_score DECIMAL(4,3) NOT NULL, -- company culture and values alignment
    professional_development_score DECIMAL(4,3) NOT NULL, -- shows commitment to growth
    
    -- Composite Score
    overall_relevance_score DECIMAL(4,3) NOT NULL, -- weighted combination
    inclusion_recommendation VARCHAR(30) NOT NULL, -- include, exclude, optional
    
    -- Match Context
    relevant_skills TEXT[], -- skills from this role that match job requirements
    demonstrates_qualities TEXT[], -- qualities this role demonstrates for the job
    network_advantages TEXT[], -- networking advantages for this role/company
    cultural_alignment TEXT[], -- how this aligns with company culture/values
    relevance_reasoning TEXT, -- why this role is/isn't relevant
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- FUNCTIONS FOR COMMUNITY LEADERSHIP MANAGEMENT
-- =====================================================

-- Function to get recommended community leadership roles for a job
CREATE OR REPLACE FUNCTION get_recommended_community_leadership(
    p_profile_id UUID,
    p_job_id UUID,
    p_min_relevance DECIMAL DEFAULT 0.4
)
RETURNS TABLE (
    leadership_id UUID,
    role VARCHAR,
    organization VARCHAR,
    relevance_score DECIMAL,
    inclusion_recommendation VARCHAR,
    demonstrates_qualities TEXT[],
    network_advantages TEXT[],
    reasoning TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cl.leadership_id,
        cl.role,
        cl.organization,
        jclr.overall_relevance_score,
        jclr.inclusion_recommendation,
        jclr.demonstrates_qualities,
        jclr.network_advantages,
        jclr.relevance_reasoning
    FROM community_leadership cl
    JOIN job_community_leadership_relevance jclr ON cl.leadership_id = jclr.leadership_id
    WHERE jclr.profile_id = p_profile_id 
    AND jclr.job_id = p_job_id
    AND cl.role_status IN ('active', 'completed', 'ongoing')
    AND jclr.overall_relevance_score >= p_min_relevance
    ORDER BY jclr.overall_relevance_score DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get community leadership achievements for selected roles
CREATE OR REPLACE FUNCTION get_community_leadership_achievements_for_resume(
    p_leadership_id UUID,
    p_job_context VARCHAR DEFAULT NULL,
    p_max_achievements INTEGER DEFAULT 3
)
RETURNS TABLE (
    achievement_id UUID,
    achievement_text TEXT,
    achievement_category VARCHAR,
    skills_demonstrated TEXT[],
    professional_relevance TEXT,
    impact_description TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cla.achievement_id,
        cla.achievement_text,
        cla.achievement_category,
        cla.skills_demonstrated,
        cla.professional_relevance,
        cla.impact_description
    FROM community_leadership_achievements cla
    WHERE cla.leadership_id = p_leadership_id
    AND cla.show_by_default = true
    AND (
        p_job_context IS NULL OR
        (p_job_context = 'leadership' AND cla.achievement_category IN ('leadership', 'program_development')) OR
        (p_job_context = 'nonprofit' AND cla.achievement_category IN ('fundraising', 'community_impact')) OR
        (p_job_context = 'networking' AND cla.achievement_category IN ('networking', 'mentorship'))
    )
    ORDER BY 
        cla.is_featured DESC,
        cla.professional_relevance_score DESC,
        cla.display_order ASC
    LIMIT p_max_achievements;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate community leadership section value for a resume
CREATE OR REPLACE FUNCTION calculate_community_leadership_resume_value(
    p_profile_id UUID,
    p_job_id UUID
)
RETURNS TABLE (
    total_roles INTEGER,
    avg_relevance_score DECIMAL,
    recommended_inclusions INTEGER,
    leadership_value_score DECIMAL,
    network_value_score DECIMAL,
    cultural_fit_score DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_roles,
        AVG(jclr.overall_relevance_score) as avg_relevance_score,
        COUNT(CASE WHEN jclr.inclusion_recommendation = 'include' THEN 1 END)::INTEGER as recommended_inclusions,
        AVG(jclr.leadership_skills_score) as leadership_value_score,
        AVG(jclr.network_value_score) as network_value_score,
        AVG(jclr.cultural_fit_score) as cultural_fit_score
    FROM community_leadership cl
    JOIN job_community_leadership_relevance jclr ON cl.leadership_id = jclr.leadership_id
    WHERE jclr.profile_id = p_profile_id 
    AND jclr.job_id = p_job_id
    AND cl.role_status IN ('active', 'completed', 'ongoing');
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Community leadership indexes
CREATE INDEX idx_community_leadership_profile_id ON community_leadership(profile_id);
CREATE INDEX idx_community_leadership_organization ON community_leadership(organization);
CREATE INDEX idx_community_leadership_dates ON community_leadership(start_date DESC, end_date DESC);
CREATE INDEX idx_community_leadership_keywords ON community_leadership USING GIN(primary_keywords);
CREATE INDEX idx_community_leadership_skills ON community_leadership USING GIN(leadership_skills);
CREATE INDEX idx_community_leadership_type ON community_leadership(role_type, organization_type);
CREATE INDEX idx_community_leadership_status ON community_leadership(role_status);
CREATE INDEX idx_community_leadership_level ON community_leadership(leadership_level);

-- Community leadership achievements indexes
CREATE INDEX idx_community_leadership_achievements_leadership_id ON community_leadership_achievements(leadership_id);
CREATE INDEX idx_community_leadership_achievements_category ON community_leadership_achievements(achievement_category);
CREATE INDEX idx_community_leadership_achievements_featured ON community_leadership_achievements(is_featured);
CREATE INDEX idx_community_leadership_achievements_relevance ON community_leadership_achievements(professional_relevance_score DESC);

-- Selection and relevance indexes
CREATE INDEX idx_resume_community_leadership_selections_resume_id ON resume_community_leadership_selections(resume_id);
CREATE INDEX idx_resume_community_leadership_selections_included ON resume_community_leadership_selections(is_included);
CREATE INDEX idx_job_community_leadership_relevance_profile_job ON job_community_leadership_relevance(profile_id, job_id);
CREATE INDEX idx_job_community_leadership_relevance_score ON job_community_leadership_relevance(overall_relevance_score DESC);

-- =====================================================
-- ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE community_leadership ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_leadership_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_community_leadership_selections ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_community_leadership_relevance ENABLE ROW LEVEL SECURITY;

-- Policies for community leadership data
CREATE POLICY "Users can manage own community leadership" ON community_leadership FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own community leadership achievements" ON community_leadership_achievements FOR ALL USING (
    leadership_id IN (
        SELECT leadership_id FROM community_leadership 
        WHERE profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
    )
);

CREATE POLICY "Users can manage own community leadership selections" ON resume_community_leadership_selections FOR ALL USING (
    resume_id IN (
        SELECT resume_id FROM generated_resumes 
        WHERE profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
    )
);

CREATE POLICY "Users can view own community leadership relevance" ON job_community_leadership_relevance FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

-- =====================================================
-- SAMPLE DATA STRUCTURE FOR ALLEN WALKER'S COMMUNITY LEADERSHIP
-- =====================================================

-- Example: How Allen's community leadership would be structured

/*
-- Example Community Leadership Role
INSERT INTO community_leadership (
    profile_id, role, organization, location, start_date, end_date,
    narrative, role_type, organization_type, organization_size,
    leadership_level, team_size, key_achievements, impact_metrics,
    leadership_skills, professional_skills, soft_skills,
    network_connections, industry_exposure, networking_value,
    career_relevance, transferable_skills, demonstrates_qualities,
    primary_keywords, leadership_keywords, skill_keywords,
    include_for_leadership_roles, include_for_community_focused_roles
) VALUES (
    'allen_profile_id',
    'Board Member & Technology Committee Chair',
    'Los Angeles Healthcare Innovation Network',
    'Los Angeles, CA',
    '2020-01-01',
    NULL, -- ongoing
    'Serve as board member and chair the Technology Committee for a regional healthcare innovation network focused on advancing digital health solutions. Lead strategic technology initiatives, mentor healthcare startups, and facilitate partnerships between healthcare organizations and technology companies. Oversee annual technology summit attended by 500+ healthcare professionals.',
    'board_member',
    'professional_association',
    'regional',
    'executive',
    8, -- committee size
    ARRAY[
        'Chaired Technology Committee overseeing $2M in innovation grants',
        'Led strategic planning for digital health initiatives across 15 member organizations',
        'Mentored 25+ healthcare technology startups through accelerator program',
        'Organized annual Healthcare Innovation Summit with 500+ attendees'
    ],
    ARRAY[
        '$2M in innovation grants managed',
        '15 member organizations served',
        '25+ startups mentored',
        '500+ summit attendees annually'
    ],
    ARRAY['Strategic Leadership', 'Committee Management', 'Technology Strategy', 'Mentorship'],
    ARRAY['Healthcare Technology', 'Digital Health', 'Innovation Management', 'Grant Management'],
    ARRAY['Public Speaking', 'Relationship Building', 'Cross-functional Collaboration'],
    ARRAY['Healthcare Executives', 'Technology Leaders', 'Startup Founders', 'Innovation Directors'],
    ARRAY['Healthcare', 'Technology', 'Digital Health', 'Innovation'],
    'Provides access to healthcare innovation ecosystem and technology leadership network',
    'Demonstrates technology leadership in healthcare sector, directly relevant to healthcare technology and innovation roles',
    ARRAY['Technology Leadership', 'Healthcare Innovation', 'Strategic Planning', 'Mentorship', 'Grant Management'],
    ARRAY['Strategic Thinking', 'Innovation Leadership', 'Stakeholder Management', 'Technology Vision'],
    ARRAY['healthcare innovation', 'technology leadership', 'digital health', 'board member'],
    ARRAY['board member', 'committee chair', 'strategic leadership', 'technology strategy'],
    ARRAY['healthcare', 'technology', 'innovation', 'mentorship', 'grants'],
    true, -- include for leadership roles
    true  -- include for community-focused roles
);

-- Sample achievements for community leadership
INSERT INTO community_leadership_achievements (
    leadership_id, achievement_text, achievement_category,
    skills_demonstrated, leadership_qualities, professional_relevance,
    demonstrates_capability, primary_keywords,
    is_featured, professional_relevance_score
) VALUES
('leadership_role_id', 'Led Technology Committee in awarding $2M in innovation grants to 15 healthcare organizations, resulting in 8 successful digital health product launches', 'leadership',
ARRAY['Grant Management', 'Technology Assessment', 'Strategic Decision Making'],
ARRAY['Strategic Leadership', 'Financial Stewardship', 'Innovation Vision'],
'Demonstrates ability to manage large budgets and assess technology investments',
ARRAY['Budget Management', 'Technology Strategy', 'Innovation Leadership'],
ARRAY['grant management', 'technology assessment', 'healthcare innovation'],
true, 0.9),

('leadership_role_id', 'Mentored 25+ healthcare technology startups through accelerator program, with 60% achieving Series A funding within 18 months', 'mentorship',
ARRAY['Mentorship', 'Business Development', 'Technology Guidance'],
ARRAY['Coaching', 'Strategic Guidance', 'Industry Expertise'],
'Shows ability to develop talent and guide technology initiatives to success',
ARRAY['Talent Development', 'Strategic Guidance', 'Technology Leadership'],
ARRAY['mentorship', 'startup guidance', 'technology development'],
true, 0.8);
*/
