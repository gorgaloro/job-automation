"""
Supabase Client Configuration

Centralized Supabase client setup and configuration.
"""

import os
import logging
from typing import Optional
from supabase import create_client, Client

logger = logging.getLogger(__name__)

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Optional[Client]:
    """Get or create Supabase client instance"""
    global _supabase_client
    
    if _supabase_client is not None:
        return _supabase_client
    
    # Get Supabase credentials from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.warning("Supabase credentials not found in environment variables")
        logger.info("Running in demo mode without database connection")
        return None
    
    try:
        _supabase_client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
        return _supabase_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None

def reset_supabase_client():
    """Reset the Supabase client (useful for testing)"""
    global _supabase_client
    _supabase_client = None
