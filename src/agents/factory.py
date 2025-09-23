"""
Agent Factory Module

Centralized agent creation and configuration for the Agno Blog application.
"""

import logging
from typing import List, Optional

from agno.agent import Agent
from agno.models.anthropic import Claude

from config import Config
from database import get_database, get_knowledge
from tools.content_processor import ContentProcessingTools
from tools.template_manager import TemplateManagementTools
from tools.web_scraper import WebScrapingTools

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating and managing agents."""

    def __init__(self):
        self.db = get_database()
        self.knowledge = get_knowledge()
        self.web_scraper = WebScrapingTools()
        self.content_processor = ContentProcessingTools()
        self.template_manager = TemplateManagementTools()

    def create_url_processor_agent(self) -> Optional[Agent]:
        """Create the URL processor agent."""
        try:
            if not Config.ANTHROPIC_API_KEY:
                logger.warning(
                    "ANTHROPIC_API_KEY not set, URL processor agent unavailable"
                )
                return None

            agent = Agent(
                name="URL Processor",
                model=Claude(id="claude-sonnet-4-20250514"),
                tools=[
                    self.web_scraper,
                    self.content_processor,
                ],
                instructions=[
                    "Extract main content from provided URLs",
                    "Identify key topics and themes",
                    "Collect relevant metadata (title, author, date, etc.)",
                    "Clean and structure the extracted content",
                    "Provide a summary of the extracted content",
                ],
                db=self.db,
                enable_user_memories=True,
                markdown=True,
            )
            logger.info(
                "URL Processor agent created successfully"
            )
            return agent
        except Exception as e:
            logger.error(
                f"Failed to create URL Processor agent: {e}"
            )
            return None

    def create_content_generator_agent(
        self,
    ) -> Optional[Agent]:
        """Create the content generator agent."""
        try:
            if not Config.ANTHROPIC_API_KEY:
                logger.warning(
                    "ANTHROPIC_API_KEY not set, content generator agent unavailable"
                )
                return None

            agent = Agent(
                name="Content Generator",
                model=Claude(id="claude-sonnet-4-20250514"),
                tools=[
                    self.template_manager,
                    self.content_processor,
                ],
                instructions=[
                    "Generate engaging blog posts using provided templates",
                    "Maintain consistent tone and style",
                    "Optimize for SEO and readability",
                    "Include relevant metadata and tags",
                    "Format content appropriately for web publication",
                ],
                db=self.db,
                knowledge=self.knowledge,
                markdown=True,
            )
            logger.info(
                "Content Generator agent created successfully"
            )
            return agent
        except Exception as e:
            logger.error(
                f"Failed to create Content Generator agent: {e}"
            )
            return None

    def create_template_manager_agent(
        self,
    ) -> Optional[Agent]:
        """Create the template manager agent."""
        try:
            if not Config.ANTHROPIC_API_KEY:
                logger.warning(
                    "ANTHROPIC_API_KEY not set, template manager agent unavailable"
                )
                return None

            agent = Agent(
                name="Template Manager",
                model=Claude(id="claude-sonnet-4-20250514"),
                tools=[self.template_manager],
                instructions=[
                    "Analyze user feedback on generated content",
                    "Identify patterns in feedback to improve templates",
                    "Update templates while maintaining consistency",
                    "Always ask for user confirmation before updating templates",
                    "Track template versions and changes",
                ],
                db=self.db,
                markdown=True,
            )
            logger.info(
                "Template Manager agent created successfully"
            )
            return agent
        except Exception as e:
            logger.error(
                f"Failed to create Template Manager agent: {e}"
            )
            return None

    def create_all_agents(self) -> List[Agent]:
        """Create all available agents."""
        agents = []

        # Create agents
        url_processor = self.create_url_processor_agent()
        content_generator = (
            self.create_content_generator_agent()
        )
        template_manager = (
            self.create_template_manager_agent()
        )

        # Add successfully created agents to the list
        for agent in [
            url_processor,
            content_generator,
            template_manager,
        ]:
            if agent is not None:
                agents.append(agent)

        logger.info(
            f"Created {len(agents)} agents successfully"
        )
        return agents


# Global agent factory instance
_agent_factory = AgentFactory()


def get_agent_factory() -> AgentFactory:
    """Get the agent factory instance."""
    return _agent_factory


def create_agents() -> List[Agent]:
    """Create all agents."""
    return _agent_factory.create_all_agents()
