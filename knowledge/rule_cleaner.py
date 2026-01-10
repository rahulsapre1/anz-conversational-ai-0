"""
Rule-based content cleaner for scraped knowledge base documents.
Removes navigation elements and artifacts while preserving all factual content.
"""
import sys
import re
from typing import List, Optional
from pathlib import Path

# Add project root to Python path (for running as script)
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.logger import get_logger

logger = get_logger(__name__)


# Lines to completely remove (exact matches, case-insensitive)
NAVIGATION_LINES_TO_REMOVE = [
    "find anz",
    "support centre",
    "jump to",
    "top",
    "branch locator",
    "quick links",
    "calculators and tools",
    "apply online",
    "register for internet banking",
]

# Phrases to remove from lines (but keep the rest of the line)
PHRASES_TO_REMOVE = [
    r"click to play video",
    r"video transcript",
    r"\d+:\d+",  # Video duration timestamps like "1:47", "00:53"
]

# Special unicode characters to remove (using chr() to avoid escape issues)
UNICODE_TO_REMOVE = [
    chr(0xf0),  # Various special characters
    chr(0x2022),  # Bullet
    chr(0x25b6),  # Play arrow
    chr(0x2191),  # Up arrow
    chr(0x2192),  # Right arrow
    chr(0x2193),  # Down arrow
    chr(0x2190),  # Left arrow
]


def remove_navigation_lines(lines: List[str]) -> List[str]:
    """
    Remove navigation-only lines.
    
    Args:
        lines: List of content lines
    
    Returns:
        Filtered list with navigation lines removed
    """
    filtered = []
    for line in lines:
        stripped = line.strip()
        
        # Keep empty lines
        if not stripped:
            filtered.append(line)
            continue
        
        # Check if line is only navigation text (case-insensitive)
        is_navigation = any(
            nav.strip().lower() == stripped.lower()
            for nav in NAVIGATION_LINES_TO_REMOVE
        )
        
        if not is_navigation:
            filtered.append(line)
    
    return filtered


def clean_line_phrases(line: str) -> str:
    """
    Remove specific phrases from a line while keeping the rest.
    
    Args:
        line: Content line
    
    Returns:
        Line with phrases removed
    """
    cleaned = line
    
    # Remove video-related phrases
    for phrase in PHRASES_TO_REMOVE:
        cleaned = re.sub(phrase, '', cleaned, flags=re.IGNORECASE)
    
    return cleaned


def remove_unicode_artifacts(text: str) -> str:
    """
    Remove special unicode characters that don't convey meaning.
    
    Args:
        text: Text content
    
    Returns:
        Text with unicode artifacts removed
    """
    cleaned = text
    
    # Remove specific unicode characters
    for char in UNICODE_TO_REMOVE:
        cleaned = cleaned.replace(char, '')
    
    # Note: We're NOT removing single-character lines here as they might be meaningful
    # The navigation line removal handles those cases
    
    return cleaned


def organize_with_headers(lines: List[str]) -> List[str]:
    """
    Add markdown headers to organize content, but preserve all original content.
    
    Args:
        lines: List of content lines
    
    Returns:
        Lines with headers added where appropriate
    """
    organized = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            organized.append(lines[i])
            i += 1
            continue
        
        # Detect potential section headers (lines that are short, title-like)
        # This is conservative - only add headers if line looks like a title
        is_potential_header = (
            len(line) < 80 and
            not line.startswith(('http', 'www.', '+61', '13 ')) and
            not re.match(r'^\d+[\.\)]', line) and  # Not numbered list
            not line.startswith('-') and  # Not bullet point
            line[0].isupper() and
            i > 0 and  # Not first line
            i < len(lines) - 1  # Not last line
        )
        
        if is_potential_header and organized and organized[-1].strip():
            # Check if previous content was substantial (more than just whitespace)
            organized.append(f"\n## {line}\n")
        else:
            organized.append(lines[i])
        
        i += 1
    
    return organized


def clean_content_rules(content: str, add_headers: bool = False) -> str:
    """
    Clean content using rule-based approach.
    
    Args:
        content: Raw content to clean
        add_headers: Whether to add markdown headers for organization
    
    Returns:
        Cleaned content
    """
    # Split into lines
    lines = content.split('\n')
    
    # Remove navigation lines
    lines = remove_navigation_lines(lines)
    
    # Clean phrases from each line
    lines = [clean_line_phrases(line) for line in lines]
    
    # Rejoin and remove unicode artifacts
    cleaned = '\n'.join(lines)
    cleaned = remove_unicode_artifacts(cleaned)
    
    # Clean up multiple blank lines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    # Optionally add headers
    if add_headers:
        lines = cleaned.split('\n')
        lines = organize_with_headers(lines)
        cleaned = '\n'.join(lines)
    
    # Final cleanup: remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    return cleaned


