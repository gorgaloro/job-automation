-- Supabase Resume Optimizer Tables
-- Based on comprehensive schemas from memories
-- Created: 2025-07-27

-- Enable RLS (Row Level Security) for all tables
-- You can adjust policies as needed

-- 1. Personal Information
CREATE TABLE personal_info (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    name TEXT NOT NULL,
    location TEXT,
    phone TEXT,
    email TEXT,
    linkedin TEXT,
    portfolio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Executive Summaries (with versioning)
CREATE TABLE executive_summaries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    version INTEGER DEFAULT 1,
    content TEXT NOT NULL,
    target_context TEXT, -- job type, industry, etc.
    score DECIMAL(3,3) DEFAULT 0.000,
    quality_score DECIMAL(3,3) DEFAULT 0.000,
    keyword_density DECIMAL(3,3) DEFAULT 0.000,
    readability_score DECIMAL(3,3) DEFAULT 0.000,
    impact_score DECIMAL(3,3) DEFAULT 0.000,
    usage_count INTEGER DEFAULT 0,
    success_rate DECIMAL(3,3) DEFAULT 0.000,
    avg_response_time DECIMAL(5,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Strategic Impact (bullet points)
CREATE TABLE strategic_impact (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    text TEXT NOT NULL,
    score DECIMAL(3,3) DEFAULT 0.000,
    categories TEXT[] DEFAULT '{}',
    keywords TEXT[] DEFAULT '{}',
    impact_metrics JSONB DEFAULT '{}',
    selected BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Employment History (main jobs)
CREATE TABLE employment_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    start_date TEXT, -- Using TEXT for flexibility (e.g., "2019", "Jan 2019")
    end_date TEXT,
    employment_type TEXT DEFAULT 'professional_experience', -- professional_experience, early_career_experience, additional_experience
    selected BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Employment Bullet Points (granular bullet-level optimization)
CREATE TABLE employment_bullet_points (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    employment_id UUID REFERENCES employment_history(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id),
    text TEXT NOT NULL,
    category TEXT DEFAULT 'General', -- Achievement, Leadership, Technical, Process Improvement, etc.
    score DECIMAL(3,3) DEFAULT 0.000,
    keywords TEXT[] DEFAULT '{}',
    skills TEXT[] DEFAULT '{}',
    impact_metrics JSONB DEFAULT '{}',
    selected BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Community Leadership & Networks
CREATE TABLE community_leadership (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    title TEXT NOT NULL, -- Role/position
    company TEXT NOT NULL, -- Organization name
    location TEXT,
    start_date TEXT,
    end_date TEXT,
    leadership_level TEXT DEFAULT 'member', -- executive, board, committee, team_lead, member
    team_size INTEGER DEFAULT 0,
    budget_responsibility DECIMAL(12,2) DEFAULT 0.00,
    selected BOOLEAN DEFAULT FALSE, -- Checkbox control
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. Community Leadership Achievements
CREATE TABLE community_leadership_achievements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    community_leadership_id UUID REFERENCES community_leadership(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id),
    text TEXT NOT NULL,
    category TEXT DEFAULT 'Leadership',
    score DECIMAL(3,3) DEFAULT 0.000,
    impact_metrics JSONB DEFAULT '{}',
    selected BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. Skills & Expertise
CREATE TABLE skills (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    skill TEXT NOT NULL,
    category TEXT DEFAULT 'core', -- core, technical, soft
    proficiency_level TEXT DEFAULT 'intermediate', -- beginner, intermediate, advanced, expert
    relevance DECIMAL(3,3) DEFAULT 0.000,
    years_experience INTEGER DEFAULT 0,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. Education
CREATE TABLE education (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    degree TEXT NOT NULL,
    field_of_study TEXT,
    school TEXT NOT NULL,
    location TEXT,
    graduation_year TEXT,
    gpa DECIMAL(3,2),
    honors TEXT[] DEFAULT '{}',
    relevant_coursework TEXT[] DEFAULT '{}',
    thesis_title TEXT,
    research_projects TEXT[] DEFAULT '{}',
    skills_acquired TEXT[] DEFAULT '{}',
    show_gpa BOOLEAN DEFAULT FALSE,
    show_honors BOOLEAN DEFAULT TRUE,
    show_coursework BOOLEAN DEFAULT FALSE,
    display_format TEXT DEFAULT 'standard', -- standard, detailed, condensed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 10. Certifications
CREATE TABLE certifications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    name TEXT NOT NULL,
    code TEXT, -- certification code/ID
    issuer TEXT NOT NULL,
    certification_type TEXT DEFAULT 'professional', -- professional, technical, vendor, regulatory
    level TEXT DEFAULT 'standard', -- foundation, associate, professional, expert, master
    issue_date DATE,
    expiration_date DATE,
    renewal_date DATE,
    credential_id TEXT,
    verification_url TEXT,
    digital_badge_url TEXT,
    certificate_file_url TEXT,
    skills_validated TEXT[] DEFAULT '{}',
    industry_relevance TEXT[] DEFAULT '{}',
    status TEXT DEFAULT 'active', -- active, expired, expiring_soon, no_expiration
    show_expiration BOOLEAN DEFAULT TRUE,
    show_credential_id BOOLEAN DEFAULT FALSE,
    display_format TEXT DEFAULT 'standard', -- standard, detailed, condensed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 11. Job Analysis Data (for optimization context)
CREATE TABLE job_analyses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    job_title TEXT NOT NULL,
    company_name TEXT NOT NULL,
    job_location TEXT,
    job_description TEXT,
    company_summary JSONB DEFAULT '{}',
    keyword_analysis JSONB DEFAULT '{}',
    job_summary JSONB DEFAULT '{}',
    overall_score DECIMAL(3,3) DEFAULT 0.000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 12. Section Scores (for resume optimization)
CREATE TABLE section_scores (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    job_analysis_id UUID REFERENCES job_analyses(id),
    professional_experience DECIMAL(3,3) DEFAULT 0.000,
    early_career_experience DECIMAL(3,3) DEFAULT 0.000,
    additional_experience DECIMAL(3,3) DEFAULT 0.000,
    community_leadership DECIMAL(3,3) DEFAULT 0.000,
    strategic_impact DECIMAL(3,3) DEFAULT 0.000,
    skills DECIMAL(3,3) DEFAULT 0.000,
    education DECIMAL(3,3) DEFAULT 0.000,
    certifications DECIMAL(3,3) DEFAULT 0.000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE personal_info ENABLE ROW LEVEL SECURITY;
ALTER TABLE executive_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategic_impact ENABLE ROW LEVEL SECURITY;
ALTER TABLE employment_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE employment_bullet_points ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_leadership ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_leadership_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE education ENABLE ROW LEVEL SECURITY;
ALTER TABLE certifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE section_scores ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (users can only access their own data)
CREATE POLICY "Users can view own personal_info" ON personal_info FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own personal_info" ON personal_info FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own personal_info" ON personal_info FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own executive_summaries" ON executive_summaries FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own executive_summaries" ON executive_summaries FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own executive_summaries" ON executive_summaries FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own strategic_impact" ON strategic_impact FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own strategic_impact" ON strategic_impact FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own strategic_impact" ON strategic_impact FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own employment_history" ON employment_history FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own employment_history" ON employment_history FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own employment_history" ON employment_history FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own employment_bullet_points" ON employment_bullet_points FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own employment_bullet_points" ON employment_bullet_points FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own employment_bullet_points" ON employment_bullet_points FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own community_leadership" ON community_leadership FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own community_leadership" ON community_leadership FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own community_leadership" ON community_leadership FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own community_leadership_achievements" ON community_leadership_achievements FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own community_leadership_achievements" ON community_leadership_achievements FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own community_leadership_achievements" ON community_leadership_achievements FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own skills" ON skills FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own skills" ON skills FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own skills" ON skills FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own education" ON education FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own education" ON education FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own education" ON education FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own certifications" ON certifications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own certifications" ON certifications FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own certifications" ON certifications FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own job_analyses" ON job_analyses FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own job_analyses" ON job_analyses FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own job_analyses" ON job_analyses FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own section_scores" ON section_scores FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own section_scores" ON section_scores FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own section_scores" ON section_scores FOR UPDATE USING (auth.uid() = user_id);

-- Create indexes for better performance
CREATE INDEX idx_employment_history_user_id ON employment_history(user_id);
CREATE INDEX idx_employment_history_type ON employment_history(employment_type);
CREATE INDEX idx_employment_bullet_points_employment_id ON employment_bullet_points(employment_id);
CREATE INDEX idx_employment_bullet_points_user_id ON employment_bullet_points(user_id);
CREATE INDEX idx_strategic_impact_user_id ON strategic_impact(user_id);
CREATE INDEX idx_community_leadership_user_id ON community_leadership(user_id);
CREATE INDEX idx_skills_user_id ON skills(user_id);
CREATE INDEX idx_education_user_id ON education(user_id);
CREATE INDEX idx_certifications_user_id ON certifications(user_id);
CREATE INDEX idx_job_analyses_user_id ON job_analyses(user_id);
CREATE INDEX idx_section_scores_user_id ON section_scores(user_id);

-- Add helpful comments
COMMENT ON TABLE personal_info IS 'Core personal/contact information for resume header';
COMMENT ON TABLE executive_summaries IS 'Versioned executive summaries with performance tracking';
COMMENT ON TABLE strategic_impact IS 'High-level strategic achievements and impact statements';
COMMENT ON TABLE employment_history IS 'Job history with flexible employment types';
COMMENT ON TABLE employment_bullet_points IS 'Granular bullet points with scoring for optimization';
COMMENT ON TABLE community_leadership IS 'Professional community involvement and leadership roles';
COMMENT ON TABLE skills IS 'Technical and soft skills with proficiency levels';
COMMENT ON TABLE education IS 'Educational background with flexible display options';
COMMENT ON TABLE certifications IS 'Professional certifications with expiration tracking';
COMMENT ON TABLE job_analyses IS 'Job posting analysis for resume optimization';
COMMENT ON TABLE section_scores IS 'Section-level scoring for resume optimization';
