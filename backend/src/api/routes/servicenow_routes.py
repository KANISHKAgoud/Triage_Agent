from fastapi import APIRouter, HTTPException, status
router = APIRouter()
from backend.src.storage.servicenow_storage import get_incidents


@router.get("/servicenow/incidents")
async def servicenow_incidents():

    rows = get_incidents()

    return {
        "count": len(rows),
        "incidents": rows,
    }