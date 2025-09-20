from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.db.sqlite import SqliteDb
from typing import Dict, Any
import asyncio
import json
from ..tools.web_scraper import WebScraperTool
from ..models.blog_post import BlogPost, BlogPostStatus

class URLProcessorAgent:
    """Agent responsible for processing URLs and extracting content"""
    
    def __init__(self, db: SqliteDb):
        self.db = db
        self.web_scraper = WebScraperTool()
        
        # Create the Agno Agent
        self.agent = Agent(
            name="URL Processor",
            role="Extract and process content from URLs for blog generation",
            model=Claude(id="claude-sonnet-4-0"),
            db=db,
            instructions=[
                "Extract main content from provided URLs",
                "Identify key topics and themes in the content",
                "Collect relevant metadata (title, author, date, tags, etc.)",
                "Clean and structure the extracted content for blog generation",
                "Identify the main points and key information",
                "Determine the appropriate category and tags for the content",
                "Provide a summary of the extracted content"
            ],
            enable_user_memories=True,
            add_history_to_context=True,
            markdown=True,
        )
    
    async def process_url(self, url: str) -> Dict[str, Any]:
        """Process a URL and extract content for blog generation"""
        try:
            # Extract content from URL
            extraction_result = await self.web_scraper.extract_content(url)
            
            if extraction_result["status"] != "success":
                return {
                    "status": "error",
                    "message": f"Failed to extract content: {extraction_result.get('message', 'Unknown error')}",
                    "url": url
                }
            
            # Use the agent to analyze and structure the content
            analysis_prompt = f"""
            以下のURLから抽出したコンテンツを分析し、ブログ記事生成に適した形に構造化してください。

            URL: {url}
            タイトル: {extraction_result['title']}
            コンテンツ: {extraction_result['content'][:2000]}...
            メタデータ: {json.dumps(extraction_result['metadata'], ensure_ascii=False, indent=2)}

            以下の形式でJSONレスポンスを返してください：
            {{
                "title": "ブログ記事のタイトル",
                "summary": "記事の要約（200文字以内）",
                "key_points": ["ポイント1", "ポイント2", "ポイント3"],
                "category": "カテゴリ名",
                "tags": ["タグ1", "タグ2", "タグ3"],
                "structured_content": "構造化されたコンテンツ",
                "seo_keywords": ["キーワード1", "キーワード2"],
                "reading_time": "推定読了時間（分）"
            }}
            """
            
            # Get analysis from the agent
            response = await self.agent.arun(analysis_prompt)
            
            # Parse the response (assuming it's JSON)
            try:
                analysis = json.loads(response.content)
            except json.JSONDecodeError:
                # If not JSON, create a basic structure
                analysis = {
                    "title": extraction_result['title'],
                    "summary": extraction_result['content'][:200] + "...",
                    "key_points": [],
                    "category": "一般",
                    "tags": extraction_result['metadata'].get('tags', []),
                    "structured_content": extraction_result['content'],
                    "seo_keywords": [],
                    "reading_time": "5"
                }
            
            # Create blog post data
            blog_data = {
                "url_source": url,
                "original_title": extraction_result['title'],
                "original_content": extraction_result['content'],
                "metadata": extraction_result['metadata'],
                "analysis": analysis,
                "extraction_timestamp": extraction_result.get('timestamp', None)
            }
            
            return {
                "status": "success",
                "data": blog_data,
                "message": "URL processed successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing URL: {str(e)}",
                "url": url
            }
    
    async def batch_process_urls(self, urls: list) -> Dict[str, Any]:
        """Process multiple URLs in batch"""
        results = []
        
        for url in urls:
            result = await self.process_url(url)
            results.append({
                "url": url,
                "result": result
            })
        
        return {
            "status": "completed",
            "results": results,
            "total_processed": len(urls)
        }
    
    async def close(self):
        """Clean up resources"""
        await self.web_scraper.close()