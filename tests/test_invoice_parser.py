"""
Unit tests for invoice_parser.py (Hash computation, PyMuPDF extraction, and error handling)
"""

import hashlib
import pytest
import invoice_parser

try:
    import pymupdf as fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    try:
        import fitz
        PYMUPDF_AVAILABLE = True
    except ImportError:
        PYMUPDF_AVAILABLE = False


def test_compute_file_hash():
    sample_content = b"FreelanceFlow AI Test Invoice Content"
    expected = hashlib.sha256(sample_content).hexdigest()
    assert invoice_parser.compute_file_hash(sample_content) == expected


def test_pdf_extraction_real_or_mock():
    if not PYMUPDF_AVAILABLE:
        pytest.skip("PyMuPDF not installed in this environment")

    # Generate a lightweight in-memory PDF using PyMuPDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "INVOICE #INV-8891\nMerchant: Acme Cloud Services\nTotal: $149.00\nDate: 2026-10-15")
    pdf_bytes = doc.tobytes()
    doc.close()

    extracted = invoice_parser.extract_text_from_pdf(pdf_bytes)
    assert "Acme Cloud Services" in extracted
    assert "INV-8891" in extracted
    assert "$149.00" in extracted


def test_unsupported_file_extension():
    with pytest.raises(ValueError) as excinfo:
        invoice_parser.parse_document("spreadsheet.xlsx", b"fake binary data")
    assert "Unsupported file format" in str(excinfo.value)
