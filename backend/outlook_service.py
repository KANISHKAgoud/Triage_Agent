emails = [
    {
        "id": "MAIL-001",
        "subject": "VPN Login Failure",
        "body": "Unable to login after changing phone",
        "processed": False,
    },
    {
        "id": "MAIL-002",
        "subject": "Password Reset",
        "body": "Forgot my password",
        "processed": False,
    },
]


def fetch_new_emails():

    return [
        email
        for email in emails
        if not email["processed"]
    ]


def mark_email_processed(email_id):

    for email in emails:

        if email["id"] == email_id:
            email["processed"] = True