#!/usr/bin/env python3
"""
Script to help set up Supabase database schema.

This script:
1. Reads the database schema from database/schema.sql
2. Displays it for you to copy into Supabase SQL Editor
3. Provides instructions for manual setup

Usage:
    python setup_supabase.py
"""

import os
from pathlib import Path

def read_schema():
    """Read the database schema SQL file."""
    schema_file = Path(__file__).parent / "database" / "schema.sql"
    
    if not schema_file.exists():
        print("❌ Error: database/schema.sql not found")
        print("   Please create the schema file first (see guides/TASK_02_DATABASE.md)")
        return None
    
    with open(schema_file, "r") as f:
        return f.read()

def check_env_config():
    """Check if Supabase credentials are in .env file."""
    from dotenv import load_dotenv
    
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    
    config_status = {
        "url_set": bool(supabase_url and supabase_url != "https://xxx.supabase.co"),
        "key_set": bool(supabase_key and supabase_key != "eyJ..."),
        "url": supabase_url,
        "key": supabase_key[:20] + "..." if supabase_key and len(supabase_key) > 20 else supabase_key
    }
    
    return config_status

def main():
    """Main function to display setup instructions."""
    print("=" * 70)
    print("Supabase Database Setup")
    print("=" * 70)
    print()
    
    # Check environment configuration
    config = check_env_config()
    
    print("📋 Configuration Check:")
    if config["url_set"] and config["key_set"]:
        print("   ✅ SUPABASE_URL is set")
        print("   ✅ SUPABASE_KEY is set")
        print(f"   URL: {config['url']}")
        print(f"   Key: {config['key']}")
    else:
        print("   ⚠️  Supabase credentials not fully configured")
        if not config["url_set"]:
            print("   ❌ SUPABASE_URL is missing or placeholder")
        if not config["key_set"]:
            print("   ❌ SUPABASE_KEY is missing or placeholder")
        print()
        print("   Please update your .env file with:")
        print("   SUPABASE_URL=https://xxxxx.supabase.co")
        print("   SUPABASE_KEY=eyJ...  # Use anon/public key")
    print()
    
    # Read schema
    schema_sql = read_schema()
    
    if not schema_sql:
        return 1
    
    print("=" * 70)
    print("Database Schema SQL")
    print("=" * 70)
    print()
    print("Follow these steps to set up your database:")
    print()
    print("1. Go to your Supabase project dashboard")
    print("2. Click 'SQL Editor' in the left sidebar")
    print("3. Click 'New query'")
    print("4. Copy and paste the SQL below into the editor")
    print("5. Click 'Run' (or press Cmd/Ctrl + Enter)")
    print("6. Wait for success message")
    print("7. Verify tables in 'Table Editor'")
    print()
    print("-" * 70)
    print("SQL SCHEMA (copy everything below this line):")
    print("-" * 70)
    print()
    print(schema_sql)
    print()
    print("-" * 70)
    print("END OF SQL SCHEMA")
    print("-" * 70)
    print()
    
    print("=" * 70)
    print("After Running the SQL")
    print("=" * 70)
    print()
    print("Verify the following tables were created:")
    print("  ✅ interactions")
    print("  ✅ escalations")
    print("  ✅ knowledge_documents")
    print()
    print("You can verify by:")
    print("  1. Going to 'Table Editor' in Supabase")
    print("  2. Checking that all three tables are listed")
    print()
    print("To test your connection, run:")
    print("  python3 test_supabase_connection.py")
    print()
    
    return 0

if __name__ == "__main__":
    exit(main())