def clean_document_file(
    filepath: str,
    add_headers: bool = True,
    backup: bool = True
) -> Optional[str]:
    """
    Clean a single document file using rule-based approach.
    
    Args:
        filepath: Path to document file
        add_headers: Whether to add markdown headers
        backup: Whether to backup original file
    
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
            content = f.read()
        
        # Parse metadata header
        lines = content.split('\n')
        metadata_lines = []
        content_start_idx = 0
        title = ""
        url = ""
        retrieval_date = ""
        
        # Build metadata and find content start
        for i, line in enumerate(lines):
            if line.startswith("Title: "):
                title = line.replace("Title: ", "").strip()
                metadata_lines.append(line)
            elif line.startswith("Source URL: "):
                url = line.replace("Source URL: ", "").strip()
                metadata_lines.append(line)
            elif line.startswith("Retrieval Date: "):
                retrieval_date = line.replace("Retrieval Date: ", "").strip()
                metadata_lines.append(line)
            elif line.startswith("Content Type: "):
                metadata_lines.append(line)
                metadata_lines.append("Cleaned: Yes")  # Add cleaned flag
            elif line.strip() == "" and i >= 4 and content_start_idx == 0:
                # First empty line after metadata marks content start (line 4 or later)
                # Make sure we've seen Content Type
                if any("Content Type:" in ml or "Content Type: " in ml for ml in metadata_lines):
                    content_start_idx = i + 1
                    break  # Stop processing metadata
        
        # If we didn't find content start, look for it after Content Type
        if content_start_idx == 0:
            for i, line in enumerate(lines):
                if i > 0 and (lines[i-1].startswith("Content Type:") or lines[i-1].startswith("Content Type: ")) and line.strip() == "":
                    content_start_idx = i + 1
                    break
        
        # Get all lines from content start to end
        if content_start_idx > 0:
            content_lines = lines[content_start_idx:]
        else:
            # Fallback: assume content starts after line 5
            content_lines = lines[5:]
        
        # Find footer (after "---") - search from the end
        footer_idx = len(content_lines)
        # Look for "---" in the last 10 lines (where footer typically is)
        search_start = max(0, len(content_lines) - 10)
        for i in range(len(content_lines) - 1, search_start - 1, -1):
            if i >= 0 and content_lines[i].strip() == "---":
                footer_idx = i
                break
        
        # Extract main content (everything before footer)
        main_content = '\n'.join(content_lines[:footer_idx])
        
        # Debug: Log content length before cleaning
        logger.debug("content_before_cleaning", length=len(main_content), lines=len(content_lines[:footer_idx]))
        
        # Clean content
        logger.info("cleaning_started", filepath=filepath, url=url, content_length=len(main_content))
        cleaned_content = clean_content_rules(main_content, add_headers=add_headers)
        
        # Debug: Log content length after cleaning
        logger.debug("content_after_cleaning", length=len(cleaned_content))
        
        # Backup original if requested
        if backup:
            backup_path = path.with_suffix('.original.txt')
            if not backup_path.exists():
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info("backup_created", backup_path=str(backup_path))
        
        # Reconstruct document with metadata
        footer_lines = content_lines[footer_idx:] if footer_idx < len(content_lines) else []
        footer = '\n'.join(footer_lines)
        
        formatted = '\n'.join(metadata_lines) + '\n\n' + cleaned_content + '\n\n' + footer
        
        # Write cleaned version
        with open(path, "w", encoding="utf-8") as f:
            f.write(formatted)
        
        logger.info("cleaning_complete", filepath=filepath)
        return str(path)
        
    except Exception as e:
        logger.error("clean_document_error", filepath=filepath, error=str(e))
        return None


def clean_all_documents(
    directory: str = "scraped_docs",
    add_headers: bool = True,
    backup: bool = True
) -> dict:
    """
    Clean all documents in a directory.
    
    Args:
        directory: Directory containing documents
        add_headers: Whether to add markdown headers
        backup: Whether to backup original files
    
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
    
    results = {}
    for filepath in txt_files:
        result = clean_document_file(str(filepath), add_headers=add_headers, backup=backup)
        results[str(filepath)] = result is not None
    
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
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean scraped knowledge base documents with rule-based approach")
    parser.add_argument(
        "--directory",
        default="scraped_docs",
        help="Directory containing documents (default: scraped_docs)"
    )
    parser.add_argument(
        "--file",
        help="Clean a single file instead of all files in directory"
    )
    parser.add_argument(
        "--no-headers",
        action="store_true",
        help="Don't add markdown headers"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create backup files"
    )
    
    args = parser.parse_args()
    
    add_headers = not args.no_headers
    backup = not args.no_backup
    
    if args.file:
        result = clean_document_file(args.file, add_headers=add_headers, backup=backup)
        if result:
            print(f"✓ Cleaned: {result}")
            sys.exit(0)
        else:
            print(f"✗ Failed to clean: {args.file}")
            sys.exit(1)
    else:
        results = clean_all_documents(
            directory=args.directory,
            add_headers=add_headers,
            backup=backup
        )
        successful = sum(1 for v in results.values() if v)
        total = len(results)
        print(f"Cleaned {successful}/{total} documents")
        sys.exit(0 if successful == total else 1)
