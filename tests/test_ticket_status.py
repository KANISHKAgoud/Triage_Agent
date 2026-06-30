# test_ticket_status.py

from backend.src.services.postgres_service import get_pg_connection

conn = get_pg_connection()

cur = conn.cursor()

cur.execute("""
SELECT
    ticket_id,
    ticket_status
FROM triage_results
ORDER BY id DESC
""")

rows = cur.fetchall()

print(rows)

conn.close()