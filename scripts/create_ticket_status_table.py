from backend.database import get_connection

conn = get_connection()

conn.execute("""
CREATE TABLE IF NOT EXISTS ticket_status (
    issue_key TEXT PRIMARY KEY,
    status TEXT
)
""")

conn.commit()
conn.close()

print("ticket_status table created")