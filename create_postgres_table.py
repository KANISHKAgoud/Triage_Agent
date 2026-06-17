from backend.postgres_service import get_pg_connection

conn = get_pg_connection()

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS triage_results (
    id SERIAL PRIMARY KEY,
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

print("Postgres table created")