import traceback

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_image
from .layout_builder import build_comic_layout
from .exporters import save_pdf


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


class PromptRequest(BaseModel):

    prompt: str

    character_name: str = ""

    setting: str = ""

    tone: str = ""

    style: str = ""


# Home page
@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )


# Generate comic from HTML form
@router.post(
    "/generate",
    response_class=HTMLResponse
)
async def generate_comic(

    request: Request,

    prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    style: str = Form(...)

):

    try:

        # Combine all user inputs
        full_prompt = (

            f"{prompt}\n"

            f"The main character is "
            f"{character_name}.\n"

            f"The setting is "
            f"{setting}.\n"

            f"The tone is "
            f"{tone}. "

            f"The art style is "
            f"{style}."

        )

        # Step 1: Generate 5-panel outline
        outline = generate_outline(
            full_prompt
        )

        # Check outline
        if (

            not isinstance(outline, list)

            or not outline

            or "error" in outline[0]

            or any(
                "image_prompt" not in panel
                for panel in outline
            )

        ):

            raise ValueError(
                "Invalid outline from Gemini."
            )


        # Step 2: Generate detailed story
        full_story = generate_story(
            outline
        )


        # Step 3: Generate images
        images = [

            generate_image(
                panel["image_prompt"]
            )

            for panel in outline

        ]


        # Step 4: Build comic layout
        layout = build_comic_layout(

            images,

            full_story,

            outline

        )


        # Step 5: Create PDF
        pdf_path = save_pdf(
            layout
        )


        web_pdf_path = "/" + pdf_path.replace(
            "\\",
            "/"
        )


        # Show comic preview
        return templates.TemplateResponse(
    request=request,
    name="comic_preview.html",
    context={
        "request": request,
        "outline": outline,
        "story": full_story,
        "layout": layout,
        "pdf_path": web_pdf_path
    }
)


    except Exception as e:

        traceback.print_exc()

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# Generate comic using JSON
@router.post(
    "/generate-comic/json"
)
async def generate_comic_json(
    data: PromptRequest
):

    try:

        full_prompt = (

            f"{data.prompt}\n"

            f"The main character is "
            f"{data.character_name}.\n"

            f"The setting is "
            f"{data.setting}.\n"

            f"The tone is "
            f"{data.tone}. "

            f"The art style is "
            f"{data.style}."

        )


        outline = generate_outline(
            full_prompt
        )


        if (

            not isinstance(outline, list)

            or not outline

            or "error" in outline[0]

        ):

            raise ValueError(
                "Invalid outline from Gemini."
            )


        full_story = generate_story(
            outline
        )


        images = [

            generate_image(
                panel["image_prompt"]
            )

            for panel in outline

        ]


        layout = build_comic_layout(

            images,

            full_story,

            outline

        )


        pdf_path = save_pdf(
            layout
        )


        return {

            "layout": layout,

            "pdf_path":
                "/" +
                pdf_path.replace(
                    "\\",
                    "/"
                )

        }


    except Exception as e:

        traceback.print_exc()

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# Export success page
@router.get(
    "/export-success",
    response_class=HTMLResponse
)
async def export_success(

    request: Request,

    pdf_path: str = ""

):

    return templates.TemplateResponse(

        "export_success.html",

        {

            "request": request,

            "pdf_path": pdf_path

        }

    )


# Test image generation
@router.get(
    "/test-image"
)
async def test_image(

    prompt: str =
    "A futuristic city at sunset, sci-fi, cinematic, artstation"

):

    try:

        image_path = generate_image(
            prompt
        )

        return {

            "message":
                "Image generated successfully",

            "path":
                image_path

        }

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )