from typing import List, Tuple
import os, json, glob
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document

# Directory to persist Chroma DB
_EMBED_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

# Singleton store instance
_store: Chroma | None = None

# Lazy init embeddings
def _get_embeddings():
    return OpenAIEmbeddings()


def _load_kb_files(pattern_dir: str) -> Tuple[List[str], List[dict]]:
    """Scan pattern JSON files and return (texts, metadata)."""
    texts, metas = [], []
    for fp in glob.glob(os.path.join(pattern_dir, "*.json")):
        with open(fp, "r", encoding="utf-8") as f:
            meta = json.load(f)
        text = f"{meta.get('name','')} : {meta.get('description','')}"
        texts.append(text)
        metas.append(meta)
    return texts, metas


def build_store(pattern_dir: str = os.path.join(os.path.dirname(__file__), "pattern_kb")) -> None:
    """One-time build of the Chroma vector DB from pattern JSON files."""
    texts, metas = _load_kb_files(pattern_dir)
    if not texts:
        raise ValueError("No pattern JSON files found in pattern_kb directory.")

    Chroma.from_texts(
        texts=texts,
        embedding=_get_embeddings(),
        metadatas=metas,
        persist_directory=_EMBED_DIR,
    ).persist()
    print(f"Vector store built with {len(texts)} documents → {_EMBED_DIR}")


def get_store() -> Chroma:
    """Return (and cache) a Chroma store instance, building if missing."""
    global _store
    if _store is None:
        if not os.path.exists(_EMBED_DIR):
            raise RuntimeError(
                "Chroma store not found. Run `python -m ai.vector_store` to build it "
                "after adding pattern JSON files to ai/pattern_kb/."
            )
        _store = Chroma(persist_directory=_EMBED_DIR, embedding_function=_get_embeddings())
    return _store


if __name__ == "__main__":
    # Allow `python -m ai.vector_store` to build the DB quickly
    build_store() 