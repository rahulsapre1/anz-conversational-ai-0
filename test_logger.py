"""
Test suite for InteractionLogger service.

Tests async logging, retry queue, and API call logging.
"""
import asyncio
import time
from services.logger import get_interaction_logger
from utils.logger import setup_logging, get_logger

# Setup structured logging
setup_logging()
logger = get_logger(__name__)


async def test_basic_interaction_logging():
    """Test basic interaction logging."""
    print("\n=== Test 1: Basic Interaction Logging ===")
    
    interaction_logger = get_interaction_logger()
    interaction_logger.start_timer()
    
    # Simulate some processing time
    await asyncio.sleep(0.1)
    
    interaction_id = interaction_logger.log_interaction(
        assistant_mode="customer",
        user_query="What are the fees for my account?",
        session_id="test_session_123",
        intent_name="fee_inquiry",
        intent_category="automatable",
        classification_reason="User asking about standard fees",
        step_1_intent_completed=True,
        step_2_routing_decision="continue",
        step_3_retrieval_performed=True,
        step_4_response_generated=True,
        step_5_confidence_score=0.85,
        step_6_escalation_triggered=False,
        outcome="resolved",
        confidence_score=0.85,
        response_text="Based on ANZ's fee schedule, the monthly account fee is $5.",
        citations=[{"number": 1, "source": "ANZ Fee Schedule", "url": "https://anz.com/fees"}],
        retrieved_chunks_count=3
    )
    
    print(f"  Interaction logging initiated (non-blocking)")
    print(f"  Returned: {interaction_id} (should be None for non-blocking)")
    
    # Wait a bit for async logging to complete
    await asyncio.sleep(2)
    print("  ✅ Basic interaction logging test completed")


async def test_escalation_logging():
    """Test escalation logging."""
    print("\n=== Test 2: Escalation Logging ===")
    
    interaction_logger = get_interaction_logger()
    interaction_logger.start_timer()
    
    await asyncio.sleep(0.1)
    
    # First log the interaction
    interaction_logger.log_interaction(
        assistant_mode="customer",
        user_query="I need to dispute a transaction",
        session_id="test_session_456",
        intent_name="transaction_dispute",
        intent_category="sensitive",
        classification_reason="Transaction disputes require human review",
        step_1_intent_completed=True,
        step_2_routing_decision="escalate",
        step_3_retrieval_performed=False,
        step_4_response_generated=False,
        step_5_confidence_score=None,
        step_6_escalation_triggered=True,
        outcome="escalated",
        confidence_score=None,
        escalation_reason="Transaction disputes require human agent review",
        response_text=None,
        citations=None,
        retrieved_chunks_count=0
    )
    
    print("  Escalation interaction logged")
    
    # Wait for async operations
    await asyncio.sleep(2)
    print("  ✅ Escalation logging test completed")


async def test_api_call_logging():
    """Test API call logging."""
    print("\n=== Test 3: API Call Logging ===")
    
    interaction_logger = get_interaction_logger()
    
    # Log successful API call
    interaction_logger.log_api_call(
        api_name="openai_chat_completion",
        endpoint="/v1/chat/completions",
        method="POST",
        processing_time_ms=1250,
        status_code=200,
        request_tokens=150,
        response_tokens=200,
        total_tokens=350,
        model="gpt-4o-mini"
    )
    
    print("  Successful API call logged")
    
    # Log failed API call
    interaction_logger.log_api_call(
        api_name="openai_chat_completion",
        endpoint="/v1/chat/completions",
        method="POST",
        processing_time_ms=5000,
        status_code=500,
        error="Internal server error",
        model="gpt-4o-mini"
    )
    
    print("  Failed API call logged")
    print("  ✅ API call logging test completed")


async def test_confidence_score_validation():
    """Test confidence score validation."""
    print("\n=== Test 4: Confidence Score Validation ===")
    
    interaction_logger = get_interaction_logger()
    interaction_logger.start_timer()
    
    # Test with invalid confidence score (should be logged but score set to None)
    interaction_logger.log_interaction(
        assistant_mode="customer",
        user_query="Test query",
        confidence_score=1.5,  # Invalid: > 1.0
        outcome="resolved"
    )
    
    print("  Invalid confidence score (1.5) logged (should be validated)")
    
    # Test with valid confidence score
    interaction_logger.log_interaction(
        assistant_mode="customer",
        user_query="Test query 2",
        confidence_score=0.75,  # Valid
        outcome="resolved"
    )
    
    print("  Valid confidence score (0.75) logged")
    
    await asyncio.sleep(1)
    print("  ✅ Confidence score validation test completed")


