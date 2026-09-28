from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from fastapi.staticfiles import (
    StaticFiles,
)

from fastapi.templating import (
    Jinja2Templates,
)

from .config import (
    get_settings,
)

from .routes import (
    router,
)


settings = get_settings()


# =================================================
# Application lifespan
# =================================================

@asynccontextmanager
async def lifespan(
    app: FastAPI,
):

    settings.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    settings.panel_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    yield


# =================================================
# FastAPI Application
# =================================================

app = FastAPI(

    title=settings.app_name,

    version="1.0.0",

    description=(
        "AI comic story creator "
        "using Gemini and "
        "Stable Diffusion."
    ),

    lifespan=lifespan,
)


# =================================================
# Static files
# =================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

app.mount(

    "/static",

    StaticFiles(
        directory=str(
            BASE_DIR / "static"
        )
    ),

    name="static",
)


# =================================================
# Templates
# =================================================

templates = Jinja2Templates(

    directory=str(
        BASE_DIR / "templates"
    )
)

app.state.templates = templates


# =================================================
# Routes
# =================================================

app.include_router(
    router
)


# =================================================
# Health check
# =================================================

@app.get("/health")
async def health():

    return {

        "status": "ok",

        "app":
            settings.app_name,

        "image_provider":
            settings.image_provider,
    }