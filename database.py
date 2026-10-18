"""
database.py - SQLite storage and management for FreelanceFlow AI.
Uses parameterized queries to prevent SQL injection and ensures ACID compliance.
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "freelanceflow.db")

EXPENSE_CATEGORIES = [
    "Software & Subscriptions",
    "Hardware & Equipment",
    "Office Supplies",
    "Hosting & Cloud",
    "Travel & Transport",
    "Meals & Entertainment",
    "Professional Services",
    "Utilities & Phone",
    "Marketing & Ads",
    "Other",
]


@contextmanager
def get_connection(db_path: Optional[str] = None) -> Generator[sqlite3.Connection, None, None]:
    """Yields a sqlite3 connection with dict-like row access, safely closing it when done."""
    target_path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: Optional[str] = None) -> None:
    """Initializes the database schema with necessary tables and indexes."""
    target_path = db_path or DEFAULT_DB_PATH
    with get_connection(target_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merchant TEXT NOT NULL,
                invoice_number TEXT,
                date TEXT NOT NULL,
                currency TEXT NOT NULL DEFAULT 'USD',
                subtotal REAL DEFAULT 0.0,
                tax REAL DEFAULT 0.0,
                total REAL NOT NULL,
                category TEXT NOT NULL DEFAULT 'Other',
                file_hash TEXT,
                file_name TEXT,
                notes TEXT,
                is_demo INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_expenses_file_hash ON expenses(file_hash);
            """
        )
        conn.commit()


