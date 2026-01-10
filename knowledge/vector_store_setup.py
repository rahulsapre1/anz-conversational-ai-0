"""
Vector Store Setup - Upload files and create OpenAI Vector Stores.
"""
import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from openai import OpenAI

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config import Config
from database.supabase_client import SupabaseClient
from utils.logger import get_logger

logger = get_logger(__name__)


class VectorStoreSetup:
    """Setup and manage OpenAI Vector Stores."""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.db_client = SupabaseClient()
        # #region agent log
        import json
        with open('/Users/rahulsapre/playground/anz-conversational-ai-0/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId": "debug-session", "runId": "init", "hypothesisId": "A", "location": "vector_store_setup.py:26", "message": "Checking beta namespace structure", "data": {"beta_attrs": [x for x in dir(self.client.beta) if not x.startswith('_')], "has_vector_stores": hasattr(self.client.beta, 'vector_stores'), "has_assistants": hasattr(self.client.beta, 'assistants')}, "timestamp": int(time.time() * 1000)}) + '\n')
        # #endregion
        logger.info("VectorStoreSetup initialized")
    
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
        # #region agent log
        import json
        with open('/Users/rahulsapre/playground/anz-conversational-ai-0/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId": "debug-session", "runId": "create-vs", "hypothesisId": "A", "location": "vector_store_setup.py:45", "message": "Before vector store creation", "data": {"name": name, "beta_has_vector_stores": hasattr(self.client.beta, 'vector_stores'), "beta_has_assistants": hasattr(self.client.beta, 'assistants')}, "timestamp": int(time.time() * 1000)}) + '\n')
        # #endregion
        try:
            # #region agent log
            with open('/Users/rahulsapre/playground/anz-conversational-ai-0/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "create-vs", "hypothesisId": "B", "location": "vector_store_setup.py:48", "message": "Attempting vector_stores.create (correct path)", "data": {"attempting_path": "vector_stores.create"}, "timestamp": int(time.time() * 1000)}) + '\n')
            # #endregion
            vector_store = self.client.vector_stores.create(
                name=name,
                description=description or ""
            )
            logger.info(
                "vector_store_created",
                vector_store_id=vector_store.id,
                name=name
            )
            # #region agent log
            with open('/Users/rahulsapre/playground/anz-conversational-ai-0/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "create-vs", "hypothesisId": "A", "location": "vector_store_setup.py:53", "message": "Vector store creation succeeded", "data": {"vector_store_id": vector_store.id}, "timestamp": int(time.time() * 1000)}) + '\n')
            # #endregion
            return vector_store.id
        except AttributeError as e:
            # #region agent log
            assistants_attrs = []
            if hasattr(self.client.beta, 'assistants'):
                assistants_attrs = [x for x in dir(self.client.beta.assistants) if not x.startswith('_')]
            with open('/Users/rahulsapre/playground/anz-conversational-ai-0/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "create-vs", "hypothesisId": "B", "location": "vector_store_setup.py:57", "message": "AttributeError - checking alternative paths", "data": {"error": str(e), "has_assistants": hasattr(self.client.beta, 'assistants'), "assistants_attrs": assistants_attrs, "has_assistants_vector_stores": hasattr(self.client.beta.assistants, 'vector_stores') if hasattr(self.client.beta, 'assistants') else False}, "timestamp": int(time.time() * 1000)}) + '\n')
            # #endregion
            logger.error("vector_store_creation_failed", error=str(e), name=name, error_type="AttributeError")
            return None
        except Exception as e:
            # #region agent log
            with open('/Users/rahulsapre/playground/anz-conversational-ai-0/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "create-vs", "hypothesisId": "C", "location": "vector_store_setup.py:63", "message": "Other exception during vector store creation", "data": {"error": str(e), "error_type": type(e).__name__}, "timestamp": int(time.time() * 1000)}) + '\n')
            # #endregion
            logger.error("vector_store_creation_failed", error=str(e), name=name)
            return None
    
    def upload_file(
        self,
        file_path: str,
        purpose: str = "assistants"
    ) -> Optional[str]:
        """
        Upload a file to OpenAI Files API.
        
        Supports both .txt and .md files (OpenAI accepts text-based files).
        
        Args:
            file_path: Path to file to upload (must be .txt or .md, UTF-8 encoded)
            purpose: File purpose (default: "assistants")
        
        Returns:
            File ID if successful, None otherwise
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error("file_not_found", file_path=file_path)
                return None
            
            # Accept both .txt and .md files
            if not (file_path.endswith('.txt') or file_path.endswith('.md')):
                logger.error(
                    "unsupported_file_format",
                    file_path=file_path,
                    message="File must be .txt or .md format"
                )
                return None
            
            with open(file_path, "rb") as file:
                uploaded_file = self.client.files.create(
                    file=file,
                    purpose=purpose
                )
            
            logger.info(
                "file_uploaded",
                file_id=uploaded_file.id,
                filename=path.name,
                size_bytes=path.stat().st_size
            )
            return uploaded_file.id
        except Exception as e:
            logger.error("file_upload_failed", file_path=file_path, error=str(e))
            return None
    
    def attach_files_to_vector_store(
        self,
        vector_store_id: str,
        file_ids: List[str]
    ) -> bool:
        """
        Attach files to a Vector Store.
        
        Files are attached individually. OpenAI processes them asynchronously.
        
        Args:
            vector_store_id: Vector Store ID
            file_ids: List of file IDs to attach
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not file_ids:
                logger.warning("no_files_to_attach", vector_store_id=vector_store_id)
                return True
            
            total_files = len(file_ids)
            attached_count = 0
            failed_count = 0
            
            logger.info(
                "attaching_files",
                vector_store_id=vector_store_id,
                total_files=total_files
            )
            
            # Attach files individually
            for i, file_id in enumerate(file_ids, 1):
                try:
                    # Attach file to vector store
                    self.client.vector_stores.files.create(
                        vector_store_id=vector_store_id,
                        file_id=file_id
                    )
                    attached_count += 1
                    
                    # Log progress every 10 files
                    if i % 10 == 0 or i == total_files:
                        logger.info(
                            "attachment_progress",
                            vector_store_id=vector_store_id,
                            attached=i,
                            total=total_files
                        )
                    
                    # Small delay to avoid rate limits
                    if i < total_files:
                        time.sleep(0.1)
                        
                except Exception as e:
                    failed_count += 1
                    logger.warning(
                        "file_attachment_failed",
                        vector_store_id=vector_store_id,
                        file_id=file_id,
                        error=str(e)
                    )
            
            logger.info(
                "files_attachment_complete",
                vector_store_id=vector_store_id,
                total_files=total_files,
                attached=attached_count,
                failed=failed_count
            )
            
            # Wait for all files to be processed
            if attached_count > 0:
                logger.info(
                    "waiting_for_file_processing",
                    vector_store_id=vector_store_id,
                    total_files=attached_count
                )
                self._wait_for_vector_store_processing(vector_store_id, attached_count)
            
            return attached_count > 0
            
        except Exception as e:
            logger.error(
                "file_attachment_failed",
                vector_store_id=vector_store_id,
                error=str(e)
            )
            return False
    
    def _wait_for_vector_store_processing(
        self,
        vector_store_id: str,
        expected_file_count: int,
        timeout: int = 600,
        check_interval: int = 10
    ):
        """
        Wait for files in vector store to be processed.
        
        Args:
            vector_store_id: Vector Store ID
            expected_file_count: Expected number of files
            timeout: Maximum wait time in seconds
            check_interval: Seconds between status checks
        """
        start_time = time.time()
        last_completed = -1
        
        logger.info(
            "starting_processing_wait",
            vector_store_id=vector_store_id,
            expected_files=expected_file_count,
            timeout=timeout
        )
        
        while True:
            elapsed = time.time() - start_time
            
            if elapsed > timeout:
                logger.warning(
                    "vector_store_processing_timeout",
                    vector_store_id=vector_store_id,
                    timeout=timeout,
                    expected_files=expected_file_count
                )
                break
            
            try:
                # List all files in vector store
                all_files = []
                has_more = True
                
                # Paginate through all files
                while has_more:
                    response = self.client.vector_stores.files.list(
                        vector_store_id=vector_store_id,
                        limit=100
                    )
                    all_files.extend(response.data)
                    has_more = response.has_more if hasattr(response, 'has_more') else False
                
                file_count = len(all_files)
                
                # Check completion status
                # Files have status: 'in_progress' or 'completed' (or 'failed')
                completed_count = 0
                in_progress_count = 0
                failed_count = 0
                
                for file_obj in all_files:
                    status = getattr(file_obj, 'status', 'unknown')
                    if status == 'completed':
                        completed_count += 1
                    elif status == 'in_progress':
                        in_progress_count += 1
                    elif status == 'failed':
                        failed_count += 1
                
                # Log progress if changed
                if completed_count != last_completed:
                    logger.info(
                        "vector_store_processing_status",
                        vector_store_id=vector_store_id,
                        completed=completed_count,
                        in_progress=in_progress_count,
                        failed=failed_count,
                        total=file_count,
                        elapsed_seconds=int(elapsed)
                    )
                    last_completed = completed_count
                
                # Check if all files are processed
                if completed_count >= expected_file_count:
                    logger.info(
                        "vector_store_processing_complete",
                        vector_store_id=vector_store_id,
                        total_files=file_count,
                        completed_files=completed_count,
                        failed_files=failed_count,
                        elapsed_seconds=int(elapsed)
                    )
                    break
                
            except Exception as e:
                logger.warning(
                    "vector_store_status_check_error",
                    vector_store_id=vector_store_id,
                    error=str(e)
                )
            
            time.sleep(check_interval)
    
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
            description="Vector Store for customer-facing ANZ support content"
        )
        
        if not vector_store_id:
            return None
        
        # Attach files if provided
        if file_ids:
            success = self.attach_files_to_vector_store(vector_store_id, file_ids)
            if not success:
                logger.warning(
                    "file_attachment_failed_but_store_created",
                    vector_store_id=vector_store_id
                )
        
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
        
        # Attach files if provided
        if file_ids:
            success = self.attach_files_to_vector_store(vector_store_id, file_ids)
            if not success:
                logger.warning(
                    "file_attachment_failed_but_store_created",
                    vector_store_id=vector_store_id
                )
        
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
        
        try:
            doc_id = self.db_client.insert_knowledge_document(doc_data)
            if doc_id:
                logger.info(
                    "document_registered",
                    doc_id=doc_id,
                    file_id=openai_file_id,
                    title=title[:50]
                )
            return doc_id
        except Exception as e:
            logger.error(
                "document_registration_failed",
                file_id=openai_file_id,
                error=str(e)
            )
            return None


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


def parse_document_metadata(file_path: str) -> Dict[str, Optional[str]]:
    """
    Parse metadata from scraped document file.
    
    Args:
        file_path: Path to .md file
    
    Returns:
        Dictionary with title, url, retrieval_date
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[:10]  # Read first 10 lines for metadata
        
        metadata = {
            "title": None,
            "url": None,
            "retrieval_date": None
        }
        
        for line in lines:
            if line.startswith("Title: "):
                metadata["title"] = line.replace("Title: ", "").strip()
            elif line.startswith("Source URL: "):
                metadata["url"] = line.replace("Source URL: ", "").strip()
            elif line.startswith("Retrieval Date: "):
                metadata["retrieval_date"] = line.replace("Retrieval Date: ", "").strip()
        
        return metadata
    except Exception as e:
        logger.error("metadata_parse_error", file_path=file_path, error=str(e))
        return {"title": None, "url": None, "retrieval_date": None}


def upload_and_register_documents(
    file_paths: List[str],
    topic_collection: str = "customer"
) -> List[str]:
    """
    Upload files to OpenAI and register in database.
    
    Args:
        file_paths: List of file paths to upload
        topic_collection: 'customer' or 'banker'
    
    Returns:
        List of OpenAI file IDs
    """
    setup = VectorStoreSetup()
    file_ids = []
    
    for file_path in file_paths:
        # Upload file
        file_id = setup.upload_file(file_path)
        if not file_id:
            logger.warning("file_upload_skipped", file_path=file_path)
            continue
        
        # Parse metadata
        metadata = parse_document_metadata(file_path)
        
        # Register in database
        setup.register_document(
            openai_file_id=file_id,
            title=metadata.get("title") or Path(file_path).stem,
            source_url=metadata.get("url"),
            content_type="public",
            topic_collection=topic_collection
        )
        
        file_ids.append(file_id)
    
    logger.info(
        "upload_and_register_complete",
        total_files=len(file_paths),
        successful=len(file_ids),
        topic_collection=topic_collection
    )
    
    return file_ids
