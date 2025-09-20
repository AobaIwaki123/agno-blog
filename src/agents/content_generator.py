from agno.agent import Agent
from agno.models.openai import OpenAIChat

from src.tools.template_loader import template_loader_tool

content_generator_agent = Agent(
    name="Content Generator",
    model=OpenAIChat(id="gpt-5-mini"),
    tools=[template_loader_tool],
    instructions=[
        "Generate blog posts using provided templates",
        "Maintain consistent tone and style",
        "Optimize for SEO and readability",
        "Include relevant metadata and tags",
        "Ensure content is engaging and well-structured",
        "Use markdown formatting for better presentation",
    ],
    markdown=True,
)
