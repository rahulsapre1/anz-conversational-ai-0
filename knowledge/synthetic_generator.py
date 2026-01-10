"""
Synthetic Document Generator - Create synthetic documents for banker-facing content.
"""
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

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
    import re
    
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
    Save synthetic document to .md file (for consistency with scraped docs).
    
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
        filename = f"{sanitized_title}_synthetic.md"
        filepath = Path(output_dir) / filename
        
        # Save file (UTF-8 encoding)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(formatted)
        
        logger.info("synthetic_document_saved", filename=filename, topic=topic)
        return str(filepath)
    
    except Exception as e:
        logger.error("synthetic_document_save_error", title=title, error=str(e))
        return None


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
    content = f"""This document provides a summary of {policy_name} based on available information and standard banking practices.

## Overview

{policy_name} outlines the key terms, conditions, and procedures relevant to this policy area.

## Key Points:
"""
    for i, point in enumerate(summary_points, 1):
        content += f"{i}. {point}\n"
    
    content += f"""
## Important Notes

**This is a synthetic summary. For official policy details, please refer to ANZ's official documentation or contact ANZ's policy team directly.**

Bankers should always verify policy information with official sources before providing guidance to customers. This document is provided as a reference guide only and should not be considered authoritative.
"""
    
    return {
        "title": f"{policy_name} Summary",
        "content": content,
        "assumptions": assumptions,
        "topic": "policy"
    }


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

## Process Overview

The following steps provide a general framework for {process_name}. Actual implementation may vary based on specific circumstances and system requirements.

## Process Steps:
"""
    for i, step in enumerate(steps, 1):
        content += f"**Step {i}**: {step}\n\n"
    
    content += f"""## Important Notes

**This is a synthetic process flow. Actual processes may vary based on:**
- Specific account types or products
- Customer circumstances
- System capabilities and configurations
- Regulatory requirements at the time of processing

Please verify with ANZ's official process documentation or system guides for specific requirements and current procedures.
"""
    
    return {
        "title": f"{process_name} Process",
        "content": content,
        "assumptions": assumptions,
        "topic": "process"
    }


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

## Overview

When handling queries related to {guideline_name}, bankers should follow these general guidelines. These are based on standard banking compliance practices.

## Guidelines:
"""
    for i, guideline in enumerate(guidelines, 1):
        content += f"{i}. {guideline}\n"
    
    content += f"""
## Important Notes

**This is a synthetic guideline. For official compliance requirements, please refer to:**
- ANZ's official compliance documentation
- Internal compliance training materials
- Regulatory guidance from relevant authorities (e.g., ASIC, APRA)
- ANZ's legal and compliance team

Bankers must ensure they are using current, official compliance guidance when assisting customers. This document should not replace official compliance training or documentation.
"""
    
    return {
        "title": f"{guideline_name} Compliance Guidelines",
        "content": content,
        "assumptions": assumptions,
        "topic": "compliance"
    }


def create_product_comparison(
    comparison_name: str,
    products: Dict[str, List[str]],
    assumptions: List[str]
) -> Dict[str, str]:
    """
    Create a synthetic product comparison document.
    
    Args:
        comparison_name: Name/title of the comparison
        products: Dictionary of product names to their features/characteristics
        assumptions: Assumptions made
    
    Returns:
        Document dictionary
    """
    content = f"""This document provides a high-level comparison of {comparison_name} for reference purposes.

## Overview

This comparison highlights key differences and similarities between the products/services listed below. This information should be used as a starting point for discussions with customers.

## Product Comparison:

"""
    for product_name, features in products.items():
        content += f"### {product_name}\n\n"
        for feature in features:
            content += f"- {feature}\n"
        content += "\n"
    
    content += f"""## Important Notes

**This is a synthetic product comparison. For accurate, current product information:**
- Refer to official ANZ product documentation
- Use ANZ's product comparison tools (if available)
- Consult with product specialists for detailed questions
- Verify current features, fees, and eligibility criteria

Product features, fees, and eligibility criteria may change. Always verify current information before providing product comparisons to customers.
"""
    
    return {
        "title": f"{comparison_name} Comparison",
        "content": content,
        "assumptions": assumptions,
        "topic": "product_comparison"
    }


