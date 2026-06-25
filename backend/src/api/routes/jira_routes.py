
from fastapi import APIRouter, HTTPException, status
router = APIRouter()
import re
from backend.src.graph.langgraph_service import process_query_langgraph
from backend.src.services.jira_service import add_jira_comment
from backend.src.storage.ticket_status_storage import (
    set_status,
    get_status,
)


from backend.src.storage.jira_storage import (
    get_jira_issues,
    get_jira_issue,
    get_jira_issue_keys,
)

from backend.src.storage.jira_processed_storage import (
    get_processed_ticket,
    is_processed,
    mark_processed,
)



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

def extract_jira_description(issue):

    description = (
        issue.get("fields", {})
        .get("description")
    )

    if not description:
        return ""

    return extract_jira_text(description)



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


    return {
        "issue_key": issue_key,
        "status": get_status(issue_key)
    }