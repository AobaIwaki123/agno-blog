from agno.workflow.workflow import Workflow
from agno.workflow.step import Step
from agno.db.sqlite import SqliteDb
from typing import Dict, Any
from ..agents.url_processor import URLProcessorAgent
from ..agents.content_generator import ContentGeneratorAgent
from ..agents.template_manager import TemplateManagerAgent

class BlogWorkflow:
    """Main workflow for blog post generation"""
    
    def __init__(self, db: SqliteDb):
        self.db = db
        
        # Initialize agents
        self.url_processor = URLProcessorAgent(db)
        self.content_generator = ContentGeneratorAgent(db)
        self.template_manager = TemplateManagerAgent(db)
        
        # Create workflow steps
        self.workflow = Workflow(
            id="blog-generation",
            name="Blog Post Generation",
            description="Complete workflow for generating blog posts from URLs",
            db=db,
            steps=[
                Step(
                    name="extract_content",
                    description="Extract content from URL",
                    agent=self.url_processor.agent,
                ),
                Step(
                    name="generate_post",
                    description="Generate blog post from extracted content",
                    agent=self.content_generator.agent,
                ),
                Step(
                    name="format_content",
                    description="Format and optimize content",
                    agent=self.content_generator.agent,
                ),
            ],
        )
    
    async def generate_blog_post(self, 
                                url: str, 
                                template_id: str = None,
                                custom_instructions: str = None) -> Dict[str, Any]:
        """Generate a complete blog post from URL"""
        try:
            # Step 1: Extract content from URL
            url_result = await self.url_processor.process_url(url)
            if url_result["status"] != "success":
                return url_result
            
            # Step 2: Get template
            template = None
            if template_id:
                # Get specific template (would be from database)
                pass
            else:
                # Use default template
                template = self.template_manager.get_default_template()
            
            # Step 3: Generate blog post
            blog_result = await self.content_generator.generate_blog_post(
                url_data=url_result["data"],
                template=template,
                custom_instructions=custom_instructions
            )
            
            if blog_result["status"] != "success":
                return blog_result
            
            return {
                "status": "success",
                "blog_post": blog_result["blog_post"],
                "url_data": url_result["data"],
                "message": "Blog post generated successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error in blog generation workflow: {str(e)}"
            }
    
    async def improve_blog_post(self, 
                               blog_post_id: str, 
                               feedback: str) -> Dict[str, Any]:
        """Improve an existing blog post based on feedback"""
        try:
            # Get blog post (would be from database)
            # For now, we'll simulate this
            blog_post = None  # This would be retrieved from database
            
            if not blog_post:
                return {
                    "status": "error",
                    "message": "Blog post not found"
                }
            
            # Improve the blog post
            improvement_result = await self.content_generator.improve_blog_post(
                blog_post=blog_post,
                feedback=feedback
            )
            
            return improvement_result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error improving blog post: {str(e)}"
            }
    
    async def update_template(self, 
                            template_id: str, 
                            feedback: str, 
                            user_rating: int = None) -> Dict[str, Any]:
        """Update template based on user feedback"""
        try:
            update_result = await self.template_manager.update_template(
                template_id=template_id,
                feedback=feedback,
                user_rating=user_rating
            )
            
            return update_result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error updating template: {str(e)}"
            }
    
    async def close(self):
        """Clean up resources"""
        await self.url_processor.close()