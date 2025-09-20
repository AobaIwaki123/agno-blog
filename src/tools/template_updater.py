import json
from datetime import datetime
from pathlib import Path

from agno.tools import Tool


@Tool
def template_updater_tool(
    template_id: str,
    feedback: str,
    confirm_update: bool = False,
) -> str:
    """Update template based on user feedback. Requires confirmation."""
    try:
        templates_dir = Path("templates")
        template_path = (
            templates_dir / f"{template_id}.json"
        )

        if not template_path.exists():
            return f"Template {template_id} not found"

        # Load existing template
        with open(
            template_path, "r", encoding="utf-8"
        ) as f:
            template_data = json.load(f)

        if not confirm_update:
            # Return analysis without updating
            return f"Template update analysis for {template_id}:\nFeedback: {feedback}\n\nPlease confirm update with confirm_update=True"

        # Update template based on feedback
        current_version = template_data.get(
            "version", "1.0.0"
        )
        major, minor, patch = map(
            int, current_version.split(".")
        )
        patch += 1  # Increment patch version
        new_version = f"{major}.{minor}.{patch}"

        template_data["version"] = new_version
        template_data["updated_at"] = (
            datetime.utcnow().isoformat()
        )
        template_data["last_feedback"] = feedback

        # Save updated template
        with open(
            template_path, "w", encoding="utf-8"
        ) as f:
            json.dump(
                template_data,
                f,
                indent=2,
                ensure_ascii=False,
            )

        return f"Template {template_id} updated to version {new_version} based on feedback"

    except Exception as e:
        return f"Error updating template: {str(e)}"
