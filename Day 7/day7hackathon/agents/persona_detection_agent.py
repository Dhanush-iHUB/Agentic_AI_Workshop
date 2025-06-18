from .base_agent import BaseAgent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

class PersonaResult(BaseModel):
    persona: str = Field(..., description="Either 'genz' or 'professional'")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(..., description="Explanation for the decision")

class PersonaDetectionAgent(BaseAgent):
    def __init__(self, model_name="models/gemini-1.5-flash", temperature=0.7):
        # Use ChatGoogleGenerativeAI directly for structured output
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature
        ).with_structured_output(PersonaResult)
        self.system_prompt = (
            "You are an expert at analyzing website content and identifying the target audience. "
            "Your task is to determine if the content is more suitable for Generation Z (young, informal, trendy) or "
            "Professional (formal, business-oriented) audiences. Analyze the text, tone, and style to make this determination. "
            "Return your response as a JSON with the format: {\"persona\": \"genz|professional\", \"confidence\": 0.0-1.0, \"reasoning\": \"explanation\"}. "
            "Respond ONLY with valid JSON and nothing else."
        )

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
        try:
            result = self.llm.invoke(messages)
            return result.dict()
        except Exception as e:
            return {
                "persona": "professional",  # default to professional if parsing fails
                "confidence": 0.5,
                "reasoning": f"Failed to parse LLM response: {str(e)}"
            } 