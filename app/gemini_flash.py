import os
import json
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODELS = [
    "gemini-3.5-flash-lite",
]


def generate_content_with_retry(prompt: str):
    last_error = None

    for model in MODELS:
        for attempt in range(3):
            try:
                return client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )

            except ServerError as error:
                last_error = error
                time.sleep(2 ** attempt)

    raise last_error


def generate_outline(user_prompt: str) -> list:
    prompt = f"""
You are a professional AI comic planner.

Generate a strictly formatted JSON array containing exactly 5 panel
descriptions for the comic story below.

STORY:
{user_prompt}

Each panel object must include:
- "panel": panel number
- "title": short panel title
- "scene_description": description of what happens
- "image_prompt": detailed image generation prompt

Return ONLY valid JSON. Do not include explanations or markdown.
"""

    try:
        response = generate_content_with_retry(prompt)
        output_text = response.text.strip()
        panel_data = json.loads(output_text)

        if not isinstance(panel_data, list) or len(panel_data) != 5:
            raise ValueError("Gemini did not return exactly 5 panels.")

        required_keys = {
            "panel",
            "title",
            "scene_description",
            "image_prompt",
        }

        for panel in panel_data:
            if not isinstance(panel, dict) or not required_keys.issubset(panel):
                raise ValueError("Invalid panel format.")

        return panel_data

    except Exception as error:
        print("Gemini Flash Error:", error)
        raise