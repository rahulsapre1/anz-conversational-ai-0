# Task 6: Vector Store Setup & File Attachment

## Overview
Create OpenAI Vector Stores and attach uploaded files for knowledge base storage and retrieval.

## Prerequisites
- Task 1, 3, 4 completed (Project setup, OpenAI client, knowledge scraping)

## Key Concepts

- **OpenAI Vector Store**: Managed vector store that automatically handles document parsing, chunking, and embedding
- **Files API**: Upload files to OpenAI via Files API
- **Vector Store Attachment**: Attach files to Vector Store (OpenAI processes them automatically)
- **Multiple Vector Stores**: One per topic collection (customer/banker)

## Deliverables

### knowledge/vector_store_setup.py

```python
from openai import OpenAI
from typing import List, Optional, Dict, Any
from config import Config
from database.supabase_client import get_db_client
import logging
import time

logger = logging.getLogger(__name__)

class VectorStoreSetup:
    """Setup and manage OpenAI Vector Stores."""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.db_client = get_db_client()
    
    def create_vector_store(
        self,
        name: str,
        description: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a new Vector Store.
        
        Args:
            name: Name for the Vector Store
            description: Optional description
        
        Returns:
            Vector Store ID if successful, None otherwise
        """
        try:
            vector_store = self.client.beta.vector_stores.create(
                name=name,
                description=description
            )
            logger.info(f"Created Vector Store: {vector_store.id} ({name})")
            return vector_store.id
        except Exception as e:
            logger.error(f"Failed to create Vector Store: {e}")
            return None
    
    def upload_file(
        self,
        file_path: str,
        purpose: str = "assistants"
    ) -> Optional[str]:
        """
        Upload a file to OpenAI Files API.
        
        Args:
            file_path: Path to .txt file to upload (must be UTF-8 encoded)
            purpose: File purpose (default: "assistants")
        
        Returns:
            File ID if successful, None otherwise
        """
        try:
            # Ensure file is .txt format
            if not file_path.endswith('.txt'):
                logger.error(f"File must be .txt format: {file_path}")
                return None
            
            with open(file_path, "rb") as file:
                uploaded_file = self.client.files.create(
                    file=file,
                    purpose=purpose
                )
            logger.info(f"Uploaded file: {uploaded_file.id} ({file_path})")
            return uploaded_file.id
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return None
    
    def attach_files_to_vector_store(
        self,
        vector_store_id: str,
        file_ids: List[str]
    ) -> bool:
        """
        Attach files to a Vector Store.
        
        Args:
            vector_store_id: Vector Store ID
            file_ids: List of file IDs to attach
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create vector store file batch
            batch = self.client.beta.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_ids=file_ids
            )
            
            # Wait for processing (OpenAI processes files asynchronously)
            self._wait_for_file_batch_processing(vector_store_id, batch.id)
            
            logger.info(f"Attached {len(file_ids)} files to Vector Store {vector_store_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to attach files to Vector Store: {e}")
            return False
    
    def _wait_for_file_batch_processing(
        self,
        vector_store_id: str,
        batch_id: str,
        timeout: int = 300
    ):
        """Wait for file batch processing to complete."""
        start_time = time.time()
        while True:
            # Check batch status
            # Note: Actual implementation depends on OpenAI API response
            # This is a placeholder - adjust based on actual API
            
            if time.time() - start_time > timeout:
                logger.warning(f"File batch processing timeout after {timeout} seconds")
                break
            
            time.sleep(5)  # Check every 5 seconds
    
    def setup_customer_vector_store(
        self,
        file_ids: List[str]
    ) -> Optional[str]:
        """
        Create customer Vector Store and attach files.
        
        Args:
            file_ids: List of file IDs for customer content
        
        Returns:
            Vector Store ID if successful, None otherwise
        """
        # Create Vector Store
        vector_store_id = self.create_vector_store(
            name="Customer Knowledge Base",
            description="Vector Store for customer-facing ANZ content"
        )
        
        if not vector_store_id:
            return None
        
        # Attach files
        if file_ids:
            self.attach_files_to_vector_store(vector_store_id, file_ids)
        
        return vector_store_id
    
    def setup_banker_vector_store(
        self,
        file_ids: List[str]
    ) -> Optional[str]:
        """
        Create banker Vector Store and attach files.
        
        Args:
            file_ids: List of file IDs for banker content
        
        Returns:
            Vector Store ID if successful, None otherwise
        """
        # Create Vector Store
        vector_store_id = self.create_vector_store(
            name="Banker Knowledge Base",
            description="Vector Store for banker-facing ANZ content"
        )
        
        if not vector_store_id:
            return None
        
        # Attach files
        if file_ids:
            self.attach_files_to_vector_store(vector_store_id, file_ids)
        
        return vector_store_id
    
    def register_document(
        self,
        openai_file_id: str,
        title: str,
        source_url: Optional[str] = None,
        content_type: str = "public",
        topic_collection: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Register document in Supabase knowledge_documents table.
        
        Args:
            openai_file_id: OpenAI file ID
            title: Document title
            source_url: Optional source URL
            content_type: 'public' or 'synthetic'
            topic_collection: 'customer' or 'banker'
            metadata: Optional additional metadata
        
        Returns:
            Document ID if successful, None otherwise
        """
        doc_data = {
            "openai_file_id": openai_file_id,
            "title": title,
            "source_url": source_url,
            "content_type": content_type,
            "topic_collection": topic_collection,
            "metadata": metadata or {}
        }
        
        return self.db_client.insert_knowledge_document(doc_data)

def setup_vector_stores(
    customer_file_ids: List[str],
    banker_file_ids: List[str]
) -> Dict[str, Optional[str]]:
    """
    Setup both customer and banker Vector Stores.
    
    Args:
        customer_file_ids: List of file IDs for customer content
        banker_file_ids: List of file IDs for banker content
    
    Returns:
        Dictionary with 'customer' and 'banker' Vector Store IDs
    """
    setup = VectorStoreSetup()
    
    customer_vs_id = setup.setup_customer_vector_store(customer_file_ids)
    banker_vs_id = setup.setup_banker_vector_store(banker_file_ids)
    
    return {
        "customer": customer_vs_id,
        "banker": banker_vs_id
    }
```

