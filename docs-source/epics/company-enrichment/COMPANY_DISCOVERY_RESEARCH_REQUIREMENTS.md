# Company Discovery & Research Dashboard - Requirements Document

## Overview
The Company Discovery & Research Dashboard serves as the central hub for discovering, researching, and analyzing target companies for job search opportunities. This module leverages the existing robust company enrichment infrastructure (Clearbit, ZoomInfo, Apollo APIs) to provide comprehensive company intelligence and research workflows.

## 🎯 **Core Objectives**

### **Primary Goals**
1. **Smart Company Discovery** - AI-powered company recommendations based on user profile and preferences
2. **Comprehensive Research Workspace** - Centralized research environment with enriched company data
3. **Competitive Intelligence** - Company comparison tools and market positioning analysis
4. **Opportunity Identification** - Job opening detection and hiring pattern analysis
5. **Research Workflow Management** - Structured research processes with progress tracking

### **User Value Proposition**
- **Reduce research time** from hours to minutes per company
- **Increase research quality** with multi-source data enrichment
- **Identify hidden opportunities** through AI-powered discovery
- **Make informed decisions** with comprehensive company intelligence
- **Track research progress** with organized workflows and notes

---

## 🏗️ **Existing Infrastructure Analysis**

### **✅ STRONG FOUNDATION - Already Built**

#### **Company Enrichment APIs** (Production Ready)
- **Location**: `/src/integrations/company_enrichment_apis.py`
- **APIs Integrated**: Clearbit, ZoomInfo, Apollo
- **Features**: 
  - Normalized company data structure
  - Multi-API fallback system
  - Batch enrichment capabilities
  - Async processing for performance

#### **Data Structure** (CompanyData class)
```python
@dataclass
class CompanyData:
    name: str
    domain: str
    description: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    founded_year: Optional[int] = None
    revenue: Optional[str] = None
    funding: Optional[str] = None
    technologies: Optional[List[str]] = None
    social_media: Optional[Dict[str, str]] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    source_api: str = None
    confidence_score: Optional[float] = None
    raw_data: Optional[Dict] = None
```

#### **Service Layer** (CompanyEnrichmentService)
- Multi-API orchestration with priority fallback
- Error handling and logging
- Batch processing capabilities
- Demo/testing functions

### **🔄 NEEDS ENHANCEMENT - Build Upon Existing**

#### **Database Integration**
- **Current**: In-memory processing only
- **Needed**: Supabase integration for persistent storage, research tracking, notes

#### **AI-Powered Discovery**
- **Current**: Manual company lookup by domain/name
- **Needed**: AI recommendations based on user profile, job preferences, career goals

#### **Research Workflow Management**
- **Current**: Basic data enrichment
- **Needed**: Research templates, progress tracking, note-taking, collaboration

---

## 📊 **Dashboard Module Specifications**

### **1. Company Discovery Engine**

#### **Smart Discovery Features**
- **AI-Powered Recommendations**: Companies matching user profile and preferences
- **Industry Exploration**: Discover companies within target industries
- **Growth Stage Filtering**: Startups, scale-ups, enterprise, public companies
- **Location-Based Discovery**: Companies in target geographic areas
- **Technology Stack Matching**: Companies using specific technologies or tools

#### **Discovery Criteria**
```typescript
interface DiscoveryFilters {
  industries: string[]
  companySize: string[]  // "1-10", "11-50", "51-200", "201-1000", "1000+"
  locations: string[]
  fundingStage: string[]  // "seed", "series-a", "series-b", "ipo", "public"
  technologies: string[]
  revenueRange: string[]
  foundedYear: { min: number, max: number }
  growthRate: string  // "high", "medium", "stable"
  hiringActivity: string  // "active", "moderate", "low"
}
```

#### **Discovery Sources**
- **Existing APIs**: Clearbit, ZoomInfo, Apollo for company data
- **Job Board Integration**: Companies actively hiring (from job board APIs)
- **News & Funding Data**: Companies with recent funding, acquisitions, expansions
- **Network Analysis**: Companies where user has connections (LinkedIn integration)

### **2. Research Workspace**

#### **Company Profile View**
- **Header Section**: Company logo, name, tagline, key metrics
- **Overview Tab**: Description, industry, size, location, founding info
- **Financials Tab**: Revenue, funding, valuation, growth metrics
- **Technology Tab**: Tech stack, tools, platforms, integrations
- **People Tab**: Leadership team, key employees, hiring managers
- **News Tab**: Recent news, press releases, funding announcements
- **Jobs Tab**: Current openings, hiring patterns, role analysis
- **Network Tab**: Connections at company, referral opportunities

