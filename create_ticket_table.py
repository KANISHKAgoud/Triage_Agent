from backend.src.services.postgres_service import get_pg_connection

conn = get_pg_connection()

cur = conn.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS tickets (
        id SERIAL PRIMARY KEY,
        ticket_id TEXT,
        subject TEXT,
        status TEXT,
        category TEXT,
        subcategory TEXT,
        resolution TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)

conn.commit()

print("Tickets table created")

conn.close()
