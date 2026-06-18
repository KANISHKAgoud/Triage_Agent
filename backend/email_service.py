import os
import smtplib

from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


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

    msg = MIMEText(body)

    msg["Subject"] = "Triage Agent Resolution"
    msg["From"] = os.getenv("SMTP_EMAIL")
    msg["To"] = recipient

    try:

        server = smtplib.SMTP(
            os.getenv("SMTP_SERVER"),
            int(os.getenv("SMTP_PORT")),
        )

        server.starttls()

        server.login(
            os.getenv("SMTP_EMAIL"),
            os.getenv("SMTP_PASSWORD"),
        )

        server.send_message(msg)

        server.quit()

        print(
            f"Email sent successfully to {recipient}"
        )

    except Exception as e:

        print(
            f"Failed to send email: {e}"
        )