"""
Content Generator Agent

This agent specializes in generating blog posts from extracted content
using templates and AI-powered content creation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.knowledge.knowledge import Knowledge
from agno.models.anthropic import Claude
from agno.tools import tool

from tools.content_processor import ContentProcessingTools
from tools.template_manager import TemplateManagementTools

logger = logging.getLogger(__name__)


class ContentGeneratorAgent:
    """Agent specialized in generating blog posts from extracted content."""

    def __init__(
        self,
        db: SqliteDb,
        knowledge: Optional[Knowledge] = None,
    ):
        self.template_manager = TemplateManagementTools()
        self.content_processor = ContentProcessingTools()
        self.knowledge = knowledge

        # Define tools using the @tool decorator
        @tool
        def generate_blog_post(
            extracted_content: Dict[str, Any],
            template_id: str = "default",
            style_preferences: Optional[
                Dict[str, Any]
            ] = None,
        ) -> Dict[str, Any]:
            """
            Generate a blog post from extracted content using a template.

            Args:
                extracted_content: Dictionary containing extracted content and metadata
                template_id: ID of the template to use
                style_preferences: Optional style preferences

            Returns:
                Dictionary containing generated blog post
            """
            return self._generate_blog_post_impl(
                extracted_content,
                template_id,
                style_preferences,
            )

        @tool
        def enhance_blog_content(
            blog_content: str,
            enhancement_type: str = "readability",
        ) -> Dict[str, Any]:
            """
            Enhance blog content for better readability, SEO, or engagement.

            Args:
                blog_content: The blog content to enhance
                enhancement_type: Type of enhancement (readability, seo, engagement)

            Returns:
                Dictionary containing enhanced content
            """
            return self._enhance_blog_content_impl(
                blog_content, enhancement_type
            )

        @tool
        def optimize_for_seo(
            content: str,
            target_keywords: Optional[List[str]] = None,
        ) -> Dict[str, Any]:
            """
            Optimize content for search engines.

            Args:
                content: Content to optimize
                target_keywords: Optional list of target keywords

            Returns:
                Dictionary containing SEO optimization results
            """
            return self._optimize_for_seo_impl(
                content, target_keywords
            )

        # Create the Agno agent
        self.agent = Agent(
            name="Content Generator",
            model=Claude(id="claude-sonnet-4-20250514"),
            tools=[
                generate_blog_post,
                enhance_blog_content,
                optimize_for_seo,
            ],
            instructions=[
                "You are a specialized agent for generating high-quality blog posts.",
                "Your primary responsibilities:",
                "1. Transform extracted content into engaging blog posts",
                "2. Use appropriate templates based on content type and user preferences",
                "3. Optimize content for SEO and readability",
                "4. Maintain consistent tone and style",
                "5. Include relevant metadata, tags, and formatting",
                "",
                "When generating blog posts:",
                "- Choose the most appropriate template for the content type",
                "- Create engaging titles and introductions",
                "- Structure content with clear headings and sections",
                "- Include relevant examples, code snippets, or quotes when appropriate",
                "- Generate SEO-friendly meta descriptions and tags",
                "- Ensure content flows naturally and is easy to read",
                "- Add calls-to-action or conclusions that engage readers",
                "",
                "Focus on creating valuable, informative, and engaging content.",
                "Always maintain factual accuracy and provide proper attribution.",
            ],
            db=db,
            knowledge=knowledge,
            markdown=True,
        )

    def _generate_blog_post_impl(
        self,
        extracted_content: Dict[str, Any],
        template_id: str = "default",
        style_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a blog post from extracted content using a template.

        Args:
            extracted_content: Dictionary containing extracted content and metadata
            template_id: ID of the template to use
            style_preferences: Optional style preferences

        Returns:
            Dictionary containing generated blog post
        """
        try:
            logger.info(
                f"Content Generator: Generating blog post using template {template_id}"
            )

            # Load template
            template_data = (
                self.template_manager.load_template(
                    template_id
                )
            )
            if not template_data:
                return {
                    "status": "error",
                    "message": f"Template {template_id} not found",
                }

            # Extract content components
            title = extracted_content.get(
                "title", "Untitled"
            )
            content = extracted_content.get("content", "")
            summary = extracted_content.get("summary", "")
            keywords = extracted_content.get("keywords", [])
            url = extracted_content.get("url", "")

            if not content:
                return {
                    "status": "error",
                    "message": "No content provided for blog post generation",
                }

            # Apply style preferences
            style_prefs = style_preferences or {}
            tone = style_prefs.get("tone", "professional")
            target_audience = style_prefs.get(
                "target_audience", "general"
            )
            content_length = style_prefs.get(
                "content_length", "medium"
            )

            # Generate blog post components
            blog_components = (
                self._generate_blog_components(
                    content,
                    title,
                    summary,
                    keywords,
                    tone,
                    target_audience,
                    content_length,
                )
            )

            # Render template with generated components
            template_variables = {
                "title": blog_components["title"],
                "introduction": blog_components[
                    "introduction"
                ],
                "main_content": blog_components[
                    "main_content"
                ],
                "key_points": blog_components["key_points"],
                "conclusion": blog_components["conclusion"],
                "publish_date": datetime.now().strftime(
                    "%Y-%m-%d"
                ),
                "tags": ", ".join(keywords[:5]),
                "source_url": url,
            }

            # Add any additional variables from template
            for var in template_data.get("variables", []):
                if var not in template_variables:
                    template_variables[var] = (
                        blog_components.get(var, f"[{var}]")
                    )

            # Render the final blog post
            blog_content = (
                self.template_manager.render_template(
                    template_id, template_variables
                )
            )

            # Generate metadata
            metadata = {
                "template_used": template_id,
                "style_preferences": style_prefs,
                "generation_timestamp": datetime.utcnow().isoformat(),
                "source_content_hash": self.content_processor.generate_content_hash(
                    content
                ),
                "word_count": len(blog_content.split()),
                "estimated_reading_time": max(
                    1, len(blog_content.split()) // 200
                ),
            }

            result = {
                "status": "success",
                "blog_post": blog_content,
                "title": blog_components["title"],
                "metadata": metadata,
                "template_id": template_id,
                "source_url": url,
            }

            logger.info("Blog post generated successfully")
            return result

        except Exception as e:
            logger.error(
                f"Error generating blog post: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Blog post generation failed: {str(e)}",
            }

    def _enhance_blog_content_impl(
        self,
        blog_content: str,
        enhancement_type: str = "readability",
    ) -> Dict[str, Any]:
        """
        Enhance blog content for better readability, SEO, or engagement.

        Args:
            blog_content: The blog content to enhance
            enhancement_type: Type of enhancement (readability, seo, engagement)

        Returns:
            Dictionary containing enhanced content
        """
        try:
            logger.info(
                f"Content Generator: Enhancing content for {enhancement_type}"
            )

            enhanced_content = blog_content
            changes_made = []

            if enhancement_type == "readability":
                # Improve readability
                enhanced_content = (
                    self._enhance_readability(
                        enhanced_content
                    )
                )
                changes_made.append(
                    "Improved readability and structure"
                )

            elif enhancement_type == "seo":
                # SEO optimization
                enhanced_content = self._enhance_seo(
                    enhanced_content
                )
                changes_made.append("Optimized for SEO")

            elif enhancement_type == "engagement":
                # Improve engagement
                enhanced_content = self._enhance_engagement(
                    enhanced_content
                )
                changes_made.append(
                    "Enhanced for reader engagement"
                )

            return {
                "status": "success",
                "enhanced_content": enhanced_content,
                "original_content": blog_content,
                "changes_made": changes_made,
                "enhancement_type": enhancement_type,
            }

        except Exception as e:
            logger.error(
                f"Error enhancing content: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"Content enhancement failed: {str(e)}",
            }

    def _optimize_for_seo_impl(
        self,
        content: str,
        target_keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Optimize content for search engines.

        Args:
            content: Content to optimize
            target_keywords: Optional list of target keywords

        Returns:
            Dictionary containing SEO optimization results
        """
        try:
            logger.info(
                "Content Generator: Optimizing content for SEO"
            )

            # Extract current keywords if none provided
            if not target_keywords:
                keywords_with_freq = (
                    self.content_processor.extract_keywords(
                        content, max_keywords=10
                    )
                )
                target_keywords = [
                    kw[0] for kw in keywords_with_freq[:5]
                ]

            # Generate SEO recommendations
            seo_analysis = {
                "target_keywords": target_keywords,
                "keyword_density": self._calculate_keyword_density(
                    content, target_keywords
                ),
                "meta_description": self._generate_meta_description(
                    content
                ),
                "title_suggestions": self._generate_title_suggestions(
                    content, target_keywords
                ),
                "header_structure": self._analyze_header_structure(
                    content
                ),
                "internal_linking_opportunities": self._find_linking_opportunities(
                    content
                ),
                "content_length": len(content.split()),
                "readability_score": self._calculate_readability_score(
                    content
                ),
            }

            # Generate optimized content
            optimized_content = (
                self._apply_seo_optimizations(
                    content, target_keywords
                )
            )

            return {
                "status": "success",
                "optimized_content": optimized_content,
                "seo_analysis": seo_analysis,
                "recommendations": self._generate_seo_recommendations(
                    seo_analysis
                ),
            }

        except Exception as e:
            logger.error(
                f"Error optimizing for SEO: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"SEO optimization failed: {str(e)}",
            }

    def _generate_blog_components(
        self,
        content: str,
        title: str,
        summary: str,
        keywords: List[str],
        tone: str,
        target_audience: str,
        content_length: str,
    ) -> Dict[str, str]:
        """Generate individual components for the blog post."""

        # Analyze content structure
        sections = (
            self.content_processor.split_into_sections(
                content, max_section_length=500
            )
        )

        components = {}

        # Generate improved title
        components["title"] = self._improve_title(
            title, keywords, tone
        )

        # Generate introduction
        components["introduction"] = (
            self._generate_introduction(
                summary or content[:300],
                tone,
                target_audience,
            )
        )

        # Process main content
        components["main_content"] = (
            self._process_main_content(
                sections, tone, content_length
            )
        )

        # Extract key points
        components["key_points"] = self._extract_key_points(
            content, keywords
        )

        # Generate conclusion
        components["conclusion"] = (
            self._generate_conclusion(content, tone)
        )

        return components

    def _improve_title(
        self,
        original_title: str,
        keywords: List[str],
        tone: str,
    ) -> str:
        """Improve the original title for better engagement."""
        # Simple title improvement logic
        if len(original_title) < 30 and keywords:
            # Add a relevant keyword if title is short
            return f"{original_title}: {keywords[0].title()} Guide"
        return original_title

    def _generate_introduction(
        self,
        content_preview: str,
        tone: str,
        target_audience: str,
    ) -> str:
        """Generate an engaging introduction."""
        # Extract first meaningful sentence
        sentences = content_preview.split(".")[:2]
        intro_base = ". ".join(sentences).strip()

        if tone == "casual":
            return f"Have you ever wondered about this? {intro_base}. Let's dive in and explore this topic together."
        elif tone == "professional":
            return f"In today's digital landscape, understanding this topic is crucial. {intro_base}. This article will provide comprehensive insights."
        else:
            return f"{intro_base}. In this post, we'll explore the key aspects and implications of this topic."

    def _process_main_content(
        self,
        sections: List[Dict[str, Any]],
        tone: str,
        content_length: str,
    ) -> str:
        """Process and structure the main content."""
        if not sections:
            return "Content processing failed."

        processed_content = ""

        for i, section in enumerate(sections):
            section_content = section["content"]

            # Add section headers for longer content
            if len(sections) > 1 and content_length in [
                "long",
                "detailed",
            ]:
                processed_content += (
                    f"\n\n### Section {i + 1}\n\n"
                )

            processed_content += section_content + "\n\n"

        return processed_content.strip()

    def _extract_key_points(
        self, content: str, keywords: List[str]
    ) -> str:
        """Extract key points from the content."""
        # Simple key point extraction
        sentences = content.split(".")
        key_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 50 and any(
                keyword in sentence.lower()
                for keyword in keywords
            ):
                key_sentences.append(f"• {sentence}")
                if len(key_sentences) >= 3:
                    break

        return (
            "\n".join(key_sentences)
            if key_sentences
            else "• Key insights from the content\n• Important takeaways\n• Actionable recommendations"
        )

    def _generate_conclusion(
        self, content: str, tone: str
    ) -> str:
        """Generate a conclusion based on the content."""
        if tone == "casual":
            return "That's a wrap! We've covered a lot of ground here. What are your thoughts on this topic? Feel free to share your experiences in the comments below."
        elif tone == "professional":
            return "In conclusion, this analysis demonstrates the importance of understanding these key concepts. Organizations and individuals should consider these insights when making related decisions."
        else:
            return "To summarize, we've explored the main aspects of this topic and its implications. This information should provide a solid foundation for further exploration and application."

    def _enhance_readability(self, content: str) -> str:
        """Enhance content for better readability."""
        # Add more paragraph breaks
        content = content.replace(". ", ".\n\n")

        # Remove excessive line breaks
        import re

        content = re.sub(r"\n\n\n+", "\n\n", content)

        return content

    def _enhance_seo(self, content: str) -> str:
        """Enhance content for SEO."""
        # Ensure proper heading structure
        lines = content.split("\n")
        enhanced_lines = []

        for line in lines:
            line = line.strip()
            if (
                line
                and not line.startswith("#")
                and len(line) < 100
                and line.isupper()
            ):
                # Convert all-caps lines to headers
                enhanced_lines.append(f"## {line.title()}")
            else:
                enhanced_lines.append(line)

        return "\n".join(enhanced_lines)

    def _enhance_engagement(self, content: str) -> str:
        """Enhance content for better reader engagement."""
        # Add engaging elements
        if "?" not in content:
            content += (
                "\n\nWhat are your thoughts on this topic?"
            )

        return content

    def _calculate_keyword_density(
        self, content: str, keywords: List[str]
    ) -> Dict[str, float]:
        """Calculate keyword density."""
        word_count = len(content.split())
        density = {}

        for keyword in keywords:
            keyword_count = content.lower().count(
                keyword.lower()
            )
            density[keyword] = (
                (keyword_count / word_count) * 100
                if word_count > 0
                else 0
            )

        return density

    def _generate_meta_description(
        self, content: str
    ) -> str:
        """Generate a meta description."""
        return self.content_processor.generate_summary(
            content, max_length=160, sentences=2
        )

    def _generate_title_suggestions(
        self, content: str, keywords: List[str]
    ) -> List[str]:
        """Generate alternative title suggestions."""
        suggestions = []

        if keywords:
            suggestions.append(
                f"Complete Guide to {keywords[0].title()}"
            )
            suggestions.append(
                f"Understanding {keywords[0].title()}: Key Insights"
            )
            suggestions.append(
                f"Everything You Need to Know About {keywords[0].title()}"
            )

        return suggestions

    def _analyze_header_structure(
        self, content: str
    ) -> Dict[str, Any]:
        """Analyze the header structure of the content."""
        import re

        headers = {
            "h1": len(
                re.findall(r"^# ", content, re.MULTILINE)
            ),
            "h2": len(
                re.findall(r"^## ", content, re.MULTILINE)
            ),
            "h3": len(
                re.findall(r"^### ", content, re.MULTILINE)
            ),
        }

        return {
            "headers": headers,
            "total_headers": sum(headers.values()),
            "has_proper_structure": headers["h1"] == 1
            and headers["h2"] > 0,
        }

    def _find_linking_opportunities(
        self, content: str
    ) -> List[str]:
        """Find opportunities for internal linking."""
        # Simple implementation - look for common topics
        opportunities = []

        common_topics = [
            "tutorial",
            "guide",
            "introduction",
            "overview",
            "comparison",
        ]
        content_lower = content.lower()

        for topic in common_topics:
            if topic in content_lower:
                opportunities.append(
                    f"Link to related {topic} content"
                )

        return opportunities

    def _calculate_readability_score(
        self, content: str
    ) -> float:
        """Calculate a simple readability score."""
        words = content.split()
        sentences = content.split(".")

        if len(sentences) == 0:
            return 0.0

        avg_words_per_sentence = len(words) / len(sentences)

        # Simple scoring: lower is better (easier to read)
        if avg_words_per_sentence <= 15:
            return 8.0  # Good
        elif avg_words_per_sentence <= 20:
            return 6.0  # Fair
        else:
            return 4.0  # Difficult

    def _apply_seo_optimizations(
        self, content: str, keywords: List[str]
    ) -> str:
        """Apply SEO optimizations to content."""
        optimized = content

        # Ensure keywords appear naturally
        if (
            keywords
            and keywords[0].lower() not in content.lower()
        ):
            # Add keyword naturally to the first paragraph
            paragraphs = optimized.split("\n\n")
            if paragraphs:
                first_para = paragraphs[0]
                paragraphs[0] = (
                    f"{first_para} This relates to {keywords[0]} and its applications."
                )
                optimized = "\n\n".join(paragraphs)

        return optimized

    def _generate_seo_recommendations(
        self, seo_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate SEO improvement recommendations."""
        recommendations = []

        # Check content length
        word_count = seo_analysis.get("content_length", 0)
        if word_count < 300:
            recommendations.append(
                "Consider expanding content to at least 300 words for better SEO"
            )

        # Check header structure
        headers = seo_analysis.get("header_structure", {})
        if not headers.get("has_proper_structure", False):
            recommendations.append(
                "Improve header structure with proper H1 and H2 tags"
            )

        # Check keyword density
        keyword_density = seo_analysis.get(
            "keyword_density", {}
        )
        for keyword, density in keyword_density.items():
            if density < 0.5:
                recommendations.append(
                    f"Consider using '{keyword}' more frequently (current density: {density:.1f}%)"
                )
            elif density > 3.0:
                recommendations.append(
                    f"Reduce usage of '{keyword}' to avoid keyword stuffing (current density: {density:.1f}%)"
                )

        return recommendations

    async def generate_blog_post(
        self,
        extracted_content: Dict[str, Any],
        template_id: str = "default",
        style_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a complete blog post from extracted content.

        Args:
            extracted_content: Content extracted by URL processor
            template_id: Template to use for generation
            style_preferences: Style and tone preferences

        Returns:
            Dictionary containing the generated blog post and metadata
        """
        try:
            logger.info(
                f"Content Generator Agent: Generating blog post with template {template_id}"
            )

            # Prepare the prompt for the agent
            content_summary = {
                "title": extracted_content.get("title", ""),
                "content_length": len(
                    extracted_content.get("content", "")
                ),
                "keywords": extracted_content.get(
                    "keywords", []
                ),
                "summary": extracted_content.get(
                    "summary", ""
                ),
                "url": extracted_content.get("url", ""),
            }

            prompt = f"""
            Please generate a high-quality blog post from the following extracted content:
            
            Content Summary: {content_summary}
            Template ID: {template_id}
            Style Preferences: {style_preferences or "Default professional style"}
            
            Please:
            1. Use the blog generation tool to create the post
            2. Optimize the content for readability and SEO
            3. Ensure proper structure and engaging presentation
            4. Include relevant metadata and tags
            
            Generate a comprehensive blog post that provides value to readers.
            """

            # Run the agent
            response = await self.agent.arun(prompt)

            logger.info(
                "Content Generator Agent: Blog post generation completed"
            )

            return {
                "status": "success",
                "agent_response": response.content,
                "template_used": template_id,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(
                f"Error generating blog post: {str(e)}"
            )
            return {"status": "error", "message": str(e)}


# Example usage and testing
if __name__ == "__main__":
    import asyncio

    from agno.db.sqlite import SqliteDb

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Create database
    db = SqliteDb(db_file="test_content_generator.db")

    # Create content generator agent
    content_generator = ContentGeneratorAgent(db)

    async def test_content_generator():
        # Test content
        extracted_content = {
            "title": "Introduction to Machine Learning",
            "content": "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. It has applications in many fields including natural language processing, computer vision, and recommendation systems.",
            "summary": "An overview of machine learning concepts and applications",
            "keywords": [
                "machine learning",
                "artificial intelligence",
                "algorithms",
                "data",
            ],
            "url": "https://example.com/ml-intro",
        }

        # Test blog post generation
        result = await content_generator.generate_blog_post(
            extracted_content, "default"
        )
        print(f"Blog generation result: {result['status']}")

        if result["status"] == "success":
            print(
                f"Agent response: {result['agent_response'][:300]}..."
            )

        # Clean up
        import os

        if os.path.exists("test_content_generator.db"):
            os.remove("test_content_generator.db")

    # Run test
    asyncio.run(test_content_generator())
