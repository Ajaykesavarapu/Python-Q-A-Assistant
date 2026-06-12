#!/usr/bin/env python3
"""
Ingest the Stack Overflow Q&A dataset into Chroma Cloud.
Run with: python scripts/ingest_cloud.py
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# --- CHROMA CLOUD CREDENTIALS ---
CHROMA_API_KEY  = "ck-6uthjAvAxWT7p4m5sFKJPS5WjDsgrdxQhHjP5yfGUjAG"
CHROMA_TENANT   = "42b4f98b-4a30-4074-88a3-973ecc46be27"
CHROMA_DATABASE = "PythonQAAssistant"
COLLECTION_NAME = "stackoverflow_python"

import chromadb
from chromadb.utils import embedding_functions
import pandas as pd
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ── helpers ──────────────────────────────────────────────────────────────────

def clean_html(html: str) -> str:
    if not html:
        return ""
    return BeautifulSoup(html, "html.parser").get_text(separator="\n").strip()


def load_qa_pairs():
    questions_path = BASE_DIR / "data" / "raw" / "Questions.csv"
    answers_path   = BASE_DIR / "data" / "raw" / "Answers.csv"
    tags_path      = BASE_DIR / "data" / "raw" / "Tags.csv"

    print(f"Loading Questions from {questions_path}...")
    questions_df = pd.read_csv(questions_path)
    print(f"Loading Answers from {answers_path}...")
    answers_df   = pd.read_csv(answers_path)
    print(f"Loading Tags from {tags_path}...")
    tags_df      = pd.read_csv(tags_path)

    best_answers  = answers_df.sort_values("Score", ascending=False).drop_duplicates(subset="ParentId")
    merged        = questions_df.merge(best_answers, left_on="Id", right_on="ParentId", suffixes=("_q", "_a"))
    tags_grouped  = tags_df.groupby("Id")["Tag"].apply(list).reset_index()
    merged        = merged.merge(tags_grouped, left_on="Id_q", right_on="Id", how="left")
    merged["Tag"] = merged["Tag"].apply(lambda x: x if isinstance(x, list) else [])

    pairs = []
    for _, row in merged.iterrows():
        pairs.append({
            "question_id":    int(row["Id_q"]),
            "answer_id":      int(row["Id_a"]),
            "title":          str(row.get("Title", "")),
            "question_body":  str(row.get("Body_q", "")),
            "answer_body":    str(row.get("Body_a", "")),
            "question_score": int(row.get("Score_q", 0)),
            "answer_score":   int(row.get("Score_a", 0)),
            "tags":           row["Tag"],
        })
    print(f"Joined {len(pairs)} QA records.")
    return pairs


def build_chunks(pairs, chunk_size=1000, chunk_overlap=200):
    from langchain_core.documents import Document
    documents = []
    for p in pairs:
        combined = (
            f"Title: {p['title']}\n\n"
            f"Question:\n{clean_html(p['question_body'])}\n\n"
            f"Accepted Answer:\n{clean_html(p['answer_body'])}"
        )
        documents.append(Document(
            page_content=combined,
            metadata={
                "question_id":    p["question_id"],
                "answer_id":      p["answer_id"],
                "title":          p["title"],
                "question_score": p["question_score"],
                "answer_score":   p["answer_score"],
                "tags":           ", ".join(p["tags"]),
            }
        ))
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")
    return chunks


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("INGESTING INTO CHROMA CLOUD")
    print(f"  Tenant:     {CHROMA_TENANT}")
    print(f"  Database:   {CHROMA_DATABASE}")
    print(f"  Collection: {COLLECTION_NAME}")
    print("=" * 60)

    # 1. Connect to Chroma Cloud
    client = chromadb.CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE,
    )
    print("[✓] Connected to Chroma Cloud")

    # 2. Embedding function (local, free — no OpenAI key needed)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # 3. Create or get collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"[✓] Collection '{COLLECTION_NAME}' ready (count={collection.count()})")

    # 4. Load and chunk data
    pairs  = load_qa_pairs()
    chunks = build_chunks(pairs)

    # 5. Prepare documents for Chroma
    ids        = [f"doc_{i}" for i in range(len(chunks))]
    texts      = [c.page_content for c in chunks]
    metadatas  = [c.metadata for c in chunks]

    # 6. Upsert into cloud collection
    BATCH_SIZE = 50
    for i in range(0, len(chunks), BATCH_SIZE):
        batch_ids   = ids[i:i+BATCH_SIZE]
        batch_texts = texts[i:i+BATCH_SIZE]
        batch_meta  = metadatas[i:i+BATCH_SIZE]
        collection.upsert(ids=batch_ids, documents=batch_texts, metadatas=batch_meta)
        print(f"  Upserted batch {i//BATCH_SIZE + 1}: docs {i}–{min(i+BATCH_SIZE, len(chunks))-1}")

    final_count = collection.count()
    print("=" * 60)
    print(f"[✓] INGESTION COMPLETE — {final_count} documents in cloud")
    print("=" * 60)


if __name__ == "__main__":
    main()
