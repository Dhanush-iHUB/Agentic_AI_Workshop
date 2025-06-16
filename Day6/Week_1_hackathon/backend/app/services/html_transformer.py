"""
Service to transform HTML content based on adapted content while preserving structure and styling.
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Any
import copy

class HTMLTransformer:
    def __init__(self):
        self.landing_page_elements = {
            "hero": [".hero", "header", "#hero"],
            "value_prop": [".value-proposition", ".benefits", ".features"],
            "features": [".features", ".services", ".offerings"],
            "social_proof": [".testimonials", ".reviews", ".case-studies"],
            "cta": ["button", ".cta", ".btn", "a.button"]
        }
    
    def transform_html(self, original_html: str, adapted_content: Dict[str, Any]) -> str:
        """
        Transform the original HTML using the adapted content while preserving
        structure, styling, and non-content elements.
        """
        # Parse original HTML
        soup = BeautifulSoup(original_html, 'html.parser')
        
        # Create a copy to preserve original
        new_soup = copy.copy(soup)
        
        # Update text content while preserving structure
        self._update_text_content(new_soup, adapted_content)
        
        return str(new_soup)
    
    def _update_text_content(self, soup: BeautifulSoup, adapted_content: Dict[str, Any]):
        """Update text content in the HTML while preserving structure."""
        
        # Update headings
        if "headings" in adapted_content:
            for original_heading, new_text in zip(
                soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']),
                adapted_content.get("headings", [])
            ):
                if original_heading and new_text:
                    original_heading.string = new_text
        
        # Update paragraphs
        if "paragraphs" in adapted_content:
            for original_p, new_text in zip(
                soup.find_all('p'),
                adapted_content.get("paragraphs", [])
            ):
                if original_p and new_text:
                    original_p.string = new_text
        
        # Update lists
        if "lists" in adapted_content:
            for original_list, new_items in zip(
                soup.find_all(['ul', 'ol']),
                adapted_content.get("lists", [])
            ):
                if original_list and new_items:
                    # Clear existing items
                    original_list.clear()
                    # Add new items
                    for item in new_items:
                        li = soup.new_tag('li')
                        li.string = item
                        original_list.append(li)
        
        # Update CTAs
        if "cta_buttons" in adapted_content:
            for original_cta, new_text in zip(
                soup.find_all(['button', 'a'], class_=lambda x: x and ('cta' in x or 'btn' in x)),
                adapted_content.get("cta_buttons", [])
            ):
                if original_cta and new_text:
                    original_cta.string = new_text
        
        # Update specific sections if they exist in adapted_content
        for section_type, selectors in self.landing_page_elements.items():
            if section_type in adapted_content:
                for selector in selectors:
                    sections = soup.select(selector)
                    for section in sections:
                        self._update_section_content(
                            section,
                            adapted_content[section_type]
                        )
    
    def _update_section_content(self, section: BeautifulSoup, new_content: Dict[str, Any]):
        """Update content within a specific section."""
        # Update headings in section
        headings = section.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if "heading" in new_content and headings:
            headings[0].string = new_content["heading"]
        
        # Update paragraphs in section
        paragraphs = section.find_all('p')
        if "content" in new_content and paragraphs:
            for p, text in zip(paragraphs, new_content.get("content", [])):
                p.string = text
        
        # Update lists in section
        lists = section.find_all(['ul', 'ol'])
        if "list_items" in new_content and lists:
            for lst, items in zip(lists, new_content.get("list_items", [])):
                lst.clear()
                for item in items:
                    li = section.new_tag('li')
                    li.string = item
                    lst.append(li)
        
        # Update CTAs in section
        ctas = section.find_all(['button', 'a'], class_=lambda x: x and ('cta' in x or 'btn' in x))
        if "cta" in new_content and ctas:
            for cta, text in zip(ctas, new_content.get("cta", [])):
                cta.string = text

html_transformer = HTMLTransformer() 