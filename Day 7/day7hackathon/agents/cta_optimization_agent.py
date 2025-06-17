from .base_agent import BaseAgent
from sample_data.style_examples import CTA_EXAMPLES
import json

class CTAOptimizationAgent(BaseAgent):
    def __init__(self, model_name="gemini-1.5-flash", temperature=0.7):
        super().__init__(model_name, temperature)
        self.cta_examples = CTA_EXAMPLES
    
    def process(self, content, persona, original_cta=None):
        """
        Optimize CTAs for the target persona
        Args:
            content (str): The surrounding content for context
            persona (str): Target persona ('genz' or 'professional')
            original_cta (str, optional): The original CTA text if available
        Returns:
            dict: Optimized CTA suggestions and placement recommendations
        """
        example_ctas = self.cta_examples[persona]
        
        system_prompt = f"""You are an expert in optimizing call-to-action (CTA) elements for {'Generation Z' if persona == 'genz' else 'Professional'} audiences.
        Your task is to suggest appropriate CTA text and placement recommendations based on the content and target audience.
        
        Here are some example CTAs for this audience:
        {', '.join(example_ctas)}
        
        Return your suggestions in JSON format with the following structure:
        {{
            "primary_cta": "suggested primary CTA text",
            "alternative_ctas": ["2-3 alternative CTA suggestions"],
            "placement_recommendation": "where to place the CTA",
            "styling_tips": "brief styling recommendations"
        }}"""
        
        context = f"Content: {content}\n"
        if original_cta:
            context += f"Original CTA: {original_cta}\n"
        
        messages = self._create_messages(system_prompt, context)
        response = self.llm.invoke(messages)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "primary_cta": example_ctas[0],
                "alternative_ctas": example_ctas[1:3],
                "placement_recommendation": "Prominently display above the fold",
                "styling_tips": "Use high-contrast colors and clear typography"
            } 