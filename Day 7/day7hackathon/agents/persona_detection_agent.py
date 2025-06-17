from .base_agent import BaseAgent
import json

class PersonaDetectionAgent(BaseAgent):
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.7):
        super().__init__(model_name, temperature)
        self.system_prompt = """You are an expert at analyzing website content and identifying the target audience.
        Your task is to determine if the content is more suitable for Generation Z (young, informal, trendy) or
        Professional (formal, business-oriented) audiences. Analyze the text, tone, and style to make this determination.
        Return your response as a JSON with the format: {"persona": "genz|professional", "confidence": 0.0-1.0, "reasoning": "explanation"}"""
    
    def process(self, content):
        """
        Analyze content and determine the target persona
        Args:
            content (str): The website content to analyze
        Returns:
            dict: Contains persona type, confidence score, and reasoning
        """
        messages = self._create_messages(
            self.system_prompt,
            f"Analyze this content and determine the target audience:\n\n{content}"
        )
        
        response = self.llm.invoke(messages)
        try:
            result = json.loads(response.content)
            return result
        except json.JSONDecodeError:
            return {
                "persona": "professional",  # default to professional if parsing fails
                "confidence": 0.5,
                "reasoning": "Failed to parse LLM response, defaulting to professional persona"
            } 