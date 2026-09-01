import os
import sys

# Project root directory ko Python search path me add karna
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import streamlit.components.v1 as components
from config.settings import settings
from src.core.document_loader import DocumentProcessor
from src.database.vector_store import VectorStoreManager
from src.core.rag_engine import RAGEngine

st.set_page_config(
    page_title="Voice RAG Assistant",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Voice-Enabled RAG Assistant")
st.caption("A voice-first knowledge assistant powered by Vapi, LangChain, ChromaDB, and Groq")

# Initialize managers
vector_store = VectorStoreManager()
doc_processor = DocumentProcessor()
rag_engine = RAGEngine()

# Sidebar: Document Management
with st.sidebar:
    st.header("📂 Knowledge Base Manager")
    uploaded_files = st.file_uploader(
        "Upload Documents (PDF, TXT, DOCX)",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True
    )

    if st.button("📥 Ingest Documents", use_container_width=True):
        if uploaded_files:
            with st.spinner("Processing & indexing documents into ChromaDB..."):
                all_chunks = []
                for file in uploaded_files:
                    chunks = doc_processor.process_uploaded_file(file)
                    all_chunks.extend(chunks)
                vector_store.add_documents(all_chunks)
                st.success(f"Success! Indexed {len(all_chunks)} chunks from {len(uploaded_files)} files.")
        else:
            st.warning("Please upload at least one document first.")

    st.divider()
    if st.button("🗑️ Reset Database", use_container_width=True):
        vector_store.clear_database()
        st.info("ChromaDB vector collection has been reset.")

# Main Tabs for Testing
tab_text, tab_voice = st.tabs(["💬 Text Query Testing", "🗣️ Live Voice Agent"])

with tab_text:
    st.subheader("Test RAG Pipeline (Text Mode)")
    user_query = st.text_input("Ask a question based on your uploaded documents:")
    
    if st.button("Run Query"):
        if user_query.strip():
            with st.spinner("Searching Vector DB & generating answer..."):
                answer = rag_engine.query(user_query)
                st.markdown("### Response:")
                st.write(answer)
        else:
            st.warning("Please type a question.")

with tab_voice:
    st.subheader("🗣️ Real-Time Voice Agent")
    st.write("Neeche diye gaye voice button par click karein aur mic allow karke directly baat karein:")
    
    vapi_html = f"""
    <div id="vapi-widget-container" style="display: flex; justify-content: center; align-items: center; padding: 20px;"></div>
    <script src="https://cdn.jsdelivr.net/gh/VapiAI/html-script-tag@latest/dist/assets/index.js"></script>
    <script>
      var vapiInstance = null;
      const apiKey = "{settings.VAPI_PUBLIC_KEY}";
      const assistantId = "{settings.VAPI_ASSISTANT_ID}";
      
      const buttonConfig = {{
        position: "center",
        offset: "0px",
        width: "60px",
        height: "60px",
        idle: {{
          color: "rgb(255, 75, 75)",
          type: "pill",
          title: "Start Voice Conversation",
          subtitle: "Talk to RAG Voice Assistant",
          icon: "https://unpkg.com/lucide-static@0.321.0/icons/phone.svg",
        }},
        loading: {{
          color: "rgb(93, 124, 202)",
          type: "pill",
          title: "Connecting...",
          subtitle: "Please wait",
          icon: "https://unpkg.com/lucide-static@0.321.0/icons/loader-2.svg",
        }},
        active: {{
          color: "rgb(255, 0, 0)",
          type: "pill",
          title: "Call in progress...",
          subtitle: "Listening to you",
          icon: "https://unpkg.com/lucide-static@0.321.0/icons/phone-off.svg",
        }},
      }};

      vapiSDK.run({{
        apiKey: apiKey,
        assistant: assistantId,
        config: buttonConfig,
      }});
    </script>
    """
    components.html(vapi_html, height=220)