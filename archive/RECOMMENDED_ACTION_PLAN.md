# ContactIQ - Recommended Action Plan
**Based on Architecture Audit**

**Last Updated**: After implementation of authentication, async architecture, structured logging, and timeout handling

---

## Quick Summary

**Total Issues Found**: 25+ architectural loopholes  
**Critical Issues**: 8 (must fix before MVP)  
**High Priority**: 7 (should fix before MVP)  
**Medium Priority**: 10 (can fix post-MVP)

**Status**: 
- ✅ **Completed**: Basic Authentication, Structured Logging
- ⚠️ **Partially Completed**: Timeout Handling (30s implemented, but not all scenarios)
- ❌ **Not Yet Implemented**: Rate Limiting, PII Masking, Input Validation, Error Recovery, etc.

**Estimated Additional Time**: 2-4 days for remaining critical fixes

---

## 🚨 MUST FIX BEFORE MVP (Critical)

### 1. Security Foundation (2 days)

#### 1.1 Basic Authentication & Rate Limiting
**Status**: ✅ **PARTIALLY COMPLETED**
- ✅ **Authentication**: Implemented as Task 15 (simple password authentication)
- ❌ **Rate Limiting**: Not yet implemented
```python
# Add to main.py or middleware
- API key validation (if full auth is out of scope)
- Rate limiting: 10 requests/minute per session
- IP-based throttling: 100 requests/hour per IP
- Use: slowapi or flask-limiter for Streamlit
```

**Files to modify**:
- `main.py` - Add rate limiting middleware
- `config.py` - Add rate limit configuration
- `utils/rate_limiter.py` - New file for rate limiting logic

**Time**: 0.5 days

---

#### 1.2 PII Detection & Masking
```python
# Add to services/logger.py before logging
import re

def mask_pii(text: str) -> tuple[str, bool]:
    """Mask PII in text and return masked text + detection flag."""
    pii_detected = False
    
    # Account numbers (4+ digits)
    text = re.sub(r'\b\d{4,}\b', '[ACCOUNT_MASKED]', text)
    
    # Credit cards (16 digits)
    text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD_MASKED]', text)
    
    # Emails
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_MASKED]', text)
    
    # Phone numbers
    text = re.sub(r'\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b', '[PHONE_MASKED]', text)
    
    return text, pii_detected
```

**Files to modify**:
- `services/logger.py` - Add PII masking before logging
- `utils/pii_detector.py` - New file for PII detection

**Time**: 0.5 days

---

#### 1.3 Input Validation & Sanitization
```python
# Add to utils/validators.py
def validate_user_query(query: str) -> tuple[str, bool, Optional[str]]:
    """Validate and sanitize user query."""
    if not query or not isinstance(query, str):
        return "", False, "Query must be a non-empty string"
    
    if len(query) > 2000:
        return query[:2000], False, "Query too long (max 2000 chars)"
    
    # Basic sanitization
    query = query.strip()
    
    # Block obvious injection attempts
    dangerous_patterns = [
        r'<script', r'javascript:', r'onerror=', 
        r'union\s+select', r'drop\s+table'
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return "", False, "Query contains potentially dangerous content"
    
    return query, True, None
```

**Files to modify**:
- `utils/validators.py` - Add input validation
- `main.py` - Validate before processing

**Time**: 0.5 days

---

#### 1.4 Secure API Key Management
```python
# Update config.py to use environment variables securely
# Never commit .env to git

# Add to .gitignore (if not already):
.env
.env.local
.env.*.local
*.key
*.pem

# Use python-dotenv for loading
# Consider using AWS Secrets Manager for production
```

**Files to modify**:
- `.gitignore` - Ensure .env is ignored
- `config.py` - Add validation for required keys
- Add secrets management documentation

**Time**: 0.5 days

---

### 2. Data Integrity & Reliability (1.5 days)

