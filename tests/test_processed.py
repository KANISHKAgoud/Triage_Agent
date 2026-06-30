from backend.database import get_connection

conn = get_connection()

cursor = conn.cursor()

cursor.execute(
    "SELECT * FROM processed_jira_tickets"
)

rows = cursor.fetchall()

print(rows)

cursor.close()
conn.close()