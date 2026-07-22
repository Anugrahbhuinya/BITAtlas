import os
import logging
import threading

# Prevent HuggingFace tokenizer parallelism warnings / thread issues
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logger = logging.getLogger("rag_vector_store")

# Define PERSIST_DIRECTORY as an absolute path relative to the backend directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PERSIST_DIRECTORY = os.path.join(BACKEND_DIR, "chroma_db")

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
                embedding_fn = get_embedding_model()
                logger.info(f"Initializing Chroma vector store connection at {PERSIST_DIRECTORY}...")
                _vector_store = Chroma(
                    persist_directory=PERSIST_DIRECTORY,
                    embedding_function=embedding_fn
                )
                logger.info("Vector database connection ready")
    return _vector_store