def create_fee_structure_document(
    fee_category: str,
    fee_items: Dict[str, str],
    assumptions: List[str]
) -> Dict[str, str]:
    """
    Create a synthetic fee structure document.
    
    Args:
        fee_category: Category of fees (e.g., "Account Fees", "Transaction Fees")
        fee_items: Dictionary of fee name to description
        assumptions: Assumptions made
    
    Returns:
        Document dictionary
    """
    content = f"""This document provides a reference guide for {fee_category}.

## Overview

The following information outlines typical fees and charges that may apply in this category. Actual fees may vary based on account type, customer relationship, and current promotions.

## Fee Structure:

"""
    for fee_name, fee_description in fee_items.items():
        content += f"### {fee_name}\n\n{fee_description}\n\n"
    
    content += f"""## Important Notes

**This is a synthetic fee structure guide. For accurate fee information:**
- Refer to official ANZ fee schedules and pricing guides
- Check the customer's specific account type and terms
- Verify current fee structures in ANZ's systems
- Consult with pricing specialists for complex fee questions

Fees and charges are subject to change. Always verify current fee information from official sources before providing guidance to customers. Fee waivers, discounts, or promotional pricing may apply in specific circumstances.
"""
    
    return {
        "title": f"{fee_category} Fee Structure",
        "content": content,
        "assumptions": assumptions,
        "topic": "fee_structure"
    }


def create_eligibility_criteria_document(
    product_or_service: str,
    criteria: List[str],
    assumptions: List[str]
) -> Dict[str, str]:
    """
    Create a synthetic eligibility criteria document.
    
    Args:
        product_or_service: Name of product or service
        criteria: List of eligibility criteria
        assumptions: Assumptions made
    
    Returns:
        Document dictionary
    """
    content = f"""This document outlines general eligibility criteria for {product_or_service}.

## Overview

The following criteria provide general guidance on eligibility requirements. Actual eligibility is determined by ANZ's credit assessment processes and may vary based on individual circumstances.

## Eligibility Criteria:

"""
    for i, criterion in enumerate(criteria, 1):
        content += f"{i}. {criterion}\n"
    
    content += f"""## Important Notes

**This is a synthetic eligibility guide. For official eligibility requirements:**
- Refer to ANZ's official product eligibility documentation
- Use ANZ's eligibility checking systems or tools
- Consult with credit assessment teams for complex cases
- Verify current eligibility criteria as requirements may change

Eligibility is subject to credit assessment and approval. Meeting general criteria does not guarantee approval. Final eligibility decisions are made by ANZ's credit assessment team based on comprehensive evaluation of individual circumstances.
"""
    
    return {
        "title": f"{product_or_service} Eligibility Criteria",
        "content": content,
        "assumptions": assumptions,
        "topic": "eligibility"
    }


def create_compliance_phrasing_guide(
    topic: str,
    phrases: Dict[str, List[str]],
    assumptions: List[str]
) -> Dict[str, str]:
    """
    Create a synthetic compliance phrasing guide.
    
    Args:
        topic: Topic area for the phrasing guide
        phrases: Dictionary of situation/context to list of appropriate phrases
        assumptions: Assumptions made
    
    Returns:
        Document dictionary
    """
    content = f"""This document provides guidance on compliant language and phrasing for {topic}.

## Overview

When discussing {topic} with customers, it's important to use language that is clear, compliant, and appropriate. This guide provides example phrases that align with standard banking compliance practices.

## Phrasing Guidelines:

"""
    for situation, phrase_list in phrases.items():
        content += f"### {situation}\n\n"
        content += "**Appropriate phrases:**\n\n"
        for phrase in phrase_list:
            content += f"- \"{phrase}\"\n"
        content += "\n"
    
    content += f"""## Important Notes

**This is a synthetic phrasing guide. For official compliance language:**
- Refer to ANZ's official compliance and communication guidelines
- Use approved scripts and templates provided by ANZ
- Consult with compliance or legal teams for sensitive topics
- Stay updated on regulatory guidance related to customer communications

Language requirements may vary by jurisdiction and regulatory context. Always ensure compliance with current ANZ policies and regulatory requirements. This guide should not replace official compliance training.
"""
    
    return {
        "title": f"{topic} Compliance Phrasing Guide",
        "content": content,
        "assumptions": assumptions,
        "topic": "compliance_phrasing"
    }


