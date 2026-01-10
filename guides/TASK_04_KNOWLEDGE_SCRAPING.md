# Task 4: Knowledge Base Ingestion - Web Scraping

## Overview
Implement async web scraping infrastructure to collect ANZ public content from URLs listed in `ANZ_web_scrape.xml`. Extract, clean, and format content as `.txt` files ready for OpenAI Vector Store upload.

## Prerequisites
- Task 1 completed (project structure, config, logging)
- Task 3 completed (OpenAI client setup)
- `ANZ_web_scrape.xml` file in project root
- Virtual environment activated

## Deliverables

### 1. Web Scraping Module (knowledge/ingestor.py)

Create `knowledge/ingestor.py` with async web scraping functionality.

**Key Requirements**:
- Async implementation using `aiohttp`
- Concurrent URL fetching with rate limiting
- 30s timeout per URL
- Content extraction using BeautifulSoup
- Format as `.txt` files with metadata header
- Sanitized filenames
- Structured logging

## Implementation

### Step 1: Install Additional Dependencies

Add to `requirements.txt` (if not already present):
```python
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
```

Install:
```bash
pip install aiohttp beautifulsoup4 lxml
```

### Step 2: Create Helper Functions

```python
# knowledge/ingestor.py
import re
import asyncio
import aiohttp
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path

from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


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

### Step 3: Parse ANZ_web_scrape.xml

```python
def load_urls_from_xml(xml_path: str = "ANZ_web_scrape.xml") -> List[str]:
    """
    Load URLs from ANZ_web_scrape.xml file.
    
    Note: The file is actually a text file with URLs, not strict XML.
    Each line that starts with "http" is treated as a URL.
    
    Args:
        xml_path: Path to file containing URLs
    
    Returns:
        List of URLs to scrape
    """
    urls = []
    try:
        with open(xml_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Check if line is a URL
                if line.startswith("http://") or line.startswith("https://"):
                    urls.append(line)
        
        # Remove duplicates and sort
        urls = sorted(list(set(urls)))
        
        logger.info("urls_loaded_from_file", count=len(urls), file=xml_path)
        return urls
    
    except FileNotFoundError:
        logger.error("file_not_found", file=xml_path)
        raise
    except Exception as e:
        logger.error("url_parse_error", error=str(e), file=xml_path)
        raise
```

### Step 4: Async Web Scraping Function

```python
async def fetch_url(
    session: aiohttp.ClientSession,
    url: str,
    timeout: int = 30
) -> Optional[Dict[str, Any]]:
    """
    Fetch a single URL with timeout handling.
    
    Args:
        session: aiohttp session
        url: URL to fetch
        timeout: Timeout in seconds
    
    Returns:
        Dictionary with url, content, status, or None on failure
    """
    start_time = time.time()
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
            if response.status == 200:
                content = await response.text()
                processing_time = (time.time() - start_time) * 1000
                logger.info(
                    "url_fetched",
                    url=url,
                    status=response.status,
                    processing_time_ms=processing_time
                )
                return {
                    "url": url,
                    "content": content,
                    "status": response.status
                }
            else:
                processing_time = (time.time() - start_time) * 1000
                logger.warn(
                    "url_fetch_failed",
                    url=url,
                    status=response.status,
                    processing_time_ms=processing_time
                )
                return None
    
    except asyncio.TimeoutError:
        processing_time = (time.time() - start_time) * 1000
        logger.error(
            "url_fetch_timeout",
            url=url,
            timeout=timeout,
            processing_time_ms=processing_time
        )
        return None
    
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        logger.error(
            "url_fetch_error",
            url=url,
            error=str(e),
            processing_time_ms=processing_time
        )
        return None


def extract_content(html: str, url: str) -> Dict[str, Optional[str]]:
    """
    Extract main content from HTML using BeautifulSoup.
    
    Args:
        html: HTML content
        url: Source URL
    
    Returns:
        Dictionary with title, content, url
    """
    try:
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else "Untitled"
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            element.decompose()
        
        # Try to find main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content|main|article', re.I))
        
        if main_content:
            # Extract text from main content
            content = main_content.get_text(separator='\n', strip=True)
        else:
            # Fallback: extract from body
            body = soup.find('body')
            if body:
                content = body.get_text(separator='\n', strip=True)
            else:
                content = soup.get_text(separator='\n', strip=True)
        
        # Clean up content (remove excessive whitespace)
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        content = '\n'.join(lines)
        
        return {
            "title": title,
            "content": content,
            "url": url
        }
    
    except Exception as e:
        logger.error("content_extraction_error", url=url, error=str(e))
        return {
            "title": "Error Extracting Content",
            "content": None,
            "url": url
        }
```

### Step 5: Main Scraping Function with Rate Limiting

```python
async def scrape_urls(
    urls: List[str],
    max_concurrent: int = 5,
    delay_between_batches: float = 1.0,
    timeout: int = 30
) -> List[Dict[str, Any]]:
    """
    Scrape multiple URLs concurrently with rate limiting.
    
    Args:
        urls: List of URLs to scrape
        max_concurrent: Maximum concurrent requests
        delay_between_batches: Delay between batches (seconds)
        timeout: Timeout per URL (seconds)
    
    Returns:
        List of scraped documents with metadata
    """
    scraped_docs = []
    retrieval_date = datetime.now().strftime("%Y-%m-%d")
    
    # Create semaphore for rate limiting
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_with_semaphore(session: aiohttp.ClientSession, url: str):
        async with semaphore:
            result = await fetch_url(session, url, timeout)
            if result and result.get("content"):
                extracted = extract_content(result["content"], url)
                if extracted.get("content"):
                    return {
                        "title": extracted["title"],
                        "url": extracted["url"],
                        "content": extracted["content"],
                        "retrieval_date": retrieval_date
                    }
            return None
    
    async with aiohttp.ClientSession() as session:
        # Process URLs in batches
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i:i + max_concurrent]
            tasks = [fetch_with_semaphore(session, url) for url in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, dict) and result:
                    scraped_docs.append(result)
                elif isinstance(result, Exception):
                    logger.error("batch_processing_error", error=str(result))
            
            # Rate limiting: delay between batches
            if i + max_concurrent < len(urls):
                await asyncio.sleep(delay_between_batches)
    
    logger.info("scraping_complete", total_urls=len(urls), successful=len(scraped_docs))
    return scraped_docs
