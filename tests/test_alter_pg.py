from backend.src.services.postgres_service import get_pg_connection

conn = get_pg_connection()

cur = conn.cursor()

cur.execute("""
ALTER TABLE triage_results
ADD COLUMN ticket_status VARCHAR(50);
""")

conn.commit()

print("Column added successfully")

conn.close()