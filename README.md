# 🧠 End-to-End RAG (Retrieval-Augmented Generation) System

A robust, production-ready Retrieval-Augmented Generation (RAG) system built with **FastAPI**, **PostgreSQL + pgvector**, and **Google Gemini**, complete with an interactive frontend dashboard.

---

## 🌟 Overview

This repository provides an end-to-end RAG architecture consisting of:
1. **Ingestion Pipeline**: Automated document ingestion, smart chunking with customizable size & overlap, vector embedding generation, and persistent storage in PostgreSQL with `pgvector`.
2. **Query Pipeline**: Semantic search using vector similarity, contextual chunk retrieval, prompt construction, and answer generation.
3. **FastAPI Backend**: Asynchronous REST API serving file upload, processing, and query endpoints.
4. **Interactive UI**: Clean, responsive frontend for uploading documents, running queries, and viewing latency benchmarks.

---

## 🏗️ System Architecture

```
[User Document (PDF/Text)]
          │
          ▼
┌─────────────────────────────────┐
│       Ingestion Pipeline        │
│ 1. Text Loader                  │
│ 2. Text Chunker (Sliding Window)│
│ 3. Embedder (Gemini API)        │
└─────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│     PostgreSQL + pgvector       │
│  (Vector Dimension: 1536)       │
└─────────────────────────────────┘
          ▲
          │ Similarity Retrieval (Top-K Chunks)
          │
┌─────────────────────────────────┐
│         Query Pipeline          │
│ 1. Query Embedder               │
│ 2. Vector Search                │
│ 3. Contextual Prompt Assembly   │
│ 4. LLM Generation               │
└─────────────────────────────────┘
          ▲
          │
[FastAPI REST API / Web Frontend]
```

---

## 📂 Project Structure

```
├── Ingestion_Pipeline/
│   ├── chunking.py           # Text chunking with sliding window & overlap
│   ├── embeddings.py         # Embedding generation
│   ├── textloader.py         # Document text extraction
│   ├── vectore_store.py      # PostgreSQL + pgvector table setup and insertion
│   └── main.py               # Ingestion pipeline entry point
├── Query_Pipeline/
│   ├── chunk_retriver.py     # Semantic chunk retrieval using pgvector
│   ├── query_embedder.py     # Query embedding generator
│   ├── llm_answer.py         # Answer generation with LLM & chat history
│   └── main.py               # Query pipeline CLI runner
├── Librarie/
│   ├── prompt_library.py     # Curated prompt templates
│   └── system_instruction_library.py # System instructions for factual Q&A
├── backend/
│   ├── main.py               # FastAPI application & REST endpoints
│   ├── utilities.py          # File path & system helpers
│   └── uploaded_files/       # Storage for incoming uploaded documents
├── frontend/
│   ├── index.html            # Web dashboard interface
│   ├── style.css             # UI styling
│   └── app.js                # Frontend API client logic
├── .env.example              # Template for environment variables
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+**
- **PostgreSQL** with the `pgvector` extension installed.
- **Google Gemini API Key** (or local LLM provider).

### 2. Setup PostgreSQL & pgvector
Make sure your PostgreSQL server is running, then enable pgvector on your database:
```sql
CREATE DATABASE "TASK";
\c "TASK"
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/JainKushal556/rag-system.git
cd rag-system

# Create and activate virtual environment
python -m venv .venv
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```
Edit `.env`:
```env
GEMINIAPI_KEY=your_gemini_api_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=TASK
DB_USER=postgres
DB_PASSWORD=your_password
```

---

## ⚡ Running the Application

### Start the FastAPI Backend
```bash
uvicorn backend.main:app --reload
```
The API server will run at `http://127.0.0.1:8000`.
Interactive API docs (Swagger) available at `http://127.0.0.1:8000/docs`.

### Run Ingestion Pipeline Directly (CLI)
```bash
python -m Ingestion_Pipeline.main
```

### Run Query Pipeline Directly (CLI)
```bash
python -m Query_Pipeline.main
```

### Launch Web Frontend
Open `frontend/index.html` directly in your browser or serve it with any static server:
```bash
cd frontend
python -m http.server 5500
```
Visit `http://localhost:5500` to interact with the RAG interface.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check endpoint |
| `POST` | `/uploadfile` | Uploads document (PDF/TXT), parses, chunks, and indexes embeddings into `pgvector` |
| `POST` | `/query` | Accepts question, retrieves relevant context, and returns answer with elapsed latency |

---

## 🛡️ License

Distributed under the MIT License. Feel free to use and adapt for your own projects!
