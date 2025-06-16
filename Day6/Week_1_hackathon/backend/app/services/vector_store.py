import chromadb
from chromadb.config import Settings as ChromaSettings
from ..core.config import settings
from typing import List, Dict
import os
from datetime import datetime

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_DIR,
            settings=ChromaSettings(
                allow_reset=True,
                is_persistent=True
            )
        )
        
        # Create collections for different purposes
        self.example_content_collection = self.client.get_or_create_collection(
            name="example_content",
            metadata={"description": "Stores example content for different personas"}
        )
        
        self.processed_content_collection = self.client.get_or_create_collection(
            name="processed_content",
            metadata={"description": "Stores processed website content"}
        )
    
    def add_example_content(self, texts: List[str], personas: List[str], metadata: List[Dict] = None):
        """Add example content to the vector store"""
        if metadata is None:
            metadata = [{"persona": persona} for persona in personas]
            
        self.example_content_collection.add(
            documents=texts,
            metadatas=metadata,
            ids=[f"example_{i}" for i in range(len(texts))]
        )
    
    def query_similar_content(self, query_text: str, persona: str, n_results: int = 5):
        """Query similar content for a specific persona"""
        results = self.example_content_collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where={"persona": persona}
        )
        return results
    
    def store_processed_content(self, content: str, url: str, persona: str):
        """Store processed website content"""
        self.processed_content_collection.add(
            documents=[content],
            metadatas=[{
                "url": url,
                "persona": persona,
                "timestamp": str(datetime.now())
            }],
            ids=[f"content_{url}_{persona}"]
        )

vector_store = VectorStore() 