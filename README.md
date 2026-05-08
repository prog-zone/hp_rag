# Harry Potter RAG

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688.svg?logo=fastapi)
![Qdrant](https://img.shields.io/badge/Qdrant-vector_search-red.svg)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A RAG API built on top of all 7 Harry Potter books. Ask it anything about the wizarding world and get answers grounded strictly in the books with citations back to the exact book and page.

Built as a side project to explore building a clean, production-style RAG pipeline with query rewriting, hybrid retrieval, and cross-encoder reranking.

---

## How the RAG Pipeline Works

```
User Query
    │
    ▼
Query Rewriting  ← GPT-4o-mini resolves aliases ("Padfoot" → "Sirius Black"),
    │               fixes spell names, extracts book filters if mentioned
    ▼
Dense Vector Search (Qdrant)
    │   Embedding model: text-embedding-3-small (OpenAI)
    │   Top-30 candidates, cosine similarity threshold: 0.30
    │   Optional filter: narrows search to specific books
    ▼
Cross-Encoder Reranking  ← BAAI/bge-reranker-base (HuggingFace)
    │                       Top-5 chunks selected
    ▼
GPT-4o-mini
    │   Strict prompt: cite book + page, never use outside knowledge
    ▼
Response with sources (book title, page, similarity score)
```

**Why query rewriting?** Names like "Padfoot", "He-Who-Must-Not-Be-Named", or "Moony" won't match their vector representations well. Rewriting to canonical names before embedding significantly improves retrieval accuracy.

**Why reranking?** Dense vector search optimizes for broad similarity. The cross-encoder reranker scores each chunk against the query directly, catching cases where the top vector matches aren't actually the most relevant passages.

---

## Tech Stack

| | |
|---|---|
| **API** | FastAPI (async) |
| **Vector DB** | Qdrant |
| **Embeddings** | OpenAI `text-embedding-3-small` |
| **Reranker** | HuggingFace `BAAI/bge-reranker-base` |
| **LLM** | GPT-4o-mini |
| **RAG framework** | LangChain |
| **Database** | PostgreSQL + SQLModel + Alembic |
| **UI** | Streamlit |
| **Infrastructure** | Docker Compose |

---

## Data Model

```
Session (browser session, cookie-based)
 └── Chats (threads)
      └── Messages (user + assistant turns)
```

The one-shot `/query` endpoint is stateless. The threaded chat endpoints persist full conversation history to Postgres.

---

## Project Structure

```
app/
  api/          # FastAPI routes (one-shot query + threaded chat)
  core/         # Config, Postgres + Qdrant clients, logging
  models/       # SQLModel table definitions (Session, Chat, Message)
  schemas/      # Pydantic request/response schemas
  services/     # RAG pipeline (rag_service.py, vector_service.py)
ingestion/      # PDF loading, chunking, and Qdrant ingestion pipeline
data/           # Harry Potter PDFs (books 1–7)
streamlit_app.py
```

---

## Running Locally

**Prerequisites:** Docker, Python 3.11+, an OpenAI API key.

```bash
git clone https://github.com/yourusername/hp-rag.git
cd hp-rag
cp .env.example .env  # fill in OPENAI_API_KEY, POSTGRES_* credentials
```

Start infrastructure:
```bash
docker-compose up -d
# Starts: PostgreSQL, Qdrant
```

Run the API:
```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Run the ingestion pipeline (only needed once):
```bash
python -m ingestion.pipeline
```

Run the Streamlit UI (optional):
```bash
streamlit run streamlit_app.py
```

Docs at `http://localhost:8000/docs`

---

## API

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/query` | One-shot question answering |
| `GET` | `/api/v1/threads` | List chat threads for a session |
| `POST` | `/api/v1/threads` | Create a new chat thread |
| `GET` | `/api/v1/threads/{id}/messages` | Get message history |
| `POST` | `/api/v1/threads/{id}/query` | Ask a question within a thread |
| `GET` | `/healthcheck` | Health check |

The `/query` response includes the answer, source citations (book + page + similarity score), response latency, and chunks used.

---

## License

MIT
