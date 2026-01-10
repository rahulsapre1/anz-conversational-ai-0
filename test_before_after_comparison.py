#!/usr/bin/env python3
"""
Show before/after comparison of current vs hierarchical extractor.
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
from utils.logger import setup_logging

setup_logging()


async def compare_extractors(url: str, save_files: bool = True):
    """Compare both extractors and show side-by-side results."""
    print("=" * 100)
    print(f"BEFORE/AFTER COMPARISON FOR: {url}")
    print("=" * 100)
    print()
    
    # Fetch HTML
    print("Fetching HTML...")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status != 200:
                print(f"❌ Failed to fetch URL: {response.status}")
                return
            html = await response.text()
    
    print(f"✓ Fetched {len(html):,} bytes\n")
    
    # Extract with current method
    print("Extracting with CURRENT extractor...")
    result_current = extract_content_current(html, url)
    current_content = result_current.get("content", "") if result_current else ""
    
    # Extract with hierarchical method
    print("Extracting with HIERARCHICAL extractor...")
    result_hierarchical = extract_content_hierarchical(html, url)
    hierarchical_content = result_hierarchical.get("content", "") if result_hierarchical else ""
    
    print()
    
    # Save files if requested
    if save_files:
        output_dir = Path("comparison_output")
        output_dir.mkdir(exist_ok=True)
        
        current_file = output_dir / "current_extractor.txt"
        hierarchical_file = output_dir / "hierarchical_extractor.txt"
        
        with open(current_file, "w", encoding="utf-8") as f:
            f.write(f"Title: {result_current.get('title', 'N/A')}\n")
            f.write(f"URL: {url}\n")
            f.write("=" * 80 + "\n\n")
            f.write(current_content)
        
        with open(hierarchical_file, "w", encoding="utf-8") as f:
            f.write(f"Title: {result_hierarchical.get('title', 'N/A')}\n")
            f.write(f"URL: {url}\n")
            f.write("=" * 80 + "\n\n")
            f.write(hierarchical_content)
        
        print(f"✓ Saved to: {current_file}")
        print(f"✓ Saved to: {hierarchical_file}\n")
    
    # Statistics
    print("=" * 100)
    print("STATISTICS")
    print("=" * 100)
    print(f"Current Extractor:")
    print(f"  - Length: {len(current_content):,} characters")
    print(f"  - Lines: {len(current_content.split(chr(10)))}")
    nav_count_current = sum(1 for nav in ["Find ANZ", "Support Centre", "Jump to", "Top"] if nav in current_content)
    print(f"  - Navigation elements: {nav_count_current}")
    heading_count_current = sum(1 for line in current_content.split('\n') if len(line) > 0 and line[0].isupper() and len(line) < 80 and not line.startswith(('http', 'www', '+61', '13 ')))
    print(f"  - Potential headings: ~{heading_count_current}")
    
    print(f"\nHierarchical Extractor:")
    print(f"  - Length: {len(hierarchical_content):,} characters")
    print(f"  - Lines: {len(hierarchical_content.split(chr(10)))}")
    nav_count_hier = sum(1 for nav in ["Find ANZ", "Support Centre", "Jump to", "Top"] if nav in hierarchical_content)
    print(f"  - Navigation elements: {nav_count_hier}")
    heading_count_hier = hierarchical_content.count('\n#')
    print(f"  - Markdown headings (#): {heading_count_hier}")
    
    print()
    
    # Show sample sections
    print("=" * 100)
    print("SAMPLE COMPARISON - First 1000 characters")
    print("=" * 100)
    
    print("\n" + "-" * 100)
    print("BEFORE (Current Extractor):")
    print("-" * 100)
    print(current_content[:1000])
    if len(current_content) > 1000:
        print("\n... (truncated)")
    
    print("\n" + "-" * 100)
    print("AFTER (Hierarchical Extractor):")
    print("-" * 100)
    print(hierarchical_content[:1000])
    if len(hierarchical_content) > 1000:
        print("\n... (truncated)")
    
    # Show a specific section comparison
    print("\n" + "=" * 100)
    print("HEADING STRUCTURE COMPARISON")
    print("=" * 100)
    
    print("\n[BEFORE] First 10 lines that look like headings:")
    lines_current = current_content.split('\n')
    heading_lines = [line for line in lines_current[:50] 
                     if line.strip() and len(line.strip()) < 100 
                     and line.strip()[0].isupper() 
                     and not line.strip().startswith(('http', 'www', '+61', '13 ', 'Find ANZ', 'Support Centre'))][:10]
    for i, line in enumerate(heading_lines, 1):
        print(f"  {i}. {line[:80]}")
    
    print("\n[AFTER] First 10 markdown headings (#):")
    lines_hier = hierarchical_content.split('\n')
    heading_lines = [line for line in lines_hier if line.strip().startswith('#')][:10]
    for i, line in enumerate(heading_lines, 1):
        print(f"  {i}. {line[:80]}")
    
    print("\n" + "=" * 100)
    print("✓ Comparison complete!")
    print("=" * 100)


async def main():
    # Test with PayID page (a good example)
    test_url = "https://www.anz.com.au/support/online-banking/payments/pay-id/"
    
    await compare_extractors(test_url, save_files=True)


if __name__ == "__main__":
    asyncio.run(main())
