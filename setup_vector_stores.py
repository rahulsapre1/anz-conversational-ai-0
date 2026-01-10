#!/usr/bin/env python3
"""
Setup Vector Stores: Upload all scraped documents and create vector stores.
"""
import sys
import asyncio
from pathlib import Path
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from knowledge.vector_store_setup import (
    VectorStoreSetup,
    upload_and_register_documents,
    parse_document_metadata
)
from utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def get_all_document_files(directory: str = "scraped_docs") -> List[str]:
    """
    Get all .md files from directory.
    
    Args:
        directory: Directory containing documents
    
    Returns:
        List of file paths
    """
    doc_dir = Path(directory)
    if not doc_dir.exists():
        logger.error("directory_not_found", directory=directory)
        return []
    
    md_files = list(doc_dir.glob("*.md"))
    logger.info("documents_found", count=len(md_files), directory=directory)
    return [str(f) for f in md_files]


def determine_topic_collection(file_path: str) -> str:
    """
    Determine if document belongs to 'customer' or 'banker' collection.
    
    For now, all scraped content is customer-facing, but this can be enhanced
    to analyze content or use metadata.
    
    Args:
        file_path: Path to document file
    
    Returns:
        'customer' or 'banker'
    """
    # For Task 6, all scraped content is customer-facing
    # Banker content would come from synthetic generation (Task 7)
    return "customer"


def main():
    """Main function to setup vector stores."""
    print("=" * 80)
    print("Vector Store Setup")
    print("=" * 80)
    print()
    
    # Step 1: Get all document files
    print("Step 1: Loading documents...")
    file_paths = get_all_document_files("scraped_docs")
    
    if not file_paths:
        print("❌ No documents found in scraped_docs/")
        return
    
    print(f"✓ Found {len(file_paths)} documents\n")
    
    # Step 2: Upload files and register in database
    print("Step 2: Uploading files to OpenAI and registering in database...")
    print("(This may take a few minutes for all files...)\n")
    
    customer_file_ids = []
    banker_file_ids = []
    
    setup = VectorStoreSetup()
    
    for i, file_path in enumerate(file_paths, 1):
        # Determine topic collection
        topic = determine_topic_collection(file_path)
        
        print(f"[{i}/{len(file_paths)}] Uploading: {Path(file_path).name}...", end=" ")
        
        # Upload file
        file_id = setup.upload_file(file_path)
        if not file_id:
            print("❌ Failed")
            continue
        
        # Parse metadata
        metadata = parse_document_metadata(file_path)
        
        # Register in database
        doc_id = setup.register_document(
            openai_file_id=file_id,
            title=metadata.get("title") or Path(file_path).stem,
            source_url=metadata.get("url"),
            content_type="public",
            topic_collection=topic,
            metadata={"filename": Path(file_path).name}
        )
        
        if doc_id:
            print(f"✓ Uploaded (ID: {file_id[:20]}...)")
        
        # Add to appropriate list
        if topic == "banker":
            banker_file_ids.append(file_id)
        else:
            customer_file_ids.append(file_id)
    
    print(f"\n✓ Uploaded {len(customer_file_ids)} customer documents")
    print(f"✓ Uploaded {len(banker_file_ids)} banker documents\n")
    
    # Step 3: Create Vector Stores
    print("Step 3: Creating Vector Stores...\n")
    
    customer_vs_id = None
    banker_vs_id = None
    
    if customer_file_ids:
        print("Creating Customer Vector Store...")
        customer_vs_id = setup.setup_customer_vector_store(customer_file_ids)
        if customer_vs_id:
            print(f"✓ Customer Vector Store created: {customer_vs_id}\n")
        else:
            print("❌ Failed to create Customer Vector Store\n")
    
    if banker_file_ids:
        print("Creating Banker Vector Store...")
        banker_vs_id = setup.setup_banker_vector_store(banker_file_ids)
        if banker_vs_id:
            print(f"✓ Banker Vector Store created: {banker_vs_id}\n")
        else:
            print("❌ Failed to create Banker Vector Store\n")
    
    # Step 4: Output results
    print("=" * 80)
    print("SETUP COMPLETE")
    print("=" * 80)
    print()
    
    if customer_vs_id:
        print(f"Customer Vector Store ID: {customer_vs_id}")
        print(f"  → Add to .env: OPENAI_VECTOR_STORE_ID_CUSTOMER={customer_vs_id}\n")
    
    if banker_vs_id:
        print(f"Banker Vector Store ID: {banker_vs_id}")
        print(f"  → Add to .env: OPENAI_VECTOR_STORE_ID_BANKER={banker_vs_id}\n")
    
    print("Summary:")
    print(f"  - Total files uploaded: {len(customer_file_ids) + len(banker_file_ids)}")
    print(f"  - Customer documents: {len(customer_file_ids)}")
    print(f"  - Banker documents: {len(banker_file_ids)}")
    print(f"  - Vector Stores created: {sum(1 for x in [customer_vs_id, banker_vs_id] if x)}")
    print()
    
    if customer_vs_id or banker_vs_id:
        print("⚠️  IMPORTANT: Add Vector Store IDs to your .env file:")
        print("=" * 80)
        if customer_vs_id:
            print(f"OPENAI_VECTOR_STORE_ID_CUSTOMER={customer_vs_id}")
        if banker_vs_id:
            print(f"OPENAI_VECTOR_STORE_ID_BANKER={banker_vs_id}")
        print("=" * 80)


if __name__ == "__main__":
    main()
