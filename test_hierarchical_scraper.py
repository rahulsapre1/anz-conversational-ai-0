#!/usr/bin/env python3
"""
Test hierarchical scraper on a specific URL and save as .md file.
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from knowledge.ingestor import (
    fetch_url,
    extract_content_hierarchical,
    format_document_for_upload,
    save_document
)
from utils.logger import setup_logging, get_logger
import aiohttp

setup_logging()
logger = get_logger(__name__)


async def test_hierarchical_scrape(url: str, output_dir: str = "test_output"):
    """Test hierarchical scraper on a single URL."""
    print("=" * 80)
    print(f"Testing Hierarchical Scraper")
    print(f"URL: {url}")
    print("=" * 80)
    print()
    
    # Fetch HTML
    print("1. Fetching HTML...")
    async with aiohttp.ClientSession() as session:
        result = await fetch_url(session, url, timeout=30)
        
        if not result or not result.get("content"):
            print("❌ Failed to fetch URL")
            return None
        
        html = result["content"]
        print(f"   ✓ Fetched {len(html):,} bytes of HTML\n")
    
    # Extract with hierarchical extractor
    print("2. Extracting content with hierarchical extractor...")
    extracted = extract_content_hierarchical(html, url)
    
    if not extracted or not extracted.get("content"):
        print("❌ Failed to extract content")
        return None
    
    print(f"   ✓ Extracted {len(extracted['content']):,} characters")
    print(f"   ✓ Title: {extracted['title']}\n")
    
    # Create document
    from datetime import datetime
    doc = {
        "title": extracted["title"],
        "url": extracted["url"],
        "content": extracted["content"],
        "retrieval_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    # Save as .md file
    print("3. Saving as .md file...")
    filepath = save_document(doc, output_dir)
    
    if filepath:
        print(f"   ✓ Saved to: {filepath}\n")
        
        # Show preview
        print("=" * 80)
        print("FILE PREVIEW (First 800 characters):")
        print("=" * 80)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            print(content[:800])
            if len(content) > 800:
                print("\n... (truncated)")
        
        # Statistics
        print("\n" + "=" * 80)
        print("STATISTICS:")
        print("=" * 80)
        lines = content.split('\n')
        markdown_headings = sum(1 for line in lines if line.strip().startswith('#'))
        nav_elements = sum(1 for nav in ["Find ANZ", "Support Centre", "Jump to", "Top"] if nav in content)
        
        print(f"Total length: {len(content):,} characters")
        print(f"Total lines: {len(lines)}")
        print(f"Markdown headings (#): {markdown_headings}")
        print(f"Navigation elements: {nav_elements}")
        print(f"File: {filepath}")
        print("=" * 80)
        
        return filepath
    else:
        print("❌ Failed to save file")
        return None


async def main():
    test_url = "https://www.anz.com.au/security/report-scams-fraud/"
    
    result = await test_hierarchical_scrape(test_url, output_dir="test_output")
    
    if result:
        print(f"\n✅ Success! File saved: {result}")
    else:
        print("\n❌ Failed to scrape and save")


if __name__ == "__main__":
    asyncio.run(main())
