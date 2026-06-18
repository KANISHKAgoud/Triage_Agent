from backend.postgres_service import get_pg_connection


def create_ticket(
    ticket_id,
    subject,
    status,
    category,
    subcategory,
    resolution,
):
    conn = get_pg_connection()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO tickets
        (
            ticket_id,
            subject,
            status,
            category,
            subcategory,
            resolution
        )
        VALUES (%s,%s,%s,%s,%s,%s)
        """,
        (
            ticket_id,
            subject,
            status,
            category,
            subcategory,
            resolution,
        ),
    )

    conn.commit()
    conn.close()


def get_tickets():

    conn = get_pg_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM tickets
        ORDER BY id DESC
        """
    )

    rows = cur.fetchall()

    conn.close()

    return rows