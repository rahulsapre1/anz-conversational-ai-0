#!/usr/bin/env python3
"""
Test script for Task 9: Router Service

This script tests:
1. Routing for human_only category (should escalate)
2. Routing for automatable category (should continue)
3. Routing for sensitive category (should continue)
4. Invalid category handling (should default to escalate)
5. Router class helper methods
6. Response structure validation
"""

import sys
import logging
from utils.logger import setup_logging

# Setup logging
setup_logging()

def test_route_human_only():
    """Test routing for human_only category."""
    print("=" * 60)
    print("Testing HumanOnly Intent Routing")
    print("=" * 60)
    print()
    
    try:
        from services.router import route
        
        test_cases = [
            ("human_only", "financial_advice", "customer"),
            ("human_only", "complaint", "customer"),
            ("human_only", "fraud_alert", "customer"),
            ("human_only", "unknown", "customer"),
        ]
        
        passed = 0
        failed = 0
        
        for intent_category, intent_name, assistant_mode in test_cases:
            print(f"Testing: {intent_category} ({intent_name}, {assistant_mode})")
            
            result = route(intent_category, intent_name, assistant_mode)
            
            if result["route"] == "escalate" and result["next_step"] == 6:
                print(f"  ✅ PASSED: Route={result['route']}, Next Step={result['next_step']}")
                print(f"     Reason: {result['reason']}")
                passed += 1
            else:
                print(f"  ❌ FAILED: Expected escalate/6, got {result['route']}/{result['next_step']}")
                failed += 1
            print()
        
        print(f"Results: {passed} passed, {failed} failed")
        print()
        return failed == 0
        
    except Exception as e:
        print(f"❌ Error testing human_only routing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_route_automatable():
    """Test routing for automatable category."""
    print("=" * 60)
    print("Testing Automatable Intent Routing")
    print("=" * 60)
    print()
    
    try:
        from services.router import route
        
        test_cases = [
            ("automatable", "fee_inquiry", "customer"),
            ("automatable", "transaction_explanation", "customer"),
            ("automatable", "account_limits", "customer"),
            ("automatable", "policy_lookup", "banker"),
        ]
        
        passed = 0
        failed = 0
        
        for intent_category, intent_name, assistant_mode in test_cases:
            print(f"Testing: {intent_category} ({intent_name}, {assistant_mode})")
            
            result = route(intent_category, intent_name, assistant_mode)
            
            if result["route"] == "continue" and result["next_step"] == 3:
                print(f"  ✅ PASSED: Route={result['route']}, Next Step={result['next_step']}")
                print(f"     Reason: {result['reason']}")
                passed += 1
            else:
                print(f"  ❌ FAILED: Expected continue/3, got {result['route']}/{result['next_step']}")
                failed += 1
            print()
        
        print(f"Results: {passed} passed, {failed} failed")
        print()
        return failed == 0
        
    except Exception as e:
        print(f"❌ Error testing automatable routing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_route_sensitive():
    """Test routing for sensitive category."""
    print("=" * 60)
    print("Testing Sensitive Intent Routing")
    print("=" * 60)
    print()
    
    try:
        from services.router import route
        
        test_cases = [
            ("sensitive", "account_balance", "customer"),
            ("sensitive", "transaction_history", "customer"),
            ("sensitive", "password_reset", "customer"),
            ("sensitive", "customer_specific_query", "banker"),
        ]
        
        passed = 0
        failed = 0
        
        for intent_category, intent_name, assistant_mode in test_cases:
            print(f"Testing: {intent_category} ({intent_name}, {assistant_mode})")
            
            result = route(intent_category, intent_name, assistant_mode)
            
            if result["route"] == "continue" and result["next_step"] == 3:
                print(f"  ✅ PASSED: Route={result['route']}, Next Step={result['next_step']}")
                print(f"     Reason: {result['reason']}")
                passed += 1
            else:
                print(f"  ❌ FAILED: Expected continue/3, got {result['route']}/{result['next_step']}")
                failed += 1
            print()
        
        print(f"Results: {passed} passed, {failed} failed")
        print()
        return failed == 0
        
    except Exception as e:
        print(f"❌ Error testing sensitive routing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_route_invalid_category():
    """Test routing for invalid category."""
    print("=" * 60)
    print("Testing Invalid Category Handling")
    print("=" * 60)
    print()
    
    try:
        from services.router import route
        
        test_cases = [
            ("invalid_category", None, None),
            ("", None, None),
            ("unknown_category", "test", "customer"),
        ]
        
        passed = 0
        failed = 0
        
        for intent_category, intent_name, assistant_mode in test_cases:
            print(f"Testing invalid category: '{intent_category}'")
            
            result = route(intent_category, intent_name, assistant_mode)
            
            # Should default to escalate
            if result["route"] == "escalate" and result["next_step"] == 6:
                print(f"  ✅ PASSED: Correctly defaulted to escalate/6")
                print(f"     Reason: {result['reason']}")
                passed += 1
            else:
                print(f"  ❌ FAILED: Expected escalate/6, got {result['route']}/{result['next_step']}")
                failed += 1
            print()
        
        print(f"Results: {passed} passed, {failed} failed")
        print()
        return failed == 0
        
    except Exception as e:
        print(f"❌ Error testing invalid category: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_router_class():
    """Test Router class methods."""
    print("=" * 60)
    print("Testing Router Class Methods")
    print("=" * 60)
    print()
    
    try:
        from services.router import Router
        
        router = Router()
        
        tests_passed = 0
        tests_failed = 0
        
        # Test should_escalate
        print("1. Testing should_escalate()...")
        if router.should_escalate("human_only") == True:
            print("   ✅ human_only should escalate: True")
            tests_passed += 1
        else:
            print("   ❌ human_only should escalate: False (expected True)")
            tests_failed += 1
        
        if router.should_escalate("automatable") == False:
            print("   ✅ automatable should escalate: False")
            tests_passed += 1
        else:
            print("   ❌ automatable should escalate: True (expected False)")
            tests_failed += 1
        
        if router.should_escalate("sensitive") == False:
            print("   ✅ sensitive should escalate: False")
            tests_passed += 1
        else:
            print("   ❌ sensitive should escalate: True (expected False)")
            tests_failed += 1
        print()
        
        # Test get_next_step
        print("2. Testing get_next_step()...")
        if router.get_next_step("human_only") == 6:
            print("   ✅ human_only next_step: 6")
            tests_passed += 1
        else:
            print(f"   ❌ human_only next_step: {router.get_next_step('human_only')} (expected 6)")
            tests_failed += 1
        
        if router.get_next_step("automatable") == 3:
            print("   ✅ automatable next_step: 3")
            tests_passed += 1
        else:
            print(f"   ❌ automatable next_step: {router.get_next_step('automatable')} (expected 3)")
            tests_failed += 1
        
        if router.get_next_step("sensitive") == 3:
            print("   ✅ sensitive next_step: 3")
            tests_passed += 1
        else:
            print(f"   ❌ sensitive next_step: {router.get_next_step('sensitive')} (expected 3)")
            tests_failed += 1
        print()
        
        # Test route method
        print("3. Testing Router.route() method...")
        result = router.route("human_only", "financial_advice", "customer")
        if result["route"] == "escalate" and result["next_step"] == 6:
            print("   ✅ Router.route() works correctly")
            tests_passed += 1
        else:
            print(f"   ❌ Router.route() failed: {result}")
            tests_failed += 1
        print()
        
        print(f"Router class tests: {tests_passed} passed, {tests_failed} failed")
        print()
        return tests_failed == 0
        
    except Exception as e:
        print(f"❌ Error testing Router class: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_response_structure():
    """Test that response has correct structure."""
    print("=" * 60)
    print("Testing Response Structure")
    print("=" * 60)
    print()
    
    try:
        from services.router import route
        
        # Test escalate response structure
        result = route("human_only", "financial_advice", "customer")
        
        required_fields_escalate = ["route", "next_step", "skip_to_step", "reason"]
        missing_fields = [field for field in required_fields_escalate if field not in result]
        
        if missing_fields:
            print(f"❌ Missing required fields for escalate: {missing_fields}")
            return False
        
        if result["route"] != "escalate":
            print(f"❌ Route should be 'escalate', got '{result['route']}'")
            return False
        
        if result["next_step"] != 6 or result["skip_to_step"] != 6:
            print(f"❌ Steps should be 6, got next_step={result['next_step']}, skip_to_step={result['skip_to_step']}")
            return False
        
        print("✅ Escalate response structure correct:")
        for field in required_fields_escalate:
            print(f"   - {field}: {result[field]}")
        print()
        
        # Test continue response structure
        result = route("automatable", "fee_inquiry", "customer")
        
        required_fields_continue = ["route", "next_step", "reason"]
        missing_fields = [field for field in required_fields_continue if field not in result]
        
        if missing_fields:
            print(f"❌ Missing required fields for continue: {missing_fields}")
            return False
        
        if result["route"] != "continue":
            print(f"❌ Route should be 'continue', got '{result['route']}'")
            return False
        
        if result["next_step"] != 3:
            print(f"❌ Next step should be 3, got {result['next_step']}")
            return False
        
        print("✅ Continue response structure correct:")
        for field in required_fields_continue:
            print(f"   - {field}: {result[field]}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing response structure: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Testing Router Service (Task 9)")
    print("=" * 60)
    print()
    
    results = []
    
    # Test response structure first (quick check)
    print("Running response structure test...")
    results.append(test_response_structure())
    print()
    
    # Test human_only routing
    print("Running human_only routing tests...")
    results.append(test_route_human_only())
    print()
    
    # Test automatable routing
    print("Running automatable routing tests...")
    results.append(test_route_automatable())
    print()
    
    # Test sensitive routing
    print("Running sensitive routing tests...")
    results.append(test_route_sensitive())
    print()
    
    # Test invalid category handling
    print("Running invalid category handling tests...")
    results.append(test_route_invalid_category())
    print()
    
    # Test Router class
    print("Running Router class tests...")
    results.append(test_router_class())
    print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} test suites passed")
    print("=" * 60)
    
    if passed == total:
        print("✅ All tests passed! The router is ready to use.")
        return 0
    else:
        print("⚠️  Some tests had issues. Please review the output above.")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
