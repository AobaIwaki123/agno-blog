from agno.agent import Agent
from agno.models.anthropic import Claude

from src.tools.web_scraper import web_scraper_tool

url_processor_agent = Agent(
    name="URL Processor",
    model=Claude(id="claude-sonnet-4-0"),
    tools=[web_scraper_tool],
    instructions=[
        "Extract main content from provided URLs",
        "Identify key topics and themes",
        "Collect relevant metadata (title, author, date)",
        "Structure content for blog generation",
        "Return clean, well-formatted content with proper metadata",
    ],
    markdown=True,
)
