import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.knowledge.embedder.cohere import CohereEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.anthropic import Claude
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from agno.vectordb.lancedb import LanceDb, SearchType

from ..models.blog_post import BlogPost, BlogPostStatus
from ..tools.content_formatter import ContentFormatterTool

# ログ設定
logger = logging.getLogger(__name__)


class ContentGeneratorAgent:
    """Agent responsible for generating blog posts from extracted content with enhanced capabilities"""

    def __init__(self, db: SqliteDb):
        self.db = db
        self.content_formatter = ContentFormatterTool()

        # ナレッジベースの設定（オプション）
        try:
            self.knowledge = Knowledge(
                vector_db=LanceDb(
                    uri="tmp/lancedb",
                    table_name="blog_knowledge",
                    search_type=SearchType.hybrid,
                    embedder=CohereEmbedder(
                        id="embed-v4.0"
                    ),
                ),
            )
            logger.info(
                "Knowledge base initialized successfully"
            )
        except Exception as e:
            logger.warning(
                f"Failed to initialize knowledge base: {e}"
            )
            self.knowledge = None

        # 最適化されたAgent設定
        self.agent = Agent(
            name="Content Generator",
            role="Generate engaging blog posts from extracted content",
            model=Claude(id="claude-sonnet-4-0"),
            db=db,
            knowledge=self.knowledge,  # ナレッジベースを追加
            tools=[
                DuckDuckGoTools(),  # リアルタイム情報検索
                HackerNewsTools(),  # 技術トレンド情報
            ],
            instructions=[
                "Generate engaging and well-structured blog posts",
                "Use knowledge base to enhance content with relevant information",
                "Search for latest trends and information when needed",
                "Maintain consistent tone and style throughout the post",
                "Optimize content for SEO and readability",
                "Include relevant metadata and tags",
                "Create compelling titles and introductions",
                "Structure content with proper headings and sections",
                "Add value through analysis and insights",
                "Ensure content is original and engaging",
                "Use tools to gather additional context when beneficial",
            ],
            enable_user_memories=True,
            add_history_to_context=True,
            num_history_runs=5,  # より多くの履歴を保持
            markdown=True,
        )

    async def generate_blog_post(
        self,
        url_data: Dict[str, Any],
        template: Optional[str] = None,
        custom_instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a blog post from processed URL data"""
        try:
            analysis = url_data.get("analysis", {})
            original_content = url_data.get(
                "original_content", ""
            )
            metadata = url_data.get("metadata", {})

            # Prepare generation prompt
            generation_prompt = f"""
            以下の情報を基に、魅力的なブログ記事を生成してください。

            **元のコンテンツ情報:**
            - タイトル: {analysis.get("title", "不明")}
            - 要約: {analysis.get("summary", "")}
            - キーポイント: {", ".join(analysis.get("key_points", []))}
            - カテゴリ: {analysis.get("category", "一般")}
            - タグ: {", ".join(analysis.get("tags", []))}
            - 推定読了時間: {analysis.get("reading_time", "5")}分

            **元のコンテンツ:**
            {original_content[:3000]}

            **メタデータ:**
            {json.dumps(metadata, ensure_ascii=False, indent=2)}

            **カスタム指示:**
            {custom_instructions or "特に指定なし"}

            以下の形式でブログ記事を生成してください：

            # [魅力的なタイトル]

            ## はじめに
            [記事の導入部分 - 読者の興味を引く内容]

            ## 主要内容
            [元のコンテンツを基にした、構造化された内容]

            ## まとめ
            [記事の要点をまとめた結論部分]

            ---
            *この記事は {url_data.get("url_source", "不明なソース")} から自動生成されました。*
            *生成日時: {datetime.now().strftime("%Y年%m月%d日 %H:%M")}*

            **タグ:** {", ".join(analysis.get("tags", []))}
            **カテゴリ:** {analysis.get("category", "一般")}
            **読了時間:** 約{analysis.get("reading_time", "5")}分
            """

            # Generate content using the agent
            response = await self.agent.arun(
                generation_prompt
            )
            generated_content = response.content

            # Create blog post object
            blog_post = BlogPost(
                id=str(uuid.uuid4()),
                title=analysis.get("title", "Untitled"),
                content=generated_content,
                url_source=url_data.get("url_source"),
                template_used=template or "default",
                status=BlogPostStatus.DRAFT,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=analysis.get("tags", []),
                metadata={
                    "original_metadata": metadata,
                    "analysis": analysis,
                    "generation_timestamp": datetime.now().isoformat(),
                    "reading_time": analysis.get(
                        "reading_time", "5"
                    ),
                    "category": analysis.get(
                        "category", "一般"
                    ),
                },
            )

            return {
                "status": "success",
                "blog_post": blog_post,
                "message": "Blog post generated successfully",
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error generating blog post: {str(e)}",
            }

    async def improve_blog_post(
        self, blog_post: BlogPost, feedback: str
    ) -> Dict[str, Any]:
        """Improve an existing blog post based on feedback"""
        try:
            improvement_prompt = f"""
            以下のブログ記事を、ユーザーフィードバックに基づいて改善してください。

            **現在のブログ記事:**
            {blog_post.content}

            **ユーザーフィードバック:**
            {feedback}

            改善されたブログ記事を生成してください。フィードバックの内容を反映し、
            より良い記事になるように修正してください。
            """

            # Get improved content from the agent
            response = await self.agent.arun(
                improvement_prompt
            )
            improved_content = response.content

            # Update the blog post
            blog_post.content = improved_content
            blog_post.updated_at = datetime.now()
            blog_post.user_feedback = {
                "feedback": feedback,
                "improvement_timestamp": datetime.now().isoformat(),
            }

            return {
                "status": "success",
                "blog_post": blog_post,
                "message": "Blog post improved successfully",
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error improving blog post: {str(e)}",
            }

    async def generate_multiple_variants_parallel(
        self, url_data: Dict[str, Any], count: int = 3
    ) -> Dict[str, Any]:
        """並列で複数のバリエーションを生成"""
        try:
            logger.info(
                f"Generating {count} variants in parallel"
            )
            # 並列実行用のタスクを作成
            tasks = []
            for i in range(count):
                task = self._generate_single_variant(
                    url_data, i + 1
                )
                tasks.append(task)

            # 並列実行
            variants = await asyncio.gather(
                *tasks, return_exceptions=True
            )

            # エラーハンドリング
            valid_variants = []
            for i, variant in enumerate(variants):
                if isinstance(variant, Exception):
                    logger.error(
                        f"Variant {i + 1} generation failed: {variant}"
                    )
                else:
                    valid_variants.append(variant)

            logger.info(
                f"Successfully generated {len(valid_variants)} variants"
            )
            return {
                "status": "success",
                "variants": valid_variants,
                "message": f"Generated {len(valid_variants)} variants successfully",
            }

        except Exception as e:
            logger.error(
                f"Error generating variants: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Error generating variants: {str(e)}",
            }

    async def _generate_single_variant(
        self, url_data: Dict[str, Any], variant_number: int
    ) -> Dict[str, Any]:
        """単一のバリエーションを生成"""
        try:
            variant_prompt = f"""
            以下の情報を基に、バリエーション{variant_number}のブログ記事を生成してください。
            各バリエーションは異なるアプローチやトーンで書いてください。

            **元のコンテンツ情報:**
            - タイトル: {url_data.get("analysis", {}).get("title", "不明")}
            - 要約: {url_data.get("analysis", {}).get("summary", "")}
            - キーポイント: {", ".join(url_data.get("analysis", {}).get("key_points", []))}

            **バリエーション{variant_number}の指示:**
            {self._get_variant_instructions(variant_number)}

            魅力的なブログ記事を生成してください。
            """

            response = await self.agent.arun(variant_prompt)

            return {
                "variant_number": variant_number,
                "content": response.content,
                "instructions": self._get_variant_instructions(
                    variant_number
                ),
            }
        except Exception as e:
            logger.error(
                f"Error generating variant {variant_number}: {str(e)}"
            )
            raise e

    async def generate_multiple_variants(
        self, url_data: Dict[str, Any], count: int = 3
    ) -> Dict[str, Any]:
        """Generate multiple variants of a blog post (legacy method for backward compatibility)"""
        return (
            await self.generate_multiple_variants_parallel(
                url_data, count
            )
        )

    def _get_variant_instructions(
        self, variant_number: int
    ) -> str:
        """Get specific instructions for each variant"""
        instructions = {
            1: "技術的で詳細なアプローチで、専門的な内容を重視してください。",
            2: "初心者向けの分かりやすいアプローチで、親しみやすいトーンで書いてください。",
            3: "実用的でアクション指向のアプローチで、読者がすぐに実践できる内容にしてください。",
        }
        return instructions.get(
            variant_number,
            "バランスの取れたアプローチで書いてください。",
        )
