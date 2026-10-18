"""
Unit tests for database.py (SQLite operations, duplicate hash detection, parameterized queries)
"""

import os
import tempfile
import pytest

import database


@pytest.fixture
def temp_db():
    """Creates an isolated temporary sqlite database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    database.init_db(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_init_and_add_expense(temp_db):
    exp_id = database.add_expense(
        merchant="GitHub",
        invoice_number="GH-1234",
        date="2026-10-01",
        currency="USD",
        subtotal=19.00,
        tax=0.00,
        total=19.00,
        category="Software & Subscriptions",
        file_hash="test_github_sha256",
        notes="Copilot subscription",
        db_path=temp_db,
    )
    assert exp_id > 0

    record = database.get_expense(exp_id, db_path=temp_db)
    assert record is not None
    assert record["merchant"] == "GitHub"
    assert record["invoice_number"] == "GH-1234"
    assert record["total"] == 19.00
    assert record["currency"] == "USD"
    assert record["category"] == "Software & Subscriptions"


def test_duplicate_hash_detection(temp_db):
    test_hash = "abcdef1234567890"
    assert database.check_duplicate_hash(test_hash, db_path=temp_db) is None

    database.add_expense(
        merchant="Adobe",
        invoice_number="AD-999",
        date="2026-10-05",
        currency="USD",
        subtotal=54.99,
        tax=4.40,
        total=59.39,
        category="Software & Subscriptions",
        file_hash=test_hash,
        db_path=temp_db,
    )

    duplicate = database.check_duplicate_hash(test_hash, db_path=temp_db)
    assert duplicate is not None
    assert duplicate["merchant"] == "Adobe"
    assert duplicate["total"] == 59.39


def test_update_and_delete_expense(temp_db):
    exp_id = database.add_expense(
        merchant="AWS",
        invoice_number="INV-1",
        date="2026-10-10",
        currency="USD",
        subtotal=20.0,
        tax=2.0,
        total=22.0,
        category="Hosting & Cloud",
        db_path=temp_db,
    )

    # Update
    updated = database.update_expense(
        expense_id=exp_id,
        merchant="AWS Web Services",
        invoice_number="INV-1-MOD",
        date="2026-10-11",
        currency="USD",
        subtotal=25.0,
        tax=2.5,
        total=27.5,
        category="Hosting & Cloud",
        notes="Adjusted bill",
        db_path=temp_db,
    )
    assert updated is True

    record = database.get_expense(exp_id, db_path=temp_db)
    assert record["merchant"] == "AWS Web Services"
    assert record["total"] == 27.5

    # Delete
    deleted = database.delete_expense(exp_id, db_path=temp_db)
    assert deleted is True
    assert database.get_expense(exp_id, db_path=temp_db) is None


def test_list_and_filter_expenses(temp_db):
    database.add_expense(
        merchant="Coffee Roasters",
        invoice_number="C-1",
        date="2026-09-01",
        currency="USD",
        subtotal=5.0,
        tax=0.5,
        total=5.5,
        category="Meals & Entertainment",
        db_path=temp_db,
    )
    database.add_expense(
        merchant="JetBrains",
        invoice_number="J-1",
        date="2026-10-01",
        currency="USD",
        subtotal=199.0,
        tax=0.0,
        total=199.0,
        category="Software & Subscriptions",
        db_path=temp_db,
    )

    # Category filter
    meals = database.list_expenses(category="Meals & Entertainment", db_path=temp_db)
    assert len(meals) == 1
    assert meals[0]["merchant"] == "Coffee Roasters"

    # Search filter
    search_res = database.list_expenses(search="JetBrains", db_path=temp_db)
    assert len(search_res) == 1
    assert search_res[0]["merchant"] == "JetBrains"


def test_load_demo_data(temp_db):
    count = database.load_demo_data(db_path=temp_db)
    assert count == 12
    stats = database.get_summary_stats(db_path=temp_db)
    assert stats["total_count"] == 12
    assert stats["total_amount"] > 0
