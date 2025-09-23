#!/usr/bin/env python3
"""
Test Agent Implementation

Test script to verify that agents are properly created and can be used.
"""

import os
import sys
import asyncio
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.factory import get_agent_factory
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_agent_creation():
    """Test agent creation."""
    logger.info("Testing agent creation...")
    
    factory = get_agent_factory()
    
    # Test URL Processor Agent
    logger.info("Creating URL Processor Agent...")
    url_agent = factory.create_url_processor_agent()
    if url_agent:
        logger.info("✅ URL Processor Agent created successfully")
    else:
        logger.error("❌ Failed to create URL Processor Agent")
    
    # Test Content Generator Agent
    logger.info("Creating Content Generator Agent...")
    content_agent = factory.create_content_generator_agent()
    if content_agent:
        logger.info("✅ Content Generator Agent created successfully")
    else:
        logger.error("❌ Failed to create Content Generator Agent")
    
    # Test Template Manager Agent
    logger.info("Creating Template Manager Agent...")
    template_agent = factory.create_template_manager_agent()
    if template_agent:
        logger.info("✅ Template Manager Agent created successfully")
    else:
        logger.error("❌ Failed to create Template Manager Agent")
    
    return url_agent, content_agent, template_agent


async def test_agent_basic_functionality():
    """Test basic agent functionality."""
    logger.info("Testing basic agent functionality...")
    
    factory = get_agent_factory()
    
    # Test URL Processor with a simple task
    url_agent = factory.create_url_processor_agent()
    if url_agent:
        try:
            logger.info("Testing URL Processor Agent with simple task...")
            result = await url_agent.arun("Hello, can you confirm you're working?")
            logger.info(f"✅ URL Processor Agent response: {result.content[:100]}...")
        except Exception as e:
            logger.error(f"❌ URL Processor Agent test failed: {e}")
    
    # Test Content Generator with a simple task
    content_agent = factory.create_content_generator_agent()
    if content_agent:
        try:
            logger.info("Testing Content Generator Agent with simple task...")
            result = await content_agent.arun("Generate a short test blog post about AI.")
            logger.info(f"✅ Content Generator Agent response: {result.content[:100]}...")
        except Exception as e:
            logger.error(f"❌ Content Generator Agent test failed: {e}")
    
    # Test Template Manager with a simple task
    template_agent = factory.create_template_manager_agent()
    if template_agent:
        try:
            logger.info("Testing Template Manager Agent with simple task...")
            result = await template_agent.arun("Analyze this feedback: 'The blog posts need more engaging introductions.'")
            logger.info(f"✅ Template Manager Agent response: {result.content[:100]}...")
        except Exception as e:
            logger.error(f"❌ Template Manager Agent test failed: {e}")


def check_environment():
    """Check environment variables."""
    logger.info("Checking environment variables...")
    
    if Config.ANTHROPIC_API_KEY:
        logger.info("✅ ANTHROPIC_API_KEY is set")
    else:
        logger.warning("⚠️ ANTHROPIC_API_KEY is not set")
    
    if Config.OPENAI_API_KEY:
        logger.info("✅ OPENAI_API_KEY is set")
    else:
        logger.warning("⚠️ OPENAI_API_KEY is not set")
    
    if hasattr(Config, 'DATABASE_URL') and Config.DATABASE_URL:
        logger.info("✅ DATABASE_URL is set")
    else:
        logger.warning("⚠️ DATABASE_URL is not set")


async def main():
    """Main test function."""
    logger.info("🚀 Starting Agent Implementation Test")
    
    # Check environment
    check_environment()
    
    # Test agent creation
    await test_agent_creation()
    
    # Test basic functionality
    await test_agent_basic_functionality()
    
    logger.info("🎉 Agent Implementation Test Complete")


if __name__ == "__main__":
    asyncio.run(main())