## Helper Functions

**Note**: These helper functions should be implemented in `knowledge/ingestor.py` (Task 4).

```python
import re
from datetime import datetime
from typing import Dict, Any

def sanitize_filename(title: str, max_length: int = 100) -> str:
    """
    Sanitize page title for use as filename.
    
    Args:
        title: Page title
        max_length: Maximum filename length
    
    Returns:
        Sanitized filename (without extension)
    """
    # Convert to lowercase
    sanitized = title.lower()
    
    # Replace spaces with underscores
    sanitized = sanitized.replace(" ", "_")
    
    # Remove special characters (keep alphanumeric, underscore, hyphen)
    sanitized = re.sub(r'[^a-z0-9_-]', '', sanitized)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # Remove leading/trailing underscores or hyphens
    sanitized = sanitized.strip('_-')
    
    return sanitized if sanitized else "untitled_document"

def format_document_for_upload(
    title: str,
    url: str,
    date: str,
    content: str
) -> str:
    """
    Format extracted webpage content for OpenAI upload.
    
    Args:
        title: Page title
        url: Source URL
        date: Retrieval date (YYYY-MM-DD format)
        content: Extracted text content
    
    Returns:
        Formatted text content with metadata header
    """
    formatted = f"""Title: {title}
Source URL: {url}
Retrieval Date: {date}
Content Type: public

{content}

---
Original URL: {url}
Scraped: {date}
"""
    return formatted
```

## Usage Example

