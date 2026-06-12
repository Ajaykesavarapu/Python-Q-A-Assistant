import re
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.utils.logger import logger

def clean_html(html_string: str) -> str:
    """Cleans HTML tags using BeautifulSoup for semantic text reading."""
    if not html_string:
        return ""
    # BeautifulSoup parsing
    soup = BeautifulSoup(html_string, "lxml" if "lxml" in BeautifulSoup.NO_PARSE_ONLY else "html.parser")
    # Clean standard layout tags but preserve block structure readability
    return soup.get_text(separator="\n").strip()

def clean_and_chunk_documents(qa_pairs: list, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """
    Cleans raw bodies, pairs questions/answers, creates LangChain Documents, and splits into chunks.
    """
    logger.info("Initializing BeautifulSoup cleaning stage...")
    documents = []
    
    for pair in qa_pairs:
        # Clean HTML fields
        clean_q_body = clean_html(pair["question_body"])
        clean_a_body = clean_html(pair["answer_body"])
        title = pair["title"]
        
        # Combined full grounding context template
        combined_text = (
            f"Title: {title}\n\n"
            f"Question:\n{clean_q_body}\n\n"
            f"Accepted Answer:\n{clean_a_body}"
        )
        
        metadata = {
            "question_id": pair["question_id"],
            "answer_id": pair["answer_id"],
            "title": title,
            "question_score": pair["question_score"],
            "answer_score": pair["answer_score"],
            "tags": ", ".join(pair["tags"])
        }
        
        documents.append(Document(page_content=combined_text, metadata=metadata))
        
    # Chunking using recursive character text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    logger.info(f"Chunking {len(documents)} raw documents with size={chunk_size}, overlap={chunk_overlap}...")
    splitted_chunks = splitter.split_documents(documents)
    return splitted_chunks
