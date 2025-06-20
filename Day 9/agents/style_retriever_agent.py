from .base_agent import BaseAgent
from langchain.agents import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import AgentAction, AgentFinish
from langchain.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from typing import List, Tuple, Dict, Any, Union
import json
import os
import chromadb

class StyleRetrieverAgent(BaseAgent):
    def __init__(self, model_name="models/gemini-1.5-flash", temperature=0.7):
        super().__init__(model_name, temperature)
        
        # Initialize embeddings and vector store
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vector_store = None
        self.collection_name = "style_examples"
        self._initialize_vector_store()
        
        # Initialize chains
        self.style_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["text"],
                template="""Analyze the following text and identify its key stylistic elements:
                Text: {text}
                
                Consider:
                - Writing style (formal/informal)
                - Tone of voice
                - Language patterns
                - Rhetorical devices
                - Vocabulary level
                """
            )
        )
        
        self.style_matching_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["style_analysis", "retrieved_examples", "persona"],
                template="""Based on the style analysis and target persona, select the most relevant style examples:
                
                Style Analysis: {style_analysis}
                Target Persona: {persona}
                Retrieved Examples: {retrieved_examples}
                
                Select 2-3 most relevant examples that best match the target persona and explain why each was chosen.
                """
            )
        )
    
    def _initialize_vector_store(self):
        """Initialize ChromaDB vector store with style examples"""
        from sample_data.style_examples import STYLE_EXAMPLES
        
        # Create persistent directory for ChromaDB
        persist_directory = "chroma_db"
        if not os.path.exists(persist_directory):
            os.makedirs(persist_directory)
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(path=persist_directory)
        
        # Create or get collection
        try:
            collection = client.get_collection(name=self.collection_name)
            print(f"Found existing collection: {self.collection_name}")
        except ValueError:
            print(f"Creating new collection: {self.collection_name}")
            collection = client.create_collection(name=self.collection_name)
        
        # Convert examples to documents format
        texts = []
        metadatas = []
        ids = []
        
        for idx, example in enumerate(STYLE_EXAMPLES):
            texts.append(example["content"])
            metadatas.append({
                "style": example["style"],
                "persona": example["persona"],
                "type": example["type"]
            })
            ids.append(f"example_{idx}")
        
        # Create vector store
        self.vector_store = Chroma(
            client=client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )
        
        # Add documents if collection is empty
        if len(collection.get()["ids"]) == 0:
            self.vector_store.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Added {len(texts)} examples to ChromaDB collection")
    
    def _get_tools(self) -> List[Tool]:
        """Define tools available to this agent"""
        return [
            Tool(
                name="analyze_style",
                func=self._analyze_style,
                description="Analyzes text to identify key stylistic elements"
            ),
            Tool(
                name="retrieve_examples",
                func=self._retrieve_examples,
                description="Retrieves relevant style examples from the vector store"
            ),
            Tool(
                name="match_examples",
                func=self._match_examples,
                description="Matches and ranks style examples based on analysis and persona"
            )
        ]
    
    def _analyze_style(self, text: str) -> Dict[str, str]:
        """Tool function to analyze text style"""
        result = self.style_analysis_chain.run(text=text)
        return {"style_analysis": result}
    
    def _retrieve_examples(self, persona: str) -> List[Dict[str, Any]]:
        """Tool function to retrieve relevant examples from vector store"""
        results = self.vector_store.similarity_search_with_metadata(
            persona,
            k=5,
            filter={"persona": persona}
        )
        
        examples = []
        for doc in results:
            examples.append({
                "content": doc.page_content,
                "style": doc.metadata["style"],
                "persona": doc.metadata["persona"],
                "type": doc.metadata["type"]
            })
        
        return examples
    
    def _match_examples(self, style_analysis: str, examples: List[Dict[str, Any]], persona: str) -> Dict[str, Any]:
        """Tool function to match and rank style examples"""
        examples_str = json.dumps(examples, indent=2)
        result = self.style_matching_chain.run(
            style_analysis=style_analysis,
            retrieved_examples=examples_str,
            persona=persona
        )
        
        return {
            "matched_examples": examples[:3],  # Take top 3 examples
            "matching_explanation": result
        }
    
    def aplan(self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs) -> Union[AgentAction, AgentFinish]:
        """Plan next action based on current state"""
        text = kwargs.get("text", "")
        persona = kwargs.get("persona", "")
        
        # If no steps taken yet, start with style analysis
        if not intermediate_steps:
            return AgentAction(
                tool="analyze_style",
                tool_input=text,
                log="Analyzing text style"
            )
        
        # If style analyzed, retrieve examples
        if len(intermediate_steps) == 1:
            return AgentAction(
                tool="retrieve_examples",
                tool_input=persona,
                log="Retrieving style examples for persona"
            )
        
        # If examples retrieved, match them
        if len(intermediate_steps) == 2:
            style_analysis = intermediate_steps[0][1].get("style_analysis", "")
            examples = intermediate_steps[1][1]
            return AgentAction(
                tool="match_examples",
                tool_input={
                    "style_analysis": style_analysis,
                    "examples": examples,
                    "persona": persona
                },
                log="Matching and ranking style examples"
            )
        
        # Finish after matching examples
        return AgentFinish(
            return_values={"style_examples": intermediate_steps[-1][1]["matched_examples"]},
            log=f"Style examples retrieved and matched: {intermediate_steps[-1][1]['matching_explanation']}"
        ) 