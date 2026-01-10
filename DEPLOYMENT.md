# ContactIQ - Deployment Guide

## Local Development

### Prerequisites
- Python 3.12 or 3.13
- Virtual environment
- All API keys configured

### Steps

1. **Set up environment**:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   - Create `.env` file in root directory
   - Fill in all required values (see README.md for details)

3. **Set up database**:
   - Create Supabase project at https://supabase.com
   - Run `database/schema.sql` in Supabase SQL Editor
   - Or run migrations: `python database/run_migrations.py`

4. **Ingest knowledge base**:
   ```bash
   python knowledge/ingestor.py
   python knowledge/vector_store_setup.py
   ```
   - Note the Vector Store IDs and add them to `.env`

5. **Run application**:
   ```bash
   streamlit run main.py
   ```

6. **Access application**:
   - Open browser to `http://localhost:8501`
   - Enter password from `.env`
   - Start using the application!

## Production Deployment

### ⭐ Option 1: Streamlit Cloud (EASIEST - Recommended)

**Best for:** Quick deployment, free tier, built specifically for Streamlit
**Pricing:** Free tier available
**Time to deploy:** ~5 minutes

#### Prerequisites
- GitHub account
- Code pushed to a GitHub repository
- All environment variables ready from your `.env` file

#### Step-by-Step Instructions

1. **Prepare your repository**:
   ```bash
   # Ensure everything is committed to GitHub
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**:
   - Go to https://share.streamlit.io
   - Click "Sign in" and authorize with your GitHub account
   - Click "New app" button
   - Fill in the form:
     - **Repository**: Select your repository (e.g., `your-username/anz-conversational-ai-0`)
     - **Branch**: `main` (or your default branch)
     - **Main file path**: `main.py`
     - **App URL**: Choose a unique URL (e.g., `contactiq` → `contactiq.streamlit.app`)
   - Click "Deploy"

3. **Set environment variables (Secrets)**:
   - Once deployed, click "Settings" (⚙️ icon) in the app dashboard
   - Go to "Secrets" tab
   - Paste your environment variables in this format:
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
   - **Important**: Use double quotes around values, no spaces around `=`
   - Click "Save"

4. **Redeploy**:
   - The app will automatically redeploy after saving secrets
   - Or click "Manage app" → "Reboot app" to manually trigger
   - Wait 1-2 minutes for deployment to complete

5. **Access your app**:
   - Your app will be live at: `https://your-app-name.streamlit.app`
   - Test authentication with your `SESSION_PASSWORD`

#### Streamlit Cloud Advantages
- ✅ Free tier (unlimited public apps)
- ✅ Automatic deployments on git push
- ✅ Built-in HTTPS/SSL
- ✅ No configuration needed
- ✅ Easy secret management
- ✅ Automatic scaling

---

### Option 2: Render (Good Alternative)

**Best for:** Docker deployments, more control, private apps
**Pricing:** Free tier available (spins down after 15 min of inactivity)
**Time to deploy:** ~10 minutes

#### Prerequisites
- GitHub account
- Code pushed to a GitHub repository
- Dockerfile (already created ✓)

#### Step-by-Step Instructions

1. **Sign up for Render**:
   - Go to https://render.com
   - Click "Get Started for Free"
   - Sign up with GitHub (recommended for easy repo access)

2. **Create a new Web Service**:
   - In Render dashboard, click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure the service**:
   - **Name**: `contactiq` (or your preferred name)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `.` if needed)
   - **Environment**: `Docker`
   - **Dockerfile Path**: `Dockerfile` (should auto-detect)
   - **Docker Context**: `.` (current directory)
   - **Plan**: `Free` (or choose a paid plan for always-on)

4. **Set environment variables**:
   Scroll down to "Environment Variables" section and add each variable:
   - `OPENAI_API_KEY` = `sk-...`
   - `OPENAI_MODEL` = `gpt-4o-mini`
   - `OPENAI_VECTOR_STORE_ID_CUSTOMER` = `vs_...`
   - `OPENAI_VECTOR_STORE_ID_BANKER` = `vs_...`
   - `SUPABASE_URL` = `https://xxx.supabase.co`
   - `SUPABASE_KEY` = `eyJ...`
   - `CONFIDENCE_THRESHOLD` = `0.68`
   - `LOG_LEVEL` = `INFO`
   - `SESSION_PASSWORD` = `your-secure-password`
   - `API_TIMEOUT` = `30`

5. **Deploy**:
   - Click "Create Web Service"
   - Render will build your Docker image (first build takes 5-10 minutes)
   - Watch the logs to ensure successful build
   - Once deployed, you'll get a URL like: `https://contactiq.onrender.com`

6. **Configure auto-deploy** (optional):
   - In service settings, enable "Auto-Deploy" for automatic deployments on git push

#### Render Advantages
- ✅ Free tier available
- ✅ Docker support (more control)
- ✅ Private apps on free tier
- ✅ Good for containerized deployments
- ⚠️ Free tier spins down after 15 min inactivity (cold starts)
- ⚠️ First response can be slow after spin-down

#### Using render.yaml (Alternative Method)
If you want to use Infrastructure as Code:
- Your `render.yaml` file is already configured
- Go to Render dashboard → "New" → "Blueprint"
- Connect your repo
- Render will automatically detect and use `render.yaml`

---

### Option 3: Docker Deployment (Self-Hosted)

