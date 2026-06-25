from backend.database import get_connection


def ensure_processed_table():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS processed_jira_tickets (
            issue_key TEXT PRIMARY KEY,
            category TEXT,
            subcategory TEXT,
            resolution TEXT,
            summary TEXT,
            description TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute("PRAGMA table_info(processed_jira_tickets)")
    columns = {
        row[1]
        for row in cursor.fetchall()
    }

    for column_name, column_type in (
        ("category", "TEXT"),
        ("subcategory", "TEXT"),
        ("resolution", "TEXT"),
        ("summary", "TEXT"),
        ("description", "TEXT"),
    ):
        if column_name not in columns:
            cursor.execute(
                f"ALTER TABLE processed_jira_tickets ADD COLUMN {column_name} {column_type}"
            )

    conn.commit()

    cursor.close()
    conn.close()


def is_processed(issue_key):

    ensure_processed_table()

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


def get_processed_ticket(issue_key):

    ensure_processed_table()

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            issue_key,
            category,
            subcategory,
            resolution,
            summary,
            description,
            processed_at
        FROM processed_jira_tickets
        WHERE issue_key = ?
        """,
        (issue_key,)
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        return None

    return {
        "issue_key": row[0],
        "category": row[1],
        "subcategory": row[2],
        "resolution": row[3],
        "summary": row[4],
        "description": row[5],
        "processed_at": row[6],
    }


def mark_processed(
    issue_key,
    category=None,
    subcategory=None,
    resolution=None,
    summary=None,
    description=None,
):

    ensure_processed_table()

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO processed_jira_tickets(
            issue_key,
            category,
            subcategory,
            resolution,
            summary,
            description
        )
        VALUES(?,?,?,?,?,?)
        ON CONFLICT(issue_key) DO UPDATE SET
            category = COALESCE(excluded.category, processed_jira_tickets.category),
            subcategory = COALESCE(excluded.subcategory, processed_jira_tickets.subcategory),
            resolution = COALESCE(excluded.resolution, processed_jira_tickets.resolution),
            summary = COALESCE(excluded.summary, processed_jira_tickets.summary),
            description = COALESCE(excluded.description, processed_jira_tickets.description)
        """,
        (
            issue_key,
            category,
            subcategory,
            resolution,
            summary,
            description,
        )
    )

    conn.commit()

    cursor.close()
    conn.close()
