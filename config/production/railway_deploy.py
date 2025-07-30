"""
Production Railway Deployment Script
Deploys complete AI Job Search Automation Platform with Supabase backend
"""

import os
import subprocess
import sys
from pathlib import Path

def deploy_production_system():
    """Deploy complete production system to Railway"""
    
    print("🚀 Deploying AI Job Search Automation Platform to Railway...")
    
    # Create Railway deployment files
    create_railway_config()
    create_requirements_file()
    create_startup_script()
    
    print("✅ Deployment files created")
    print("📋 Next steps:")
    print("1. Set environment variables in Railway dashboard:")
    print("   - SUPABASE_URL")
    print("   - SUPABASE_ANON_KEY") 
    print("   - SUPABASE_SERVICE_KEY")
    print("   - OPENAI_API_KEY")
    print("   - DATABASE_URL")
    print("2. Deploy to Railway: railway up")
    print("3. Run database migrations in Supabase")

def create_railway_config():
    """Create railway.json configuration"""
    config = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "NIXPACKS",
            "buildCommand": "pip install -r requirements.txt"
        },
        "deploy": {
            "startCommand": "python -m uvicorn src.api.production_app:app --host 0.0.0.0 --port $PORT",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 300,
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 3
        }
    }
    
    with open("railway.json", "w") as f:
        import json
        json.dump(config, f, indent=2)

def create_requirements_file():
    """Create production requirements.txt"""
    requirements = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "supabase==2.0.2",
        "asyncpg==0.29.0",
        "openai==1.3.5",
        "pydantic==2.5.0",
        "python-jose[cryptography]==3.3.0",
        "python-multipart==0.0.6",
        "httpx==0.25.2",
        "python-dotenv==1.0.0",
        "psycopg2-binary==2.9.9",
        "sqlalchemy==2.0.23",
        "alembic==1.13.1"
    ]
    
    with open("requirements.txt", "w") as f:
        f.write("\n".join(requirements))

def create_startup_script():
    """Create startup script for Railway"""
    script = """#!/bin/bash
echo "🚀 Starting AI Job Search Automation Platform..."
echo "📊 Environment: Production"
echo "🗄️ Database: Supabase PostgreSQL"
echo "🤖 AI: OpenAI GPT-4"

# Start the FastAPI application
exec python -m uvicorn src.api.production_app:app --host 0.0.0.0 --port $PORT --log-level info
"""
    
    with open("start.sh", "w") as f:
        f.write(script)
    
    # Make executable
    os.chmod("start.sh", 0o755)

if __name__ == "__main__":
    deploy_production_system()
