# 🐍 Python Q&A Assistant

> A production-grade, AI-powered assistant for Python programming questions — grounded in real Stack Overflow answers, not hallucinations.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_Pipeline-FF6B6B?style=flat)](https://github.com/langchain-ai/langgraph)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange?style=flat)](https://www.trychroma.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 About the Project

The **Python Q&A Assistant** is a full-stack intelligent question-answering system designed specifically for Python developers. It combines **Retrieval-Augmented Generation (RAG)** with a **LangGraph agentic pipeline** to deliver precise, code-rich answers backed by a curated Stack Overflow corpus — eliminating the hallucination problem common in vanilla LLM responses.

When you ask a Python question, the system:
1. **Classifies** the question to determine if it's Python-related
2. **Retrieves** the most semantically similar Stack Overflow Q&A pairs from ChromaDB
3. **Generates** a grounded, context-aware answer using your configured LLM provider
4. **Streams** the response token-by-token back to the browser in real-time

Off-topic questions are detected early and can optionally be routed to an external LLM with a one-click workflow.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Semantic Search** | Embeds questions and retrieves top-k matches from a Stack Overflow Python corpus using ChromaDB |
| 🤖 **LangGraph Agent** | Multi-node StateGraph: classify → retrieve → generate → fallback, with full step audit |
| 🌐 **Multi-Provider LLM** | Plug in Google Gemini or OpenAI — switch providers without touching code |
| ⚡ **Streaming Responses** | Server-Sent Events (SSE) stream tokens in real time for a ChatGPT-like experience |
| 💻 **Premium Web UI** | Dark-mode interface with source cards, live agent workflow visualizer, and a system logs panel |
| ⚙️ **Settings Drawer** | Configure LLM provider, model, API key, and temperature directly from the UI |
| 🚫 **Off-topic Routing** | Non-Python questions are caught and optionally answered by an external LLM |
| 📊 **Stats Endpoint** | Live corpus metadata — document count, vector store size |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Web Browser (UI)                       │
│           Vanilla HTML / CSS / JavaScript                │
│     Dark mode · Source cards · Agent workflow viz        │
└───────────────────────────┬──────────────────────────────┘
                            │  HTTP / SSE
                            ▼
┌──────────────────────────────────────────────────────────┐
│          Express + Vite Dev Server  (port 3000)          │
│   Hot Module Replacement in dev · Proxies /api/* to      │
│   FastAPI in prod · Direct Gemini/OpenAI for /external   │
└───────────────────────────┬──────────────────────────────┘
                            │  REST proxy → FastAPI
                            ▼
┌──────────────────────────────────────────────────────────┐
│            FastAPI + Uvicorn  (port 8000)                │
│                  app/api/routes.py                       │
│   /health  /ask  /ask/stream  /ask/external  /stats      │
└───────────────────────────┬──────────────────────────────┘
                            │  ainvoke / astream
                            ▼
┌──────────────────────────────────────────────────────────┐
│              LangGraph Agent  (StateGraph)               │
│                                                          │
│   classify_question_node                                 │
│          │                                               │
│     Python? ──Yes──▶ retrieve_context_node               │
│          │                   │                           │
│         No                   ▼                           │
│          │          generate_answer_node                 │
│          ▼                   │                           │
│    fallback_node             ▼                           │
│          │                [END]                          │
│          ▼                                               │
│       [END]                                              │
└───────────────────────────┬──────────────────────────────┘
                            │  similarity search
                            ▼
┌──────────────────────────────────────────────────────────┐
│              ChromaDB  Vector Store  (local)             │
│         Stack Overflow Python Q&A corpus                 │
│   Embeddings: sentence-transformers / OpenAI Ada         │
└──────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Vanilla HTML5, CSS3 (custom properties + dark mode), JavaScript ES2022 |
| **Dev Server** | Node.js 18+, Express, Vite (HMR in development) |
| **Backend API** | Python 3.11+, FastAPI, Uvicorn (ASGI) |
| **Agent Orchestration** | LangGraph `StateGraph`, LangChain LCEL |
| **Vector Store** | ChromaDB (local, serverless, zero infrastructure) |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` (default) · OpenAI `text-embedding-3-small` (optional) |
| **LLM Providers** | Google Gemini (`gemini-1.5-flash`, `gemini-pro`) · OpenAI (`gpt-4o`, `gpt-4o-mini`) |
| **HTTP Client** | `httpx` (async, streaming-capable) |
| **Data Source** | Stack Overflow Python Q&A (Kaggle public dataset) |

---

## 📂 Repository Structure

```
Python-Q-A-Assistant/
├── index.html                    # Main frontend entry point (served by Vite)
├── frontend/
│   └── index.html                # Mirror of the frontend for production builds
├── server.ts                     # Express + Vite dev server with API proxy
├── package.json                  # Node.js dependencies & npm scripts
├── vite.config.ts                # Vite bundler configuration
├── tsconfig.json                 # TypeScript configuration
├── .env.example                  # Environment variables template
│
└── python-qa-assistant/          # Python FastAPI backend
    ├── app/
    │   ├── main.py               # FastAPI app factory, CORS, middleware
    │   ├── api/
    │   │   └── routes.py         # /health, /ask, /ask/stream, /ask/external, /stats
    │   ├── agent/
    │   │   ├── graph.py          # LangGraph StateGraph definition
    │   │   ├── nodes.py          # classify, retrieve, generate, fallback nodes
    │   │   └── state.py          # AgentState TypedDict
    │   ├── rag/
    │   │   ├── pipeline.py       # LangChain LCEL RAG chain
    │   │   ├── retriever.py      # ChromaDB retriever setup
    │   │   └── embeddings.py     # Embedding model loader
    │   ├── models/
    │   │   └── schemas.py        # Pydantic request/response schemas
    │   ├── core/
    │   │   ├── config.py         # App settings (pydantic-settings)
    │   │   └── llm.py            # LLM client factory (Gemini / OpenAI)
    │   └── ingestion/            # Data ingestion pipeline
    ├── scripts/
    │   ├── download_data.py      # Download Stack Overflow dataset from Kaggle
    │   └── ingest.py             # Embed documents and populate ChromaDB
    ├── tests/                    # Pytest test suite
    ├── notebooks/                # Evaluation notebooks & benchmark results
    ├── requirements.txt          # Python dependencies
    ├── docker-compose.yml        # Docker Compose for containerized deployment
    └── render.yaml               # Render.com deployment configuration
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- An API key for **Google Gemini** or **OpenAI** (at least one required)
- Kaggle credentials (optional — a mock dataset is auto-generated if absent)

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

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# Install Python dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env and fill in your API keys
```

**`.env` configuration:**
```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
LLM_PROVIDER=google             # google | openai
LLM_MODEL=gemini-1.5-flash
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

### 3. Download & Index the Dataset

```bash
# Download Stack Overflow Python Q&A corpus (Kaggle)
python scripts/download_data.py

# Embed documents and index them into ChromaDB
python scripts/ingest.py
```

> **Note:** If Kaggle credentials are not configured, a mock dataset is generated automatically so you can still run and evaluate the full pipeline.

---

### 4. Start the Backend Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- FastAPI server: `http://localhost:8000`
- Interactive API docs (Swagger UI): `http://localhost:8000/docs`

---

### 5. Set Up & Start the Frontend

```bash
# From the project root (Python-Q-A-Assistant/)
cd ..

npm install
npm run dev
```

The web UI is served at **`http://localhost:3000`**.

---

## 📡 API Reference

### `GET /api/health`
Returns server status and vector store connectivity.

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
Same as `/api/ask` but streams tokens in real-time via **Server-Sent Events (SSE)** — ideal for the live chat UI.

```bash
curl -N -X POST http://localhost:8000/api/ask/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the GIL in Python?"}'
```

---

### `POST /api/ask/external`
Route a question to an external LLM provider (e.g. for off-topic queries) with a custom API key.

```bash
curl -X POST http://localhost:8000/api/ask/external \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain how neural networks work",
    "provider": "OpenAI",
    "model": "gpt-4o-mini",
    "api_key": "sk-..."
  }'
```

---

### `GET /api/stats`
Returns corpus metadata including indexed document count and vector store size.

---

## 🧪 Running Tests

```bash
cd python-qa-assistant
pytest tests/ -v --cov=app
```

Benchmark results across 8 diverse Python developer queries are available in `notebooks/test_results.ipynb`.  
Average response time: **250–600 ms** per query.

---

## 🐳 Docker

Run the full backend stack as a portable container:

```bash
cd python-qa-assistant
docker-compose up --build
```

This maps FastAPI to port `8000` and mounts `chroma_db/` and `data/` as persistent volumes.

---

## ☁️ Deployment

### Render
The project includes a `render.yaml` for zero-config deployment on [Render](https://render.com):

1. Connect this GitHub repository in the Render dashboard.
2. Add `OPENAI_API_KEY` and/or `GEMINI_API_KEY` as **Environment Secrets**.
3. The service auto-builds from the `python-qa-assistant/` subdirectory.
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Railway / Fly.io
1. Connect the GitHub repository.
2. Set the root directory to `python-qa-assistant/`.
3. Add `PORT=8000` and your API key secrets.
4. Deploy — no other configuration needed.

---

## 📈 Scaling Considerations

| Concern | Recommended Approach |
|---|---|
| **Concurrency** | `uvicorn app.main:app --workers 4` for multi-process scaling |
| **Response Caching** | Add Redis with TTL ~1h to short-circuit repeated identical queries |
| **Vector Store** | Migrate from local ChromaDB → Qdrant Cloud or `pgvector` for horizontal scale |
| **Embedding Speed** | Switch to OpenAI `text-embedding-3-small` for GPU-free, fast cloud embeddings |
| **Estimated Cost** | ~$0.002 per query (classify + embed + generate at `gpt-4o-mini` rates) |

---

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.
