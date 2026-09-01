from langchain_community.embeddings import HuggingFaceEmbeddings
from config.settings import settings

def get_embedding_function():
    """Sentence-Transformers embedding model initialize karta hai."""
    embedding_model = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    return embedding_model