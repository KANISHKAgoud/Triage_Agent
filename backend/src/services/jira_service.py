import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
load_dotenv()


def create_jira_ticket(
    ticket_id,
    category,
    subcategory,
    resolution,
):

    url = f"{os.getenv('JIRA_URL')}/rest/api/3/issue"

    auth = HTTPBasicAuth(
        os.getenv("JIRA_EMAIL"),
        os.getenv("JIRA_API_TOKEN"),
    )

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "fields": {
            "project": {
                "key": os.getenv("JIRA_PROJECT_KEY")
            },
            "summary": f"{ticket_id} - {category}",
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "text": resolution,
                                "type": "text"
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": "Task"
            }
        }
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        auth=auth,
        timeout=20,
    )

    print("=" * 60)
    print("JIRA CREATE RESPONSE")
    print(response.status_code)
    print(response.text)
    print("=" * 60)

    response.raise_for_status()

    return response.json()

def add_jira_comment(
    issue_key,
    comment_text,
):

    url = (
        f"{os.getenv('JIRA_URL')}"
        f"/rest/api/3/issue/{issue_key}/comment"
    )

    auth = HTTPBasicAuth(
        os.getenv("JIRA_EMAIL"),
        os.getenv("JIRA_API_TOKEN"),
    )

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": comment_text,
                        }
                    ]
                }
            ]
        }
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        auth=auth,
    )

    print(response.status_code)
    print(response.text)

    return response.json()