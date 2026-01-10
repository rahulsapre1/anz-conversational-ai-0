# Task 7: Knowledge Base Ingestion - Synthetic Documents

## Overview
Create synthetic documents to fill content gaps that public ANZ pages cannot cover. These documents must be clearly labeled as synthetic, document their assumptions, and be narrow and explicit in scope.

## Prerequisites
- Task 1 completed (project structure, config, logging)
- Task 6 completed (Vector Store setup)
- Knowledge of content gaps from Task 4 (web scraping)
- Virtual environment activated

## Important Notes

⚠️ **Synthetic documents should only be created when:**
- Public ANZ content has clear gaps
- The gap is specific and narrow
- The information is needed for the MVP to function
- You can clearly document assumptions

❌ **Do NOT create synthetic documents for:**
- Topics already covered by public ANZ pages
- Broad, general topics
- Information that should come from official sources
- Content that would be misleading without official backing

## Deliverables

### 1. Synthetic Document Generator (knowledge/synthetic_generator.py)

Create `knowledge/synthetic_generator.py` with functions to generate and format synthetic documents.

## Implementation

### Step 1: Document Structure

Synthetic documents must follow this exact format:

```
Title: [Topic] - SYNTHETIC CONTENT
Label: SYNTHETIC
Content Type: synthetic

[Document content here]

Assumptions:
- [Assumption 1]
- [Assumption 2]
- [Assumption 3]

Source: Generated for ContactIQ MVP
Generated Date: [YYYY-MM-DD]
```

### Step 2: Helper Functions

```python
# knowledge/synthetic_generator.py
import re
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from config import Config
from utils.logger import get_logger
from knowledge.ingestor import sanitize_filename, format_document_for_upload

logger = get_logger(__name__)


def format_synthetic_document(
    title: str,
    content: str,
    assumptions: List[str],
    topic: str = "general"
) -> str:
    """
    Format synthetic document with proper labeling and structure.
    
    Args:
        title: Document title (without "SYNTHETIC CONTENT" suffix)
        content: Document content
        assumptions: List of assumptions made
        topic: Topic category (for organization)
    
    Returns:
        Formatted synthetic document text
    """
    full_title = f"{title} - SYNTHETIC CONTENT"
    generated_date = datetime.now().strftime("%Y-%m-%d")
    
    assumptions_text = "\n".join([f"- {assumption}" for assumption in assumptions])
    
    formatted = f"""Title: {full_title}
Label: SYNTHETIC
Content Type: synthetic
Topic: {topic}

{content}

Assumptions:
{assumptions_text}

Source: Generated for ContactIQ MVP
Generated Date: {generated_date}
"""
    return formatted


def save_synthetic_document(
    title: str,
    content: str,
    assumptions: List[str],
    topic: str = "general",
    output_dir: str = "synthetic_docs"
) -> Optional[str]:
    """
    Save synthetic document to .txt file.
    
    Args:
        title: Document title
        content: Document content
        assumptions: List of assumptions
        topic: Topic category
        output_dir: Output directory
    
    Returns:
        Path to saved file, or None on failure
    """
    try:
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Format document
        formatted = format_synthetic_document(title, content, assumptions, topic)
        
        # Sanitize filename
        sanitized_title = sanitize_filename(title)
        filename = f"{sanitized_title}_synthetic.txt"
        filepath = Path(output_dir) / filename
        
        # Save file (UTF-8 encoding)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(formatted)
        
        logger.info("synthetic_document_saved", filename=filename, topic=topic)
        return str(filepath)
    
    except Exception as e:
        logger.error("synthetic_document_save_error", title=title, error=str(e))
        return None
```

### Step 3: Identify Content Gaps

Before creating synthetic documents, identify gaps:

```python
def identify_content_gaps(
    scraped_topics: List[str],
    required_topics: List[str]
) -> List[str]:
    """
    Identify topics that are missing from scraped content.
    
    Args:
        scraped_topics: List of topics covered by scraped content
        required_topics: List of topics required for MVP
    
    Returns:
        List of missing topics
    """
    scraped_lower = [t.lower() for t in scraped_topics]
    missing = []
    
    for topic in required_topics:
        if topic.lower() not in scraped_lower:
            missing.append(topic)
    
    logger.info("content_gaps_identified", missing_count=len(missing), missing_topics=missing)
    return missing
```

### Step 4: Create Synthetic Documents

Example synthetic documents you might need:

#### Example 1: Policy Summary (where public docs incomplete)

