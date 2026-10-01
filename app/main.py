from pathlib import Path

from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from .routes import router


app = FastAPI(
    title="ComicCraft AI"
)


# Create required folders
Path(
    "static/panels"
).mkdir(
    parents=True,
    exist_ok=True
)

Path(
    "static/exports"
).mkdir(
    parents=True,
    exist_ok=True
)

Path(
    "static/fonts"
).mkdir(
    parents=True,
    exist_ok=True
)


# Connect static files
app.mount(
    "/static",
    StaticFiles(
        directory="static"
    ),
    name="static"
)


# Connect routes
app.include_router(
    router
)