"""
Claude API client wrapper for AI Sutra
Optimized for web search and real-time content fetching
"""
import os
from typing import List, Dict, Optional
from anthropic import Anthropic
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Wrapper for Anthropic Claude API
    Handles all interactions with Claude for content curation with web search
    """
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        # Initialize Anthropic client
        self.client = Anthropic(api_key=api_key)
        
        # Use Claude Sonnet 4 for web search capability
        self.model = "claude-sonnet-4-20250514"
    
    async def fetch_content_for_topic(
        self, 
        topic_name: str, 
        description: str = "",
        max_items: int = 5
    ) -> List[Dict[str, str]]:
        """
        Fetch and curate content for a specific topic using web search
        
        Args:
            topic_name: Name of the topic
            description: Description to guide search
            max_items: Maximum number of items to return
            
        Returns:
            List of content items with title, summary, url, source
        """
        
        prompt = f"""You are a content curator for "{topic_name}".

Your task: Use web search to find {max_items} of the latest, most relevant, high-quality content about this topic.

Topic: {topic_name}
{f"Additional context: {description}" if description else ""}

Search the web for recent articles, news, updates from the past 1-24 hours.

CRITICAL: You MUST respond with ONLY a valid JSON array. No explanations, no preamble, no markdown backticks.

Return EXACTLY this format:
[
  {{
    "title": "Article title here",
    "summary": "Brief 2-3 sentence summary",
    "url": "https://actual-url.com",
    "source": "Source name"
  }}
]

Rules:
- Return {max_items} recent items
- Use web_search tool to find current content  
- URLs must be real and working
- Focus on content from the last 24-48 hours
- No explanations before or after the JSON
- Start response with [ and end with ]"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search"
                }]
            )
            
            # Extract text from response
            result_text = self._extract_text_from_response(response)
            
            # Clean and parse JSON
            content_items = self._parse_json_response(result_text)
            
            logger.info(f"✅ Successfully fetched {len(content_items)} items for {topic_name}")
            
            return content_items[:max_items]
            
        except Exception as e:
            logger.error(f"❌ Error fetching content for {topic_name}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def generate_ai_content(
        self,
        topic_name: str,
        description: str,
        time_period: str,
        current_date: str
    ) -> Dict[str, str]:
        """
        Generate AI content for a topic - comprehensive, time-aware response
        
        Args:
            topic_name: Name of the topic
            description: Additional details/context
            time_period: Time period string (e.g., "Daily - Feb 11, 2026")
            current_date: Current date string
            
        Returns:
            Dictionary with title, summary, and content
        """
        
        prompt = f"""You are generating personalized content for: {topic_name}

Context: {description}
Time Period: {time_period}
Current Date: {current_date}

Your task:
1. Use web_search to gather the LATEST information relevant to this topic and time period
2. Generate a comprehensive, well-written response that:
   - Is time-aware (considers current planetary positions for astrology, current market data for stocks, etc.)
   - Uses the latest available information
   - Is personalized based on the provided context/details
   - Is formatted as a complete article/report

CRITICAL: Return ONLY valid JSON with this exact format:
{{
  "title": "A compelling title for this content",
  "summary": "A 2-3 sentence summary",
  "content": "The full comprehensive response (can be multiple paragraphs, use \\n for line breaks)"
}}

Guidelines:
- For astrology: Consider current planetary transits and the specific time period
- For market analysis: Use latest market data and trends
- For personalized advice: Consider the user's specific details
- Make it conversational, engaging, and valuable
- The content should be substantial (300-500 words minimum)

Return ONLY the JSON object. No markdown, no backticks, no explanations."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "web_search_20250305",
                    "name": "web_search"
                }]
            )
            
            # Extract text from response
            result_text = self._extract_text_from_response(response)
            
            # Parse JSON
            import json
            
            # Clean text
            result_text = result_text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            elif result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            ai_content = json.loads(result_text)
            
            logger.info(f"✅ Generated AI content: {ai_content.get('title', 'Untitled')}")
            
            return ai_content
            
        except Exception as e:
            logger.error(f"❌ Error generating AI content: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    async def generate_learning_content(
        self,
        topic_name: str,
        description: str,
        current_day: int,
        total_days: int,
        previous_context: str
    ) -> Dict[str, str]:
        """
        Generate structured learning content - day-by-day curriculum
        
        Args:
            topic_name: Name of the learning topic
            description: Additional details/goals
            current_day: Current day number (1, 2, 3...)
            total_days: Total days in the learning plan
            previous_context: Summary of previous lessons
            
        Returns:
            Dictionary with title, summary, and content
        """
        
        prompt = f"""You are creating a structured learning curriculum for: {topic_name}

