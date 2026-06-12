import os
from langchain_chroma import Chroma
from app.core.config import settings
from app.utils.logger import logger
from app.rag.embeddings import get_embedding_model

def index_documents_to_chroma(chunks: list) -> Chroma:
    """
    Instantiates the selected embedding model, indexes document chunks,
    and returns a persistent ChromaDB Vector Store.
    """
    logger.info("Retrieving or downloading embedding model...")
    embeddings = get_embedding_model()
    
    chroma_path = settings.CHROMA_DB_PATH
    collection_name = settings.COLLECTION_NAME
    
    logger.info(f"Creating persistent Chroma DB index at: {chroma_path}, collection: {collection_name}...")
    
    # Initialize Persistent Chroma DB vector store
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=chroma_path,
        collection_name=collection_name
    )
    
    logger.info(f"[+] Successfully indexed {len(chunks)} chunks into self-contained ChromaDB.")
    return vector_store
