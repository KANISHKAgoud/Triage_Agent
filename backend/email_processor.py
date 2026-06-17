from backend.langgraph_service import process_query_langgraph


def process_email(email):

    query = (
        email["subject"]
        + "\n\n"
        + email["body"]
    )

    result = process_query_langgraph(
        query=query,
        ticket_id=email["id"],
    )

    return {
        "email_id": email["id"],
        "subject": email["subject"],
        "triage_result": result,
    }