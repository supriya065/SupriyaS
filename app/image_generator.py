import os
import re

import torch

from pathlib import Path
from dotenv import load_dotenv
from diffusers import StableDiffusionPipeline


load_dotenv()


HF_API_KEY = os.getenv("HF_API_KEY")

MODEL_ID = "runwayml/stable-diffusion-v1-5"

OUTPUT_FOLDER = Path("static/panels")
OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


def sanitize_filename(text):
    """Create a safe filename."""

    filename = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        text
    )

    return filename[:50]


# Load Stable Diffusion
if torch.cuda.is_available():

    dtype = torch.float16
    device = "cuda"

else:

    dtype = torch.float32
    device = "cpu"


pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_ID,
    torch_dtype=dtype,
    token=HF_API_KEY
)

pipe = pipe.to(device)


def generate_image(prompt, filename=None):
    """
    Generate a comic-style image using Stable Diffusion.
    """

    if filename is None:

        filename = sanitize_filename(
            prompt
        )

    if not filename.endswith(".png"):

        filename = filename + ".png"


    filepath = OUTPUT_FOLDER / filename


    # Keep the prompt short enough for
    # Stable Diffusion's text encoder.
    short_prompt = " ".join(
        prompt.split()
    )[:300]


    comic_prompt = (
        "comic book panel, colorful digital art, "
        "clear characters, cinematic composition, "
        "detailed background, dramatic lighting, "
        "family friendly. "
        + short_prompt
    )


    image = pipe(
        comic_prompt,
        num_inference_steps=30,
        width=512,
        height=512
    ).images[0]


    image.save(filepath)


    return str(filepath).replace(
        "\\",
        "/"
    )