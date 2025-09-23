"""
Template Management Tools for Blog Posts

This module provides tools for managing blog post templates,
handling user feedback, and updating templates based on user input.
"""

import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TemplateManagementTools:
    """Tools for managing blog post templates."""

    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)

        # Ensure we have a default template
        self._ensure_default_template()

    def _ensure_default_template(self):
        """Ensure a default template exists."""
        default_template_path = (
            self.templates_dir / "default.json"
        )

        if not default_template_path.exists():
            default_template = {
                "id": "default",
                "name": "Default Blog Template",
                "description": "Standard blog post template with title, introduction, main content, and conclusion",
                "content": """# {title}

## Introduction

{introduction}

## Main Content

{main_content}

## Key Points

{key_points}

## Conclusion

{conclusion}

---

*Published on {publish_date}*
*Tags: {tags}*
*Source: {source_url}*""",
                "version": "1.0.0",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "usage_count": 0,
                "feedback_score": 5.0,
                "is_active": True,
                "variables": [
                    "title",
                    "introduction",
                    "main_content",
                    "key_points",
                    "conclusion",
                    "publish_date",
                    "tags",
                    "source_url",
                ],
                "feedback_history": [],
            }

            self.save_template("default", default_template)
            logger.info("Created default template")

    def load_template(
        self, template_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load a template by ID.

        Args:
            template_id: Unique identifier for the template

        Returns:
            Template data dictionary or None if not found
        """
        try:
            template_file = (
                self.templates_dir / f"{template_id}.json"
            )

            if not template_file.exists():
                logger.warning(
                    f"Template {template_id} not found"
                )
                return None

            with open(
                template_file, "r", encoding="utf-8"
            ) as f:
                template_data = json.load(f)

            logger.info(f"Loaded template: {template_id}")
            return template_data

        except Exception as e:
            logger.error(
                f"Error loading template {template_id}: {str(e)}"
            )
            return None

    def save_template(
        self,
        template_id: str,
        template_data: Dict[str, Any],
    ) -> bool:
        """
        Save a template to disk.

        Args:
            template_id: Unique identifier for the template
            template_data: Template data dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            template_file = (
                self.templates_dir / f"{template_id}.json"
            )

            # Update metadata
            template_data["id"] = template_id
            template_data["updated_at"] = (
                datetime.utcnow().isoformat()
            )

            # Ensure required fields exist
            if "created_at" not in template_data:
                template_data["created_at"] = (
                    datetime.utcnow().isoformat()
                )
            if "usage_count" not in template_data:
                template_data["usage_count"] = 0
            if "feedback_score" not in template_data:
                template_data["feedback_score"] = 5.0
            if "feedback_history" not in template_data:
                template_data["feedback_history"] = []

            with open(
                template_file, "w", encoding="utf-8"
            ) as f:
                json.dump(
                    template_data,
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            logger.info(f"Saved template: {template_id}")
            return True

        except Exception as e:
            logger.error(
                f"Error saving template {template_id}: {str(e)}"
            )
            return False

    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all available templates.

        Returns:
            List of template summaries
        """
        try:
            templates = []

            for template_file in self.templates_dir.glob(
                "*.json"
            ):
                template_id = template_file.stem
                template_data = self.load_template(
                    template_id
                )

                if template_data:
                    # Return summary information
                    templates.append(
                        {
                            "id": template_data.get(
                                "id", template_id
                            ),
                            "name": template_data.get(
                                "name", template_id
                            ),
                            "description": template_data.get(
                                "description", ""
                            ),
                            "version": template_data.get(
                                "version", "1.0.0"
                            ),
                            "usage_count": template_data.get(
                                "usage_count", 0
                            ),
                            "feedback_score": template_data.get(
                                "feedback_score", 5.0
                            ),
                            "is_active": template_data.get(
                                "is_active", True
                            ),
                            "updated_at": template_data.get(
                                "updated_at", ""
                            ),
                        }
                    )

            # Sort by usage count and feedback score
            templates.sort(
                key=lambda x: (
                    x["usage_count"],
                    x["feedback_score"],
                ),
                reverse=True,
            )

            return templates

        except Exception as e:
            logger.error(
                f"Error listing templates: {str(e)}"
            )
            return []

    def create_template(
        self,
        name: str,
        content: str,
        description: str = "",
        variables: List[str] = None,
    ) -> str:
        """
        Create a new template.

        Args:
            name: Template name
            content: Template content with placeholders
            description: Template description
            variables: List of variable names used in template

        Returns:
            Template ID of created template
        """
        try:
            template_id = str(uuid.uuid4())[:8]

            # Extract variables from content if not provided
            if variables is None:
                import re

                variables = re.findall(
                    r"\{(\w+)\}", content
                )
                variables = list(
                    set(variables)
                )  # Remove duplicates

            template_data = {
                "id": template_id,
                "name": name,
                "description": description,
                "content": content,
                "version": "1.0.0",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "usage_count": 0,
                "feedback_score": 5.0,
                "is_active": True,
                "variables": variables,
                "feedback_history": [],
            }

            if self.save_template(
                template_id, template_data
            ):
                logger.info(
                    f"Created new template: {template_id} ({name})"
                )
                return template_id
            else:
                raise Exception("Failed to save template")

        except Exception as e:
            logger.error(
                f"Error creating template: {str(e)}"
            )
            return ""

    def update_template_from_feedback(
        self,
        template_id: str,
        feedback: str,
        user_confirmation: bool = False,
    ) -> Dict[str, Any]:
        """
        Update template based on user feedback.

        Args:
            template_id: Template to update
            feedback: User feedback text
            user_confirmation: Whether user confirmed the update

        Returns:
            Dictionary with update results and proposed changes
        """
        try:
            template_data = self.load_template(template_id)
            if not template_data:
                return {
                    "status": "error",
                    "message": "Template not found",
                }

            # Analyze feedback
            feedback_analysis = self._analyze_feedback(
                feedback
            )

            # Generate proposed changes
            proposed_changes = (
                self._generate_template_changes(
                    template_data, feedback_analysis
                )
            )

            if not user_confirmation:
                return {
                    "status": "pending_confirmation",
                    "message": "Template update requires user confirmation",
                    "proposed_changes": proposed_changes,
                    "feedback_analysis": feedback_analysis,
                }

            # Apply changes if confirmed
            if proposed_changes and user_confirmation:
                updated_template = (
                    self._apply_template_changes(
                        template_data, proposed_changes
                    )
                )

                # Add feedback to history
                feedback_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "feedback": feedback,
                    "analysis": feedback_analysis,
                    "changes_applied": proposed_changes,
                }
                updated_template["feedback_history"].append(
                    feedback_entry
                )

                # Update version
                current_version = updated_template.get(
                    "version", "1.0.0"
                )
                version_parts = current_version.split(".")
                version_parts[-1] = str(
                    int(version_parts[-1]) + 1
                )
                updated_template["version"] = ".".join(
                    version_parts
                )

                # Save updated template
                if self.save_template(
                    template_id, updated_template
                ):
                    return {
                        "status": "success",
                        "message": "Template updated successfully",
                        "changes_applied": proposed_changes,
                        "new_version": updated_template[
                            "version"
                        ],
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Failed to save updated template",
                    }

            return {
                "status": "no_changes",
                "message": "No changes to apply",
            }

        except Exception as e:
            logger.error(
                f"Error updating template from feedback: {str(e)}"
            )
            return {"status": "error", "message": str(e)}

    def _analyze_feedback(
        self, feedback: str
    ) -> Dict[str, Any]:
        """Analyze user feedback to understand what needs to be changed."""
        analysis = {
            "sentiment": "neutral",
            "issues": [],
            "suggestions": [],
            "sections_mentioned": [],
        }

        feedback_lower = feedback.lower()

        # Detect sentiment
        positive_words = [
            "good",
            "great",
            "excellent",
            "perfect",
            "like",
            "love",
            "better",
        ]
        negative_words = [
            "bad",
            "poor",
            "terrible",
            "hate",
            "dislike",
            "wrong",
            "issue",
        ]

        positive_count = sum(
            1
            for word in positive_words
            if word in feedback_lower
        )
        negative_count = sum(
            1
            for word in negative_words
            if word in feedback_lower
        )

        if positive_count > negative_count:
            analysis["sentiment"] = "positive"
        elif negative_count > positive_count:
            analysis["sentiment"] = "negative"

        # Detect specific issues
        issue_patterns = [
            ("too long", "length"),
            ("too short", "length"),
            ("unclear", "clarity"),
            ("confusing", "clarity"),
            ("missing", "completeness"),
            ("need more", "completeness"),
            ("repetitive", "redundancy"),
            ("boring", "engagement"),
        ]

        for pattern, issue_type in issue_patterns:
            if pattern in feedback_lower:
                analysis["issues"].append(issue_type)

        # Detect section mentions
        sections = [
            "title",
            "introduction",
            "conclusion",
            "content",
            "summary",
        ]
        for section in sections:
            if section in feedback_lower:
                analysis["sections_mentioned"].append(
                    section
                )

        return analysis

    def _generate_template_changes(
        self,
        template_data: Dict[str, Any],
        feedback_analysis: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate proposed changes based on feedback analysis."""
        changes = []
        content = template_data.get("content", "")

        # Generate changes based on issues identified
        for issue in feedback_analysis.get("issues", []):
            if issue == "length":
                changes.append(
                    {
                        "type": "content_adjustment",
                        "description": "Adjust content length based on feedback",
                        "action": "modify_sections",
                    }
                )
            elif issue == "clarity":
                changes.append(
                    {
                        "type": "clarity_improvement",
                        "description": "Improve clarity and readability",
                        "action": "add_explanations",
                    }
                )
            elif issue == "completeness":
                changes.append(
                    {
                        "type": "content_addition",
                        "description": "Add missing content sections",
                        "action": "add_sections",
                    }
                )

        # Generate changes for mentioned sections
        for section in feedback_analysis.get(
            "sections_mentioned", []
        ):
            changes.append(
                {
                    "type": "section_modification",
                    "section": section,
                    "description": f"Modify {section} section based on feedback",
                    "action": "update_section",
                }
            )

        return changes

    def _apply_template_changes(
        self,
        template_data: Dict[str, Any],
        changes: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Apply the proposed changes to the template."""
        updated_template = template_data.copy()
        content = updated_template.get("content", "")

        for change in changes:
            if change["type"] == "content_adjustment":
                # Add more detailed instructions for content generation
                if "## Instructions" not in content:
                    content += "\n\n## Instructions\n\nGenerate content that is well-structured and appropriate in length."

            elif change["type"] == "clarity_improvement":
                # Add clarity instructions
                if "clear and concise" not in content:
                    content = content.replace(
                        "{main_content}",
                        "{main_content}\n\n*Note: Keep content clear and concise*",
                    )

            elif change["type"] == "content_addition":
                # Add additional sections if needed
                if (
                    "## Additional Information"
                    not in content
                ):
                    content += "\n\n## Additional Information\n\n{additional_info}"
                    if (
                        "additional_info"
                        not in updated_template.get(
                            "variables", []
                        )
                    ):
                        updated_template[
                            "variables"
                        ].append("additional_info")

        updated_template["content"] = content
        return updated_template

    def increment_usage_count(
        self, template_id: str
    ) -> bool:
        """
        Increment the usage count for a template.

        Args:
            template_id: Template to update

        Returns:
            True if successful, False otherwise
        """
        try:
            template_data = self.load_template(template_id)
            if not template_data:
                return False

            template_data["usage_count"] = (
                template_data.get("usage_count", 0) + 1
            )
            return self.save_template(
                template_id, template_data
            )

        except Exception as e:
            logger.error(
                f"Error incrementing usage count: {str(e)}"
            )
            return False

    def update_feedback_score(
        self, template_id: str, score: float
    ) -> bool:
        """
        Update the feedback score for a template.

        Args:
            template_id: Template to update
            score: New feedback score (1-10)

        Returns:
            True if successful, False otherwise
        """
        try:
            template_data = self.load_template(template_id)
            if not template_data:
                return False

            # Average with existing score
            current_score = template_data.get(
                "feedback_score", 5.0
            )
            usage_count = template_data.get(
                "usage_count", 1
            )

            # Weighted average based on usage
            new_score = (
                (current_score * usage_count) + score
            ) / (usage_count + 1)
            template_data["feedback_score"] = round(
                new_score, 2
            )

            return self.save_template(
                template_id, template_data
            )

        except Exception as e:
            logger.error(
                f"Error updating feedback score: {str(e)}"
            )
            return False

    def render_template(
        self, template_id: str, variables: Dict[str, str]
    ) -> str:
        """
        Render a template with provided variables.

        Args:
            template_id: Template to render
            variables: Dictionary of variable values

        Returns:
            Rendered template content
        """
        try:
            template_data = self.load_template(template_id)
            if not template_data:
                return ""

            content = template_data.get("content", "")

            # Replace variables in template
            for var_name, var_value in variables.items():
                placeholder = "{" + var_name + "}"
                content = content.replace(
                    placeholder, str(var_value)
                )

            # Increment usage count
            self.increment_usage_count(template_id)

            return content

        except Exception as e:
            logger.error(
                f"Error rendering template: {str(e)}"
            )
            return ""


# Example usage and testing
if __name__ == "__main__":
    # Setup logging for testing
    logging.basicConfig(level=logging.INFO)

    # Create template manager instance
    template_manager = TemplateManagementTools(
        templates_dir="test_templates"
    )

    print("Testing TemplateManagementTools:")

    # List templates
    templates = template_manager.list_templates()
    print(f"Available templates: {len(templates)}")
    for template in templates:
        print(
            f"  - {template['name']} (ID: {template['id']})"
        )

    # Test rendering
    if templates:
        template_id = templates[0]["id"]
        variables = {
            "title": "Test Blog Post",
            "introduction": "This is a test introduction.",
            "main_content": "This is the main content of the blog post.",
            "key_points": "• Point 1\n• Point 2\n• Point 3",
            "conclusion": "This is the conclusion.",
            "publish_date": datetime.now().strftime(
                "%Y-%m-%d"
            ),
            "tags": "test, example, blog",
            "source_url": "https://example.com",
        }

        rendered = template_manager.render_template(
            template_id, variables
        )
        print(f"\nRendered template:\n{rendered}")

    # Test feedback processing
    feedback = "The introduction is too long and the conclusion needs more detail."
    result = template_manager.update_template_from_feedback(
        "default", feedback, False
    )
    print(f"\nFeedback processing result: {result}")

    # Clean up test directory
    import shutil

    if os.path.exists("test_templates"):
        shutil.rmtree("test_templates")
