-- =====================================================
-- EDUCATION SCHEMA
-- Comprehensive education tracking for degrees, certifications, and continuous learning
-- =====================================================

-- =====================================================
-- EDUCATION TABLE
-- =====================================================

CREATE TABLE education (
    education_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    
    -- Core Education Information
    institution VARCHAR(200) NOT NULL, -- university, college, school name
    degree_type VARCHAR(50) NOT NULL, -- bachelors, masters, doctorate, certificate, diploma, professional
    degree_name VARCHAR(200) NOT NULL, -- specific degree or program name
    field_of_study VARCHAR(200), -- major, concentration, specialization
    minor_field VARCHAR(200), -- minor or secondary field
    
    -- Dates & Duration
    start_date DATE,
    end_date DATE, -- NULL for in progress
    graduation_date DATE, -- actual graduation date (may differ from end_date)
    is_in_progress BOOLEAN DEFAULT false,
    expected_completion DATE, -- for in-progress education
    
    -- Location & Format
    location VARCHAR(100), -- city, state, country
    education_format VARCHAR(30) DEFAULT 'in_person', -- in_person, online, hybrid, correspondence
    
    -- Academic Performance
    gpa DECIMAL(3,2), -- grade point average
    gpa_scale DECIMAL(3,1) DEFAULT 4.0, -- scale (4.0, 5.0, etc.)
    honors TEXT[], -- magna cum laude, dean's list, etc.
    class_rank INTEGER, -- ranking in class
    class_size INTEGER, -- total class size
    
    -- Academic Achievements
    thesis_title TEXT, -- thesis or capstone project title
    thesis_description TEXT, -- brief description of thesis work
    academic_projects TEXT[], -- notable academic projects
    research_areas TEXT[], -- research focus areas
    publications TEXT[], -- academic publications
    
    -- Relevant Coursework
    relevant_coursework TEXT[], -- courses relevant to career
    technical_coursework TEXT[], -- technical/specialized courses
    leadership_activities TEXT[], -- student government, clubs, etc.
    extracurricular_activities TEXT[], -- sports, organizations, etc.
    
    -- Skills & Knowledge Gained
    skills_acquired TEXT[] NOT NULL, -- skills gained through education
    technical_skills TEXT[], -- technical skills learned
    software_tools TEXT[], -- software/tools learned
    programming_languages TEXT[], -- programming languages learned
    methodologies TEXT[], -- methodologies or frameworks learned
    
    -- Professional Relevance
    career_relevance TEXT, -- how this education relates to career goals
    industry_alignment TEXT[], -- industries where this education is valuable
    job_relevance_keywords TEXT[], -- keywords for job matching
    transferable_knowledge TEXT[], -- knowledge that transfers across roles
    
    -- Certifications & Credentials
    certifications_earned TEXT[], -- certifications obtained during program
    professional_licenses TEXT[], -- licenses earned
    credential_numbers TEXT[], -- certification/license numbers
    
    -- Display & Inclusion Control
    display_order INTEGER DEFAULT 0, -- order among education entries
    is_primary_education BOOLEAN DEFAULT false, -- main/highest degree
    show_gpa BOOLEAN DEFAULT false, -- whether to display GPA
    show_coursework BOOLEAN DEFAULT false, -- whether to show relevant coursework
    show_activities BOOLEAN DEFAULT false, -- whether to show extracurriculars
    
    -- Keywords for Matching
    primary_keywords TEXT[] NOT NULL, -- main keywords for job matching
    degree_keywords TEXT[], -- degree-specific keywords
    institution_keywords TEXT[], -- institution-specific keywords
    skill_keywords TEXT[], -- skill-based keywords
    
    -- Status & Metadata
    education_status VARCHAR(20) DEFAULT 'completed', -- completed, in_progress, transferred, incomplete
    is_featured BOOLEAN DEFAULT false, -- highlight this education
    verification_status VARCHAR(20) DEFAULT 'unverified', -- verified, unverified, pending
    notes TEXT, -- internal notes
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- EDUCATION ACHIEVEMENTS
-- =====================================================

CREATE TABLE education_achievements (
    achievement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    education_id UUID NOT NULL REFERENCES education(education_id) ON DELETE CASCADE,
    
    -- Achievement Details
    achievement_text TEXT NOT NULL,
    achievement_category VARCHAR(50) NOT NULL, -- academic, leadership, research, project, award, scholarship
    
    -- Achievement Context
    achievement_date DATE, -- when achievement occurred
    recognition_level VARCHAR(30), -- institutional, departmental, national, international
    achievement_description TEXT, -- detailed description
    
    -- Skills & Impact
    skills_demonstrated TEXT[] NOT NULL, -- skills shown through this achievement
    impact_description TEXT, -- impact or significance of achievement
    quantified_results TEXT[], -- measurable outcomes
    
    -- Professional Relevance
    professional_relevance TEXT, -- how this relates to professional capabilities
    demonstrates_qualities TEXT[], -- personal/professional qualities demonstrated
    transferable_to_roles TEXT[], -- types of roles where this achievement is relevant
    
    -- Keywords for Matching
    primary_keywords TEXT[] NOT NULL, -- main keywords
    achievement_keywords TEXT[], -- achievement-specific terms
    skill_keywords TEXT[], -- skills demonstrated
    
    -- Display & Selection
    display_order INTEGER DEFAULT 0, -- order within the education entry
    is_featured BOOLEAN DEFAULT false, -- highlight this achievement
    show_by_default BOOLEAN DEFAULT true, -- include in standard display
    professional_relevance_score DECIMAL(3,2) DEFAULT 0.5, -- professional relevance (0-1)
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- RESUME EDUCATION SELECTIONS
-- =====================================================

CREATE TABLE resume_education_selections (
    selection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID NOT NULL REFERENCES generated_resumes(resume_id) ON DELETE CASCADE,
    education_id UUID NOT NULL REFERENCES education(education_id) ON DELETE CASCADE,
    
    -- Selection Configuration
    is_included BOOLEAN NOT NULL DEFAULT true, -- education is typically always included
    display_order INTEGER, -- order in education section
    
    -- Display Options
    show_gpa BOOLEAN DEFAULT false, -- whether to show GPA for this resume
    show_honors BOOLEAN DEFAULT true, -- whether to show honors/awards
    show_coursework BOOLEAN DEFAULT false, -- whether to show relevant coursework
    show_activities BOOLEAN DEFAULT false, -- whether to show extracurricular activities
    show_thesis BOOLEAN DEFAULT false, -- whether to show thesis information
    selected_achievements UUID[], -- specific achievements to highlight
    
    -- Formatting Options
    display_format VARCHAR(30) DEFAULT 'standard', -- standard, condensed, detailed
    max_coursework_items INTEGER DEFAULT 5, -- limit coursework items shown
    max_activities INTEGER DEFAULT 3, -- limit activities shown
    
    -- Context
    inclusion_reason VARCHAR(100), -- why this education entry was configured this way
    adds_value_because TEXT, -- explanation of value for this specific resume
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- JOB-EDUCATION RELEVANCE SCORING
-- =====================================================

CREATE TABLE job_education_relevance (
    relevance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    education_id UUID NOT NULL REFERENCES education(education_id) ON DELETE CASCADE,
    
    -- Relevance Scores
    degree_relevance_score DECIMAL(4,3) NOT NULL, -- how relevant the degree is
    field_alignment_score DECIMAL(4,3) NOT NULL, -- field of study alignment
    institution_prestige_score DECIMAL(4,3) NOT NULL, -- institution recognition/prestige
    skills_alignment_score DECIMAL(4,3) NOT NULL, -- skills learned vs job requirements
    coursework_relevance_score DECIMAL(4,3) NOT NULL, -- relevant coursework alignment
    
    -- Composite Score
    overall_relevance_score DECIMAL(4,3) NOT NULL, -- weighted combination
    display_recommendation VARCHAR(30) NOT NULL, -- standard, detailed, condensed
    
    -- Match Context
    relevant_skills TEXT[], -- skills from education that match job
    relevant_coursework TEXT[], -- coursework relevant to the job
    degree_advantages TEXT[], -- advantages this degree provides for the role
    institution_advantages TEXT[], -- advantages from institution reputation
    relevance_reasoning TEXT, -- why this education is relevant
    
    -- Display Recommendations
    recommend_show_gpa BOOLEAN DEFAULT false, -- recommend showing GPA
    recommend_show_coursework BOOLEAN DEFAULT false, -- recommend showing coursework
    recommend_show_activities BOOLEAN DEFAULT false, -- recommend showing activities
    recommend_show_thesis BOOLEAN DEFAULT false, -- recommend showing thesis
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- FUNCTIONS FOR EDUCATION MANAGEMENT
-- =====================================================

-- Function to get education display recommendations for a job
CREATE OR REPLACE FUNCTION get_education_display_recommendations(
    p_profile_id UUID,
    p_job_id UUID
)
RETURNS TABLE (
    education_id UUID,
    institution VARCHAR,
    degree_name VARCHAR,
    relevance_score DECIMAL,
    display_recommendation VARCHAR,
    recommend_show_gpa BOOLEAN,
    recommend_show_coursework BOOLEAN,
    relevant_skills TEXT[],
    relevant_coursework TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.education_id,
        e.institution,
        e.degree_name,
        jer.overall_relevance_score,
        jer.display_recommendation,
        jer.recommend_show_gpa,
        jer.recommend_show_coursework,
        jer.relevant_skills,
        jer.relevant_coursework
    FROM education e
    JOIN job_education_relevance jer ON e.education_id = jer.education_id
    WHERE jer.profile_id = p_profile_id 
    AND jer.job_id = p_job_id
    AND e.education_status IN ('completed', 'in_progress')
    ORDER BY 
        e.is_primary_education DESC,
        jer.overall_relevance_score DESC,
        e.graduation_date DESC NULLS LAST;
END;
$$ LANGUAGE plpgsql;

-- Function to get education achievements for resume
CREATE OR REPLACE FUNCTION get_education_achievements_for_resume(
    p_education_id UUID,
    p_job_context VARCHAR DEFAULT NULL,
    p_max_achievements INTEGER DEFAULT 3
)
RETURNS TABLE (
    achievement_id UUID,
    achievement_text TEXT,
    achievement_category VARCHAR,
    skills_demonstrated TEXT[],
    professional_relevance TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ea.achievement_id,
        ea.achievement_text,
        ea.achievement_category,
        ea.skills_demonstrated,
        ea.professional_relevance
    FROM education_achievements ea
    WHERE ea.education_id = p_education_id
    AND ea.show_by_default = true
    AND (
        p_job_context IS NULL OR
        (p_job_context = 'technical' AND ea.achievement_category IN ('project', 'research')) OR
        (p_job_context = 'leadership' AND ea.achievement_category IN ('leadership', 'award')) OR
        (p_job_context = 'academic' AND ea.achievement_category IN ('academic', 'research'))
    )
    ORDER BY 
        ea.is_featured DESC,
        ea.professional_relevance_score DESC,
        ea.display_order ASC
    LIMIT p_max_achievements;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate education section value for a resume
CREATE OR REPLACE FUNCTION calculate_education_resume_value(
    p_profile_id UUID,
    p_job_id UUID
)
RETURNS TABLE (
    total_degrees INTEGER,
    avg_relevance_score DECIMAL,
    highest_degree_level VARCHAR,
    most_relevant_institution VARCHAR,
    recommended_display_format VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_degrees,
        AVG(jer.overall_relevance_score) as avg_relevance_score,
        (SELECT e2.degree_type FROM education e2 
         JOIN job_education_relevance jer2 ON e2.education_id = jer2.education_id
         WHERE jer2.profile_id = p_profile_id AND jer2.job_id = p_job_id
         ORDER BY 
           CASE e2.degree_type 
             WHEN 'doctorate' THEN 4
             WHEN 'masters' THEN 3
             WHEN 'bachelors' THEN 2
             ELSE 1
           END DESC
         LIMIT 1) as highest_degree_level,
        (SELECT e3.institution FROM education e3
         JOIN job_education_relevance jer3 ON e3.education_id = jer3.education_id
         WHERE jer3.profile_id = p_profile_id AND jer3.job_id = p_job_id
         ORDER BY jer3.overall_relevance_score DESC
         LIMIT 1) as most_relevant_institution,
        CASE 
          WHEN AVG(jer.overall_relevance_score) > 0.8 THEN 'detailed'
          WHEN AVG(jer.overall_relevance_score) > 0.5 THEN 'standard'
          ELSE 'condensed'
        END as recommended_display_format
    FROM education e
    JOIN job_education_relevance jer ON e.education_id = jer.education_id
    WHERE jer.profile_id = p_profile_id 
    AND jer.job_id = p_job_id
    AND e.education_status IN ('completed', 'in_progress');
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Education indexes
CREATE INDEX idx_education_profile_id ON education(profile_id);
CREATE INDEX idx_education_institution ON education(institution);
CREATE INDEX idx_education_degree_type ON education(degree_type);
CREATE INDEX idx_education_graduation_date ON education(graduation_date DESC NULLS LAST);
CREATE INDEX idx_education_keywords ON education USING GIN(primary_keywords);
CREATE INDEX idx_education_skills ON education USING GIN(skills_acquired);
CREATE INDEX idx_education_status ON education(education_status);
CREATE INDEX idx_education_primary ON education(is_primary_education);

-- Education achievements indexes
CREATE INDEX idx_education_achievements_education_id ON education_achievements(education_id);
CREATE INDEX idx_education_achievements_category ON education_achievements(achievement_category);
CREATE INDEX idx_education_achievements_featured ON education_achievements(is_featured);
CREATE INDEX idx_education_achievements_relevance ON education_achievements(professional_relevance_score DESC);

-- Selection and relevance indexes
CREATE INDEX idx_resume_education_selections_resume_id ON resume_education_selections(resume_id);
CREATE INDEX idx_job_education_relevance_profile_job ON job_education_relevance(profile_id, job_id);
CREATE INDEX idx_job_education_relevance_score ON job_education_relevance(overall_relevance_score DESC);

-- =====================================================
-- ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE education ENABLE ROW LEVEL SECURITY;
ALTER TABLE education_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_education_selections ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_education_relevance ENABLE ROW LEVEL SECURITY;

-- Policies for education data
CREATE POLICY "Users can manage own education" ON education FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

CREATE POLICY "Users can manage own education achievements" ON education_achievements FOR ALL USING (
    education_id IN (
        SELECT education_id FROM education 
        WHERE profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
    )
);

CREATE POLICY "Users can manage own education selections" ON resume_education_selections FOR ALL USING (
    resume_id IN (
        SELECT resume_id FROM generated_resumes 
        WHERE profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
    )
);

CREATE POLICY "Users can view own education relevance" ON job_education_relevance FOR ALL USING (
    profile_id IN (SELECT profile_id FROM candidate_profiles WHERE user_id = auth.uid())
);

-- =====================================================
-- SAMPLE DATA STRUCTURE FOR ALLEN WALKER'S EDUCATION
-- =====================================================

-- Example: How Allen's education would be structured

/*
-- Example Education Entry
INSERT INTO education (
    profile_id, institution, degree_type, degree_name, field_of_study,
    start_date, end_date, graduation_date, location, education_format,
    gpa, honors, relevant_coursework, technical_coursework,
    skills_acquired, technical_skills, career_relevance,
    industry_alignment, job_relevance_keywords,
    primary_keywords, degree_keywords, skill_keywords,
    is_primary_education, show_gpa, show_coursework
) VALUES (
    'allen_profile_id',
    'University of California, Los Angeles (UCLA)',
    'bachelors',
    'Bachelor of Arts in Business Economics',
    'Business Economics',
    '1998-09-01',
    '2002-06-01',
    '2002-06-15',
    'Los Angeles, CA',
    'in_person',
    3.4,
    ARRAY['Dean''s List (2 semesters)'],
    ARRAY[
        'Operations Management',
        'Project Management',
        'Business Process Analysis',
        'Financial Analysis',
        'Strategic Management',
        'Information Systems Management'
    ],
    ARRAY[
        'Management Information Systems',
        'Database Management',
        'Business Process Modeling',
        'Statistical Analysis'
    ],
    ARRAY['Business Analysis', 'Project Management', 'Financial Analysis', 'Strategic Planning', 'Process Optimization'],
    ARRAY['Excel', 'Access', 'Statistical Software', 'Business Process Modeling'],
    'Provides foundational business and analytical skills that support program management and strategic roles across industries',
    ARRAY['Healthcare', 'Technology', 'Financial Services', 'Consulting'],
    ARRAY['business economics', 'project management', 'operations', 'analysis', 'strategic planning'],
    ARRAY['business economics', 'ucla', 'bachelor of arts', 'operations management'],
    ARRAY['ucla', 'university of california'],
    ARRAY['business analysis', 'project management', 'financial analysis', 'strategic planning'],
    true, -- primary education
    false, -- don't show GPA by default
    true  -- show relevant coursework
);

-- Sample education achievements
INSERT INTO education_achievements (
    education_id, achievement_text, achievement_category,
    skills_demonstrated, professional_relevance, demonstrates_qualities,
    primary_keywords, is_featured, professional_relevance_score
) VALUES
('education_id', 'Dean''s List recognition for academic excellence (2 semesters)', 'academic',
ARRAY['Academic Excellence', 'Time Management', 'Analytical Thinking'],
'Demonstrates consistent high performance and ability to excel under pressure',
ARRAY['Excellence', 'Consistency', 'Academic Rigor'],
ARRAY['dean''s list', 'academic excellence', 'high performance'],
true, 0.7),

('education_id', 'Completed capstone project analyzing operational efficiency improvements for local healthcare system', 'project',
ARRAY['Business Analysis', 'Healthcare Operations', 'Process Improvement'],
'Shows early interest and capability in healthcare operations and process optimization',
ARRAY['Analytical Thinking', 'Healthcare Focus', 'Process Improvement'],
ARRAY['capstone project', 'healthcare operations', 'process improvement'],
true, 0.9);
*/
