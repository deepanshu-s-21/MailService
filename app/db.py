import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

DB_PATH = Path(__file__).resolve().parent.parent / "mail_service.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the database schema if it doesn't exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                status TEXT NOT NULL, -- 'SENT' or 'FAILED'
                error_message TEXT,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_created_at ON emails(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_recipient ON emails(recipient)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_status ON emails(status)")
        conn.commit()


def save_email(
    recipient: str,
    subject: str,
    body: str,
    status: str,
    error_message: Optional[str] = None
) -> int:
    """Save an email record and return its ID."""
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO emails (recipient, subject, body, status, error_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (recipient, subject, body, status, error_message, created_at))
        conn.commit()
        return cursor.lastrowid


def get_emails(
    search: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Retrieve emails with optional search, status filtering, and pagination."""
    query = "SELECT id, recipient, subject, body, status, error_message, created_at FROM emails WHERE 1=1"
    params: List[Any] = []

    if status and status.upper() in ("SENT", "FAILED"):
        query += " AND status = ?"
        params.append(status.upper())

    if search and search.strip():
        term = f"%{search.strip()}%"
        query += " AND (recipient LIKE ? OR subject LIKE ? OR body LIKE ?)"
        params.extend([term, term, term])

    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_email_by_id(email_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single email by its ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, recipient, subject, body, status, error_message, created_at
            FROM emails
            WHERE id = ?
        """, (email_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_email(email_id: int) -> bool:
    """Delete an email record by its ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM emails WHERE id = ?", (email_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_stats() -> Dict[str, Any]:
    """Get email delivery statistics."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM emails")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emails WHERE status = 'SENT'")
        sent = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emails WHERE status = 'FAILED'")
        failed = cursor.fetchone()[0]

        rate = round((sent / total * 100), 1) if total > 0 else 100.0

        return {
            "total": total,
            "sent": sent,
            "failed": failed,
            "success_rate": rate
        }
