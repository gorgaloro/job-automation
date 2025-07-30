-- =====================================================
-- ADDITIONAL EXPERIENCE SCHEMA - SEPARATE FROM EARLY CAREER
-- Property management and other non-core professional experience
-- =====================================================

-- =====================================================
-- ADDITIONAL EXPERIENCE TABLE
-- =====================================================

CREATE TABLE additional_experience (
    additional_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    
    -- Basic Role Information
    company VARCHAR(200) NOT NULL,
    job_title VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    location VARCHAR(100),
    employment_type VARCHAR(20) DEFAULT 'full_time', -- full_time, part_time, contract, seasonal
    
    -- Role Context & Summary
    role_summary TEXT, -- brief overview of the role
    industry VARCHAR(100), -- industry context
    company_size VARCHAR(20), -- startup, small, medium, large, enterprise
    role_category VARCHAR(30), -- operations, sales, customer_service, management, other
    
    -- Key Responsibilities & Achievements
    key_responsibilities TEXT[] NOT NULL, -- main responsibilities in this role
    key_achievements TEXT[], -- notable achievements or accomplishments
    quantified_results TEXT[], -- specific metrics or results achieved
    
    -- Skills & Competencies Demonstrated
    skills_demonstrated TEXT[] NOT NULL, -- skills gained or demonstrated
    leadership_experience TEXT[], -- any leadership or management experience
    customer_facing_experience TEXT[], -- customer service or client interaction
    operational_skills TEXT[], -- operational or process management skills
    
    -- Technologies & Systems
    technologies_used TEXT[], -- tools, systems, or technologies used
    industry_systems TEXT[], -- industry-specific systems (Yardi, etc.)
    
    -- Keywords for Matching
    primary_keywords TEXT[] NOT NULL, -- main keywords for job matching
    industry_keywords TEXT[], -- industry-specific terms
    transferable_keywords TEXT[], -- skills that transfer to other industries
    
    -- Inclusion Control & Display
    default_include BOOLEAN DEFAULT false, -- whether to include by default
    include_for_operations_roles BOOLEAN DEFAULT false, -- include for operations positions
    include_for_management_roles BOOLEAN DEFAULT false, -- include for management positions
    include_for_customer_service_roles BOOLEAN DEFAULT false, -- include for customer-facing roles
    include_for_diverse_background BOOLEAN DEFAULT true, -- include to show diverse experience
    
    -- Display Configuration
    display_order INTEGER DEFAULT 0, -- order among additional experience roles
    display_format VARCHAR(30) DEFAULT 'condensed', -- full, condensed, bullet_only
    max_bullets_to_show INTEGER DEFAULT 2, -- limit number of bullets shown
    
    -- Relevance & Context
    relevance_to_current_career TEXT, -- how this role relates to current career path
    transferable_skills TEXT[], -- skills that transfer to current roles
    demonstrates_qualities TEXT[], -- personal qualities or work ethic demonstrated
    
    -- Status & Metadata
    role_status VARCHAR(20) DEFAULT 'active', -- active, archived, deprecated
    is_featured BOOLEAN DEFAULT false, -- highlight this role when included
    notes TEXT, -- internal notes about when/why to include this role
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- ADDITIONAL EXPERIENCE BULLET POINTS
-- =====================================================

CREATE TABLE additional_experience_bullet_points (
    bullet_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    additional_id UUID NOT NULL REFERENCES additional_experience(additional_id) ON DELETE CASCADE,
    
    -- Bullet Point Content
    bullet_text TEXT NOT NULL,
    bullet_category VARCHAR(30) NOT NULL, -- responsibility, achievement, leadership, customer_service, operations
    
    -- Impact & Results
    has_quantified_impact BOOLEAN DEFAULT false,
    impact_metrics JSONB, -- specific metrics or results
    impact_description TEXT, -- narrative description of impact
    
    -- Skills & Qualities Demonstrated
    skills_demonstrated TEXT[] NOT NULL, -- skills shown in this bullet
    qualities_demonstrated TEXT[], -- work qualities or characteristics shown
    transferable_elements TEXT[], -- what transfers to other roles/industries
    
    -- Transferability & Relevance
    relevant_for_operations BOOLEAN DEFAULT false, -- relevant for operations roles
    relevant_for_management BOOLEAN DEFAULT false, -- relevant for management roles
    relevant_for_customer_service BOOLEAN DEFAULT false, -- relevant for customer-facing roles
    shows_work_ethic BOOLEAN DEFAULT false, -- demonstrates strong work ethic
    shows_leadership BOOLEAN DEFAULT false, -- demonstrates leadership qualities
    
    -- Keywords for Matching
    primary_keywords TEXT[] NOT NULL, -- main keywords
    transferable_keywords TEXT[], -- skills that transfer across industries
    
    -- Display & Selection
    display_order INTEGER DEFAULT 0, -- order within the role
    is_featured BOOLEAN DEFAULT false, -- highlight this bullet when role is included
    show_by_default BOOLEAN DEFAULT true, -- include in standard display
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- UPDATED EARLY CAREER ROLES (REFINED FOR PROGRAM MANAGEMENT FOCUS)
-- =====================================================

-- Update the existing early career table to focus specifically on program/project management roles
ALTER TABLE early_career_roles 
ADD COLUMN IF NOT EXISTS role_focus VARCHAR(50) DEFAULT 'program_management'; -- program_management, technical, consulting

-- Add comment to clarify the distinction
COMMENT ON TABLE early_career_roles IS 'Early career roles specifically in program management, project management, and technical consulting (2008-2010: Amgen, Cedars-Sinai)';
COMMENT ON TABLE additional_experience IS 'Additional professional experience outside core career path (2003-2008: Property Management, Leasing)';

-- =====================================================
-- RESUME ADDITIONAL EXPERIENCE SELECTIONS
-- =====================================================

CREATE TABLE resume_additional_experience_selections (
    selection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID NOT NULL REFERENCES generated_resumes(resume_id) ON DELETE CASCADE,
    additional_id UUID NOT NULL REFERENCES additional_experience(additional_id) ON DELETE CASCADE,
    
    -- Selection Decision
    is_included BOOLEAN NOT NULL DEFAULT false, -- checkbox state
    inclusion_reason VARCHAR(100), -- why this experience was included
    selection_type VARCHAR(30), -- manual, automatic, recommended
    
    -- Display Configuration
    display_order INTEGER, -- order in additional experience section
    display_format VARCHAR(30) DEFAULT 'condensed', -- how to display this experience
    selected_bullets UUID[], -- specific bullets to include
    max_bullets INTEGER DEFAULT 2, -- limit bullets for this experience
    
    -- Context
    adds_value_because TEXT, -- explanation of why this experience adds value
    demonstrates_qualities TEXT[], -- specific qualities this experience demonstrates
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- JOB-ADDITIONAL EXPERIENCE RELEVANCE SCORING
-- =====================================================

CREATE TABLE job_additional_experience_relevance (
    relevance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    additional_id UUID NOT NULL REFERENCES additional_experience(additional_id) ON DELETE CASCADE,
    
    -- Relevance Scores
    transferable_skills_score DECIMAL(4,3) NOT NULL, -- how well skills transfer
    leadership_relevance_score DECIMAL(4,3) NOT NULL, -- leadership experience relevance
    operations_relevance_score DECIMAL(4,3) NOT NULL, -- operational experience relevance
    customer_service_relevance_score DECIMAL(4,3) NOT NULL, -- customer-facing experience relevance
    work_ethic_demonstration_score DECIMAL(4,3) NOT NULL, -- work ethic and reliability demonstration
    
    -- Composite Score
    overall_relevance_score DECIMAL(4,3) NOT NULL, -- weighted combination
    inclusion_recommendation VARCHAR(30) NOT NULL, -- include, exclude, optional
    
    -- Match Context
    transferable_elements TEXT[], -- what transfers from this experience
    demonstrates_qualities TEXT[], -- qualities this experience demonstrates
    relevance_reasoning TEXT, -- why this experience is/isn't relevant
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- FUNCTIONS FOR ADDITIONAL EXPERIENCE MANAGEMENT
-- =====================================================

-- Function to get recommended additional experience for a job
CREATE OR REPLACE FUNCTION get_recommended_additional_experience(
    p_profile_id UUID,
    p_job_id UUID,
    p_min_relevance DECIMAL DEFAULT 0.5
)
RETURNS TABLE (
    additional_id UUID,
    company VARCHAR,
    job_title VARCHAR,
    relevance_score DECIMAL,
    inclusion_recommendation VARCHAR,
    demonstrates_qualities TEXT[],
    reasoning TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ae.additional_id,
        ae.company,
        ae.job_title,
        jaer.overall_relevance_score,
        jaer.inclusion_recommendation,
        jaer.demonstrates_qualities,
        jaer.relevance_reasoning
    FROM additional_experience ae
    JOIN job_additional_experience_relevance jaer ON ae.additional_id = jaer.additional_id
    WHERE jaer.profile_id = p_profile_id 
    AND jaer.job_id = p_job_id
    AND ae.role_status = 'active'
    AND jaer.overall_relevance_score >= p_min_relevance
    ORDER BY jaer.overall_relevance_score DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get additional experience bullets for selected roles
CREATE OR REPLACE FUNCTION get_additional_experience_bullets_for_resume(
    p_additional_id UUID,
    p_job_context VARCHAR DEFAULT NULL,
    p_max_bullets INTEGER DEFAULT 2
)
RETURNS TABLE (
    bullet_id UUID,
    bullet_text TEXT,
    bullet_category VARCHAR,
    skills_demonstrated TEXT[],
    qualities_demonstrated TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        aebp.bullet_id,
        aebp.bullet_text,
        aebp.bullet_category,
        aebp.skills_demonstrated,
        aebp.qualities_demonstrated
    FROM additional_experience_bullet_points aebp
    WHERE aebp.additional_id = p_additional_id
    AND aebp.show_by_default = true
    AND (
        p_job_context IS NULL OR
        (p_job_context = 'operations' AND aebp.relevant_for_operations = true) OR
        (p_job_context = 'management' AND aebp.relevant_for_management = true) OR
        (p_job_context = 'customer_service' AND aebp.relevant_for_customer_service = true)
    )
    ORDER BY 
        aebp.is_featured DESC,
        aebp.shows_leadership DESC,
        aebp.display_order ASC
    LIMIT p_max_bullets;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Additional experience indexes
CREATE INDEX idx_additional_experience_profile_id ON additional_experience(profile_id);
CREATE INDEX idx_additional_experience_company ON additional_experience(company);
CREATE INDEX idx_additional_experience_dates ON additional_experience(start_date DESC, end_date DESC);
CREATE INDEX idx_additional_experience_keywords ON additional_experience USING GIN(primary_keywords);
CREATE INDEX idx_additional_experience_skills ON additional_experience USING GIN(skills_demonstrated);
CREATE INDEX idx_additional_experience_category ON additional_experience(role_category);
CREATE INDEX idx_additional_experience_status ON additional_experience(role_status);

-- Additional experience bullets indexes
CREATE INDEX idx_additional_experience_bullets_additional_id ON additional_experience_bullet_points(additional_id);
CREATE INDEX idx_additional_experience_bullets_category ON additional_experience_bullet_points(bullet_category);
CREATE INDEX idx_additional_experience_bullets_featured ON additional_experience_bullet_points(is_featured);
CREATE INDEX idx_additional_experience_bullets_leadership ON additional_experience_bullet_points(shows_leadership);
CREATE INDEX idx_additional_experience_bullets_operations ON additional_experience_bullet_points(relevant_for_operations);

-- Selection and relevance indexes
CREATE INDEX idx_resume_additional_experience_selections_resume_id ON resume_additional_experience_selections(resume_id);
CREATE INDEX idx_resume_additional_experience_selections_included ON resume_additional_experience_selections(is_included);
CREATE INDEX idx_job_additional_experience_relevance_profile_job ON job_additional_experience_relevance(profile_id, job_id);
CREATE INDEX idx_job_additional_experience_relevance_score ON job_additional_experience_relevance(overall_relevance_score DESC);

-- =====================================================
-- ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE additional_experience ENABLE ROW LEVEL SECURITY;
ALTER TABLE additional_experience_bullet_points ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_additional_experience_selections ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_additional_experience_relevance ENABLE ROW LEVEL SECURITY;

-- Policies for additional experience data
CREATE POLICY "Users can manage own additional experience" ON additional_experience FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own additional experience bullets" ON additional_experience_bullet_points FOR ALL USING (
    additional_id IN (
        SELECT additional_id FROM additional_experience 
        WHERE profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
    )
);

CREATE POLICY "Users can manage own additional experience selections" ON resume_additional_experience_selections FOR ALL USING (
    resume_id IN (
        SELECT resume_id FROM generated_resumes 
        WHERE profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
    )
);

CREATE POLICY "Users can view own additional experience relevance" ON job_additional_experience_relevance FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

-- =====================================================
-- SAMPLE DATA FOR ALLEN WALKER'S ADDITIONAL EXPERIENCE
-- =====================================================

-- Example: How Allen's additional experience would be structured

/*
-- Property Management & Leasing Experience (Los Angeles 2003-2008)
INSERT INTO additional_experience (
    profile_id, company, job_title, start_date, end_date, location,
    role_summary, industry, company_size, role_category,
    key_responsibilities, key_achievements,
    skills_demonstrated, leadership_experience, customer_facing_experience, operational_skills,
    technologies_used, industry_systems,
    primary_keywords, industry_keywords, transferable_keywords,
    include_for_operations_roles, include_for_management_roles, include_for_diverse_background,
    relevance_to_current_career, transferable_skills, demonstrates_qualities
) VALUES (
    'allen_profile_id',
    'Various Property Management Companies',
    'Leasing Manager & Property Operations',
    '2003-01-01',
    '2008-12-31',
    'Los Angeles, CA',
    'Operations and management roles in residential property management, demonstrating customer service excellence, team leadership, and operational efficiency.',
    'Real Estate & Property Management',
    'medium',
    'operations',
    ARRAY[
        'Closed over 100 residential leases as leasing manager of 314-unit high-rise',
        'Led team of 3 leasing agents and coordinated full-cycle tenant onboarding',
        'Managed daily operations for 130-unit downtown building',
        'Oversaw rent collection, maintenance workflows, and leasing activities'
    ],
    ARRAY[
        'Successfully closed 100+ residential leases with high conversion rates',
        'Led and managed team of 3 direct reports',
        'Maintained high occupancy rates and tenant satisfaction scores',
        'Streamlined operational workflows and improved efficiency'
    ],
    ARRAY['Team Leadership', 'Customer Service', 'Operations Management', 'Sales', 'Process Management'],
    ARRAY['Led team of 3 leasing agents', 'Managed daily operations across multiple properties'],
    ARRAY['Customer consultation and needs assessment', 'Tenant relationship management', 'Lease negotiation'],
    ARRAY['Daily operations management', 'Workflow optimization', 'Vendor coordination', 'Maintenance oversight'],
    ARRAY['Yardi Property Management System', 'CRM Systems', 'Lease Management Software'],
    ARRAY['Yardi'],
    ARRAY['property management', 'leasing', 'operations', 'team leadership', 'customer service'],
    ARRAY['real estate', 'property management', 'residential', 'leasing'],
    ARRAY['team leadership', 'operations management', 'customer service', 'sales', 'process management'],
    true,  -- include for operations roles
    true,  -- include for management roles
    true,  -- include for diverse background
    'Demonstrates early leadership experience, operations management capabilities, and customer service excellence that translate to program management and operational roles.',
    ARRAY['Team Leadership', 'Operations Management', 'Customer Service', 'Process Management', 'Vendor Coordination'],
    ARRAY['Strong Work Ethic', 'Customer Focus', 'Team Leadership', 'Operational Excellence', 'Results-Driven']
);

-- Sample bullet points for additional experience
INSERT INTO additional_experience_bullet_points (
    additional_id, bullet_text, bullet_category,
    skills_demonstrated, qualities_demonstrated, transferable_elements,
    relevant_for_operations, relevant_for_management, shows_leadership, shows_work_ethic,
    primary_keywords, transferable_keywords,
    is_featured, display_order
) VALUES
('additional_experience_id', 'Closed over 100 residential leases as leasing manager of a 314-unit new construction high-rise—led a team of 3 agents and coordinated full-cycle leasing and tenant onboarding', 'achievement',
ARRAY['Team Leadership', 'Sales', 'Customer Service'], 
ARRAY['Results-Driven', 'Leadership', 'Customer Focus'],
ARRAY['Team management', 'Process coordination', 'Customer relationship management'],
true, true, true, true,
ARRAY['leasing', 'team leadership', 'customer service', 'coordination'],
ARRAY['team leadership', 'process management', 'customer service'],
true, 1),

('additional_experience_id', 'Managed daily operations for a 130-unit downtown building—oversaw rent collection, maintenance workflows, and leasing activities using Yardi', 'responsibility',
ARRAY['Operations Management', 'Process Management', 'Technology Systems'],
ARRAY['Operational Excellence', 'Attention to Detail', 'Systems Thinking'],
ARRAY['Operations oversight', 'Workflow management', 'System utilization'],
true, true, false, true,
ARRAY['operations', 'management', 'workflows', 'yardi'],
ARRAY['operations management', 'process management', 'systems'],
true, 2);
*/
