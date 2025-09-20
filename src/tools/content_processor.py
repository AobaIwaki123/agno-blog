"""
Content Processing Tools for Blog Content

This module provides tools for processing, analyzing, and formatting
content for blog post generation and management.
"""

import re
import json
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
from collections import Counter
import hashlib

logger = logging.getLogger(__name__)

class ContentProcessingTools:
    """Tools for processing and structuring extracted content."""
    
    def __init__(self):
        # Common stop words to filter out from keyword extraction
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
    
    def clean_content(self, content: str) -> str:
        """
        Clean and normalize content text.
        
        Args:
            content: Raw content text to clean
            
        Returns:
            Cleaned and normalized content
        """
        if not content:
            return ""
        
        try:
            # Remove extra whitespace and normalize line breaks
            content = re.sub(r'\s+', ' ', content)
            content = re.sub(r'\n\s*\n', '\n\n', content)
            
            # Fix common encoding issues
            content = content.replace('\u2019', "'")  # Right single quotation mark
            content = content.replace('\u2018', "'")  # Left single quotation mark
            content = content.replace('\u201c', '"')  # Left double quotation mark
            content = content.replace('\u201d', '"')  # Right double quotation mark
            content = content.replace('\u2013', '-')  # En dash
            content = content.replace('\u2014', '--') # Em dash
            
            # Remove or replace problematic characters
            content = re.sub(r'[^\w\s.,!?;:()\-"\'\/\n]', '', content)
            
            # Remove repeated punctuation
            content = re.sub(r'([.!?]){2,}', r'\1', content)
            
            # Clean up spacing around punctuation
            content = re.sub(r'\s+([,.!?;:])', r'\1', content)
            content = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', content)
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error cleaning content: {str(e)}")
            return content  # Return original if cleaning fails
    
    def extract_keywords(self, content: str, max_keywords: int = 10) -> List[Tuple[str, int]]:
        """
        Extract keywords from content based on frequency.
        
        Args:
            content: Content text to analyze
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of tuples (keyword, frequency) sorted by frequency
        """
        try:
            if not content:
                return []
            
            # Convert to lowercase and extract words
            words = re.findall(r'\b\w+\b', content.lower())
            
            # Filter out stop words and short words
            filtered_words = [
                word for word in words 
                if len(word) > 3 and word not in self.stop_words
            ]
            
            # Count word frequencies
            word_freq = Counter(filtered_words)
            
            # Return top keywords
            return word_freq.most_common(max_keywords)
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    def generate_summary(self, content: str, max_length: int = 200, sentences: int = 3) -> str:
        """
        Generate a summary of the content.
        
        Args:
            content: Content text to summarize
            max_length: Maximum length of summary
            sentences: Maximum number of sentences to include
            
        Returns:
            Generated summary
        """
        try:
            if not content:
                return ""
            
            # Split into sentences
            sentence_list = re.split(r'[.!?]+', content)
            sentence_list = [s.strip() for s in sentence_list if s.strip()]
            
            if not sentence_list:
                return ""
            
            # Take first few sentences that fit within length limit
            summary = ""
            sentence_count = 0
            
            for sentence in sentence_list:
                if sentence_count >= sentences:
                    break
                    
                potential_summary = summary + sentence + ". "
                if len(potential_summary) <= max_length:
                    summary = potential_summary
                    sentence_count += 1
                else:
                    break
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return content[:max_length] + "..." if len(content) > max_length else content
    
    def analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """
        Analyze the structure and characteristics of content.
        
        Args:
            content: Content text to analyze
            
        Returns:
            Dictionary containing content analysis
        """
        try:
            if not content:
                return {"word_count": 0, "sentence_count": 0, "paragraph_count": 0}
            
            # Basic counts
            words = re.findall(r'\b\w+\b', content)
            sentences = re.split(r'[.!?]+', content)
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            # Content characteristics
            avg_words_per_sentence = len(words) / max(len(sentences), 1)
            avg_words_per_paragraph = len(words) / max(len(paragraphs), 1)
            
            # Reading time estimation (200 words per minute)
            reading_time = max(1, len(words) // 200)
            
            # Content complexity indicators
            long_words = [word for word in words if len(word) > 6]
            complexity_score = len(long_words) / max(len(words), 1)
            
            return {
                "word_count": len(words),
                "sentence_count": len(sentences),
                "paragraph_count": len(paragraphs),
                "avg_words_per_sentence": round(avg_words_per_sentence, 1),
                "avg_words_per_paragraph": round(avg_words_per_paragraph, 1),
                "estimated_reading_time": reading_time,
                "complexity_score": round(complexity_score, 2),
                "character_count": len(content),
                "long_words_count": len(long_words)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content structure: {str(e)}")
            return {"error": str(e)}
    
    def extract_entities(self, content: str) -> Dict[str, List[str]]:
        """
        Extract potential entities from content (simplified version).
        
        Args:
            content: Content text to analyze
            
        Returns:
            Dictionary containing different types of entities
        """
        try:
            entities = {
                "urls": [],
                "emails": [],
                "dates": [],
                "numbers": [],
                "capitalized_words": []
            }
            
            # Extract URLs
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
            entities["urls"] = re.findall(url_pattern, content)
            
            # Extract email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            entities["emails"] = re.findall(email_pattern, content)
            
            # Extract potential dates
            date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
            entities["dates"] = re.findall(date_pattern, content)
            
            # Extract numbers
            number_pattern = r'\b\d+(?:\.\d+)?\b'
            entities["numbers"] = re.findall(number_pattern, content)
            
            # Extract capitalized words (potential proper nouns)
            capitalized_pattern = r'\b[A-Z][a-z]+\b'
            capitalized_words = re.findall(capitalized_pattern, content)
            # Filter out common words and keep unique ones
            entities["capitalized_words"] = list(set([
                word for word in capitalized_words 
                if word.lower() not in self.stop_words and len(word) > 2
            ]))
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return {"error": str(e)}
    
    def generate_content_hash(self, content: str) -> str:
        """
        Generate a unique hash for content to detect duplicates.
        
        Args:
            content: Content text to hash
            
        Returns:
            SHA-256 hash of the content
        """
        try:
            # Normalize content for consistent hashing
            normalized = self.clean_content(content).lower()
            return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        except Exception as e:
            logger.error(f"Error generating content hash: {str(e)}")
            return ""
    
    def split_into_sections(self, content: str, max_section_length: int = 1000) -> List[Dict[str, Any]]:
        """
        Split content into manageable sections.
        
        Args:
            content: Content text to split
            max_section_length: Maximum length per section
            
        Returns:
            List of sections with metadata
        """
        try:
            if not content:
                return []
            
            # Split by paragraphs first
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            sections = []
            current_section = ""
            section_num = 1
            
            for paragraph in paragraphs:
                # Check if adding this paragraph would exceed the limit
                potential_section = current_section + "\n\n" + paragraph if current_section else paragraph
                
                if len(potential_section) <= max_section_length:
                    current_section = potential_section
                else:
                    # Save current section if it has content
                    if current_section:
                        sections.append({
                            "section_number": section_num,
                            "content": current_section.strip(),
                            "word_count": len(re.findall(r'\b\w+\b', current_section)),
                            "character_count": len(current_section)
                        })
                        section_num += 1
                    
                    # Start new section with current paragraph
                    current_section = paragraph
            
            # Add the last section
            if current_section:
                sections.append({
                    "section_number": section_num,
                    "content": current_section.strip(),
                    "word_count": len(re.findall(r'\b\w+\b', current_section)),
                    "character_count": len(current_section)
                })
            
            return sections
            
        except Exception as e:
            logger.error(f"Error splitting content into sections: {str(e)}")
            return [{"section_number": 1, "content": content, "error": str(e)}]
    
    def format_for_markdown(self, content: str, title: str = "") -> str:
        """
        Format content for Markdown output.
        
        Args:
            content: Content text to format
            title: Optional title to include
            
        Returns:
            Markdown-formatted content
        """
        try:
            formatted = ""
            
            # Add title if provided
            if title:
                formatted += f"# {title}\n\n"
            
            # Clean content
            clean_content = self.clean_content(content)
            
            # Split into paragraphs and format
            paragraphs = [p.strip() for p in clean_content.split('\n\n') if p.strip()]
            
            for paragraph in paragraphs:
                # Check if paragraph looks like a heading
                if len(paragraph) < 100 and paragraph.isupper():
                    formatted += f"## {paragraph.title()}\n\n"
                elif len(paragraph) < 80 and not paragraph.endswith('.'):
                    formatted += f"### {paragraph}\n\n"
                else:
                    formatted += f"{paragraph}\n\n"
            
            return formatted.strip()
            
        except Exception as e:
            logger.error(f"Error formatting content for markdown: {str(e)}")
            return content


# Example usage and testing
if __name__ == "__main__":
    # Setup logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Create processor instance
    processor = ContentProcessingTools()
    
    # Test content
    test_content = """
    This is a sample article about artificial intelligence and machine learning.
    
    Machine learning is a subset of AI that focuses on algorithms. These algorithms
    can learn patterns from data without being explicitly programmed.
    
    Some popular applications include natural language processing, computer vision,
    and recommendation systems. Companies like Google, Microsoft, and OpenAI are
    leading the way in AI research.
    """
    
    print("Testing ContentProcessingTools:")
    print(f"Original content length: {len(test_content)}")
    
    # Test cleaning
    clean_content = processor.clean_content(test_content)
    print(f"Cleaned content length: {len(clean_content)}")
    
    # Test keyword extraction
    keywords = processor.extract_keywords(clean_content)
    print(f"Keywords: {keywords}")
    
    # Test summary generation
    summary = processor.generate_summary(clean_content)
    print(f"Summary: {summary}")
    
    # Test content analysis
    analysis = processor.analyze_content_structure(clean_content)
    print(f"Content analysis: {analysis}")
    
    # Test entity extraction
    entities = processor.extract_entities(clean_content)
    print(f"Entities: {entities}")
    
    # Test content hash
    content_hash = processor.generate_content_hash(clean_content)
    print(f"Content hash: {content_hash[:16]}...")
    
    # Test markdown formatting
    markdown = processor.format_for_markdown(clean_content, "AI and Machine Learning")
    print(f"Markdown formatted:\n{markdown}")