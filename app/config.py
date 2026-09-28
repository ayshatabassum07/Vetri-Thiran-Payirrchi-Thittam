from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    # -----------------------------
    # Application
    # -----------------------------

    app_name: str = "ComicCraft"
    environment: str = "development"
    debug: bool = True

    host: str = "127.0.0.1"
    port: int = 8000

    # -----------------------------
    # Gemini
    # -----------------------------

    gemini_api_key: str = ""

    gemini_outline_model: str = "gemini-2.5-flash"
    gemini_story_model: str = "gemini-2.5-flash"

    # -----------------------------
    # Image generation
    # -----------------------------

    # Options:
    # diffusers
    # placeholder
    image_provider: str = "placeholder"

    image_model: str = (
        "stable-diffusion-v1-5/stable-diffusion-v1-5"
    )

    hf_token: str = ""

    image_steps: int = 20

    image_width: int = 512
    image_height: int = 512

    image_guidance_scale: float = 7.0

    # auto / cpu / cuda / mps
    image_device: str = "auto"

    # -----------------------------
    # Comic configuration
    # -----------------------------

    panels_per_comic: int = 5

    max_prompt_length: int = 2000

    # -----------------------------
    # Directories
    # -----------------------------

    output_dir: Path = BASE_DIR / "static" / "exports"

    panel_dir: Path = BASE_DIR / "static" / "panels"

    # -----------------------------
    # Environment configuration
    # -----------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:

    settings = Settings()

    settings.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    settings.panel_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return settings