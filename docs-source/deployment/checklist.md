# 🚀 Production Deployment Checklist

## ✅ **Immediate Actions (Today)**

### **1. Domain Setup**
- [ ] **Choose domain name** (suggestions: jobsearchai.com, aicareerboost.com, smartjobhunt.com)
- [ ] **Purchase domain** through Bluehost
- [ ] **Configure DNS** with subdomains:
  ```
  A Record: @ → Bluehost IP (WordPress)
  CNAME: app → [Lovable deployment URL] 
  CNAME: api → [Railway deployment URL]
  ```

### **2. Job Board API Keys (HIGH PRIORITY)**
- [ ] **Greenhouse API**
  - Go to: https://developers.greenhouse.io/
  - Sign up for developer account
  - Create API key with job read permissions
  - Set: `GREENHOUSE_API_KEY=your_key`

- [ ] **Lever API**
  - Go to: https://help.lever.co/hc/en-us/articles/360003802392
  - Apply for API access
  - Create OAuth2 application
  - Set: `LEVER_API_KEY=your_key`

- [ ] **SmartRecruiters API**
  - Go to: https://dev.smartrecruiters.com/
  - Contact for API access
  - Get Job Ads API key
  - Set: `SMARTRECRUITERS_API_KEY=your_key`

- [ ] **Workable API**
  - Go to: https://developer.workable.com/
  - Sign up and create app
  - Get API key and subdomain
  - Set: `WORKABLE_API_KEY=your_key`
  - Set: `WORKABLE_SUBDOMAIN=your_subdomain`

### **3. Cloud Services Setup**
- [ ] **Railway Account**
  - Go to: https://railway.app/
  - Sign up with GitHub
  - Connect your job-search-automation repo
  - Set up environment variables

- [ ] **Lovable Account**
  - Go to: https://lovable.dev/
  - Sign up and create project
  - Set custom domain: app.yourdomain.com

- [ ] **Supabase Production**
  - Go to: https://supabase.com/
  - Create new production project
  - Get connection string and API keys
  - Set up database schema

## 🔧 **Environment Variables Checklist**

Copy this to your Railway environment:

```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Job Board APIs
GREENHOUSE_API_KEY=your_greenhouse_key
LEVER_API_KEY=your_lever_key
SMARTRECRUITERS_API_KEY=your_smartrecruiters_key
WORKABLE_API_KEY=your_workable_key
WORKABLE_SUBDOMAIN=your_workable_subdomain

# Existing APIs
OPENAI_API_KEY=your_openai_key
HUBSPOT_API_KEY=your_hubspot_key
INDEED_API_KEY=your_indeed_key
GITHUB_API_TOKEN=your_github_token

# Company Enrichment (Optional)
CLEARBIT_API_KEY=your_clearbit_key
APOLLO_API_KEY=your_apollo_key
ZOOMINFO_API_KEY=your_zoominfo_key

# Contact Enrichment (Optional)
HUNTER_API_KEY=your_hunter_key
ROCKETREACH_API_KEY=your_rocketreach_key
CONTACTOUT_API_KEY=your_contactout_key

# Environment
NODE_ENV=production
API_BASE_URL=https://api.yourdomain.com
DEMO_MODE=false
```

## 📋 **Today's Priority Tasks**

### **Hour 1: Domain & Accounts**
1. Choose and purchase domain
2. Create Railway account
3. Create Lovable account
4. Set up Supabase production project

### **Hour 2: API Applications**
1. Apply for Greenhouse API access
2. Apply for Lever API access
3. Contact SmartRecruiters for API
4. Sign up for Workable API

### **Hour 3: Deployment Prep**
1. Configure Railway project
2. Set up environment variables
3. Test API integrations locally
4. Prepare for deployment

## 🎯 **Success Criteria for Today**

- [ ] Domain purchased and DNS configured
- [ ] All cloud accounts created
- [ ] API applications submitted
- [ ] Environment variables documented
- [ ] Local testing successful

## 📞 **Next Steps After Setup**

1. **Deploy API to Railway** (once API keys are approved)
2. **Build frontend in Lovable** (components ready)
3. **Configure WordPress integration** (authentication bridge)
4. **Run end-to-end testing** (regression suite)
5. **Launch beta version** (limited users)

---

**Track your progress by checking off items as you complete them!** ✅
