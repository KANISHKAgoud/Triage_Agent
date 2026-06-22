from backend.database import get_connection


def is_processed(issue_key):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT issue_key
        FROM processed_jira_tickets
        WHERE issue_key = ?
        """,
        (issue_key,)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result is not None


def mark_processed(issue_key):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO processed_jira_tickets(issue_key)
        VALUES(?)
        """,
        (issue_key,)
    )

    conn.commit()

    cursor.close()
    conn.close()