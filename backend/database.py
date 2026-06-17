import sqlite3


def get_connection():
    return sqlite3.connect("triage.db")


def create_tables():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS triage_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT,
            query TEXT,
            category TEXT,
            subcategory TEXT,
            resolution TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

    conn.commit()
    conn.close()