#### **Research Tools**
- **Note-Taking System**: Rich text notes with tagging and categorization
- **Research Templates**: Structured research checklists and frameworks
- **Comparison Matrix**: Side-by-side company comparisons
- **Opportunity Scoring**: AI-powered fit analysis and opportunity ranking
- **Progress Tracking**: Research completion status and next steps

#### **Data Visualization**
- **Company Timeline**: Funding rounds, key milestones, growth events
- **Competitive Landscape**: Market positioning and competitor analysis
- **Growth Metrics**: Revenue, employee count, market share trends
- **Technology Adoption**: Tech stack evolution and platform usage

### **3. Company Comparison Tools**

#### **Comparison Matrix**
```typescript
interface CompanyComparison {
  companies: CompanyData[]
  criteria: {
    culture: { weight: number, scores: number[] }
    compensation: { weight: number, scores: number[] }
    growth: { weight: number, scores: number[] }
    technology: { weight: number, scores: number[] }
    workLifeBalance: { weight: number, scores: number[] }
    careerGrowth: { weight: number, scores: number[] }
  }
  overallScores: number[]
  recommendations: string[]
}
```

#### **Comparison Features**
- **Multi-Criteria Analysis**: Weighted scoring across multiple dimensions
- **Visual Comparisons**: Charts, graphs, and visual indicators
- **Pros/Cons Analysis**: Structured advantage/disadvantage breakdown
- **Decision Framework**: Guided decision-making with recommendations
- **Export Options**: PDF reports, spreadsheet exports, presentation slides

### **4. Market Intelligence**

#### **Industry Analysis**
- **Market Trends**: Industry growth, challenges, opportunities
- **Competitive Landscape**: Key players, market share, positioning
- **Hiring Patterns**: Industry-wide hiring trends and salary data
- **Technology Trends**: Emerging technologies and platform adoption

#### **Company Intelligence**
- **Hiring Activity**: Job posting frequency, role types, growth indicators
- **Financial Health**: Revenue trends, funding status, market performance
- **Leadership Changes**: Executive moves, organizational changes
- **Product Updates**: New features, platform changes, strategic shifts

---

## 🎨 **User Interface Design**

### **Dashboard Layout**
```
┌─────────────────────────────────────────────────────────────┐
│ Company Discovery & Research Dashboard                      │
├─────────────────┬───────────────────────────────────────────┤
│ Discovery Panel │ Research Workspace                        │
│                 │                                           │
│ • Smart Recs    │ ┌─────────────────────────────────────┐   │
│ • Filters       │ │ Company Profile                     │   │
│ • Saved Lists   │ │ ┌─────┬─────┬─────┬─────┬─────┐     │   │
│ • Recent        │ │ │Over │Fin  │Tech │Jobs │News │     │   │
│                 │ │ └─────┴─────┴─────┴─────┴─────┘     │   │
│ ┌─────────────┐ │ │                                     │   │
│ │ Company A   │ │ │ [Company Details Content]           │   │
│ │ ★★★★☆       │ │ │                                     │   │
│ └─────────────┘ │ └─────────────────────────────────────┘   │
│                 │                                           │
│ ┌─────────────┐ │ ┌─────────────────────────────────────┐   │
│ │ Company B   │ │ │ Research Notes & Tools              │   │
│ │ ★★★☆☆       │ │ │ • Notes • Templates • Comparison   │   │
│ └─────────────┘ │ └─────────────────────────────────────┘   │
└─────────────────┴───────────────────────────────────────────┘
```

### **Key UI Components**

#### **Discovery Panel (Left Sidebar)**
- **Smart Recommendations**: AI-suggested companies with fit scores
- **Filter Controls**: Industry, size, location, funding stage filters
- **Saved Company Lists**: Organized collections (targets, applied, rejected)
- **Recent Activity**: Recently viewed and researched companies
- **Quick Actions**: Add company, bulk import, export list

#### **Research Workspace (Main Area)**
- **Company Profile Tabs**: Organized information display
- **Rich Content Display**: Logos, images, charts, data visualizations
- **Interactive Elements**: Expandable sections, hover details, quick actions
- **Integration Points**: Links to job applications, networking contacts, tasks

#### **Research Tools (Bottom Panel)**
- **Note Editor**: Rich text editor with formatting and tagging
- **Research Templates**: Pre-built research frameworks and checklists
- **Comparison Tool**: Drag-and-drop company comparison interface
- **Progress Tracker**: Research completion status and next steps

