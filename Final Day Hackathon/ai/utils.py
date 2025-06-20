# ai/utils.py
import os
from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
import logging
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
logger.info("Loading environment variables...")
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logger.warning("No OpenAI API key found in environment variables!")

# Initialize OpenAI LLM
def get_llm():
    logger.info("Initializing OpenAI LLM...")
    if not OPENAI_API_KEY:
        logger.error("Cannot initialize LLM: No API key available")
        raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
    
    try:
        # Initialize ChatOpenAI with GPT-4 Turbo
        logger.info("Initializing ChatOpenAI...")
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=OPENAI_API_KEY
        )
        logger.info("ChatOpenAI initialized successfully")
        return llm
    except Exception as e:
        logger.error(f"ChatOpenAI initialization failed: {str(e)}")
        raise

# LCNC Mapping Schema
LCNC_MAPPING_SCHEMA = {
    "container_blocks": ["div", "section", "article", "main", "aside"],
    "text_blocks": ["h1", "h2", "h3", "h4", "h5", "h6", "p", "span"],
    "input_blocks": ["input", "textarea", "select", "button"],
    "media_blocks": ["img", "video", "audio", "iframe"],
    "list_blocks": ["ul", "ol", "li"],
    "table_blocks": ["table", "tr", "td", "th"],
    "form_blocks": ["form", "fieldset", "legend"],
    "navigation_blocks": ["nav", "a", "menu"]
}

def normalize_to_list(val):
    if isinstance(val, list):
        return val
    elif isinstance(val, dict):
        return [val]
    elif val is None:
        return []
    else:
        return [val]