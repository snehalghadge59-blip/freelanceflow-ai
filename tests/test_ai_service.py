"""
Unit tests for ai_service.py (Pydantic validation, schema normalization, and error handling)
"""

import pytest
from pydantic import ValidationError

import ai_service
from ai_service import InvoiceExtractionResult, check_ollama_status


def test_pydantic_clean_currency():
    result1 = InvoiceExtractionResult(merchant="Test Corp", total=100.0, currency="$")
    assert result1.currency == "USD"

    result2 = InvoiceExtractionResult(merchant="Test Corp", total=100.0, currency="€")
    assert result2.currency == "EUR"

    result3 = InvoiceExtractionResult(merchant="Test Corp", total=100.0, currency="gbp")
    assert result3.currency == "GBP"


def test_pydantic_clean_floats():
    result = InvoiceExtractionResult(
        merchant="Stripe",
        subtotal="$120.50",
        tax="12.05",
        total="$132.55",
    )
    assert result.subtotal == 120.50
    assert result.tax == 12.05
    assert result.total == 132.55


def test_pydantic_date_normalization():
    # Slash format DD/MM/YYYY
    res1 = InvoiceExtractionResult(merchant="Acme", date="15/10/2026", total=10.0)
    assert res1.date == "2026-10-15"

    # Already YYYY-MM-DD
    res2 = InvoiceExtractionResult(merchant="Acme", date="2026-09-01", total=10.0)
    assert res2.date == "2026-09-01"

    # Month name format
    res3 = InvoiceExtractionResult(merchant="Acme", date="October 12, 2026", total=10.0)
    assert res3.date == "2026-10-12"


def test_pydantic_category_matching():
    res1 = InvoiceExtractionResult(merchant="Vercel", total=20.0, category="hosting")
    assert res1.category == "Hosting & Cloud"

    res2 = InvoiceExtractionResult(merchant="Slack", total=15.0, category="Software")
    assert res2.category == "Software & Subscriptions"

    res3 = InvoiceExtractionResult(merchant="Unknown", total=5.0, category="completely random")
    assert res3.category == "Other"


def test_ollama_status_offline_graceful():
    # Connecting to non-existent port should return gracefully without crashing
    online, models, msg = check_ollama_status("http://127.0.0.1:59999")
    assert online is False
    assert models == []
    assert "Could not connect" in msg or "Error" in msg
