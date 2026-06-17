from backend.postgres_service import get_pg_connection


def save_triage_result_pg(
    ticket_id,
    query,
    category,
    subcategory,
    resolution,
):
    conn = get_pg_connection()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO triage_results
        (
            ticket_id,
            query,
            category,
            subcategory,
            resolution
        )
        VALUES (%s,%s,%s,%s,%s)
        """,
        (
            ticket_id,
            query,
            category,
            subcategory,
            resolution,
        ),
    )

    conn.commit()
    conn.close()

    print("Saved to PostgreSQL")


def get_triage_history_pg():

    conn = get_pg_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            ticket_id,
            query,
            category,
            subcategory,
            resolution,
            created_at
        FROM triage_results
        ORDER BY id DESC
        """
    )

    rows = cur.fetchall()

    conn.close()

    return rows