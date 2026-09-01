from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.database.vector_store import VectorStoreManager
from src.models.llm import get_llm

VOICE_SYSTEM_PROMPT = """You are a knowledgeable, friendly, and concise voice AI assistant.
Answer the user's question using ONLY the provided retrieved context.

Guidelines for Voice Output:
1. Keep the answer natural, short, and conversational (1 to 3 sentences maximum).
2. Do not use markdown symbols, asterisks, bullet points, or tables because your answer will be spoken out loud via Text-to-Speech.
3. If the context does not contain the answer, say: "I don't have that information in my knowledge base."

Context:
{context}

Question:
{question}
"""

class RAGEngine:
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.llm = get_llm(provider="groq")
        self.prompt = ChatPromptTemplate.from_template(VOICE_SYSTEM_PROMPT)
        self.parser = StrOutputParser()

    def query(self, user_query: str) -> str:
        """User query ke against RAG pipeline chala kar response return karta hai."""
        # Step A: Vector search
        relevant_docs = self.vector_store.search_similar(user_query, top_k=3)
        
        if relevant_docs:
            context_text = "\n\n".join([doc.page_content for doc in relevant_docs])
        else:
            context_text = "No relevant context available."

        # Step B: LLM Generation
        chain = self.prompt | self.llm | self.parser
        response = chain.invoke({
            "context": context_text,
            "question": user_query
        })
        return response.strip()