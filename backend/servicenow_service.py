def create_incident(
    ticket_id,
    category,
    subcategory,
    resolution,
):

    print(
        f"""
ServiceNow Incident Created

Ticket ID: {ticket_id}
Category: {category}
Subcategory: {subcategory}
Resolution: {resolution}
"""
    )
    