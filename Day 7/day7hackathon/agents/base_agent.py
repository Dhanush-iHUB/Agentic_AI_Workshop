from langchain_google_genai import ChatGoogleGenerativeAI
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, model_name="gemini-1.5-flash", temperature=0.7):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature
        )
        
    @abstractmethod
    def process(self, *args, **kwargs):
        """Process method to be implemented by each agent"""
        pass
    
    def _create_messages(self, system_prompt, user_prompt):
        """Helper method to create message format for the LLM (Gemini expects tuples)"""
        messages = [
            ("system", system_prompt),
            ("human", user_prompt)
        ]
        return messages 