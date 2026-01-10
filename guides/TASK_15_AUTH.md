# Task 15: Authentication Module

## Overview
Implement simple password authentication at session start to protect the application from unauthorized access.

## Prerequisites
- Task 1 (Foundation) completed
- Config module with SESSION_PASSWORD setting

## Deliverables

### 1. Authentication Module (ui/auth.py)

Create `ui/auth.py` with password authentication functionality.

**Implementation:**
```python
# ui/auth.py
import streamlit as st
from config import Config

def check_authentication():
    """
    Check if user is authenticated, show password prompt if not.
    
    Returns:
        bool: True if authenticated, False otherwise (and shows prompt)
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        # Show authentication UI
        st.title("🔐 ContactIQ - Authentication Required")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Please enter the password to continue")
            password = st.text_input(
                "Password:",
                type="password",
                key="password_input",
                label_visibility="visible"
            )
            
            if st.button("Login", type="primary", use_container_width=True):
                if password == Config.SESSION_PASSWORD:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Please try again.")
        
        st.stop()
    
    return True


def logout():
    """Clear authentication state and rerun app."""
    if "authenticated" in st.session_state:
        del st.session_state.authenticated
    st.rerun()
```

### 2. Update Config Module

Ensure `config.py` includes the SESSION_PASSWORD setting:

```python
# config.py (add to existing Config class)
class Config:
    # ... existing config ...
    
    # Authentication
    SESSION_PASSWORD = os.getenv("SESSION_PASSWORD", "rahul")
```

### 3. Update .env.example

Add SESSION_PASSWORD to `.env.example`:

```bash
# Authentication
SESSION_PASSWORD=rahul
```

### 4. Integration in main.py

Update `main.py` to use authentication:

```python
# main.py
import streamlit as st
from ui.auth import check_authentication

# Check authentication before showing any content
check_authentication()

# Rest of the application...
st.title("ContactIQ")
# ... rest of UI
```

## Implementation Details

### Authentication Flow

1. **User opens application**
   - `check_authentication()` is called at the start of `main.py`
   - Checks if `st.session_state.authenticated` exists and is True

2. **If not authenticated:**
   - Display password prompt UI
   - User enters password
   - On "Login" button click:
     - Compare password with `Config.SESSION_PASSWORD`
     - If correct: Set `st.session_state.authenticated = True` and rerun
     - If incorrect: Show error message and allow retry

3. **If authenticated:**
   - Continue to main application
   - Authentication state persists for the session duration

### Security Considerations

**Note**: This is a simple password-based authentication for MVP purposes. For production:
- Consider implementing proper authentication (OAuth2, JWT)
- Use environment variables for password (never hardcode)
- Implement session expiration
- Add rate limiting for login attempts
- Use secure password hashing

**Current Implementation:**
- Password stored in environment variable (not hardcoded)
- Session-based (persists for Streamlit session)
- Simple password comparison (no hashing for MVP)

### Error Handling

- **Incorrect password**: Show error message, allow retry
- **Empty password**: Allow user to enter password
- **Config missing**: Default to "rahul" (for development)

### UI/UX

- Clean, centered password prompt
- Password input field with hidden characters
- Clear error messaging
- Primary button for login action
- Professional appearance matching ContactIQ branding

## Success Criteria

- [ ] `ui/auth.py` created with `check_authentication()` function
- [ ] Password prompt displayed when not authenticated
- [ ] Correct password ("rahul") grants access
- [ ] Incorrect password shows error message
- [ ] Authenticated state persists for session
- [ ] Main application only accessible after authentication
- [ ] Config module includes SESSION_PASSWORD
- [ ] .env.example includes SESSION_PASSWORD
- [ ] main.py integrates authentication check

## Testing

### Manual Testing

1. **Test Authentication Prompt:**
   - Run application
   - Verify password prompt is displayed
   - Verify UI is clean and centered

2. **Test Correct Password:**
   - Enter correct password ("rahul")
   - Click "Login"
   - Verify main application is shown
   - Verify no password prompt on page refresh (within session)

3. **Test Incorrect Password:**
   - Enter incorrect password
   - Click "Login"
   - Verify error message is displayed
   - Verify password prompt remains visible
   - Verify can retry with correct password

4. **Test Session Persistence:**
   - Authenticate successfully
   - Navigate through application
   - Verify authentication persists
   - Verify no re-authentication required

5. **Test Environment Variable:**
   - Set SESSION_PASSWORD in .env to different value
   - Restart application
   - Verify new password works
   - Verify old password no longer works

## Reference

- **DETAILED_PLAN.md** Section 9.1 (Authentication)
- **TASK_BREAKDOWN.md** Task 15
- **Streamlit Session State**: https://docs.streamlit.io/library/api-reference/session-state

## Notes

- Authentication is session-based (Streamlit session_state)
- Password is configurable via environment variable
- Simple implementation suitable for MVP
- Can be enhanced for production with proper auth mechanisms
