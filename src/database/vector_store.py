import os
from langchain_community.vectorstores import Chroma
from src.models.embeddings import get_embedding_function
from config.settings import settings

class VectorStoreManager:
    def __init__(self):
        # Local HuggingFace embedding function load karna
        self.embeddings = get_embedding_function()
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # ChromaDB vector store collection initialize karna
        self.vector_db = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings,
            collection_name="voice_rag_knowledge"
        )

    def add_documents(self, documents):
        """Document chunks ko vector database me add aur save karta hai."""
        if not documents:
            return
        self.vector_db.add_documents(documents)
        self.vector_db.persist()

    def get_retriever(self, top_k: int = None):
        """LangChain retrieval ke liye retriever object return karta hai."""
        k = top_k or settings.TOP_K
        return self.vector_db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

    def search_similar(self, query: str, top_k: int = None):
        """Query ke against sab se closely matching document chunks dhoondta hai."""
        k = top_k or settings.TOP_K
        return self.vector_db.similarity_search(query, k=k)

    def clear_database(self):
        """Purane vector collection ko delete karke database fresh reset karta hai."""
        self.vector_db.delete_collection()
        self.vector_db = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings,
            collection_name="voice_rag_knowledge"
        )