from google import genai
from google.genai import types

from .config import get_settings
from .schemas import (
    OutlineResponse,
    PromptRequest,
    StoryResponse,
)


class GeminiService:

    def __init__(self) -> None:

        settings = get_settings()

        if not settings.gemini_api_key:

            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Add your Gemini API key to the .env file."
            )

        self.settings = settings

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    # ------------------------------------------------
    # Generic structured JSON generation
    # ------------------------------------------------

    def _generate_json(
        self,
        model: str,
        prompt: str,
        schema: type,
    ):

        response = self.client.models.generate_content(

            model=model,

            contents=prompt,

            config=types.GenerateContentConfig(

                temperature=0.9,

                response_mime_type="application/json",

                response_schema=schema,
            ),
        )

        if not response.text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return schema.model_validate_json(
            response.text
        )

    # ------------------------------------------------
    # Generate comic outline
    # ------------------------------------------------

    def generate_outline(
        self,
        request: PromptRequest,
    ) -> OutlineResponse:

        panel_count = (
            self.settings.panels_per_comic
        )

        prompt = f"""
You are the story-planning engine for ComicCraft.

Create exactly {panel_count} connected comic panels.

Return ONLY JSON matching the supplied schema.

USER STORY:
{request.story_prompt}

MAIN CHARACTER:
{request.character_name}

SETTING:
{request.setting}

TONE:
{request.tone}

ART STYLE:
{request.art_style}

Requirements:

1. Keep the same main character throughout.
2. Create a clear beginning.
3. Develop the story in the middle.
4. Give the story a satisfying ending.
5. Each panel needs:
   - panel number
   - concise title
   - vivid scene description
   - detailed image-generation prompt
6. Image prompts must describe:
   - character appearance
   - character action
   - environment
   - composition
   - lighting
   - requested art style
7. Do not include dialogue text inside image prompts.
8. Make the five panels visually connected.
"""

        result = self._generate_json(
            self.settings.gemini_outline_model,
            prompt,
            OutlineResponse,
        )

        if len(result.panels) != panel_count:

            raise RuntimeError(
                f"Gemini returned "
                f"{len(result.panels)} panels. "
                f"Expected {panel_count}."
            )

        return result

    # ------------------------------------------------
    # Generate story
    # ------------------------------------------------

    def generate_story(
        self,
        request: PromptRequest,
        outline: OutlineResponse,
    ) -> StoryResponse:

        outline_text = (
            outline.model_dump_json(
                indent=2
            )
        )

        prompt = f"""
You are the comic script writer for ComicCraft.

Expand the following comic outline into a coherent
comic script.

Return ONLY JSON matching the supplied schema.

USER STORY:
{request.story_prompt}

MAIN CHARACTER:
{request.character_name}

SETTING:
{request.setting}

TONE:
{request.tone}

ART STYLE:
{request.art_style}

OUTLINE:
{outline_text}

Requirements:

1. Preserve the exact panel order.
2. Preserve panel numbers.
3. Keep the same protagonist.
4. Maintain continuity between panels.
5. Write concise comic narration.
6. Provide 0-3 short dialogue lines per panel.
7. Provide an optional ambient caption.
8. Keep the tone requested by the user.
9. Do not introduce a completely different protagonist.
"""

        return self._generate_json(
            self.settings.gemini_story_model,
            prompt,
            StoryResponse,
        )