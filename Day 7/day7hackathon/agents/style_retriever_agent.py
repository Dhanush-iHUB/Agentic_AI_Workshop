from .base_agent import BaseAgent
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from sample_data.style_examples import GENZ_EXAMPLES, PROFESSIONAL_EXAMPLES

class StyleRetrieverAgent(BaseAgent):
    def __init__(self, model_name="gemini-1.5-flash", temperature=0.7):
        super().__init__(model_name, temperature)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self._initialize_vector_stores()
        
    def _initialize_vector_stores(self):
        """Initialize separate vector stores for each persona"""
        # Prepare documents for Gen Z
        genz_texts = [ex["content"] for ex in GENZ_EXAMPLES]
        self.genz_store = FAISS.from_texts(
            genz_texts,
            self.embeddings,
            metadatas=[{"style": ex["style"], "type": ex["type"]} for ex in GENZ_EXAMPLES]
        )
        
        # Prepare documents for Professionals
        prof_texts = [ex["content"] for ex in PROFESSIONAL_EXAMPLES]
        self.prof_store = FAISS.from_texts(
            prof_texts,
            self.embeddings,
            metadatas=[{"style": ex["style"], "type": ex["type"]} for ex in PROFESSIONAL_EXAMPLES]
        )
    
    def process(self, content, persona):
        """
        Retrieve relevant style examples based on content and persona
        Args:
            content (str): The content to find style examples for
            persona (str): Either 'genz' or 'professional'
        Returns:
            list: Relevant style examples with their metadata
        """
        store = self.genz_store if persona == "genz" else self.prof_store
        results = store.similarity_search_with_score(content, k=2)
        
        # Format results
        examples = []
        for doc, score in results:
            examples.append({
                "content": doc.page_content,
                "style": doc.metadata["style"],
                "type": doc.metadata["type"],
                "relevance_score": float(score)
            })
            
        return examples 