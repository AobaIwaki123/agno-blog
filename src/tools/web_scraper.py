import re

import httpx
from agno.tools import Tool
from bs4 import BeautifulSoup


@Tool
async def web_scraper_tool(url: str) -> dict:
    """Extract content from a given URL"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()

            soup = BeautifulSoup(
                response.text, "html.parser"
            )

            # Remove unwanted elements
            for element in soup(
                [
                    "script",
                    "style",
                    "nav",
                    "footer",
                    "header",
                ]
            ):
                element.decompose()

            # Extract title
            title = soup.title.string if soup.title else ""

            # Extract main content
            main_content = (
                soup.find("main")
                or soup.find("article")
                or soup.find(
                    "div",
                    class_=re.compile(
                        r"content|main|article"
                    ),
                )
            )
            if main_content:
                content = main_content.get_text(
                    separator="\n\n", strip=True
                )
            else:
                content = soup.get_text(
                    separator="\n\n", strip=True
                )

            # Clean up content
            content = re.sub(r"\n{3,}", "\n\n", content)
            content = re.sub(r"\s{2,}", " ", content)

            return {
                "title": title,
                "content": content,
                "url": url,
                "status": "success",
                "metadata": {
                    "source": "web_scraper",
                    "content_length": len(content),
                    "title_length": len(title),
                },
            }

    except httpx.RequestError as e:
        return {
            "status": "error",
            "message": f"Request failed: {str(e)}",
            "url": url,
        }
    except httpx.HTTPStatusError as e:
        return {
            "status": "error",
            "message": f"HTTP error: {e.response.status_code}",
            "url": url,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "url": url,
        }