```python
def create_policy_summary(
    policy_name: str,
    summary_points: List[str],
    assumptions: List[str]
) -> Dict[str, str]:
    """
    Create a synthetic policy summary document.
    
    Args:
        policy_name: Name of the policy
        summary_points: Key points about the policy
        assumptions: Assumptions made
    
    Returns:
        Document dictionary
    """
    content = f"""This document provides a summary of {policy_name} based on available information.

Key Points:
"""
    for i, point in enumerate(summary_points, 1):
        content += f"{i}. {point}\n"
    
    content += f"""
Note: This is a synthetic summary. For official policy details, please refer to ANZ's official documentation or contact ANZ directly.
"""
    
    return {
        "title": f"{policy_name} Summary",
        "content": content,
        "assumptions": assumptions,
        "topic": "policy"
    }
```

#### Example 2: Process Flow (where documentation missing)

```python
def create_process_flow(
    process_name: str,
    steps: List[str],
    assumptions: List[str]
) -> Dict[str, str]:
    """
    Create a synthetic process flow document.
    
    Args:
        process_name: Name of the process
        steps: Process steps
        assumptions: Assumptions made
    
    Returns:
        Document dictionary
    """
    content = f"""This document outlines the general process for {process_name}.

Process Steps:
"""
    for i, step in enumerate(steps, 1):
        content += f"Step {i}: {step}\n"
    
    content += f"""
Note: This is a synthetic process flow. Actual processes may vary. Please verify with ANZ for specific requirements.
"""
    
    return {
        "title": f"{process_name} Process",
        "content": content,
        "assumptions": assumptions,
        "topic": "process"
    }
```

#### Example 3: Compliance Guidelines (internal procedures)

```python
def create_compliance_guideline(
    guideline_name: str,
    guidelines: List[str],
    assumptions: List[str]
) -> Dict[str, str]:
    """
    Create a synthetic compliance guideline document.
    
    Args:
        guideline_name: Name of the guideline
        guidelines: List of guidelines
        assumptions: Assumptions made
    
    Returns:
        Document dictionary
    """
    content = f"""This document provides general compliance guidelines for {guideline_name}.

Guidelines:
"""
    for i, guideline in enumerate(guidelines, 1):
        content += f"{i}. {guideline}\n"
    
    content += f"""
Note: This is a synthetic guideline. For official compliance requirements, please refer to ANZ's official compliance documentation.
"""
    
    return {
        "title": f"{guideline_name} Compliance Guidelines",
        "content": content,
        "assumptions": assumptions,
        "topic": "compliance"
    }
```

### Step 5: Main Generator Function

```python
def generate_synthetic_documents(
    gap_topics: List[str],
    output_dir: str = "synthetic_docs"
) -> List[Dict[str, str]]:
    """
    Generate synthetic documents for identified gaps.
    
    Args:
        gap_topics: List of topics that need synthetic documents
        output_dir: Output directory
    
    Returns:
        List of document metadata dictionaries
    """
    generated_docs = []
    
    # Example: Generate documents for specific gaps
    # You should customize this based on actual gaps identified
    
    for topic in gap_topics:
        if topic.lower() == "account_closure_process":
            doc = create_process_flow(
                process_name="Account Closure",
                steps=[
                    "Contact ANZ customer service",
                    "Verify account ownership",
                    "Settle any outstanding balances",
                    "Complete closure request form",
                    "Receive confirmation"
                ],
                assumptions=[
                    "Standard account closure process applies",
                    "No special circumstances",
                    "All fees and charges are settled"
                ]
            )
            filepath = save_synthetic_document(
                title=doc["title"],
                content=doc["content"],
                assumptions=doc["assumptions"],
                topic=doc["topic"],
                output_dir=output_dir
            )
            if filepath:
                generated_docs.append({
                    **doc,
                    "filepath": filepath
                })
        
        # Add more topic-specific document generation as needed
    
    logger.info("synthetic_documents_generated", count=len(generated_docs))
    return generated_docs
```

### Step 6: Integration with Vector Store Setup

After generating synthetic documents, upload them to Vector Store:

```python
# This will be done in Task 6 (Vector Store Setup)
# But you can prepare the documents here

async def prepare_synthetic_documents_for_upload(
    synthetic_docs: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """
    Prepare synthetic documents for Vector Store upload.
    
    Args:
        synthetic_docs: List of synthetic document dictionaries
    
    Returns:
        List of documents ready for upload (with filepaths)
    """
    prepared = []
    
    for doc in synthetic_docs:
        prepared.append({
            "title": doc["title"],
            "url": f"synthetic://{doc['topic']}/{sanitize_filename(doc['title'])}",
            "content": doc["content"],
            "retrieval_date": datetime.now().strftime("%Y-%m-%d"),
            "content_type": "synthetic",
            "topic": doc.get("topic", "general"),
            "filepath": doc.get("filepath"),
            "assumptions": doc.get("assumptions", [])
        })
    
    return prepared
```

