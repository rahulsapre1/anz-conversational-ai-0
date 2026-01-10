#!/usr/bin/env python3
"""
Upload Synthetic Documents to Banker Vector Store.
"""
import sys
from pathlib import Path
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from knowledge.vector_store_setup import (
    VectorStoreSetup,
    parse_document_metadata
)
from knowledge.synthetic_generator import format_synthetic_document
from utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def get_synthetic_document_files(directory: str = "synthetic_docs") -> List[str]:
    """
    Get all synthetic .md files from directory.
    
    Args:
        directory: Directory containing synthetic documents
    
    Returns:
        List of file paths
    """
    doc_dir = Path(directory)
    if not doc_dir.exists():
        logger.error("directory_not_found", directory=directory)
        return []
    
    md_files = list(doc_dir.glob("*_synthetic.md"))
    logger.info("synthetic_documents_found", count=len(md_files), directory=directory)
    return [str(f) for f in md_files]


def parse_synthetic_metadata(file_path: str) -> Dict[str, str]:
    """
    Parse metadata from synthetic document file.
    
    Args:
        file_path: Path to synthetic .md file
    
    Returns:
        Dictionary with title, topic, generated_date, source_url
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[:10]  # Read first 10 lines for metadata
        
        metadata = {
            "title": None,
            "topic": None,
            "generated_date": None,
            "source_url": None
        }
        
        for line in lines:
            if line.startswith("Title: "):
                metadata["title"] = line.replace("Title: ", "").strip()
            elif line.startswith("Topic: "):
                metadata["topic"] = line.replace("Topic: ", "").strip()
            elif line.startswith("Generated Date: "):
                metadata["generated_date"] = line.replace("Generated Date: ", "").strip()
        
        # Generate synthetic URL
        if metadata["title"]:
            sanitized = metadata["title"].lower().replace(" ", "_").replace("-", "_")
            metadata["source_url"] = f"synthetic://banker/{sanitized}"
        
        return metadata
    except Exception as e:
        logger.error("metadata_parse_error", file_path=file_path, error=str(e))
        return {
            "title": Path(file_path).stem,
            "topic": "general",
            "generated_date": None,
            "source_url": f"synthetic://banker/{Path(file_path).stem}"
        }


def main():
    """Main function to upload synthetic documents to Banker Vector Store."""
    print("=" * 80)
    print("Upload Synthetic Documents to Banker Vector Store")
    print("=" * 80)
    print()
    
    # Step 1: Get all synthetic document files
    print("Step 1: Loading synthetic documents...")
    file_paths = get_synthetic_document_files("synthetic_docs")
    
    if not file_paths:
        print("❌ No synthetic documents found in synthetic_docs/")
        return
    
    print(f"✓ Found {len(file_paths)} synthetic documents\n")
    
    # Step 2: Get Banker Vector Store ID from config
    from config import Config
    banker_vs_id = Config.OPENAI_VECTOR_STORE_ID_BANKER
    
    if not banker_vs_id:
        print("❌ No Banker Vector Store ID found in .env file")
        print("   Please set OPENAI_VECTOR_STORE_ID_BANKER in your .env file")
        return
    
    print(f"✓ Using Banker Vector Store: {banker_vs_id}\n")
    
    # Step 3: Upload files and register in database
    print("Step 2: Uploading files to OpenAI and registering in database...")
    print("(This may take a few minutes...)\n")
    
    banker_file_ids = []
    setup = VectorStoreSetup()
    
    for i, file_path in enumerate(file_paths, 1):
        # Parse metadata
        metadata = parse_synthetic_metadata(file_path)
        
        print(f"[{i}/{len(file_paths)}] Uploading: {Path(file_path).name}...", end=" ")
        
        # Upload file
        file_id = setup.upload_file(file_path)
        if not file_id:
            print("❌ Failed")
            continue
        
        # Register in database
        doc_id = setup.register_document(
            openai_file_id=file_id,
            title=metadata.get("title") or Path(file_path).stem,
            source_url=metadata.get("source_url"),
            content_type="synthetic",
            topic_collection="banker",
            metadata={
                "filename": Path(file_path).name,
                "topic": metadata.get("topic", "general"),
                "generated_date": metadata.get("generated_date")
            }
        )
        
        if doc_id:
            print(f"✓ Uploaded (ID: {file_id[:20]}...)")
        
        banker_file_ids.append(file_id)
    
    print(f"\n✓ Uploaded {len(banker_file_ids)} synthetic documents\n")
    
    # Step 4: Attach files to Banker Vector Store
    print("Step 3: Attaching files to Banker Vector Store...\n")
    
    if banker_file_ids:
        success = setup.attach_files_to_vector_store(banker_vs_id, banker_file_ids)
        if success:
            print(f"✓ Successfully attached {len(banker_file_ids)} files to Banker Vector Store\n")
        else:
            print("⚠️  Some files may not have been attached. Check logs for details.\n")
    else:
        print("❌ No files to attach\n")
    
    # Step 5: Output results
    print("=" * 80)
    print("UPLOAD COMPLETE")
    print("=" * 80)
    print()
    
    print("Summary:")
    print(f"  - Total files uploaded: {len(banker_file_ids)}")
    print(f"  - Vector Store: {banker_vs_id}")
    print(f"  - Content Type: synthetic")
    print(f"  - Topic Collection: banker")
    print()
    
    if banker_file_ids:
        print("✅ Synthetic documents successfully uploaded to Banker Vector Store!")
        print("   Documents are being processed by OpenAI and will be available shortly.")
    else:
        print("❌ No documents were uploaded. Please check errors above.")


if __name__ == "__main__":
    main()
