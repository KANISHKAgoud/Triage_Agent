"""Smoke test script for semantic incident search."""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from rag.search import search_incidents


QUERIES = [
    "VPN not working after changing mobile phone",
    "User cannot access shared mailbox",
    "Database report timing out",
    "Customer documents not uploading",
    "Account locked repeatedly",
]


def print_results(query: str) -> None:
    """Run one query and print the most relevant incident matches."""

    print(f"\nQuery: {query}")
    print("-" * 80)

    results = search_incidents(query, top_k=3)

    for result in results:
        print(f"Ticket ID: {result['ticket_id']}")
        print(f"Issue Name: {result['issue_name']}")
        print(f"Category: {result['category']}")
        print(f"Score: {result['score']:.4f}")
        print()


def main() -> None:
    """Run all configured search queries."""

    for query in QUERIES:
        print_results(query)


if __name__ == "__main__":
    main()
