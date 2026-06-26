import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


class GeminiServiceError(Exception):
    pass


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)


def ask_gemini(system_prompt: str, user_prompt: str) -> dict:

    prompt = f"""
{system_prompt}

-----------------------

{user_prompt}
"""

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )

        text = response.text.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "")
            text = text.replace("```", "").strip()

        return json.loads(text)

    except Exception as e:
        raise GeminiServiceError(str(e))