**Best for:** Running on your own server (VPS, EC2, etc.)
**Files needed:** `Dockerfile` and `.dockerignore` (already created ✓)

#### Quick Start

1. **Build the Docker image**:
   ```bash
   docker build -t contactiq .
   ```

2. **Run the container**:
   ```bash
   # Using .env file
   docker run -p 8501:8501 --env-file .env contactiq
   
   # Or with individual environment variables
   docker run -p 8501:8501 \
     -e OPENAI_API_KEY="sk-..." \
     -e SUPABASE_URL="https://..." \
     -e SUPABASE_KEY="..." \
     # ... add other variables
     contactiq
   ```

3. **Access your app**:
   - Open browser to `http://localhost:8501`
   - If on a server, use `http://your-server-ip:8501`

#### Docker Compose (Recommended for Production)

Create a `docker-compose.yml` file:
```yaml
version: '3.8'

services:
  contactiq:
    build: .
    ports:
      - "8501:8501"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:
```bash
docker-compose up -d
```

### Option 4: Other Platforms

#### Railway.app
- Similar to Render, supports Docker
- Go to https://railway.app
- Connect GitHub repo → New Project → Deploy from GitHub
- Set environment variables in dashboard
- **Advantage**: Free tier with $5 credit monthly

#### Fly.io
- Great for global distribution
- Install flyctl: `curl -L https://fly.io/install.sh | sh`
- Run: `fly launch` (creates `fly.toml`)
- Set secrets: `fly secrets set KEY=value`
- Deploy: `fly deploy`

#### AWS (EC2/ECS/Lambda)
- **EC2**: Deploy Docker container, use Elastic Beanstalk for easier management
- **ECS**: Container orchestration, better for production
- **App Runner**: Serverless containers (similar to Render)
- Set environment variables via AWS Secrets Manager

#### Google Cloud Platform (Cloud Run)
- Serverless containers
- Deploy: `gcloud run deploy contactiq --source .`
- Set environment variables in Cloud Run dashboard
- **Advantage**: Pay per request, good for variable traffic

#### Azure (Container Instances/App Service)
- Use Azure Container Instances for simple deployments
- Or Azure App Service for managed containers
- Set environment variables in Azure Portal

---

## 🎯 Recommendation

**For easiest deployment:** Use **Streamlit Cloud** (Option 1)
- Zero configuration
- Free tier
- Automatic HTTPS
- Deploys in ~5 minutes

**For more control:** Use **Render** (Option 2)
- Docker support
- More customizable
- Good free tier

**For production/high traffic:** Use **Railway**, **Fly.io**, or cloud providers (AWS/GCP/Azure)

## Post-Deployment

1. **Verify**:
   - Authentication works
   - Pipeline executes correctly
   - Logging works
   - Dashboard displays metrics
   - Vector Store retrieval works

2. **Monitor**:
   - Check logs for errors
   - Monitor API usage (OpenAI dashboard)
   - Review dashboard metrics
   - Monitor Supabase database

3. **Maintenance**:
   - Regularly update knowledge base
   - Monitor confidence scores and escalation rates
   - Review and adjust thresholds as needed
   - Keep dependencies updated

## Troubleshooting

### Common Issues

1. **Configuration errors**:
   - Verify all environment variables are set
   - Check `.env` file format (no quotes around values)
   - Ensure Vector Store IDs are correct

2. **Database connection errors**:
   - Verify Supabase URL and key
   - Check database schema is created
   - Test connection: `python test_supabase_connection.py`

3. **OpenAI API errors**:
   - Verify API key is valid
   - Check API usage limits
   - Verify Vector Store IDs are correct

4. **Import errors**:
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`
   - Check Python version (3.12 or 3.13)

## Security Considerations

1. **Environment Variables**:
   - Never commit `.env` file to version control
   - Use secure password for `SESSION_PASSWORD`
   - Rotate API keys regularly

2. **Authentication**:
   - Use strong password for session authentication
   - Consider implementing OAuth for production

3. **API Keys**:
   - Store API keys securely
   - Use environment variables or secrets management
   - Monitor API usage for anomalies

4. **Database**:
   - Use Supabase Row Level Security (RLS) policies
   - Limit database access to necessary operations
   - Regularly backup database

## Performance Optimization

1. **Caching**:
   - Consider caching frequent queries
   - Cache Vector Store results if appropriate

2. **Async Operations**:
   - All services use async/await for better performance
   - Timeout handling prevents hanging requests

3. **Database**:
   - Index frequently queried columns
   - Use connection pooling for Supabase

4. **Monitoring**:
   - Monitor response times
   - Track API usage and costs
   - Review escalation rates

## Backup and Recovery

1. **Database Backups**:
   - Supabase provides automatic backups
   - Export data regularly: `pg_dump` or Supabase dashboard

2. **Vector Store Backups**:
   - Vector Stores are managed by OpenAI
   - Document Vector Store IDs and file IDs

3. **Code Backups**:
   - Use version control (Git)
   - Tag releases for easy rollback

## Scaling Considerations

1. **Horizontal Scaling**:
   - Streamlit Cloud handles scaling automatically
   - For self-hosted, use load balancer with multiple instances

2. **Database Scaling**:
   - Supabase handles database scaling
   - Monitor connection limits

3. **API Rate Limits**:
   - Monitor OpenAI API rate limits
   - Implement rate limiting if needed
   - Consider caching for frequently asked questions
