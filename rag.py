from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
import os

#create pdf vector store
def create_pdf_vector_store():
    """Create or load a FAISS vector store from PDF files for weather knowledge."""
    vector_store_dir = "vector_store/pdf"
    vector_store_path = os.path.join(vector_store_dir, "faiss_index")

    # Check if vector store exists
    if os.path.exists(vector_store_path):
        try:
            embeddings = OllamaEmbeddings(model="nomic-embed-text")
            vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
            print("Loaded existing PDF vector store from disk.")
            return vector_store
        except Exception as e:
            print(f"Error loading PDF vector store: {str(e)}. Recreating vector store.")

    # Create new vector store
    try:
        pdf_loader = DirectoryLoader("data/climate_data", glob="**/*.pdf", loader_cls=PyPDFLoader)
        pdf_docs = pdf_loader.load()
       #chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(pdf_docs)
        print(f"chunks created: {len(splits)}")
        #embed
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        #store vector db
        vector_store = FAISS.from_documents(splits, embeddings)
        
        # Create directory if it doesn't exist
        os.makedirs(vector_store_dir, exist_ok=True)
        # Save vector store to disk
        vector_store.save_local(vector_store_path)
        print(f"Saved PDF vector store to {vector_store_path}")
        return vector_store
    except Exception as e:
        print(f"Error creating PDF vector store: {str(e)}")
        return None