```

### Step 6: Save Documents to Files

```python
def save_document(doc: Dict[str, str], output_dir: str = "scraped_docs") -> Optional[str]:
    """
    Save document to .txt file.
    
    Args:
        doc: Document dictionary with title, url, content, retrieval_date
        output_dir: Output directory for files
    
    Returns:
        Path to saved file, or None on failure
    """
    try:
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Sanitize filename
        sanitized_title = sanitize_filename(doc["title"])
        filename = f"{sanitized_title}.txt"
        filepath = Path(output_dir) / filename
        
        # Format document
        formatted_content = format_document_for_upload(
            title=doc["title"],
            url=doc["url"],
            date=doc["retrieval_date"],
            content=doc["content"]
        )
        
        # Save file (UTF-8 encoding)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(formatted_content)
        
        logger.info("document_saved", filename=filename, url=doc["url"])
        return str(filepath)
    
    except Exception as e:
        logger.error("document_save_error", url=doc.get("url"), error=str(e))
        return None


def chunk_large_document(
    doc: Dict[str, str],
    max_chunk_size: int = 500000,  # ~500KB
    output_dir: str = "scraped_docs"
) -> List[str]:
    """
    Split large document into chunks if needed.
    
    Args:
        doc: Document dictionary
        max_chunk_size: Maximum size per chunk (bytes)
        output_dir: Output directory
    
    Returns:
        List of file paths for chunks
    """
    formatted_content = format_document_for_upload(
        title=doc["title"],
        url=doc["url"],
        date=doc["retrieval_date"],
        content=doc["content"]
    )
    
    content_bytes = formatted_content.encode('utf-8')
    
    if len(content_bytes) <= max_chunk_size:
        # No chunking needed
        filepath = save_document(doc, output_dir)
        return [filepath] if filepath else []
    
    # Split into chunks
    sanitized_title = sanitize_filename(doc["title"])
    chunk_paths = []
    
    # Split content into chunks (by lines to avoid breaking words)
    lines = doc["content"].split('\n')
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_bytes = line.encode('utf-8')
        if current_size + len(line_bytes) > max_chunk_size and current_chunk:
            # Save current chunk
            chunk_doc = {
                **doc,
                "content": '\n'.join(current_chunk)
            }
            chunk_num = len(chunk_paths) + 1
            chunk_filename = f"{sanitized_title}_chunk_{chunk_num}.txt"
            chunk_path = Path(output_dir) / chunk_filename
            
            formatted_chunk = format_document_for_upload(
                title=f"{doc['title']} (Part {chunk_num})",
                url=doc["url"],
                date=doc["retrieval_date"],
                content=chunk_doc["content"]
            )
            
            with open(chunk_path, "w", encoding="utf-8") as f:
                f.write(formatted_chunk)
            
            chunk_paths.append(str(chunk_path))
            current_chunk = []
            current_size = 0
        
        current_chunk.append(line)
        current_size += len(line_bytes)
    
    # Save remaining chunk
    if current_chunk:
        chunk_doc = {
            **doc,
            "content": '\n'.join(current_chunk)
        }
        chunk_num = len(chunk_paths) + 1
        chunk_filename = f"{sanitized_title}_chunk_{chunk_num}.txt"
        chunk_path = Path(output_dir) / chunk_filename
        
        formatted_chunk = format_document_for_upload(
            title=f"{doc['title']} (Part {chunk_num})",
            url=doc["url"],
            date=doc["retrieval_date"],
            content=chunk_doc["content"]
        )
        
        with open(chunk_path, "w", encoding="utf-8") as f:
            f.write(formatted_chunk)
        
        chunk_paths.append(str(chunk_path))
    
    logger.info("document_chunked", url=doc["url"], chunks=len(chunk_paths))
    return chunk_paths
