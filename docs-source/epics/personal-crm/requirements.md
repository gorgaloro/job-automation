# Epic: Personal CRM - Lightweight Customer Relationship Management

## Overview
The Personal CRM epic creates a lightweight, user-friendly CRM system designed for individual job seekers and professionals. This module enables the platform to serve monthly subscribers who need basic CRM functionality without requiring enterprise-level integrations like HubSpot or Salesforce.

## Strategic Vision

### **Product Positioning**
- **Target Market**: Individual professionals, job seekers, freelancers, consultants
- **Value Proposition**: Affordable, easy-to-use CRM focused on career networking and job search
- **Differentiation**: AI-powered insights, resume optimization integration, job search workflow automation

### **Business Model Integration**
- **Monthly Subscription Model**: Lightweight CRM for individual users ($9-29/month)
- **Enterprise Upgrade Path**: API integrations to HubSpot, Salesforce for power users
- **Freemium Option**: Basic contact management with premium AI features

## Core Features

### 1. Contact Management
```sql
-- Core contact database
CREATE TABLE crm_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    company TEXT,
    job_title TEXT,
    linkedin_url TEXT,
    twitter_url TEXT,
    location TEXT,
    contact_source TEXT, -- 'networking_event', 'linkedin', 'referral', 'cold_outreach'
    relationship_type TEXT, -- 'recruiter', 'hiring_manager', 'peer', 'mentor', 'referral'
    connection_strength TEXT, -- 'strong', 'medium', 'weak', 'new'
    last_contact_date DATE,
    next_follow_up_date DATE,
    notes TEXT,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. Interaction Tracking
```sql
-- Track all interactions with contacts
CREATE TABLE crm_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES crm_contacts(id) ON DELETE CASCADE,
    interaction_type TEXT NOT NULL, -- 'email', 'call', 'meeting', 'linkedin_message', 'coffee_chat'
    interaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    subject TEXT,
    notes TEXT,
    outcome TEXT, -- 'positive', 'neutral', 'negative', 'no_response'
    follow_up_required BOOLEAN DEFAULT false,
    follow_up_date DATE,
    attachments TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3. Opportunity Pipeline
