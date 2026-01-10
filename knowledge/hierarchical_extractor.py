"""
Hierarchical HTML content extractor that preserves structure and converts to markdown.
Removes navigation elements at HTML level for cleaner output.
"""
import sys
import re
from typing import Dict, Optional
from pathlib import Path
from bs4 import BeautifulSoup, Tag, NavigableString

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.logger import get_logger

logger = get_logger(__name__)


# HTML elements/classes that typically contain navigation or non-content
NAVIGATION_SELECTORS = [
    'nav',
    'header',
    'footer',
    'aside',
    '[role="navigation"]',
    '[role="banner"]',
    '[role="contentinfo"]',
    '[role="complementary"]',
    '.breadcrumb',
    '.breadcrumbs',
    '.navigation',
    '.nav',
    '.sidebar',
    '.skip-link',
    '.skip-to-content',
    '.jump-to',
    '.jump-to-content',
    '[aria-label*="navigation" i]',
    '[aria-label*="menu" i]',
    '[class*="nav" i]',
    '[class*="menu" i]',
    '[class*="breadcrumb" i]',
    '[class*="sidebar" i]',
]

# Classes/IDs that are likely navigation or non-content
NAVIGATION_CLASSES = [
    'nav',
    'navigation',
    'menu',
    'breadcrumb',
    'breadcrumbs',
    'sidebar',
    'skip-link',
    'skip-to',
    'jump-to',
    'quick-links',
    'footer-links',
]


def remove_navigation_elements(soup: BeautifulSoup) -> None:
    """
    Remove navigation-related elements from the HTML soup.
    Preserves main content areas.
    
    Args:
        soup: BeautifulSoup object to clean
    """
    # Remove script, style, and other non-content elements first
    for tag in soup(['script', 'style', 'noscript', 'iframe', 'embed', 'object']):
        tag.decompose()
    
    # Remove standard navigation elements (but not main/article/content divs)
    for selector in NAVIGATION_SELECTORS:
        for element in soup.select(selector):
            # Don't remove if it's a main content area
            if element.name in ['main', 'article']:
                continue
            # Don't remove divs that are main content areas
            if element.name == 'div':
                classes = ' '.join(element.get('class', [])).lower()
                ids = element.get('id', '').lower()
                if 'content' in classes or 'content' in ids or 'main' in classes or 'main' in ids:
                    continue
            element.decompose()
    
    # Remove elements with navigation-related classes (but preserve content areas)
    for class_name in NAVIGATION_CLASSES:
        for element in soup.find_all(class_=re.compile(class_name, re.I)):
            # Skip main content areas
            if element.name in ['main', 'article']:
                continue
            if element.name == 'div':
                classes = ' '.join(element.get('class', [])).lower()
                if 'content' in classes or 'main' in classes:
                    continue
            element.decompose()
    
    # Remove elements that are likely navigation based on content
    # (e.g., links that say "Jump to", "Skip to content", etc.)
    # But only if they're not inside main content areas
    navigation_text_patterns = [
        r'^jump to',
        r'^skip to',
        r'^find anz',
        r'^support centre',
        r'^top$',
        r'^back to top',
    ]
    
    for pattern in navigation_text_patterns:
        for element in soup.find_all(text=re.compile(pattern, re.I)):
            parent = element.parent
            if not parent:
                continue
            
            # Don't remove if inside main/article
            if parent.find_parent(['main', 'article']):
                # Only remove if it's clearly navigation (link/button)
                if parent.name not in ['a', 'button']:
                    continue
            
            if parent.name in ['a', 'button', 'div', 'span']:
                # Only remove if it's a link or button, or very short text
                if parent.name in ['a', 'button'] or len(element.strip()) < 20:
                    parent.decompose()


def convert_heading_to_markdown(element: Tag) -> str:
    """
    Convert HTML heading to markdown format.
    
    Args:
        element: Heading tag (h1-h6)
    
    Returns:
        Markdown heading string
    """
    level = int(element.name[1])  # Extract number from h1, h2, etc.
    text = element.get_text(strip=True)
    return f"{'#' * level} {text}\n"


def convert_list_to_markdown(element: Tag) -> str:
    """
    Convert HTML list (ul/ol) to markdown format.
    
    Args:
        element: List tag (ul or ol)
    
    Returns:
        Markdown list string
    """
    markdown_lines = []
    items = element.find_all('li', recursive=False)
    
    for item in items:
        text = item.get_text(separator=' ', strip=True)
        # Clean up whitespace
        text = ' '.join(text.split())
        
        if element.name == 'ol':
            # For ordered lists, we'll use simple bullets since we can't track numbers easily
            # But we preserve the order
            markdown_lines.append(f"- {text}")
        else:
            markdown_lines.append(f"- {text}")
    
    return '\n'.join(markdown_lines) + '\n'


def convert_link_to_markdown(element: Tag) -> str:
    """
    Convert HTML link to markdown format.
    
    Args:
        element: Anchor tag
    
    Returns:
        Markdown link or plain text
    """
    text = element.get_text(strip=True)
    href = element.get('href', '')
    
    # Skip anchor links and navigation links
    if href.startswith('#') or not href:
        return text
    
    # Convert relative URLs to absolute (basic handling)
    if href.startswith('/'):
        # Could extract base URL, but for now just return text
        return text
    
    # Return markdown link if it's external
    if href.startswith('http'):
        return f"[{text}]({href})"
    
    return text


