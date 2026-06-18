from backend.postgres_storage import (
    update_ticket_status_pg,
)


def update_ticket_status(
    ticket_id,
    status,
):
    update_ticket_status_pg(
        ticket_id,
        status,
    )

    print(
        f"Ticket {ticket_id} status updated to {status}"
    )