"""FastAPI application entry point."""

from fastapi import FastAPI

from .routes import router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    app = FastAPI(
        title="Triage Agent API",
        version="1.0.0",
        description="Production-ready API shell for the Triage Agent service.",
    )

    # Register all API routes in one place so the app can grow cleanly.
    app.include_router(router)

    return app


# ASGI application used by Uvicorn/Gunicorn in development and production.
app = create_app()
