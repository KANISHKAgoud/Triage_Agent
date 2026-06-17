from backend.postgres_service import get_pg_connection

conn = get_pg_connection()

print("Connected successfully")

conn.close()