from .base_agent import BaseAgent
from langchain.agents import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import AgentAction, AgentFinish
from typing import List, Tuple, Dict, Any, Union

class ContentRefinementAgent(BaseAgent):
    def __init__(self, model_name="models/gemini-1.5-flash", temperature=0.7):
        super().__init__(model_name, temperature)
        
        # Initialize chains
        self.style_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["content"],
                template="""Analyze the writing style of the following content and identify key style elements:
                Content: {content}
                Key style elements to identify:
                - Tone and voice
                - Vocabulary level
                - Sentence structure
                - Rhetorical devices used
                """
            )
        )
        
        self.content_rewrite_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["content", "persona", "style_examples"],
                template="""You are an expert content writer specializing in writing for {persona} audiences.
                Your task is to rewrite the given content to match the style and tone appropriate for the target audience.
                Use these style examples as inspiration:
                {style_examples}
                
                Content to rewrite:
                {content}
                """
            )
        )
    
    def _get_tools(self) -> List[Tool]:
        """Define tools available to this agent"""
        return [
            Tool(
                name="analyze_style",
                func=self._analyze_style,
                description="Analyzes the writing style of given content"
            ),
            Tool(
                name="rewrite_content",
                func=self._rewrite_content,
                description="Rewrites content for a specific persona using style examples"
            )
        ]
    
    def _analyze_style(self, content: str) -> Dict[str, Any]:
        """Tool function to analyze content style"""
        result = self.style_analysis_chain.run(content=content)
        return {"style_analysis": result}
    
    def _rewrite_content(self, content: str, persona: str, style_examples: List[Dict[str, str]]) -> str:
        """Tool function to rewrite content"""
        style_examples_text = "\n".join([
            f"Example {i+1}:\n{ex['content']}\nStyle: {ex['style']}"
            for i, ex in enumerate(style_examples)
        ])
        
        result = self.content_rewrite_chain.run(
            content=content,
            persona=persona,
            style_examples=style_examples_text
        )
        return result
    
    def aplan(self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs) -> Union[AgentAction, AgentFinish]:
        """Plan next action based on current state"""
        content = kwargs.get("content", "")
        persona = kwargs.get("persona", "")
        style_examples = kwargs.get("style_examples", [])
        
        # If no steps taken yet, start with style analysis
        if not intermediate_steps:
            return AgentAction(
                tool="analyze_style",
                tool_input=content,
                log="Analyzing content style first"
            )
            
        # If style analyzed, proceed with content rewrite
        if len(intermediate_steps) == 1:
            return AgentAction(
                tool="rewrite_content",
                tool_input={
                    "content": content,
                    "persona": persona,
                    "style_examples": style_examples
                },
                log="Rewriting content based on style analysis and examples"
            )
            
        # Finish after content rewrite
        return AgentFinish(
            return_values={"output": intermediate_steps[-1][1]},
            log="Content refinement completed"
        )

    def process(self, content, persona, style_examples):
        """
        Rewrite content to match the target persona and style
        Args:
            content (str): Original content to rewrite
            persona (str): Target persona ('genz' or 'professional')
            style_examples (list): Retrieved style examples to base the rewrite on
        Returns:
            str: Rewritten content
        """
        print(f"[ContentRefinementAgent] Input: content={content[:60]}..., persona={persona}, style_examples={style_examples}")
        # Create a detailed prompt using style examples
        style_examples_text = "\n".join([
            f"Style Example {idx+1}:\n"
            f"Content: {ex['content']}\n"
            f"Style: {ex['style']}"
            for idx, ex in enumerate(style_examples)
        ])
        
        system_prompt = f"""You are an expert content writer specializing in writing for {'Generation Z' if persona == 'genz' else 'Professional'} audiences.
        Your task is to rewrite the given content to match the style and tone appropriate for the target audience.
        Use the provided style examples as inspiration for the tone, vocabulary, and writing style.
        
        For Generation Z, focus on:
        - Casual, conversational tone
        - Modern slang and emoji usage
        - Short, punchy sentences
        - Engaging and relatable language
        
        For Professionals, focus on:
        - Formal, business-appropriate tone
        - Industry-standard terminology
        - Clear, concise communication
        - Data-driven and solution-focused language
        
        Here are some style examples to guide you:
        {style_examples_text}
        
        Maintain the same key information and message, but adapt the style completely."""
        
        user_prompt = f"Please rewrite this content:\n\n{content}"
        
        messages = self._create_messages(system_prompt, user_prompt)
        response = self.llm.invoke(messages)
        print(f"[ContentRefinementAgent] Output: {response.content[:200]}...")
        return response.content 