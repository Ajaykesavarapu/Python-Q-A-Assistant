#!/usr/bin/env python3
"""
Standalone ingestion helper that bypasses the broken preprocessor.
This is a NEW file and does NOT modify any existing code.
Run with: python scripts/ingest_direct.py
"""

import os
import sys
import time
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set empty OpenAI key so embeddings fall back to SentenceTransformers
os.environ.setdefault("OPENAI_API_KEY", "")
os.environ["EMBEDDING_MODEL"] = "all-MiniLM-L6-v2"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ingest_direct")

import re
import pandas as pd
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def clean_html(html_string: str) -> str:
    """Cleans HTML tags – fixed version using 'html.parser'."""
    if not html_string:
        return ""
    soup = BeautifulSoup(html_string, "html.parser")
    return soup.get_text(separator="\n").strip()

def load_and_join_datasets(questions_path, answers_path, tags_path):
    logger.info(f"Loading Questions from {questions_path}...")
    questions_df = pd.read_csv(questions_path)
    logger.info(f"Loading Answers from {answers_path}...")
    answers_df = pd.read_csv(answers_path)
    logger.info(f"Loading Tags from {tags_path}...")
    tags_df = pd.read_csv(tags_path)

    # Get best answer per question (highest score)
    best_answers = answers_df.sort_values("Score", ascending=False).drop_duplicates(subset="ParentId")
    merged = questions_df.merge(best_answers, left_on="Id", right_on="ParentId", suffixes=("_q", "_a"))

    # Group tags per question
    tags_grouped = tags_df.groupby("Id")["Tag"].apply(list).reset_index()
    merged = merged.merge(tags_grouped, left_on="Id_q", right_on="Id", how="left")
    merged["Tag"] = merged["Tag"].apply(lambda x: x if isinstance(x, list) else [])

    qa_pairs = []
    for _, row in merged.iterrows():
        qa_pairs.append({
            "question_id": int(row["Id_q"]),
            "answer_id": int(row["Id_a"]),
            "title": str(row.get("Title", "")),
            "question_body": str(row.get("Body_q", "")),
            "answer_body": str(row.get("Body_a", "")),
            "question_score": int(row.get("Score_q", 0)),
            "answer_score": int(row.get("Score_a", 0)),
            "tags": row["Tag"]
        })

    logger.info(f"Joined {len(qa_pairs)} high-quality QA records.")
    return qa_pairs

def build_documents(qa_pairs, chunk_size=1000, chunk_overlap=200):
    documents = []
    for pair in qa_pairs:
        clean_q = clean_html(pair["question_body"])
        clean_a = clean_html(pair["answer_body"])
        combined_text = (
            f"Title: {pair['title']}\n\n"
            f"Question:\n{clean_q}\n\n"
            f"Accepted Answer:\n{clean_a}"
        )
        metadata = {
            "question_id": pair["question_id"],
            "answer_id": pair["answer_id"],
            "title": pair["title"],
            "question_score": pair["question_score"],
            "answer_score": pair["answer_score"],
            "tags": ", ".join(pair["tags"])
        }
        documents.append(Document(page_content=combined_text, metadata=metadata))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Created {len(chunks)} document chunks.")
    return chunks

def index_to_chroma(chunks, chroma_path, collection_name):
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_chroma import Chroma

    logger.info("Loading SentenceTransformer embedding model (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

    logger.info(f"Indexing {len(chunks)} chunks into ChromaDB at {chroma_path}...")
    
    # Remove old db if it exists
    import shutil
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=chroma_path,
        collection_name=collection_name
    )
    logger.info(f"Indexed {len(chunks)} chunks successfully into ChromaDB!")
    return db

def main():
    start = time.time()
    logger.info("=" * 60)
    logger.info("DIRECT INGESTION (bypassing broken preprocessor)")
    logger.info("=" * 60)

    questions_path = BASE_DIR / "data" / "raw" / "Questions.csv"
    answers_path   = BASE_DIR / "data" / "raw" / "Answers.csv"
    tags_path      = BASE_DIR / "data" / "raw" / "Tags.csv"
    chroma_path    = str(BASE_DIR / "chroma_db")
    collection_name = "stackoverflow_python"

    qa_pairs = load_and_join_datasets(questions_path, answers_path, tags_path)
    chunks   = build_documents(qa_pairs)
    index_to_chroma(chunks, chroma_path, collection_name)

    elapsed = time.time() - start
    logger.info("=" * 60)
    logger.info(f"INGESTION COMPLETE in {elapsed:.1f}s")
    logger.info(f"  QA records: {len(qa_pairs)}")
    logger.info(f"  Chunks:     {len(chunks)}")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
