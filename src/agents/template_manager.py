from agno.agent import Agent
from agno.models.anthropic import Claude

from src.tools.template_updater import template_updater_tool

template_manager_agent = Agent(
    name="Template Manager",
    model=Claude(id="claude-sonnet-4-0"),
    tools=[template_updater_tool],
    instructions=[
        "Analyze user feedback on generated content",
        "Identify patterns in feedback to improve templates",
        "Update templates while maintaining consistency",
        "Always confirm changes with user before updating",
        "Track template versions and changes",
        "Ensure templates produce high-quality blog content",
    ],
    markdown=True,
)
