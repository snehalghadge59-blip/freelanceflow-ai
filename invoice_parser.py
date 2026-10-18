"""
invoice_parser.py - Text extraction and document parsing for invoices & receipts.
Supports PyMuPDF for native PDF text extraction and pytesseract for image OCR.
"""

import hashlib
import io
import os
import shutil
from typing import Dict, Optional, Tuple

try:
    import pymupdf as fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    try:
        import fitz
        PYMUPDF_AVAILABLE = True
    except ImportError:
        PYMUPDF_AVAILABLE = False

try:
    from PIL import Image
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False


def compute_file_hash(file_bytes: bytes) -> str:
    """Computes SHA-256 digest of file content for duplicate invoice detection."""
    hasher = hashlib.sha256()
    hasher.update(file_bytes)
    return hasher.hexdigest()


def find_tesseract_binary() -> Optional[str]:
    """Detects if tesseract binary is installed or configured."""
    # 1. Check environment variable override
    env_path = os.environ.get("TESSERACT_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    # 2. Check if tesseract is in system PATH
    which_path = shutil.which("tesseract")
    if which_path:
        return which_path

    # 3. Check common Windows installation paths
    common_win_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
    ]
    for p in common_win_paths:
        if os.path.exists(p):
            return p

    return None


def is_ocr_available() -> Tuple[bool, str]:
    """Checks if image OCR is currently supported on this machine."""
    if not PYTESSERACT_AVAILABLE:
        return False, "pytesseract or Pillow Python library is not installed."
    tess_bin = find_tesseract_binary()
    if not tess_bin:
        return False, (
            "Tesseract OCR executable was not found on your system. "
            "Please install Tesseract OCR (e.g. from UB-Mannheim/tesseract/wiki) or use native PDF files."
        )
    return True, f"Tesseract ready: {tess_bin}"


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts text content from a PDF document using PyMuPDF."""
    if not PYMUPDF_AVAILABLE:
        raise RuntimeError("PyMuPDF (fitz) is not installed. Please run `pip install pymupdf`.")

    extracted_pages = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text and text.strip():
                extracted_pages.append(f"--- Page {page_num + 1} ---\n{text.strip()}")
    finally:
        doc.close()

    full_text = "\n\n".join(extracted_pages).strip()
    return full_text


def extract_text_from_image(image_bytes: bytes) -> str:
    """Extracts text from an image (PNG, JPG) using pytesseract."""
    can_ocr, reason = is_ocr_available()
    if not can_ocr:
        raise RuntimeError(reason)

    tess_bin = find_tesseract_binary()
    if tess_bin:
        pytesseract.pytesseract.tesseract_cmd = tess_bin

    image = Image.open(io.BytesIO(image_bytes))
    # Convert image to RGB if needed
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    text = pytesseract.image_to_string(image)
    return text.strip()


def parse_document(file_name: str, file_bytes: bytes) -> Dict[str, str]:
    """
    Parses an uploaded invoice file (PDF or Image) and returns text and metadata.
    Returns dict: {'text': ..., 'method': ..., 'hash': ...}
    """
    file_hash = compute_file_hash(file_bytes)
    ext = os.path.splitext(file_name)[1].lower()

    if ext == ".pdf":
        raw_text = extract_text_from_pdf(file_bytes)
        method = "PyMuPDF (Native PDF Extraction)"
    elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
        raw_text = extract_text_from_image(file_bytes)
        method = "Tesseract OCR (Image Extraction)"
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Please upload a PDF, PNG, or JPG document.")

    return {
        "text": raw_text,
        "method": method,
        "hash": file_hash,
        "file_name": file_name,
    }