---

## 🔧 **Technical Implementation**

### **Frontend Architecture**

#### **React Component Structure**
```typescript
// Main Dashboard Component
CompanyDiscoveryDashboard/
├── DiscoveryPanel/
│   ├── SmartRecommendations.tsx
│   ├── FilterControls.tsx
│   ├── SavedLists.tsx
│   └── RecentActivity.tsx
├── ResearchWorkspace/
│   ├── CompanyProfile/
│   │   ├── OverviewTab.tsx
│   │   ├── FinancialsTab.tsx
│   │   ├── TechnologyTab.tsx
│   │   ├── JobsTab.tsx
│   │   └── NewsTab.tsx
│   └── ResearchTools/
│       ├── NotesEditor.tsx
│       ├── ResearchTemplates.tsx
│       ├── ComparisonTool.tsx
│       └── ProgressTracker.tsx
└── CompanyComparison/
    ├── ComparisonMatrix.tsx
    ├── ScoringCriteria.tsx
    └── DecisionFramework.tsx
```

#### **State Management**
```typescript
interface CompanyDiscoveryState {
  discoveryFilters: DiscoveryFilters
  recommendedCompanies: CompanyData[]
  savedLists: CompanyList[]
  currentCompany: CompanyData | null
  researchNotes: ResearchNote[]
  comparisonSet: CompanyData[]
  loading: boolean
  error: string | null
}
```

### **Backend Integration**

#### **API Endpoints**
```typescript
// Company Discovery
GET /api/companies/discover - Smart company recommendations
POST /api/companies/search - Advanced company search
GET /api/companies/{id} - Company profile data
POST /api/companies/enrich - Enrich company data

// Research Management
GET /api/research/notes - User research notes
POST /api/research/notes - Create/update research notes
GET /api/research/templates - Research templates
POST /api/research/progress - Update research progress

// Comparison Tools
POST /api/companies/compare - Compare multiple companies
GET /api/companies/scoring - Company scoring criteria
POST /api/companies/score - Score company fit
```

#### **Database Schema (Supabase)**
```sql
-- Companies table
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    domain TEXT UNIQUE,
    description TEXT,
    industry TEXT,
    size TEXT,
    location TEXT,
    founded_year INTEGER,
    revenue TEXT,
    funding TEXT,
    technologies TEXT[],
    social_media JSONB,
    logo_url TEXT,
    website TEXT,
    phone TEXT,
    source_api TEXT,
    confidence_score FLOAT,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Research notes table
CREATE TABLE research_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    company_id UUID REFERENCES companies(id),
    title TEXT NOT NULL,
    content TEXT,
    tags TEXT[],
    research_stage TEXT,
    priority INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Company lists table
CREATE TABLE company_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    name TEXT NOT NULL,
    description TEXT,
    company_ids UUID[],
    list_type TEXT DEFAULT 'custom',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Company scoring table
CREATE TABLE company_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    company_id UUID REFERENCES companies(id),
    criteria JSONB,
    overall_score FLOAT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **AI Integration**

#### **Smart Discovery Algorithm**
```python
class CompanyDiscoveryAI:
    def recommend_companies(self, user_profile: UserProfile, 
                          preferences: JobSearchPreferences) -> List[CompanyRecommendation]:
        """
        AI-powered company recommendations based on:
        - User skills and experience
        - Career goals and preferences
        - Industry trends and growth
        - Network connections and referral opportunities
        - Job market data and hiring patterns
        """
        
    def score_company_fit(self, company: CompanyData, 
                         user_profile: UserProfile) -> CompanyFitScore:
        """
        Multi-dimensional company fit scoring:
        - Role alignment (skills, experience, career level)
        - Culture fit (values, work style, company size)
        - Growth opportunity (career advancement, learning)
        - Compensation potential (salary, equity, benefits)
        - Location and remote work compatibility
        """
