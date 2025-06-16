from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from typing import List, Dict
import os
import json
import google.generativeai as genai

from ..core.config import settings
from .vector_store import vector_store

# Set Google API Key
GOOGLE_API_KEY = "AIzaSyCUWiRl0qbvHVA-GafKsncf_UlQrnHaTw0"
genai.configure(api_key=GOOGLE_API_KEY)

class ContentRewriterAgent:
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=settings.MODEL_TEMPERATURE,
            google_api_key=GOOGLE_API_KEY
        )
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
        
        # Create Chroma client from existing ChromaDB
        self.vector_store = Chroma(
            client=vector_store.client,
            embedding_function=self.embeddings,
            collection_name="example_content"
        )
        
        # Define tools
        self.tools = [
            Tool(
                name="Search Similar Content",
                func=self._search_similar_content,
                description="Search for similar content examples based on the persona"
            ),
            Tool(
                name="Get Persona Rules",
                func=self._get_persona_rules,
                description="Get detailed writing rules for a specific persona"
            ),
            Tool(
                name="Analyze Content Structure",
                func=self._analyze_content_structure,
                description="Analyze the structure and components of the content"
            )
        ]

    async def rewrite_content(self, content: str, persona: str) -> Dict[str, str]:
        """Rewrite content for a specific persona"""
        try:
            # Get persona rules
            persona_rules = self._get_persona_rules(persona)
            
            # Analyze content structure
            content_analysis = self._analyze_content_structure(content)
            
            # Create a simpler prompt for direct content rewriting
            rewrite_prompt = f"""You are an expert content rewriter specializing in adapting content for different audience personas.

Current Persona Rules:
{persona_rules}

Original Content:
{content}

Content Analysis:
{content_analysis}

Your task is to rewrite the content while:
1. Maintaining the core message
2. Adapting tone and vocabulary for the persona
3. Restructuring for optimal engagement
4. Adding persona-appropriate examples and analogies

Please provide only the rewritten content without any additional explanations or metadata.

Rewritten content:"""

            # Use LLM directly for rewriting
            response = await self.llm.ainvoke(rewrite_prompt)
            rewritten_content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "rewritten_content": rewritten_content,
                "persona_rules_used": json.loads(persona_rules),
                "content_analysis": content_analysis
            }
            
        except Exception as e:
            print(f"Error in rewrite_content: {str(e)}")
            raise

    def _search_similar_content(self, query: str, persona: str = None) -> List[str]:
        """Search for similar content examples"""
        filter_dict = {"persona": persona} if persona else None
        results = self.vector_store.similarity_search(
            query,
            k=3,
            filter=filter_dict
        )
        return [doc.page_content for doc in results]
    
    def _get_persona_rules(self, persona: str) -> str:
        """Get detailed writing rules for a persona"""
        rules = settings.PERSONA_RULES.get(persona, {})
        return json.dumps(rules, indent=2)
    
    def _analyze_content_structure(self, content: str) -> str:
        """Analyze content structure and components"""
        analysis_prompt = """Analyze the following content and identify its:
1. Main message/purpose
2. Current tone and style
3. Key components (headings, paragraphs, CTAs, etc.)
4. Current engagement techniques
5. Technical or specialized terminology

Content:
{content}

Analysis:"""
        
        # Use LLM directly for analysis
        response = self.llm.invoke(analysis_prompt.format(content=content))
        return response.content if hasattr(response, 'content') else str(response)

content_agent = ContentRewriterAgent() 