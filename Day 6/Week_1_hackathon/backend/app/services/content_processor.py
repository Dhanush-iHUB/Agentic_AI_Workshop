from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from ..core.config import settings
from .vector_store import vector_store
from .content_agent import content_agent
import re

class ContentProcessor:
    def __init__(self):
        self.persona_style_guide = {
            "gen_z": {
                "tone": "casual and friendly",
                "vocabulary": "simple, modern slang",
                "cta_style": "direct, emoji-friendly",
                "layout": "visual-heavy, mobile-first"
            },
            "cxo": {
                "tone": "professional and authoritative",
                "vocabulary": "business-oriented, strategic",
                "cta_style": "value-proposition focused",
                "layout": "clean, data-driven"
            },
            # Add other personas here
        }
    
    def extract_content(self, html_content: str) -> Dict[str, List[str]]:
        """Extract different content elements from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        return {
            "headings": [h.text.strip() for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])],
            "paragraphs": [p.text.strip() for p in soup.find_all('p')],
            "cta_buttons": [button.text.strip() for button in soup.find_all(['button', 'a'], class_=re.compile(r'btn|button|cta'))],
            "lists": [ul.text.strip() for ul in soup.find_all(['ul', 'ol'])]
        }
    
    async def adapt_content_for_persona(self, content: Dict[str, List[str]], persona: str) -> Dict[str, List[str]]:
        """Adapt content for specific persona using RAG and LangChain agent"""
        adapted_content = {}
        
        for content_type, texts in content.items():
            adapted_texts = []
            for text in texts:
                # Use the content agent to rewrite each piece of content
                result = await content_agent.rewrite_content(text, persona)
                adapted_texts.append(result["rewritten_content"])
            
            adapted_content[content_type] = adapted_texts
        
        return adapted_content
    
    def generate_suggestions(self, content: Dict[str, List[str]], persona: str) -> Dict[str, str]:
        """Generate suggestions for content improvements"""
        style = self.persona_style_guide.get(persona, self.persona_style_guide["gen_z"])
        
        return {
            "tone_suggestions": f"Adapt tone to be more {style['tone']}",
            "vocabulary_suggestions": f"Use {style['vocabulary']} vocabulary",
            "cta_suggestions": f"Make CTAs more {style['cta_style']}",
            "layout_suggestions": f"Consider {style['layout']} layout"
        }

content_processor = ContentProcessor() 