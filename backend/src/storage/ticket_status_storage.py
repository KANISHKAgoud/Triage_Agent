from backend.database import get_connection


def get_status(issue_key):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT status
        FROM ticket_status
        WHERE issue_key = ?
        """,
        (issue_key,)
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row:
        return row[0]

    return "NEW"


def set_status(issue_key, status):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE
        INTO ticket_status(issue_key, status)
        VALUES(?, ?)
        """,
        (issue_key, status)
    )

    conn.commit()

    cursor.close()
    conn.close()