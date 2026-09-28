def build_comic_layout(
    outline,
    story,
    image_paths,
):

    story_by_number = {
        panel.panel_number: panel
        for panel in story
    }

    layout = []

    for panel in outline:

        script = story_by_number.get(
            panel.panel_number
        )

        if not script:

            raise ValueError(
                "Missing story content "
                f"for panel "
                f"{panel.panel_number}"
            )

        layout.append({

            "panel_number":
                panel.panel_number,

            "title":
                script.title
                or panel.title,

            "image_path":
                image_paths[
                    panel.panel_number - 1
                ],

            "scene_description":
                (
                    script.scene_description
                    or panel.scene_description
                ),

            "caption":
                script.caption,

            "narration":
                script.narration,

            "dialogue":
                script.dialogue,

            "image_prompt":
                panel.image_prompt,
        })

    return layout