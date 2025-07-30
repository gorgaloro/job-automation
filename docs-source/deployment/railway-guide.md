# 🚂 Railway Deployment Guide

## 🚀 **Quick Deploy to Railway**

Your AI Job Search Platform API is ready for Railway deployment! Follow these steps:

### **Step 1: Railway Account Setup (2 minutes)**

1. **Go to Railway**: https://railway.app/
2. **Sign up with GitHub** (recommended for easy repo connection)
3. **Verify your account** via email

### **Step 2: Deploy Your Project (5 minutes)**

1. **Create New Project**:
   - Click "New Project" 
   - Select "Deploy from GitHub repo"
   - Choose your `job-search-automation` repository

2. **Railway Auto-Detection**:
   - Railway will automatically detect your Python project
   - It will use the `railway.json` configuration file
   - It will install dependencies from `requirements.txt`

3. **Environment Variables Setup**:
   ```bash
   # Required for basic functionality
   NODE_ENV=production
   DEMO_MODE=false
   
   # OpenAI (you already have this)
   OPENAI_API_KEY=your_openai_key
   
   # Job Board APIs (get these from API providers)
   GREENHOUSE_API_KEY=your_greenhouse_key
   LEVER_API_KEY=your_lever_key
   SMARTRECRUITERS_API_KEY=your_smartrecruiters_key
   WORKABLE_API_KEY=your_workable_key
   WORKABLE_SUBDOMAIN=your_workable_subdomain
   
   # Company Enrichment (optional)
   CLEARBIT_API_KEY=your_clearbit_key
   APOLLO_API_KEY=your_apollo_key
   ZOOMINFO_API_KEY=your_zoominfo_key
   
   # Contact Enrichment (optional)
   HUNTER_API_KEY=your_hunter_key
   ROCKETREACH_API_KEY=your_rocketreach_key
   CONTACTOUT_API_KEY=your_contactout_key
   
   # Database (when ready)
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

### **Step 3: Custom Domain Setup (3 minutes)**

1. **In Railway Dashboard**:
   - Go to your deployed project
   - Click "Settings" → "Domains"
   - Click "Custom Domain"
   - Enter: `api.yourdomain.com`

2. **In Bluehost DNS**:
   - Add CNAME record: `api` → `your-railway-app.railway.app`

### **Step 4: Test Deployment (2 minutes)**

1. **Health Check**: `https://api.yourdomain.com/health`
2. **API Docs**: `https://api.yourdomain.com/docs`
3. **Status Check**: `https://api.yourdomain.com/api/v1/status`

## 🎯 **Expected Results**

### **Immediate (Demo Mode)**
```json
{
  "status": "healthy",
  "service": "AI Job Search Platform API",
  "version": "1.0.0",
  "environment": "production"
}
```

### **With API Keys Configured**
- Job board integration will fetch real jobs
- Company enrichment will return detailed company data
- Contact enrichment will find email addresses

## 💰 **Railway Pricing**

- **Hobby Plan**: $5/month (perfect for testing)
- **Pro Plan**: $20/month (production ready)
- **Usage-based pricing** for compute and bandwidth

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Build Fails**:
   - Check `requirements.txt` has all dependencies
   - Verify Python version compatibility

2. **Health Check Fails**:
   - Ensure `/health` endpoint is accessible
   - Check Railway logs for errors

3. **API Keys Not Working**:
   - Verify environment variables are set correctly
   - Check API key permissions and quotas

### **Railway CLI (Optional)**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link [your-project-id]
railway up
```

## 📊 **Monitoring**

### **Railway Built-in Monitoring**
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: Deployment history and rollbacks

### **Custom Monitoring**
- **Health Checks**: Automated via Railway
- **API Usage**: Track via endpoint metrics
- **Error Tracking**: Built into FastAPI logging

## 🚀 **Next Steps After Deployment**

1. **Test all endpoints** with Postman or curl
2. **Apply for job board API keys** (Greenhouse, Lever, etc.)
3. **Set up Supabase production database**
4. **Build Lovable frontend** to connect to your API
5. **Configure WordPress authentication bridge**

---

**Your API is production-ready and will scale automatically on Railway!** 🌟

## 📞 **Support**

- **Railway Docs**: https://docs.railway.app/
- **Railway Discord**: https://discord.gg/railway
- **API Documentation**: `https://api.yourdomain.com/docs`
