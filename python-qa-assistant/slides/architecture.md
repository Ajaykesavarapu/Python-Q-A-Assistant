# Python Programming Q&A Assistant — Slide Deck

## Slide 1: Title — Python Q&A Assistant for Analytics Vidhya
- **Sub-header**: Production-Ready Agentic RAG Platform for Data Science Learners
- **Author**: Ajay Kesavarapu, AI/ML Platform Engineer
- **Theme**: Minimal Slate Dark

---

## Slide 2: Problem Statement & Vision
- **Learner Friction**: Searching for quality Python solutions across scattered online discussions is distracting and error-prone.
- **Accurate Context**: Generative AI models are prone to hallucinating syntactical syntax and outdated patterns.
- **Goal**: Build an AI programmer's Q&A assistant utilizing grounding through verified Stack Overflow Python datasets, guaranteeing accurate, secure, code-backed answers.

---

## Slide 3: System Architecture
- **Layered Design**:
  - **API Layer**: Fast, non-blocking asynchronous endpoints served via FastAPI and Uvicorn.
  - **Agent Engine**: Agent orchestration using LangGraph with strict conditional node matching.
  - **Durable Retrieval (RAG)**: Persistent semantic storage with ChromaDB & dense local/cloud embedding vector spaces.
- **Visual Path**:
  `[Client Web/Curl] ⇄ [FastAPI Web Server] ⇄ [LangGraph Agent Executor] 🔌 [Chroma DB / Gemini API]`

---

## Slide 4: LangGraph Agent Flow
- **State-Authoritative Nodes**:
  1. `classify_question_node`: Identifies whether an incoming query is Python/programming related.
  2. `retrieve_context_node`: Connects to ChromaDB to retrieve top-5 relevant code scripts and discussions.
  3. `generate_answer_node`: Employs grounding and generates custom markdown answers.
  4. `fallback_node`: Gracefully catches security risks or unrelated queries with a polite message.
- **Branching**:
  `START ➔ classify_question ➔ [Is Python?] --(Yes)--> retrieve ➔ generate ➔ END`
  `                             └──(No)--> fallback ➔ END`

---

## Slide 5: RAG Pipeline Mechanics
- **Ingestion**:
  - Parse `Questions.csv`, `Answers.csv`, and `Tags.csv`.
  - Filter by `score > 0` and highest ParentId score. Clean raw HTML.
  - Split using `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)`.
- **Retrieval & Retrieval-Grounded Generation**:
  - Embed with `text-embedding-3-small` or local embeddings.
  - Wrap in custom LangChain LCEL (LangChain Expression Language) for linear flow:
    `retriever | format_docs | prompt | llm | parser`

---

## Slide 6: Technology Stack & Selection
- **FastAPI**: Asynchronous event loop, rapid routing, automated OpenAPI/Swagger generation.
- **LangChain & LangGraph**: Clean declarative graph workflows with deterministic state tracking.
- **ChromaDB**: Native vector storage, serverless operational modes, metadata querying.
- **OpenAI/HuggingFace**: High-performance semantic density modeling.

---

## Slide 7: API Design
- **GET `/health`**: Returns engine status and vector DB connection heartbeat.
- **POST `/ask`**: Accepts JSON query body with optional chat history, returning:
  - `answer` (Grounded markdown)
  - `sources` (Matched Snippet, Title, ID, and Relevance Score)
  - `steps_taken` (Array of executed agent nodes)
  - `processing_time_ms`
- **POST `/ask/stream`**: Server-Sent Events (SSE) streaming tokens to the client.
- **GET `/stats`**: Exposes corpus intelligence (indexed size in MB, total documents).

---

## Slide 8: Test Suitability & Coverage
- **API Tests (`test_api.py`)**: Uses `httpx.AsyncClient` validating 200, 422, CORS, and structural schemas.
- **Pipeline Verification (`test_rag.py`)**: Tests semantic accuracy of documents retrieved under mock settings.
- **Edge cases covered**: Empty queries, SQL injections, fully off-topic questions.
- **8 Diverse Production Queries**: Evaluated and validated across Exception Handling, Data Merging, GIL, SQLite, and Pandas.

---

## Slide 9: Scaling for 100+ Concurrent Users
- **Multi-Worker Execution**: Deploy with `uvicorn --workers 4` for CPU concurrency.
- **Redis Caching**: Layered key-value cache (TTL = 1 hour) for redundant, high-frequency user inquiries.
- **Vector Search Tuning**: Transition serverless ChromaDB to a decoupled, low-latency PostgreSQL with pgvector.
- **Cost Estimation**:
  - Classification using cheaper models (e.g. `gpt-4o-mini` or `gemini-3.5-flash`): ~$0.0001 per run.
  - Average query token usage: ~1500 tokens. Estimated total of $0.002 per production request.

---

## Slide 10: Future Roadmap & Improvements
- **Self-Correcting RAG**: Implement CRAG (Corrective RAG) nodes to re-evaluate or expand search using Google Grounding if local vector distance exceeds thresholds.
- **Fine-Tuning**: Finetune a lightweight model (e.g., Llama-3-8B-Instruct) directly on clean Python questions corpora.
- **Advanced Ingestion**: Multi-vector indexing mapping small chunks to larger summaries.
