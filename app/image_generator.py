from pathlib import Path

import hashlib
import re

from PIL import Image, ImageDraw

from .config import get_settings


_PIPELINE = None


# ------------------------------------------------
# Safe filename
# ------------------------------------------------

def _safe_name(text: str) -> str:

    cleaned = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "-",
        text,
    )

    cleaned = cleaned.strip("-").lower()

    return cleaned[:80] or "panel"


# ------------------------------------------------
# Select device
# ------------------------------------------------

def _device(settings):

    if settings.image_device != "auto":

        return settings.image_device

    try:

        import torch

        if torch.cuda.is_available():

            return "cuda"

        if (
            getattr(
                torch.backends,
                "mps",
                None,
            )
            and torch.backends.mps.is_available()
        ):

            return "mps"

    except Exception:

        pass

    return "cpu"


# ------------------------------------------------
# Placeholder image
# ------------------------------------------------

def _placeholder(
    prompt: str,
    path: Path,
    panel_number: int,
) -> None:

    image = Image.new(
        "RGB",
        (768, 512),
        "#f4efe6",
    )

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (20, 20, 748, 492),
        outline="#252525",
        width=5,
    )

    draw.text(
        (45, 45),
        f"ComicCraft Panel {panel_number}",
        fill="#111111",
    )

    text = prompt[:420]

    draw.multiline_text(
        (45, 100),
        text,
        fill="#222222",
        spacing=8,
    )

    image.save(
        path,
        format="PNG",
    )


# ------------------------------------------------
# Load Stable Diffusion
# ------------------------------------------------

def _get_pipeline():

    global _PIPELINE

    if _PIPELINE is not None:

        return _PIPELINE

    settings = get_settings()

    from diffusers import (
        StableDiffusionPipeline
    )

    import torch

    device = _device(settings)

    if device == "cuda":

        dtype = torch.float16

    else:

        dtype = torch.float32

    kwargs = {
        "torch_dtype": dtype
    }

    if settings.hf_token:

        kwargs["token"] = (
            settings.hf_token
        )

    _PIPELINE = (
        StableDiffusionPipeline
        .from_pretrained(
            settings.image_model,
            **kwargs,
        )
    )

    _PIPELINE = _PIPELINE.to(
        device
    )

    if device == "cuda":

        _PIPELINE.enable_attention_slicing()

    return _PIPELINE


# ------------------------------------------------
# Generate image
# ------------------------------------------------

def generate_image(
    prompt: str,
    panel_number: int,
) -> str:

    settings = get_settings()

    digest = hashlib.sha256(
        prompt.encode("utf-8")
    ).hexdigest()[:12]

    filename = (
        f"panel-"
        f"{panel_number}-"
        f"{_safe_name(prompt)}-"
        f"{digest}.png"
    )

    path = (
        settings.panel_dir /
        filename
    )

    if path.exists():

        return (
            f"/static/panels/"
            f"{filename}"
        )

    # --------------------------------------------
    # Development mode
    # --------------------------------------------

    if (
        settings.image_provider.lower()
        == "placeholder"
    ):

        _placeholder(
            prompt,
            path,
            panel_number,
        )

        return (
            f"/static/panels/"
            f"{filename}"
        )

    # --------------------------------------------
    # Stable Diffusion
    # --------------------------------------------

    pipe = _get_pipeline()

    result = pipe(

        prompt=prompt,

        negative_prompt=(
            "blurry, distorted, low quality, "
            "extra limbs, bad anatomy, "
            "unreadable text, watermark"
        ),

        num_inference_steps=(
            settings.image_steps
        ),

        guidance_scale=(
            settings.image_guidance_scale
        ),

        width=settings.image_width,

        height=settings.image_height,
    )

    image = result.images[0]

    image.save(path)

    return (
        f"/static/panels/"
        f"{filename}"
    )