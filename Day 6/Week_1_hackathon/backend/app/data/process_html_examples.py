"""
Script to process landing page HTML examples and populate the vector store.
Specifically designed to extract and process content from landing pages for different personas.
"""

import os
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple
import asyncio

class LandingPageProcessor:
    def __init__(self):
        # Define important landing page elements to extract
        self.landing_page_elements = {
            "hero": {
                "selectors": [".hero", "header", "#hero"],
                "importance": "high"
            },
            "value_prop": {
                "selectors": [".value-proposition", ".benefits", ".features"],
                "importance": "high"
            },
            "cta": {
                "selectors": ["button", ".cta", ".btn", "a.button"],
                "importance": "high"
            },
            "features": {
                "selectors": [".features", ".services", ".offerings"],
                "importance": "medium"
            },
            "social_proof": {
                "selectors": [".testimonials", ".reviews", ".case-studies"],
                "importance": "medium"
            }
        }

    def extract_content_from_html(self, html_file: Path) -> List[Tuple[str, Dict]]:
        """
        Extract content from landing page HTML file with specific focus on landing page elements.
        Returns list of (content, metadata) tuples.
        """
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        extracted_content = []
        
        # Get page title
        title = soup.title.string if soup.title else ""
        
        # Process each landing page element type
        for element_type, config in self.landing_page_elements.items():
            # Find sections matching any of the selectors
            for selector in config["selectors"]:
                elements = soup.select(selector)
                
                for element in elements:
                    content_parts = []
                    
                    # Extract headings
                    headings = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    for heading in headings:
                        content_parts.append(f"Heading: {heading.text.strip()}")
                    
                    # Extract paragraphs
                    paragraphs = element.find_all('p')
                    for p in paragraphs:
                        content_parts.append(f"Content: {p.text.strip()}")
                    
                    # Extract lists
                    lists = element.find_all(['ul', 'ol'])
                    for lst in lists:
                        items = [item.text.strip() for item in lst.find_all('li')]
                        content_parts.append(f"List Items:\n" + "\n".join(f"- {item}" for item in items))
                    
                    # Extract CTAs
                    ctas = element.find_all(['button', 'a'])
                    for cta in ctas:
                        if any(c in cta.get('class', []) for c in ['cta', 'btn', 'button']):
                            content_parts.append(f"CTA: {cta.text.strip()}")
                    
                    # Combine all content parts
                    section_content = "\n".join(content_parts).strip()
                    
                    if section_content:
                        metadata = {
                            "page_title": title,
                            "content_type": "landing_page",
                            "element_type": element_type,
                            "importance": config["importance"],
                            "section_class": " ".join(element.get('class', [])),
                        }
                        extracted_content.append((section_content, metadata))
        
        return extracted_content

async def process_landing_pages():
    """Process all landing page examples and populate the vector store."""
    from ..services.vector_store import vector_store
    
    examples_dir = Path(__file__).parent / "html_examples"
    processor = LandingPageProcessor()
    
    for persona_dir in examples_dir.iterdir():
        if persona_dir.is_dir():
            persona = persona_dir.name
            print(f"\nProcessing landing pages for persona: {persona}")
            
            all_content = []
            all_metadata = []
            
            # Process each landing page HTML file
            for html_file in persona_dir.glob("landing_page*.html"):
                print(f"Processing file: {html_file.name}")
                content_chunks = processor.extract_content_from_html(html_file)
                
                for content, metadata in content_chunks:
                    metadata["persona"] = persona
                    all_content.append(content)
                    all_metadata.append(metadata)
            
            # Add to vector store
            if all_content:
                vector_store.add_example_content(
                    texts=all_content,
                    personas=[persona] * len(all_content),
                    metadata=all_metadata
                )
                print(f"Added {len(all_content)} content chunks from landing pages for {persona}")

if __name__ == "__main__":
    asyncio.run(process_landing_pages()) 