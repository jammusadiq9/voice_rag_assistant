import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from config.settings import settings

def get_llm(provider: str = "groq", model_name: str = None):
    # Direct settings attribute se key fetch karein
    groq_api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    openai_api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")

    # Extra fallback: Direct streamlit secrets check
    if not groq_api_key:
        try:
            import streamlit as st
            if "GROQ_API_KEY" in st.secrets:
                groq_api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass

    if provider.lower() == "groq":
        if not groq_api_key:
            raise ValueError("Koi valid API Key nahi mili. Kripya GROQ_API_KEY set karein.")
        
        target_model = model_name or "llama-3.3-70b-versatile"
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