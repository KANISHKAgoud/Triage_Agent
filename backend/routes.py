"""API route definitions for the Triage Agent service."""

import re

from backend.storage_service import get_triage_history
from backend.langgraph_service import process_query_langgraph
from fastapi import APIRouter, HTTPException, status
from starlette.concurrency import run_in_threadpool
from backend.postgres_storage import get_triage_history_pg
from backend.outlook_graph_service import get_emails
from backend.outlook_service import fetch_new_emails
from backend.email_processor import process_email
from backend.email_service import send_triage_email
from backend.ticket_storage import get_tickets
from backend.servicenow_storage import get_incidents
from backend.vector_service import get_vector_stats
# from backend.jira_storage import get_jira_issues
from backend.ticket_storage import get_tickets
from backend.servicenow_storage import get_incidents
from backend.vector_service import get_vector_stats
from backend.jira_processed_storage import (
    get_processed_ticket,
    is_processed,
    mark_processed,
)
from backend.jira_service import add_jira_comment
from backend.jira_storage import (
    get_jira_issues,
    get_jira_issue,
    get_jira_issue_keys,
)
# from backend.jira_storage import get_jira_issue
from backend.agent_service import process_query
from backend.freescout_service import (
    add_ticket_note,
    update_ticket_fields,
)

from .models import (
    AgentRequest,
    AgentResponse,
    FreeScoutWebhookRequest,
    FreeScoutWebhookResponse,
    RetrievedIncident,
)


router = APIRouter()


def extract_jira_text(node):
    def collect_text(node):
        if isinstance(node, str):
            return [node]

        if isinstance(node, list):
            values = []
            for item in node:
                values.extend(collect_text(item))
            return values

        if not isinstance(node, dict):
            return []

        values = []

        text = node.get("text")
        if text:
            values.append(text)

        for child in node.get("content", []):
            values.extend(collect_text(child))

        return values

    return "\n".join(
        text
        for text in collect_text(node)
        if text
    )


def extract_jira_description(issue):

    description = (
        issue.get("fields", {})
        .get("description")
    )

    if not description:
        return ""

    return extract_jira_text(description)


def extract_latest_ai_comment(issue):

    comments = (
        issue.get("fields", {})
        .get("comment", {})
        .get("comments", [])
    )

    parsed_comments = []

    for comment in comments:
        body_text = extract_jira_text(
            comment.get("body", {})
        )

        category_match = re.search(
            r"Category:\s*(.+)",
            body_text,
            re.IGNORECASE,
        )
        subcategory_match = re.search(
            r"Subcategory:\s*(.+)",
            body_text,
            re.IGNORECASE,
        )
        resolution_match = re.search(
            r"Resolution:\s*([\s\S]+)",
            body_text,
            re.IGNORECASE,
        )

        if not (
            category_match
            or subcategory_match
            or resolution_match
        ):
            continue

        parsed_comments.append(
            {
                "created": comment.get("created", ""),
                "category": (
                    category_match.group(1).strip()
                    if category_match
                    else None
                ),
                "subcategory": (
                    subcategory_match.group(1).strip()
                    if subcategory_match
                    else None
                ),
                "resolution": (
                    resolution_match.group(1).strip()
                    if resolution_match
                    else None
                ),
            }
        )

    if not parsed_comments:
        return None

    return sorted(
        parsed_comments,
        key=lambda item: item.get("created") or "",
    )[-1]


def enrich_jira_issue(issue):

    issue_key = issue.get("key") or issue.get("issue_key")
    fields = issue.get("fields", {})
    processed_ticket = get_processed_ticket(issue_key) if issue_key else None
    latest_ai_comment = extract_latest_ai_comment(issue)

    category = (
        latest_ai_comment.get("category")
        if latest_ai_comment and latest_ai_comment.get("category")
        else processed_ticket.get("category")
        if processed_ticket
        else None
    )
    subcategory = (
        latest_ai_comment.get("subcategory")
        if latest_ai_comment and latest_ai_comment.get("subcategory")
        else processed_ticket.get("subcategory")
        if processed_ticket
        else None
    )
    resolution = (
        latest_ai_comment.get("resolution")
        if latest_ai_comment and latest_ai_comment.get("resolution")
        else processed_ticket.get("resolution")
        if processed_ticket
        else None
    )

    has_ai_result = (
        processed_ticket is not None
        or latest_ai_comment is not None
    )

    issue["ai_status"] = "Triaged" if has_ai_result else "Pending"
    issue["processed"] = has_ai_result
    issue["category"] = category
    issue["subcategory"] = subcategory
    issue["resolution"] = resolution
    issue["jira_status"] = (
        fields.get("status", {})
        .get("name")
        if isinstance(fields.get("status"), dict)
        else fields.get("status")
    )
    issue["created_date"] = fields.get("created")
    issue["summary"] = fields.get("summary") or issue.get("summary")
    issue["description"] = (
        extract_jira_description(issue)
        or (
            processed_ticket.get("description")
            if processed_ticket
            else ""
        )
    )

    return issue