def extract_hierarchical_content(element: Tag, level: int = 0) -> str:
    """
    Recursively extract content from HTML element, preserving hierarchy.
    
    Args:
        element: BeautifulSoup element to extract from
        level: Current nesting level
    
    Returns:
        Markdown-formatted content string
    """
    content_parts = []
    
    for child in element.children:
        if isinstance(child, NavigableString):
            # Plain text node
            text = str(child).strip()
            if text:
                content_parts.append(text)
        elif isinstance(child, Tag):
            tag_name = child.name.lower()
            
            # Handle headings
            if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                content_parts.append(convert_heading_to_markdown(child))
            
            # Handle lists
            elif tag_name in ['ul', 'ol']:
                content_parts.append(convert_list_to_markdown(child))
            
            # Handle list items (already handled by parent list, but catch any strays)
            elif tag_name == 'li':
                text = child.get_text(separator=' ', strip=True)
                if text:
                    content_parts.append(f"- {text}\n")
            
            # Handle links
            elif tag_name == 'a':
                link_text = convert_link_to_markdown(child)
                if link_text:
                    content_parts.append(link_text)
            
            # Handle paragraphs
            elif tag_name == 'p':
                text = child.get_text(separator=' ', strip=True)
                if text:
                    content_parts.append(f"{text}\n")
            
            # Handle strong/bold
            elif tag_name in ['strong', 'b']:
                text = child.get_text(strip=True)
                if text:
                    content_parts.append(f"**{text}**")
            
            # Handle emphasis/italic
            elif tag_name in ['em', 'i']:
                text = child.get_text(strip=True)
                if text:
                    content_parts.append(f"*{text}*")
            
            # Handle line breaks
            elif tag_name == 'br':
                content_parts.append('\n')
            
            # Handle divs, sections - recursively process
            elif tag_name in ['div', 'section', 'article', 'main']:
                # Skip if it's likely navigation
                classes = ' '.join(child.get('class', []))
                if any(nav_class in classes.lower() for nav_class in NAVIGATION_CLASSES):
                    continue
                
                nested_content = extract_hierarchical_content(child, level + 1)
                if nested_content.strip():
                    content_parts.append(nested_content)
            
            # For other elements, just extract text recursively
            else:
                nested_content = extract_hierarchical_content(child, level + 1)
                if nested_content.strip():
                    content_parts.append(nested_content)
    
    # Join parts - use space for inline elements, preserve newlines
    if not content_parts:
        return ''
    
    result = ' '.join(content_parts)
    # Clean up: normalize whitespace but preserve intentional newlines
    result = re.sub(r'[ \t]+', ' ', result)  # Multiple spaces/tabs to single space
    result = re.sub(r' \n', '\n', result)  # Space before newline
    result = re.sub(r'\n ', '\n', result)  # Space after newline
    return result


def extract_content_hierarchical(html: str, url: str) -> Dict[str, Optional[str]]:
    """
    Extract content from HTML preserving hierarchical structure as markdown.
    
    Args:
        html: HTML content
        url: Source URL
    
    Returns:
        Dictionary with title, content (markdown), url
    """
    try:
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else "Untitled"
        
        # Try to find main content area BEFORE removing navigation
        # (so we can target removal more precisely)
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', class_=re.compile('content|main|article', re.I)) or
            soup.find('div', id=re.compile('content|main|article', re.I))
        )
        
        # Remove navigation elements at HTML level
        remove_navigation_elements(soup)
        
        # If main_content was found, check if it still exists after nav removal
        if main_content and main_content in soup.descendants:
            # Extract hierarchical content as markdown
            logger.debug("found_main_content", url=url, tag=main_content.name)
            content = extract_hierarchical_content(main_content)
        elif main_content:
            # main_content reference might be stale, find it again
            main_content = (
                soup.find('main') or
                soup.find('article') or
                soup.find('div', class_=re.compile('content|main|article', re.I)) or
                soup.find('div', id=re.compile('content|main|article', re.I))
            )
            if main_content:
                content = extract_hierarchical_content(main_content)
            else:
                # Fallback: extract from body
                body = soup.find('body')
                if body:
                    content = extract_hierarchical_content(body)
                else:
                    content = extract_hierarchical_content(soup)
        else:
            # Fallback: extract from body, but still preserve hierarchy
            logger.debug("main_content_not_found_using_body", url=url)
            body = soup.find('body')
            if body:
                content = extract_hierarchical_content(body)
            else:
                # Last resort: convert entire document
                logger.debug("body_not_found_using_soup", url=url)
                content = extract_hierarchical_content(soup)
        
        # Clean up content
        # Remove excessive blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        # Remove leading/trailing whitespace
        content = content.strip()
        
        # Log if content is empty
        if not content:
            logger.warning("extracted_content_empty", url=url)
        
        return {
            "title": title,
            "content": content,
            "url": url
        }
    
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error("hierarchical_extraction_error", url=url, error=str(e), traceback=error_detail)
        # Fallback to simple extraction
        return {
            "title": "Error Extracting Content",
            "content": None,
            "url": url
        }
