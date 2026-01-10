#!/usr/bin/env python3
"""
Test script for hierarchical extractor - compares with current extractor.
"""
import sys
import asyncio
import aiohttp
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from knowledge.hierarchical_extractor import extract_content_hierarchical
from knowledge.ingestor import extract_content as extract_content_current
from utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def test_extractors(url: str):
    """Test both extractors on the same URL."""
    print("=" * 80)
    print(f"Testing extractors on: {url}")
    print("=" * 80)
    
    # Fetch HTML
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status != 200:
                print(f"❌ Failed to fetch URL: {response.status}")
                return
            
            html = await response.text()
            print(f"✓ Fetched HTML: {len(html)} bytes\n")
    
    # Test current extractor
    print("-" * 80)
    print("CURRENT EXTRACTOR RESULTS:")
    print("-" * 80)
    result_current = extract_content_current(html, url)
    if result_current and result_current.get("content"):
        content_current = result_current["content"]
        print(f"Title: {result_current['title']}")
        print(f"Content length: {len(content_current)} characters")
        print(f"Lines: {len(content_current.split(chr(10)))}")
        print("\nFirst 500 characters:")
        print(content_current[:500])
        print("\n...")
        
        # Count navigation elements
        nav_count = sum(1 for nav in ["Find ANZ", "Support Centre", "Jump to", "Top"] 
                       if nav in content_current)
        print(f"\nNavigation elements found: {nav_count}")
    else:
        print("❌ Failed to extract content")
    
    # Test hierarchical extractor
    print("\n" + "-" * 80)
    print("HIERARCHICAL EXTRACTOR RESULTS:")
    print("-" * 80)
    result_hierarchical = extract_content_hierarchical(html, url)
    if result_hierarchical and result_hierarchical.get("content"):
        content_hierarchical = result_hierarchical["content"]
        print(f"Title: {result_hierarchical['title']}")
        print(f"Content length: {len(content_hierarchical)} characters")
        print(f"Lines: {len(content_hierarchical.split(chr(10)))}")
        print("\nFirst 500 characters:")
        print(content_hierarchical[:500])
        print("\n...")
        
        # Count navigation elements
        nav_count = sum(1 for nav in ["Find ANZ", "Support Centre", "Jump to", "Top"] 
                       if nav in content_hierarchical)
        print(f"\nNavigation elements found: {nav_count}")
        
        # Count markdown headings
        heading_count = content_hierarchical.count('\n#')
        print(f"Markdown headings found: {heading_count}")
    else:
        print("❌ Failed to extract content")
    
    # Comparison
    print("\n" + "=" * 80)
    print("COMPARISON:")
    print("=" * 80)
    if result_current and result_hierarchical:
        current_content = result_current.get("content", "")
        hierarchical_content = result_hierarchical.get("content", "")
        
        print(f"Current extractor:     {len(current_content):6} chars, {len(current_content.split(chr(10))):4} lines")
        print(f"Hierarchical extractor: {len(hierarchical_content):6} chars, {len(hierarchical_content.split(chr(10))):4} lines")
        
        # Show a sample section comparison
        print("\n--- SAMPLE SECTION COMPARISON ---")
        print("\n[Current - First heading-like text found]:")
        lines_current = current_content.split('\n')
        for i, line in enumerate(lines_current[:30]):
            if len(line) > 0 and line[0].isupper() and len(line) < 80:
                print(f"  {line}")
                if i < len(lines_current) - 1:
                    print(f"  {lines_current[i+1][:100]}")
                break
        
        print("\n[Hierarchical - First markdown heading found]:")
        lines_hierarchical = hierarchical_content.split('\n')
        for i, line in enumerate(lines_hierarchical[:30]):
            if line.startswith('#'):
                print(f"  {line}")
                if i < len(lines_hierarchical) - 1:
                    print(f"  {lines_hierarchical[i+1][:100]}")
                break
    
    print("\n" + "=" * 80)


async def main():
    # Get a sample URL from the XML file
    test_url = "https://www.anz.com.au/support/online-banking/payments/pay-id/"
    
    print("\nTesting hierarchical extractor vs current extractor\n")
    await test_extractors(test_url)


if __name__ == "__main__":
    asyncio.run(main())
