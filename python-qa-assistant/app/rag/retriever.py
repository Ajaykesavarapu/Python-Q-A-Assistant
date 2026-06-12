import os
from langchain_chroma import Chroma
from app.core.config import settings
from app.utils.logger import logger
from app.rag.embeddings import get_embedding_model

def get_retriever():
    """
    Returns the Chroma vector store retriever with parameters loaded from configuration settings.
    If the database is not indexed yet, builds a small in-memory or on-disk mock instance so the
    FastAPI web server launches successfully without crashing.
    """
    embeddings = get_embedding_model()
    chroma_path = settings.CHROMA_DB_PATH
    collection_name = settings.COLLECTION_NAME
    top_k = settings.TOP_K_RETRIEVAL
    
    # Check if the persistence path exists and contains databases
    db_exists = os.path.exists(chroma_path) and len(os.listdir(chroma_path)) > 0 if os.path.exists(chroma_path) else False
    
    if not db_exists:
        logger.warning(f"[!] Vector database directory {chroma_path} empty or missing! Seeding rapid runtime metadata to avoid crash.")
        # Create a tiny mock database to allow the server to run successfully
        from langchain_core.documents import Document
        mock_docs = [
            Document(
                page_content="Title: Pandas CSV parsing\n\nQuestion: How do load dataframe csv in pandas?\n\nAnswer: Use pd.read_csv('filename.csv') to read files.",
                metadata={"question_id": 1, "answer_id": 1001, "title": "Pandas CSV", "question_score": 10, "answer_score": 10, "tags": "python, pandas"}
            ),
            Document(
                page_content="Title: Python Lists vs Tuples\n\nQuestion: What is difference list vs tuple?\n\nAnswer: Lists are mutable. Tuples are immutable.",
                metadata={"question_id": 2, "answer_id": 1002, "title": "Python Lists vs Tuples", "question_score": 10, "answer_score": 10, "tags": "python"}
            )
        ]
        db = Chroma.from_documents(
            documents=mock_docs,
            embedding=embeddings,
            persist_directory=chroma_path,
            collection_name=collection_name
        )
    else:
        db = Chroma(
            persist_directory=chroma_path,
            embedding_function=embeddings,
            collection_name=collection_name
        )
        
    return db.as_retriever(search_kwargs={"k": top_k})