Learning Goal: {description}
Current Progress: Day {current_day} of {total_days}

{previous_context}

Your task: Create a comprehensive, structured lesson for Day {current_day}.

IMPORTANT GUIDELINES:
1. This is part of a {total_days}-day structured curriculum
2. Build progressively on previous lessons
3. Include: Theory, Examples, Exercises, and Practice Problems
4. Make it hands-on and practical
5. Ensure the content is substantial and educational
6. Format it like a proper course lesson, not a news article

Structure your lesson with:
- Clear learning objectives for this day
- Theoretical concepts explained simply
- Practical examples with code/exercises (if applicable)
- Step-by-step exercises the learner should complete
- Summary of key takeaways
- Preview of what's coming next

CRITICAL: Return ONLY valid JSON with this exact format:
{{
  "title": "Day {current_day}: [Specific topic for today]",
  "summary": "Brief 2-3 sentence overview of what this lesson covers",
  "content": "The complete structured lesson (use \\n\\n for paragraphs, include headers like:\\n\\n## Learning Objectives\\n\\n## Theory\\n\\n## Examples\\n\\n## Exercises\\n\\n## Summary\\n\\n)"
}}

Make the content feel like a real course - structured, educational, and progressive.
Minimum 500 words for the content section.

Return ONLY the JSON object. No markdown, no backticks, no explanations."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract text from response
            result_text = self._extract_text_from_response(response)
            
            # Parse JSON
            import json
            
            # Clean text
            result_text = result_text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            elif result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            learning_content = json.loads(result_text)
            
            logger.info(f"✅ Generated learning content: {learning_content.get('title', 'Untitled')}")
            
            return learning_content
            
        except Exception as e:
            logger.error(f"❌ Error generating learning content: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    
    
    
    def _extract_text_from_response(self, response) -> str:
        """
        Extract text content from Claude API response
        Handles different response formats and content blocks
        """
        result_text = ""
        
        # Handle content blocks
        if hasattr(response, 'content'):
            for block in response.content:
                # Check block type
                if hasattr(block, 'type'):
                    if block.type == "text":
                        result_text += block.text
                    elif block.type == "tool_use":
                        # Skip tool use blocks, we want the final text response
                        continue
                elif hasattr(block, 'text'):
                    result_text += block.text
                else:
                    # Fallback: convert to string
                    result_text += str(block)
        
        return result_text.strip()
    
    def _parse_json_response(self, text: str) -> List[Dict[str, str]]:
        """
        Parse JSON from text, handling markdown code blocks and formatting
        """
        import json
        
        # Clean up text
        text = text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        # Try to parse JSON
        try:
            data = json.loads(text)
            
            # Ensure it's a list
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                logger.warning(f"⚠️ Unexpected data type: {type(data)}")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {e}")
            logger.error(f"Raw text (first 300 chars): {text[:300]}...")
            return []
    
    async def test_connection(self) -> bool:
        """Test if Claude API connection is working"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[{"role": "user", "content": "Say 'hello' if you can read this."}]
            )
            result = self._extract_text_from_response(response)
            return "hello" in result.lower()
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False


# Singleton instance
_claude_client: Optional[ClaudeClient] = None


def get_claude_client() -> ClaudeClient:
    """Get or create Claude client instance (singleton pattern)"""
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient()
    return _claude_client