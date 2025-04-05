"""
Content Agent module for the Autonomous Marketing Agent.

This module implements the Content Agent that handles content creation,
optimization, and management across various marketing channels.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime

from core.agents.base_agent import BaseAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContentAgent(BaseAgent):
    """
    Agent responsible for content creation and management.
    
    The Content Agent handles:
    1. Content planning and calendar management
    2. Multi-format content generation
    3. Content optimization
    4. Content performance tracking
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Content Agent.
        
        Args:
            config: Agent configuration
        """
        super().__init__(config)
        self.content_calendar = {}
        self.content_templates = {}
        self.content_metrics = {}
        logger.info("Content Agent initialized")
        
    def _register_actions(self) -> None:
        """
        Register all actions that this agent can perform.
        """
        self.register_action("generate_content", self.generate_content)
        self.register_action("optimize_content", self.optimize_content)
        self.register_action("plan_content_calendar", self.plan_content_calendar)
        self.register_action("analyze_content_performance", self.analyze_content_performance)
        self.register_action("create_content_brief", self.create_content_brief)
        
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize the Content Agent.
        
        Returns:
            Dict containing initialization status
        """
        try:
            # Load content templates if available
            templates_path = self.config.get("templates_path")
            if templates_path and os.path.exists(templates_path):
                with open(templates_path, 'r') as file:
                    self.content_templates = json.load(file)
                    
            # Load content calendar if available
            calendar_path = self.config.get("calendar_path")
            if calendar_path and os.path.exists(calendar_path):
                with open(calendar_path, 'r') as file:
                    self.content_calendar = json.load(file)
                    
            return {"status": "success", "message": "Content Agent initialized successfully"}
        except Exception as e:
            logger.error(f"Error initializing Content Agent: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def shutdown(self) -> Dict[str, Any]:
        """
        Shutdown the Content Agent.
        
        Returns:
            Dict containing shutdown status
        """
        try:
            # Save content templates
            templates_path = self.config.get("templates_path")
            if templates_path:
                os.makedirs(os.path.dirname(templates_path), exist_ok=True)
                with open(templates_path, 'w') as file:
                    json.dump(self.content_templates, file)
                    
            # Save content calendar
            calendar_path = self.config.get("calendar_path")
            if calendar_path:
                os.makedirs(os.path.dirname(calendar_path), exist_ok=True)
                with open(calendar_path, 'w') as file:
                    json.dump(self.content_calendar, file)
                    
            return {"status": "success", "message": "Content Agent shut down successfully"}
        except Exception as e:
            logger.error(f"Error shutting down Content Agent: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def generate_content(self, 
                              content_type: str, 
                              topic: str, 
                              keywords: List[str], 
                              tone: str = "professional",
                              length: str = "medium") -> Dict[str, Any]:
        """
        Generate content based on specified parameters.
        
        Args:
            content_type: Type of content (blog, social, email, etc.)
            topic: Main topic of the content
            keywords: Target keywords for the content
            tone: Tone of the content
            length: Length of the content
            
        Returns:
            Dict containing generated content
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Get content template
            template = self._get_content_template(content_type)
            
            # Generate content
            # In a real implementation, this would use NLP models or APIs
            content = self._generate_content_from_template(template, topic, keywords, tone, length)
            
            # Generate metadata
            metadata = {
                "content_type": content_type,
                "topic": topic,
                "keywords": keywords,
                "tone": tone,
                "length": length,
                "generated_at": datetime.now().isoformat(),
                "word_count": len(content.split())
            }
            
            # Generate content ID
            content_id = f"{content_type}_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Update knowledge graph
            if self.knowledge_graph:
                # Create content node
                self.knowledge_graph.add_node(content_id, {
                    "type": "content",
                    "content_type": content_type,
                    "topic": topic,
                    "metadata": metadata
                })
                
                # Connect to content category
                self.knowledge_graph.add_edge("content", content_id, {"type": "contains"})
                
                # Connect to keywords
                for keyword in keywords:
                    keyword_id = f"keyword_{keyword.replace(' ', '_')}"
                    if keyword_id in self.knowledge_graph.graph:
                        self.knowledge_graph.add_edge(content_id, keyword_id, {"type": "targets"})
                    
            execution_time = asyncio.get_event_loop().time() - start_time
            return {
                "status": "success",
                "content_id": content_id,
                "content": content,
                "metadata": metadata,
                "execution_time": execution_time
            }
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def optimize_content(self, 
                              content: str, 
                              content_type: str,
                              target_platform: str,
                              target_audience: str,
                              optimization_goals: List[str]) -> Dict[str, Any]:
        """
        Optimize content for specific platforms and audiences.
        
        Args:
            content: Content to optimize
            content_type: Type of content
            target_platform: Platform to optimize for
            target_audience: Target audience
            optimization_goals: Goals for optimization
            
        Returns:
            Dict containing optimized content
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Analyze content
            content_analysis = self._analyze_content(content, content_type)
            
            # Generate optimization recommendations
            recommendations = self._generate_optimization_recommendations(
                content_analysis, target_platform, target_audience, optimization_goals
            )
            
            # Apply optimizations
            optimized_content = self._apply_content_optimizations(content, recommendations)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            return {
                "status": "success",
                "original_content": content,
                "optimized_content": optimized_content,
                "analysis": content_analysis,
                "recommendations": recommendations,
                "execution_time": execution_time
            }
        except Exception as e:
            logger.error(f"Error optimizing content: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def plan_content_calendar(self, 
                                   start_date: str,
                                   end_date: str,
                                   content_types: List[str],
                                   topics: List[str],
                                   frequency: Dict[str, int]) -> Dict[str, Any]:
        """
        Plan a content calendar for a specified period.
        
        Args:
            start_date: Start date for the calendar
            end_date: End date for the calendar
            content_types: Types of content to include
            topics: Topics to cover
            frequency: Frequency of each content type
            
        Returns:
            Dict containing content calendar
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Generate content calendar
            calendar = self._generate_content_calendar(
                start_date, end_date, content_types, topics, frequency
            )
            
            # Update content calendar
            calendar_id = f"calendar_{start_date}_{end_date}"
            self.content_calendar[calendar_id] = calendar
            
            # Update knowledge graph
            if self.knowledge_graph:
                # Create calendar node
                self.knowledge_graph.add_node(calendar_id, {
                    "type": "content_calendar",
                    "start_date": start_date,
                    "end_date": end_date,
                    "calendar": calendar
                })
                
                # Connect to content category
                self.knowledge_graph.add_edge("content", calendar_id, {"type": "contains"})
                
            execution_time = asyncio.get_event_loop().time() - start_time
            return {
                "status": "success",
                "calendar_id": calendar_id,
                "calendar": calendar,
                "execution_time": execution_time
            }
        except Exception as e:
            logger.error(f"Error planning content calendar: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def analyze_content_performance(self, 
                                         content_ids: List[str],
                                         metrics: List[str],
                                         period: str = "last_month") -> Dict[str, Any]:
        """
        Analyze content performance.
        
        Args:
            content_ids: IDs of content to analyze
            metrics: Metrics to analyze
            period: Time period for analysis
            
        Returns:
            Dict containing content performance analysis
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Analyze content performance
            # In a real implementation, this would use analytics APIs
            performance = {}
            
            for content_id in content_ids:
                performance[content_id] = self._simulate_content_performance(content_id, metrics, period)
                
                # Update content metrics
                self.content_metrics[content_id] = performance[content_id]
                
                # Update knowledge graph
                if self.knowledge_graph and content_id in self.knowledge_graph.graph:
                    self.knowledge_graph.update_node(content_id, {
                        "performance": performance[content_id]
                    })
                    
            execution_time = asyncio.get_event_loop().time() - start_time
            return {
                "status": "success",
                "content_analyzed": len(content_ids),
                "performance": performance,
                "execution_time": execution_time
            }
        except Exception as e:
            logger.error(f"Error analyzing content performance: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def create_content_brief(self, 
                                  topic: str,
                                  content_type: str,
                                  target_audience: str,
                                  keywords: List[str],
                                  competitors: List[str] = None) -> Dict[str, Any]:
        """
        Create a content brief for content creation.
        
        Args:
            topic: Topic for the content
            content_type: Type of content
            target_audience: Target audience
            keywords: Target keywords
            competitors: Competitor content to analyze
            
        Returns:
            Dict containing content brief
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Analyze competitors if provided
            competitor_analysis = {}
            if competitors:
                for competitor in competitors:
                    competitor_analysis[competitor] = self._analyze_competitor_content(
                        competitor, topic, content_type
                    )
                    
            # Generate content brief
            brief = {
                "topic": topic,
                "content_type": content_type,
                "target_audience": target_audience,
                "keywords": keywords,
                "outline": self._generate_content_outline(topic, content_type, keywords),
                "tone_and_style": self._recommend_tone_and_style(target_audience, content_type),
                "recommended_length": self._recommend_content_length(content_type),
                "competitor_analysis": competitor_analysis,
                "created_at": datetime.now().isoformat()
            }
            
            # Generate brief ID
            brief_id = f"brief_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Update knowledge graph
            if self.knowledge_graph:
                # Create brief node
                self.knowledge_graph.add_node(brief_id, {
                    "type": "content_brief",
                    "topic": topic,
                    "content_type": content_type,
                    "brief": brief
                })
                
                # Connect to content category
                self.knowledge_graph.add_edge("content", brief_id, {"type": "contains"})
                
                # Connect to keywords
                for keyword in keywords:
                    keyword_id = f"keyword_{keyword.replace(' ', '_')}"
                    if keyword_id in self.knowledge_graph.graph:
                        self.knowledge_graph.add_edge(brief_id, keyword_id, {"type": "targets"})
                    
            execution_time = asyncio.get_event_loop().time() - start_time
            return {
                "status": "success",
                "brief_id": brief_id,
                "brief": brief,
                "execution_time": execution_time
            }
        except Exception as e:
            logger.error(f"Error creating content brief: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    # Helper methods
    def _get_content_template(self, content_type: str) -> Dict[str, Any]:
        """Get content template for a specific content type."""
        if content_type in self.content_templates:
            return self.content_templates[content_type]
            
        # Default templates for common content types
        default_templates = {
            "blog": {
                "structure": ["title", "introduction", "main_points", "conclusion"],
                "title_format": "{topic}: {benefit} for {audience}",
                "introduction_format": "Introduction about {topic} highlighting {pain_point} and {solution}.",
                "main_points_format": "Main points about {topic} with {examples} and {statistics}.",
                "conclusion_format": "Conclusion summarizing {key_points} with {call_to_action}."
            },
            "social": {
                "structure": ["hook", "value", "call_to_action"],
                "hook_format": "Attention-grabbing statement about {topic}.",
                "value_format": "Value proposition related to {topic}.",
                "call_to_action_format": "Call to action encouraging {desired_action}."
            },
            "email": {
                "structure": ["subject", "greeting", "body", "closing", "signature"],
                "subject_format": "{benefit} for {audience} with {topic}",
                "greeting_format": "Hello {audience},",
                "body_format": "Email body about {topic} highlighting {pain_point} and {solution}.",
                "closing_format": "Closing with {call_to_action}.",
                "signature_format": "Best regards,\n{sender_name}"
            }
        }
        
        return default_templates.get(content_type, {})
        
    def _generate_content_from_template(self, 
                                       template: Dict[str, Any],
                                       topic: str,
                                       keywords: List[str],
                                       tone: str,
                                       length: str) -> str:
        """Generate content from a template."""
        # This is a simplified implementation
        # In a real system, this would use NLP models to generate high-quality content
        
        if not template or "structure" not in template:
            return f"Generated content about {topic} using keywords: {', '.join(keywords)}."
            
        content_parts = []
        
        # Generate content based on template structure
        for part in template["structure"]:
            format_key = f"{part}_format"
            if format_key in template:
                # Replace placeholders in the format
                part_content = template[format_key]
                part_content = part_content.replace("{topic}", topic)
                
                if "{keywords}" in part_content:
                    part_content = part_content.replace("{keywords}", ", ".join(keywords))
                    
                # Add more placeholder replacements as needed
                part_content = part_content.replace("{audience}", "target audience")
                part_content = part_content.replace("{benefit}", "key benefit")
                part_content = part_content.replace("{pain_point}", "common pain point")
                part_content = part_content.replace("{solution}", "proposed solution")
                part_content = part_content.replace("{examples}", "relevant examples")
                part_content = part_content.replace("{statistics}", "supporting statistics")
                part_content = part_content.replace("{key_points}", "key points")
                part_content = part_content.replace("{call_to_action}", "call to action")
                part_content = part_content.replace("{desired_action}", "desired action")
                part_content = part_content.replace("{sender_name}", "Sender Name")
                
                content_parts.append(part_content)
            else:
                content_parts.append(f"{part.capitalize()} about {topic}.")
                
        # Adjust content length
        content = "\n\n".join(content_parts)
        if length == "short":
            # Simulate shorter content
            content = "\n".join(content_parts[:2])
        elif length == "long":
            # Simulate longer content
            for i in range(2):
                content_parts.append(f"Additional information about {topic} with keyword {keywords[0] if keywords else 'focus'}.")
            content = "\n\n".join(content_parts)
            
        return content
        
    def _analyze_content(self, content: str, content_type: str) -> Dict[str, Any]:
        """Analyze content."""
        # This is a simplified implementation
        # In a real system, this would use NLP to analyze content quality, readability, etc.
        
        words = content.split()
        sentences = content.split('.')
        
        analysis = {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
            "readability": self._calculate_readability(content),
            "sentiment": self._analyze_sentiment(content),
            "content_type": content_type
        }
        
        return analysis
        
    def _calculate_readability(self, content: str) -> float:
        """Calculate readability score."""
        # Simplified Flesch Reading Ease calculation
        words = content.split()
        sentences = content.split('.')
        
        if not words or not sentences:
            return 0
            
        avg_sentence_length = len(words) / len(sentences)
        
        # Simplified calculation
        readability = 206.835 - (1.015 * avg_sentence_length)
        
        return max(0, min(100, readability))
        
    def _analyze_sentiment(self, content: str) -> str:
        """Analyze sentiment of content."""
        # This is a simplified implementation
        # In a real system, this would use NLP models for sentiment analysis
        
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "best", "positive"]
        negative_words = ["bad", "poor", "terrible", "worst", "negative", "awful", "horrible"]
        
        content_lower = content.lower()
        
        positive_count = sum(content_lower.count(word) for word in positive_words)
        negative_count = sum(content_lower.count(word) for word in negative_words)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
            
    def _generate_optimization_recommendations(self, 
                                             content_analysis: Dict[str, Any],
                                             target_platform: str,
                                             target_audience: str,
                                             optimization_goals: List[str]) -> List[Dict[str, Any]]:
        """Generate content optimization recommendations."""
        recommendations = []
        
        # Check word count based on platform
        if target_platform == "blog" and content_analysis["word_count"] < 500:
            recommendations.append({
                "type": "word_count",
                "message": "Content is too short for a blog post. Aim for at least 1000 words for better engagement."
            })
        elif target_platform == "social" and content_analysis["word_count"] > 100:
            recommendations.append({
                "type": "word_count",
                "message": "Content is too long for social media. Keep it under 100 words for better engagement."
            })
            
        # Check readability
        if content_analysis["readability"] < 50:
            recommendations.append({
                "type": "readability",
                "message": "Content readability is low. Simplify sentences and use more common words."
            })
            
        # Check sentiment based on goals
        if "engagement" in optimization_goals and content_analysis["sentiment"] == "neutral":
            recommendations.append({
                "type": "sentiment",
                "message": "Content sentiment is neutral. Consider using more emotionally engaging language for better engagement."
            })
            
        return recommendations
        
    def _apply_content_optimizations(self, content: str, recommendations: List[Dict[str, Any]]) -> str:
        """Apply content optimizations."""
        # This is a simplified implementation
        # In a real system, this would use NLP to intelligently modify the content
        
        optimized_content = content
        
        # Apply simple optimizations based on recommendations
        for recommendation in recommendations:
            if recommendation["type"] == "word_count" and "too short" in recommendation["message"]:
                optimized_content += "\n\nAdditional information to expand on the topic and provide more value to the reader."
            elif recommendation["type"] == "word_count" and "too long" in recommendation["message"]:
                # Simplistic truncation
                words = optimized_content.split()
                if len(words) > 100:
                    optimized_content = " ".join(words[:100])
                    
        return optimized_content
        
    def _generate_content_calendar(self,
                                  start_date: str,
                                  end_date: str,
                                  content_types: List[str],
                                  topics: List[str],
                                  frequency: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate a content calendar."""
        from datetime import datetime, timedelta
        
        # Parse dates
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        calendar = []
        current_date = start
        topic_index = 0
        
        while current_date <= end:
            # Determine content type for this day
            for content_type in content_types:
                # Check if we should publish this content type on this day
                # based on frequency
                days_in_period = (end - start).days + 1
                type_frequency = frequency.get(content_type, 1)
                
                if type_frequency > 0 and days_in_period > 0:
                    # Calculate if this is a publishing day for this content type
                    publishing_interval = days_in_period / type_frequency
                    days_since_start = (current_date - start).days
                    
                    if days_since_start % max(1, int(publishing_interval)) == 0:
                        # Add to calendar
                        topic = topics[topic_index % len(topics)]
                        topic_index += 1
                        
                        calendar_item = {
                            "date": current_date.isoformat(),
                            "content_type": content_type,
                            "topic": topic,
                            "status": "planned"
                        }
                        
                        calendar.append(calendar_item)
                        
            # Move to next day
            current_date += timedelta(days=1)
            
        return calendar
        
    def _simulate_content_performance(self, content_id: str, metrics: List[str], period: str) -> Dict[str, Any]:
        """Simulate content performance metrics."""
        import random
        
        performance = {
            "content_id": content_id,
            "period": period
        }
        
        # Generate random metrics
        for metric in metrics:
            if metric == "views":
                performance[metric] = random.randint(100, 10000)
            elif metric == "engagement":
                performance[metric] = random.uniform(0.01, 0.2)
            elif metric == "shares":
                performance[metric] = random.randint(5, 500)
            elif metric == "comments":
                performance[metric] = random.randint(0, 100)
            elif metric == "conversions":
                performance[metric] = random.randint(1, 50)
            elif metric == "time_on_page":
                performance[metric] = random.uniform(10, 300)
            else:
                performance[metric] = random.randint(1, 100)
                
        return performance
        
    def _analyze_competitor_content(self, competitor: str, topic: str, content_type: str) -> Dict[str, Any]:
        """Analyze competitor content."""
        import random
        
        # This is a simplified implementation
        # In a real system, this would involve web scraping and content analysis
        
        return {
            "competitor": competitor,
            "content_type": content_type,
            "topic": topic,
            "word_count": random.randint(500, 3000),
            "readability": random.uniform(50, 90),
            "key_points": ["Point 1", "Point 2", "Point 3"],
            "strengths": ["Strength 1", "Strength 2"],
            "weaknesses": ["Weakness 1", "Weakness 2"]
        }
        
    def _generate_content_outline(self, topic: str, content_type: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Generate a content outline."""
        if content_type == "blog":
            return [
                {"section": "Introduction", "description": f"Introduction to {topic}"},
                {"section": "What is {topic}", "description": f"Definition and explanation of {topic}"},
                {"section": "Benefits of {topic}", "description": f"Key benefits and advantages of {topic}"},
                {"section": "How to implement {topic}", "description": f"Step-by-step guide to implementing {topic}"},
                {"section": "Case studies", "description": f"Real-world examples of {topic} in action"},
                {"section": "Conclusion", "description": f"Summary and next steps for {topic}"}
            ]
        elif content_type == "social":
            return [
                {"section": "Hook", "description": f"Attention-grabbing statement about {topic}"},
                {"section": "Value", "description": f"Key value proposition related to {topic}"},
                {"section": "Call to Action", "description": f"Clear call to action related to {topic}"}
            ]
        elif content_type == "email":
            return [
                {"section": "Subject Line", "description": f"Compelling subject line about {topic}"},
                {"section": "Introduction", "description": f"Brief introduction to {topic}"},
                {"section": "Main Content", "description": f"Key information about {topic}"},
                {"section": "Call to Action", "description": f"Clear call to action related to {topic}"},
                {"section": "Closing", "description": f"Brief closing statement"}
            ]
        else:
            return [
                {"section": "Main Content", "description": f"Content about {topic}"}
            ]
            
    def _recommend_tone_and_style(self, target_audience: str, content_type: str) -> Dict[str, Any]:
        """Recommend tone and style for content."""
        # Default recommendations based on content type
        if content_type == "blog":
            return {
                "tone": "informative and conversational",
                "style": "educational with practical examples",
                "voice": "second person (you/your)",
                "formality": "semi-formal"
            }
        elif content_type == "social":
            return {
                "tone": "engaging and concise",
                "style": "direct and attention-grabbing",
                "voice": "first person (we/our) or second person (you/your)",
                "formality": "casual"
            }
        elif content_type == "email":
            return {
                "tone": "personal and direct",
                "style": "clear and action-oriented",
                "voice": "second person (you/your)",
                "formality": "business casual"
            }
        else:
            return {
                "tone": "professional",
                "style": "clear and concise",
                "voice": "third person",
                "formality": "formal"
            }
            
    def _recommend_content_length(self, content_type: str) -> Dict[str, Any]:
        """Recommend content length based on content type."""
        if content_type == "blog":
            return {
                "word_count": "1000-2000 words",
                "sections": "5-7 sections",
                "paragraphs_per_section": "2-4 paragraphs"
            }
        elif content_type == "social":
            return {
                "word_count": "50-100 words",
                "sections": "1 section",
                "paragraphs_per_section": "1-2 paragraphs"
            }
        elif content_type == "email":
            return {
                "word_count": "200-500 words",
                "sections": "3-5 sections",
                "paragraphs_per_section": "1-2 paragraphs"
            }
        else:
            return {
                "word_count": "500-1000 words",
                "sections": "3-5 sections",
                "paragraphs_per_section": "1-3 paragraphs"
            }
