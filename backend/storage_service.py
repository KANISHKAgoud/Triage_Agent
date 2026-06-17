from backend.database import get_connection


def save_triage_result(
    ticket_id,
    query,
    category,
    subcategory,
    resolution,
):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO triage_results
        (
            ticket_id,
            query,
            category,
            subcategory,
            resolution
        )
        VALUES (?, ?, ?, ?, ?)
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
    

def get_triage_history():

    conn = get_connection()

    rows = conn.execute(
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
    ).fetchall()

    conn.close()

    return rows