import asyncio
import time
import re
from typing import Optional, Dict, Any, List
from utils.openai_client import get_openai_client
from utils.logger import get_logger
from config import Config
from database.supabase_client import get_db_client
from utils.document_lookup import get_url_for_filename

logger = get_logger(__name__)


def _parse_chunk_metadata(chunk: str) -> Dict[str, Optional[str]]:
    """
    Extract metadata (title, source_url) from retrieved chunk text.
    """
    title = None
    source_url = None
    for line in chunk.splitlines():
        stripped = line.strip()
        if stripped.startswith("Title:"):
            title = stripped.replace("Title:", "").strip()
        elif stripped.startswith("Source URL:"):
            source_url = stripped.replace("Source URL:", "").strip()
        elif stripped.startswith("Original URL:") and not source_url:
            source_url = stripped.replace("Original URL:", "").strip()
        if title and source_url:
            break
    return {"title": title, "source_url": source_url}

class RetrievalService:
    """Retrieval service using OpenAI Vector Store + Responses API with file_search tool."""
    
    def __init__(self):
        self.client = get_openai_client()
        self.customer_vector_store_id = Config.OPENAI_VECTOR_STORE_ID_CUSTOMER
        self.banker_vector_store_id = Config.OPENAI_VECTOR_STORE_ID_BANKER
        self.timeout = Config.API_TIMEOUT
    
    async def retrieve(
        self,
        user_query: str,
        assistant_mode: str
    ) -> Dict[str, Any]:
        """
        Retrieve relevant chunks using Responses API with file_search tool (async with timeout).
        
        Args:
            user_query: User query string
            assistant_mode: 'customer' or 'banker'
        
        Returns:
            Dictionary with retrieved_chunks, citations, file_ids, success, error
        """
        start_time = time.time()
        
        # Select appropriate Vector Store ID
        vector_store_id = (
            self.customer_vector_store_id if assistant_mode == "customer"
            else self.banker_vector_store_id
        )
        
        if not vector_store_id:
            processing_time = (time.time() - start_time) * 1000
            logger.error(
                "no_vector_store_configured",
                assistant_mode=assistant_mode,
                processing_time_ms=processing_time
            )
            return {
                "retrieved_chunks": [],
                "citations": [],
                "file_ids": [],
                "success": False,
                "error": f"No Vector Store ID configured for mode: {assistant_mode}",
                "retrieved_chunks_count": 0
            }
        
        try:
            # Use Responses API for vector store retrieval
            # The Responses API is a newer API that combines Chat Completions and Assistants capabilities
            def _retrieve_with_responses_api():
                """Use Responses API with vector store."""
                try:
                    # Use the Responses API endpoint
                    import requests
                    
                    headers = {
                        "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    
                    # Responses API uses different structure: input instead of messages
                    # and supports file_search tool with vector_store_ids
                    payload = {
                        "model": self.client.model,
                        "input": user_query,
                        "tools": [{
                            "type": "file_search",
                            "vector_store_ids": [vector_store_id]
                        }],
                        "temperature": 0.3
                    }
                    
                    # Use Responses API endpoint
                    response = requests.post(
                        "https://api.openai.com/v1/responses",
                        headers=headers,
                        json=payload,
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Responses API returns output as an array with different output types
                        # Find the message output type which contains the text and annotations
                        content = ""
                        annotations = []
                        
                        if "output" in data and isinstance(data["output"], list):
                            for output_item in data["output"]:
                                if output_item.get("type") == "message":
                                    # Extract content from message
                                    message_content = output_item.get("content", [])
                                    for content_block in message_content:
                                        if content_block.get("type") == "output_text":
                                            content = content_block.get("text", "")
                                            
                                            # Extract annotations from content block
                                            if "annotations" in content_block:
                                                for ann in content_block["annotations"]:
                                                    annotations.append({
                                                        "type": ann.get("type", "file_citation"),
                                                        "text": ann.get("text", ""),
                                                        "file_id": ann.get("file_id"),
                                                        "filename": ann.get("filename"),
                                                        "index": ann.get("index"),
                                                        "quote": ann.get("quote", "")
                                                    })
                        
                        return {
                            "content": content,
                            "annotations": annotations,
                            "usage": data.get("usage", {})
                        }
                    else:
                        error_data = response.json() if response.text else {}
                        error_msg = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                        raise Exception(f"API error: {error_msg}")
                        
                except requests.exceptions.RequestException as e:
                    raise Exception(f"Request failed: {str(e)}")
                except Exception as e:
                    raise Exception(f"Retrieval failed: {str(e)}")
            
            # Run synchronous API call in thread pool with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(_retrieve_with_responses_api),
                timeout=self.timeout
            )
            
        except asyncio.TimeoutError:
            processing_time = (time.time() - start_time) * 1000
            logger.error(
                "retrieval_timeout",
                timeout_seconds=self.timeout,
                processing_time_ms=processing_time,
                assistant_mode=assistant_mode,
                user_query_preview=user_query[:50]
            )
            return {
                "retrieved_chunks": [],
                "citations": [],
                "file_ids": [],
                "success": False,
                "error": f"Retrieval timeout after {self.timeout} seconds",
                "retrieved_chunks_count": 0
            }
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(
                "retrieval_error",
                error=str(e),
                error_type=type(e).__name__,
                processing_time_ms=processing_time,
                assistant_mode=assistant_mode,
                user_query_preview=user_query[:50]
            )
            return {
                "retrieved_chunks": [],
                "citations": [],
                "file_ids": [],
                "success": False,
                "error": str(e),
                "retrieved_chunks_count": 0
            }
        
        if not response:
            processing_time = (time.time() - start_time) * 1000
            logger.error(
                "retrieval_api_failed",
                processing_time_ms=processing_time,
                assistant_mode=assistant_mode,
                user_query_preview=user_query[:50]
            )
            return {
                "retrieved_chunks": [],
                "citations": [],
                "file_ids": [],
                "success": False,
                "error": "Chat Completions API call failed for retrieval",
                "retrieved_chunks_count": 0
            }
        
        # Parse response for retrieved content and citations
        content = response.get("content", "")
        annotations = response.get("annotations", [])
        tool_calls = response.get("tool_calls", [])
        
        retrieved_chunks = []
        citations = []
        file_ids = set()
        chunk_metadata_list: List[Dict[str, Optional[str]]] = []
        
        # Extract content as retrieved chunk
        # Split content into chunks if it contains multiple citations/sections
        if content:
            # For now, add entire content as one chunk
            # In future, could split by citations if needed
            retrieved_chunks.append(content)
            chunk_metadata = _parse_chunk_metadata(content)
            if chunk_metadata.get("title") or chunk_metadata.get("source_url"):
                chunk_metadata_list.append(chunk_metadata)
        
        metadata_map: Dict[str, Dict[str, Optional[str]]] = {}
        # Extract citations from annotations (OpenAI's citation format)
        # Track unique file IDs and their citation numbers
        file_id_to_number = {}  # Maps file_id to citation number
        citation_number = 1

        for annotation in annotations:
            file_id = annotation.get("file_id")
            quote = annotation.get("quote", "")
            text = annotation.get("text", "")
            
            if file_id:
                file_ids.add(file_id)
                # Assign citation number to file_id if not seen before
                if file_id not in file_id_to_number:
                    file_id_to_number[file_id] = citation_number
                    citation_number += 1
                
                citation_num = file_id_to_number[file_id]
                
                filename = annotation.get("filename") or annotation.get("name")
                annotation_url = annotation.get("url")
                # Create citation entry (will be enriched with metadata later)
                citation = {
                    "number": citation_num,
                    "file_id": file_id,
                    "quote": quote or text,
                    "source": filename or f"Document {citation_num}",  # Will be enriched with actual title
                    "url": annotation_url or "",  # Will be enriched with actual URL
                    "original_filename": filename
                }
                citations.append(citation)
        
        # Enrich citations with metadata from Supabase
        if file_ids:
            try:
                db_client = get_db_client()
                metadata_map = db_client.get_document_metadata_by_file_ids(list(file_ids))
                
                # Update citations with metadata
                for citation in citations:
                    file_id = citation.get("file_id")
                    if file_id and file_id in metadata_map:
                        metadata = metadata_map[file_id]
                        citation["source"] = metadata.get("title", citation.get("source", "Unknown Document"))
                        citation["url"] = metadata.get("source_url", "")
                        citation["content_type"] = metadata.get("content_type", "public")
                
                logger.info(
                    "citations_enriched",
                    total_citations=len(citations),
                    enriched_count=sum(1 for c in citations if c.get("url"))
                )
            except Exception as e:
                logger.warning(
                    "citation_enrichment_failed",
                    error=str(e),
                    file_ids_count=len(file_ids)
                )
                # Continue with basic citations if enrichment fails

        # If any citation lacks a URL, try matching by filename lookup
        for citation in citations:
            if not citation.get("url"):
                alt_url = get_url_for_filename(citation.get("original_filename"))
                if alt_url:
                    citation["url"] = alt_url

        # Always display the URL as the source when available
        for citation in citations:
            url = citation.get("url")
            if url:
                citation["source"] = url
        
        # If still no citations, fall back to metadata_map or chunk metadata
        if not citations:
            if metadata_map:
                for idx, (file_id, metadata) in enumerate(metadata_map.items(), start=1):
                    citations.append({
                        "number": idx,
                        "file_id": file_id,
                        "quote": "",
                        "source": metadata.get("title", f"Document {idx}"),
                        "url": metadata.get("source_url", ""),
                        "content_type": metadata.get("content_type", "public")
                    })
            elif chunk_metadata_list:
                for idx, meta in enumerate(chunk_metadata_list, start=1):
                    citations.append({
                        "number": idx,
                        "file_id": None,
                        "quote": "",
                        "source": meta.get("title", f"Document {idx}"),
                        "url": meta.get("source_url", ""),
                    })

        # Extract file IDs from tool calls if available
        for tool_call in tool_calls:
            if tool_call.get("type") == "file_search":
                # Try to extract file IDs from function arguments if available
                function = tool_call.get("function", {})
                if function:
                    # Arguments might contain file IDs (depends on API response format)
                    pass
        
        # If no citations from annotations, try to extract from content
        # OpenAI may embed citations in content like [file-xyz] or similar
        if not citations and content:
            # Try to find citation patterns in content
            citation_pattern = r'\[file-([a-zA-Z0-9_-]+)\]'
            matches = re.findall(citation_pattern, content)
            for idx, match in enumerate(matches, 1):
                file_id = f"file-{match}"
                file_ids.add(file_id)
                citations.append({
                    "number": idx,
                    "file_id": file_id,
                    "quote": "",
                    "source": f"Document {idx}",
                    "url": ""
                })
            
            # Try to enrich these citations too
            if file_ids:
                try:
                    db_client = get_db_client()
                    metadata_map = db_client.get_document_metadata_by_file_ids(list(file_ids))
                    for citation in citations:
                        file_id = citation.get("file_id")
                        if file_id and file_id in metadata_map:
                            metadata = metadata_map[file_id]
                            citation["source"] = metadata.get("title", citation.get("source", "Unknown Document"))
                            citation["url"] = metadata.get("source_url", "")
                except Exception as e:
                    logger.warning("citation_enrichment_failed_pattern_match", error=str(e))
        
        # If no content retrieved, check for errors
        if not retrieved_chunks:
            processing_time = (time.time() - start_time) * 1000
            logger.warning(
                "no_chunks_retrieved",
                processing_time_ms=processing_time,
                assistant_mode=assistant_mode,
                user_query_preview=user_query[:50],
                vector_store_id=vector_store_id
            )
            return {
                "retrieved_chunks": [],
                "citations": [],
                "file_ids": list(file_ids),
                "success": False,
                "error": "No results found in Vector Store",
                "retrieved_chunks_count": 0
            }
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(
            "retrieval_completed",
            assistant_mode=assistant_mode,
            retrieved_chunks_count=len(retrieved_chunks),
            citations_count=len(citations),
            file_ids_count=len(file_ids),
            processing_time_ms=processing_time,
            user_query_length=len(user_query),
            user_query_preview=user_query[:50]
        )
        
        return {
            "retrieved_chunks": retrieved_chunks,
            "citations": citations,
            "file_ids": list(file_ids),
            "success": True,
            "retrieved_chunks_count": len(retrieved_chunks),
            "chunk_metadata": chunk_metadata_list
        }

async def retrieve_chunks(
    user_query: str,
    assistant_mode: str
) -> Dict[str, Any]:
    """Convenience function for retrieval."""
    service = RetrievalService()
    return await service.retrieve(user_query, assistant_mode)
