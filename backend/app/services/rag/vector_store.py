from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

PERSIST_DIRECTORY = "chroma_db"

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

vector_store = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embedding_model
)


def get_vector_store():
    return vector_store