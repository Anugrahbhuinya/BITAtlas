import os
import logging
import threading
from pathlib import Path

# Prevent HuggingFace tokenizer parallelism warnings / thread issues
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logger = logging.getLogger("rag_vector_store")

# Resolve base directories safely across Windows, Linux, and Docker
BASE_DIR = Path(__file__).resolve().parents[4]

def get_persist_directory() -> str:
    candidates = [
        BASE_DIR / "chroma_db",
        BASE_DIR / "backend" / "chroma_db",
        Path("/app/chroma_db"),
        Path("/chroma_db"),
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return str(candidate)
    return str(BASE_DIR / "chroma_db")

PERSIST_DIRECTORY = get_persist_directory()

_embedding_model = None
_vector_store = None
_lock = threading.Lock()


def get_embedding_model():
    """
    Lazy singleton loader for HuggingFaceEmbeddings.
    Loads the BAAI/bge-small-en-v1.5 model on CPU only when first requested.
    """
    global _embedding_model
    if _embedding_model is None:
        with _lock:
            if _embedding_model is None:
                logger.info("Initializing HuggingFaceEmbeddings lazily (BAAI/bge-small-en-v1.5 on CPU)...")
                from langchain_huggingface import HuggingFaceEmbeddings
                _embedding_model = HuggingFaceEmbeddings(
                    model_name="BAAI/bge-small-en-v1.5",
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True}
                )
                logger.info("RAG embeddings initialized lazily")
    return _embedding_model


def get_vector_store():
    """
    Lazy singleton loader for Chroma vector database connection.
    Connects to the persistent directory using the lazy embedding model.
    """
    global _vector_store
    if _vector_store is None:
        with _lock:
            if _vector_store is None:
                from langchain_chroma import Chroma
                persist_dir = get_persist_directory()
                embedding_fn = get_embedding_model()
                logger.info(f"Initializing Chroma vector store connection at {persist_dir}...")
                _vector_store = Chroma(
                    persist_directory=persist_dir,
                    embedding_function=embedding_fn
                )
                logger.info("Vector database connection ready")
    return _vector_store