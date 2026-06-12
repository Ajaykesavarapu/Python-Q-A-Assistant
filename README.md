# Python Q&A Assistant

A production-grade, AI-powered Python programming assistant built with **RAG (Retrieval-Augmented Generation)** and a **LangGraph agentic pipeline**. Ask any Python question and get grounded, accurate answers backed by real Stack Overflow data — not hallucinated responses.

---

## What It Does

The assistant classifies incoming questions, retrieves the most relevant Stack Overflow answers from a local vector store, and generates a grounded, code-rich response using your preferred LLM provider (Google Gemini or OpenAI). Off-topic questions are caught early and can be optionally routed to an external LLM.

**Key features:**
- 🔍 **Semantic search** over a curated Stack Overflow Python corpus (ChromaDB)
- 🤖 **LangGraph agent** with classify → retrieve → generate node workflow
- 🌐 **Multi-provider LLM support** — Google Gemini, OpenAI
- 💬 **Streaming responses** via Server-Sent Events (`/api/ask/stream`)
- 🖥️ **Premium web UI** — dark mode, source cards, live agent workflow visualizer, system logs panel
- ⚙️ **Settings drawer** — configure provider, model, API key, temperature without touching code

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Web Browser (UI)                   │
│         index.html — Vanilla HTML/CSS/JS            │
└────────────────────────┬────────────────────────────┘
                         │  HTTP REST  (port 3000 dev / 8000 prod)
                         ▼
┌─────────────────────────────────────────────────────┐
│            Express Dev Server (server.ts)           │
│   Vite HMR + /api/health, /api/stats, /api/ask,     │
│   /api/ask/external  →  Gemini / OpenAI direct      │
└────────────────────────┬────────────────────────────┘
                         │  proxied or standalone
                         ▼
┌─────────────────────────────────────────────────────┐
│           FastAPI + Uvicorn  (port 8000)            │
│              app/api/routes.py                      │
└────────────────────────┬────────────────────────────┘
                         │  ainvoke / astream
                         ▼
┌─────────────────────────────────────────────────────┐
│           LangGraph Agent  (StateGraph)             │
│                                                     │
│  classify_question_node                             │
│         │                                           │
│    Python? ──Yes──▶ retrieve_context_node           │
│         │                  │                        │
│        No                  ▼                        │
│         │         generate_answer_node              │
│         ▼                  │                        │
│   fallback_node            ▼                        │
│         │               [END]                       │
│         ▼                                           │
│      [END]                                          │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│         ChromaDB  Vector Store (local)             │
│    Stack Overflow Python Q&A corpus                 │
│    Embeddings: sentence-transformers / OpenAI       │
└─────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Vanilla HTML5, CSS3 (custom properties), JavaScript (ES2022) |
| **Dev Server** | Node.js + Express + Vite (HMR in development) |
| **Backend API** | Python 3.11, FastAPI, Uvicorn |
| **Agent Orchestration** | LangGraph `StateGraph`, LangChain LCEL |
| **Vector Store** | ChromaDB (local, serverless) |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` or OpenAI `text-embedding-3-small` |
| **LLM Providers** | Google Gemini (`gemini-*`), OpenAI (`gpt-4o-mini`, etc.) |
| **HTTP Client** | `httpx` (async, for external LLM calls) |
| **Data Source** | Stack Overflow Python Q&A (Kaggle dataset) |

---

## Repository Structure

```
Python-Q-A-Assistant/
├── index.html                  # Main frontend entry point (served by Vite)
├── frontend/
│   └── index.html              # Mirror copy of the frontend
├── server.ts                   # Express + Vite dev server
├── package.json                # Node dependencies & dev scripts
├── vite.config.ts              # Vite bundler config
├── tsconfig.json               # TypeScript config
├── .env.example                # Required environment variables template
│
└── python-qa-assistant/        # Python FastAPI backend
    ├── app/
    │   ├── main.py             # FastAPI app factory + middleware
    │   ├── api/
    │   │   └── routes.py       # /health, /ask, /ask/external, /ask/stream, /stats
    │   ├── agent/
    │   │   ├── graph.py        # LangGraph StateGraph definition
    │   │   ├── nodes.py        # classify, retrieve, generate, fallback nodes
    │   │   └── state.py        # AgentState TypedDict
    │   ├── rag/
    │   │   ├── pipeline.py     # LangChain LCEL RAG chain
    │   │   ├── retriever.py    # ChromaDB retriever setup
    │   │   └── embeddings.py   # Embedding model loader
    │   ├── models/
    │   │   └── schemas.py      # Pydantic request/response models
    │   ├── core/
    │   │   ├── config.py       # Settings (pydantic-settings)
    │   │   └── llm.py          # LLM client factory
    │   └── ingestion/          # Data ingestion pipeline
    ├── scripts/
    │   ├── download_data.py    # Download Stack Overflow dataset
    │   └── ingest.py           # Embed & index into ChromaDB
    ├── requirements.txt
    ├── docker-compose.yml
    └── render.yaml             # Render.com deployment config
