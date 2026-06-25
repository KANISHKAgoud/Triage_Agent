from backend.src.services.postgres_service import get_pg_connection

conn = get_pg_connection()

cur = conn.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS servicenow_incidents (
        id SERIAL PRIMARY KEY,
        ticket_id VARCHAR(100),
        category VARCHAR(100),
        subcategory VARCHAR(100),
        resolution TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)

conn.commit()
conn.close()

print("ServiceNow table created")