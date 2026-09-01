import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import settings

class DocumentProcessor:
    def __init__(self):
        # Text ko chote tukron (chunks) me divide karne wala splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )

    def process_uploaded_file(self, uploaded_file):
        """
        Streamlit uploaded file ko read kar ke chunked documents return karta hai.
        """
        suffix = os.path.splitext(uploaded_file.name)[1].lower()
        
        # Temporary file create karna taake LangChain loaders read kar sakein
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name

        try:
            # File format ke mutabiq loader choose karna
            if suffix == ".pdf":
                loader = PyPDFLoader(tmp_path)
            elif suffix == ".txt":
                loader = TextLoader(tmp_path, encoding="utf-8")
            elif suffix in [".docx", ".doc"]:
                loader = Docx2txtLoader(tmp_path)
            else:
                raise ValueError(f"Unsupported file format: {suffix}")

            docs = loader.load()
            
            # Har chunk ke sath file ka original naam metadata me add karna
            for doc in docs:
                doc.metadata["source_file"] = uploaded_file.name
                
            chunks = self.text_splitter.split_documents(docs)
            return chunks
            
        finally:
            # Kaam khatam hone par temporary file delete karna
            if os.path.exists(tmp_path):
                os.remove(tmp_path)