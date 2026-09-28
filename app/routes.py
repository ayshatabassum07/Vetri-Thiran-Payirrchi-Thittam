```python
import asyncio

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
)

from .schemas import PromptRequest
from .gemini_client import GeminiService
from .image_generator import generate_image
from .layout_builder import build_comic_layout
from .exporters import save_pdf


router = APIRouter()


async def _generate(
    request_data: PromptRequest,
):
    service = GeminiService()

    outline = await asyncio.to_thread(
        service.generate_outline,
        request_data,
    )

    story = await asyncio.to_thread(
        service.generate_story,
        request_data,
        outline,
    )

    image_paths = []

    for panel in outline.panels:
        image_path = await asyncio.to_thread(
            generate_image,
            panel.image_prompt,
            panel.panel_number,
        )

        image_paths.append(image_path)

    layout = build_comic_layout(
        outline.panels,
        story.panels,
        image_paths,
    )

    pdf_path = await asyncio.to_thread(
        save_pdf,
        layout,
        request_data.character_name,
    )

    return layout, pdf_path


@router.get(
    "/",
    response_class=HTMLResponse,
)
async def home(request: Request):

    return request.app.state.templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.post(
    "/generate",
    response_class=HTMLResponse,
)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):

    try:
        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        layout, pdf_path = await _generate(data)

        return request.app.state.templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_path": pdf_path,
            },
        )

    except Exception as exc:

        return request.app.state.templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "error": str(exc),
            },
            status_code=500,
        )


@router.post("/generate-comic/json")
async def generate_json(
    payload: PromptRequest,
):

    try:

        layout, pdf_path = await _generate(
            payload
        )

        return JSONResponse({
            "success": True,
            "layout": layout,
            "pdf_path": pdf_path,
        })

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
async def export_success(
    request: Request,
):

    return request.app.state.templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={},
    )


@router.post("/test-image")
async def test_image(
    prompt: str = Form(...),
):

    try:

        path = await asyncio.to_thread(
            generate_image,
            prompt,
            1,
        )

        return {
            "success": True,
            "image_path": path,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
```
