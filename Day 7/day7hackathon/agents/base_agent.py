from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.7):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature
        )
        
    @abstractmethod
    def process(self, *args, **kwargs):
        """Process method to be implemented by each agent"""
        pass
    
    def _create_messages(self, system_prompt, user_prompt):
        """Helper method to create message format for the LLM"""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        return messages 