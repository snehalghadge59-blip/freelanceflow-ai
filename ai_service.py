"""
ai_service.py - Local Ollama + Gemma integration for AI invoice data extraction.
Validates extracted output strictly using Pydantic.
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import requests
from pydantic import BaseModel, Field, field_validator

from database import EXPENSE_CATEGORIES

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_GEMMA_MODEL = "gemma2:2b"


class OllamaServiceError(Exception):
    """Custom exception raised when Ollama service fails or is unreachable."""
    pass


class InvoiceExtractionResult(BaseModel):
    """Pydantic model representing structured invoice fields extracted by Gemma."""
    merchant: str = Field(default="", description="Name of vendor, supplier, or merchant")
    invoice_number: Optional[str] = Field(default=None, description="Invoice or receipt number")
    date: Optional[str] = Field(default=None, description="Invoice date in YYYY-MM-DD format")
    currency: str = Field(default="USD", description="Currency code (e.g., USD, EUR, GBP, CAD)")
    subtotal: float = Field(default=0.0, description="Subtotal amount before tax")
    tax: float = Field(default=0.0, description="Tax or VAT amount")
    total: float = Field(default=0.0, description="Total amount paid or due")
    category: str = Field(default="Other", description="Expense category from standard list")
    notes: Optional[str] = Field(default=None, description="Short summary or itemization description")

    @field_validator("currency", mode="before")
    @classmethod
    def clean_currency(cls, v: Any) -> str:
        if not v or not isinstance(v, str):
            return "USD"
        cleaned = v.strip().upper()
        # Common symbol mappings
        symbol_map = {"$": "USD", "€": "EUR", "£": "GBP", "₹": "INR", "¥": "JPY", "C$": "CAD", "A$": "AUD"}
        return symbol_map.get(cleaned, cleaned[:5])

    @field_validator("subtotal", "tax", "total", mode="before")
    @classmethod
    def clean_float(cls, v: Any) -> float:
        if v is None or v == "":
            return 0.0
        if isinstance(v, (int, float)):
            return max(0.0, round(float(v), 2))
        if isinstance(v, str):
            # Strip currency symbols and whitespace
            cleaned_str = re.sub(r"[^\d.-]", "", v)
            try:
                val = float(cleaned_str)
                return max(0.0, round(val, 2))
            except ValueError:
                return 0.0
        return 0.0

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, v: Any) -> Optional[str]:
        if not v or not isinstance(v, str):
            return None
        v_clean = v.strip()
        # Try common formats and convert to YYYY-MM-DD
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%m-%d-%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(v_clean, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # Simple regex fallback if it looks like YYYY-MM-DD
        match = re.search(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", v_clean)
        if match:
            y, m, d = match.groups()
            return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"

        return v_clean or None

    @field_validator("category", mode="before")
    @classmethod
    def match_category(cls, v: Any) -> str:
        if not v or not isinstance(v, str):
            return "Other"
        v_lower = v.strip().lower()
        for cat in EXPENSE_CATEGORIES:
            if v_lower in cat.lower() or cat.lower() in v_lower:
                return cat
        return "Other"


def check_ollama_status(base_url: str = DEFAULT_OLLAMA_URL) -> Tuple[bool, List[str], str]:
    """
    Pings local Ollama instance and returns available models.
    Returns: (is_online, available_models, status_message)
    """
    clean_url = base_url.rstrip("/")
    try:
        resp = requests.get(f"{clean_url}/api/tags", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            return True, models, "Ollama service is connected and healthy."
        return False, [], f"Ollama returned HTTP status {resp.status_code}."
    except requests.exceptions.ConnectionError:
        return False, [], f"Could not connect to Ollama at {clean_url}. Is Ollama running?"
    except requests.exceptions.Timeout:
        return False, [], f"Connection to Ollama at {clean_url} timed out."
    except Exception as e:
        return False, [], f"Error connecting to Ollama: {str(e)}"


def extract_invoice_data(
    raw_text: str,
    model: str = DEFAULT_GEMMA_MODEL,
    base_url: str = DEFAULT_OLLAMA_URL,
    timeout: int = 90,
) -> InvoiceExtractionResult:
    """
    Sends raw invoice text to Ollama running Gemma and parses the structured JSON output.
    Raises OllamaServiceError if the server is unreachable or output cannot be parsed.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Cannot extract from empty document text.")

    clean_url = base_url.rstrip("/")

    categories_list = ", ".join(f'"{c}"' for c in EXPENSE_CATEGORIES)

    prompt = f"""You are a financial receipt and invoice data extractor for freelancers.
Extract the following details from this invoice/receipt text and output ONLY valid JSON without markdown formatting or code blocks:
- "merchant": Name of the vendor, business, or merchant
- "invoice_number": Invoice or receipt ID (or null if missing)
- "date": Invoice or transaction date in YYYY-MM-DD format (or null if missing)
- "currency": ISO currency code like USD, EUR, GBP, CAD (default to USD)
- "subtotal": Numeric subtotal before tax (e.g. 45.00)
- "tax": Numeric tax or VAT amount (e.g. 4.50)
- "total": Final total amount paid or due (e.g. 49.50)
- "category": Choose the single best match strictly from this list: [{categories_list}]
- "notes": Short 1-sentence description of items purchased

Document Text:
\"\"\"
{raw_text[:4000]}
\"\"\"

Return ONLY valid JSON matching this schema:
{{
  "merchant": "...",
  "invoice_number": "...",
  "date": "YYYY-MM-DD",
  "currency": "USD",
  "subtotal": 0.0,
  "tax": 0.0,
  "total": 0.0,
  "category": "...",
  "notes": "..."
}}
"""

    payload = {
        "model": model,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.1,
        },
    }

    try:
        response = requests.post(
            f"{clean_url}/api/generate",
            json=payload,
            timeout=timeout,
        )
    except requests.exceptions.ConnectionError:
        raise OllamaServiceError(
            f"Ollama is not running at {clean_url}. Please launch Ollama and run `ollama run {model}`."
        )
    except requests.exceptions.Timeout:
        raise OllamaServiceError(
            f"Extraction request timed out after {timeout} seconds. Your local model may be busy or downloading."
        )
    except Exception as e:
        raise OllamaServiceError(f"Failed to communicate with Ollama: {str(e)}")

    if response.status_code != 200:
        error_msg = response.text
        try:
            error_msg = response.json().get("error", response.text)
        except Exception:
            pass
        raise OllamaServiceError(f"Ollama error (HTTP {response.status_code}): {error_msg}")

    try:
        response_data = response.json()
        raw_output = response_data.get("response", "").strip()
        # Clean any accidental code block markers
        raw_output = re.sub(r"^```json\s*", "", raw_output)
        raw_output = re.sub(r"^```\s*", "", raw_output)
        raw_output = re.sub(r"\s*```$", "", raw_output)

        parsed_json = json.loads(raw_output)
        result = InvoiceExtractionResult.model_validate(parsed_json)
        return result
    except (json.JSONDecodeError, Exception) as e:
        raise OllamaServiceError(
            f"Failed to parse model response into structured JSON: {str(e)}. "
            f"Raw model response: {response.text[:300]}"
        )
