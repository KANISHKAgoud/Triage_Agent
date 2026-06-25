from backend.src.graph.langgraph_service import process_query_langgraph
from backend.src.services.outlook_service import mark_email_processed
from backend.src.services.email_service import send_triage_email
from backend.src.storage.ticket_storage import create_ticket
from backend.src.services.ticket_service import update_ticket_status
from backend.ticket_status import PROCESSING
from backend.src.services.servicenow_service import create_incident
from backend.src.services.jira_service import create_jira_ticket

def process_email(email):

    query = (
        email["subject"]
        + "\n\n"
        + email["body"]
    )

    update_ticket_status(
        email["id"],
        PROCESSING,
    )

    result = process_query_langgraph(
        query=query,
        ticket_id=email["id"],
    )

    create_incident(
        ticket_id=email["id"],
        category=result["predicted_category"],
        subcategory=result["predicted_subcategory"],
        resolution=result["recommended_resolution"],
    )

    print("ServiceNow Incident Saved")

    create_jira_ticket(
        ticket_id=email["id"],
        category=result["predicted_category"],
        subcategory=result["predicted_subcategory"],
        resolution=result["recommended_resolution"],
    )

    print("Jira Ticket Created")

    create_ticket(
        ticket_id=email["id"],
        subject=email["subject"],
        status="TRIAGED",
        category=result["predicted_category"],
        subcategory=result["predicted_subcategory"],
        resolution=result["recommended_resolution"],
    )

    send_triage_email(
        recipient="oakcompasshub@outlook.com",
        category=result["predicted_category"],
        subcategory=result["predicted_subcategory"],
        resolution=result["recommended_resolution"],
    )

    mark_email_processed(email["id"])

    return {
        "email_id": email["id"],
        "subject": email["subject"],
        "triage_result": result,
    }