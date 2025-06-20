from .base_agent import BaseAgent
from langchain.agents import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import AgentAction, AgentFinish
from typing import List, Tuple, Dict, Any, Union

class CTAOptimizationAgent(BaseAgent):
    def __init__(self, model_name="models/gemini-1.5-flash", temperature=0.7):
        super().__init__(model_name, temperature)
        
        # Initialize chains
        self.context_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["content"],
                template="""Analyze the following content to understand the context and value proposition:
                Content: {content}
                
                Consider:
                - Main value proposition
                - User pain points addressed
                - Key benefits offered
                - Target audience needs
                - Desired user action
                """
            )
        )
        
        self.cta_generation_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["context_analysis", "current_cta", "persona"],
                template="""Based on the context analysis and target persona, optimize the CTA:
                
                Context Analysis: {context_analysis}
                Current CTA: {current_cta}
                Target Persona: {persona}
                
                For Generation Z CTAs:
                - Use casual, engaging language
                - Keep it short and punchy
                - Include modern phrases
                - Consider emoji usage
                
                For Professional CTAs:
                - Use clear, action-oriented language
                - Focus on value proposition
                - Maintain professional tone
                - Emphasize benefits
                
                Generate:
                1. Primary CTA (main button/link text)
                2. Secondary CTA (alternative option)
                3. Microcopy (supporting text)
                """
            )
        )
        
        self.ab_testing_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["cta_variants", "persona"],
                template="""Analyze these CTA variants for {persona} audience:
                {cta_variants}
                
                For each variant:
                1. Rate effectiveness (1-10)
                2. Explain strengths/weaknesses
                3. Suggest A/B testing metrics
                """
            )
        )
    
    def _get_tools(self) -> List[Tool]:
        """Define tools available to this agent"""
        return [
            Tool(
                name="analyze_context",
                func=self._analyze_context,
                description="Analyzes content context for CTA optimization"
            ),
            Tool(
                name="generate_cta_variants",
                func=self._generate_cta_variants,
                description="Generates optimized CTA variants"
            ),
            Tool(
                name="analyze_variants",
                func=self._analyze_variants,
                description="Analyzes and rates CTA variants"
            )
        ]
    
    def _analyze_context(self, content: str) -> Dict[str, str]:
        """Tool function to analyze content context"""
        result = self.context_analysis_chain.run(content=content)
        return {"context_analysis": result}
    
    def _generate_cta_variants(self, context_analysis: str, current_cta: str, persona: str) -> Dict[str, Any]:
        """Tool function to generate CTA variants"""
        result = self.cta_generation_chain.run(
            context_analysis=context_analysis,
            current_cta=current_cta,
            persona=persona
        )
        
        # Parse the results into structured format
        lines = result.strip().split('\n')
        variants = {
            "primary_cta": lines[0].replace("1. Primary CTA:", "").strip(),
            "secondary_cta": lines[1].replace("2. Secondary CTA:", "").strip(),
            "microcopy": lines[2].replace("3. Microcopy:", "").strip()
        }
        
        return variants
    
    def _analyze_variants(self, variants: Dict[str, str], persona: str) -> Dict[str, Any]:
        """Tool function to analyze CTA variants"""
        variants_str = "\n".join([
            f"{k}: {v}"
            for k, v in variants.items()
        ])
        
        result = self.ab_testing_chain.run(
            cta_variants=variants_str,
            persona=persona
        )
        
        return {
            "variants": variants,
            "analysis": result
        }
    
    def aplan(self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs) -> Union[AgentAction, AgentFinish]:
        """Plan next action based on current state"""
        content = kwargs.get("content", "")
        current_cta = kwargs.get("current_cta", "")
        persona = kwargs.get("persona", "")
        
        # If no steps taken yet, start with context analysis
        if not intermediate_steps:
            return AgentAction(
                tool="analyze_context",
                tool_input=content,
                log="Analyzing content context for CTA optimization"
            )
        
        # If context analyzed, generate CTA variants
        if len(intermediate_steps) == 1:
            context_analysis = intermediate_steps[0][1].get("context_analysis", "")
            return AgentAction(
                tool="generate_cta_variants",
                tool_input={
                    "context_analysis": context_analysis,
                    "current_cta": current_cta,
                    "persona": persona
                },
                log="Generating optimized CTA variants"
            )
        
        # If variants generated, analyze them
        if len(intermediate_steps) == 2:
            variants = intermediate_steps[1][1]
            return AgentAction(
                tool="analyze_variants",
                tool_input={
                    "variants": variants,
                    "persona": persona
                },
                log="Analyzing and rating CTA variants"
            )
        
        # Finish after variant analysis
        final_result = intermediate_steps[-1][1]
        return AgentFinish(
            return_values={
                "primary_cta": final_result["variants"]["primary_cta"],
                "secondary_cta": final_result["variants"]["secondary_cta"],
                "microcopy": final_result["variants"]["microcopy"],
                "analysis": final_result["analysis"]
            },
            log="CTA optimization completed with variants and analysis"
        ) 