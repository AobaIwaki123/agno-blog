import asyncio
import logging
import re
from typing import Any, Dict
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from httpx import HTTPTransport

# ログ設定
logger = logging.getLogger(__name__)


class WebScraperTool:
    """Web scraping tool for extracting content from URLs with enhanced error handling"""

    def __init__(self):
        # より詳細なタイムアウト設定
        timeout = httpx.Timeout(
            connect=10.0,  # 接続タイムアウト
            read=30.0,  # 読み取りタイムアウト
            write=10.0,  # 書き込みタイムアウト
            pool=5.0,  # プールタイムアウト
        )

        # リトライ機能付きトランスポート
        transport = HTTPTransport(retries=3)

        self.client = httpx.AsyncClient(
            timeout=timeout,
            transport=transport,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            },
        )

    async def extract_content(
        self, url: str
    ) -> Dict[str, Any]:
        """Extract main content from a given URL with enhanced error handling"""
        try:
            logger.info(
                f"Extracting content from URL: {url}"
            )
            response = await self.client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(
                response.content, "html.parser"
            )

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract title
            title = self._extract_title(soup)

            # Extract main content
            content = self._extract_main_content(soup)

            # Extract metadata
            metadata = self._extract_metadata(soup, url)

            logger.info(
                f"Successfully extracted content from {url}: {len(content)} characters"
            )

            return {
                "title": title,
                "content": content,
                "metadata": metadata,
                "url": url,
                "status": "success",
                "timestamp": asyncio.get_event_loop().time(),
            }

        except httpx.ConnectTimeout:
            logger.error(
                f"Connection timeout for URL: {url}"
            )
            return {
                "status": "error",
                "message": "Connection timeout - unable to connect to the server",
                "url": url,
                "error_type": "connect_timeout",
            }
        except httpx.ReadTimeout:
            logger.error(f"Read timeout for URL: {url}")
            return {
                "status": "error",
                "message": "Read timeout - server took too long to respond",
                "url": url,
                "error_type": "read_timeout",
            }
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error {e.response.status_code} for URL: {url}"
            )
            return {
                "status": "error",
                "message": f"HTTP {e.response.status_code} - {e.response.reason_phrase}",
                "url": url,
                "error_type": "http_error",
                "status_code": e.response.status_code,
            }
        except httpx.RequestError as e:
            logger.error(
                f"Request error for URL {url}: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Request failed: {str(e)}",
                "url": url,
                "error_type": "request_error",
            }
        except Exception as e:
            logger.error(
                f"Unexpected error for URL {url}: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "url": url,
                "error_type": "unexpected_error",
            }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from the page"""
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text().strip()

        # Try h1 tag as fallback
        h1_tag = soup.find("h1")
        if h1_tag:
            return h1_tag.get_text().strip()

        return "Untitled"

    def _extract_main_content(
        self, soup: BeautifulSoup
    ) -> str:
        """Extract main content from the page"""
        # Try to find main content areas
        content_selectors = [
            "article",
            "main",
            ".content",
            ".post-content",
            ".entry-content",
            ".article-content",
            "#content",
            ".main-content",
        ]

        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                return self._clean_text(
                    content_elem.get_text()
                )

        # Fallback to body content
        body = soup.find("body")
        if body:
            return self._clean_text(body.get_text())

        return ""

    def _extract_metadata(
        self, soup: BeautifulSoup, url: str
    ) -> Dict[str, Any]:
        """Extract metadata from the page"""
        metadata: Dict[str, Any] = {
            "url": url,
            "domain": urlparse(url).netloc,
            "author": None,
            "description": None,
            "published_date": None,
            "tags": [],
        }

        # Extract meta description
        meta_desc = soup.find(
            "meta", attrs={"name": "description"}
        )
        if meta_desc:
            metadata["description"] = meta_desc.get(
                "content"
            )

        # Extract author
        author_selectors = [
            'meta[name="author"]',
            ".author",
            ".byline",
            '[rel="author"]',
        ]

        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                if author_elem.name == "meta":
                    metadata["author"] = author_elem.get(
                        "content"
                    )
                else:
                    metadata["author"] = (
                        author_elem.get_text().strip()
                    )
                break

        # Extract published date
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            ".published",
            ".date",
            "time[datetime]",
        ]

        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                if date_elem.name == "meta":
                    metadata["published_date"] = (
                        date_elem.get("content")
                    )
                elif date_elem.get("datetime"):
                    metadata["published_date"] = (
                        date_elem.get("datetime")
                    )
                else:
                    metadata["published_date"] = (
                        date_elem.get_text().strip()
                    )
                break

        # Extract tags
        tag_selectors = [
            'meta[name="keywords"]',
            ".tags a",
            ".tag",
            '[rel="tag"]',
        ]

        for selector in tag_selectors:
            tag_elem = soup.select_one(selector)
            if tag_elem:
                if tag_elem.name == "meta":
                    tags_text = tag_elem.get("content", "")
                    metadata["tags"] = [
                        tag.strip()
                        for tag in tags_text.split(",")
                        if tag.strip()
                    ]
                else:
                    metadata["tags"] = [
                        tag.get_text().strip()
                        for tag in soup.select(selector)
                    ]
                break

        return metadata

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
