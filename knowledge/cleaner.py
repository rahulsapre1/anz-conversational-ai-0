"""
Optional LLM-based content cleaner for scraped knowledge base documents.
Cleans and structures content to improve vector search quality.
"""
import sys
import asyncio
from typing import Dict, Optional
from pathlib import Path

# Add project root to Python path (for running as script)
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.openai_client import get_openai_client
from utils.logger import get_logger

logger = get_logger(__name__)


CLEANING_PROMPT = """You are reorganizing scraped ANZ Bank support documentation. This is REORGANIZATION ONLY, not summarization or condensing.

STRICT INSTRUCTIONS - FOLLOW EXACTLY:

1. DELETE THESE LINES ONLY (complete line matches):
   - Lines that are ONLY "Find ANZ"
   - Lines that are ONLY "Support Centre"
   - Lines that are ONLY "Jump to"
   - Lines that are ONLY "Top"
   - Lines that are ONLY "Branch locator"
   - Lines that are ONLY "Quick links"
   - Lines that are ONLY "Calculators and tools"
   - Lines containing ONLY "Click to play video"
   - Lines containing ONLY "Video transcript"
   - Lines that are ONLY video duration like "00:53" or "1:47"

2. REMOVE these phrases from lines (but keep the rest of the line):
   - Remove "Click to play video" phrase
   - Remove "Video transcript" phrase
   - Remove unicode arrow symbols like ► or ▲ (but keep the text around them)

3. COPY EVERYTHING ELSE VERBATIM:
   - Copy every phone number exactly as written
   - Copy every email address exactly as written
   - Copy every step-by-step instruction word-for-word
   - Copy every section heading and ALL its content
   - Copy Android instructions exactly (keep them separate)
   - Copy iPhone instructions exactly (keep them separate)
   - Copy all numbered steps (01., 02., etc.)
   - Copy all bullet points
   - Copy all contact information
   - Copy all scenarios and conditions
   - Copy all warnings and notices

4. ORGANIZE (reorganize, don't rewrite):
   - Group similar content under clear markdown headers (##, ###)
   - Maintain original wording - DO NOT paraphrase
   - Keep original formatting (numbered lists, bullets)
   - Preserve all original details

EXAMPLE OF WHAT TO DO:
Original: "Find ANZ\nSupport Centre\nReport a scam\n\nANZ Cards: 13 22 73\nInternet Banking: 13 33 50"
Output: "## Contact Information\n\nANZ Cards: 13 22 73\nInternet Banking: 13 33 50"

DO NOT:
- Do NOT combine multiple phone numbers into one
- Do NOT remove any phone numbers or contact details
- Do NOT summarize procedures
- Do NOT remove step-by-step instructions
- Do NOT generalize platform-specific instructions
- Do NOT add your own words or explanations
- Do NOT remove duplicate information if it's in different sections

OUTPUT REQUIREMENT:
The output must contain EVERY piece of factual information from the input. If you're unsure whether to include something, INCLUDE IT. Better to have too much detail than too little."""


def clean_content_with_llm(
    content: str,
    title: str,
    url: str,
    model: str = "gpt-4o"
) -> Optional[str]:
    """
    Clean and structure content using LLM.
    
    Args:
        content: Raw scraped content
        title: Page title
        url: Source URL
        model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)
    
    Returns:
        Cleaned content or None on failure
    """
    try:
        client = get_openai_client()
        
        # Use a more specific prompt with context
        system_prompt = CLEANING_PROMPT
        user_prompt = f"""Clean and structure this ANZ support page content:

Title: {title}
URL: {url}

Content to clean:
{content}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = client.chat_completion(
            messages=messages,
            temperature=0.3,  # Lower temperature for more consistent, factual output
            max_tokens=4000,  # Enough for most pages
            max_retries=3
        )
        
        if response and response.get("content"):
            cleaned = response["content"].strip()
            
            # Log token usage for cost tracking
            usage = response.get("usage", {})
            logger.info(
                "content_cleaned",
                url=url,
                tokens_used=usage.get("total_tokens", 0),
                model=model
            )
            
            return cleaned
        else:
            logger.error("llm_cleaning_failed", url=url, reason="No content in response")
            return None
            
    except Exception as e:
        logger.error("llm_cleaning_error", url=url, error=str(e))
        return None


def needs_cleaning(content: str) -> bool:
    """
    Quick check if content likely needs cleaning.
    
    Args:
        content: Content to check
    
    Returns:
        True if content likely needs cleaning
    """
    # Heuristics for content that needs cleaning
    navigation_indicators = [
        "Find ANZ",
        "Support Centre",
        "Jump to",
        "Quick links",
        "Branch locator",
        "Top\n"
    ]
    
    # Check if navigation elements are present
    has_navigation = any(indicator in content for indicator in navigation_indicators)
    
    # Check for very short content (might need enhancement)
    is_very_short = len(content.strip()) < 500
    
    # Check for special character artifacts (like arrow symbols, special unicode)
    # Using chr() to avoid unicode escape issues
    artifacts = [chr(0xf0), chr(0x2022), chr(0x25b6), chr(0x2191), chr(0x2192)]
    has_artifacts = any(char in content for char in artifacts)
    
    return has_navigation or (is_very_short and has_artifacts)


async def clean_document_file(
    filepath: str,
    model: str = "gpt-4o",
    force: bool = False
) -> Optional[str]:
    """
    Clean a single document file.
    
    Args:
        filepath: Path to document file
        model: OpenAI model to use
        force: If True, clean even if heuristics suggest it's not needed
    
    Returns:
        Path to cleaned file or None on failure
    """
    try:
        path = Path(filepath)
        if not path.exists():
            logger.error("file_not_found", filepath=filepath)
            return None
        
        # Read original content
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Parse metadata header
        metadata_end = 0
        title = ""
        url = ""
        retrieval_date = ""
        
        for i, line in enumerate(lines):
            if line.startswith("Title: "):
                title = line.replace("Title: ", "").strip()
            elif line.startswith("Source URL: "):
                url = line.replace("Source URL: ", "").strip()
            elif line.startswith("Retrieval Date: "):
                retrieval_date = line.replace("Retrieval Date: ", "").strip()
            elif line.strip() == "" and i > 4:
                metadata_end = i + 1
                break
        
        # Extract content (skip metadata header)
        content_lines = lines[metadata_end:]
        # Remove footer (after "---")
        content = "".join(content_lines)
        if "---" in content:
            content = content.split("---")[0]
        
        content = content.strip()
        
        # Check if cleaning is needed
        if not force and not needs_cleaning(content):
            logger.info("cleaning_not_needed", filepath=filepath)
            return str(path)
        
        # Clean with LLM
        logger.info("cleaning_started", filepath=filepath, url=url)
        cleaned_content = clean_content_with_llm(content, title, url, model)
        
        if not cleaned_content:
            logger.warning("cleaning_failed_keeping_original", filepath=filepath)
            return str(path)
        
        # Write cleaned version (backup original first)
        backup_path = path.with_suffix('.original.txt')
        if not backup_path.exists():
            path.rename(backup_path)
        
        # Format cleaned document
        formatted = f"""Title: {title}
