from backend.database import get_connection

conn = get_connection()

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS processed_jira_tickets (
    issue_key TEXT PRIMARY KEY,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

cursor.close()
conn.close()

print("Processed Jira table created")