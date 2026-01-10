# Hierarchical Scraper Approach

## Overview

The improved hierarchical scraper preserves document structure during extraction, converting HTML to markdown while removing navigation elements at the HTML level.

## Key Improvements Over Current Scraper

### 1. **Structure Preservation**
- **Current**: Flattens all HTML → plain text (loses hierarchy)
- **Improved**: Converts HTML headings → Markdown headings (`#`, `##`, `###`)
- **Benefit**: Better document organization, improves vector embeddings

### 2. **Navigation Removal at HTML Level**
- **Current**: Removes `<nav>`, `<header>`, `<footer>` but navigation inside `<main>` slips through
- **Improved**: Removes navigation elements based on:
  - Semantic HTML (`role="navigation"`, `role="banner"`)
  - Common classes (`.breadcrumb`, `.navigation`, `.sidebar`)
  - Content patterns ("Jump to", "Skip to", etc.)
- **Benefit**: Cleaner output from the start, less post-processing

### 3. **List Structure Preservation**
- **Current**: `<ul>`, `<ol>` → plain text lines
- **Improved**: Converts to markdown lists (`- item`, preserves order)
- **Benefit**: Better readability and structure

### 4. **Hierarchical Extraction**
- **Current**: Single pass, extracts all text
- **Improved**: Recursive extraction that understands document structure
- **Benefit**: Preserves section relationships

## Implementation Details

### Navigation Detection

```python
# Multiple strategies for finding navigation:
1. Semantic HTML: role="navigation", role="banner"
2. Common classes: .nav, .navigation, .breadcrumb, .sidebar
3. Content patterns: Text like "Jump to", "Skip to content"
4. Element types: <nav>, <header>, <footer>, <aside>
```

### Structure Conversion

- `H1` → `# Heading`
- `H2` → `## Heading`
- `H3` → `### Heading`
- `<ul>` → Markdown bullet list
- `<ol>` → Markdown numbered list (as bullets for simplicity)
- `<a href>` → `[text](url)` or plain text for anchors
- `<strong>`, `<b>` → `**bold**`
- `<em>`, `<i>` → `*italic*`

### Content Extraction Flow

1. **Parse HTML** with BeautifulSoup
2. **Remove navigation elements** using multiple strategies
3. **Find main content area** (`<main>`, `<article>`, or content divs)
4. **Recursively extract** content, preserving structure
5. **Convert to markdown** with proper formatting
6. **Clean up** excessive whitespace

## Usage

### Integration with Existing Ingestor

Replace the `extract_content()` function in `knowledge/ingestor.py`:

```python
from knowledge.hierarchical_extractor import extract_content_hierarchical

# In scrape_urls(), replace:
# extracted = extract_content(result["content"], url)
# With:
extracted = extract_content_hierarchical(result["content"], url)
```

### Standalone Usage

```python
from knowledge.hierarchical_extractor import extract_content_hierarchical

html_content = "<html>..."
result = extract_content_hierarchical(html_content, url="https://example.com")
print(result["content"])  # Markdown-formatted content
```

## Benefits

1. **Better Vector Embeddings**: Hierarchical structure provides context
2. **Improved Retrieval**: Semantic search benefits from structure
3. **Cleaner Output**: Less navigation artifacts from the start
4. **Reduced Post-Processing**: Fewer cleaning steps needed
5. **Better Readability**: Markdown format is human-readable
6. **Preserved Relationships**: Section hierarchy is maintained

## Trade-offs

### Pros
- Cleaner output from extraction
- Better structure for knowledge base
- Reduced need for post-processing
- Better for vector search

### Cons
- Slightly more complex code
- Markdown conversion might not be perfect for all HTML
- Some edge cases in HTML structure might not convert well

## Comparison: Current vs Hierarchical

### Current Approach
```
Input HTML:
<h1>Title</h1>
<nav>Find ANZ</nav>
<h2>Section</h2>
<p>Content</p>

Output:
Title
Find ANZ
Section
Content
```

### Hierarchical Approach
```
Input HTML:
<h1>Title</h1>
<nav>Find ANZ</nav>  # Removed at HTML level
<h2>Section</h2>
<p>Content</p>

Output:
# Title

## Section
Content
```

## Next Steps

1. Test hierarchical extractor on a sample URL
2. Compare output with current scraper
3. Integrate into `ingestor.py` if results are better
4. Optionally run on all scraped content (re-scrape)
5. Evaluate impact on vector search quality