```python
from knowledge.vector_store_setup import setup_vector_stores
from knowledge.ingestor import scrape_and_process_urls, format_document_for_upload, sanitize_filename
from datetime import datetime

# Step 1: Scrape ANZ URLs
urls = load_urls_from_xml("ANZ_web_scrape.xml")
scraped_docs = scrape_and_process_urls(urls)

# Step 2: Process all scraped documents

# Step 3: Upload files to OpenAI
from knowledge.vector_store_setup import VectorStoreSetup
setup = VectorStoreSetup()

customer_file_ids = []
banker_file_ids = []

for doc in scraped_docs:
    # Format doc as .txt file with metadata header including source URL
    formatted_content = format_document_for_upload(
        title=doc["title"],
        url=doc["url"],
        date=doc.get("date", datetime.now().strftime("%Y-%m-%d")),
        content=doc["content"]
    )
    
    # Sanitize title for filename
    sanitized_title = sanitize_filename(doc["title"])
    temp_file = f"{sanitized_title}.txt"
    
    # Save as .txt file (UTF-8 encoding)
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(formatted_content)
    
    # Upload .txt file
    file_id = setup.upload_file(temp_file)
    
    if file_id:
        # Register in database
        setup.register_document(
            openai_file_id=file_id,
            title=doc["title"],
            source_url=doc["url"],
            content_type="public",
            topic_collection=doc.get("topic", "customer")  # Determine based on content
        )
        
        # Add to appropriate list
        if doc.get("topic") == "banker":
            banker_file_ids.append(file_id)
        else:
            customer_file_ids.append(file_id)

# Step 4: Create Vector Stores and attach files
vector_store_ids = setup_vector_stores(
    customer_file_ids=customer_file_ids,
    banker_file_ids=banker_file_ids
)

print(f"Customer Vector Store ID: {vector_store_ids['customer']}")
print(f"Banker Vector Store ID: {vector_store_ids['banker']}")

# Step 5: Add to .env
# OPENAI_VECTOR_STORE_ID_CUSTOMER=vs_...
# OPENAI_VECTOR_STORE_ID_BANKER=vs_...
```

## Setup Instructions

1. **Upload Files**:
   - Use Files API to upload processed documents
   - Files must be in .txt format (plain text, UTF-8 encoding)
   - Each file includes source URL in metadata header
   - File naming: Sanitized page title (e.g., "anz_fee_schedule.txt")
   - OpenAI automatically parses and extracts text from .txt files

2. **Create Vector Stores**:
   - Create one Vector Store for customer content
   - Create one Vector Store for banker content
   - Note the Vector Store IDs

3. **Attach Files**:
   - Attach customer-related files to customer Vector Store
   - Attach banker-related files to banker Vector Store
   - Wait for OpenAI to process files (parsing, chunking, embedding)

4. **Register in Database**:
   - Register each file in Supabase `knowledge_documents` table
   - Track metadata (title, URL, content type, topic collection)

5. **Configure Environment**:
   - Add Vector Store IDs to `.env` file
   - Use IDs in retrieval service

## Validation Checklist

- [ ] Vector Stores created successfully
- [ ] Files uploaded to OpenAI Files API
- [ ] Files attached to appropriate Vector Store
- [ ] Files processed by OpenAI (parsing, chunking, embedding)
- [ ] Documents registered in Supabase knowledge_documents table
- [ ] Vector Store IDs added to .env configuration
- [ ] Can retrieve chunks from Vector Store (test with Task 10)

## Integration Points

- **Task 4**: Knowledge scraping provides documents to upload
- **Task 7**: Synthetic documents also uploaded and attached
- **Task 10**: Retrieval service uses Vector Store IDs

## Notes

- **File Processing**: OpenAI processes files asynchronously. Wait for processing to complete before querying.
- **File Formats**: Use .txt format (plain text, UTF-8 encoding) for webpage content. Each file should include source URL in metadata header.
- **Vector Store Limits**: Be aware of Vector Store size limits (check OpenAI documentation).
- **Batch Processing**: When attaching multiple files, use batch operations for efficiency.

## Common Issues

1. **File upload fails**: Check file format (.txt required), size limits (512MB max, 2M tokens max), API key permissions
2. **Vector Store creation fails**: Check API key has necessary permissions
3. **Files not processing**: Wait longer, ensure files are .txt format with UTF-8 encoding
4. **Vector Store ID not found**: Ensure Vector Store was created and ID is correct

## Success Criteria

✅ Vector Stores created for customer and banker content
✅ Files uploaded and attached to Vector Stores
✅ Files processed by OpenAI (check status)
✅ Documents registered in Supabase
✅ Vector Store IDs configured in .env
✅ Can retrieve chunks using Vector Store IDs (test with retrieval service)
