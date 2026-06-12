#!/usr/bin/env python3
"""
Python script to execute dataset ingestion, cleaning, chunking, and ChromaDB indexing.
Run with: python scripts/ingest.py
"""

import os
import sys
import time
import logging
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Set paths relative to script
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Load Env
load_dotenv(BASE_DIR / ".env")

# Hand-rolled or library components
from app.utils.logger import logger
from app.ingestion.loader import load_and_join_datasets
from app.ingestion.preprocessor import clean_and_chunk_documents
from app.ingestion.indexer import index_documents_to_chroma

def main():
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("STARTING DATA INGESTION ENGINE")
    logger.info("=" * 60)

    questions_path = BASE_DIR / "data" / "raw" / "Questions.csv"
    answers_path = BASE_DIR / "data" / "raw" / "Answers.csv"
    tags_path = BASE_DIR / "data" / "raw" / "Tags.csv"

    # Quick check for CSV files, download if not exists
    if not (questions_path.exists() and answers_path.exists()):
        logger.warning("Dataset CSV files not found. Auto-running down loader...")
        from download_data import create_simulated_dataset
        create_simulated_dataset()

    try:
        logger.info("[*] Phase 1: Loading & Joining Questions and Answers...")
        qa_pairs = load_and_join_datasets(
            questions_path=str(questions_path),
            answers_path=str(answers_path),
            tags_path=str(tags_path)
        )
        logger.info(f"[✓] Joined {len(qa_pairs)} high-quality QA records successfully.")

        logger.info("[*] Phase 2: Preprocessing, HTML Cleaning, & Semantic Chunking...")
        chunks = clean_and_chunk_documents(qa_pairs)
        logger.info(f"[✓] Generated {len(chunks)} structural document chunks.")

        logger.info("[*] Phase 3: Indexing chunks in ChromaDB Vector Store...")
        vector_store = index_documents_to_chroma(chunks)
        
        elapsed_time = time.time() - start_time
        logger.info("=" * 60)
        logger.info(f"[+] INGESTION COMPLETELY SUCCESSFUL!")
        logger.info(f"    - Total Questions Processed: {len(qa_pairs)}")
        logger.info(f"    - Chunks Created and Vectorized: {len(chunks)}")
        logger.info(f"    - Execution Time: {elapsed_time:.2f} seconds")
        logger.info("=" * 60)

    except Exception as e:
        logger.exception(f"[-] CRITICAL ERROR DURING INGESTION: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
