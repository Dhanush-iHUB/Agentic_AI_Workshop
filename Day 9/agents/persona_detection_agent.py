from .base_agent import BaseAgent
from langchain.agents import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import AgentAction, AgentFinish
from typing import List, Tuple, Dict, Any, Union

class PersonaResult(BaseModel):
    persona: str = Field(..., description="Either 'genz' or 'professional'")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(..., description="Explanation for the decision")

class PersonaDetectionAgent(BaseAgent):
    def __init__(self, model_name="models/gemini-1.5-flash", temperature=0.7):
        super().__init__(model_name, temperature)
        
        # Initialize chains
        self.text_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["text"],
                template="""Analyze the following text and identify key indicators of the target audience:
                Text: {text}
                
                Consider:
                - Language complexity and formality
                - Industry-specific terminology
                - Cultural references
                - Writing style and tone
                """
            )
        )
        
        self.persona_classification_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["analysis", "text"],
                template="""Based on the analysis and text, determine if the content is more suitable for:
                1. Generation Z ('genz'): casual, modern, emoji-friendly, informal
                2. Professional: formal, business-oriented, industry-standard
                
                Analysis: {analysis}
                Text: {text}
                
                Respond with either 'genz' or 'professional' and a brief explanation.
                """
            )
        )
    
    def _get_tools(self) -> List[Tool]:
        """Define tools available to this agent"""
        return [
            Tool(
                name="analyze_text",
                func=self._analyze_text,
                description="Analyzes text to identify audience indicators"
            ),
            Tool(
                name="classify_persona",
                func=self._classify_persona,
                description="Classifies text as targeting either 'genz' or 'professional' persona"
            )
        ]
    
    def _analyze_text(self, text: str) -> Dict[str, str]:
        """Tool function to analyze text for audience indicators"""
        result = self.text_analysis_chain.run(text=text)
        return {"analysis": result}
    
    def _classify_persona(self, text: str, analysis: str) -> Dict[str, str]:
        """Tool function to classify the target persona"""
        result = self.persona_classification_chain.run(
            text=text,
            analysis=analysis
        )
        persona = "genz" if "genz" in result.lower() else "professional"
        return {
            "persona": persona,
            "explanation": result
        }
    
    def plan(self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs) -> Union[AgentAction, AgentFinish]:
        """Plan next action based on current state"""
        text = kwargs.get("text", "")
        
        # If no steps taken yet, start with text analysis
        if not intermediate_steps:
            return AgentAction(
                tool="analyze_text",
                tool_input=text,
                log="Analyzing text for audience indicators"
            )
        
        # If text analyzed, proceed with persona classification
        if len(intermediate_steps) == 1:
            analysis = intermediate_steps[0][1].get("analysis", "")
            return AgentAction(
                tool="classify_persona",
                tool_input={
                    "text": text,
                    "analysis": analysis
                },
                log="Classifying target persona based on analysis"
            )
        
        # Finish after persona classification
        return AgentFinish(
            return_values={"persona": intermediate_steps[-1][1]["persona"]},
            log=f"Persona detection completed: {intermediate_steps[-1][1]['explanation']}"
        )

    def process(self, content):
        """
        Analyze content and determine the target persona
        Args:
            content (str): The website content to analyze
        Returns:
            dict: Contains persona type, confidence score, and reasoning
        """
        print(f"[PersonaDetectionAgent] Input: content={content[:60]}...")
        messages = self._create_messages(
            self.system_prompt,
            f"Analyze this content and determine the target audience:\n\n{content}"
        )
        try:
            result = self.llm.invoke(messages)
            print(f"[PersonaDetectionAgent] Output: {result.dict()}")
            return result.dict()
        except Exception as e:
            fallback = {
                "persona": "professional",  # default to professional if parsing fails
                "confidence": 0.5,
                "reasoning": f"Failed to parse LLM response: {str(e)}"
            }
            print(f"[PersonaDetectionAgent] Fallback Output: {fallback}")
            return fallback 