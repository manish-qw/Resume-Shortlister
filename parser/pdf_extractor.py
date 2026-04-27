"""
PDF text extraction using pdfplumber.
Step 1 of the two-step parsing pipeline: PDF → raw text.
"""
# - extract_text(pdf_path: str) -> str
# - Page-by-page extraction with page break markers
# - Error handling for corrupt/encrypted PDFs
