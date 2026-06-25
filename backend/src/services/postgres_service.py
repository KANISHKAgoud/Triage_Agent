import psycopg2


def get_pg_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="triage_db",
        user="triage_user",
        password="triage_password",
    )