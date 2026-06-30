from backend.src.services.jira_service import create_jira_ticket

create_jira_ticket(
    ticket_id="MAIL-999",
    category="VPN",
    subcategory="Remote Access",
    resolution="VPN login failed after MFA device change",
)