```

### Step 7: Main Entry Point

```python
async def scrape_and_process_urls(
    xml_path: str = "ANZ_web_scrape.xml",
    output_dir: str = "scraped_docs",
    max_concurrent: int = 5,
    delay_between_batches: float = 1.0,
    timeout: int = None
) -> List[Dict[str, Any]]:
    """
    Main function to scrape URLs from XML and save as .txt files.
    
    Args:
        xml_path: Path to ANZ_web_scrape.xml
        output_dir: Directory to save scraped files
        max_concurrent: Maximum concurrent requests
        delay_between_batches: Delay between batches (seconds)
        timeout: Timeout per URL (defaults to Config.API_TIMEOUT)
    
    Returns:
        List of document metadata dictionaries
    """
    timeout = timeout or Config.API_TIMEOUT
    
    logger.info("scraping_started", xml_path=xml_path, output_dir=output_dir)
    
    # Load URLs
    urls = load_urls_from_xml(xml_path)
    if not urls:
        logger.error("no_urls_found", xml_path=xml_path)
        return []
    
    # Scrape URLs
    scraped_docs = await scrape_urls(
        urls=urls,
        max_concurrent=max_concurrent,
        delay_between_batches=delay_between_batches,
        timeout=timeout
    )
    
    # Save documents to files
    processed_docs = []
    for doc in scraped_docs:
        # Check if document needs chunking
        content_bytes = doc["content"].encode('utf-8')
        if len(content_bytes) > 500000:  # ~500KB
            filepaths = chunk_large_document(doc, output_dir=output_dir)
        else:
            filepath = save_document(doc, output_dir)
            filepaths = [filepath] if filepath else []
        
        # Add file paths to document metadata
        for filepath in filepaths:
            if filepath:
                processed_docs.append({
                    **doc,
                    "filepath": filepath
                })
    
    logger.info(
        "scraping_complete",
        total_urls=len(urls),
        successful=len(scraped_docs),
        files_created=len(processed_docs)
    )
    
    return processed_docs


# For running as script
if __name__ == "__main__":
    import sys
    
    async def main():
        result = await scrape_and_process_urls()
        print(f"Scraped {len(result)} documents")
        return result
    
    asyncio.run(main())
