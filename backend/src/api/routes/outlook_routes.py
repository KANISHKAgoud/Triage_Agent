from fastapi import APIRouter, HTTPException, status
router = APIRouter()
from backend.src.services.outlook_service import fetch_new_emails
from backend.src.services.outlook_graph_service import get_emails
from backend.src.services.email_processor import process_email



@router.get("/outlook/test")
async def outlook_test():

    emails = fetch_new_emails()

    return {
        "count": len(emails),
        "emails": emails,
    }

@router.get("/outlook/live")
async def outlook_live():

    emails = get_emails()

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