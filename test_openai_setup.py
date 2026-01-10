#!/usr/bin/env python3
"""
Test script for Task 3: OpenAI Client Setup & Intent Taxonomy

This script tests:
1. OpenAI client initialization and connection
2. Intent taxonomy constants
3. Validation functions
"""

import sys
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

def test_openai_client():
    """Test OpenAI client connection."""
    print("=" * 60)
    print("Testing OpenAI Client")
    print("=" * 60)
    print()
    
    try:
        from utils.openai_client import get_openai_client
        
        client = get_openai_client()
        print(f"✅ OpenAI client initialized")
        print(f"   Model: {client.model}")
        print()
        
        # Test simple chat completion
        print("Testing chat completion...")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, OpenAI setup is working!'"}
        ]
        
        response = client.chat_completion(messages, temperature=0.7, max_tokens=50)
        
        if response:
            print("✅ Chat completion successful")
            print(f"   Response: {response['content']}")
            print(f"   Tokens used: {response['usage']['total_tokens']}")
        else:
            print("❌ Chat completion failed")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error testing OpenAI client: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_intent_taxonomy():
    """Test intent taxonomy constants."""
    print("=" * 60)
    print("Testing Intent Taxonomy")
    print("=" * 60)
    print()
    
    try:
        from utils.constants import (
            get_intent_taxonomy,
            get_valid_intents,
            get_intent_category,
            CUSTOMER_INTENTS,
            BANKER_INTENTS
        )
        
        # Test customer intents
        print("Customer Intents:")
        customer_intents = get_intent_taxonomy("customer")
        print(f"   Total: {len(customer_intents)} intents")
        print(f"   Intent names: {list(customer_intents.keys())[:5]}... (showing first 5)")
        print()
        
        # Test banker intents
        print("Banker Intents:")
        banker_intents = get_intent_taxonomy("banker")
        print(f"   Total: {len(banker_intents)} intents")
        print(f"   Intent names: {list(banker_intents.keys())[:5]}... (showing first 5)")
        print()
        
        # Test get_valid_intents
        valid_customer = get_valid_intents("customer")
        valid_banker = get_valid_intents("banker")
        print(f"✅ Valid customer intents: {len(valid_customer)}")
        print(f"✅ Valid banker intents: {len(valid_banker)}")
        print()
        
        # Test get_intent_category
        category = get_intent_category("fee_inquiry", "customer")
        print(f"✅ Intent category for 'fee_inquiry' (customer): {category}")
        
        category = get_intent_category("policy_lookup", "banker")
        print(f"✅ Intent category for 'policy_lookup' (banker): {category}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing intent taxonomy: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validators():
    """Test validation functions."""
    print("=" * 60)
    print("Testing Validators")
    print("=" * 60)
    print()
    
    try:
        from utils.validators import (
            validate_intent_classification,
            validate_confidence_score,
            sanitize_user_query
        )
        
        # Test valid intent classification
        print("Testing valid intent classification...")
        valid_data = {
            "intent_name": "fee_inquiry",
            "intent_category": "automatable",
            "classification_reason": "User asking about standard fees"
        }
        is_valid, error = validate_intent_classification(valid_data, "customer")
        if is_valid:
            print("✅ Valid intent classification passed")
        else:
            print(f"❌ Valid intent classification failed: {error}")
            return False
        print()
        
        # Test invalid intent classification
        print("Testing invalid intent classification...")
        invalid_data = {
            "intent_name": "fee_inquiry",
            "intent_category": "invalid_category",  # Invalid
            "classification_reason": "User asking about standard fees"
        }
        is_valid, error = validate_intent_classification(invalid_data, "customer")
        if not is_valid:
            print(f"✅ Invalid intent classification correctly rejected: {error}")
        else:
            print("❌ Invalid intent classification should have been rejected")
            return False
        print()
        
        # Test confidence score validation
        print("Testing confidence score validation...")
        if validate_confidence_score(0.75):
            print("✅ Valid confidence score (0.75) passed")
        else:
            print("❌ Valid confidence score failed")
            return False
        
        if not validate_confidence_score(1.5):
            print("✅ Invalid confidence score (1.5) correctly rejected")
        else:
            print("❌ Invalid confidence score should have been rejected")
            return False
        print()
        
        # Test query sanitization
        print("Testing query sanitization...")
        sanitized = sanitize_user_query("  Hello, world!  ")
        if sanitized == "Hello, world!":
            print("✅ Query sanitization (trim) works")
        else:
            print(f"❌ Query sanitization failed: '{sanitized}'")
            return False
        
        long_query = "x" * 3000
        sanitized = sanitize_user_query(long_query)
        if len(sanitized) == 2000:
            print("✅ Query sanitization (truncate) works")
        else:
            print(f"❌ Query truncation failed: length {len(sanitized)}")
            return False
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing validators: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print()
    print("=" * 60)
    print("Task 3: OpenAI Setup & Intent Taxonomy - Test Suite")
    print("=" * 60)
    print()
    
    results = []
    
    # Test OpenAI client
    results.append(("OpenAI Client", test_openai_client()))
    print()
    
    # Test intent taxonomy
    results.append(("Intent Taxonomy", test_intent_taxonomy()))
    print()
    
    # Test validators
    results.append(("Validators", test_validators()))
    print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print()
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✅ All tests passed!")
        print("Task 3 setup is complete and working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print()
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