```

## Usage Example

```python
# In a script or interactive session
import asyncio
from knowledge.ingestor import scrape_and_process_urls

# Run scraping
docs = asyncio.run(scrape_and_process_urls(
    xml_path="ANZ_web_scrape.xml",
    output_dir="scraped_docs",
    max_concurrent=5,
    delay_between_batches=1.0
))

print(f"Scraped {len(docs)} documents")
# Documents are saved in scraped_docs/ directory as .txt files
```

## File Format

Each scraped document is saved as a `.txt` file with this structure:

```
Title: [Page Title]
Source URL: [Original URL]
Retrieval Date: [YYYY-MM-DD]
Content Type: public

[Main content text - cleaned and formatted]

---
Original URL: [URL]
Scraped: [Date]
```

**Example filename**: `anz_fee_schedule.txt`

## Error Handling

- **Timeout**: 30s timeout per URL (configurable via Config.API_TIMEOUT)
- **Rate Limiting**: Semaphore limits concurrent requests (default: 5)
- **Retries**: Not implemented in this task (can be added if needed)
- **Logging**: All errors logged with structured logging (ERROR level)

## Success Criteria

- [ ] Can load URLs from `ANZ_web_scrape.xml`
- [ ] Can scrape ANZ public pages (async with concurrent requests)
- [ ] Extracts clean content (removes nav, footer, ads)
- [ ] Extracts metadata correctly (title, URL, date)
- [ ] Formats content as `.txt` files with proper structure
- [ ] Sanitizes titles for file naming
- [ ] Includes source URL in file metadata header
- [ ] Handles errors gracefully (timeouts, network errors)
- [ ] Timeout handling (30s per URL)
- [ ] Outputs `.txt` files ready for OpenAI upload (UTF-8 encoding)
- [ ] Logs all operations with structured logging (INFO, WARN, ERROR)
- [ ] Respects rate limiting (doesn't overload servers)

## Testing

### Manual Testing

1. **Test URL Loading**:
   ```python
   from knowledge.ingestor import load_urls_from_xml
   urls = load_urls_from_xml()
   print(f"Loaded {len(urls)} URLs")
   ```

2. **Test Single URL Scraping**:
   ```python
   import asyncio
   from knowledge.ingestor import fetch_url, extract_content
   import aiohttp
   
   async def test():
       async with aiohttp.ClientSession() as session:
           result = await fetch_url(session, "https://www.anz.com.au/support/legal/rates-fees-terms/")
           if result:
               extracted = extract_content(result["content"], result["url"])
               print(f"Title: {extracted['title']}")
               print(f"Content length: {len(extracted['content'])}")
   
   asyncio.run(test())
   ```

3. **Test Full Scraping**:
   ```python
   import asyncio
   from knowledge.ingestor import scrape_and_process_urls
   
   docs = asyncio.run(scrape_and_process_urls(max_concurrent=3))
   print(f"Scraped {len(docs)} documents")
   ```

4. **Verify File Format**:
   - Check that files are saved in `scraped_docs/` directory
   - Verify file format matches specification
   - Check that source URL is included in metadata
   - Verify UTF-8 encoding

## Integration Points

- **Task 6 (Vector Store Setup)**: Uses scraped `.txt` files for upload
- **Task 14 (Logging)**: Uses structured logging from `utils/logger.py`
- **Config**: Uses `Config.API_TIMEOUT` for timeout values

## Notes

- **Rate Limiting**: Adjust `max_concurrent` and `delay_between_batches` to respect server limits
- **Robots.txt**: Consider adding robots.txt checking if needed
- **Content Quality**: May need to adjust BeautifulSoup selectors based on ANZ website structure
- **Chunking**: Large documents are automatically chunked (500KB limit)
- **Error Recovery**: Failed URLs are logged but don't stop the process

## Reference

- **DETAILED_PLAN.md** Section 8.1 (Knowledge Ingestion)
- **TASK_BREAKDOWN.md** Task 4
- **BeautifulSoup Documentation**: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **aiohttp Documentation**: https://docs.aiohttp.org/
