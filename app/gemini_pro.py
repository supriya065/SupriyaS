import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


MODEL = "gemini-3.5-flash-lite"


def generate_story(outline: list) -> str:
    """
    Generates a detailed comic story with narration
    and character dialogue from the 5-panel outline.
    """

    formatted_outline = "\n".join(
        [
            f"Panel {i + 1}: {item}"
            for i, item in enumerate(outline)
        ]
    )

    prompt = f"""
You are a professional comic book writer.

Create a detailed comic story from this 5-panel outline:

{formatted_outline}

Instructions:

- Write narration for every panel.
- Add suitable character dialogues.
- Make the story engaging and cohesive.
- Keep each panel connected to the next.
- Clearly separate each panel.
- Use a comic-book writing style.

Start each section exactly like this:

Panel 1
Panel 2
Panel 3
Panel 4
Panel 5
"""

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        return response.text.strip()

    except Exception as error:

        print("Gemini Story Error:", error)

        raise