def check_duplicate_hash(file_hash: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Checks if a file with the same SHA-256 hash has already been recorded."""
    if not file_hash:
        return None
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, merchant, invoice_number, date, total, currency, file_name, created_at
            FROM expenses
            WHERE file_hash = ?
            LIMIT 1;
            """,
            (file_hash,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def add_expense(
    merchant: str,
    invoice_number: Optional[str],
    date: str,
    currency: str,
    subtotal: float,
    tax: float,
    total: float,
    category: str,
    file_hash: Optional[str] = None,
    file_name: Optional[str] = None,
    notes: Optional[str] = None,
    is_demo: int = 0,
    db_path: Optional[str] = None,
) -> int:
    """Inserts a new expense record using parameterized queries."""
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO expenses (
                merchant, invoice_number, date, currency,
                subtotal, tax, total, category,
                file_hash, file_name, notes, is_demo, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                merchant.strip(),
                (invoice_number or "").strip() or None,
                date.strip(),
                currency.strip().upper(),
                float(subtotal or 0.0),
                float(tax or 0.0),
                float(total),
                category.strip() or "Other",
                file_hash,
                file_name,
                (notes or "").strip() or None,
                int(is_demo),
                created_at,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def update_expense(
    expense_id: int,
    merchant: str,
    invoice_number: Optional[str],
    date: str,
    currency: str,
    subtotal: float,
    tax: float,
    total: float,
    category: str,
    notes: Optional[str] = None,
    db_path: Optional[str] = None,
) -> bool:
    """Updates an existing expense record by ID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE expenses
            SET merchant = ?,
                invoice_number = ?,
                date = ?,
                currency = ?,
                subtotal = ?,
                tax = ?,
                total = ?,
                category = ?,
                notes = ?
            WHERE id = ?;
            """,
            (
                merchant.strip(),
                (invoice_number or "").strip() or None,
                date.strip(),
                currency.strip().upper(),
                float(subtotal or 0.0),
                float(tax or 0.0),
                float(total),
                category.strip() or "Other",
                (notes or "").strip() or None,
                int(expense_id),
            ),
        )
        conn.commit()
        return cursor.rowcount > 0


def delete_expense(expense_id: int, db_path: Optional[str] = None) -> bool:
    """Deletes an expense record by ID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?;", (int(expense_id),))
        conn.commit()
        return cursor.rowcount > 0


def get_expense(expense_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves a single expense by ID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses WHERE id = ?;", (int(expense_id),))
        row = cursor.fetchone()
        return dict(row) if row else None


def list_expenses(
    search: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Lists expenses with optional filtering for search terms, category, and date range."""
    query = "SELECT * FROM expenses WHERE 1=1"
    params: List[Any] = []

    if search:
        search_term = f"%{search.strip()}%"
        query += " AND (merchant LIKE ? OR invoice_number LIKE ? OR notes LIKE ?)"
        params.extend([search_term, search_term, search_term])

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)

    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    query += " ORDER BY date DESC, id DESC;"

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_summary_stats(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Computes summary metrics for dashboard KPIs."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_count,
                COALESCE(SUM(total), 0.0) as total_amount,
                COALESCE(AVG(total), 0.0) as avg_amount,
                COUNT(DISTINCT category) as category_count
            FROM expenses;
            """
        )
        row = cursor.fetchone()
        stats = dict(row) if row else {"total_count": 0, "total_amount": 0.0, "avg_amount": 0.0, "category_count": 0}

        # Find top category
        cursor.execute(
            """
            SELECT category, SUM(total) as cat_total
            FROM expenses
            GROUP BY category
            ORDER BY cat_total DESC
            LIMIT 1;
            """
        )
        top_cat_row = cursor.fetchone()
        stats["top_category"] = top_cat_row["category"] if top_cat_row else "None"
        stats["top_category_amount"] = top_cat_row["cat_total"] if top_cat_row else 0.0
        return stats


def load_demo_data(db_path: Optional[str] = None) -> int:
    """Inserts a realistic set of fictional sample freelancer expenses for Demo Mode."""
    sample_records = [
        ("Figma Professional", "INV-2026-081", "2026-09-01", "USD", 15.00, 0.00, 15.00, "Software & Subscriptions", "Monthly UI/UX design tool license", "demo_figma_hash"),
        ("GitHub Copilot", "GH-882194", "2026-09-05", "USD", 19.00, 0.00, 19.00, "Software & Subscriptions", "AI developer pairing subscription", "demo_github_hash"),
        ("AWS Web Services", "981240182", "2026-09-12", "USD", 48.75, 4.25, 53.00, "Hosting & Cloud", "Client project demo server and S3 bucket", "demo_aws_hash"),
        ("WeWork Co-Working", "WW-77492", "2026-09-15", "USD", 35.00, 3.50, 38.50, "Office Supplies", "Hot desk pass for client meetings", "demo_wework_hash"),
        ("Blue Bottle Coffee", "REC-4410", "2026-09-18", "USD", 18.20, 1.64, 19.84, "Meals & Entertainment", "Coffee meeting with freelance design client", "demo_coffee_hash"),
        ("Notion Workspace Plus", "NTN-2026-09", "2026-09-20", "USD", 10.00, 0.00, 10.00, "Software & Subscriptions", "Client portal and task management", "demo_notion_hash"),
        ("Keychron K2 Mechanical Keyboard", "AMZ-99321", "2026-09-25", "USD", 89.00, 8.01, 97.01, "Hardware & Equipment", "Ergonomic workspace upgrade", "demo_keyboard_hash"),
        ("Vercel Pro Team", "VER-33214", "2026-10-01", "USD", 20.00, 1.80, 21.80, "Hosting & Cloud", "Next.js & Streamlit application deployments", "demo_vercel_hash"),
        ("Zoom Video Pro", "ZM-871120", "2026-10-05", "USD", 15.99, 1.28, 17.27, "Utilities & Phone", "Client video conferences and recording", "demo_zoom_hash"),
        ("LegalZoom LLC Filing Advice", "LZ-55102", "2026-10-10", "USD", 150.00, 0.00, 150.00, "Professional Services", "Contract legal review for retainer agreement", "demo_legal_hash"),
        ("Uber Business", "UBR-90124", "2026-10-12", "USD", 24.50, 2.20, 26.70, "Travel & Transport", "Ride to in-person design sprint kickoff", "demo_uber_hash"),
        ("Google Workspace Business", "GGL-44321", "2026-10-14", "USD", 12.00, 0.00, 12.00, "Software & Subscriptions", "Freelance business domain email & storage", "demo_google_hash"),
    ]

    inserted_count = 0
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for merchant, inv_num, date_str, cur, subtotal, tax, total, cat, notes, fhash in sample_records:
            # Check if demo record already exists
            cursor.execute("SELECT id FROM expenses WHERE file_hash = ?", (fhash,))
            if not cursor.fetchone():
                cursor.execute(
                    """
                    INSERT INTO expenses (
                        merchant, invoice_number, date, currency,
                        subtotal, tax, total, category,
                        file_hash, file_name, notes, is_demo, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?);
                    """,
                    (merchant, inv_num, date_str, cur, subtotal, tax, total, cat, fhash, f"sample_{merchant.lower().replace(' ', '_')}.pdf", notes, datetime.now(timezone.utc).isoformat()),
                )
                inserted_count += 1
        conn.commit()
    return inserted_count


def clear_all_expenses(db_path: Optional[str] = None) -> int:
    """Clears all expenses from the database. Useful for resetting."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses;")
        count = cursor.rowcount
        conn.commit()
        return count
