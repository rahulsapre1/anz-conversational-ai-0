# ContactIQ 💬

**Conversational AI for Banking (MVP)**

A safe, transparent AI system for handling banking queries with policy-backed responses, confidence scoring, and automatic escalation.

---

## 🎯 Quick Start

```bash
git clone https://github.com/rahulsapre1/anz-conversational-ai-0.git
cd anz-conversational-ai-0
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Fill in your keys
streamlit run main.py
```

**Deploy:** See [`QUICK_DEPLOY.md`](QUICK_DEPLOY.md) for Streamlit Cloud deployment (5 minutes)

---

## 🏗️ Architecture

```mermaid
graph TB
    A[Streamlit Frontend] --> B[Authentication]
    B --> C[Chat Interface]
    B --> D[Dashboard]
    B --> E[Tested Questions]
    C --> F[AI Pipeline]
    F --> G[(Supabase DB)]
    F --> H[OpenAI API]
    H --> I[Vector Store]
```

---

## 🔄 Pipeline Flow

```mermaid
flowchart LR
    A[User Query] --> B[1. Intent<br/>Classification]
    B --> C[2. Router]
    C -->|Automatable| D[3. Retrieval<br/>Vector Store]
    C -->|Human Only| H[Escalate]
    D --> E[4. Response<br/>Generation]
    E --> F[5. Confidence<br/>Scoring]
    F -->|≥0.68| G[Return Response]
    F -->|<0.68| H[6. Escalation]
    G --> I[7. Logging]
    H --> I
```

---

## 📊 Features

```mermaid
mindmap
  root((ContactIQ))
    Dual Modes
      Customer Assistant
      Banker Assistant
    Safety
      Confidence Scoring
      Auto Escalation
      Policy-Backed
    Transparency
      Citations
      Confidence Scores
      Escalation Reasons
    Analytics
      KPI Dashboard
      Time-Based Trends
      Tested Questions
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **Backend** | Python 3.12+ (async/await) |
| **AI/ML** | OpenAI gpt-4o-mini, Vector Store |
| **Database** | Supabase PostgreSQL |
| **Logging** | structlog |

---

## 📁 Project Structure

```
anz-conversational-ai-0/
├── main.py              # Entry point
├── config.py            # Configuration
├── services/            # Pipeline services (async)
│   ├── intent_classifier.py
│   ├── router.py
│   ├── retrieval_service.py
│   ├── response_generator.py
│   ├── confidence_scorer.py
│   ├── escalation_handler.py
│   └── logger.py
├── ui/                  # Streamlit UI
│   ├── auth.py
│   ├── chat_interface.py
│   ├── dashboard.py
│   └── tested_questions.py
├── database/            # Supabase schema & client
├── knowledge/           # Vector Store setup
└── tests/               # Test suite (56 tests)
```

---

## ⚙️ Configuration

Required environment variables (`.env`):

```bash
OPENAI_API_KEY=sk-...
OPENAI_VECTOR_STORE_ID_CUSTOMER=vs_...
OPENAI_VECTOR_STORE_ID_BANKER=vs_...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
SESSION_PASSWORD=your-password
```

See [`SETUP_SUPABASE.md`](SETUP_SUPABASE.md) for database setup.

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# With coverage
pytest --cov=services --cov=ui --cov-report=html tests/
```

**Test Coverage:** 56 tests covering all services, integration, auth, timeouts, and logging.

---

## 🚀 Deployment

### Streamlit Cloud (Recommended - Free)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy and add secrets
4. **Done!** ⚡

See [`QUICK_DEPLOY.md`](QUICK_DEPLOY.md) for step-by-step guide.

### Render / Railway / Fly.io
- Use provided `Dockerfile`
- See [`DEPLOYMENT.md`](DEPLOYMENT.md) for details

---

## 📈 Safety & Escalation

The system escalates when:

```mermaid
graph LR
    A[Query] --> B{Intent Type?}
    B -->|Human Only| E[Escalate]
    B -->|Automatable| C{Confidence?}
    C -->|≥0.68| D[Respond]
    C -->|<0.68| E[Escalate]
    B -->|Security/Fraud| E
    B -->|Financial Advice| E
    B -->|Account-Specific| E
```

**Escalation Triggers:**
- Intent category: `HumanOnly`
- Confidence score < `0.68`
- Security/fraud requests
- Account-specific queries
- Financial advice requests

---

## 📚 Documentation

- [`QUICK_DEPLOY.md`](QUICK_DEPLOY.md) - Fast deployment guide
- [`DEPLOYMENT.md`](DEPLOYMENT.md) - Complete deployment guide
- [`IMPLEMENTATION_GUIDE.md`](IMPLEMENTATION_GUIDE.md) - Implementation details
- [`PRD.md`](PRD.md) - Product Requirements Document
- [`guides/MASTER_INDEX.md`](guides/MASTER_INDEX.md) - Task guides index

---

## ⚠️ Safety Notice

**ContactIQ does not provide financial advice and always escalates when uncertainty exists.**

---

## 📝 License

[Your License Here]

---

## 🔗 Links

- **Repository:** https://github.com/rahulsapre1/anz-conversational-ai-0
- **Deploy:** https://share.streamlit.io (Streamlit Cloud)
