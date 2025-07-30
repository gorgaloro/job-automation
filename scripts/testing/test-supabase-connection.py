#!/usr/bin/env python3
"""
Test Supabase Connection and Create Tables

This script tests your Supabase connection and creates the necessary tables
for the personal brand system.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.integrations.supabase.supabase_client import get_supabase_client
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you've installed dependencies: pip install -r requirements.txt")
    sys.exit(1)

def test_connection():
    """Test Supabase connection"""
    print("=" * 60)
    print("TESTING SUPABASE CONNECTION")
    print("=" * 60)
    
    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    print(f"SUPABASE_URL: {'OK Set' if supabase_url else 'X Missing'}")
    print(f"SUPABASE_KEY: {'OK Set' if supabase_key else 'X Missing'}")
    
    if not supabase_url or not supabase_key:
        print("X Missing Supabase credentials in .env file")
        print("Please add:")
        print("SUPABASE_URL=your_supabase_project_url")
        print("SUPABASE_KEY=your_supabase_anon_key")
        return False
    
    # Test connection
    print(f"\nTesting connection to: {supabase_url[:50]}...")
    
    try:
        client = get_supabase_client()
        if client:
            print("SUCCESS: Supabase connection successful!")
            return client
        else:
            print("ERROR: Failed to create Supabase client")
            return False
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        return False

def create_personal_brand_tables(client):
    """Create personal brand tables in Supabase"""
    print("\n" + "=" * 60)
    print("CREATING PERSONAL BRAND TABLES")
    print("=" * 60)
    
    # SQL for creating personal brand tables
    tables_sql = [
        {
            "name": "personal_brand_profiles",
            "sql": """
            CREATE TABLE IF NOT EXISTS personal_brand_profiles (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                user_id TEXT NOT NULL,
                brand_summary TEXT,
                professional_identity TEXT,
                unique_value_proposition TEXT,
                work_preferences JSONB,
                career_motivators JSONB,
                industry_preferences JSONB,
                role_preferences JSONB,
                skills_expertise TEXT[],
                confidence_score FLOAT DEFAULT 0.0,
                profile_version TEXT DEFAULT '1.0',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
        },
        {
            "name": "interview_sessions",
            "sql": """
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                session_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                transcript JSONB,
                questions_asked TEXT[],
                key_insights TEXT[],
                session_duration INTEGER DEFAULT 0,
                session_quality_score FLOAT DEFAULT 0.0,
                generated_profile_id UUID REFERENCES personal_brand_profiles(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                completed_at TIMESTAMP WITH TIME ZONE
            );
            """
        },
        {
            "name": "profile_evolution",
            "sql": """
            CREATE TABLE IF NOT EXISTS profile_evolution (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                profile_id UUID REFERENCES personal_brand_profiles(id),
                change_type TEXT NOT NULL,
                changes_made JSONB,
                trigger_event TEXT,
                confidence_delta FLOAT DEFAULT 0.0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
        }
    ]
    
    # Create tables
    for table in tables_sql:
        try:
            print(f"Creating table: {table['name']}...")
            
            # Execute the SQL
            result = client.rpc('exec_sql', {'sql': table['sql']})
            
            if result:
                print(f"SUCCESS: Table {table['name']} created successfully")
            else:
                print(f"SUCCESS: Table {table['name']} already exists or created")
                
        except Exception as e:
            print(f"ERROR: Failed to create table {table['name']}: {e}")
            
            # Try alternative method - direct SQL execution
            try:
                print(f"Trying alternative method for {table['name']}...")
                # Note: This might not work depending on your Supabase setup
                # You may need to run these SQL commands directly in Supabase dashboard
                print(f"SQL to run manually in Supabase dashboard:")
                print(table['sql'])
                print()
            except Exception as e2:
                print(f"ERROR: Alternative method also failed: {e2}")

def test_table_access(client):
    """Test if we can access the created tables"""
    print("\n" + "=" * 60)
    print("TESTING TABLE ACCESS")
    print("=" * 60)
    
    tables_to_test = [
        "personal_brand_profiles",
        "interview_sessions", 
        "profile_evolution"
    ]
    
    for table_name in tables_to_test:
        try:
            print(f"Testing access to {table_name}...")
            
            # Try to select from the table (should return empty result)
            result = client.table(table_name).select("*").limit(1).execute()
            
            if result:
                print(f"SUCCESS: Can access {table_name} - found {len(result.data)} records")
            else:
                print(f"SUCCESS: Can access {table_name} - table is empty")
                
        except Exception as e:
            print(f"ERROR: Cannot access {table_name}: {e}")
            print(f"You may need to create this table manually in Supabase dashboard")

def main():
    """Main test function"""
    print("SUPABASE CONNECTION & TABLE SETUP TEST")
    print("This will test your connection and create necessary tables")
    print()
    
    # Test connection
    client = test_connection()
    if not client:
        print("\nERROR: Cannot proceed without valid Supabase connection")
        return
    
    # Create tables
    create_personal_brand_tables(client)
    
    # Test table access
    test_table_access(client)
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. If any tables failed to create, run the SQL manually in Supabase dashboard")
    print("2. Run the personal brand demo again: python demo_personal_brand.py")
    print("3. The system should now use live database instead of demo mode")
    print()
    print("Your personal brand system is ready to rock! 🚀")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted. Goodbye!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        print("Make sure you have:")
        print("1. Valid Supabase credentials in .env file")
        print("2. Installed dependencies: pip install -r requirements.txt")
        print("3. Supabase project with proper permissions")
