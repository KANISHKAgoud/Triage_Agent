from backend.postgres_service import get_pg_connection

conn = get_pg_connection()

cur = conn.cursor()

cur.execute("""
SELECT column_name
FROM information_schema.columns
WHERE table_name='triage_results';
""")

for row in cur.fetchall():
    print(row)

conn.close()