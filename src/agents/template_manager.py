from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.db.sqlite import SqliteDb
from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime
from ..models.blog_post import BlogTemplate

class TemplateManagerAgent:
    """Agent responsible for managing blog post templates"""
    
    def __init__(self, db: SqliteDb):
        self.db = db
        
        # Create the Agno Agent
        self.agent = Agent(
            name="Template Manager",
            role="Manage and update blog post templates based on user feedback",
            model=Claude(id="claude-sonnet-4-0"),
            db=db,
            instructions=[
                "Analyze user feedback on generated content",
                "Identify patterns in feedback to improve templates",
                "Update templates while maintaining consistency",
                "Track template versions and changes",
                "Ensure templates produce high-quality blog posts",
                "Adapt templates based on content type and category"
            ],
            enable_user_memories=True,
            add_history_to_context=True,
            markdown=True,
        )
        
        # Initialize default templates
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default blog post templates"""
        self.default_templates = {
            "general": """# {title}

## はじめに
{introduction}

## 主要内容
{main_content}

## まとめ
{conclusion}

---
*この記事は {url_source} から自動生成されました。*
*生成日時: {created_at}*

**タグ:** {tags}
**カテゴリ:** {category}
**読了時間:** 約{reading_time}分
""",
            "technical": """# {title}

## 概要
{introduction}

## 技術詳細
{main_content}

## 実装例
{examples}

## まとめ
{conclusion}

---
*この記事は {url_source} から自動生成されました。*
*生成日時: {created_at}*

**タグ:** {tags}
**カテゴリ:** {category}
**読了時間:** 約{reading_time}分
""",
            "news": """# {title}

## ニュース概要
{introduction}

## 詳細情報
{main_content}

## 影響と今後の展望
{impact}

## まとめ
{conclusion}

---
*この記事は {url_source} から自動生成されました。*
*生成日時: {created_at}*

**タグ:** {tags}
**カテゴリ:** {category}
**読了時間:** 約{reading_time}分
"""
        }
    
    async def create_template(self, 
                            name: str, 
                            content: str, 
                            category: str = "general") -> Dict[str, Any]:
        """Create a new blog post template"""
        try:
            template = BlogTemplate(
                id=str(uuid.uuid4()),
                name=name,
                content=content,
                version="1.0",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                usage_count=0,
                feedback_score=0.0,
                is_active=True
            )
            
            # Validate template with the agent
            validation_prompt = f"""
            以下のブログテンプレートを検証してください：

            **テンプレート名:** {name}
            **カテゴリ:** {category}
            **テンプレート内容:**
            {content}

            テンプレートが適切かどうか、改善点があるかどうかを分析し、
            JSON形式でフィードバックを返してください：

            {{
                "is_valid": true/false,
                "issues": ["問題点1", "問題点2"],
                "suggestions": ["改善提案1", "改善提案2"],
                "score": 0-10
            }}
            """
            
            response = await self.agent.arun(validation_prompt)
            
            try:
                validation = json.loads(response.content)
            except json.JSONDecodeError:
                validation = {
                    "is_valid": True,
                    "issues": [],
                    "suggestions": [],
                    "score": 8.0
                }
            
            if not validation.get("is_valid", True):
                return {
                    "status": "error",
                    "message": f"Template validation failed: {', '.join(validation.get('issues', []))}",
                    "validation": validation
                }
            
            return {
                "status": "success",
                "template": template,
                "validation": validation,
                "message": "Template created successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error creating template: {str(e)}"
            }
    
    async def update_template(self, 
                            template_id: str, 
                            feedback: str, 
                            user_rating: Optional[int] = None) -> Dict[str, Any]:
        """Update a template based on user feedback"""
        try:
            # Get current template (this would be from database in real implementation)
            current_template = self._get_template(template_id)
            if not current_template:
                return {
                    "status": "error",
                    "message": "Template not found"
                }
            
            # Analyze feedback with the agent
            analysis_prompt = f"""
            以下のユーザーフィードバックを分析し、テンプレートの改善案を提案してください：

            **現在のテンプレート:**
            {current_template['content']}

            **ユーザーフィードバック:**
            {feedback}

            **ユーザー評価:** {user_rating or '未評価'}

            以下の形式でJSONレスポンスを返してください：

            {{
                "analysis": "フィードバックの分析",
                "improvements": ["改善点1", "改善点2"],
                "updated_template": "改善されたテンプレート内容",
                "confidence": 0-1
            }}
            """
            
            response = await self.agent.arun(analysis_prompt)
            
            try:
                analysis = json.loads(response.content)
            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "message": "Failed to parse agent response"
                }
            
            # Create updated template
            updated_template = BlogTemplate(
                id=current_template['id'],
                name=current_template['name'],
                content=analysis.get('updated_template', current_template['content']),
                version=self._increment_version(current_template['version']),
                created_at=current_template['created_at'],
                updated_at=datetime.now(),
                usage_count=current_template['usage_count'],
                feedback_score=self._calculate_feedback_score(
                    current_template['feedback_score'], 
                    user_rating
                ),
                is_active=True
            )
            
            return {
                "status": "success",
                "template": updated_template,
                "analysis": analysis,
                "message": "Template updated successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error updating template: {str(e)}"
            }
    
    async def get_template_suggestions(self, 
                                     content_type: str, 
                                     feedback_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get template suggestions based on content type and feedback history"""
        try:
            suggestions_prompt = f"""
            以下の条件に基づいて、ブログテンプレートの改善提案をしてください：

            **コンテンツタイプ:** {content_type}
            **フィードバック履歴:** {json.dumps(feedback_history or [], ensure_ascii=False, indent=2)}

            以下の形式でJSONレスポンスを返してください：

            {{
                "suggestions": [
                    {{
                        "type": "構造改善",
                        "description": "提案の説明",
                        "priority": "high/medium/low",
                        "implementation": "具体的な実装方法"
                    }}
                ],
                "new_template_variants": [
                    {{
                        "name": "テンプレート名",
                        "description": "テンプレートの説明",
                        "content": "テンプレート内容"
                    }}
                ]
            }}
            """
            
            response = await self.agent.arun(suggestions_prompt)
            
            try:
                suggestions = json.loads(response.content)
            except json.JSONDecodeError:
                suggestions = {
                    "suggestions": [],
                    "new_template_variants": []
                }
            
            return {
                "status": "success",
                "suggestions": suggestions,
                "message": "Template suggestions generated successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error generating suggestions: {str(e)}"
            }
    
    def _get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template by ID (placeholder for database implementation)"""
        # This would be replaced with actual database query
        return {
            "id": template_id,
            "name": "Default Template",
            "content": self.default_templates.get("general", ""),
            "version": "1.0",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "usage_count": 0,
            "feedback_score": 0.0,
            "is_active": True
        }
    
    def _increment_version(self, current_version: str) -> str:
        """Increment template version"""
        try:
            major, minor = current_version.split('.')
            return f"{major}.{int(minor) + 1}"
        except:
            return "1.1"
    
    def _calculate_feedback_score(self, current_score: float, user_rating: Optional[int]) -> float:
        """Calculate updated feedback score"""
        if user_rating is None:
            return current_score
        
        # Simple weighted average
        return (current_score * 0.7) + (user_rating * 0.3)
    
    def get_default_template(self, category: str = "general") -> str:
        """Get default template for category"""
        return self.default_templates.get(category, self.default_templates["general"])