def generate_banker_synthetic_documents(
    output_dir: str = "synthetic_docs"
) -> List[Dict[str, str]]:
    """
    Generate synthetic documents for banker-facing content gaps.
    
    Args:
        output_dir: Output directory for generated documents
    
    Returns:
        List of generated document metadata dictionaries
    """
    generated_docs = []
    
    # 1. Fee Structure Document
    logger.info("generating_fee_structure_doc")
    fee_doc = create_fee_structure_document(
        fee_category="Account and Transaction Fees",
        fee_items={
            "Monthly Account Fee": "A monthly fee may apply to certain account types. Fee waivers may be available for customers meeting specific criteria such as minimum deposit amounts or maintaining certain account balances.",
            "Transaction Fees": "Fees may apply for certain types of transactions, including international transfers, currency conversion, and some payment methods. Standard domestic transactions are typically fee-free for most account types.",
            "Overdraft Fees": "Overdraft fees may apply if an account goes into overdraft without approved overdraft protection. Fees vary based on the account type and overdraft amount.",
            "ATM Fees": "ANZ ATMs are typically free for ANZ customers. Fees may apply when using non-ANZ ATMs or international ATMs. Third-party ATM operators may also charge their own fees."
        },
        assumptions=[
            "General fee structures based on standard banking practices",
            "Fee amounts and structures vary by account type",
            "Fee waivers and discounts may be available based on customer relationships",
            "Specific fee amounts should be verified from official sources"
        ]
    )
    filepath = save_synthetic_document(
        title=fee_doc["title"],
        content=fee_doc["content"],
        assumptions=fee_doc["assumptions"],
        topic=fee_doc["topic"],
        output_dir=output_dir
    )
    if filepath:
        generated_docs.append({**fee_doc, "filepath": filepath})
    
    # 2. Eligibility Criteria Document
    logger.info("generating_eligibility_doc")
    eligibility_doc = create_eligibility_criteria_document(
        product_or_service="Personal Credit Card Application",
        criteria=[
            "Applicant must be at least 18 years of age",
            "Applicant must be an Australian resident or hold an eligible visa",
            "Applicant must meet minimum income requirements (varies by card type)",
            "Applicant must have a good credit history",
            "Applicant must provide proof of identity and income",
            "Existing ANZ customers may have streamlined application processes"
        ],
        assumptions=[
            "General eligibility criteria based on standard credit card practices",
            "Specific income requirements vary by card product type",
            "Credit assessment considers multiple factors beyond listed criteria",
            "Eligibility is subject to ANZ's credit assessment and approval processes"
        ]
    )
    filepath = save_synthetic_document(
        title=eligibility_doc["title"],
        content=eligibility_doc["content"],
        assumptions=eligibility_doc["assumptions"],
        topic=eligibility_doc["topic"],
        output_dir=output_dir
    )
    if filepath:
        generated_docs.append({**eligibility_doc, "filepath": filepath})
    
    # 3. Process Flow Document - Account Closure
    logger.info("generating_account_closure_process")
    process_doc = create_process_flow(
        process_name="Customer Account Closure Request",
        steps=[
            "Verify customer identity and account ownership through standard authentication procedures",
            "Review account status to ensure no pending transactions or outstanding obligations",
            "Confirm any direct debits or automatic payments are cancelled or redirected",
            "Settle any outstanding fees, charges, or balances",
            "Complete account closure request form or initiate closure through appropriate system",
            "Provide customer with written confirmation of closure request",
            "Process closure after all transactions have cleared and final statements are issued"
        ],
        assumptions=[
            "Standard account closure process for personal accounts",
            "Process may vary for joint accounts or business accounts",
            "Some account types may have specific closure requirements or notice periods",
            "Final account statements and closure confirmation are typically provided"
        ]
    )
    filepath = save_synthetic_document(
        title=process_doc["title"],
        content=process_doc["content"],
        assumptions=process_doc["assumptions"],
        topic=process_doc["topic"],
        output_dir=output_dir
    )
    if filepath:
        generated_docs.append({**process_doc, "filepath": filepath})
    
    # 4. Compliance Phrasing Guide
    logger.info("generating_compliance_phrasing")
    phrasing_doc = create_compliance_phrasing_guide(
        topic="Fee Disclosure and Product Recommendations",
        phrases={
            "When discussing fees": [
                "Fees and charges may apply depending on your account type and usage",
                "I can provide general information about typical fees, but your specific fees will be outlined in your account terms and conditions",
                "Some fees may be waived if you meet certain criteria",
                "Would you like me to check your specific account details to confirm the fees that apply to you?"
            ],
            "When providing product information": [
                "This product may be suitable for customers who [specific criteria]",
                "I can provide general information, but I recommend reviewing the Product Disclosure Statement (PDS) for full details",
                "Each customer's situation is unique, and I'd recommend discussing your specific needs with a qualified advisor",
                "This information is general in nature and doesn't constitute financial advice"
            ],
            "When discussing eligibility": [
                "Eligibility is subject to credit assessment and approval",
                "Meeting these criteria doesn't guarantee approval, as we assess each application individually",
                "I can provide general guidance, but the final decision is made through our credit assessment process",
                "Would you like me to help you check your eligibility, or do you have questions about the application process?"
            ]
        },
        assumptions=[
            "Phrases align with standard banking compliance practices",
            "Specific wording requirements may vary based on regulatory context",
            "These phrases should be adapted based on actual customer circumstances",
            "Compliance language should always align with ANZ's official guidelines"
        ]
    )
    filepath = save_synthetic_document(
        title=phrasing_doc["title"],
        content=phrasing_doc["content"],
        assumptions=phrasing_doc["assumptions"],
        topic=phrasing_doc["topic"],
        output_dir=output_dir
    )
    if filepath:
        generated_docs.append({**phrasing_doc, "filepath": filepath})
    
    # 5. Policy Summary - Overdraft Policy
    logger.info("generating_overdraft_policy")
    policy_doc = create_policy_summary(
        policy_name="Overdraft and Account Overdraft Policy",
        summary_points=[
            "Overdraft protection may be available for eligible accounts subject to credit assessment",
            "Unarranged overdrafts may incur fees and charges",
            "Arranged overdraft facilities are subject to approval and may have ongoing fees",
            "Overdraft limits and terms are determined based on credit assessment",
            "Customers should monitor their account balance to avoid unarranged overdrafts",
            "Overdraft facilities may be reviewed and adjusted based on account usage and credit assessment"
        ],
        assumptions=[
            "General policy information based on standard overdraft practices",
            "Specific terms and conditions vary by account type and customer circumstances",
            "Fee structures and interest rates apply to overdraft facilities",
            "Policy details should be verified from official ANZ policy documentation"
        ]
    )
    filepath = save_synthetic_document(
        title=policy_doc["title"],
        content=policy_doc["content"],
        assumptions=policy_doc["assumptions"],
        topic=policy_doc["topic"],
        output_dir=output_dir
    )
    if filepath:
        generated_docs.append({**policy_doc, "filepath": filepath})
    
    # 6. Product Comparison - Transaction Accounts
    logger.info("generating_product_comparison")
    comparison_doc = create_product_comparison(
        comparison_name="ANZ Personal Transaction Accounts",
        products={
            "ANZ Access Advantage": [
                "Monthly account fee may apply",
                "Free electronic transactions",
                "Access to ANZ Internet Banking and mobile app",
                "ATM access at ANZ and selected partner ATMs",
                "Optional overdraft facility available (subject to approval)"
            ],
            "ANZ Access Basic": [
                "Lower or no monthly account fee",
                "Basic transaction features",
                "Access to ANZ Internet Banking and mobile app",
                "Suitable for customers with simpler banking needs",
                "May have limitations on certain transaction types"
            ]
        },
        assumptions=[
            "Product features based on general account information",
            "Specific features, fees, and eligibility criteria vary by product",
            "Product offerings and features may change over time",
            "Detailed comparison should be made using official ANZ product information"
        ]
    )
    filepath = save_synthetic_document(
        title=comparison_doc["title"],
        content=comparison_doc["content"],
        assumptions=comparison_doc["assumptions"],
        topic=comparison_doc["topic"],
        output_dir=output_dir
    )
    if filepath:
        generated_docs.append({**comparison_doc, "filepath": filepath})
    
    logger.info("synthetic_documents_generated", count=len(generated_docs))
    return generated_docs
