from bs4 import BeautifulSoup
from agents.persona_detection_agent import PersonaDetectionAgent
from agents.style_retriever_agent import StyleRetrieverAgent
from agents.content_refinement_agent import ContentRefinementAgent
from agents.cta_optimization_agent import CTAOptimizationAgent
from langchain.chains import SequentialChain, LLMChain
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from typing import Dict, List, Any

class ContentOptimizer:
    def __init__(self):
        # Initialize agents with executors
        self.persona_detector = PersonaDetectionAgent()
        self.persona_executor = AgentExecutor.from_agent_and_tools(
            agent=self.persona_detector,
            tools=self.persona_detector.tools,
            memory=self.persona_detector.memory,
            verbose=True
        )
        
        self.style_retriever = StyleRetrieverAgent()
        self.style_executor = AgentExecutor.from_agent_and_tools(
            agent=self.style_retriever,
            tools=self.style_retriever.tools,
            memory=self.style_retriever.memory,
            verbose=True
        )
        
        self.content_refiner = ContentRefinementAgent()
        self.refiner_executor = AgentExecutor.from_agent_and_tools(
            agent=self.content_refiner,
            tools=self.content_refiner.tools,
            memory=self.content_refiner.memory,
            verbose=True
        )
        
        self.cta_optimizer = CTAOptimizationAgent()
        self.cta_executor = AgentExecutor.from_agent_and_tools(
            agent=self.cta_optimizer,
            tools=self.cta_optimizer.tools,
            memory=self.cta_optimizer.memory,
            verbose=True
        )
        
        # Initialize shared memory
        self.memory = ConversationBufferMemory(
            memory_key="optimization_history",
            return_messages=True
        )
    
    def _extract_text_elements(self, html: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Extract text content and CTAs from HTML"""
        soup = BeautifulSoup(html, 'html5lib')
        
        # Extract main content elements
        text_elements = []
        for tag in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'span', 'div']:
            elements = soup.find_all(tag)
            for elem in elements:
                if elem.text.strip():
                    text_elements.append({
                        'tag': tag,
                        'content': elem.text.strip(),
                        'element': elem
                    })
        
        # Extract CTAs (buttons and links)
        ctas = []
        for elem in soup.find_all(['a', 'button']):
            if elem.text.strip():
                ctas.append({
                    'tag': elem.name,
                    'content': elem.text.strip(),
                    'element': elem
                })
        
        return text_elements, ctas
    
    def optimize_content(self, html_content: str, target_persona: str = None) -> tuple[str, Dict[str, Any]]:
        """
        Optimize HTML content for the target persona using LangChain agents and chains
        Args:
            html_content (str): Original HTML content
            target_persona (str, optional): Force a specific persona ('genz' or 'professional')
        Returns:
            tuple: (optimized HTML content, optimization report)
        """
        soup = BeautifulSoup(html_content, 'html5lib')
        text_elements, ctas = self._extract_text_elements(html_content)
        
        # Combine all text for persona detection
        all_text = " ".join([elem['content'] for elem in text_elements])
        
        # Create optimization chain
        if not target_persona:
            # Detect persona using agent
            persona_result = self.persona_executor.run(
                input={"text": all_text}
            )
            target_persona = persona_result['persona']
            
        # Get style examples using agent
        style_result = self.style_executor.run(
            input={
                "text": all_text,
                "persona": target_persona
            }
        )
        style_examples = style_result['style_examples']
        
        # Process each text element using content refinement agent
        for elem in text_elements:
            refinement_result = self.refiner_executor.run(
                input={
                    "content": elem['content'],
                    "persona": target_persona,
                    "style_examples": style_examples
                }
            )
            elem['element'].string = refinement_result['output']
        
        # Optimize CTAs using agent
        cta_recommendations = []
        for cta in ctas:
            cta_result = self.cta_executor.run(
                input={
                    "content": all_text,
                    "persona": target_persona,
                    "current_cta": cta['content']
                }
            )
            cta['element'].string = cta_result['primary_cta']
            cta_recommendations.append({
                'original': cta['content'],
                'optimized': cta_result
            })
        
        # Save optimization history to memory
        self.memory.save_context(
            {"input": all_text},
            {
                "output": {
                    "persona": target_persona,
                    "style_examples": style_examples,
                    "elements_optimized": len(text_elements),
                    "ctas_optimized": len(cta_recommendations)
                }
            }
        )
        
        # Prepare optimization report
        report = {
            'target_persona': target_persona,
            'style_examples_used': style_examples,
            'elements_optimized': len(text_elements),
            'ctas_optimized': cta_recommendations,
            'optimization_history': self.memory.load_memory_variables({})
        }
        
        return str(soup), report 