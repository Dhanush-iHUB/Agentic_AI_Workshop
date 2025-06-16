from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from .core.config import settings
from .services.content_processor import content_processor
from .services.vector_store import vector_store
from .services.html_transformer import html_transformer
from typing import Dict, List
import uvicorn

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Content Rewriter API is running"}

@app.get("/personas")
async def get_personas():
    """Get list of available personas"""
    return {
        "personas": settings.PERSONAS,
        "descriptions": settings.PERSONA_RULES
    }

@app.post("/analyze")
async def analyze_content(
    file: UploadFile,
    persona: str = Form(...),
    return_type: str = Form("json")  # Can be 'json' or 'html'
):
    """
    Analyze and adapt content for specific persona.
    Returns either JSON with analysis or transformed HTML.
    """
    if persona not in settings.PERSONAS:
        raise HTTPException(status_code=400, detail=f"Invalid persona. Available personas: {settings.PERSONAS}")
    
    try:
        content = await file.read()
        html_content = content.decode()
        
        # Extract content from HTML
        extracted_content = content_processor.extract_content(html_content)
        
        # Adapt content for persona
        adapted_content = await content_processor.adapt_content_for_persona(extracted_content, persona)
        
        # Generate suggestions
        suggestions = content_processor.generate_suggestions(extracted_content, persona)
        
        if return_type == "html":
            # Transform the HTML with adapted content
            transformed_html = html_transformer.transform_html(html_content, adapted_content)
            return HTMLResponse(content=transformed_html, media_type="text/html")
        else:
            return {
                "original_content": extracted_content,
                "adapted_content": adapted_content,
                "suggestions": suggestions
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train")
async def add_training_examples(examples: Dict[str, List[Dict[str, str]]]):
    """Add example content to the vector store for RAG"""
    try:
        for persona, contents in examples.items():
            texts = [content["text"] for content in contents]
            metadata = [{"persona": persona, **content.get("metadata", {})} for content in contents]
            vector_store.add_example_content(texts, [persona] * len(texts), metadata)
        return {"message": "Training examples added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