```sql
-- Job opportunities and their progression
CREATE TABLE crm_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_title TEXT NOT NULL,
    company_name TEXT NOT NULL,
    contact_id UUID REFERENCES crm_contacts(id),
    job_description TEXT,
    salary_range TEXT,
    location TEXT,
    application_date DATE,
    status TEXT DEFAULT 'interested', -- 'interested', 'applied', 'phone_screen', 'interview', 'final_round', 'offer', 'rejected', 'withdrawn'
    priority_level TEXT DEFAULT 'medium', -- 'high', 'medium', 'low'
    match_score DECIMAL(3,2),
    next_action TEXT,
    next_action_date DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. Activity Dashboard
```sql
-- Daily/weekly activity tracking
CREATE TABLE crm_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL, -- 'contact_added', 'interaction_logged', 'follow_up_completed', 'opportunity_updated'
    activity_date DATE NOT NULL,
    description TEXT,
    related_contact_id UUID REFERENCES crm_contacts(id),
    related_opportunity_id UUID REFERENCES crm_opportunities(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## User Interface Components

### 1. Dashboard Overview
- **Quick Stats**: Total contacts, active opportunities, pending follow-ups
- **Today's Tasks**: Scheduled follow-ups, upcoming interviews, action items
- **Recent Activity**: Latest interactions and updates
- **Pipeline View**: Visual opportunity progression

### 2. Contact Management Interface
- **Contact List**: Searchable, filterable contact database
- **Contact Profile**: Detailed view with interaction history
- **Quick Actions**: Email, call, LinkedIn connect, schedule follow-up
- **Bulk Operations**: Mass updates, tagging, export

### 3. Opportunity Tracking
- **Pipeline Board**: Kanban-style opportunity progression
- **Opportunity Details**: Job info, contact relationships, timeline
- **Application Tracking**: Status updates, interview scheduling
- **Success Analytics**: Conversion rates, time-to-hire metrics

### 4. Communication Hub
- **Email Integration**: Log emails automatically (Gmail/Outlook plugins)
- **Calendar Sync**: Meeting scheduling and follow-up reminders
- **Template Library**: Email templates for common scenarios
- **Automated Reminders**: Follow-up notifications and task alerts

## AI-Powered Features

### 1. Smart Contact Insights
```sql
-- AI-generated contact insights
CREATE TABLE crm_contact_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES crm_contacts(id) ON DELETE CASCADE,
    insight_type TEXT, -- 'communication_style', 'best_contact_time', 'interests', 'mutual_connections'
    insight_text TEXT,
    confidence_score DECIMAL(3,2),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. Opportunity Scoring
- **Match Algorithm**: AI scoring based on resume alignment
- **Success Prediction**: Likelihood of getting interview/offer
- **Timing Optimization**: Best times to apply or follow up
- **Personalization Suggestions**: Tailored outreach recommendations

### 3. Automated Workflows
- **Follow-up Sequences**: Automated reminder scheduling
- **Status Updates**: Smart opportunity progression tracking
- **Relationship Mapping**: Connection strength analysis
- **Performance Analytics**: Success rate optimization

## Integration Architecture

### 1. Internal Platform Integration
```javascript
// Integration with Resume Optimizer
const optimizeResumeForOpportunity = async (opportunityId, resumeId) => {
  const opportunity = await getOpportunity(opportunityId);
  const optimizedResume = await optimizeResume(resumeId, opportunity.job_description);
  return optimizedResume;
};

// Integration with Job Search
const syncJobApplications = async (userId) => {
  const applications = await getJobApplications(userId);
  const opportunities = await createOpportunitiesFromApplications(applications);
  return opportunities;
};
```

### 2. External CRM Integration (Enterprise Tier)
```javascript
// HubSpot Integration
const syncToHubSpot = async (userId, contactData) => {
  const hubspotClient = new HubSpotClient(user.hubspot_api_key);
  const hubspotContact = await hubspotClient.contacts.create(contactData);
  return hubspotContact;
};

// Salesforce Integration
const syncToSalesforce = async (userId, opportunityData) => {
  const sfClient = new SalesforceClient(user.salesforce_credentials);
  const sfOpportunity = await sfClient.opportunities.create(opportunityData);
  return sfOpportunity;
};
```

### 3. Third-Party Integrations
- **LinkedIn API**: Contact import, profile enrichment
- **Gmail/Outlook**: Email tracking and logging
- **Calendar APIs**: Meeting scheduling and reminders
- **Zoom/Teams**: Interview link generation and tracking

## Subscription Tiers

### **Personal Tier ($19/month)**
- Up to 500 contacts
- Basic opportunity tracking
- Email templates and reminders
- Mobile app access
- Basic analytics

### **Professional Tier ($39/month)**
- Unlimited contacts
- Advanced AI insights
- Email/calendar integration
- Custom workflows
- Advanced analytics
- Priority support

### **Enterprise Tier ($99/month)**
- Everything in Professional
- HubSpot/Salesforce integration
- Team collaboration features
- Custom integrations
- Dedicated support
- White-label options

## Technical Implementation

### 1. Backend Architecture
- **Database**: Supabase PostgreSQL with RLS
- **API**: RESTful endpoints with real-time subscriptions
- **Authentication**: Supabase Auth with role-based access
- **File Storage**: Supabase Storage for attachments

### 2. Frontend Components
- **React/Vue Components**: Reusable CRM interface elements
- **Mobile App**: React Native for iOS/Android
- **Browser Extensions**: Chrome/Firefox for email logging
- **Desktop App**: Electron wrapper for offline access

### 3. AI/ML Services
- **OpenAI Integration**: Contact insights and recommendations
- **Natural Language Processing**: Email sentiment analysis
- **Predictive Analytics**: Success probability modeling
- **Automation Engine**: Workflow trigger processing

## Success Metrics

### **User Engagement**
- Daily/weekly active users
- Contact addition rate
- Interaction logging frequency
- Opportunity conversion rates

### **Business Metrics**
- Monthly recurring revenue (MRR)
- Customer acquisition cost (CAC)
- Customer lifetime value (CLV)
- Churn rate and retention

### **Product Metrics**
- Feature adoption rates
- User satisfaction scores
- Support ticket volume
- Integration usage rates

## Development Roadmap

### **Phase 1: Core CRM (3 months)**
- Contact management system
- Basic interaction tracking
- Simple opportunity pipeline
- Mobile-responsive web app

### **Phase 2: AI Enhancement (2 months)**
- Smart contact insights
- Opportunity scoring
- Automated reminders
- Email integration

### **Phase 3: Advanced Features (3 months)**
- Calendar integration
- Advanced analytics
- Mobile app development
- Template library

### **Phase 4: Enterprise Integration (2 months)**
- HubSpot/Salesforce connectors
- Team collaboration features
- Advanced workflow automation
- White-label customization

## Risk Mitigation

### **Technical Risks**
- **Data Security**: Implement comprehensive encryption and RLS
- **Scalability**: Design for horizontal scaling from day one
- **Integration Complexity**: Start with simple APIs, expand gradually

### **Business Risks**
- **Market Competition**: Focus on AI differentiation and job search integration
- **User Adoption**: Provide excellent onboarding and support
- **Pricing Strategy**: Offer competitive freemium tier to drive adoption

### **Regulatory Risks**
- **Data Privacy**: GDPR/CCPA compliance built-in
- **Email Regulations**: CAN-SPAM compliance for automated emails
- **International Markets**: Localization and compliance planning

## Future Enhancements

### **Advanced AI Features**
- Predictive networking recommendations
- Automated relationship scoring
- Intelligent email composition
- Career path optimization

### **Marketplace Integration**
- Third-party app ecosystem
- Custom integration marketplace
- API monetization platform
- Partner program development

### **Enterprise Features**
- Multi-tenant architecture
- Advanced reporting and analytics
- Custom branding and white-labeling
- Enterprise security compliance

This Personal CRM epic provides a comprehensive foundation for building a productizable CRM solution that serves individual users while maintaining clear upgrade paths to enterprise functionality. The modular design allows for incremental development and revenue growth through subscription tiers.