#### 2.1 Transaction Management & Idempotency
```python
# Add to services/logger.py
import uuid
from typing import Optional

class InteractionLogger:
    def __init__(self):
        self.db_client = get_db_client()
        self.start_time: Optional[float] = None
    
    def log_interaction_start(
        self,
        assistant_mode: str,
        user_query: str,
        request_id: Optional[str] = None
    ) -> str:
        """Log interaction start with request_id for idempotency."""
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Check if request_id already exists (idempotency)
        existing = self.db_client.get_interaction_by_request_id(request_id)
        if existing:
            logger.warning(f"Duplicate request_id: {request_id}")
            return existing['id']
        
        # Insert with request_id
        interaction_id = self.db_client.insert_interaction({
            "request_id": request_id,
            "assistant_mode": assistant_mode,
            "user_query": user_query,
            "outcome": "processing",  # Initial state
            # ... other fields
        })
        
        return interaction_id
    
    def log_interaction_complete(
        self,
        interaction_id: str,
        **updates
    ):
        """Update interaction on completion (atomic)."""
        # Use database transaction for atomic update
        self.db_client.update_interaction(interaction_id, updates)
```

**Files to modify**:
- `services/logger.py` - Add idempotency and transaction support
- `database/supabase_client.py` - Add transaction methods
- `database/schema.sql` - Add request_id column with unique constraint

**Time**: 1 day

---

#### 2.2 Async Logging Queue
**Status**: ✅ **COMPLETED**
- ✅ **Implementation**: Async logging implemented in Task 14 (non-blocking)
- ✅ **Features**: Async database operations with 30s timeout, retry queue for failed logs
- ⚠️ **Note**: Background worker pattern recommended but not yet implemented
```python
# Add to services/logger.py
import asyncio
from queue import Queue
import threading

class InteractionLogger:
    def __init__(self):
        self.db_client = get_db_client()
        self.log_queue = Queue()
        self.worker_thread = None
        self._start_worker()
    
    def _start_worker(self):
        """Start background worker for async logging."""
        def worker():
            while True:
                try:
                    log_data = self.log_queue.get(timeout=1)
                    if log_data is None:  # Shutdown signal
                        break
                    self._write_log(log_data)
                    self.log_queue.task_done()
                except Exception as e:
                    logger.error(f"Logging worker error: {e}")
        
        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()
    
    def log_interaction_async(self, **kwargs):
        """Queue log for async writing (non-blocking)."""
        self.log_queue.put(kwargs)
    
    def _write_log(self, log_data):
        """Actually write log to database."""
        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.db_client.insert_interaction(log_data)
                return
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to log after {max_retries} attempts: {e}")
                    # Could send to dead letter queue here
                else:
                    time.sleep(2 ** attempt)  # Exponential backoff
```

