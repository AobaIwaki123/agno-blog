import re
from typing import Dict, Any, List
from datetime import datetime

class ContentFormatterTool:
    """Tool for formatting and structuring blog content"""
    
    def __init__(self):
        self.default_template = """# {title}

{content}

---
*この記事は {url_source} から自動生成されました。*
*生成日時: {created_at}*
"""
    
    def format_blog_post(self, 
                        title: str, 
                        content: str, 
                        url_source: str = None,
                        template: str = None,
                        metadata: Dict[str, Any] = None) -> str:
        """Format content into a blog post using template"""
        
        if template is None:
            template = self.default_template
        
        # Clean and structure content
        formatted_content = self._structure_content(content)
        
        # Prepare template variables
        template_vars = {
            "title": self._format_title(title),
            "content": formatted_content,
            "url_source": url_source or "不明なソース",
            "created_at": datetime.now().strftime("%Y年%m月%d日 %H:%M"),
            "metadata": metadata or {}
        }
        
        # Format the template
        formatted_post = template.format(**template_vars)
        
        return formatted_post
    
    def _structure_content(self, content: str) -> str:
        """Structure content with proper headings and paragraphs"""
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        structured_content = []
        
        for i, paragraph in enumerate(paragraphs):
            # Check if paragraph looks like a heading
            if self._is_heading(paragraph):
                structured_content.append(f"\n## {paragraph.strip('# ')}\n")
            else:
                # Regular paragraph
                structured_content.append(f"{paragraph}\n")
        
        return '\n'.join(structured_content)
    
    def _is_heading(self, text: str) -> bool:
        """Check if text looks like a heading"""
        # Check for common heading patterns
        heading_patterns = [
            r'^#{1,6}\s+',  # Markdown headers
            r'^[A-Z][^.!?]*:$',  # Text ending with colon
            r'^[A-Z][^.!?]*\?$',  # Question format
            r'^\d+\.\s+[A-Z]',  # Numbered list items
        ]
        
        for pattern in heading_patterns:
            if re.match(pattern, text.strip()):
                return True
        
        # Check if it's short and doesn't end with punctuation
        if len(text) < 100 and not text.endswith(('.', '!', '?')):
            return True
        
        return False
    
    def _format_title(self, title: str) -> str:
        """Format title for better presentation"""
        # Remove extra whitespace
        title = re.sub(r'\s+', ' ', title.strip())
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
        
        return title
    
    def extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        
        # Filter and clean sentences
        key_points = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:
                # Check if sentence contains important keywords
                important_keywords = [
                    '重要', '注目', 'ポイント', '特徴', 'メリット', 'デメリット',
                    '方法', '手順', '理由', '原因', '結果', '効果'
                ]
                
                if any(keyword in sentence for keyword in important_keywords):
                    key_points.append(sentence)
        
        return key_points[:5]  # Return top 5 key points
    
    def generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate a summary of the content"""
        # Extract first few sentences
        sentences = re.split(r'[.!?]+', content)
        
        summary = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(summary + sentence) < max_length:
                summary += sentence + "。"
            else:
                break
        
        return summary
    
    def add_seo_optimization(self, content: str, keywords: List[str] = None) -> str:
        """Add SEO optimization to content"""
        if not keywords:
            return content
        
        # Add keywords to headings if possible
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            if line.startswith('##') and keywords:
                # Try to incorporate keywords into headings
                for keyword in keywords:
                    if keyword.lower() not in line.lower():
                        line = line.replace('##', f'## {keyword}について')
                        break
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)