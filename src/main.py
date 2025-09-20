from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from agno.models.anthropic import Claude
from agno.agent import Agent
from agno.tools.mcp import MCPTools
import uvicorn
import os
from typing import List, Optional
import json

from .models.blog_post import BlogPost, BlogPostRequest, TemplateUpdateRequest, BlogPostResponse
from .workflows.blog_workflow import BlogWorkflow
from .agents.url_processor import URLProcessorAgent
from .agents.content_generator import ContentGeneratorAgent
from .agents.template_manager import TemplateManagerAgent

# Initialize database
db = SqliteDb(db_file="blog.db")

# Initialize FastAPI app
app = FastAPI(
    title="Agno Blog Application",
    description="AI-powered blog generation and management system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize workflow
blog_workflow = BlogWorkflow(db)

# Initialize agents
url_processor = URLProcessorAgent(db)
content_generator = ContentGeneratorAgent(db)
template_manager = TemplateManagerAgent(db)

# Create main blog agent
blog_agent = Agent(
    name="Blog Agent",
    model=Claude(id="claude-sonnet-4-0"),
    db=db,
    tools=[MCPTools(transport="streamable-http", url="https://docs.agno.com/mcp")],
    add_history_to_context=True,
    markdown=True,
    instructions=[
        "You are a blog management assistant",
        "Help users generate, edit, and manage blog posts",
        "Provide guidance on content optimization and SEO",
        "Assist with template management and customization"
    ]
)

# Create AgentOS
agent_os = AgentOS(
    description="Agno Blog Application - AI-powered blog generation",
    os_id="agno-blog",
    agents=[blog_agent],
    db=db,
    enable_mcp=True,
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# In-memory storage for demo (replace with database in production)
blog_posts = []
templates_data = []

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Main page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agno Blog</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .form-group { margin: 20px 0; }
            label { display: block; margin-bottom: 5px; }
            input, textarea { width: 100%; padding: 10px; margin-bottom: 10px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            button:hover { background: #0056b3; }
            .blog-post { border: 1px solid #ddd; padding: 20px; margin: 20px 0; }
            .error { color: red; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Agno Blog - AI-Powered Blog Generation</h1>
            
            <h2>新しいブログ記事を生成</h2>
            <form id="generateForm">
                <div class="form-group">
                    <label for="url">URL:</label>
                    <input type="url" id="url" name="url" placeholder="https://example.com/article" required>
                </div>
                <div class="form-group">
                    <label for="instructions">カスタム指示 (オプション):</label>
                    <textarea id="instructions" name="instructions" rows="3" placeholder="記事のトーンやスタイルについての指示..."></textarea>
                </div>
                <button type="submit">ブログ記事を生成</button>
            </form>
            
            <div id="result"></div>
            
            <h2>生成されたブログ記事</h2>
            <div id="blogPosts"></div>
            
            <h2>テンプレート管理</h2>
            <div class="form-group">
                <label for="feedback">テンプレート改善フィードバック:</label>
                <textarea id="feedback" name="feedback" rows="3" placeholder="テンプレートの改善点について..."></textarea>
                <button onclick="updateTemplate()">テンプレートを更新</button>
            </div>
        </div>
        
        <script>
            // Generate blog post
            document.getElementById('generateForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const url = document.getElementById('url').value;
                const instructions = document.getElementById('instructions').value;
                
                try {
                    const response = await fetch('/api/generate-post', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url, custom_instructions: instructions })
                    });
                    
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        document.getElementById('result').innerHTML = 
                            '<div class="success">ブログ記事が生成されました！</div>';
                        loadBlogPosts();
                    } else {
                        document.getElementById('result').innerHTML = 
                            '<div class="error">エラー: ' + result.message + '</div>';
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = 
                        '<div class="error">エラー: ' + error.message + '</div>';
                }
            });
            
            // Load blog posts
            async function loadBlogPosts() {
                try {
                    const response = await fetch('/api/blog-posts');
                    const posts = await response.json();
                    
                    const container = document.getElementById('blogPosts');
                    container.innerHTML = posts.map(post => `
                        <div class="blog-post">
                            <h3>${post.title}</h3>
                            <p><strong>作成日:</strong> ${new Date(post.created_at).toLocaleString()}</p>
                            <p><strong>ソースURL:</strong> <a href="${post.url_source}" target="_blank">${post.url_source}</a></p>
                            <div style="white-space: pre-wrap;">${post.content}</div>
                            <button onclick="improvePost('${post.id}')">記事を改善</button>
                        </div>
                    `).join('');
                } catch (error) {
                    console.error('Error loading blog posts:', error);
                }
            }
            
            // Update template
            async function updateTemplate() {
                const feedback = document.getElementById('feedback').value;
                if (!feedback) {
                    alert('フィードバックを入力してください');
                    return;
                }
                
                try {
                    const response = await fetch('/api/update-template', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ template_id: 'default', feedback })
                    });
                    
                    const result = await response.json();
                    if (result.status === 'success') {
                        alert('テンプレートが更新されました！');
                    } else {
                        alert('エラー: ' + result.message);
                    }
                } catch (error) {
                    alert('エラー: ' + error.message);
                }
            }
            
            // Improve post
            async function improvePost(postId) {
                const feedback = prompt('改善点を入力してください:');
                if (!feedback) return;
                
                try {
                    const response = await fetch(`/api/improve-post/${postId}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ feedback })
                    });
                    
                    const result = await response.json();
                    if (result.status === 'success') {
                        alert('記事が改善されました！');
                        loadBlogPosts();
                    } else {
                        alert('エラー: ' + result.message);
                    }
                } catch (error) {
                    alert('エラー: ' + error.message);
                }
            }
            
            // Load blog posts on page load
            loadBlogPosts();
        </script>
    </body>
    </html>
    """

@app.post("/api/generate-post", response_model=BlogPostResponse)
async def generate_blog_post(request: BlogPostRequest):
    """Generate a blog post from URL"""
    try:
        result = await blog_workflow.generate_blog_post(
            url=request.url,
            template_id=request.template_id,
            custom_instructions=request.custom_instructions
        )
        
        if result["status"] == "success":
            # Store blog post (in production, this would be in database)
            blog_post = result["blog_post"]
            blog_posts.append(blog_post.dict())
            
            return BlogPostResponse(
                post=blog_post,
                status="success",
                message="Blog post generated successfully"
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blog-posts")
async def get_blog_posts():
    """Get all blog posts"""
    return blog_posts

@app.post("/api/improve-post/{post_id}")
async def improve_blog_post(post_id: str, feedback: dict):
    """Improve a blog post based on feedback"""
    try:
        # Find blog post
        post = next((p for p in blog_posts if p["id"] == post_id), None)
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        # Improve the post
        result = await blog_workflow.improve_blog_post(
            blog_post_id=post_id,
            feedback=feedback["feedback"]
        )
        
        if result["status"] == "success":
            # Update the post
            updated_post = result["blog_post"]
            for i, p in enumerate(blog_posts):
                if p["id"] == post_id:
                    blog_posts[i] = updated_post.dict()
                    break
            
            return {"status": "success", "message": "Blog post improved successfully"}
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update-template")
async def update_template(request: TemplateUpdateRequest):
    """Update template based on user feedback"""
    try:
        result = await blog_workflow.update_template(
            template_id=request.template_id,
            feedback=request.feedback,
            user_rating=request.user_rating
        )
        
        if result["status"] == "success":
            return {"status": "success", "message": "Template updated successfully"}
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/templates")
async def get_templates():
    """Get all templates"""
    return templates_data

@app.post("/api/templates")
async def create_template(template: dict):
    """Create a new template"""
    try:
        result = await template_manager.create_template(
            name=template["name"],
            content=template["content"],
            category=template.get("category", "general")
        )
        
        if result["status"] == "success":
            templates_data.append(result["template"].dict())
            return {"status": "success", "message": "Template created successfully"}
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Agno Blog API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)