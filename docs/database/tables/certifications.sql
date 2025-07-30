-- =====================================================
-- CERTIFICATIONS SCHEMA
-- Comprehensive certification tracking for professional credentials, licenses, and continuous learning
-- =====================================================

-- =====================================================
-- CERTIFICATIONS TABLE
-- =====================================================

CREATE TABLE certifications (
    certification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    
    -- Core Certification Information
    certification_name VARCHAR(200) NOT NULL, -- full certification name
    certification_code VARCHAR(50), -- certification code/abbreviation (PMP, CISSP, etc.)
    issuing_organization VARCHAR(200) NOT NULL, -- organization that issued the certification
    certification_type VARCHAR(50) NOT NULL, -- professional, technical, industry, vendor, academic
    
    -- Certification Details
    certification_level VARCHAR(50), -- entry, associate, professional, expert, master
    specialization VARCHAR(200), -- specific area of specialization
    certification_description TEXT, -- description of what the certification covers
    
    -- Dates & Status
    issue_date DATE NOT NULL, -- when certification was earned
    expiration_date DATE, -- when certification expires (NULL for non-expiring)
    renewal_date DATE, -- next renewal date
    is_active BOOLEAN DEFAULT true, -- whether certification is currently active
    is_expired BOOLEAN DEFAULT false, -- whether certification has expired
    
    -- Renewal & Maintenance
    renewal_required BOOLEAN DEFAULT false, -- whether renewal is required
    renewal_period_months INTEGER, -- renewal period in months
    continuing_education_required BOOLEAN DEFAULT false, -- whether CE credits required
    ce_credits_required INTEGER, -- continuing education credits needed
    ce_credits_earned INTEGER DEFAULT 0, -- CE credits earned toward renewal
    
    -- Credential Information
    credential_id VARCHAR(100), -- certification ID/number
    verification_url TEXT, -- URL to verify certification
    digital_badge_url TEXT, -- URL to digital badge
    certificate_file_path TEXT, -- path to certificate file
    
    -- Skills & Competencies
    skills_validated TEXT[] NOT NULL, -- skills this certification validates
    technical_skills TEXT[], -- technical skills covered
    knowledge_areas TEXT[], -- knowledge domains covered
    competency_level VARCHAR(30), -- beginner, intermediate, advanced, expert
    
    -- Professional Value
    industry_relevance TEXT[], -- industries where this certification is valuable
    job_roles_relevant TEXT[], -- job roles where this certification is important
    career_impact TEXT, -- how this certification impacts career prospects
    salary_impact_percentage DECIMAL(5,2), -- estimated salary impact percentage
    
    -- Preparation & Achievement
    preparation_hours INTEGER, -- hours spent preparing for certification
    exam_score INTEGER, -- exam score (if applicable)
    exam_passing_score INTEGER, -- minimum passing score
    attempt_number INTEGER DEFAULT 1, -- which attempt this was
    study_materials TEXT[], -- materials used for preparation
    
    -- Keywords for Matching
    primary_keywords TEXT[] NOT NULL, -- main keywords for job matching
    technical_keywords TEXT[], -- technical terms and skills
    vendor_keywords TEXT[], -- vendor-specific terms (Microsoft, AWS, etc.)
    industry_keywords TEXT[], -- industry-specific terms
    
    -- Display & Inclusion Control
    display_order INTEGER DEFAULT 0, -- order among certifications
    is_featured BOOLEAN DEFAULT false, -- highlight this certification
    show_expiration_date BOOLEAN DEFAULT true, -- whether to show expiration
    show_credential_id BOOLEAN DEFAULT false, -- whether to show credential ID
    show_score BOOLEAN DEFAULT false, -- whether to show exam score
    
    -- Relevance Filters
    include_for_technical_roles BOOLEAN DEFAULT false, -- include for technical positions
    include_for_management_roles BOOLEAN DEFAULT false, -- include for management positions
    include_for_vendor_specific BOOLEAN DEFAULT false, -- include for vendor-specific roles
    include_for_compliance_roles BOOLEAN DEFAULT false, -- include for compliance/audit roles
    
    -- Status & Metadata
    certification_status VARCHAR(20) DEFAULT 'active', -- active, expired, suspended, revoked
    verification_status VARCHAR(20) DEFAULT 'unverified', -- verified, unverified, pending
    priority_level VARCHAR(20) DEFAULT 'medium', -- high, medium, low
    notes TEXT, -- internal notes about certification
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- CERTIFICATION ACHIEVEMENTS
-- =====================================================

CREATE TABLE certification_achievements (
    achievement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    certification_id UUID NOT NULL REFERENCES certifications(certification_id) ON DELETE CASCADE,
    
    -- Achievement Details
    achievement_text TEXT NOT NULL,
    achievement_category VARCHAR(50) NOT NULL, -- exam_performance, recognition, specialization, renewal
    
    -- Achievement Context
    achievement_date DATE, -- when achievement occurred
    achievement_description TEXT, -- detailed description
    recognition_level VARCHAR(30), -- personal, organizational, industry, global
    
    -- Performance Metrics
    percentile_ranking INTEGER, -- percentile ranking (if available)
    score_achieved INTEGER, -- score achieved
    perfect_score BOOLEAN DEFAULT false, -- whether achieved perfect score
    first_attempt BOOLEAN DEFAULT true, -- achieved on first attempt
    
    -- Professional Impact
    demonstrates_expertise TEXT[], -- areas of expertise this achievement demonstrates
    career_advancement_impact TEXT, -- how this achievement advanced career
    professional_recognition TEXT, -- professional recognition received
    
    -- Keywords for Matching
    primary_keywords TEXT[] NOT NULL, -- main keywords
    achievement_keywords TEXT[], -- achievement-specific terms
    expertise_keywords TEXT[], -- expertise areas demonstrated
    
    -- Display & Selection
    display_order INTEGER DEFAULT 0, -- order within the certification
    is_featured BOOLEAN DEFAULT false, -- highlight this achievement
    show_by_default BOOLEAN DEFAULT true, -- include in standard display
    professional_impact_score DECIMAL(3,2) DEFAULT 0.5, -- professional impact (0-1)
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- RESUME CERTIFICATION SELECTIONS
-- =====================================================

CREATE TABLE resume_certification_selections (
    selection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID NOT NULL REFERENCES generated_resumes(resume_id) ON DELETE CASCADE,
    certification_id UUID NOT NULL REFERENCES certifications(certification_id) ON DELETE CASCADE,
    
    -- Selection Configuration
    is_included BOOLEAN NOT NULL DEFAULT true, -- whether to include this certification
    display_order INTEGER, -- order in certifications section
    
    -- Display Options
    show_expiration_date BOOLEAN DEFAULT true, -- show expiration date
    show_credential_id BOOLEAN DEFAULT false, -- show credential ID
    show_issuing_organization BOOLEAN DEFAULT true, -- show issuing organization
    show_specialization BOOLEAN DEFAULT false, -- show specialization details
    show_achievements BOOLEAN DEFAULT false, -- show related achievements
    selected_achievements UUID[], -- specific achievements to highlight
    
    -- Formatting Options
    display_format VARCHAR(30) DEFAULT 'standard', -- standard, condensed, detailed
    max_achievements INTEGER DEFAULT 2, -- limit achievements shown
    
    -- Context & Value
    inclusion_reason VARCHAR(100), -- why this certification was included
    adds_value_because TEXT, -- explanation of value for this specific resume
    demonstrates_competency TEXT[], -- competencies this certification demonstrates
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- JOB-CERTIFICATION RELEVANCE SCORING
-- =====================================================

CREATE TABLE job_certification_relevance (
    relevance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    certification_id UUID NOT NULL REFERENCES certifications(certification_id) ON DELETE CASCADE,
    
    -- Relevance Scores
    skill_alignment_score DECIMAL(4,3) NOT NULL, -- skills validated vs job requirements
    industry_relevance_score DECIMAL(4,3) NOT NULL, -- industry alignment
    role_relevance_score DECIMAL(4,3) NOT NULL, -- job role alignment
    vendor_alignment_score DECIMAL(4,3) NOT NULL, -- vendor/technology alignment
    compliance_value_score DECIMAL(4,3) NOT NULL, -- compliance/regulatory value
    
    -- Composite Score
    overall_relevance_score DECIMAL(4,3) NOT NULL, -- weighted combination
    inclusion_recommendation VARCHAR(30) NOT NULL, -- include, exclude, optional
    
    -- Match Context
    relevant_skills TEXT[], -- skills from certification that match job
    demonstrates_competencies TEXT[], -- competencies this certification demonstrates
    vendor_advantages TEXT[], -- vendor-specific advantages
    compliance_advantages TEXT[], -- compliance/regulatory advantages
    career_advancement_value TEXT, -- how this certification supports career goals
    relevance_reasoning TEXT, -- why this certification is/isn't relevant
    
    -- Display Recommendations
    recommend_show_expiration BOOLEAN DEFAULT true, -- recommend showing expiration
    recommend_show_specialization BOOLEAN DEFAULT false, -- recommend showing specialization
    recommend_highlight_achievements BOOLEAN DEFAULT false, -- recommend highlighting achievements
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- FUNCTIONS FOR CERTIFICATION MANAGEMENT
-- =====================================================

-- Function to get recommended certifications for a job
CREATE OR REPLACE FUNCTION get_recommended_certifications(
    p_profile_id UUID,
    p_job_id UUID,
    p_min_relevance DECIMAL DEFAULT 0.3
)
RETURNS TABLE (
    certification_id UUID,
    certification_name VARCHAR,
    certification_code VARCHAR,
    issuing_organization VARCHAR,
    relevance_score DECIMAL,
    inclusion_recommendation VARCHAR,
    relevant_skills TEXT[],
    demonstrates_competencies TEXT[],
    reasoning TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.certification_id,
        c.certification_name,
        c.certification_code,
        c.issuing_organization,
        jcr.overall_relevance_score,
        jcr.inclusion_recommendation,
        jcr.relevant_skills,
        jcr.demonstrates_competencies,
        jcr.relevance_reasoning
    FROM certifications c
    JOIN job_certification_relevance jcr ON c.certification_id = jcr.certification_id
    WHERE jcr.profile_id = p_profile_id 
    AND jcr.job_id = p_job_id
    AND c.certification_status = 'active'
    AND c.is_active = true
    AND jcr.overall_relevance_score >= p_min_relevance
    ORDER BY jcr.overall_relevance_score DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get certification achievements for resume
CREATE OR REPLACE FUNCTION get_certification_achievements_for_resume(
    p_certification_id UUID,
    p_job_context VARCHAR DEFAULT NULL,
    p_max_achievements INTEGER DEFAULT 2
)
RETURNS TABLE (
    achievement_id UUID,
    achievement_text TEXT,
    achievement_category VARCHAR,
    demonstrates_expertise TEXT[],
    professional_impact_score DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ca.achievement_id,
        ca.achievement_text,
        ca.achievement_category,
        ca.demonstrates_expertise,
        ca.professional_impact_score
    FROM certification_achievements ca
    WHERE ca.certification_id = p_certification_id
    AND ca.show_by_default = true
    AND (
        p_job_context IS NULL OR
        (p_job_context = 'technical' AND ca.achievement_category IN ('exam_performance', 'specialization')) OR
        (p_job_context = 'management' AND ca.achievement_category IN ('recognition', 'renewal')) OR
        (p_job_context = 'compliance' AND ca.achievement_category IN ('specialization', 'recognition'))
    )
    ORDER BY 
        ca.is_featured DESC,
        ca.professional_impact_score DESC,
        ca.display_order ASC
    LIMIT p_max_achievements;
END;
$$ LANGUAGE plpgsql;

-- Function to check certification expiration status
CREATE OR REPLACE FUNCTION check_certification_expiration_status(
    p_profile_id UUID
)
RETURNS TABLE (
    certification_id UUID,
    certification_name VARCHAR,
    expiration_date DATE,
    days_until_expiration INTEGER,
    renewal_required BOOLEAN,
    status VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.certification_id,
        c.certification_name,
        c.expiration_date,
        CASE 
            WHEN c.expiration_date IS NULL THEN NULL
            ELSE (c.expiration_date - CURRENT_DATE)::INTEGER
        END as days_until_expiration,
        c.renewal_required,
        CASE 
            WHEN c.expiration_date IS NULL THEN 'no_expiration'
            WHEN c.expiration_date < CURRENT_DATE THEN 'expired'
            WHEN c.expiration_date <= CURRENT_DATE + INTERVAL '90 days' THEN 'expiring_soon'
            ELSE 'active'
        END as status
    FROM certifications c
    WHERE c.profile_id = p_profile_id
    AND c.certification_status = 'active'
    ORDER BY 
        CASE 
            WHEN c.expiration_date IS NULL THEN 9999
            ELSE (c.expiration_date - CURRENT_DATE)::INTEGER
        END ASC;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate certification section value for a resume
CREATE OR REPLACE FUNCTION calculate_certification_resume_value(
    p_profile_id UUID,
    p_job_id UUID
)
RETURNS TABLE (
    total_certifications INTEGER,
    active_certifications INTEGER,
    avg_relevance_score DECIMAL,
    recommended_inclusions INTEGER,
    technical_certifications INTEGER,
    management_certifications INTEGER,
    vendor_certifications INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_certifications,
        COUNT(CASE WHEN c.is_active = true THEN 1 END)::INTEGER as active_certifications,
        AVG(jcr.overall_relevance_score) as avg_relevance_score,
        COUNT(CASE WHEN jcr.inclusion_recommendation = 'include' THEN 1 END)::INTEGER as recommended_inclusions,
        COUNT(CASE WHEN c.certification_type = 'technical' THEN 1 END)::INTEGER as technical_certifications,
        COUNT(CASE WHEN c.certification_type = 'professional' THEN 1 END)::INTEGER as management_certifications,
        COUNT(CASE WHEN c.certification_type = 'vendor' THEN 1 END)::INTEGER as vendor_certifications
    FROM certifications c
    JOIN job_certification_relevance jcr ON c.certification_id = jcr.certification_id
    WHERE jcr.profile_id = p_profile_id 
    AND jcr.job_id = p_job_id
    AND c.certification_status = 'active';
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Certifications indexes
CREATE INDEX idx_certifications_profile_id ON certifications(profile_id);
CREATE INDEX idx_certifications_name ON certifications(certification_name);
CREATE INDEX idx_certifications_organization ON certifications(issuing_organization);
CREATE INDEX idx_certifications_type ON certifications(certification_type);
CREATE INDEX idx_certifications_expiration ON certifications(expiration_date);
CREATE INDEX idx_certifications_keywords ON certifications USING GIN(primary_keywords);
CREATE INDEX idx_certifications_skills ON certifications USING GIN(skills_validated);
CREATE INDEX idx_certifications_status ON certifications(certification_status, is_active);
CREATE INDEX idx_certifications_featured ON certifications(is_featured);

-- Certification achievements indexes
CREATE INDEX idx_certification_achievements_certification_id ON certification_achievements(certification_id);
CREATE INDEX idx_certification_achievements_category ON certification_achievements(achievement_category);
CREATE INDEX idx_certification_achievements_featured ON certification_achievements(is_featured);
CREATE INDEX idx_certification_achievements_impact ON certification_achievements(professional_impact_score DESC);

-- Selection and relevance indexes
CREATE INDEX idx_resume_certification_selections_resume_id ON resume_certification_selections(resume_id);
CREATE INDEX idx_resume_certification_selections_included ON resume_certification_selections(is_included);
CREATE INDEX idx_job_certification_relevance_profile_job ON job_certification_relevance(profile_id, job_id);
CREATE INDEX idx_job_certification_relevance_score ON job_certification_relevance(overall_relevance_score DESC);

-- =====================================================
-- ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE certifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE certification_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_certification_selections ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_certification_relevance ENABLE ROW LEVEL SECURITY;

-- Policies for certification data
CREATE POLICY "Users can manage own certifications" ON certifications FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own certification achievements" ON certification_achievements FOR ALL USING (
    certification_id IN (
        SELECT certification_id FROM certifications 
        WHERE profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
    )
);

CREATE POLICY "Users can manage own certification selections" ON resume_certification_selections FOR ALL USING (
    resume_id IN (
        SELECT resume_id FROM generated_resumes 
        WHERE profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
    )
);

CREATE POLICY "Users can view own certification relevance" ON job_certification_relevance FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

-- =====================================================
-- SAMPLE DATA STRUCTURE FOR ALLEN WALKER'S CERTIFICATIONS
-- =====================================================

-- Example: How Allen's certifications would be structured

/*
-- Example Certification Entry
INSERT INTO certifications (
    profile_id, certification_name, certification_code, issuing_organization, certification_type,
    certification_level, specialization, certification_description,
    issue_date, expiration_date, renewal_required, renewal_period_months,
    credential_id, verification_url,
    skills_validated, technical_skills, knowledge_areas, competency_level,
    industry_relevance, job_roles_relevant, career_impact,
    preparation_hours, exam_score, exam_passing_score,
    primary_keywords, technical_keywords, vendor_keywords,
    include_for_technical_roles, include_for_management_roles,
    is_featured, priority_level
) VALUES (
    'allen_profile_id',
    'Project Management Professional',
    'PMP',
    'Project Management Institute (PMI)',
    'professional',
    'professional',
    'Healthcare IT Project Management',
    'Globally recognized certification demonstrating competency in project management across industries, with specialization in healthcare IT implementations.',
    '2019-03-15',
    '2025-03-15',
    true,
    36, -- 3 years
    'PMP-2019-12345',
    'https://www.pmi.org/certifications/verify',
    ARRAY['Project Management', 'Risk Management', 'Stakeholder Management', 'Schedule Management', 'Budget Management'],
    ARRAY['MS Project', 'Agile Methodologies', 'Waterfall', 'Risk Assessment Tools'],
    ARRAY['Project Integration', 'Scope Management', 'Time Management', 'Cost Management', 'Quality Management'],
    'expert',
    ARRAY['Healthcare', 'Technology', 'Financial Services', 'Manufacturing'],
    ARRAY['Project Manager', 'Program Manager', 'IT Manager', 'Operations Manager'],
    'Validates project management expertise and significantly enhances credibility for program management roles',
    120, -- hours of preparation
    285, -- exam score
    175, -- passing score
    ARRAY['pmp', 'project management', 'pmi', 'project manager'],
    ARRAY['project management', 'risk management', 'agile', 'waterfall'],
    ARRAY['pmi', 'project management institute'],
    false, -- not specifically technical
    true,  -- include for management roles
    true,  -- featured certification
    'high'
);

-- Sample certification achievements
INSERT INTO certification_achievements (
    certification_id, achievement_text, achievement_category,
    demonstrates_expertise, professional_impact_score,
    primary_keywords, is_featured
) VALUES
('certification_id', 'Achieved PMP certification on first attempt with score of 285/300 (95th percentile)', 'exam_performance',
ARRAY['Project Management Excellence', 'First-Attempt Success', 'High Performance'],
0.9,
ARRAY['pmp', 'first attempt', 'high score', '95th percentile'],
true),

('certification_id', 'Maintained PMP certification through continuous professional development and renewal cycles since 2019', 'renewal',
ARRAY['Continuous Learning', 'Professional Development', 'Commitment to Excellence'],
0.7,
ARRAY['continuous learning', 'professional development', 'certification maintenance'],
false);
*/
