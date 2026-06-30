OUTPUT_FORMAT = """
Return ONLY valid JSON.

{
    "reasoning": "",

    "category": "",

    "subcategory": "",

    "priority": "Low | Medium | High | Critical",

    "confidence": 0.0,

    "recommended_resolution": "",

    "requires_manual_review": false
}

Rules:

- Return ONLY JSON.
- Do not return markdown.
- Do not wrap JSON inside ``` blocks.
- Confidence must be between 0.0 and 1.0.
- If confidence is below 0.50 then set
  requires_manual_review = true.
- reasoning should briefly explain why the category was chosen.
"""