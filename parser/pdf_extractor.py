"""
PDF text extraction using pdfplumber.
Step 1 of the two-step parsing pipeline: PDF → raw text.
"""

import logging
import pdfplumber

logger = logging.getLogger(__name__)

def extract_text(pdf_path: str) -> str:
    """
    Extracts raw text from a PDF file.
    
    Reads the PDF page by page and joins the text using a page break marker.
    This provides clear demarcation of pages which helps the LLM maintain context.
    
    Returns an empty string if the PDF is corrupt, encrypted, or unreadable.
    """
    try:
        pages_text = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
        
        # Join pages with a clear marker
        return "\n\n--- Page Break ---\n\n".join(pages_text)
    
    except Exception as e:
        logger.warning(f"Failed to extract text from {pdf_path}. Reason: {str(e)}")
        return ""
