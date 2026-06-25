from backend.src.services.postgres_service import get_pg_connection

def update_ticket_status_pg(
    ticket_id,
    ticket_status,
):
    conn = get_pg_connection()

    cur = conn.cursor()

    cur.execute(
        """
        UPDATE triage_results
        SET ticket_status = %s
        WHERE ticket_id = %s
        """,
        (
            ticket_status,
            ticket_id,
        ),
    )

    conn.commit()
    conn.close()

    print(
        f"PostgreSQL status updated: {ticket_id} -> {ticket_status}"
    )


def save_triage_result_pg(
    ticket_id,
    query,
    category,
    subcategory,
    resolution,
    ticket_status,
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
            resolution,
            ticket_status
        )
        VALUES (%s,%s,%s,%s,%s,%s)
        """,
        (
            ticket_id,
            query,
            category,
            subcategory,
            resolution,
            ticket_status,
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
            ticket_status,
            resolution,
            created_at
        FROM triage_results
        ORDER BY id DESC
        """
    )

    rows = cur.fetchall()

    conn.close()

    return rows