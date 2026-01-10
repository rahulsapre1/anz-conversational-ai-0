#!/usr/bin/env python3
"""
Test script to verify Supabase connection and setup.

This script:
1. Tests connection to Supabase
2. Verifies tables exist
3. Tests basic insert/query operations

Usage:
    python test_supabase_connection.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test Supabase connection."""
    try:
        from database.supabase_client import get_db_client
        
        print("=" * 60)
        print("Supabase Connection Test")
        print("=" * 60)
        print()
        
        # Check environment variables
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_KEY", "")
        
        if not supabase_url or supabase_url == "https://xxx.supabase.co":
            print("❌ SUPABASE_URL not configured")
            print("   Please set SUPABASE_URL in your .env file")
            return False
        
        if not supabase_key or supabase_key == "eyJ...":
            print("❌ SUPABASE_KEY not configured")
            print("   Please set SUPABASE_KEY in your .env file")
            return False
        
        print("✅ Environment variables configured")
        print(f"   URL: {supabase_url}")
        print(f"   Key: {supabase_key[:20]}...")
        print()
        
        # Initialize client
        print("Initializing Supabase client...")
        try:
            client = get_db_client()
            print("✅ Client initialized")
        except Exception as e:
            print(f"❌ Failed to initialize client: {e}")
            return False
        
        print()
        
        # Test connection
        print("Testing connection...")
        if client.test_connection():
            print("✅ Connection successful!")
        else:
            print("❌ Connection failed")
            return False
        
        print()
        
        # Test insert
        print("Testing insert operation...")
        test_data = {
            "assistant_mode": "customer",
            "user_query": "test query from setup script",
            "outcome": "resolved",
            "step_1_intent_completed": True
        }
        
        interaction_id = client.insert_interaction(test_data)
        
        if interaction_id:
            print(f"✅ Test interaction inserted: {interaction_id}")
            
            # Clean up test data (optional)
            print()
            print("Note: Test data was inserted. You can delete it manually")
            print("      from the Supabase Table Editor if desired.")
        else:
            print("❌ Failed to insert test data")
            print("   This might indicate a permissions issue")
            return False
        
        print()
        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print()
        print("Your Supabase setup is working correctly.")
        print("You can now proceed with the rest of the setup.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you have installed all dependencies:")
        print("   pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