```

---

## 🎯 **User Workflows**

### **Workflow 1: Discover New Target Companies**
1. **Set Discovery Criteria** - Define industry, size, location preferences
2. **Review AI Recommendations** - Browse smart suggestions with fit scores
3. **Apply Filters** - Refine results by funding stage, technology, growth
4. **Quick Preview** - View company cards with key metrics and scores
5. **Add to Research List** - Save interesting companies for detailed research

### **Workflow 2: Deep Company Research**
1. **Select Company** - Choose company from discovery or manual search
2. **Auto-Enrich Data** - Trigger multi-API data enrichment
3. **Review Profile Tabs** - Explore overview, financials, technology, jobs
4. **Take Research Notes** - Document insights, questions, opportunities
5. **Score Opportunity** - Rate company fit across multiple criteria
6. **Plan Next Steps** - Set research tasks, application timeline, networking

### **Workflow 3: Compare Target Companies**
1. **Select Companies** - Choose 2-5 companies for comparison
2. **Define Criteria** - Set importance weights for different factors
3. **Review Comparison Matrix** - Analyze side-by-side data and scores
4. **Identify Trade-offs** - Understand pros/cons of each option
5. **Make Decision** - Choose top targets based on comprehensive analysis
6. **Export Analysis** - Save comparison report for future reference

### **Workflow 4: Track Research Progress**
1. **View Research Dashboard** - See all companies in research pipeline
2. **Check Progress Status** - Identify incomplete research and next steps
3. **Update Research Notes** - Add new insights and information
4. **Set Research Tasks** - Create follow-up actions and deadlines
5. **Monitor Market Changes** - Track company news and updates
6. **Maintain Company Lists** - Organize targets by priority and status

---

## 📈 **Success Metrics & KPIs**

### **Discovery Effectiveness**
- **Recommendation Accuracy**: % of AI recommendations that user finds relevant
- **Discovery Conversion**: % of discovered companies that become application targets
- **Time to Discovery**: Average time to find suitable target companies
- **Filter Usage**: Most effective discovery filters and criteria

### **Research Efficiency**
- **Research Completion Rate**: % of companies with complete research profiles
- **Time per Company**: Average research time per company
- **Data Enrichment Success**: % of companies successfully enriched with external data
- **Note-Taking Activity**: Research notes created per company

### **Decision Quality**
- **Application Success Rate**: Interview rates for researched vs. non-researched companies
- **Company Fit Accuracy**: Actual vs. predicted company fit scores
- **Research ROI**: Job offers from thoroughly researched companies
- **User Satisfaction**: Feedback on research quality and usefulness

---

## 🚀 **Implementation Phases**

### **Phase 1: Foundation (Week 1)**
- **Database Setup**: Create Supabase tables for companies, notes, lists
- **API Integration**: Connect existing enrichment service to database
- **Basic UI**: Simple company search and profile display
- **Data Migration**: Import existing company data and test enrichment

### **Phase 2: Discovery Engine (Week 2)**
- **Smart Recommendations**: Implement AI-powered company discovery
- **Advanced Filters**: Build comprehensive filtering system
- **Company Lists**: Create saved lists and organization features
- **Search Interface**: Advanced search with multiple criteria

### **Phase 3: Research Workspace (Week 3)**
- **Profile Tabs**: Build comprehensive company profile interface
- **Notes System**: Implement rich text notes with tagging
- **Research Templates**: Create structured research frameworks
- **Progress Tracking**: Build research workflow management

### **Phase 4: Comparison & Analytics (Week 4)**
- **Comparison Tool**: Multi-company comparison matrix
- **Scoring System**: Company fit scoring and ranking
- **Analytics Dashboard**: Research metrics and insights
- **Export Features**: PDF reports and data export

### **Phase 5: Integration & Polish (Week 5)**
- **Cross-Module Integration**: Connect to job applications, networking, tasks
- **Performance Optimization**: Caching, lazy loading, search optimization
- **Mobile Responsiveness**: Ensure mobile-friendly interface
- **User Testing**: Gather feedback and refine user experience

---

## 🔗 **Integration Points**

### **Job Application Dashboard**
- **One-Click Apply**: Direct application initiation from company research
- **Application Tracking**: Link research notes to application records
- **Status Updates**: Track application progress with company context

### **Networking Dashboard**
- **Connection Discovery**: Find network contacts at target companies
- **Referral Opportunities**: Identify warm introduction paths
- **Relationship Mapping**: Visualize network connections to companies

### **Job Search Tasks**
- **Research Tasks**: Auto-generate research tasks for target companies
- **Follow-up Reminders**: Set tasks for company news monitoring
- **Application Deadlines**: Track job posting deadlines and application windows

### **News & Market Intelligence**
- **Company Alerts**: Automated news alerts for target companies
- **Industry Trends**: Market intelligence relevant to target companies
- **Funding Updates**: Track funding rounds and company milestones

This comprehensive Company Discovery & Research module will transform your job search from reactive to proactive, enabling you to identify and thoroughly research the best opportunities before they become widely known. The integration with your existing company enrichment infrastructure provides a strong foundation for rapid development and immediate value.
