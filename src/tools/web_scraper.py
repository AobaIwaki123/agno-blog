"""
Web Scraping Tools for Blog Content Extraction

This module provides tools for extracting content from web URLs,
cleaning the content, and preparing it for blog post generation.
"""

import httpx
import re
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

class WebScrapingTools:
    """Custom web scraping tools for blog content extraction."""
    
    def __init__(self, timeout: int = 30, max_content_length: int = 50000):
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.session = httpx.Client(
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
    
    def extract_content(self, url: str) -> Dict[str, Any]:
        """
        Extract main content from a URL.
        
        Args:
            url: The URL to extract content from
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        try:
            logger.info(f"Extracting content from URL: {url}")
            
            # Validate URL
            if not self._is_valid_url(url):
                return {"status": "error", "message": "Invalid URL format"}
            
            # Fetch the webpage
            response = self.session.get(url)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract various content elements
            title = self._extract_title(soup)
            content = self._extract_main_content(soup)
            metadata = self._extract_metadata(soup, url)
            
            # Clean and process content
            clean_content = self._clean_content(content)
            
            # Validate content length
            if len(clean_content) > self.max_content_length:
                clean_content = clean_content[:self.max_content_length] + "..."
                logger.warning(f"Content truncated to {self.max_content_length} characters")
            
            result = {
                "title": title,
                "content": clean_content,
                "url": url,
                "metadata": metadata,
                "extracted_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
            logger.info(f"Successfully extracted content from {url}")
            return result
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.reason_phrase}"
            logger.error(f"HTTP error extracting from {url}: {error_msg}")
            return {"status": "error", "message": error_msg, "url": url}
            
        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(f"Request error extracting from {url}: {error_msg}")
            return {"status": "error", "message": error_msg, "url": url}
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error extracting from {url}: {error_msg}")
            return {"status": "error", "message": error_msg, "url": url}
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate if the URL is properly formatted."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the page title."""
        # Try different title sources in order of preference
        title_selectors = [
            'h1',  # Main heading
            'title',  # HTML title tag
            '.title, .post-title, .entry-title',  # Common title classes
            '[property="og:title"]',  # Open Graph title
            '[name="twitter:title"]'  # Twitter Card title
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title and len(title) > 5:  # Ensure it's not too short
                    return self._clean_text(title)
        
        # Fallback to URL-based title
        return "Untitled Article"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract the main content from the page."""
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
            element.decompose()
        
        # Try content selectors in order of preference
        content_selectors = [
            'article',
            'main',
            '.content, .post-content, .entry-content',
            '.article-content, .article-body',
            '[role="main"]',
            '.main-content',
            '#content, #main'
        ]
        
        content = ""
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get_text().strip()
                if len(content) > 200:  # Ensure substantial content
                    break
        
        # Fallback to body content if no specific content area found
        if not content or len(content) < 200:
            body = soup.find('body')
            if body:
                content = body.get_text().strip()
        
        return content
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata from the page."""
        metadata = {
            "url": url,
            "domain": urlparse(url).netloc
        }
        
        # Extract meta tags
        meta_tags = {
            "description": ['meta[name="description"]', 'meta[property="og:description"]'],
            "author": ['meta[name="author"]', 'meta[property="article:author"]'],
            "published_date": ['meta[property="article:published_time"]', 'meta[name="date"]'],
            "keywords": ['meta[name="keywords"]'],
            "image": ['meta[property="og:image"]', 'meta[name="twitter:image"]']
        }
        
        for key, selectors in meta_tags.items():
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get('content')
                    if content:
                        metadata[key] = content.strip()
                        break
        
        # Extract word count
        if 'content' in locals():
            words = len(re.findall(r'\b\w+\b', content))
            metadata['word_count'] = words
            metadata['estimated_reading_time'] = max(1, words // 200)  # ~200 words per minute
        
        return metadata
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content text."""
        if not content:
            return ""
        
        # Remove extra whitespace and normalize line breaks
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # Remove special characters that might cause issues
        content = re.sub(r'[^\w\s.,!?;:()\-"\']', '', content)
        
        # Remove repeated punctuation
        content = re.sub(r'([.!?]){2,}', r'\1', content)
        
        return content.strip()
    
    def _clean_text(self, text: str) -> str:
        """Clean text for titles and short content."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing punctuation and whitespace
        text = text.strip(' .,!?;:')
        
        return text
    
    def extract_links(self, url: str) -> List[Dict[str, str]]:
        """
        Extract all links from a webpage.
        
        Args:
            url: The URL to extract links from
            
        Returns:
            List of dictionaries containing link information
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text().strip()
                
                # Convert relative URLs to absolute
                absolute_url = urljoin(url, href)
                
                if self._is_valid_url(absolute_url) and text:
                    links.append({
                        "url": absolute_url,
                        "text": text,
                        "title": link.get('title', '')
                    })
            
            return links
            
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
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            images = []
            
            for img in soup.find_all('img', src=True):
                src = img['src']
                alt = img.get('alt', '')
                
                # Convert relative URLs to absolute
                absolute_url = urljoin(url, src)
                
                if self._is_valid_url(absolute_url):
                    images.append({
                        "url": absolute_url,
                        "alt": alt,
                        "title": img.get('title', '')
                    })
            
            return images
            
        except Exception as e:
            logger.error(f"Error extracting images from {url}: {str(e)}")
            return []
    
    def __del__(self):
        """Clean up the HTTP session."""
        if hasattr(self, 'session'):
            self.session.close()


# Example usage and testing
if __name__ == "__main__":
    # Setup logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Create scraper instance
    scraper = WebScrapingTools()
    
    # Test URLs
    test_urls = [
        "https://example.com",
        "https://httpbin.org/html"  # Test endpoint
    ]
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        result = scraper.extract_content(url)
        
        if result["status"] == "success":
            print(f"Title: {result['title']}")
            print(f"Content length: {len(result['content'])}")
            print(f"Metadata: {result['metadata']}")
        else:
            print(f"Error: {result['message']}")