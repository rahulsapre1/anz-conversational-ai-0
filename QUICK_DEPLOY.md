# Quick Deployment Guide 🚀

**Fastest way to get your app live: Streamlit Cloud (~5 minutes)**

## Prerequisites Checklist

- [ ] Code is committed and pushed to GitHub
- [ ] You have all environment variables from your `.env` file:
  - [ ] `OPENAI_API_KEY`
  - [ ] `OPENAI_MODEL` (default: `gpt-4o-mini`)
  - [ ] `OPENAI_VECTOR_STORE_ID_CUSTOMER`
  - [ ] `OPENAI_VECTOR_STORE_ID_BANKER`
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_KEY`
  - [ ] `SESSION_PASSWORD` (choose a secure password)
  - [ ] `CONFIDENCE_THRESHOLD` (default: `0.68`)
  - [ ] `LOG_LEVEL` (default: `INFO`)
  - [ ] `API_TIMEOUT` (default: `30`)

## Streamlit Cloud Deployment (Recommended)

### Step 1: Push to GitHub (2 minutes)
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud (2 minutes)
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file: `main.py`
6. Click "Deploy"

### Step 3: Add Secrets (1 minute)
1. Click "Settings" ⚙️ → "Secrets"
2. Paste this format (replace with your actual values):
```toml
OPENAI_API_KEY="sk-..."
OPENAI_MODEL="gpt-4o-mini"
OPENAI_VECTOR_STORE_ID_CUSTOMER="vs_..."
OPENAI_VECTOR_STORE_ID_BANKER="vs_..."
SUPABASE_URL="https://xxx.supabase.co"
SUPABASE_KEY="eyJ..."
CONFIDENCE_THRESHOLD="0.68"
LOG_LEVEL="INFO"
SESSION_PASSWORD="your-secure-password"
API_TIMEOUT="30"
```
3. Click "Save"
4. App auto-redeploys!

### Step 4: Test (1 minute)
- Visit your app URL: `https://your-app-name.streamlit.app`
- Login with your `SESSION_PASSWORD`
- Test a chat message

**Done! 🎉 Your app is live!**

---

## Alternative: Render Deployment

If you prefer Render over Streamlit Cloud:

### Step 1: Push to GitHub (same as above)

### Step 2: Deploy on Render (5 minutes)
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your repository
5. Configure:
   - Name: `contactiq`
   - Environment: `Docker`
   - Plan: `Free`
6. Add all environment variables (same as above)
7. Click "Create Web Service"
8. Wait for build to complete (~5-10 minutes)

**Done! Your app will be at: `https://contactiq.onrender.com`**

---

## Troubleshooting

### "Configuration Error" on app load
- Check all secrets are set correctly
- Verify no extra spaces or quotes
- Ensure Vector Store IDs are correct

### "Database connection error"
- Verify Supabase URL and key
- Check Supabase project is active
- Test connection locally first

### "OpenAI API error"
- Verify API key is valid
- Check API usage limits on OpenAI dashboard
- Ensure Vector Store IDs are correct

### Need help?
See full deployment guide in `DEPLOYMENT.md` for detailed troubleshooting.
