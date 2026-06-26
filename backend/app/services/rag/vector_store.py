import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Define PERSIST_DIRECTORY as an absolute path relative to the backend directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PERSIST_DIRECTORY = os.path.join(BACKEND_DIR, "chroma_db")

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

vector_store = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embedding_model
)


def get_vector_store():
    return vector_store