Source URL: {url}
Retrieval Date: {retrieval_date}
Content Type: public
Cleaned: Yes

{cleaned_content}

---
Original URL: {url}
Scraped: {retrieval_date}
Cleaned with LLM: {model}
"""
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(formatted)
        
        logger.info("cleaning_complete", filepath=filepath)
        return str(path)
        
    except Exception as e:
        logger.error("clean_document_error", filepath=filepath, error=str(e))
        return None


async def clean_all_documents(
    directory: str = "scraped_docs",
    model: str = "gpt-4o",
    force: bool = False,
    max_concurrent: int = 3
) -> Dict[str, bool]:
    """
    Clean all documents in a directory.
    
    Args:
        directory: Directory containing documents
        model: OpenAI model to use
        force: If True, clean all files regardless of heuristics
        max_concurrent: Maximum concurrent cleaning operations
    
    Returns:
        Dictionary mapping filepaths to success status
    """
    doc_dir = Path(directory)
    if not doc_dir.exists():
        logger.error("directory_not_found", directory=directory)
        return {}
    
    txt_files = list(doc_dir.glob("*.txt"))
    # Skip backup files
    txt_files = [f for f in txt_files if not f.name.endswith('.original.txt')]
    
    logger.info("cleaning_batch_started", total_files=len(txt_files), directory=directory)
    
    semaphore = asyncio.Semaphore(max_concurrent)
    results = {}
    
    async def clean_with_limit(filepath):
        async with semaphore:
            result = await clean_document_file(str(filepath), model=model, force=force)
            results[str(filepath)] = result is not None
            return result
    
    tasks = [clean_with_limit(f) for f in txt_files]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    successful = sum(1 for v in results.values() if v)
    logger.info(
        "cleaning_batch_complete",
        total=len(txt_files),
        successful=successful,
        failed=len(txt_files) - successful
    )
    
    return results


# For running as script
if __name__ == "__main__":
    import sys
    from utils.logger import setup_logging
    
    setup_logging()
    
    async def main():
        import argparse
        
        parser = argparse.ArgumentParser(description="Clean scraped knowledge base documents with LLM")
        parser.add_argument(
            "--directory",
            default="scraped_docs",
            help="Directory containing documents (default: scraped_docs)"
        )
        parser.add_argument(
            "--model",
            default="gpt-4o",
            help="OpenAI model to use (default: gpt-4o)"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Clean all files, even if heuristics suggest they don't need cleaning"
        )
        parser.add_argument(
            "--file",
            help="Clean a single file instead of all files in directory"
        )
        
        args = parser.parse_args()
        
        if args.file:
            result = await clean_document_file(args.file, model=args.model, force=args.force)
            if result:
                print(f"✓ Cleaned: {result}")
            else:
                print(f"✗ Failed to clean: {args.file}")
                sys.exit(1)
        else:
            results = await clean_all_documents(
                directory=args.directory,
                model=args.model,
                force=args.force
            )
            successful = sum(1 for v in results.values() if v)
            total = len(results)
            print(f"Cleaned {successful}/{total} documents")
            sys.exit(0 if successful == total else 1)
    
    asyncio.run(main())
