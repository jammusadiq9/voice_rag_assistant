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
    st.write("Vapi voice assistant se baat karne ke liye microphone access enable karein:")

    # Direct Web-ready Vapi Call Button (Bypasses Streamlit iframe sandboxing)
    vapi_web_portal = f"""
    <div style="display:flex; justify-content:center; align-items:center; flex-direction:column; padding:20px; border:1px solid #333; border-radius:10px; background-color:#0e1117;">
        <p style="color:#ffffff; margin-bottom:15px; font-size:16px;">Click below to launch interactive Voice Agent session</p>
        <button id="vapi-btn" onclick="startCall()" style="background-color:#ff4b4b; color:white; border:none; padding:12px 28px; font-size:16px; font-weight:bold; border-radius:8px; cursor:pointer;">
            🎙️ Start Voice Conversation
        </button>
        <p id="vapi-status" style="color:#888; font-size:13px; margin-top:12px;">Status: Ready to connect</p>
    </div>

    <script src="https://cdn.jsdelivr.net/gh/VapiAI/html-script-tag@latest/dist/assets/index.js"></script>
    <script>
        var vapiInstance = null;
        var inCall = false;

        function updateStatus(text, color) {{
            var st = document.getElementById("vapi-status");
            if (st) {{
                st.innerText = "Status: " + text;
                st.style.color = color;
            }}
        }}

        function startCall() {{
            var btn = document.getElementById("vapi-btn");
            if (!inCall) {{
                updateStatus("Connecting to Vapi...", "#f39c12");
                vapiInstance = window.vapiSDK.run({{
                    apiKey: "{settings.VAPI_PUBLIC_KEY}",
                    assistant: "{settings.VAPI_ASSISTANT_ID}"
                }});

                vapiInstance.on('call-start', () => {{
                    inCall = true;
                    btn.innerText = "🔴 End Call";
                    btn.style.backgroundColor = "#27ae60";
                    updateStatus("Connected (Listening...)", "#2ecc71");
                }});

                vapiInstance.on('call-end', () => {{
                    inCall = false;
                    btn.innerText = "🎙️ Start Voice Conversation";
                    btn.style.backgroundColor = "#ff4b4b";
                    updateStatus("Call Ended", "#888");
                }});

                vapiInstance.on('error', (err) => {{
                    console.error("Vapi Error:", err);
                    updateStatus("Connection Error. Check console/keys.", "#e74c3c");
                }});
            }} else {{
                if (vapiInstance) {{
                    vapiInstance.stop();
                }}
            }}
        }}
    </script>
    """
    components.html(vapi_web_portal, height=180)