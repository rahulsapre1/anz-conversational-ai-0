"""Unit tests for Authentication module."""
import pytest
from unittest.mock import patch, Mock, MagicMock
from ui.auth import check_authentication, logout


def test_authentication_success():
    """Test successful authentication."""
    mock_session_state = MagicMock()
    mock_session_state.authenticated = True
    mock_session_state.__contains__ = lambda self, key: key == 'authenticated'
    
    with patch('ui.auth.st.session_state', mock_session_state):
        with patch('ui.auth.st.title'), patch('ui.auth.st.stop'):
            result = check_authentication()
            assert result == True


def test_authentication_failure():
    """Test failed authentication."""
    mock_session_state = MagicMock()
    mock_session_state.authenticated = False
    mock_session_state.__contains__ = lambda self, key: key == 'authenticated'
    
    with patch('ui.auth.st.session_state', mock_session_state):
        with patch('ui.auth.st.title'), patch('ui.auth.st.text_input'), \
             patch('ui.auth.st.button'), patch('ui.auth.st.stop'):
            # Should show password prompt
            check_authentication()
            # Test would need to verify UI elements shown


def test_authentication_not_in_session_state():
    """Test authentication when not in session state."""
    mock_session_state = MagicMock()
    mock_session_state.__contains__ = lambda self, key: False
    
    with patch('ui.auth.st.session_state', mock_session_state):
        with patch('ui.auth.st.title'), patch('ui.auth.st.text_input'), \
             patch('ui.auth.st.button'), patch('ui.auth.st.stop'):
            check_authentication()
            # Should set authenticated to False and show prompt


def test_logout():
    """Test logout functionality."""
    mock_session_state = MagicMock()
    mock_session_state.authenticated = True
    mock_session_state.__contains__ = lambda self, key: key == 'authenticated'
    
    with patch('ui.auth.st.session_state', mock_session_state):
        with patch('ui.auth.st.rerun') as mock_rerun:
            logout()
            # Should clear authenticated and rerun
            mock_rerun.assert_called_once()
