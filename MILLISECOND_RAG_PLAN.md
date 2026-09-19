# ⚡ Millisecond Latency RAG Migration Plan (Voice Receptionist & SaaS Ready)

This document outlines the architectural blueprint, component-by-component migration, unit economics, and step-by-step execution to transition the RAG system from a multi-second delay (~3–4 seconds) down to **millisecond response times (~150ms–250ms)**.

---

## 1. Latency Benchmark: Current vs Target Architecture

```
CURRENT ARCHITECTURE (~2.5s - 4.0s Total Latency)
[User Query] 
     │──► 1. Google Gemini Embedder (Network Round-Trip)  [~400ms - 600ms]
     │──► 2. PostgreSQL Sequential Scan (No Index)        [~40ms - 80ms]
     │──► 3. Long Conversational Prompt Assembly           [~5ms]
     └──► 4. Gemini Flash Non-Streaming Completion       [~2000ms - 3000ms wait]
                                                        ═════════════════════════
                                                        Total: ~2.5s - 4.0s (Unusable for Calling)

TARGET MILLISECOND ARCHITECTURE (~150ms - 250ms Total Latency)
[User Query]
     │──► 1. Local CPU Micro-Embedder (FastEmbed / ONNX)  [~8ms - 15ms]
     │──► 2. PostgreSQL HNSW Index Search (Top 2 Chunks)  [~2ms - 4ms]
     │──► 3. Concise "Spoken-Style" Prompt Construction   [~1ms]
     └──► 4. Token Streaming via Groq LPU / Local Ollama  [~100ms - 150ms TTFT]
                                                        ═════════════════════════
                                                        First Word Reaches Caller: < 180ms ⚡
```

---

## 2. Component Migration Breakdown

| # | Component | Current State | Target State | Primary Benefit |
|---|---|---|---|---|
| **1** | **Query Embedder**<br>`Query_Pipeline/query_embedder.py` | Google Gemini API over HTTPS (`gemini-embedding-001`) | **FastEmbed / ONNX Runtime** (`bge-small-en-v1.5`) running locally on CPU | Eliminates **400ms–600ms** external network latency. Cost = $0. |
| **2** | **Vector Search**<br>`Query_Pipeline/chunk_retriver.py` | Sequential table scan: `ORDER BY embedding <=> %s::vector LIMIT 2` | **HNSW Index** (`USING hnsw (embedding vector_cosine_ops)`) | Search time drops from ~50ms to **~2ms**. Limits context strictly to 1–2 chunks. |
| **3** | **Prompt Builder**<br>`Librarie/prompt_library.py` | Multi-paragraph instructions with strict formatting rules | **Voice-optimized concise prompt**: 1–2 spoken sentences, no markdown, no lists | Minimizes prompt evaluation tokens, reducing Time-To-First-Token (TTFT). |
| **4** | **LLM Engine**<br>`Query_Pipeline/llm_answer.py` | Non-streaming call (`client.aio.interactions.create`) waiting for entire text | **Token Streaming** (`stream=True`) with **Groq LPU** (`llama-3.1-8b-instant`) or **Ollama** (`qwen2.5:1.5b`) | First word emitted in **~100ms** instead of waiting 3000ms. |
| **5** | **API & Transport**<br>`backend/main.py` | Standard HTTP POST returning static JSON block `{"answer": ...}` | **Server-Sent Events (SSE)** via FastAPI `StreamingResponse` | Yields tokens directly to the client/TTS engine in real-time. |
| **6** | **Frontend Display**<br>`frontend/app.js` | Spinner waiting for complete JSON promise resolution | **ReadableStream reader** (`response.body.getReader()`) | Words render token-by-token dynamically on screen. |

---

## 3. SaaS Unit Economics (Voice Receptionist Calling System)

Cost calculation based on an average **5-minute customer phone call** (approx. 12 conversational turns):

| Component | Provider / Tech | Unit Cost | Cost per 5-Minute Call |
|---|---|---|---|
| **Embedding Generation** | Local CPU (FastEmbed) | Free (Runs in backend) | **$0.000** |
| **Vector Database** | PostgreSQL + `pgvector` (Neon / Supabase) | Serverless pool | **~$0.001** |
| **LLM Inference** | Groq (`llama-3.1-8b-instant`) | $0.05 / 1M input tokens<br>$0.08 / 1M output tokens | **~$0.0005** |
| **Speech-To-Text (STT)** | Deepgram Nova-2 (WebSocket) | $0.0043 / minute | **~$0.021** |
| **Text-To-Speech (TTS)** | Cartesia Sonic / Deepgram Aura | $0.005 / 1K characters | **~$0.015** |
| **Telephony Line** | Twilio / Telnyx SIP Trunk | $0.012 / minute | **~$0.060** |
| **TOTAL COST TO HOST** | | | **~$0.098 (~10¢ per call)** |

### SaaS Margins & Pricing Strategy:
* **Standard SaaS Charge to Businesses:** $0.50 – $1.00 per call minute (or $99/month for 200 minutes).
* **Cost of 200 Minutes:** ~$3.90.
* **Monthly Revenue:** $99.00.
* **Gross Margin:** **~96% Profit Margin**.

---

## 4. Step-by-Step Implementation Roadmap

### Phase 1: Streaming Generation (Immediate Speed Win)
1. **[llm_answer.py](file:///e:/Pyhton/RAG/Query_Pipeline/llm_answer.py)**:
   - Implement `async def generate_answer_stream(query, chunks)` yielding tokens using `stream=True`.
   - Add Groq API client support (`groq` package) with fallback to local Ollama.
2. **[backend/main.py](file:///e:/Pyhton/RAG/backend/main.py)**:
   - Convert `POST /query` to stream tokens via `StreamingResponse(stream_generator(), media_type="text/event-stream")`.
3. **[frontend/app.js](file:///e:/Pyhton/RAG/frontend/app.js)**:
   - Update `sendQuestion()` to consume chunked stream using `response.body.getReader()`.

### Phase 2: Local Micro-Embedding & HNSW Indexing
1. **Local Embeddings**:
   - Replace remote Gemini embedding calls with `fastembed` (`FastEmbed.from_model("BAAI/bge-small-en-v1.5")`).
   - Generates query vectors in **< 15ms** on CPU.
2. **Database HNSW Index**:
   - Execute in PostgreSQL:
     ```sql
     CREATE INDEX IF NOT EXISTS doc_embeddings_hnsw_idx 
     ON document_embeddings 
     USING hnsw (embedding vector_cosine_ops) 
     WITH (m = 16, ef_construction = 64);
     ```

### Phase 3: Semantic Caching (Sub-5ms Repetitive Answers)
1. Add an in-memory cosine cache dictionary:
   - If incoming query has similarity `> 0.95` with a previously cached question, return the answer instantly in **2ms** without querying the LLM.

### Phase 4: Telephony & Voice Pipeline (When Ready for Calls)
1. Integrate **LiveKit Agents** or **Pipecat**:
   - Audio WebSocket from Twilio $\rightarrow$ Deepgram STT $\rightarrow$ RAG Pipeline $\rightarrow$ Cartesia TTS $\rightarrow$ Caller.
   - Built-in interruption handling (turn detection).
