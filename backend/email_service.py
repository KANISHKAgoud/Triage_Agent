import smtplib
from email.mime.text import MIMEText


def send_triage_email(
    recipient,
    category,
    subcategory,
    resolution,
):
    body = f"""
Category: {category}

Subcategory: {subcategory}

Resolution:
{resolution}
"""

    print(
        f"Would send email to {recipient}"
    )

    print(body)