@router.get(
    "/",
    summary="API health welcome",
)
async def read_root() -> dict[str, str]:
    """Return a simple status message for the API root."""

    return {
        "message": "Welcome to Triage Agent API",
        "status": "running",
    }


@router.post(
    "/agent",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
    summary="Process a user query",
)
@router.post(
    "/agent/query",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
    summary="Process a user query",
)
async def run_agent(payload: AgentRequest) -> AgentResponse:
    """Search historical incidents and return the closest matches."""

    search_query = payload.search_query

    try:
        result = await run_in_threadpool(
    process_query_langgraph,
    search_query,
)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        print(exc)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    retrieved_incidents = [
        RetrievedIncident(
            ticket_id=str(incident["ticket_id"]),
            issue_name=str(incident["issue_name"]),
            category=str(incident["category"]),
            subcategory=str(incident["subcategory"]),
            priority=str(incident["priority"]),
            department=str(incident["department"]),
            status=str(incident["status"]),
            score=float(incident["score"]),
            symptoms=str(incident["symptoms"]),
            root_cause=str(incident["root_cause"]),
            resolution=str(incident["resolution"]),
        )
        for incident in result["retrieved_incidents"]
    ]

    return AgentResponse(
        status="success",
        query=search_query,
        session_id=payload.session_id,
        predicted_category=str(result["predicted_category"]),
        predicted_subcategory=str(result["predicted_subcategory"]),
        confidence_score=float(result["confidence_score"]),
        recommended_resolution=str(result["recommended_resolution"]),
        retrieved_incidents=retrieved_incidents,
    )


@router.post(
    "/freescout/webhook",
    response_model=FreeScoutWebhookResponse,
    status_code=status.HTTP_200_OK,
    summary="Process a FreeScout ticket webhook",
)

async def run_freescout_webhook(
    payload: FreeScoutWebhookRequest,
) -> FreeScoutWebhookResponse:
    """Search historical incidents for a FreeScout ticket webhook."""

    search_query = payload.search_query

    try:
        result = await run_in_threadpool(
        process_query_langgraph,
        search_query,
        payload.ticket_id,
)
        update_ticket_fields(
            ticket_id=payload.ticket_id,
            category=result["predicted_category"],
            subcategory=result["predicted_subcategory"],
        )
        add_ticket_note(
            ticket_id=payload.ticket_id,
            note=result["recommended_resolution"],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while processing FreeScout webhook.",
        ) from exc

    retrieved_incidents = [
        RetrievedIncident(
            ticket_id=str(incident["ticket_id"]),
            issue_name=str(incident["issue_name"]),
            category=str(incident["category"]),
            subcategory=str(incident["subcategory"]),
            priority=str(incident["priority"]),
            department=str(incident["department"]),
            status=str(incident["status"]),
            score=float(incident["score"]),
            symptoms=str(incident["symptoms"]),
            root_cause=str(incident["root_cause"]),
            resolution=str(incident["resolution"]),
        )
        for incident in result["retrieved_incidents"]
    ]

    return FreeScoutWebhookResponse(
        ticket_id=payload.ticket_id,
        predicted_category=str(result["predicted_category"]),
        predicted_subcategory=str(result["predicted_subcategory"]),
        recommended_resolution=str(result["recommended_resolution"]),
        retrieved_incidents=retrieved_incidents,
    )


@router.get("/email/test")
async def email_test():

    send_triage_email(
        recipient="user@example.com",
        category="VPN",
        subcategory="Remote Access",
        resolution="Reset MFA registration",
    )

    return {
        "status": "email simulated"
    }


@router.get("/outlook/test")
async def outlook_test():

    emails = fetch_new_emails()

    return {
        "count": len(emails),
        "emails": emails,
    }

@router.get("/outlook/process")
async def outlook_process():

    emails = fetch_new_emails()

    results = []

    for email in emails:
        results.append(
            process_email(email)
        )

    return {
        "processed": len(results),
        "results": results,
    }

@router.get("/outlook/live")
async def outlook_live():

    emails = get_emails()

    return {
        "count": len(emails),
        "emails": emails,
    }


@router.get("/history")
async def history():

    rows = get_triage_history()

    return {
        "count": len(rows),
        "results": rows,
    }

@router.get("/postgres-history")
async def postgres_history():

    rows = get_triage_history_pg()

    return {
        "count": len(rows),
        "results": rows,
    }

@router.get("/tickets")
async def tickets():

    rows = get_tickets()

    return {
        "count": len(rows),
        "tickets": rows,
    }

@router.get("/vector-health")
async def vector_health():

    return get_vector_stats()

