# Supabase Setup Instructions

This guide will help you set up your Supabase project and configure it for ContactIQ.

## Step 1: Create Supabase Account and Project

1. **Go to Supabase**: https://supabase.com
2. **Sign up** (or sign in if you already have an account)
3. **Create a new project**:
   - Click "New Project"
   - Fill in:
     - **Name**: ContactIQ (or any name you prefer)
     - **Database Password**: Choose a strong password (save it securely)
     - **Region**: Choose closest to you
     - **Pricing Plan**: Free tier is sufficient for MVP
   - Click "Create new project"
   - Wait 2-3 minutes for project to initialize

## Step 2: Get Your Supabase Credentials

Once your project is created:

1. **Go to Project Settings**:
   - Click the gear icon (⚙️) in the left sidebar
   - Or go to: Settings → API

2. **Find your credentials**:
   - **Project URL**: Found under "Project URL" (e.g., `https://xxxxx.supabase.co`)
   - **API Keys**: 
     - **anon/public key**: Use this for client operations (safe to use in frontend)
     - **service_role key**: Keep this secret (only for admin operations)

3. **Copy these values** - you'll need them for your `.env` file

## Step 3: Update Your .env File

Add your Supabase credentials to your `.env` file:

```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJ...  # Use the anon/public key here
```

**Important**: Use the **anon/public key** (not the service_role key) for `SUPABASE_KEY`.

## Step 4: Create Database Schema

You have two options:

### Option A: Use the Setup Script (Recommended)

Run the setup script which will:
1. Display the SQL schema
2. Guide you through running it in Supabase SQL Editor

```bash
python3 setup_supabase.py
```

### Option B: Manual Setup

1. **Open Supabase SQL Editor**:
   - In your Supabase project dashboard
   - Click "SQL Editor" in the left sidebar
   - Click "New query"

2. **Copy and paste the schema**:
   - Open `database/schema.sql` in your project
   - Copy all the SQL content
   - Paste into the SQL Editor

3. **Run the SQL**:
   - Click "Run" (or press Cmd/Ctrl + Enter)
   - Wait for success message

4. **Verify tables were created**:
   - Go to "Table Editor" in the left sidebar
   - You should see three tables:
     - `interactions`
     - `escalations`
     - `knowledge_documents`

## Step 5: Verify Setup

Test your Supabase connection:

```bash
python3 test_supabase_connection.py
```

Or test manually in Python:

```python
from database.supabase_client import get_db_client

client = get_db_client()
if client.test_connection():
    print("✅ Supabase connection successful!")
else:
    print("❌ Connection failed. Check your credentials.")
```

## Step 6: Test Database Operations

Test inserting data:

```python
from database.supabase_client import get_db_client

client = get_db_client()

# Test insert
test_data = {
    "assistant_mode": "customer",
    "user_query": "test query",
    "outcome": "resolved",
    "step_1_intent_completed": True
}

interaction_id = client.insert_interaction(test_data)
if interaction_id:
    print(f"✅ Test interaction inserted: {interaction_id}")
else:
    print("❌ Failed to insert test data")
```

## Troubleshooting

### Connection Issues

- **Error: "Invalid API key"**
  - Verify you're using the **anon/public key** (not service_role)
  - Check that the key is copied correctly (no extra spaces)

- **Error: "Connection refused"**
  - Verify `SUPABASE_URL` is correct
  - Check that your project is active (not paused)

- **Error: "Table not found"**
  - Make sure you ran the schema SQL in SQL Editor
  - Verify tables exist in Table Editor

### Permission Issues

- If you get permission errors, ensure you're using the **anon/public key**
- The service_role key has admin access but should not be used in client code

## Next Steps

Once Supabase is set up:

1. ✅ Your `.env` file has `SUPABASE_URL` and `SUPABASE_KEY`
2. ✅ Database tables are created
3. ✅ Connection test passes

You can now proceed to:
- **Task 3**: OpenAI Setup
- **Task 6**: Vector Store Setup (will use Supabase for knowledge_documents)
- **Task 14**: Logging Service (will use Supabase for interactions)

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase/supabase-py)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
