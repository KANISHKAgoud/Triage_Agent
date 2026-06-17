from backend.postgres_service import get_pg_connection

conn = get_pg_connection()

cur = conn.cursor()

cur.execute(
    """
    SELECT *
    FROM triage_results
    ORDER BY id DESC
    """
)

rows = cur.fetchall()

print(rows)

conn.close()