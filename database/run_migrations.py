"""
Run database migrations.
Can be executed manually or via Supabase SQL editor.

This script reads the schema.sql file and displays it for manual execution
in the Supabase SQL Editor. For MVP, manual execution is recommended.
"""
import sys
from pathlib import Path

def main():
    """Display migration SQL for manual execution."""
    # Read schema.sql
    schema_file = Path(__file__).parent / "schema.sql"
    
    if not schema_file.exists():
        print("❌ Error: database/schema.sql not found")
        return 1
    
    with open(schema_file, "r") as f:
        schema_sql = f.read()
    
    print("=" * 60)
    print("Database Migration Script")
    print("=" * 60)
    print("\nCopy and paste the following SQL into Supabase SQL Editor:\n")
    print(schema_sql)
    print("\n" + "=" * 60)
    print("After running the SQL, verify tables were created.")
    print("=" * 60)
    print("\nTo verify, run this query in Supabase SQL Editor:")
    print("""
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
    """)
    
    return 0

if __name__ == "__main__":
    exit(main())
