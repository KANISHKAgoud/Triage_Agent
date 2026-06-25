from typing import Any

HARDWARE_KEYWORDS = {
    "laptop",
    "battery",
    "overheating",
    "keyboard",
    "monitor",
    "display",
    "printer",
    "scanner",
}

HARDWARE_KEYWORD_BOOST = 0.20


def has_hardware_keyword(query: str) -> bool:
    query = query.lower()

    return any(
        keyword in query
        for keyword in HARDWARE_KEYWORDS
    )


def apply_hardware_keyword_boost(
    query: str,
    incidents: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    if not has_hardware_keyword(query):
        return incidents

    boosted = []

    for incident in incidents:

        incident = dict(incident)

        if incident.get("category") == "Hardware":
            incident["score"] = min(
                1.0,
                float(incident.get("score", 0)) + HARDWARE_KEYWORD_BOOST,
            )

        boosted.append(incident)

    boosted.sort(
        key=lambda x: float(x.get("score", 0)),
        reverse=True,
    )

    return boosted