from pydantic_settings import BaseSettings
from typing import List, Dict, Any
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Content Rewriter API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Vector DB Settings
    CHROMA_DB_DIR: str = "data/chroma_db"
    
    # Gemini Settings
    MODEL_TEMPERATURE: float = 0.7
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "your_default_google_api_key_here")
    
    # Predefined Personas
    PERSONAS: List[str] = [
        "gen_z",
        "millennials",
        "cxo",
        "technical",
        "creative_professionals",
        "enterprise"
    ]
    
    # Detailed Persona Rules
    PERSONA_RULES: Dict[str, Dict[str, Any]] = {
        "gen_z": {
            "description": "Young, digital native audience aged 10-25. Prefers casual, authentic communication with emojis and modern slang.",
            "tone": {
                "style": "casual, energetic, playful",
                "emotion": "enthusiastic, authentic, relatable",
                "formality": "very informal"
            },
            "vocabulary": {
                "level": "simple to moderate",
                "preferences": ["modern slang", "emojis", "abbreviations"],
                "avoid": ["corporate jargon", "complex terminology", "formal language"]
            },
            "content_structure": {
                "length": "short, bite-sized",
                "format": ["bullet points", "short paragraphs", "visual breaks"],
                "engagement": ["questions", "calls to action", "interactive elements"]
            },
            "examples": {
                "cta": ["Get started 🚀", "Join the fun! ✨", "Try it now 👉"],
                "greetings": ["Hey there!", "What's up?", "Hey fam!"],
                "transitions": ["BTW", "NGL", "FR"]
            }
        },
        "cxo": {
            "description": "C-level executives and decision makers. Focuses on ROI, strategic value, and business impact.",
            "tone": {
                "style": "professional, authoritative, strategic",
                "emotion": "confident, measured, insightful",
                "formality": "formal"
            },
            "vocabulary": {
                "level": "advanced",
                "preferences": ["business terminology", "industry-specific terms", "metrics"],
                "avoid": ["slang", "casual expressions", "ambiguous terms"]
            },
            "content_structure": {
                "length": "concise but comprehensive",
                "format": ["executive summaries", "clear sections", "data-driven points"],
                "engagement": ["ROI statements", "strategic implications", "market context"]
            },
            "examples": {
                "cta": ["Schedule a Strategic Review", "Access Executive Brief", "Explore Enterprise Solutions"],
                "greetings": ["Dear [Title] [Name]", "Greetings", "Dear Executive Team"],
                "transitions": ["Furthermore", "Moreover", "Consequently"]
            }
        },
        "technical": {
            "description": "Engineers, developers, and technical professionals. Appreciates detailed specifications and technical accuracy.",
            "tone": {
                "style": "precise, technical, detailed",
                "emotion": "logical, analytical, objective",
                "formality": "semi-formal"
            },
            "vocabulary": {
                "level": "technical",
                "preferences": ["technical terms", "specifications", "code examples"],
                "avoid": ["marketing fluff", "vague descriptions", "non-technical analogies"]
            },
            "content_structure": {
                "length": "detailed",
                "format": ["technical documentation", "code blocks", "step-by-step guides"],
                "engagement": ["implementation examples", "technical specifications", "architecture diagrams"]
            },
            "examples": {
                "cta": ["View Documentation", "Clone Repository", "See Technical Specs"],
                "greetings": ["Hello", "Hi team", "Greetings developers"],
                "transitions": ["Additionally", "Specifically", "For example"]
            }
        }
        # Add other personas with similar detailed rules
    }

    class Config:
        case_sensitive = True

settings = Settings()

# Ensure ChromaDB directory exists
os.makedirs(Path(settings.CHROMA_DB_DIR), exist_ok=True)
