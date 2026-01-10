"""Unit tests for Router service."""
import pytest
from services.router import Router, route


def test_route_human_only():
    """Test routing for human_only category."""
    result = route("human_only", "financial_advice", "customer")
    
    assert result["route"] == "escalate"
    assert result["next_step"] == 6
    assert result["skip_to_step"] == 6


def test_route_automatable():
    """Test routing for automatable category."""
    result = route("automatable", "fee_inquiry", "customer")
    
    assert result["route"] == "continue"
    assert result["next_step"] == 3


def test_route_sensitive():
    """Test routing for sensitive category."""
    result = route("sensitive", "account_balance", "customer")
    
    assert result["route"] == "continue"
    assert result["next_step"] == 3


def test_route_invalid_category():
    """Test routing for invalid category."""
    result = route("invalid_category", None, None)
    
    # Should default to escalate
    assert result["route"] == "escalate"
    assert result["next_step"] == 6


def test_router_class():
    """Test Router class methods."""
    router = Router()
    
    assert router.should_escalate("human_only") == True
    assert router.should_escalate("automatable") == False
    
    assert router.get_next_step("human_only") == 6
    assert router.get_next_step("automatable") == 3


def test_router_route_method():
    """Test Router class route method."""
    router = Router()
    
    result = router.route("human_only", "test_intent", "customer")
    
    assert result["route"] == "escalate"
    assert result["next_step"] == 6
