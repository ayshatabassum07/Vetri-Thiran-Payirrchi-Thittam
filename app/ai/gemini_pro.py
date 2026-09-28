from .gemini_client import GeminiService

from .schemas import (
    OutlineResponse,
    PromptRequest,
)


def generate_story(
    request: PromptRequest,
    outline,
):

    if isinstance(outline, list):

        outline = OutlineResponse(
            panels=outline
        )

    service = GeminiService()

    result = service.generate_story(
        request,
        outline,
    )

    return result.panels