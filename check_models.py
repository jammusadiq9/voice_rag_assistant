import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
print(f"API Key Found: {'Yes' if groq_api_key else 'No'}")

try:
    client = Groq(api_key=groq_api_key)
    models = client.models.list()
    print("\n--- Available Groq Models on your Account ---")
    for m in models.data:
        print(m.id)
except Exception as e:
    print(f"Error fetching models: {e}")