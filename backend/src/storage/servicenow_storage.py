from backend.src.services.postgres_service import get_pg_connection


def save_incident(
    ticket_id,
    category,
    subcategory,
    resolution,
):

    conn = get_pg_connection()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO servicenow_incidents
        (
            ticket_id,
            category,
            subcategory,
            resolution
        )
        VALUES (%s,%s,%s,%s)
        """,
        (
            ticket_id,
            category,
            subcategory,
            resolution,
        ),
    )

    conn.commit()
    conn.close()

    print("ServiceNow Incident Saved")
    

def get_incidents():

    conn = get_pg_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM servicenow_incidents
        ORDER BY id DESC
        """
    )

    rows = cur.fetchall()

    conn.close()

    return rows