## Example Synthetic Documents

### Example 1: Account Closure Process

**When to create**: If public ANZ pages don't clearly explain the account closure process.

```python
doc = create_process_flow(
    process_name="Personal Account Closure",
    steps=[
        "Contact ANZ via phone, branch, or online banking",
        "Verify your identity and account ownership",
        "Ensure all transactions are cleared",
        "Settle any outstanding fees or charges",
        "Complete account closure request",
        "Receive written confirmation of closure"
    ],
    assumptions=[
        "Standard personal account closure process",
        "No joint account holders",
        "No pending transactions",
        "Account is in good standing"
    ]
)
```

### Example 2: Policy Summary

**When to create**: If a policy exists but public documentation is incomplete.

```python
doc = create_policy_summary(
    policy_name="Overdraft Policy",
    summary_points=[
        "Overdraft protection may be available for eligible accounts",
        "Fees may apply for overdraft usage",
        "Approval is subject to credit assessment",
        "Terms and conditions apply"
    ],
    assumptions=[
        "General policy information based on standard banking practices",
        "Specific terms may vary by account type",
        "Eligibility criteria not fully documented in public sources"
    ]
)
```

## Best Practices

### 1. Be Explicit and Narrow
- ✅ **Good**: "Account Closure Process - Step 1: Contact ANZ"
- ❌ **Bad**: "Banking Procedures"

### 2. Document All Assumptions
- ✅ List every assumption made
- ✅ Be transparent about limitations
- ✅ Note when information is inferred

### 3. Use Clear Labeling
- ✅ Always include "SYNTHETIC CONTENT" in title
- ✅ Include "Label: SYNTHETIC" in metadata
- ✅ Set content_type to "synthetic"

### 4. Keep It Minimal
- ✅ Only create what's absolutely necessary
- ✅ Prefer to leave gaps rather than create misleading content
- ✅ Update when real content becomes available

### 5. Mark in Responses
- ✅ Response generator should detect synthetic content
- ✅ Add disclaimer: "Note: This information is based on synthetic content and may not reflect official ANZ policy."

## Success Criteria

- [ ] Synthetic documents clearly labeled with "SYNTHETIC CONTENT"
- [ ] All assumptions documented
- [ ] Documents saved as `.txt` files with proper format
- [ ] Documents uploaded to OpenAI Files API (via Task 6)
- [ ] Documents attached to appropriate Vector Store (via Task 6)
- [ ] Marked in metadata as "synthetic" (content_type field)
- [ ] Format matches specification (see DETAILED_PLAN.md Section 8.2)
- [ ] Documents are narrow and explicit in scope
- [ ] Only created when necessary (gaps identified)

## Testing

### Manual Testing

1. **Test Document Generation**:
   ```python
   from knowledge.synthetic_generator import create_process_flow, save_synthetic_document
   
   doc = create_process_flow(
       process_name="Test Process",
       steps=["Step 1", "Step 2"],
       assumptions=["Assumption 1"]
   )
   
   filepath = save_synthetic_document(
       title=doc["title"],
       content=doc["content"],
       assumptions=doc["assumptions"],
       topic="test"
   )
   print(f"Saved to: {filepath}")
   ```

2. **Verify File Format**:
   - Check that file includes "SYNTHETIC CONTENT" in title
   - Verify "Label: SYNTHETIC" is present
   - Check that assumptions are listed
   - Verify UTF-8 encoding

3. **Test Integration**:
   - Generate synthetic documents
   - Upload to Vector Store (Task 6)
   - Verify they're marked as "synthetic" in database
   - Test retrieval to ensure they're accessible

## Integration Points

- **Task 4 (Web Scraping)**: Identify gaps by comparing scraped content to required topics
- **Task 6 (Vector Store Setup)**: Upload synthetic documents to Vector Store
- **Task 11 (Response Generator)**: Detect synthetic content and add disclaimers

## When to Skip This Task

You can skip this task if:
- ✅ All required content is available from public ANZ pages
- ✅ No significant gaps identified
- ✅ MVP can function without synthetic content

**Recommendation**: Start with public content only. Add synthetic documents only if you identify specific, critical gaps during testing.

## Reference

- **DETAILED_PLAN.md** Section 8.2 (Synthetic Document Generation)
- **TASK_BREAKDOWN.md** Task 7
- **Task 6 Guide**: For uploading synthetic documents to Vector Store

## Notes

- Synthetic documents are a last resort - prefer real content
- Always be transparent about synthetic content
- Update or remove synthetic documents when real content becomes available
- Keep synthetic documents minimal and focused
- Document assumptions thoroughly
