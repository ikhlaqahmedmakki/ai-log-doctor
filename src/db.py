import sqlite3
import os
from pathlib import Path

DEFAULT_DB_PATH = "doctor.db"

def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Create and return a database connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initialize the database and create the findings table if it doesn't exist."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            fingerprint TEXT NOT NULL,
            severity TEXT NOT NULL,
            summary TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def finding_exists(fingerprint: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Check if a finding with the given fingerprint already exists in the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM findings WHERE fingerprint = ? LIMIT 1", (fingerprint,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def insert_finding(timestamp: str, fingerprint: str, severity: str, summary: str, db_path: str = DEFAULT_DB_PATH) -> int:
    """Insert a new finding into the database and return its id."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO findings (timestamp, fingerprint, severity, summary)
        VALUES (?, ?, ?, ?)
    """, (timestamp, fingerprint, severity, summary))
    conn.commit()
    finding_id = cursor.lastrowid
    conn.close()
    return finding_id
