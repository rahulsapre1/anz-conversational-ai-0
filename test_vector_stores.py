#!/usr/bin/env python3
"""
Test Vector Store Setup - Verify files uploaded and vector stores accessible.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config import Config
from openai import OpenAI
from database.supabase_client import SupabaseClient
from utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def test_vector_store_accessibility():
    """Test if vector stores exist and are accessible."""
    print("=" * 80)
    print("Vector Store Accessibility Test")
    print("=" * 80)
    print()
    
    client = OpenAI(api_key=Config.OPENAI_API_KEY)
    db_client = SupabaseClient()
    
    # Get vector store IDs from config
    customer_vs_id = Config.OPENAI_VECTOR_STORE_ID_CUSTOMER
    banker_vs_id = Config.OPENAI_VECTOR_STORE_ID_BANKER
    
    if not customer_vs_id and not banker_vs_id:
        print("❌ No Vector Store IDs found in .env file")
        return False
    
    results = {
        "customer": {"exists": False, "files": 0, "completed": 0, "in_progress": 0, "failed": 0},
        "banker": {"exists": False, "files": 0, "completed": 0, "in_progress": 0, "failed": 0}
    }
    
    # Test Customer Vector Store
    if customer_vs_id:
        print(f"📊 Testing Customer Vector Store: {customer_vs_id}")
        print("-" * 80)
        
        try:
            # Retrieve vector store info
            vs = client.vector_stores.retrieve(customer_vs_id)
            results["customer"]["exists"] = True
            print(f"✓ Vector Store exists")
            print(f"  Name: {vs.name}")
            print(f"  Status: {getattr(vs, 'status', 'N/A')}")
            print(f"  Created: {getattr(vs, 'created_at', 'N/A')}")
            
            # List files
            all_files = []
            has_more = True
            while has_more:
                response = client.vector_stores.files.list(
                    vector_store_id=customer_vs_id,
                    limit=100
                )
                all_files.extend(response.data)
                has_more = response.has_more if hasattr(response, 'has_more') else False
            
            results["customer"]["files"] = len(all_files)
            print(f"\n📁 Files in Vector Store: {len(all_files)}")
            
            # Check file statuses
            for file_obj in all_files:
                status = getattr(file_obj, 'status', 'unknown')
                if status == 'completed':
                    results["customer"]["completed"] += 1
                elif status == 'in_progress':
                    results["customer"]["in_progress"] += 1
                elif status == 'failed':
                    results["customer"]["failed"] += 1
            
            print(f"  ✓ Completed: {results['customer']['completed']}")
            print(f"  ⏳ In Progress: {results['customer']['in_progress']}")
            if results["customer"]["failed"] > 0:
                print(f"  ❌ Failed: {results['customer']['failed']}")
            
            # Show sample files (first 5)
            if all_files:
                print(f"\n📄 Sample files (first 5):")
                for i, file_obj in enumerate(all_files[:5], 1):
                    file_id = getattr(file_obj, 'id', 'unknown')
                    status = getattr(file_obj, 'status', 'unknown')
                    created_at = getattr(file_obj, 'created_at', 'N/A')
                    print(f"  {i}. {file_id[:30]}... [{status}]")
            
        except Exception as e:
            print(f"❌ Error accessing Customer Vector Store: {e}")
            results["customer"]["exists"] = False
        
        print()
    
    # Test Banker Vector Store
    if banker_vs_id:
        print(f"📊 Testing Banker Vector Store: {banker_vs_id}")
        print("-" * 80)
        
        try:
            # Retrieve vector store info
            vs = client.vector_stores.retrieve(banker_vs_id)
            results["banker"]["exists"] = True
            print(f"✓ Vector Store exists")
            print(f"  Name: {vs.name}")
            print(f"  Status: {getattr(vs, 'status', 'N/A')}")
            print(f"  Created: {getattr(vs, 'created_at', 'N/A')}")
            
            # List files
            all_files = []
            has_more = True
            while has_more:
                response = client.vector_stores.files.list(
                    vector_store_id=banker_vs_id,
                    limit=100
                )
                all_files.extend(response.data)
                has_more = response.has_more if hasattr(response, 'has_more') else False
            
            results["banker"]["files"] = len(all_files)
            print(f"\n📁 Files in Vector Store: {len(all_files)}")
            
            # Check file statuses
            for file_obj in all_files:
                status = getattr(file_obj, 'status', 'unknown')
                if status == 'completed':
                    results["banker"]["completed"] += 1
                elif status == 'in_progress':
                    results["banker"]["in_progress"] += 1
                elif status == 'failed':
                    results["banker"]["failed"] += 1
            
            print(f"  ✓ Completed: {results['banker']['completed']}")
            print(f"  ⏳ In Progress: {results['banker']['in_progress']}")
            if results["banker"]["failed"] > 0:
                print(f"  ❌ Failed: {results['banker']['failed']}")
            
            # Show sample files (first 5)
            if all_files:
                print(f"\n📄 Sample files (first 5):")
                for i, file_obj in enumerate(all_files[:5], 1):
                    file_id = getattr(file_obj, 'id', 'unknown')
                    status = getattr(file_obj, 'status', 'unknown')
                    created_at = getattr(file_obj, 'created_at', 'N/A')
                    print(f"  {i}. {file_id[:30]}... [{status}]")
                    
        except Exception as e:
            print(f"❌ Error accessing Banker Vector Store: {e}")
            results["banker"]["exists"] = False
        
        print()
    
    # Test Database Records
    print("📊 Testing Database Records")
    print("-" * 80)
    
    try:
        # Query knowledge_documents table
        customer_docs = db_client.client.table("knowledge_documents").select(
            "id, openai_file_id, title, topic_collection"
        ).eq("topic_collection", "customer").execute()
        
        banker_docs = db_client.client.table("knowledge_documents").select(
            "id, openai_file_id, title, topic_collection"
        ).eq("topic_collection", "banker").execute()
        
        print(f"✓ Customer documents in DB: {len(customer_docs.data)}")
        print(f"✓ Banker documents in DB: {len(banker_docs.data)}")
        
        if customer_docs.data:
            print(f"\n📄 Sample customer documents (first 3):")
            for i, doc in enumerate(customer_docs.data[:3], 1):
                print(f"  {i}. {doc.get('title', 'N/A')[:60]}...")
                print(f"     File ID: {doc.get('openai_file_id', 'N/A')[:30]}...")
        
    except Exception as e:
        print(f"❌ Error querying database: {e}")
    
    print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if customer_vs_id:
        print(f"\nCustomer Vector Store:")
        print(f"  Exists: {'✓' if results['customer']['exists'] else '❌'}")
        print(f"  Total Files: {results['customer']['files']}")
        print(f"  Completed: {results['customer']['completed']}")
        print(f"  In Progress: {results['customer']['in_progress']}")
        if results['customer']['failed'] > 0:
            print(f"  Failed: {results['customer']['failed']} ⚠️")
    
    if banker_vs_id:
        print(f"\nBanker Vector Store:")
        print(f"  Exists: {'✓' if results['banker']['exists'] else '❌'}")
        print(f"  Total Files: {results['banker']['files']}")
        print(f"  Completed: {results['banker']['completed']}")
        print(f"  In Progress: {results['banker']['in_progress']}")
        if results['banker']['failed'] > 0:
            print(f"  Failed: {results['banker']['failed']} ⚠️")
    
    # Overall status
    all_good = (
        (not customer_vs_id or results['customer']['exists']) and
        (not banker_vs_id or results['banker']['exists']) and
        results['customer']['completed'] > 0
    )
    
    print()
    if all_good:
        print("✅ All tests passed! Vector stores are accessible and files are uploaded.")
    else:
        print("⚠️  Some tests failed. Check the details above.")
    
    return all_good


def test_vector_store_search():
    """Test a simple search/retrieval query."""
    print("\n" + "=" * 80)
    print("Vector Store Search Test")
    print("=" * 80)
    print()
    
    client = OpenAI(api_key=Config.OPENAI_API_KEY)
    customer_vs_id = Config.OPENAI_VECTOR_STORE_ID_CUSTOMER
    
    if not customer_vs_id:
        print("⚠️  No Customer Vector Store ID found. Skipping search test.")
        return
    
    try:
        print(f"Testing search on Customer Vector Store: {customer_vs_id}")
        print("-" * 80)
        
        # Simple search query
        query = "How do I report a scam?"
        print(f"Query: '{query}'")
        print()
        
        # Note: Direct search API might not be available in all SDK versions
        # This is a placeholder - actual retrieval will be tested in Task 10
        print("ℹ️  Direct search functionality will be tested in Task 10 (Retrieval Service)")
        print("   Vector Store is ready for retrieval operations.")
        
    except Exception as e:
        print(f"❌ Error testing search: {e}")


if __name__ == "__main__":
    success = test_vector_store_accessibility()
    test_vector_store_search()
    
    sys.exit(0 if success else 1)
