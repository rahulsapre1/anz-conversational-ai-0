# Task 1: Project Foundation & Configuration

## Overview
Set up the project structure, environment configuration, dependencies, and basic Streamlit scaffold.

## Prerequisites
- Python 3.12 or 3.13 installed
- Virtual environment tool (venv)
- Git (for version control)

## Deliverables

### 1. Project Structure
Create the following directory structure (flattish):

```
contactiq/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── main.py                      # Streamlit app entry point
├── config.py                    # Configuration management
├── services/
│   ├── __init__.py
│   ├── intent_classifier.py
│   ├── router.py
│   ├── retrieval_service.py
│   ├── response_generator.py
│   ├── confidence_scorer.py
│   ├── escalation_handler.py
│   └── logger.py
├── knowledge/
│   ├── __init__.py
│   ├── ingestor.py
│   └── synthetic_generator.py
├── database/
│   ├── __init__.py
│   ├── schema.sql
│   ├── supabase_client.py
│   └── migrations/
├── ui/
│   ├── __init__.py
│   ├── auth.py                  # Authentication (password check)
│   ├── chat_interface.py
│   ├── dashboard.py
│   └── components.py
└── utils/
    ├── __init__.py
    ├── openai_client.py
    ├── validators.py
    └── constants.py
```

### 2. .gitignore
Create `.gitignore` with:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Streamlit
.streamlit/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

### 3. requirements.txt
```python
streamlit>=1.31.0
openai>=1.12.0
supabase>=2.0.0
python-dotenv>=1.0.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
requests>=2.31.0
pandas>=2.1.0
pydantic>=2.5.0
python-dateutil>=2.8.0
# Async support
aiohttp>=3.9.0
asyncio>=3.4.3
# Structured logging
structlog>=23.2.0
# Timeout handling
httpx>=0.25.0  # For async HTTP with timeout support
```

### 4. .env.example
```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_VECTOR_STORE_ID_CUSTOMER=vs_...
OPENAI_VECTOR_STORE_ID_BANKER=vs_...

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...

# Application
CONFIDENCE_THRESHOLD=0.68
LOG_LEVEL=INFO
SESSION_PASSWORD=rahul  # Simple password for session authentication
API_TIMEOUT=30  # Timeout in seconds for all API calls
```

### 5. config.py
Create configuration module that loads environment variables:

```python
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Application configuration loaded from environment variables."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_VECTOR_STORE_ID_CUSTOMER: Optional[str] = os.getenv("OPENAI_VECTOR_STORE_ID_CUSTOMER")
    OPENAI_VECTOR_STORE_ID_BANKER: Optional[str] = os.getenv("OPENAI_VECTOR_STORE_ID_BANKER")
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Application Configuration
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.68"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Authentication
    SESSION_PASSWORD: str = os.getenv("SESSION_PASSWORD", "rahul")
    
    # Timeouts
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))  # 30 seconds default
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        required = [
            cls.OPENAI_API_KEY,
            cls.SUPABASE_URL,
            cls.SUPABASE_KEY,
        ]
        return all(required)
    
    @classmethod
    def get_missing_config(cls) -> list[str]:
        """Get list of missing required configuration keys."""
        missing = []
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not cls.SUPABASE_URL:
            missing.append("SUPABASE_URL")
        if not cls.SUPABASE_KEY:
            missing.append("SUPABASE_KEY")
        return missing

# Validate on import
if not Config.validate():
    missing = Config.get_missing_config()
    raise ValueError(f"Missing required configuration: {', '.join(missing)}")
```

### 6. Structured Logging Setup (utils/logger.py)

Create a structured logging utility:

```python
# utils/logger.py
import structlog
import logging
import sys
from config import Config

def setup_logging():
    """Configure structured logging with log levels."""
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Set log level from config
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

def get_logger(name: str = __name__):
    """Get a structured logger instance."""
    return structlog.get_logger(name)
```

### 7. main.py (Basic Streamlit Scaffold)

```python
import streamlit as st
import sys
from config import Config
from ui.auth import check_authentication
from utils.logger import setup_logging, get_logger

# Setup structured logging
setup_logging()
logger = get_logger(__name__)

st.set_page_config(
    page_title="ContactIQ",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Note: Authentication check will be added in Task 15
    # check_authentication()
    
    st.title("ContactIQ")
    st.subtitle("Conversational AI for Banking (MVP)")
    
    # Check configuration
    if not Config.validate():
        st.error("❌ Configuration Error")
        st.write(f"Missing configuration: {', '.join(Config.get_missing_config())}")
        st.write("Please check your .env file.")
        logger.error("configuration_missing", missing=Config.get_missing_config())
        return
    
    logger.info("app_started", page="main")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Navigate",
        ["Chat", "Dashboard"]
    )
    
    if page == "Chat":
        st.header("Chat Interface")
        st.write("Chat interface will be implemented here.")
        # TODO: Import and use chat_interface
    
    elif page == "Dashboard":
        st.header("KPI Dashboard")
        st.write("Dashboard will be implemented here.")
        # TODO: Import and use dashboard

if __name__ == "__main__":
    main()
```

### 8. Create __init__.py files
Create empty `__init__.py` files in:
- `services/__init__.py`
- `knowledge/__init__.py`
- `database/__init__.py`
- `ui/__init__.py`
- `utils/__init__.py`

## Setup Instructions

1. **Create virtual environment:**
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create .env file:**
```bash
cp .env.example .env
# Edit .env with your actual keys
```

4. **Test configuration:**
```python
# In Python shell
from config import Config
print(f"OpenAI Model: {Config.OPENAI_MODEL}")
print(f"Confidence Threshold: {Config.CONFIDENCE_THRESHOLD}")
```

5. **Run Streamlit app:**
```bash
streamlit run main.py
```

## Validation Checklist

- [ ] Project structure matches specification (including ui/auth.py)
- [ ] .gitignore includes Python, env files, IDE files
- [ ] requirements.txt includes all dependencies (including async and logging libraries)
- [ ] .env.example has all required keys (including SESSION_PASSWORD, API_TIMEOUT)
- [ ] config.py loads environment variables correctly (including new settings)
- [ ] config.py validates required configuration
- [ ] Structured logging setup (utils/logger.py) created
- [ ] main.py runs without errors
- [ ] Authentication check integrated in main.py
- [ ] Streamlit app displays authentication prompt when not authenticated
- [ ] Streamlit app displays basic interface after authentication
- [ ] All __init__.py files created
- [ ] Virtual environment works
- [ ] Dependencies install without errors

## Integration Points

This task sets up the foundation for:
- **Task 2**: Database setup will use config.py for Supabase credentials
- **Task 3**: OpenAI setup will use config.py for OpenAI API key
- **All Services**: Will import from config.py for configuration

## Notes

- Use absolute imports within the project (e.g., `from services.intent_classifier import IntentClassifier`)
- Keep the structure flattish as requested
- All configuration must come from environment variables (no hardcoded values)
- Validate configuration on startup to fail fast

## Common Issues

1. **Module import errors**: Ensure all __init__.py files exist
2. **Environment variable not found**: Check .env file exists and is in project root
3. **Python version mismatch**: Ensure using Python 3.12 or 3.13
4. **Streamlit not found**: Install from requirements.txt

## Success Criteria

✅ Project structure matches DETAILED_PLAN.md Section 1
✅ Environment variables load correctly from .env
✅ Streamlit app runs without errors
✅ All dependencies installable from requirements.txt
✅ Configuration validation works
