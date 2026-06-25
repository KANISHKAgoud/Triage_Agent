"""FastAPI application entry point."""

from fastapi import FastAPI
from backend.database import create_tables
from backend.src.api.routes.agent_routes import router as agent_router
from backend.src.api.routes.dashboard_routes import router as dashboard_router
from backend.src.api.routes.email_routes import router as email_router
from backend.src.api.routes.jira_routes import router as jira_router
from backend.src.api.routes.outlook_routes import router as outlook_router
from backend.src.api.routes.servicenow_routes import router as servicenow_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    create_tables()

    app = FastAPI(
        title="Triage Agent API",
        version="1.0.0",
        description="Production-ready API shell for the Triage Agent service.",
    )


    # Register all API routes in one place so the app can grow cleanly.
    app.include_router(agent_router)
    app.include_router(jira_router)
    app.include_router(dashboard_router)
    app.include_router(email_router)
    app.include_router(outlook_router)
    app.include_router(servicenow_router)

    return app


# ASGI application used by Uvicorn/Gunicorn in development and production.
app = create_app()
