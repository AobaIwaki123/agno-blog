"""
URL Processor Agent

This agent specializes in extracting and processing content from URLs.
It coordinates web scraping, content analysis, and metadata extraction.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.db.sqlite import SqliteDb

from tools.web_scraper import WebScrapingTools
from tools.content_processor import ContentProcessingTools

logger = logging.getLogger(__name__)

class URLProcessorAgent:
    """Agent specialized in URL content extraction and processing."""
    
    def __init__(self, db: SqliteDb):
        self.web_scraper = WebScrapingTools()
        self.content_processor = ContentProcessingTools()
        
        # Create the Agno agent
        self.agent = Agent(
            name="URL Processor",
            role="Extract and process content from URLs for blog post generation",
            model=Claude(id="claude-3-5-sonnet-20241022"),
            tools=[self._create_url_extraction_tool(), self._create_content_analysis_tool()],
            instructions=[
                "You are a specialized agent for extracting and processing content from URLs.",
                "Your primary responsibilities:",
                "1. Extract clean, readable content from web pages",
                "2. Identify key topics, themes, and important information",
                "3. Generate structured summaries and metadata",
                "4. Provide content analysis including keywords and readability metrics",
                "5. Handle errors gracefully and provide meaningful feedback",
                "",
                "When processing URLs:",
                "- Always validate the URL before processing",
                "- Extract the main content, avoiding navigation, ads, and other noise",
                "- Identify the article title, author, publication date if available",
                "- Generate a concise summary of the key points",
                "- Extract relevant keywords and topics",
                "- Provide metadata about content length, reading time, etc.",
                "",
                "Be thorough but efficient. Focus on quality content extraction.",
                "If a URL cannot be processed, explain why and suggest alternatives."
            ],
            db=db,
            enable_user_memories=True,
            markdown=True,
        )
    
    def _create_url_extraction_tool(self):
        """Create a tool for URL content extraction."""
        def extract_url_content(url: str) -> Dict[str, Any]:
            """
            Extract content from a given URL.
            
            Args:
                url: The URL to extract content from
                
            Returns:
                Dictionary containing extracted content and metadata
            """
            try:
                logger.info(f"URL Processor Agent: Extracting content from {url}")
                
                # Use web scraper to extract content
                extraction_result = self.web_scraper.extract_content(url)
                
                if extraction_result["status"] != "success":
                    return {
                        "status": "error",
                        "message": f"Failed to extract content: {extraction_result.get('message', 'Unknown error')}",
                        "url": url
                    }
                
                # Process the extracted content
                raw_content = extraction_result["content"]
                title = extraction_result["title"]
                metadata = extraction_result["metadata"]
                
                # Clean and analyze content
                clean_content = self.content_processor.clean_content(raw_content)
                content_analysis = self.content_processor.analyze_content_structure(clean_content)
                keywords = self.content_processor.extract_keywords(clean_content, max_keywords=10)
                summary = self.content_processor.generate_summary(clean_content, max_length=300)
                entities = self.content_processor.extract_entities(clean_content)
                
                # Combine all information
                result = {
                    "status": "success",
                    "url": url,
                    "title": title,
                    "content": clean_content,
                    "summary": summary,
                    "keywords": [kw[0] for kw in keywords],  # Extract just the keywords
                    "metadata": {
                        **metadata,
                        "content_analysis": content_analysis,
                        "entities": entities,
                        "processed_at": datetime.utcnow().isoformat()
                    }
                }
                
                logger.info(f"Successfully processed content from {url}")
                return result
                
            except Exception as e:
                logger.error(f"Error in URL extraction tool: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Unexpected error: {str(e)}",
                    "url": url
                }
        
        return extract_url_content
    
    def _create_content_analysis_tool(self):
        """Create a tool for advanced content analysis."""
        def analyze_extracted_content(content: str, title: str = "") -> Dict[str, Any]:
            """
            Perform advanced analysis on extracted content.
            
            Args:
                content: The extracted content to analyze
                title: Optional title of the content
                
            Returns:
                Dictionary containing detailed content analysis
            """
            try:
                logger.info("URL Processor Agent: Performing content analysis")
                
                if not content:
                    return {"status": "error", "message": "No content provided for analysis"}
                
                # Perform various analyses
                structure_analysis = self.content_processor.analyze_content_structure(content)
                keywords = self.content_processor.extract_keywords(content, max_keywords=15)
                entities = self.content_processor.extract_entities(content)
                sections = self.content_processor.split_into_sections(content, max_section_length=800)
                
                # Generate different length summaries
                short_summary = self.content_processor.generate_summary(content, max_length=150, sentences=2)
                medium_summary = self.content_processor.generate_summary(content, max_length=300, sentences=4)
                
                # Content quality indicators
                quality_indicators = {
                    "has_sufficient_content": structure_analysis["word_count"] >= 100,
                    "good_readability": structure_analysis["avg_words_per_sentence"] <= 25,
                    "well_structured": structure_analysis["paragraph_count"] >= 2,
                    "keyword_rich": len(keywords) >= 5
                }
                
                # Topic classification (simplified)
                topic_keywords = {
                    "technology": ["technology", "software", "programming", "computer", "digital", "ai", "machine learning"],
                    "business": ["business", "company", "market", "revenue", "profit", "strategy"],
                    "science": ["research", "study", "experiment", "data", "analysis", "scientific"],
                    "education": ["learn", "education", "tutorial", "guide", "course", "teaching"],
                    "news": ["news", "report", "announced", "today", "recently", "update"]
                }
                
                detected_topics = []
                content_lower = content.lower()
                for topic, topic_words in topic_keywords.items():
                    if any(word in content_lower for word in topic_words):
                        detected_topics.append(topic)
                
                result = {
                    "status": "success",
                    "structure_analysis": structure_analysis,
                    "keywords": keywords,
                    "entities": entities,
                    "sections": sections,
                    "summaries": {
                        "short": short_summary,
                        "medium": medium_summary
                    },
                    "quality_indicators": quality_indicators,
                    "detected_topics": detected_topics,
                    "content_hash": self.content_processor.generate_content_hash(content),
                    "analysis_timestamp": datetime.utcnow().isoformat()
                }
                
                logger.info("Content analysis completed successfully")
                return result
                
            except Exception as e:
                logger.error(f"Error in content analysis tool: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Analysis failed: {str(e)}"
                }
        
        return analyze_extracted_content
    
    async def process_url(self, url: str, additional_context: str = "") -> Dict[str, Any]:
        """
        Process a URL and extract content for blog post generation.
        
        Args:
            url: The URL to process
            additional_context: Additional context or instructions
            
        Returns:
            Dictionary containing processed content and analysis
        """
        try:
            logger.info(f"URL Processor Agent: Starting to process URL: {url}")
            
            # Prepare the prompt for the agent
            prompt = f"""
            Please process the following URL and extract content suitable for blog post generation:
            
            URL: {url}
            
            {f"Additional context: {additional_context}" if additional_context else ""}
            
            Please:
            1. Extract the main content from the URL
            2. Analyze the content structure and quality
            3. Generate a summary and identify key topics
            4. Provide metadata and recommendations for blog post creation
            
            Use the available tools to extract and analyze the content thoroughly.
            """
            
            # Run the agent
            response = await self.agent.arun(prompt)
            
            logger.info(f"URL Processor Agent: Completed processing URL: {url}")
            
            return {
                "status": "success",
                "agent_response": response.content,
                "url": url,
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "url": url
            }
    
    def extract_links_from_url(self, url: str) -> List[Dict[str, str]]:
        """
        Extract all links from a webpage for potential follow-up processing.
        
        Args:
            url: The URL to extract links from
            
        Returns:
            List of dictionaries containing link information
        """
        try:
            logger.info(f"Extracting links from {url}")
            return self.web_scraper.extract_links(url)
        except Exception as e:
            logger.error(f"Error extracting links from {url}: {str(e)}")
            return []
    
    def get_page_images(self, url: str) -> List[Dict[str, str]]:
        """
        Extract images from a webpage.
        
        Args:
            url: The URL to extract images from
            
        Returns:
            List of dictionaries containing image information
        """
        try:
            logger.info(f"Extracting images from {url}")
            return self.web_scraper.get_page_images(url)
        except Exception as e:
            logger.error(f"Error extracting images from {url}: {str(e)}")
            return []
    
    def batch_process_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple URLs in batch.
        
        Args:
            urls: List of URLs to process
            
        Returns:
            List of processing results
        """
        results = []
        
        for url in urls:
            try:
                result = self.web_scraper.extract_content(url)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing URL {url}: {str(e)}")
                results.append({
                    "status": "error",
                    "url": url,
                    "message": str(e)
                })
        
        return results
    
    def validate_url(self, url: str) -> Dict[str, Any]:
        """
        Validate if a URL is accessible and suitable for content extraction.
        
        Args:
            url: The URL to validate
            
        Returns:
            Dictionary containing validation results
        """
        try:
            # Basic URL format validation
            from urllib.parse import urlparse
            parsed = urlparse(url)
            
            if not all([parsed.scheme, parsed.netloc]):
                return {
                    "valid": False,
                    "message": "Invalid URL format"
                }
            
            # Try to access the URL
            import httpx
            with httpx.Client(timeout=10) as client:
                response = client.head(url)
                
                return {
                    "valid": True,
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type", ""),
                    "accessible": response.status_code == 200
                }
                
        except Exception as e:
            return {
                "valid": False,
                "message": f"URL validation failed: {str(e)}"
            }


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from agno.db.sqlite import SqliteDb
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create database
    db = SqliteDb(db_file="test_url_processor.db")
    
    # Create URL processor agent
    url_processor = URLProcessorAgent(db)
    
    async def test_url_processor():
        # Test URL validation
        test_url = "https://httpbin.org/html"
        validation = url_processor.validate_url(test_url)
        print(f"URL validation result: {validation}")
        
        if validation.get("valid", False):
            # Test URL processing
            result = await url_processor.process_url(test_url)
            print(f"URL processing result: {result['status']}")
            
            if result["status"] == "success":
                print(f"Agent response: {result['agent_response'][:200]}...")
        
        # Clean up
        import os
        if os.path.exists("test_url_processor.db"):
            os.remove("test_url_processor.db")
    
    # Run test
    asyncio.run(test_url_processor())