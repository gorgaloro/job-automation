#!/bin/bash
echo "🚀 Starting AI Job Search Automation Platform..."
echo "📊 Environment: Production"
echo "🗄️ Database: Supabase PostgreSQL"
echo "🤖 AI: OpenAI GPT-4"

# Start the FastAPI application
exec python -m uvicorn src.api.production_app:app --host 0.0.0.0 --port $PORT --log-level info