```

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- An API key for **Google Gemini** or **OpenAI** (at least one required)
- Kaggle credentials (optional — mock data is auto-generated if absent)

---

### 1. Clone the Repository

```bash
git clone https://github.com/Ajaykesavarapu/Python-Q-A-Assistant.git
cd Python-Q-A-Assistant
```

---

### 2. Set Up the Python Backend

```bash
cd python-qa-assistant

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Open .env and fill in your API keys
```

**`.env` variables:**
```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
LLM_PROVIDER=google        # google | openai | anthropic
LLM_MODEL=gemini-1.5-flash
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

### 3. Download & Index the Dataset

```bash
# Download Stack Overflow Python Q&A corpus from Kaggle
python scripts/download_data.py

# Embed documents and populate ChromaDB
python scripts/ingest.py
```

> If Kaggle credentials are not configured, a mock dataset is generated automatically so you can still run and test the system.

---

### 4. Start the Backend Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The FastAPI server starts at `http://localhost:8000`.  
Interactive API docs: `http://localhost:8000/docs`

---

### 5. Set Up & Start the Frontend

```bash
# From the project root (not python-qa-assistant/)
cd ..

# Install Node dependencies
npm install

# Start the Vite dev server
npm run dev
```

The web UI starts at **`http://localhost:3000`**.

---

## API Reference

### `GET /api/health`
Returns system status and vector store connectivity.

```bash
curl http://localhost:8000/api/health
```
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "vector_store": "connected"
}
```

---

### `POST /api/ask`
Submit a Python question. Returns a grounded answer with source references and agent step audit.

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I read a CSV file using pandas?"}'
```
```json
{
  "answer": "Use `pd.read_csv()` to load a CSV:\n\n```python\nimport pandas as pd\ndf = pd.read_csv('file.csv')\n```",
  "sources": [
    { "title": "How to read CSV in pandas?", "score": 0.96, "snippet": "..." }
  ],
  "steps_taken": ["classify_question", "retrieve_context", "generate_answer"],
  "model_used": "gemini-1.5-flash",
  "processing_time_ms": 380
}
```

---

### `POST /api/ask/stream`
Same as `/api/ask` but streams tokens in real-time via Server-Sent Events.

```bash
curl -N -X POST http://localhost:8000/api/ask/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the GIL?"}'
```

---

### `POST /api/ask/external`
Route an off-topic question to an external LLM provider using a custom API key.

```bash
curl -X POST http://localhost:8000/api/ask/external \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain neural networks",
    "provider": "OpenAI",
    "model": "gpt-4o-mini",
    "api_key": "sk-..."
  }'
```

---

### `GET /api/stats`
Returns corpus metadata (document count, vector store size).

---

## Running Tests

```bash
cd python-qa-assistant
pytest tests/ -v --cov=app
```

Benchmark results for 8 diverse Python developer queries are in `notebooks/test_results.ipynb`.  
Average response time: **250–600ms** per query.

---

## Docker

Run the full stack as a portable container:

```bash
cd python-qa-assistant
docker-compose up --build
```

Maps the FastAPI server to port `8000` with volumes for `chroma_db/` and `data/` persistence.

---

## Deployment

### Render
Deploy the backend using the included `render.yaml`:
- Set `OPENAI_API_KEY` / `GEMINI_API_KEY` as environment secrets in the Render dashboard.
- The service will auto-build from the `python-qa-assistant/` subdirectory.

### Railway / Fly.io
1. Connect the GitHub repository.
2. Set the root directory to `python-qa-assistant/`.
3. Set `PORT=8000` and add your API key secrets.
4. Deploy.

---

## Scaling Considerations

| Concern | Approach |
|---|---|
| **Concurrency** | Run multiple Uvicorn workers: `uvicorn app.main:app --workers 4` |
| **Caching** | Add Redis (TTL 1h) to short-circuit repeat queries |
| **Vector Store** | Migrate from local ChromaDB to Qdrant or `pgvector` for horizontal scale |
| **Cost per query** | ~$0.002 (classify + embed + generate @ gpt-4o-mini rates) |

---

## License

MIT — see [LICENSE](LICENSE) for details.
