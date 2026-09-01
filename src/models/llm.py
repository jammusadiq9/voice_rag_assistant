import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from config.settings import settings

def get_llm(provider: str = "groq", model_name: str = None):
    # Fetch key from settings first, then fallback to env
    groq_api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    openai_api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    
    if provider.lower() == "groq":
        if not groq_api_key:
            raise ValueError("Koi valid API Key nahi mili. Kripya GROQ_API_KEY set karein.")
        
        target_model = model_name or "openai/gpt-oss-120b"
        return ChatGroq(
            groq_api_key=groq_api_key,
            model_name=target_model,
            temperature=0.3
        )
    
    elif provider.lower() == "openai":
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY nahi mili.")
        target_model = model_name or "gpt-4o-mini"
        return ChatOpenAI(
            api_key=openai_api_key,
            model=target_model,
            temperature=0.3
        )
    
    else:
        raise ValueError(f"Unsupported provider: {provider}")