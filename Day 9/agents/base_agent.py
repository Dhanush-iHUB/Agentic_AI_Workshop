from langchain.agents import Tool, AgentExecutor, BaseSingleActionAgent
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import AgentAction, AgentFinish
from langchain.prompts import BaseChatPromptTemplate
from typing import List, Tuple, Any, Union
from abc import ABC, abstractmethod

class BaseAgent(BaseSingleActionAgent, ABC):
    def __init__(self, model_name="models/gemini-1.5-flash", temperature=0.7):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.tools = self._get_tools()
        
    @abstractmethod
    def _get_tools(self) -> List[Tool]:
        """Return list of tools available to the agent"""
        pass
        
    @abstractmethod
    def aplan(self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs) -> Union[AgentAction, AgentFinish]:
        """Plan the next action based on observations"""
        pass

    def plan(self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs) -> Union[AgentAction, AgentFinish]:
        """Wrapper for aplan to maintain compatibility"""
        return self.aplan(intermediate_steps, **kwargs)

    @property
    def input_keys(self) -> List[str]:
        """Return expected input keys."""
        return ["input"]
        
    def return_stopped_response(self, early_stopping_method: str, **kwargs) -> AgentFinish:
        """Return response when agent has been stopped"""
        return AgentFinish(
            return_values={"output": "Task failed - agent stopped early"},
            log="Agent stopped due to iteration limit or error"
        )

    def _create_messages(self, system_prompt: str, user_prompt: str) -> List[Tuple[str, str]]:
        """Helper method to create message format for the LLM"""
        messages = [
            ("system", system_prompt),
            ("human", user_prompt)
        ]
        return messages 