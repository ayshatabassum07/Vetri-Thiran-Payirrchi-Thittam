from datetime import datetime
from pathlib import Path

import re

from fpdf import FPDF

from .config import get_settings


class ComicPDF(FPDF):

    def header(self):

        self.set_font(
            "Helvetica",
            "B",
            16,
        )

        self.cell(
            0,
            10,
            "ComicCraft",
            ln=True,
            align="C",
        )

        self.ln(3)


def _pdf_text(text: str) -> str:

    replacements = {

        "“": '"',
        "”": '"',

        "‘": "'",
        "’": "'",

        "—": "-",
        "–": "-",

        "…": "...",

        "•": "-",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new,
        )

    return (
        text
        .encode(
            "latin-1",
            "replace",
        )
        .decode("latin-1")
    )


def save_pdf(
    layout,
    title="ComicCraft Comic",
) -> str:

    settings = get_settings()

    timestamp = datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )

    safe_title = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "-",
        title,
    )

    safe_title = (
        safe_title
        .strip("-")
        [:50]
        or "comic"
    )

    filename = (
        f"{safe_title}-"
        f"{timestamp}.pdf"
    )

    output = (
        settings.output_dir /
        filename
    )

    pdf = ComicPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    for panel in layout:

        pdf.add_page()

        # ----------------------------------------
        # Panel title
        # ----------------------------------------

        pdf.set_font(
            "Helvetica",
            "B",
            14,
        )

        pdf.multi_cell(
            0,
            8,
            _pdf_text(
                f"Panel "
                f"{panel['panel_number']}: "
                f"{panel['title']}"
            ),
        )

        # ----------------------------------------
        # Image
        # ----------------------------------------

        image_file = (
            settings.panel_dir /
            Path(
                panel["image_path"]
            ).name
        )

        if image_file.exists():

            pdf.image(
                str(image_file),
                x=20,
                y=35,
                w=170,
            )

            pdf.set_y(145)

        else:

            pdf.set_y(40)

        # ----------------------------------------
        # Scene description
        # ----------------------------------------

        pdf.set_font(
            "Helvetica",
            "I",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            _pdf_text(
                panel[
                    "scene_description"
                ]
            ),
        )

        # ----------------------------------------
        # Caption
        # ----------------------------------------

        if panel.get("caption"):

            pdf.set_font(
                "Helvetica",
                "B",
                10,
            )

            pdf.multi_cell(
                0,
                6,
                _pdf_text(
                    "Caption: "
                    + panel["caption"]
                ),
            )

        # ----------------------------------------
        # Narration
        # ----------------------------------------

        pdf.set_font(
            "Helvetica",
            "",
            11,
        )

        pdf.multi_cell(
            0,
            6,
            _pdf_text(
                panel["narration"]
            ),
        )

        # ----------------------------------------
        # Dialogue
        # ----------------------------------------

        for line in panel.get(
            "dialogue",
            [],
        ):

            pdf.set_font(
                "Helvetica",
                "B",
                10,
            )

            pdf.multi_cell(
                0,
                6,
                _pdf_text(
                    "Dialogue: "
                    + line
                ),
            )

    pdf.output(
        str(output)
    )

    return (
        f"/static/exports/"
        f"{filename}"
    )