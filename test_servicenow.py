from backend.postgres_service import get_pg_connection

conn = get_pg_connection()

cur = conn.cursor()

cur.execute(
    """
    SELECT *
    FROM servicenow_incidents
    ORDER BY id DESC
    """
)

rows = cur.fetchall()

for row in rows:
    print(row)

conn.close()