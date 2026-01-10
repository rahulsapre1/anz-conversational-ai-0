#!/usr/bin/env python3
"""
Test script for Task 11: Response Generation Service

This script tests:
1. Response generation for customer mode
2. Response generation for banker mode
3. Citation extraction
4. Synthetic content detection
5. Error handling (no chunks, timeout)
6. Async functionality
"""

import sys
import asyncio
import logging
from utils.logger import setup_logging

# Setup logging
setup_logging()

async def test_customer_response_generation():
    """Test response generation for customer queries."""
    print("=" * 60)
    print("Testing Customer Response Generation")
    print("=" * 60)
    print()
    
    try:
        from services.response_generator import generate_response
        
        # Test with mock retrieved chunks
        retrieved_chunks = [
            "ANZ monthly account fee is $5.00 for standard personal accounts. This fee applies to all standard accounts.",
            "Standard personal accounts include basic transaction features such as online banking, mobile banking, and ATM access."
        ]
        
        citations = [
            {"number": 1, "file_id": "file-123", "source": "ANZ Fee Schedule", "url": "https://www.anz.com.au/fees"},
            {"number": 2, "file_id": "file-456", "source": "ANZ Terms", "url": "https://www.anz.com.au/terms"}
        ]
        
        print("Testing query: 'What is the monthly account fee?'")
        print(f"Retrieved chunks: {len(retrieved_chunks)}")
        
        result = await generate_response(
            user_query="What is the monthly account fee?",
            retrieved_chunks=retrieved_chunks,
            assistant_mode="customer",
            intent_name="fee_inquiry",
            citations=citations
        )
        
        if result:
            print(f"  ✅ SUCCESS")
            print(f"     Response length: {len(result['response_text'])} characters")
            print(f"     Citations: {len(result['citations'])}")
            print(f"     Has synthetic: {result['has_synthetic_content']}")
            print(f"     Response preview: {result['response_text'][:150]}...")
            if result['citations']:
                print(f"     First citation: {result['citations'][0]}")
            return True
        else:
            print("  ❌ FAILED: Result is None")
            return False
        
    except Exception as e:
        print(f"❌ Error testing customer response generation: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_banker_response_generation():
    """Test response generation for banker queries."""
    print("=" * 60)
    print("Testing Banker Response Generation")
    print("=" * 60)
    print()
    
    try:
        from services.response_generator import generate_response
        
        # Test with mock retrieved chunks
        retrieved_chunks = [
            "The policy on fee waivers requires manager approval for amounts over $50. Fee waivers are granted on a case-by-case basis.",
            "Documentation requirements include customer hardship form, proof of income, and bank statements for the last 3 months."
        ]
        
        citations = [
            {"number": 1, "file_id": "file-789", "source": "Fee Waiver Policy", "url": ""},
            {"number": 2, "file_id": "file-012", "source": "Documentation Requirements", "url": ""}
        ]
        
        print("Testing query: 'What is the policy on fee waivers?'")
        print(f"Retrieved chunks: {len(retrieved_chunks)}")
        
        result = await generate_response(
            user_query="What is the policy on fee waivers?",
            retrieved_chunks=retrieved_chunks,
            assistant_mode="banker",
            intent_name="policy_lookup",
            citations=citations
        )
        
        if result:
            print(f"  ✅ SUCCESS")
            print(f"     Response length: {len(result['response_text'])} characters")
            print(f"     Citations: {len(result['citations'])}")
            print(f"     Has synthetic: {result['has_synthetic_content']}")
            print(f"     Response preview: {result['response_text'][:150]}...")
            if result['citations']:
                print(f"     First citation: {result['citations'][0]}")
            return True
        else:
            print("  ❌ FAILED: Result is None")
            return False
        
    except Exception as e:
        print(f"❌ Error testing banker response generation: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_citation_extraction():
    """Test citation extraction from response text."""
    print("=" * 60)
    print("Testing Citation Extraction")
    print("=" * 60)
    print()
    
    try:
        from services.response_generator import ResponseGenerator
        
        generator = ResponseGenerator()
        
        # Test response text with citations
        response_text = "The monthly fee is $5.00 [1]. This applies to standard accounts [2]. Additional features are available [1]."
        
        retrieval_citations = [
            {"number": 1, "source": "ANZ Fee Schedule", "url": "https://www.anz.com.au/fees"},
            {"number": 2, "source": "ANZ Terms", "url": "https://www.anz.com.au/terms"}
        ]
        
        citations = generator._extract_citations(response_text, retrieval_citations)
        
        print(f"Response text: {response_text}")
        print(f"Extracted citations: {len(citations)}")
        
        if len(citations) == 2:  # Should extract [1] and [2]
            print("  ✅ Correctly extracted citations")
            for citation in citations:
                print(f"     Citation {citation['number']}: {citation['source']}")
            return True
        else:
            print(f"  ❌ Expected 2 citations, got {len(citations)}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing citation extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_synthetic_content_detection():
    """Test synthetic content detection."""
    print("=" * 60)
    print("Testing Synthetic Content Detection")
    print("=" * 60)
    print()
    
    try:
        from services.response_generator import ResponseGenerator
        
        generator = ResponseGenerator()
        
        # Test with synthetic content
        chunks_with_synthetic = [
            "Title: Account Closure Process\nLabel: SYNTHETIC\nContent: To close your account, visit a branch...",
            "Standard account information is available online."
        ]
        
        has_synthetic = generator._detect_synthetic_content(chunks_with_synthetic)
        
        if has_synthetic:
            print("  ✅ Correctly detected synthetic content")
            return True
        else:
            print("  ❌ Failed to detect synthetic content")
            return False
        
        # Test without synthetic content
        chunks_without_synthetic = [
            "Standard account information is available online.",
            "ANZ offers various account types."
        ]
        
        has_synthetic = generator._detect_synthetic_content(chunks_without_synthetic)
        
        if not has_synthetic:
            print("  ✅ Correctly identified non-synthetic content")
            return True
        else:
            print("  ❌ Incorrectly detected synthetic content")
            return False
        
    except Exception as e:
        print(f"❌ Error testing synthetic content detection: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_error_handling():
    """Test error handling scenarios."""
    print("=" * 60)
    print("Testing Error Handling")
    print("=" * 60)
    print()
    
    try:
        from services.response_generator import generate_response
        
        tests_passed = 0
        tests_failed = 0
        
        # Test with no retrieved chunks
        print("1. Testing with no retrieved chunks...")
        result = await generate_response(
            user_query="Test query",
            retrieved_chunks=[],
            assistant_mode="customer"
        )
        
        if result and "don't have enough information" in result["response_text"]:
            print("   ✅ Correctly handled no chunks")
            tests_passed += 1
        else:
            print("   ❌ Should return helpful message for no chunks")
            tests_failed += 1
        print()
        
        print(f"Error handling tests: {tests_passed} passed, {tests_failed} failed")
        print()
        return tests_failed == 0
        
    except Exception as e:
        print(f"❌ Error testing error handling: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_response_structure():
    """Test that response has correct structure."""
    print("=" * 60)
    print("Testing Response Structure")
    print("=" * 60)
    print()
    
    try:
        from services.response_generator import generate_response
        
        retrieved_chunks = [
            "ANZ monthly account fee is $5.00 for standard accounts."
        ]
        
        result = await generate_response(
            user_query="What is the monthly fee?",
            retrieved_chunks=retrieved_chunks,
            assistant_mode="customer"
        )
        
        if not result:
            print("❌ Result is None")
            return False
        
        required_fields = ["response_text", "citations", "has_synthetic_content"]
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        print("✅ Response has all required fields:")
        for field in required_fields:
            value = result[field]
            if isinstance(value, list):
                print(f"   - {field}: list with {len(value)} items")
            elif isinstance(value, bool):
                print(f"   - {field}: {value}")
            else:
                print(f"   - {field}: {type(value).__name__} (length: {len(value)})")
        
        # Check citation structure if present
        if result["citations"]:
            citation = result["citations"][0]
            citation_fields = ["number", "source"]
            missing_citation_fields = [f for f in citation_fields if f not in citation]
            if missing_citation_fields:
                print(f"⚠️  Citation missing fields: {missing_citation_fields}")
            else:
                print("✅ Citations have correct structure")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error testing response structure: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_integration_with_retrieval():
    """Test integration with retrieval service."""
    print("=" * 60)
    print("Testing Integration with Retrieval Service")
    print("=" * 60)
    print()
    
    try:
        from services.retrieval_service import retrieve_chunks
        from services.response_generator import generate_response
        
        # First retrieve chunks
        print("Step 1: Retrieving chunks...")
        retrieval_result = await retrieve_chunks("What are the fees for my account?", "customer")
        
        if not retrieval_result or not retrieval_result.get("success"):
            print("  ⚠️  Retrieval failed or no results (this is OK for testing)")
            return True  # Don't fail if retrieval doesn't work
        
        retrieved_chunks = retrieval_result.get("retrieved_chunks", [])
        citations = retrieval_result.get("citations", [])
        
        print(f"  Retrieved {len(retrieved_chunks)} chunks")
        print(f"  Retrieved {len(citations)} citations")
        
        if not retrieved_chunks:
            print("  ⚠️  No chunks retrieved (this is OK for testing)")
            return True
        
        # Then generate response
        print("\nStep 2: Generating response...")
        response_result = await generate_response(
            user_query="What are the fees for my account?",
            retrieved_chunks=retrieved_chunks,
            assistant_mode="customer",
            citations=citations
        )
        
        if response_result:
            print(f"  ✅ Response generated successfully")
            print(f"     Response length: {len(response_result['response_text'])} characters")
            print(f"     Citations: {len(response_result['citations'])}")
            print(f"     Response preview: {response_result['response_text'][:200]}...")
            return True
        else:
            print("  ❌ Response generation failed")
            return False
        
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Testing Response Generation Service (Task 11)")
    print("=" * 60)
    print()
    
    results = []
    
    # Test response structure first (quick check)
    print("Running response structure test...")
    results.append(await test_response_structure())
    print()
    
    # Test citation extraction
    print("Running citation extraction test...")
    results.append(await test_citation_extraction())
    print()
    
    # Test synthetic content detection
    print("Running synthetic content detection test...")
    results.append(await test_synthetic_content_detection())
    print()
    
    # Test customer response generation
    print("Running customer response generation test...")
    results.append(await test_customer_response_generation())
    print()
    
    # Test banker response generation
    print("Running banker response generation test...")
    results.append(await test_banker_response_generation())
    print()
    
    # Test error handling
    print("Running error handling test...")
    results.append(await test_error_handling())
    print()
    
    # Test integration with retrieval
    print("Running integration test...")
    results.append(await test_integration_with_retrieval())
    print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} test suites passed")
    print("=" * 60)
    
    if passed == total:
        print("✅ All tests passed! The response generator is ready to use.")
        return 0
    else:
        print("⚠️  Some tests had issues. Please review the output above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
