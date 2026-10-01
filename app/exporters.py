import os
import re
from datetime import datetime
from pathlib import Path
from fpdf import FPDF


# Folder where generated PDF files will be saved
EXPORT_FOLDER = Path("static/exports")
EXPORT_FOLDER.mkdir(parents=True, exist_ok=True)


# Font file
FONT_PATH = "static/fonts/DejaVuSans.ttf"


def clean_pdf_text(text):
    """
    Cleans Gemini-generated text so it displays nicely in the PDF.
    """

    if not text:
        return ""

    # Remove Markdown bold markers
    text = text.replace("**", "")

    # Remove common Markdown-style headings
    text = re.sub(
        r"(?i)^Title:\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    text = re.sub(
        r"(?i)^Visuals:\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    text = re.sub(
        r"(?i)^Narration\s*\(Caption\):\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    # Convert speaker labels into cleaner dialogue
    text = re.sub(
        r"(?i)^([A-Za-z][A-Za-z0-9 _-]*)\s*\(([^)]+)\):\s*",
        r"\1: ",
        text,
        flags=re.MULTILINE
    )

    # Remove unwanted "Panel X" headings from story text
    text = re.sub(
        r"(?i)^\s*Panel\s*\d+\s*$",
        "",
        text,
        flags=re.MULTILINE
    )

    # Replace characters that may not work with the PDF font
    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "•": "-",
        "→": "->",
        "←": "<-",
        "✨": "*",
        "❤️": "<3",
        "😊": ":)"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove excessive blank lines
    text = re.sub(
        r"\n\s*\n\s*\n+",
        "\n\n",
        text
    )

    # PDF-safe text
    return text.encode(
        "latin-1",
        "replace"
    ).decode("latin-1").strip()


def save_pdf(layout):
    """
    Creates a clean 5-page PDF comic.
    Each comic panel gets its own page.
    """

    pdf = FPDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    # Select font
    if os.path.exists(FONT_PATH):

        pdf.add_font(
            "DejaVu",
            "",
            FONT_PATH,
            uni=True
        )

        font_name = "DejaVu"

    else:

        font_name = "Arial"

    # Create one page for each panel
    for panel in layout:

        pdf.add_page()

        # --------------------------------
        # PANEL NUMBER
        # --------------------------------

        pdf.set_font(
            font_name,
            "",
            14
        )

        pdf.cell(
            0,
            10,
            f"Panel {panel['panel']}",
            ln=True,
            align="C"
        )

        # --------------------------------
        # PANEL TITLE
        # --------------------------------

        title = clean_pdf_text(
            panel.get(
                "title",
                f"Panel {panel['panel']}"
            )
        )

        pdf.set_font(
            font_name,
            "",
            16
        )

        pdf.cell(
            0,
            12,
            title,
            ln=True,
            align="C"
        )

        # --------------------------------
        # IMAGE
        # --------------------------------

        image_path = panel.get(
            "image_path",
            ""
        )

        y_image = 35
        image_height = 100

        if os.path.exists(image_path):

            pdf.image(
                image_path,
                x=10,
                y=y_image,
                w=pdf.w - 20,
                h=image_height
            )

        else:

            pdf.set_y(y_image)

            pdf.multi_cell(
                0,
                10,
                "Image could not be found."
            )

        # --------------------------------
        # SCENE DESCRIPTION
        # --------------------------------

        scene_description = clean_pdf_text(
            panel.get(
                "scene_description",
                ""
            )
        )

        if scene_description:

            pdf.set_y(
                y_image +
                image_height +
                12
            )

            pdf.set_font(
                font_name,
                "",
                11
            )

            pdf.multi_cell(
                0,
                7,
                scene_description
            )

        # --------------------------------
        # STORY / DIALOGUE
        # --------------------------------

        story_text = clean_pdf_text(
            panel.get(
                "text",
                ""
            )
        )

        if story_text:

            pdf.ln(5)

            pdf.set_font(
                font_name,
                "",
                11
            )

            pdf.multi_cell(
                0,
                7,
                story_text
            )

    # --------------------------------
    # SAVE PDF
    # --------------------------------

    timestamp = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    filename = f"comic_{timestamp}.pdf"

    pdf_path = EXPORT_FOLDER / filename

    pdf.output(
        str(pdf_path)
    )

    return str(pdf_path).replace(
        "\\",
       "/"
    )