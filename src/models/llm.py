from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from config.settings import settings

def get_llm(provider: str = "groq"):
    """
    Groq ya OpenAI ka LLM instance initialize karta hai.
    """
    if provider == "groq" and settings.GROQ_API_KEY:
        return ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name="openai/gpt-oss-120b",  # Active model from your Groq list
            temperature=0.2,
            max_tokens=250
        )
    elif settings.OPENAI_API_KEY:
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model_name="gpt-4o-mini",
            temperature=0.2,
            max_tokens=250
        )
    else:
        raise ValueError("Koi valid API Key nahi mili. Kripya .env me GROQ_API_KEY set karein.")