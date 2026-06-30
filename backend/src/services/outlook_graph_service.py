import os
import requests


def get_emails():

    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    if not all([tenant_id, client_id, client_secret]):
        return [
            {
                "id": "MAIL-001",
                "subject": "VPN Login Failure",
                "body": "Unable to login after changing phone",
            }
        ]

    return []
