from .gemini_client import GeminiService
from .schemas import PromptRequest


def generate_outline(request: PromptRequest):

    service = GeminiService()

    result = service.generate_outline(
        request
    )

    return result.panels