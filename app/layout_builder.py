def build_comic_layout(image_paths, full_story, outline):
    """
    Organizes the generated images and story
    into a structured comic layout.
    """

    story_panels = full_story.split("Panel")

    layout = []

    for index, panel_info in enumerate(outline):

        panel_number = index + 1

        # Get the corresponding story text
        if panel_number < len(story_panels):
            story_text = story_panels[panel_number].strip()
        else:
            story_text = ""

        # Get the corresponding image
        if index < len(image_paths):
            image_path = image_paths[index]
        else:
            image_path = ""

        layout.append({
            "panel": panel_number,
            "title": panel_info.get(
                "title",
                f"Panel {panel_number}"
            ),
            "image_path": image_path,
            "scene_description": panel_info.get(
                "scene_description",
                ""
            ),
            "text": story_text
        })

    return layout