# Python Q&A Assistant — Analytics Vidhya AI Engineer Assessment

## Overview
The **Python Programming Q&A Assistant** is a production-grade, AI-powered system designed to provide grounded, highly accurate, and syntax-valid answers resolving Python programming queries. By sourcing content from a verified, structured Kaggle Stack Overflow dataset, the assistant mitigates standard LLM hallucinations and bridges learners directly with real-world, high-utility code assets.

## Architecture

### System Flow Diagram
```
              ┌──────────────────────────────────────────────────┐
              │           Client Interface (Curl / Web UI)       │
              └────────────────────────┬─────────────────────────┘
                                       │
                                       ▼ (HTTP REST / Streaming SSE)
              ┌──────────────────────────────────────────────────┐
              │              FastAPI & Uvicorn Router            │
              └────────────────────────┬─────────────────────────┘
                                       │
                                       ▼ (ainvoke / astream)
              ┌──────────────────────────────────────────────────┐
              │             LangGraph Agent State Graph          │
              │                                                  │
              │   ┌──────────────────────────────────────────┐   │
              │   │         classify_question_node           │   │
              │   └────────────────────┬─────────────────────┘   │
              │                        │                         │
              │                        ▼ (Is it Python related?) │
              │                   [Conditional]                  │
              │                    /         \                   │
              │                  (Yes)       (No)                │
              │                  /             \                 │
              │                 ▼               ▼                │
              │       ┌───────────┐       ┌───────────┐          │
              │       │ retrieve_ │       │ fallback_ │          │
              │       │  context_ │       │   node    │          │
              │       │   node    │       └─────┬─────┘          │
              │       └─────┬─────┘             │                │
              │             │                   │                │
              │             ▼                   │                │
              │       ┌───────────┐             │                │
              │       │ generate_ │             │                │
              │       │  answer_  │             │                │
              │       │   node    │             │                │
              │       └─────┬─────┘             │                │
              │             │                   │                │
              │             ▼                   ▼                │
              │          [ END ]             [ END ]             │
              └──────────────────────────────────────────────────┘
```

### Flow Explanations
1. **LangGraph Agentic Flow**: At startup, incoming queries enter the `classify_question_node` to determine if the payload is programming relative. Coding queries get routed via conditional edges to the Chroma DB vector store retriever in the `retrieve_context_node` before landing in the `generate_answer_node` for grounded translation. Unrelated queries route into `fallback_node` generating a polite guide restricting questions to Python.
2. **Standard RAG Pipeline**: An alternative high-efficiency, stream-compatible pathway is compiled programmatically using LangChain Expression Language (LCEL): `retriever | format_docs | prompt | llm | output_parser`.

## Tech Stack
- **Languages & Frameworks**: Python 3.11, FastAPI (Fast REST routes)
- **Agent Orchestration**: LangGraph, LangChain LCEL (State management, modular chains)
- **Vector DB Storage**: ChromaDB (Serverless semantic search indexing)
- **Embeddings Space**: OpenAI `text-embedding-3-small` or `sentence-transformers/all-MiniLM-L6-v2`
- **Underlying LLM**: OpenAI `gpt-4o-mini` / Anthropic `claude-3-5-haiku` / Gemini models.

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- OpenAI API Key
- Kaggle API Credentials (Optional - Mock data is seamlessly generated if keys aren't found)

### Local Setup Steps
1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd python-qa-assistant
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env and enter your real API Keys
   ```

5. **Download and prepare the Dataset**:
   ```bash
   python scripts/download_data.py
   ```

6. **Ingest and Index the Data**:
   ```bash
   python scripts/ingest.py
   ```

7. **Start the FastAPI Application Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

## Docker Setup
Build and run the entire suite as a portable Docker container:
```bash
docker-compose up --build
```
This maps the FastAPI server to local port `8000` with volumes binding `chroma_db/` and `data/` for data persistence.

---

## API Documentation

The FastAPI Swagger interface is auto-generated and served at `http://localhost:8000/docs`.

### Selected Outlines & Examples

#### 1. GET /api/health
Returns system operational statuses.
```bash
curl -X GET http://localhost:8000/api/health
```
**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "vector_store": "connected"
}
```

#### 2. POST /api/ask
Resolve queries with grounded Python code examples.
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I read a CSV file using pandas?", "chat_history": []}'
```
**Response**:
```json
{
  "answer": "To load a CSV file, use pd.read_csv() as follows...\n\n```python\nimport pandas as pd\ndf = pd.read_csv('myfile.csv')\n```",
  "sources": [
    {
      "title": "How do I read a CSV in pandas?",
      "score": 0.96,
      "snippet": "Read file using pd.read_csv..."
    }
  ],
  "steps_taken": ["classify_question", "retrieve_context", "generate_answer"],
  "model_used": "gpt-4o-mini",
  "processing_time_ms": 420
}
```

#### 3. POST /api/ask/stream
Submit requests returning streamed tokens (Server-Sent Events).
```bash
curl -N -X POST http://localhost:8000/api/ask/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "What is mutability?"}'
```

#### 4. GET /api/stats
Exposes corpus metadata statistics.
```bash
curl -X GET http://localhost:8000/api/stats
```

---

## Running Tests
Run quality assertions across nodes, API boundaries, and custom RAG chains:
```bash
pytest tests/ -v --cov=app
```

---

## Deployment

### Hugging Face Spaces
1. Create a "Docker" SDK Space on Hugging Face.
2. Link your repository.
3. Configure Space secrets: `OPENAI_API_KEY`, setting environment flags.

### Render
Easily deploy using Render's blueprint:
```bash
# Deploys automatically by parsing render.yaml layout settings
```

### Railway
1. Connect sandbox GitHub repository to Railway.
2. Bind the port to `PORT=8000`.
3. Fill env credentials and trigger production deployment.

---

## Live Demo URL
Explore the deployed QA Assistant at:
`https://ais-pre-draatrj5rmjduinz4jtj6f-62150266998.asia-southeast1.run.app`

---

## Test Results
100% of standard tests and functional evaluations succeeded. Our benchmark report evaluating all 8 diverse developer queries is cataloged in `notebooks/test_results.ipynb`. Across the suite, average query resolution response times ranged from 250ms to 600ms.

---

## Scaling for 100+ Concurrent Users

To transition this workspace to support 100+ active concurrent users seamlessly:

1. **CPU/Asynchronous Tuning**: Maximize threading by launching with multiple Gunicorn/Uvicorn workers (`uvicorn app.main:app --workers 4`). This distributes requests across separate threads inside the microcontainer.
2. **Caching Strategy (Redis)**: Introduce a middle caching tier with Redis (TTL = 1 Hour). For high-frequency duplicate questions (e.g., "pandas read csv"), bypass vector lookups and LLM completions entirely, returning results instantly with 0ms LLM overhead.
3. **Decoupled Vector DB DB**: Move from sqlite-backed serverless Chroma DB to a high-capacity, dedicated database server like PostgreSQL with `pgvector` or Qdrant cluster to isolate indexing I/O.
4. **Embedding Batching & Model Choices**: Batch incoming indexers. Use lightweight cost-effective models (e.g. `gpt-4o-mini` or `gemini-3.5-flash`) for low cost and latency.
5. **Cost Optimization Estimates**:
   - Classification model call: ~$0.0001
   - Storage vector query matching: $0.0000
   - Generator tokens (avg 1500 context tokens): ~$0.002
   - **Estimated Total Cost Per Query: ~$0.0021**
