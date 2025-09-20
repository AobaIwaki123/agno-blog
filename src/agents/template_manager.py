"""
Template Manager Agent

This agent specializes in managing blog post templates,
processing user feedback, and updating templates based on user input.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.db.sqlite import SqliteDb

from tools.template_manager import TemplateManagementTools
from models.blog_post import BlogTemplate, FeedbackEntry

logger = logging.getLogger(__name__)

class TemplateManagerAgent:
    """Agent specialized in template management and feedback processing."""
    
    def __init__(self, db: SqliteDb):
        self.template_manager = TemplateManagementTools()
        
        # Create the Agno agent
        self.agent = Agent(
            name="Template Manager",
            role="Manage blog post templates and process user feedback for continuous improvement",
            model=Claude(id="claude-3-5-sonnet-20241022"),
            tools=[
                self._create_feedback_analysis_tool(),
                self._create_template_update_tool(),
                self._create_template_validation_tool()
            ],
            instructions=[
                "You are a specialized agent for managing blog post templates and processing user feedback.",
                "Your primary responsibilities:",
                "1. Analyze user feedback on generated blog posts",
                "2. Identify patterns and areas for template improvement",
                "3. Propose template updates based on feedback analysis",
                "4. Always require user confirmation before making template changes",
                "5. Maintain template version history and track changes",
                "6. Validate template structure and variables",
                "",
                "When processing feedback:",
                "- Carefully analyze the sentiment and specific issues mentioned",
                "- Identify which parts of the template need modification",
                "- Propose specific, actionable changes",
                "- Consider the impact of changes on existing templates",
                "- Always ask for user confirmation before applying changes",
                "- Document all changes and reasoning",
                "",
                "When managing templates:",
                "- Ensure templates are well-structured and flexible",
                "- Maintain consistent variable naming and formatting",
                "- Validate that all required variables are present",
                "- Track usage statistics and performance metrics",
                "",
                "Be conservative with changes and prioritize user satisfaction."
            ],
            db=db,
            markdown=True,
        )
    
    def _create_feedback_analysis_tool(self):
        """Create a tool for analyzing user feedback."""
        def analyze_user_feedback(feedback: str, template_id: str, 
                                generated_content: str = "") -> Dict[str, Any]:
            """
            Analyze user feedback to understand improvement areas.
            
            Args:
                feedback: User feedback text
                template_id: ID of the template that generated the content
                generated_content: The content that received feedback
                
            Returns:
                Dictionary containing feedback analysis results
            """
            try:
                logger.info(f"Template Manager: Analyzing feedback for template {template_id}")
                
                if not feedback.strip():
                    return {
                        "status": "error",
                        "message": "No feedback provided for analysis"
                    }
                
                # Load template for context
                template_data = self.template_manager.load_template(template_id)
                if not template_data:
                    return {
                        "status": "error",
                        "message": f"Template {template_id} not found"
                    }
                
                # Perform detailed feedback analysis
                analysis = self._perform_detailed_feedback_analysis(
                    feedback, template_data, generated_content
                )
                
                # Generate improvement suggestions
                suggestions = self._generate_improvement_suggestions(
                    analysis, template_data
                )
                
                # Assess impact and priority
                impact_assessment = self._assess_change_impact(
                    suggestions, template_data
                )
                
                result = {
                    "status": "success",
                    "template_id": template_id,
                    "feedback_analysis": analysis,
                    "improvement_suggestions": suggestions,
                    "impact_assessment": impact_assessment,
                    "requires_user_confirmation": True,
                    "analysis_timestamp": datetime.utcnow().isoformat()
                }
                
                logger.info(f"Feedback analysis completed for template {template_id}")
                return result
                
            except Exception as e:
                logger.error(f"Error analyzing feedback: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Feedback analysis failed: {str(e)}"
                }
        
        return analyze_user_feedback
    
    def _create_template_update_tool(self):
        """Create a tool for updating templates based on feedback."""
        def update_template_from_feedback(template_id: str, feedback_analysis: Dict[str, Any],
                                        user_confirmation: bool = False) -> Dict[str, Any]:
            """
            Update a template based on analyzed feedback.
            
            Args:
                template_id: Template to update
                feedback_analysis: Results from feedback analysis
                user_confirmation: Whether user has confirmed the changes
                
            Returns:
                Dictionary containing update results
            """
            try:
                logger.info(f"Template Manager: Updating template {template_id}")
                
                if not user_confirmation:
                    return {
                        "status": "pending_confirmation",
                        "message": "Template update requires user confirmation",
                        "proposed_changes": feedback_analysis.get("improvement_suggestions", []),
                        "impact_assessment": feedback_analysis.get("impact_assessment", {})
                    }
                
                # Load current template
                template_data = self.template_manager.load_template(template_id)
                if not template_data:
                    return {
                        "status": "error",
                        "message": f"Template {template_id} not found"
                    }
                
                # Apply improvements
                updated_template = self._apply_template_improvements(
                    template_data, feedback_analysis.get("improvement_suggestions", [])
                )
                
                # Update version and metadata
                updated_template = self._update_template_metadata(
                    updated_template, feedback_analysis
                )
                
                # Save updated template
                if self.template_manager.save_template(template_id, updated_template):
                    return {
                        "status": "success",
                        "message": "Template updated successfully",
                        "template_id": template_id,
                        "new_version": updated_template["version"],
                        "changes_applied": feedback_analysis.get("improvement_suggestions", []),
                        "updated_at": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Failed to save updated template"
                    }
                
            except Exception as e:
                logger.error(f"Error updating template: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Template update failed: {str(e)}"
                }
        
        return update_template_from_feedback
    
    def _create_template_validation_tool(self):
        """Create a tool for validating template structure."""
        def validate_template_structure(template_content: str, 
                                      variables: List[str] = None) -> Dict[str, Any]:
            """
            Validate template structure and identify issues.
            
            Args:
                template_content: Template content to validate
                variables: Expected variables in the template
                
            Returns:
                Dictionary containing validation results
            """
            try:
                logger.info("Template Manager: Validating template structure")
                
                validation_results = {
                    "is_valid": True,
                    "issues": [],
                    "warnings": [],
                    "suggestions": []
                }
                
                # Check for basic structure
                if not template_content.strip():
                    validation_results["is_valid"] = False
                    validation_results["issues"].append("Template content is empty")
                    return validation_results
                
                # Extract variables from template
                import re
                found_variables = re.findall(r'\{(\w+)\}', template_content)
                found_variables = list(set(found_variables))
                
                # Check variable consistency
                if variables:
                    missing_vars = [var for var in variables if var not in found_variables]
                    extra_vars = [var for var in found_variables if var not in variables]
                    
                    if missing_vars:
                        validation_results["warnings"].append(
                            f"Expected variables not found in template: {missing_vars}"
                        )
                    
                    if extra_vars:
                        validation_results["warnings"].append(
                            f"Unexpected variables found in template: {extra_vars}"
                        )
                
                # Check for proper markdown structure
                if template_content.count('#') == 0:
                    validation_results["warnings"].append(
                        "Template lacks proper heading structure"
                    )
                
                # Check for balanced braces
                open_braces = template_content.count('{')
                close_braces = template_content.count('}')
                if open_braces != close_braces:
                    validation_results["is_valid"] = False
                    validation_results["issues"].append(
                        f"Unbalanced braces: {open_braces} open, {close_braces} close"
                    )
                
                # Check for common template patterns
                if '{title}' not in template_content:
                    validation_results["suggestions"].append(
                        "Consider adding a {title} variable for the blog post title"
                    )
                
                if '{content}' not in template_content and '{main_content}' not in template_content:
                    validation_results["suggestions"].append(
                        "Consider adding a content variable for the main blog post content"
                    )
                
                validation_results["found_variables"] = found_variables
                validation_results["variable_count"] = len(found_variables)
                
                logger.info(f"Template validation completed. Valid: {validation_results['is_valid']}")
                return validation_results
                
            except Exception as e:
                logger.error(f"Error validating template: {str(e)}")
                return {
                    "is_valid": False,
                    "issues": [f"Validation error: {str(e)}"],
                    "warnings": [],
                    "suggestions": []
                }
        
        return validate_template_structure
    
    def _perform_detailed_feedback_analysis(self, feedback: str, 
                                          template_data: Dict[str, Any],
                                          generated_content: str) -> Dict[str, Any]:
        """Perform detailed analysis of user feedback."""
        
        feedback_lower = feedback.lower()
        analysis = {
            "sentiment": "neutral",
            "specific_issues": [],
            "affected_sections": [],
            "improvement_areas": [],
            "severity": "low",
            "feedback_categories": []
        }
        
        # Sentiment analysis
        positive_indicators = [
            "good", "great", "excellent", "perfect", "like", "love", 
            "helpful", "clear", "well-written", "informative"
        ]
        negative_indicators = [
            "bad", "poor", "terrible", "awful", "hate", "dislike", 
            "confusing", "unclear", "boring", "repetitive", "wrong"
        ]
        
        positive_score = sum(1 for word in positive_indicators if word in feedback_lower)
        negative_score = sum(1 for word in negative_indicators if word in feedback_lower)
        
        if positive_score > negative_score:
            analysis["sentiment"] = "positive"
        elif negative_score > positive_score:
            analysis["sentiment"] = "negative"
            analysis["severity"] = "medium" if negative_score > 2 else "low"
        
        # Identify specific issues
        issue_patterns = {
            "length": ["too long", "too short", "lengthy", "brief"],
            "clarity": ["unclear", "confusing", "hard to understand", "complicated"],
            "structure": ["poorly structured", "disorganized", "messy layout"],
            "tone": ["wrong tone", "too formal", "too casual", "inappropriate"],
            "content": ["missing information", "incomplete", "lacks detail", "superficial"],
            "formatting": ["bad formatting", "poor layout", "formatting issues"]
        }
        
        for issue_type, patterns in issue_patterns.items():
            if any(pattern in feedback_lower for pattern in patterns):
                analysis["specific_issues"].append(issue_type)
                analysis["feedback_categories"].append(issue_type)
        
        # Identify affected template sections
        template_sections = {
            "title": ["title", "heading", "header"],
            "introduction": ["introduction", "intro", "opening", "beginning"],
            "main_content": ["content", "body", "main section", "article"],
            "conclusion": ["conclusion", "ending", "summary", "wrap-up"],
            "formatting": ["format", "layout", "structure", "organization"]
        }
        
        for section, keywords in template_sections.items():
            if any(keyword in feedback_lower for keyword in keywords):
                analysis["affected_sections"].append(section)
        
        # Determine improvement areas
        if "length" in analysis["specific_issues"]:
            analysis["improvement_areas"].append("content_length")
        if "clarity" in analysis["specific_issues"]:
            analysis["improvement_areas"].append("readability")
        if "structure" in analysis["specific_issues"]:
            analysis["improvement_areas"].append("organization")
        if "tone" in analysis["specific_issues"]:
            analysis["improvement_areas"].append("writing_style")
        
        return analysis
    
    def _generate_improvement_suggestions(self, analysis: Dict[str, Any], 
                                        template_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific improvement suggestions based on analysis."""
        
        suggestions = []
        template_content = template_data.get("content", "")
        
        # Address specific issues
        for issue in analysis.get("specific_issues", []):
            if issue == "length":
                suggestions.append({
                    "type": "content_adjustment",
                    "description": "Adjust content length guidelines in template",
                    "action": "modify_content_instructions",
                    "priority": "medium",
                    "implementation": "Add length guidelines or modify content sections"
                })
            
            elif issue == "clarity":
                suggestions.append({
                    "type": "clarity_improvement",
                    "description": "Improve clarity and readability instructions",
                    "action": "add_clarity_guidelines",
                    "priority": "high",
                    "implementation": "Add instructions for clear, concise writing"
                })
            
            elif issue == "structure":
                suggestions.append({
                    "type": "structural_improvement",
                    "description": "Improve template organization and flow",
                    "action": "restructure_template",
                    "priority": "high",
                    "implementation": "Reorganize sections for better logical flow"
                })
            
            elif issue == "tone":
                suggestions.append({
                    "type": "tone_adjustment",
                    "description": "Adjust tone and writing style guidelines",
                    "action": "modify_tone_instructions",
                    "priority": "medium",
                    "implementation": "Add tone-specific instructions or examples"
                })
        
        # Address affected sections
        for section in analysis.get("affected_sections", []):
            if section == "introduction":
                suggestions.append({
                    "type": "section_improvement",
                    "section": "introduction",
                    "description": "Improve introduction section based on feedback",
                    "action": "enhance_introduction",
                    "priority": "medium",
                    "implementation": "Add guidelines for engaging introductions"
                })
            
            elif section == "conclusion":
                suggestions.append({
                    "type": "section_improvement",
                    "section": "conclusion",
                    "description": "Improve conclusion section based on feedback",
                    "action": "enhance_conclusion",
                    "priority": "medium",
                    "implementation": "Add guidelines for effective conclusions"
                })
        
        # Remove duplicates
        unique_suggestions = []
        seen_types = set()
        
        for suggestion in suggestions:
            suggestion_key = f"{suggestion['type']}_{suggestion.get('section', '')}"
            if suggestion_key not in seen_types:
                unique_suggestions.append(suggestion)
                seen_types.add(suggestion_key)
        
        return unique_suggestions
    
    def _assess_change_impact(self, suggestions: List[Dict[str, Any]], 
                            template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the impact of proposed changes."""
        
        impact_assessment = {
            "overall_impact": "low",
            "affected_components": [],
            "backward_compatibility": True,
            "risk_level": "low",
            "estimated_effort": "minimal",
            "user_confirmation_required": True
        }
        
        high_impact_types = ["structural_improvement", "restructure_template"]
        medium_impact_types = ["section_improvement", "content_adjustment"]
        
        high_impact_count = sum(1 for s in suggestions if s.get("type") in high_impact_types)
        medium_impact_count = sum(1 for s in suggestions if s.get("type") in medium_impact_types)
        
        if high_impact_count > 0:
            impact_assessment["overall_impact"] = "high"
            impact_assessment["risk_level"] = "medium"
            impact_assessment["estimated_effort"] = "significant"
            impact_assessment["backward_compatibility"] = False
        elif medium_impact_count > 1:
            impact_assessment["overall_impact"] = "medium"
            impact_assessment["estimated_effort"] = "moderate"
        
        # Identify affected components
        for suggestion in suggestions:
            if suggestion.get("section"):
                impact_assessment["affected_components"].append(suggestion["section"])
            if suggestion.get("type"):
                impact_assessment["affected_components"].append(suggestion["type"])
        
        impact_assessment["affected_components"] = list(set(impact_assessment["affected_components"]))
        
        return impact_assessment
    
    def _apply_template_improvements(self, template_data: Dict[str, Any], 
                                   suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply improvement suggestions to the template."""
        
        updated_template = template_data.copy()
        content = updated_template.get("content", "")
        
        changes_applied = []
        
        for suggestion in suggestions:
            suggestion_type = suggestion.get("type", "")
            
            if suggestion_type == "clarity_improvement":
                # Add clarity instructions
                if "## Writing Guidelines" not in content:
                    content += "\n\n## Writing Guidelines\n\n*Write clearly and concisely. Use simple language and short sentences.*"
                    changes_applied.append("Added clarity guidelines")
            
            elif suggestion_type == "content_adjustment":
                # Add length guidelines
                if "word count" not in content.lower():
                    content += "\n\n*Target length: 500-1000 words*"
                    changes_applied.append("Added length guidelines")
            
            elif suggestion_type == "structural_improvement":
                # Improve section organization
                if content.count("##") < 2:
                    content = content.replace(
                        "{main_content}",
                        "## Overview\n\n{overview}\n\n## Details\n\n{main_content}"
                    )
                    if "overview" not in updated_template.get("variables", []):
                        updated_template["variables"].append("overview")
                    changes_applied.append("Improved section structure")
            
            elif suggestion_type == "section_improvement":
                section = suggestion.get("section", "")
                if section == "introduction":
                    content = content.replace(
                        "{introduction}",
                        "{introduction}\n\n*Make this introduction engaging and informative*"
                    )
                    changes_applied.append("Enhanced introduction section")
                elif section == "conclusion":
                    content = content.replace(
                        "{conclusion}",
                        "{conclusion}\n\n*Provide a strong conclusion with key takeaways*"
                    )
                    changes_applied.append("Enhanced conclusion section")
        
        updated_template["content"] = content
        updated_template["changes_applied"] = changes_applied
        
        return updated_template
    
    def _update_template_metadata(self, template_data: Dict[str, Any], 
                                feedback_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Update template metadata with feedback information."""
        
        # Update version
        current_version = template_data.get("version", "1.0.0")
        version_parts = current_version.split(".")
        version_parts[-1] = str(int(version_parts[-1]) + 1)
        template_data["version"] = ".".join(version_parts)
        
        # Add feedback entry to history
        feedback_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis": feedback_analysis,
            "changes_applied": template_data.get("changes_applied", []),
            "version": template_data["version"]
        }
        
        if "feedback_history" not in template_data:
            template_data["feedback_history"] = []
        
        template_data["feedback_history"].append(feedback_entry)
        
        # Update timestamps
        template_data["updated_at"] = datetime.utcnow().isoformat()
        
        return template_data
    
    async def process_feedback(self, template_id: str, feedback: str, 
                             generated_content: str = "",
                             user_confirmation: bool = False) -> Dict[str, Any]:
        """
        Process user feedback and update template accordingly.
        
        Args:
            template_id: ID of the template to update
            feedback: User feedback text
            generated_content: The content that received feedback
            user_confirmation: Whether user has confirmed the changes
            
        Returns:
            Dictionary containing processing results
        """
        try:
            logger.info(f"Template Manager Agent: Processing feedback for template {template_id}")
            
            prompt = f"""
            Please analyze the following user feedback and propose template improvements:
            
            Template ID: {template_id}
            User Feedback: "{feedback}"
            Generated Content Preview: {generated_content[:200] + "..." if len(generated_content) > 200 else generated_content}
            User Confirmation: {user_confirmation}
            
            Please:
            1. Analyze the feedback to understand the user's concerns
            2. Identify specific areas for improvement in the template
            3. Propose concrete changes to address the feedback
            4. {"Apply the changes since user has confirmed" if user_confirmation else "Present the proposed changes for user confirmation"}
            
            Use the available tools to analyze and update the template appropriately.
            """
            
            # Run the agent
            response = await self.agent.arun(prompt)
            
            logger.info(f"Template Manager Agent: Feedback processing completed for template {template_id}")
            
            return {
                "status": "success",
                "agent_response": response.content,
                "template_id": template_id,
                "user_confirmation": user_confirmation,
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "template_id": template_id
            }
    
    async def create_new_template(self, name: str, description: str, 
                                content_type: str = "general") -> Dict[str, Any]:
        """
        Create a new blog template based on specifications.
        
        Args:
            name: Template name
            description: Template description
            content_type: Type of content (general, technical, news, etc.)
            
        Returns:
            Dictionary containing creation results
        """
        try:
            logger.info(f"Template Manager Agent: Creating new template '{name}'")
            
            prompt = f"""
            Please create a new blog post template with the following specifications:
            
            Template Name: {name}
            Description: {description}
            Content Type: {content_type}
            
            Please:
            1. Design a template structure appropriate for {content_type} content
            2. Include relevant variables and placeholders
            3. Ensure proper markdown formatting
            4. Validate the template structure
            5. Create the template using the available tools
            
            Make the template flexible and suitable for various {content_type} topics.
            """
            
            # Run the agent
            response = await self.agent.arun(prompt)
            
            logger.info(f"Template Manager Agent: Template creation completed for '{name}'")
            
            return {
                "status": "success",
                "agent_response": response.content,
                "template_name": name,
                "content_type": content_type,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "template_name": name
            }


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from agno.db.sqlite import SqliteDb
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create database
    db = SqliteDb(db_file="test_template_manager.db")
    
    # Create template manager agent
    template_manager = TemplateManagerAgent(db)
    
    async def test_template_manager():
        # Test feedback processing
        feedback = "The introduction is too long and the conclusion needs more detail."
        result = await template_manager.process_feedback(
            template_id="default",
            feedback=feedback,
            generated_content="Sample blog content...",
            user_confirmation=False
        )
        
        print(f"Feedback processing result: {result['status']}")
        if result["status"] == "success":
            print(f"Agent response: {result['agent_response'][:300]}...")
        
        # Test new template creation
        creation_result = await template_manager.create_new_template(
            name="Technical Tutorial",
            description="Template for technical tutorials and how-to guides",
            content_type="technical"
        )
        
        print(f"Template creation result: {creation_result['status']}")
        
        # Clean up
        import os
        if os.path.exists("test_template_manager.db"):
            os.remove("test_template_manager.db")
    
    # Run test
    asyncio.run(test_template_manager())