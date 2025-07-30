-- =====================================================
-- EARLY CAREER ROLES SCHEMA - OPTIONAL RESUME INCLUSION
-- Flexible early career experience with checkbox control
-- =====================================================

-- =====================================================
-- EARLY CAREER ROLES TABLE
-- =====================================================

CREATE TABLE early_career_roles (
    early_role_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    
    -- Basic Role Information
    company VARCHAR(200) NOT NULL,
    job_title VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    location VARCHAR(100),
    employment_type VARCHAR(20) DEFAULT 'full_time', -- full_time, part_time, contract, internship
    
    -- Role Context & Summary
    role_summary TEXT, -- brief overview of the role
    industry VARCHAR(100), -- industry context
    company_size VARCHAR(20), -- startup, small, medium, large, enterprise
    role_level VARCHAR(20) DEFAULT 'early_career', -- entry_level, early_career, junior
    
    -- Key Responsibilities & Achievements
    key_responsibilities TEXT[] NOT NULL, -- main responsibilities in this role
    key_achievements TEXT[], -- notable achievements or accomplishments
    quantified_results TEXT[], -- specific metrics or results achieved
    
    -- Skills & Technologies
    skills_developed TEXT[] NOT NULL, -- skills gained or demonstrated
    technologies_used TEXT[], -- tools, systems, or technologies used
    methodologies_learned TEXT[], -- processes or methodologies learned
    
    -- Professional Development
    certifications_earned TEXT[], -- certifications obtained during this role
    training_completed TEXT[], -- training programs or courses completed
    mentorship_received TEXT[], -- mentorship or guidance received
    
    -- Keywords for Matching
    primary_keywords TEXT[] NOT NULL, -- main keywords for job matching
    industry_keywords TEXT[], -- industry-specific terms
    role_keywords TEXT[], -- role-specific terms
    
    -- Inclusion Control & Display
    default_include BOOLEAN DEFAULT false, -- whether to include by default
    include_for_entry_level BOOLEAN DEFAULT true, -- include when applying to entry-level roles
    include_for_career_change BOOLEAN DEFAULT true, -- include when changing industries/roles
    include_for_skill_demonstration BOOLEAN DEFAULT false, -- include to show specific skills
    
    -- Display Configuration
    display_order INTEGER DEFAULT 0, -- order among early career roles
    display_format VARCHAR(30) DEFAULT 'condensed', -- full, condensed, bullet_only
    max_bullets_to_show INTEGER DEFAULT 3, -- limit number of bullets shown
    
    -- Relevance & Context
    relevance_to_current_career TEXT, -- how this role relates to current career path
    transferable_skills TEXT[], -- skills that transfer to current roles
    leadership_experience TEXT, -- any leadership or initiative-taking examples
    
    -- Status & Metadata
    role_status VARCHAR(20) DEFAULT 'active', -- active, archived, deprecated
    is_featured BOOLEAN DEFAULT false, -- highlight this role when included
    notes TEXT, -- internal notes about when/why to include this role
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- EARLY CAREER BULLET POINTS (DETAILED BREAKDOWN)
-- =====================================================

CREATE TABLE early_career_bullet_points (
    bullet_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    early_role_id UUID NOT NULL REFERENCES early_career_roles(early_role_id) ON DELETE CASCADE,
    
    -- Bullet Point Content
    bullet_text TEXT NOT NULL,
    bullet_category VARCHAR(30) NOT NULL, -- responsibility, achievement, leadership, learning, project
    
    -- Impact & Results
    has_quantified_impact BOOLEAN DEFAULT false,
    impact_metrics JSONB, -- specific metrics or results
    impact_description TEXT, -- narrative description of impact
    
    -- Skills & Learning Demonstrated
    skills_demonstrated TEXT[] NOT NULL, -- skills shown in this bullet
    learning_demonstrated TEXT[], -- what was learned or developed
    technologies_mentioned TEXT[], -- specific technologies used
    
    -- Transferability & Relevance
    transferable_to_roles TEXT[], -- role types this bullet is relevant for
    transferable_to_industries TEXT[], -- industries this bullet applies to
    demonstrates_growth BOOLEAN DEFAULT false, -- shows professional growth/development
    
    -- Keywords for Matching
    primary_keywords TEXT[] NOT NULL, -- main keywords
    secondary_keywords TEXT[], -- supporting keywords
    
    -- Display & Selection
    display_order INTEGER DEFAULT 0, -- order within the role
    is_featured BOOLEAN DEFAULT false, -- highlight this bullet when role is included
    show_by_default BOOLEAN DEFAULT true, -- include in standard display
    
    -- Selection Criteria
    include_for_leadership_roles BOOLEAN DEFAULT false, -- relevant for leadership positions
    include_for_technical_roles BOOLEAN DEFAULT false, -- relevant for technical positions
    include_for_project_management BOOLEAN DEFAULT false, -- relevant for PM roles
    include_for_operations BOOLEAN DEFAULT false, -- relevant for operations roles
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- RESUME EARLY CAREER SELECTIONS
-- =====================================================

CREATE TABLE resume_early_career_selections (
    selection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID NOT NULL REFERENCES generated_resumes(resume_id) ON DELETE CASCADE,
    early_role_id UUID NOT NULL REFERENCES early_career_roles(early_role_id) ON DELETE CASCADE,
    
    -- Selection Decision
    is_included BOOLEAN NOT NULL DEFAULT false, -- checkbox state
    inclusion_reason VARCHAR(100), -- why this role was included
    selection_type VARCHAR(30), -- manual, automatic, recommended
    
    -- Display Configuration
    display_order INTEGER, -- order in early career section
    display_format VARCHAR(30) DEFAULT 'condensed', -- how to display this role
    selected_bullets UUID[], -- specific bullets to include
    max_bullets INTEGER DEFAULT 3, -- limit bullets for this role
    
    -- Context
    adds_value_because TEXT, -- explanation of why this role adds value
    demonstrates_skills TEXT[], -- specific skills this role demonstrates for the job
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- EARLY CAREER RELEVANCE SCORING
-- =====================================================

CREATE TABLE job_early_career_relevance (
    relevance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    early_role_id UUID NOT NULL REFERENCES early_career_roles(early_role_id) ON DELETE CASCADE,
    
    -- Relevance Scores
    skill_relevance_score DECIMAL(4,3) NOT NULL, -- skills alignment
    industry_relevance_score DECIMAL(4,3) NOT NULL, -- industry alignment
    role_relevance_score DECIMAL(4,3) NOT NULL, -- role type alignment
    keyword_relevance_score DECIMAL(4,3) NOT NULL, -- keyword matching
    transferability_score DECIMAL(4,3) NOT NULL, -- how well skills transfer
    
    -- Composite Score
    overall_relevance_score DECIMAL(4,3) NOT NULL, -- weighted combination
    inclusion_recommendation VARCHAR(30) NOT NULL, -- include, exclude, optional
    
    -- Match Context
    matched_skills TEXT[], -- skills that align with job
    matched_keywords TEXT[], -- keywords that match
    transferable_elements TEXT[], -- what transfers from this role
    relevance_reasoning TEXT, -- why this role is/isn't relevant
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- FUNCTIONS FOR EARLY CAREER MANAGEMENT
-- =====================================================

-- Function to get recommended early career roles for a job
CREATE OR REPLACE FUNCTION get_recommended_early_career_roles(
    p_profile_id UUID,
    p_job_id UUID,
    p_min_relevance DECIMAL DEFAULT 0.6
)
RETURNS TABLE (
    early_role_id UUID,
    company VARCHAR,
    job_title VARCHAR,
    relevance_score DECIMAL,
    inclusion_recommendation VARCHAR,
    matched_skills TEXT[],
    reasoning TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ecr.early_role_id,
        ecr.company,
        ecr.job_title,
        jecr.overall_relevance_score,
        jecr.inclusion_recommendation,
        jecr.matched_skills,
        jecr.relevance_reasoning
    FROM early_career_roles ecr
    JOIN job_early_career_relevance jecr ON ecr.early_role_id = jecr.early_role_id
    WHERE jecr.profile_id = p_profile_id 
    AND jecr.job_id = p_job_id
    AND ecr.role_status = 'active'
    AND jecr.overall_relevance_score >= p_min_relevance
    ORDER BY jecr.overall_relevance_score DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get early career bullets for selected roles
CREATE OR REPLACE FUNCTION get_early_career_bullets_for_resume(
    p_early_role_id UUID,
    p_job_id UUID DEFAULT NULL,
    p_max_bullets INTEGER DEFAULT 3
)
RETURNS TABLE (
    bullet_id UUID,
    bullet_text TEXT,
    bullet_category VARCHAR,
    skills_demonstrated TEXT[],
    is_featured BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ecbp.bullet_id,
        ecbp.bullet_text,
        ecbp.bullet_category,
        ecbp.skills_demonstrated,
        ecbp.is_featured
    FROM early_career_bullet_points ecbp
    WHERE ecbp.early_role_id = p_early_role_id
    AND ecbp.show_by_default = true
    ORDER BY 
        ecbp.is_featured DESC,
        ecbp.display_order ASC
    LIMIT p_max_bullets;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Early career roles indexes
CREATE INDEX idx_early_career_roles_profile_id ON early_career_roles(profile_id);
CREATE INDEX idx_early_career_roles_company ON early_career_roles(company);
CREATE INDEX idx_early_career_roles_dates ON early_career_roles(start_date DESC, end_date DESC);
CREATE INDEX idx_early_career_roles_keywords ON early_career_roles USING GIN(primary_keywords);
CREATE INDEX idx_early_career_roles_skills ON early_career_roles USING GIN(skills_developed);
CREATE INDEX idx_early_career_roles_default_include ON early_career_roles(default_include);
CREATE INDEX idx_early_career_roles_status ON early_career_roles(role_status);

-- Early career bullets indexes
CREATE INDEX idx_early_career_bullets_role_id ON early_career_bullet_points(early_role_id);
CREATE INDEX idx_early_career_bullets_category ON early_career_bullet_points(bullet_category);
CREATE INDEX idx_early_career_bullets_featured ON early_career_bullet_points(is_featured);
CREATE INDEX idx_early_career_bullets_default ON early_career_bullet_points(show_by_default);
CREATE INDEX idx_early_career_bullets_order ON early_career_bullet_points(early_role_id, display_order);

-- Selection and relevance indexes
CREATE INDEX idx_resume_early_career_selections_resume_id ON resume_early_career_selections(resume_id);
CREATE INDEX idx_resume_early_career_selections_included ON resume_early_career_selections(is_included);
CREATE INDEX idx_job_early_career_relevance_profile_job ON job_early_career_relevance(profile_id, job_id);
CREATE INDEX idx_job_early_career_relevance_score ON job_early_career_relevance(overall_relevance_score DESC);

-- =====================================================
-- ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE early_career_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE early_career_bullet_points ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_early_career_selections ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_early_career_relevance ENABLE ROW LEVEL SECURITY;

-- Policies for early career data
CREATE POLICY "Users can manage own early career roles" ON early_career_roles FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own early career bullets" ON early_career_bullet_points FOR ALL USING (
    early_role_id IN (
        SELECT early_role_id FROM early_career_roles 
        WHERE profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
    )
);

CREATE POLICY "Users can manage own early career selections" ON resume_early_career_selections FOR ALL USING (
    resume_id IN (
        SELECT resume_id FROM generated_resumes 
        WHERE profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
    )
);

CREATE POLICY "Users can view own early career relevance" ON job_early_career_relevance FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

-- =====================================================
-- SAMPLE DATA FOR ALLEN WALKER'S EARLY CAREER ROLES
-- =====================================================

-- Example: How Allen's early career roles would be structured

/*
-- Early Career Program & Project Management (Amgen, Cedars-Sinai)
INSERT INTO early_career_roles (
    profile_id, company, job_title, start_date, end_date, location,
    role_summary, industry, company_size, role_level,
    key_responsibilities, key_achievements,
    skills_developed, technologies_used,
    primary_keywords, industry_keywords,
    default_include, include_for_entry_level, include_for_career_change,
    relevance_to_current_career, transferable_skills
) VALUES (
    'allen_profile_id',
    'Amgen & Cedars-Sinai Medical Center',
    'Program & Project Manager',
    '2008-01-01',
    '2010-12-31',
    'Los Angeles, CA',
    'Early career program and project management roles supporting large-scale system implementations and process improvements in pharmaceutical and healthcare environments.',
    'Healthcare & Pharmaceuticals',
    'enterprise',
    'early_career',
    ARRAY[
        'Managed 15+ workstreams in global SAP drug manufacturing system replacement',
        'Led revision of 2,000+ SOPs and job aids for legacy MES transition',
        'Oversaw 26 cross-functional workstreams in Epic EMR rollout across 200+ team members',
        'Developed custom SharePoint portals and status dashboards for stakeholder communication'
    ],
    ARRAY[
        'Successfully managed complex multi-workstream programs',
        'Coordinated documentation for 15,000+ users',
        'Managed 3,500+ line project plan',
        'Built stakeholder communication systems'
    ],
    ARRAY['Program Management', 'Project Management', 'Cross-functional Coordination', 'Documentation Management', 'Stakeholder Communication', 'Process Improvement'],
    ARRAY['SAP', 'Epic EMR', 'SharePoint', 'MS Project'],
    ARRAY['program management', 'project management', 'healthcare', 'pharmaceutical', 'epic', 'sap'],
    ARRAY['healthcare', 'pharmaceutical', 'manufacturing', 'emr'],
    false, -- don't include by default
    true,  -- include for entry-level roles
    true,  -- include for career change
    'Demonstrates foundational program management skills and healthcare technology experience that directly supports current senior program management roles.',
    ARRAY['Program Management', 'Healthcare Technology', 'Cross-functional Leadership', 'Process Documentation', 'Stakeholder Management']
);

-- Property Management & Operations (Los Angeles)
INSERT INTO early_career_roles (
    profile_id, company, job_title, start_date, end_date, location,
    role_summary, industry, company_size, role_level,
    key_responsibilities, key_achievements,
    skills_developed, technologies_used,
    primary_keywords, industry_keywords,
    default_include, include_for_entry_level, include_for_career_change,
    include_for_skill_demonstration,
    relevance_to_current_career, transferable_skills
) VALUES (
    'allen_profile_id',
    'Various Property Management Companies',
    'Leasing Manager & Property Operations',
    '2003-01-01',
    '2008-12-31',
    'Los Angeles, CA',
    'Early career operations and management roles in residential property management, demonstrating customer service, team leadership, and operational excellence.',
    'Real Estate & Property Management',
    'medium',
    'early_career',
    ARRAY[
        'Closed over 100 residential leases as leasing manager of 314-unit high-rise',
        'Led team of 3 leasing agents and coordinated full-cycle tenant onboarding',
        'Managed daily operations for 130-unit downtown building',
        'Oversaw rent collection, maintenance workflows, and leasing activities using Yardi'
    ],
    ARRAY[
        'Successfully closed 100+ residential leases',
        'Led and managed team of 3 direct reports',
        'Maintained high occupancy rates and tenant satisfaction',
        'Streamlined operational workflows'
    ],
    ARRAY['Team Leadership', 'Customer Service', 'Operations Management', 'Sales', 'Process Management', 'Vendor Coordination'],
    ARRAY['Yardi', 'Property Management Systems'],
    ARRAY['property management', 'leasing', 'operations', 'team leadership', 'customer service'],
    ARRAY['real estate', 'property management', 'residential'],
    false, -- don't include by default
    false, -- not relevant for entry-level tech roles
    true,  -- include for career change to show diverse background
    true,  -- include to demonstrate leadership and operations skills
    'Shows early leadership experience and operational management skills that translate to program management and team coordination.',
    ARRAY['Team Leadership', 'Operations Management', 'Customer Service', 'Process Management', 'Vendor Coordination']
);

-- Sample bullet points for the program management role
INSERT INTO early_career_bullet_points (
    early_role_id, bullet_text, bullet_category,
    skills_demonstrated, primary_keywords,
    include_for_project_management, include_for_operations,
    is_featured, display_order
) VALUES
('early_role_program_mgmt_id', 'Managed 15+ workstreams in a global SAP drug manufacturing system replacement—tracking timelines, budgets, and risk escalations for executive review', 'achievement',
ARRAY['Program Management', 'Multi-workstream Coordination', 'Executive Communication'], 
ARRAY['program management', 'workstreams', 'sap', 'manufacturing'],
true, true, true, 1),

('early_role_program_mgmt_id', 'Led revision of 2,000+ SOPs and job aids impacted by legacy MES transition—hired technical writers and coordinated documentation with LMS for 15,000+ users', 'achievement',
ARRAY['Process Documentation', 'Change Management', 'Vendor Management'],
ARRAY['documentation', 'process', 'change management', 'training'],
true, true, true, 2),

('early_role_program_mgmt_id', 'Oversaw 26 cross-functional workstreams in an Epic EMR rollout across 200+ team members—managed a 3,500+ line project plan and tracked contractor spend and onboarding', 'achievement',
ARRAY['Cross-functional Leadership', 'Epic Systems', 'Project Planning'],
ARRAY['epic', 'emr', 'cross-functional', 'project plan'],
true, false, true, 3);
*/