**Files to modify**:
- `services/logger.py` - Add async logging queue
- `main.py` - Use async logging (don't block on logging)

**Time**: 0.5 days

---

#### 2.3 Data Validation with Pydantic
```python
# Add to utils/validators.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any

class IntentClassification(BaseModel):
    intent_name: str = Field(..., min_length=1, max_length=100)
    intent_category: str = Field(..., regex="^(automatable|sensitive|human_only)$")
    classification_reason: str = Field(..., min_length=1, max_length=1000)

class ConfidenceScore(BaseModel):
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: Optional[str] = None

class InteractionLog(BaseModel):
    assistant_mode: str = Field(..., regex="^(customer|banker)$")
    user_query: str = Field(..., min_length=1, max_length=5000)
    intent_name: Optional[str] = None
    intent_category: Optional[str] = Field(None, regex="^(automatable|sensitive|human_only)$")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    outcome: str = Field(..., regex="^(resolved|escalated|processing)$")
    
    @validator('confidence_score')
    def validate_confidence(cls, v):
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError('Confidence score must be between 0.0 and 1.0')
        return v
```

**Files to modify**:
- `utils/validators.py` - Add Pydantic models
- All services - Use Pydantic for validation

**Time**: 0.5 days

---

### 3. Observability (1 day)

#### 3.1 Structured Logging
**Status**: ✅ **COMPLETED**
- ✅ **Implementation**: structlog with ERROR, WARN, INFO levels implemented in Task 14
- ✅ **Features**: All API calls logged with processing times, pipeline step tracking
- ✅ **Location**: `utils/logger.py`, `services/logger.py`
- ⚠️ **Note**: PII masking still recommended (see 1.2)
```python
# Add to utils/logger.py (new file)
import json
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.correlation_id: Optional[str] = None
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for request tracing."""
        self.correlation_id = correlation_id
    
    def _log(self, level: str, message: str, **context):
        """Log with structured JSON format."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "correlation_id": self.correlation_id,
            **context
        }
        
        # Use JSON formatter
        self.logger.log(
            getattr(logging, level.upper()),
            json.dumps(log_entry)
        )
    
    def info(self, message: str, **context):
        self._log("INFO", message, **context)
    
    def error(self, message: str, **context):
        self._log("ERROR", message, **context)
    
    def warn(self, message: str, **context):
        self._log("WARN", message, **context)
    
    def debug(self, message: str, **context):
        self._log("DEBUG", message, **context)
```

**Files to create/modify**:
- `utils/structured_logger.py` - New file
- All services - Use structured logger

**Time**: 0.5 days

---

#### 3.2 Basic Monitoring & Health Checks
```python
# Add to main.py
import time
from datetime import datetime

def health_check():
    """Health check endpoint."""
    checks = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check database
    try:
        db_client = get_db_client()
        db_client.health_check()  # Simple query
        checks["checks"]["database"] = "healthy"
    except Exception as e:
        checks["checks"]["database"] = f"unhealthy: {str(e)}"
        checks["status"] = "degraded"
    
    # Check OpenAI API
    try:
        openai_client = get_openai_client()
        # Simple API call or just check if client exists
        checks["checks"]["openai"] = "healthy"
    except Exception as e:
        checks["checks"]["openai"] = f"unhealthy: {str(e)}"
        checks["status"] = "degraded"
    
    return checks

# Add to Streamlit
if st.sidebar.button("Health Check"):
    health = health_check()
    st.json(health)
```

**Files to modify**:
- `main.py` - Add health check
- `database/supabase_client.py` - Add health_check method

**Time**: 0.5 days

---

#### 3.3 Error Tracking (Sentry)
```python
# Add to requirements.txt
sentry-sdk[streamlit]>=1.40.0

# Add to main.py or config.py
import sentry_sdk
from sentry_sdk.integrations.streamlit import StreamlitIntegration

def init_sentry():
    """Initialize Sentry for error tracking."""
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[StreamlitIntegration()],
            traces_sample_rate=0.1,  # 10% of transactions
            environment=os.getenv("ENVIRONMENT", "development")
        )
```

**Files to modify**:
- `requirements.txt` - Add sentry-sdk
- `main.py` - Initialize Sentry
- `config.py` - Add SENTRY_DSN

**Time**: 0.5 days

---

## 📋 Implementation Checklist

### Phase 1: Critical Security (2 days)
- [ ] Add rate limiting (10 req/min per session) - **NOT YET IMPLEMENTED**
- [ ] Implement PII detection and masking - **NOT YET IMPLEMENTED**
- [ ] Add input validation and sanitization - **NOT YET IMPLEMENTED**
- [ ] Secure API key management (verify .gitignore) - **NOT YET IMPLEMENTED**
- [x] Add basic authentication (API key or session-based) - **✅ COMPLETED** (Task 15: Simple password authentication)

### Phase 2: Data Integrity (1.5 days)
- [ ] Add request_id for idempotency - **NOT YET IMPLEMENTED**
- [ ] Implement transaction management for logging - **NOT YET IMPLEMENTED**
- [x] Add async logging queue (non-blocking) - **✅ COMPLETED** (Task 14: Async logging with timeout)
- [ ] Add Pydantic models for data validation - **NOT YET IMPLEMENTED**
- [ ] Update database schema with constraints - **NOT YET IMPLEMENTED**

### Phase 3: Observability (1 day)
- [x] Implement structured logging (JSON format) - **✅ COMPLETED** (Task 14: structlog with ERROR, WARN, INFO)
- [ ] Add correlation IDs for request tracing - **NOT YET IMPLEMENTED**
- [ ] Add health check endpoint - **NOT YET IMPLEMENTED**
- [ ] Integrate Sentry for error tracking - **NOT YET IMPLEMENTED**
- [ ] Add basic metrics collection - **NOT YET IMPLEMENTED**

### Phase 4: Post-MVP (Optional)
- [x] Implement async pipeline (async/await) - **✅ COMPLETED** (Throughout pipeline: Tasks 8, 10, 11, 12, 14)
- [ ] Add request queuing - **NOT YET IMPLEMENTED**
- [ ] Implement caching (Redis) - **NOT YET IMPLEMENTED**
- [ ] Add circuit breakers - **NOT YET IMPLEMENTED**
- [ ] Implement comprehensive testing (80% coverage) - **NOT YET IMPLEMENTED** (Task 19 planned)

---

## 🎯 Quick Wins (Can do in 1-2 hours each)

1. **Add .env to .gitignore** (if not already) - 5 minutes
2. **Add request_id column to database** - 30 minutes
3. **Add basic input length validation** - 30 minutes
4. **Add structured logging format** - 1 hour
5. **Add health check endpoint** - 1 hour
6. **Add PII masking for account numbers** - 1 hour

---

## 📊 Priority Matrix

| Issue | Impact | Effort | Priority | Phase |
|-------|--------|--------|----------|-------|
| Rate Limiting | High | Low | 🔴 Critical | Phase 1 |
| PII Masking | Critical | Medium | 🔴 Critical | Phase 1 |
| Input Validation | High | Low | 🔴 Critical | Phase 1 |
| Transaction Management | High | Medium | 🔴 Critical | Phase 2 |
| Async Logging | Medium | Low | ✅ **COMPLETED** | Phase 2 |
| Structured Logging | Medium | Low | ✅ **COMPLETED** | Phase 3 |
| Error Tracking | Medium | Low | 🟠 High | Phase 3 |
| Health Checks | Low | Low | 🟠 High | Phase 3 |

---

## 🚀 Recommended Execution Order

1. **Day 1 Morning**: Security basics (rate limiting, input validation, .env security)
2. **Day 1 Afternoon**: PII masking implementation
3. **Day 2 Morning**: Transaction management and idempotency
4. **Day 2 Afternoon**: Async logging queue
5. **Day 3 Morning**: Structured logging and correlation IDs
6. **Day 3 Afternoon**: Health checks and error tracking setup

**Total**: 3 days for all critical fixes

---

## 📝 Code Examples Location

All code examples above should be integrated into:
- `utils/rate_limiter.py` - Rate limiting
- `utils/pii_detector.py` - PII detection
- `utils/validators.py` - Input validation (enhanced)
- `services/logger.py` - Enhanced logging with async queue
- `utils/structured_logger.py` - Structured logging
- `main.py` - Health checks and middleware

---

## ✅ Success Criteria

After implementing Phase 1-3:
- ✅ All user inputs validated and sanitized
- ✅ PII masked before logging
- ✅ Rate limiting prevents abuse
- ✅ Logging is non-blocking
- ✅ All operations are idempotent
- ✅ Errors are tracked and visible
- ✅ System health is monitorable

---

**Next Steps**:
1. Review this action plan
2. Prioritize based on your timeline
3. Start with quick wins
4. Implement Phase 1-3 before MVP launch
5. Schedule Phase 4 for post-MVP
