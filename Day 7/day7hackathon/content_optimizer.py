from bs4 import BeautifulSoup
from agents.persona_detection_agent import PersonaDetectionAgent
from agents.style_retriever_agent import StyleRetrieverAgent
from agents.content_refinement_agent import ContentRefinementAgent
from agents.cta_optimization_agent import CTAOptimizationAgent

class ContentOptimizer:
    def __init__(self):
        self.persona_detector = PersonaDetectionAgent()
        self.style_retriever = StyleRetrieverAgent()
        self.content_refiner = ContentRefinementAgent()
        self.cta_optimizer = CTAOptimizationAgent()
    
    def _extract_text_elements(self, html):
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
    
    def optimize_content(self, html_content, target_persona=None):
        """
        Optimize HTML content for the target persona
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
        
        # Detect persona if not specified
        if not target_persona:
            persona_result = self.persona_detector.process(all_text)
            print(f"[ContentOptimizer] PersonaDetectionAgent output: {persona_result}")
            target_persona = persona_result['persona']
        
        # Get style examples
        style_examples = self.style_retriever.process(all_text, target_persona)
        print(f"[ContentOptimizer] StyleRetrieverAgent output: {style_examples}")
        
        # Process each text element
        for elem in text_elements:
            optimized_content = self.content_refiner.process(
                elem['content'],
                target_persona,
                style_examples
            )
            print(f"[ContentOptimizer] ContentRefinementAgent output: {optimized_content[:200]}...")
            elem['element'].string = optimized_content
        
        # Optimize CTAs
        cta_recommendations = []
        for cta in ctas:
            optimized_cta = self.cta_optimizer.process(
                all_text,
                target_persona,
                cta['content']
            )
            print(f"[ContentOptimizer] CTAOptimizationAgent output: {optimized_cta}")
            cta['element'].string = optimized_cta['primary_cta']
            cta_recommendations.append({
                'original': cta['content'],
                'optimized': optimized_cta
            })
        
        # Prepare optimization report
        report = {
            'target_persona': target_persona,
            'style_examples_used': style_examples,
            'elements_optimized': len(text_elements),
            'ctas_optimized': cta_recommendations
        }
        
        return str(soup), report 