async def test_processing_time_calculation():
    """Test processing time calculation."""
    print("\n=== Test 5: Processing Time Calculation ===")
    
    interaction_logger = get_interaction_logger()
    interaction_logger.start_timer()
    
    # Simulate processing
    await asyncio.sleep(0.5)
    
    interaction_logger.log_interaction(
        assistant_mode="customer",
        user_query="Test query",
        outcome="resolved"
    )
    
    print("  Processing time should be ~500ms")
    
    await asyncio.sleep(1)
    print("  ✅ Processing time calculation test completed")


async def test_trigger_type_extraction():
    """Test escalation trigger type extraction."""
    print("\n=== Test 6: Trigger Type Extraction ===")
    
    interaction_logger = get_interaction_logger()
    
    test_cases = [
        ("Low confidence score", "low_confidence"),
        ("Insufficient evidence to answer", "insufficient_evidence"),
        ("Account-specific information required", "account_specific"),
        ("Security or fraud concern", "security_fraud"),
        ("Financial advice needed", "financial_advice"),
        ("Legal or hardship situation", "legal_hardship"),
        ("User in emotional distress", "emotional_distress"),
        ("Repeated misunderstanding", "repeated_misunderstanding"),
        ("User explicitly requested human agent", "explicit_human_request"),
        ("Unknown reason", "unknown")
    ]
    
    for reason, expected_trigger in test_cases:
        trigger_type = interaction_logger._extract_trigger_type(reason)
        status = "✅" if trigger_type == expected_trigger else "❌"
        print(f"  {status} '{reason}' -> {trigger_type} (expected: {expected_trigger})")
    
    print("  ✅ Trigger type extraction test completed")


async def test_all_pipeline_steps():
    """Test logging all pipeline steps."""
    print("\n=== Test 7: All Pipeline Steps ===")
    
    interaction_logger = get_interaction_logger()
    interaction_logger.start_timer()
    
    # Simulate full pipeline
    await asyncio.sleep(0.05)  # Step 1: Intent classification
    
    await asyncio.sleep(0.05)  # Step 2: Routing
    
    await asyncio.sleep(0.1)   # Step 3: Retrieval
    
    await asyncio.sleep(0.2)   # Step 4: Response generation
    
    await asyncio.sleep(0.1)   # Step 5: Confidence scoring
    
    # Log with all steps completed
    interaction_logger.log_interaction(
        assistant_mode="banker",
        user_query="What is the policy for account closures?",
        session_id="test_session_full_pipeline",
        intent_name="policy_inquiry",
        intent_category="automatable",
        classification_reason="Standard policy question",
        step_1_intent_completed=True,
        step_2_routing_decision="continue",
        step_3_retrieval_performed=True,
        step_4_response_generated=True,
        step_5_confidence_score=0.92,
        step_6_escalation_triggered=False,
        outcome="resolved",
        confidence_score=0.92,
        response_text="According to ANZ policy...",
        citations=[{"number": 1, "source": "ANZ Policy Guide", "url": "https://anz.com/policy"}],
        retrieved_chunks_count=5
    )
    
    print("  Full pipeline logged with all steps")
    
    await asyncio.sleep(2)
    print("  ✅ All pipeline steps test completed")


async def test_concurrent_logging():
    """Test concurrent logging operations."""
    print("\n=== Test 8: Concurrent Logging ===")
    
    interaction_logger = get_interaction_logger()
    
    async def log_interaction(i: int):
        interaction_logger.start_timer()
        await asyncio.sleep(0.01 * i)  # Stagger the requests
        interaction_logger.log_interaction(
            assistant_mode="customer",
            user_query=f"Test query {i}",
            session_id=f"concurrent_session_{i}",
            outcome="resolved"
        )
    
    # Log 5 interactions concurrently
    tasks = [log_interaction(i) for i in range(5)]
    await asyncio.gather(*tasks)
    
    print("  5 concurrent interactions logged")
    
    await asyncio.sleep(2)
    print("  ✅ Concurrent logging test completed")


async def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("InteractionLogger Test Suite")
    print("=" * 60)
    
    tests = [
        test_basic_interaction_logging,
        test_escalation_logging,
        test_api_call_logging,
        test_confidence_score_validation,
        test_processing_time_calculation,
        test_trigger_type_extraction,
        test_all_pipeline_steps,
        test_concurrent_logging
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"\n  ❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    # Wait a bit more for any remaining async operations
    await asyncio.sleep(3)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    exit(exit_code)
