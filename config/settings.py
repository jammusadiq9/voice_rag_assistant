import os
from dotenv import load_dotenv

load_dotenv()

def get_secret(key: str, default: str = "") -> str:
    """Check both OS environment variables and Streamlit Cloud secrets"""
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default

class Settings:
    GROQ_API_KEY: str = get_secret("GROQ_API_KEY")
    OPENAI_API_KEY: str = get_secret("OPENAI_API_KEY")
    VAPI_API_KEY: str = get_secret("VAPI_API_KEY")
    VAPI_PUBLIC_KEY: str = get_secret("VAPI_PUBLIC_KEY")
    VAPI_ASSISTANT_ID: str = get_secret("VAPI_ASSISTANT_ID")
    CHROMA_PERSIST_DIR: str = get_secret("CHROMA_PERSIST_DIR", "./data/chroma_db")
    EMBEDDING_MODEL: str = get_secret("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Document Chunking Settings (Fixing the missing attributes)
    CHUNK_SIZE: int = int(get_secret("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(get_secret("CHUNK_OVERLAP", "200"))

settings = Settings()