# Content Rewriter API Backend

## Overview
This backend is a FastAPI-based service for analyzing and rewriting website content for different audience personas. It leverages Google Gemini (via LangChain), ChromaDB for vector storage, and provides endpoints for content adaptation, persona management, and training with new examples.

## Features
- **Persona-based Content Rewriting:** Adapts website content for various personas (e.g., Gen Z, CXO, Technical, etc.).
- **HTML Content Extraction & Transformation:** Extracts, analyzes, and rewrites HTML content while preserving structure.
- **Retrieval-Augmented Generation (RAG):** Uses example content and persona rules to improve adaptation.
- **Vector Store:** Stores and queries example and processed content using ChromaDB.
- **API Endpoints:** Upload HTML, select persona, and receive adapted content or suggestions.

## Directory Structure
```
backend/
├── app/
│   ├── api/                # (API routers, currently placeholder)
│   ├── core/               # Configuration and settings
│   ├── services/           # Content processing, vector store, agents, transformers
│   ├── main.py             # FastAPI entrypoint
│
├── data/
│   └── chroma_db/          # ChromaDB vector database files
│
├── requirements.txt        # Python dependencies
├── simple_test.html        # Example HTML input
├── test.html               # Example HTML input
```

## Setup Instructions
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set up environment variables:**
   - Create a `.env` file in `backend/app/` or set `GOOGLE_API_KEY` in your environment.
   - Example `.env`:
     ```env
     GOOGLE_API_KEY=your_google_api_key_here
     ```
3. **Run the API server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints
- `GET /` — Health check.
- `GET /personas` — List available personas and their rules.
- `POST /analyze` — Upload HTML file, select persona, and get adapted content (JSON or HTML).
- `POST /train` — Add new example content for RAG training.

## Personas
Supported personas (see `app/core/config.py` for details):
- Gen Z
- Millennials
- CXO
- Technical
- Creative Professionals
- Enterprise

Each persona has detailed rules for tone, vocabulary, structure, and examples.

## Example Usage
- Upload `simple_test.html` or `test.html` via `/analyze` endpoint to see persona-based adaptation.

## Dependencies
Key packages:
- fastapi, uvicorn
- chromadb
- beautifulsoup4
- langchain, langchain-chroma, langchain-google-genai
- python-dotenv, pydantic, pydantic-settings

See `requirements.txt` for the full list.

## Notes
- The backend expects a valid Google API key for Gemini models.
- ChromaDB files are stored in `data/chroma_db/`.
- Some service files (e.g., `embedder.py`, `rag_engine.py`, `api/endpoints.py`) are placeholders for future expansion. 