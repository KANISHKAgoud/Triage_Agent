"""Utility functions for interacting with FreeScout."""

from __future__ import annotations

import os

from dotenv import load_dotenv


class FreeScoutServiceError(RuntimeError):
    """Raised when FreeScout service configuration or operations fail."""


def get_freescout_url() -> str:
    """Read the FreeScout base URL from environment configuration."""

    load_dotenv()
    freescout_url = os.getenv("FREESCOUT_URL")

    if not freescout_url:
        raise FreeScoutServiceError("Missing FREESCOUT_URL environment variable.")

    return freescout_url


def get_freescout_api_key() -> str:
    """Read the FreeScout API key from environment configuration."""

    load_dotenv()
    api_key = os.getenv("FREESCOUT_API_KEY")

    if not api_key:
        raise FreeScoutServiceError("Missing FREESCOUT_API_KEY environment variable.")

    return api_key


def add_ticket_note(ticket_id: str, note: str) -> None:
    """Print the note payload that would be sent to FreeScout."""

    print(f"Would add note to FreeScout ticket {ticket_id}: {note}")


def update_ticket_fields(
    ticket_id: str,
    category: str,
    subcategory: str,
) -> None:
    """Print the field update payload that would be sent to FreeScout."""

    print(
        "Would update FreeScout ticket "
        f"{ticket_id} fields: category={category}, subcategory={subcategory}"
    )
