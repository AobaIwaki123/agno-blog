import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import re

class WebScraperTool:
    """Web scraping tool for extracting content from URLs"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
    
    async def extract_content(self, url: str) -> Dict[str, Any]:
        """Extract main content from a given URL"""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Extract metadata
            metadata = self._extract_metadata(soup, url)
            
            return {
                "title": title,
                "content": content,
                "metadata": metadata,
                "url": url,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "url": url
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from the page"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Try h1 tag as fallback
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return "Untitled"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from the page"""
        # Try to find main content areas
        content_selectors = [
            'article',
            'main',
            '.content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '#content',
            '.main-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                return self._clean_text(content_elem.get_text())
        
        # Fallback to body content
        body = soup.find('body')
        if body:
            return self._clean_text(body.get_text())
        
        return ""
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata from the page"""
        metadata = {
            "url": url,
            "domain": urlparse(url).netloc,
            "author": None,
            "description": None,
            "published_date": None,
            "tags": []
        }
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata["description"] = meta_desc.get('content')
        
        # Extract author
        author_selectors = [
            'meta[name="author"]',
            '.author',
            '.byline',
            '[rel="author"]'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                if author_elem.name == 'meta':
                    metadata["author"] = author_elem.get('content')
                else:
                    metadata["author"] = author_elem.get_text().strip()
                break
        
        # Extract published date
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            '.published',
            '.date',
            'time[datetime]'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                if date_elem.name == 'meta':
                    metadata["published_date"] = date_elem.get('content')
                elif date_elem.get('datetime'):
                    metadata["published_date"] = date_elem.get('datetime')
                else:
                    metadata["published_date"] = date_elem.get_text().strip()
                break
        
        # Extract tags
        tag_selectors = [
            'meta[name="keywords"]',
            '.tags a',
            '.tag',
            '[rel="tag"]'
        ]
        
        for selector in tag_selectors:
            tag_elem = soup.select_one(selector)
            if tag_elem:
                if tag_elem.name == 'meta':
                    tags_text = tag_elem.get('content', '')
                    metadata["tags"] = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
                else:
                    metadata["tags"] = [tag.get_text().strip() for tag in soup.select(selector)]
                break
        
        return metadata
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()