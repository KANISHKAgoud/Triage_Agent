import requests
import os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()


def get_jira_issues():

    url = (
        f"{os.getenv('JIRA_URL')}"
        "/rest/api/3/search/jql"
    )

    auth = HTTPBasicAuth(
        os.getenv("JIRA_EMAIL"),
        os.getenv("JIRA_API_TOKEN"),
    )

    headers = {
        "Accept": "application/json"
    }

    params = {
        "jql": f'project = {os.getenv("JIRA_PROJECT_KEY")}'
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        auth=auth,
    )

    print(response.status_code)
    print(response.text)

    return response.json()