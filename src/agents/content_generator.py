from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.db.sqlite import SqliteDb
from typing import Dict, Any, Optional
import json
import uuid
from datetime import datetime
from ..tools.content_formatter import ContentFormatterTool
from ..models.blog_post import BlogPost, BlogPostStatus

class ContentGeneratorAgent:
    """Agent responsible for generating blog posts from extracted content"""
    
    def __init__(self, db: SqliteDb):
        self.db = db
        self.content_formatter = ContentFormatterTool()
        
        # Create the Agno Agent
        self.agent = Agent(
            name="Content Generator",
            role="Generate engaging blog posts from extracted content",
            model=Claude(id="claude-sonnet-4-0"),
            db=db,
            instructions=[
                "Generate engaging and well-structured blog posts",
                "Maintain consistent tone and style throughout the post",
                "Optimize content for SEO and readability",
                "Include relevant metadata and tags",
                "Create compelling titles and introductions",
                "Structure content with proper headings and sections",
                "Add value through analysis and insights",
                "Ensure content is original and engaging"
            ],
            enable_user_memories=True,
            add_history_to_context=True,
            markdown=True,
        )
    
    async def generate_blog_post(self, 
                                url_data: Dict[str, Any], 
                                template: Optional[str] = None,
                                custom_instructions: Optional[str] = None) -> Dict[str, Any]:
        """Generate a blog post from processed URL data"""
        try:
            analysis = url_data.get('analysis', {})
            original_content = url_data.get('original_content', '')
            metadata = url_data.get('metadata', {})
            
            # Prepare generation prompt
            generation_prompt = f"""
            以下の情報を基に、魅力的なブログ記事を生成してください。

            **元のコンテンツ情報:**
            - タイトル: {analysis.get('title', '不明')}
            - 要約: {analysis.get('summary', '')}
            - キーポイント: {', '.join(analysis.get('key_points', []))}
            - カテゴリ: {analysis.get('category', '一般')}
            - タグ: {', '.join(analysis.get('tags', []))}
            - 推定読了時間: {analysis.get('reading_time', '5')}分

            **元のコンテンツ:**
            {original_content[:3000]}

            **メタデータ:**
            {json.dumps(metadata, ensure_ascii=False, indent=2)}

            **カスタム指示:**
            {custom_instructions or '特に指定なし'}

            以下の形式でブログ記事を生成してください：

            # [魅力的なタイトル]

            ## はじめに
            [記事の導入部分 - 読者の興味を引く内容]

            ## 主要内容
            [元のコンテンツを基にした、構造化された内容]

            ## まとめ
            [記事の要点をまとめた結論部分]

            ---
            *この記事は {url_data.get('url_source', '不明なソース')} から自動生成されました。*
            *生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}*

            **タグ:** {', '.join(analysis.get('tags', []))}
            **カテゴリ:** {analysis.get('category', '一般')}
            **読了時間:** 約{analysis.get('reading_time', '5')}分
            """
            
            # Generate content using the agent
            response = await self.agent.arun(generation_prompt)
            generated_content = response.content
            
            # Create blog post object
            blog_post = BlogPost(
                id=str(uuid.uuid4()),
                title=analysis.get('title', 'Untitled'),
                content=generated_content,
                url_source=url_data.get('url_source'),
                template_used=template or 'default',
                status=BlogPostStatus.DRAFT,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=analysis.get('tags', []),
                metadata={
                    'original_metadata': metadata,
                    'analysis': analysis,
                    'generation_timestamp': datetime.now().isoformat(),
                    'reading_time': analysis.get('reading_time', '5'),
                    'category': analysis.get('category', '一般')
                }
            )
            
            return {
                "status": "success",
                "blog_post": blog_post,
                "message": "Blog post generated successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error generating blog post: {str(e)}"
            }
    
    async def improve_blog_post(self, 
                               blog_post: BlogPost, 
                               feedback: str) -> Dict[str, Any]:
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
            response = await self.agent.arun(improvement_prompt)
            improved_content = response.content
            
            # Update the blog post
            blog_post.content = improved_content
            blog_post.updated_at = datetime.now()
            blog_post.user_feedback = {
                "feedback": feedback,
                "improvement_timestamp": datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "blog_post": blog_post,
                "message": "Blog post improved successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error improving blog post: {str(e)}"
            }
    
    async def generate_multiple_variants(self, 
                                       url_data: Dict[str, Any], 
                                       count: int = 3) -> Dict[str, Any]:
        """Generate multiple variants of a blog post"""
        variants = []
        
        for i in range(count):
            variant_prompt = f"""
            以下の情報を基に、バリエーション{i+1}のブログ記事を生成してください。
            各バリエーションは異なるアプローチやトーンで書いてください。

            **元のコンテンツ情報:**
            - タイトル: {url_data.get('analysis', {}).get('title', '不明')}
            - 要約: {url_data.get('analysis', {}).get('summary', '')}
            - キーポイント: {', '.join(url_data.get('analysis', {}).get('key_points', []))}

            **バリエーション{i+1}の指示:**
            {self._get_variant_instructions(i+1)}

            魅力的なブログ記事を生成してください。
            """
            
            response = await self.agent.arun(variant_prompt)
            
            variants.append({
                "variant_number": i + 1,
                "content": response.content,
                "instructions": self._get_variant_instructions(i+1)
            })
        
        return {
            "status": "success",
            "variants": variants,
            "message": f"Generated {count} variants successfully"
        }
    
    def _get_variant_instructions(self, variant_number: int) -> str:
        """Get specific instructions for each variant"""
        instructions = {
            1: "技術的で詳細なアプローチで、専門的な内容を重視してください。",
            2: "初心者向けの分かりやすいアプローチで、親しみやすいトーンで書いてください。",
            3: "実用的でアクション指向のアプローチで、読者がすぐに実践できる内容にしてください。"
        }
        return instructions.get(variant_number, "バランスの取れたアプローチで書いてください。")