@router.get("/dashboard")
async def dashboard():

    tickets = get_tickets()

    incidents = get_incidents()

    vector_stats = get_vector_stats()

    total_tickets = len(tickets)

    triaged_tickets = len(
        [
            ticket
            for ticket in tickets
            if ticket[3] == "TRIAGED"
        ]
    )

    servicenow_incidents = len(incidents)

    vector_documents = vector_stats.get(
        "documents",
        0,
    )

    return {
        "total_tickets": total_tickets,
        "triaged_tickets": triaged_tickets,
        "servicenow_incidents": servicenow_incidents,
        "vector_documents": vector_documents,
        "vector_db": "healthy",
        "mailbox": "connected",
    }


@router.get("/servicenow/incidents")
async def servicenow_incidents():

    rows = get_incidents()

    return {
        "count": len(rows),
        "incidents": rows,
    }


@router.get("/jira/issues")
async def jira_issues():

    data = get_jira_issues()

    issues = data.get(
        "issues",
        []
    )

    data["issues"] = [
        enrich_jira_issue(issue)
        for issue in issues
    ]

    return data


@router.get("/jira/issue/{issue_key}")
async def jira_issue(issue_key: str):

    data = get_jira_issue(issue_key)

    data = enrich_jira_issue(data)

    return data

@router.get("/jira/process/{issue_key}")
async def jira_process(issue_key: str):

    issue = get_jira_issue(issue_key)

    description = ""

    try:

        description = (
            issue["fields"]
            ["description"]
            ["content"][0]
            ["content"][0]
            ["text"]
        )

    except Exception:

        description = issue["fields"]["summary"]

    result = process_query_langgraph(
        description
    )

    jira_comment = f"""
    Category: {result['predicted_category']}

    Subcategory: {result['predicted_subcategory']}

    Resolution:
    {result['recommended_resolution']}
    """

    add_jira_comment(
        issue_key,
        jira_comment,
    )

    return {
        "issue_key": issue_key,
        "summary": issue["fields"]["summary"],
        "description": description,
        "predicted_category":
            result["predicted_category"],
        "predicted_subcategory":
            result["predicted_subcategory"],
        "resolution":
            result["recommended_resolution"],
    }


@router.get("/jira/process-all")
async def jira_process_all():

    issue_keys = get_jira_issue_keys()

    results = []

    for issue_key in issue_keys:

        if is_processed(issue_key):
            continue

        issue = get_jira_issue(
            issue_key
        )

        try:

            description = (
                issue["fields"]
                ["description"]
                ["content"][0]
                ["content"][0]
                ["text"]
            )

        except Exception:

            description = (
                issue["fields"]
                ["summary"]
            )

        result = process_query_langgraph(
            description
        )

        jira_comment = f"""
        Category: {result['predicted_category']}

        Subcategory: {result['predicted_subcategory']}

        Resolution:
        {result['recommended_resolution']}
        """

        add_jira_comment(
            issue_key,
            jira_comment,
        )
        mark_processed(
            issue_key,
            result["predicted_category"],
            result["predicted_subcategory"],
            result["recommended_resolution"],
            issue["fields"]["summary"],
            description,
        )

        results.append(
            {
                "issue_key": issue_key,
                "category":
                    result["predicted_category"],
                "subcategory":
                    result["predicted_subcategory"],
            }
        )

    return {
        "processed": len(results),
        "results": results,
    }


@router.get("/jira/unprocessed")
async def jira_unprocessed():

    issue_keys = get_jira_issue_keys()

    results = []

    for issue_key in issue_keys:

        if is_processed(issue_key):
            continue

        issue = get_jira_issue(issue_key)

        results.append(
            {
                "issue_key": issue_key,
                "summary": issue["fields"]["summary"],
                "status": issue["fields"]["status"]["name"],
            }
        )

    return {
        "count": len(results),
        "tickets": results,
    }


@router.post("/jira/process-ticket/{issue_key}")
async def process_single_ticket(
    issue_key: str
):

    if is_processed(issue_key):

        return {
            "status": "already_processed"
        }

    issue = get_jira_issue(
        issue_key
    )

    try:

        description = (
            issue["fields"]
            ["description"]
            ["content"][0]
            ["content"][0]
            ["text"]
        )

    except Exception:

        description = (
            issue["fields"]
            ["summary"]
        )

    result = process_query_langgraph(
        description
    )

    jira_comment = f"""
Category: {result['predicted_category']}

Subcategory: {result['predicted_subcategory']}

Resolution:
{result['recommended_resolution']}
"""

    add_jira_comment(
        issue_key,
        jira_comment,
    )

    from backend.ticket_status_storage import set_status

    set_status(
        issue_key,
        "TRIAGED"
    )

    mark_processed(
        issue_key,
        result["predicted_category"],
        result["predicted_subcategory"],
        result["recommended_resolution"],
        issue["fields"]["summary"],
        description,
    )

    return {
        "issue_key": issue_key,
        "category": result["predicted_category"],
        "subcategory": result["predicted_subcategory"],
        "resolution": result["recommended_resolution"],
    }

@router.get("/jira/status/{issue_key}")
async def jira_status(issue_key: str):

    from backend.ticket_status_storage import get_status

    return {
        "issue_key": issue_key,
        "status": get_status(issue_key)
    }
