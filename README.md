# The Lenny Growth Assistant

> An evidence-grounded AI research workspace and deliverable engine querying Lenny Rachitsky's podcast and newsletter archive. Built for product managers, growth teams, and founders.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791.svg)](https://www.postgresql.org/)
[![Ollama](https://img.shields.io/badge/Ollama-qwen2.5%3A3b-black.svg)](https://ollama.ai/)
[![Tests](https://img.shields.io/badge/tests-17%20passed-brightgreen.svg)]()

---

## 1. Product Overview

**The Lenny Growth Assistant** is an end-to-end full-stack AI research workspace built for Oogway Labs. It addresses the common pitfalls of general-purpose LLMs (hallucinations, fabricated podcast episodes, and lack of accountability) by enforcing:
1. **Verifiable Evidence Grounding:** Answers are synthesized strictly from ingested podcast and newsletter transcript chunks.
2. **Clickable Citations:** Every claim is backed by source cards detailing document titles, episode links, relevance match percentages, and verbatim transcript excerpts.
3. **Transparent Abstention Gate:** Queries outside the ingested corpus (e.g., astrophysics, sports) trigger an immediate, polite refusal to speculate, with suggested topics instead.
4. **Ship 30 for 30 Skill:** Synthesizes complex growth concepts into ~1,250-word Atomic Essays following Nicolas Cole and Dickie Bush's digital writing methodology.
5. **Sandboxed Artifact Viewer:** Renders generated HTML/CSS deliverables and growth experiment briefs in a secure iframe (`sandbox="allow-scripts"`), sanitized against cross-site scripting and unauthorized storage access.
6. **Zero-Paid-API Local First Demo:** Runs 100% locally on Windows using PostgreSQL 18 and Ollama with `qwen2.5:3b`.

---

## 2. Key Features

- **Multi-Turn Persistent Sessions:** Multi-turn conversational memory stored in PostgreSQL with strict session isolation.
- **Model Router & SDK Integration:** Real, Identifiable integration of the **Pi Coding Agent SDK** (`pi-coding-agent`), the **Anthropic Claude Agent SDK** (`claude-agent-sdk` / `anthropic`), local **Ollama**, and **OpenAI**. Switch providers dynamically in the UI without editing code.
- **Hybrid Retrieval Engine:** PostgreSQL Full-Text Search with GIN indexing (`to_tsvector` and `ts_rank_cd`) combined with lexical keyword density scoring.
- **Secure Deliverable Pipeline:** Create landing page prototypes, growth experiment plans, and product brief templates viewable side-by-side with chat.
- **Editorial UI Design:** Calm, typography-driven editorial canvas featuring *Newsreader* serif headings, *Plus Jakarta Sans* UI, and *JetBrains Mono* code.

---

## 3. Architecture Summary

```
[ Frontend: React + TS + Vite ] ──(Proxy :5173 -> :8000)──► [ FastAPI 1.0 ]
                                                                 │
                   ┌─────────────────────────────────────────────┤
                   ▼                                             ▼
       [ Ingestion & Retrieval ]                       [ ModelRouter ]
  • Overlapping Chunking (700c/150o)             • Ollama (qwen2.5:3b)
  • PostgreSQL GIN FTS + Lexical                 • Pi Coding Agent SDK
  • Abstention Threshold Gate (0.05)             • Anthropic Claude
                   │                             • OpenAI GPT-4o-mini
                   ▼                                             │
       [ PostgreSQL 18 Database ] ◄──────────────────────────────┘
  • Conversations, Messages, Citations,
    Source Documents, Chunks, Artifacts
```

For full details, see [`docs/architecture.md`](docs/architecture.md), [`docs/PRD.md`](docs/PRD.md), and [`docs/design.md`](docs/design.md).

---

## 4. Prerequisites

- **OS:** Windows 10/11 (or macOS / Linux)
- **Python:** 3.11 (virtual environment at `backend/.venv`)
- **Node.js:** v18+ (tested on Node v24.14 / npm 10.9)
- **PostgreSQL:** Version 15+ (tested on PostgreSQL 18 on port 5432)
- **Ollama:** Installed and running on `http://localhost:11434` with `qwen2.5:3b` pulled

---

## 5. Quick Start (Windows PowerShell)

### Method A: One-Command Startup
In the root directory of the project, run:
```powershell
.\run.ps1
```
This script automatically verifies PostgreSQL, checks Ollama, ingests transcripts, starts the backend on port 8000, starts the frontend on port 5173, and launches your browser.

---

### Method B: Manual Step-by-Step Setup

#### 1. Configure Environment
Copy the example environment template:
```powershell
Copy-Item .env.example .env
```
Ensure `.env` matches your local database and provider settings:
```ini
DATABASE_URL=postgresql+psycopg://postgres:Anu1116@localhost:5432/lenny_growth
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
```

#### 2. Initialize Database & Ingest Transcripts
```powershell
$env:PYTHONPATH="backend"
& .\backend\.venv\Scripts\python.exe -m app.retrieval.ingest --dir transcripts
```
Output confirms 5 source files and 32 chunks ingested with GIN indexing.

#### 3. Start Backend Server
```powershell
$env:PYTHONPATH="backend"
& .\backend\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at: `http://127.0.0.1:8000/docs`  
Health Check: `http://127.0.0.1:8000/health`

#### 4. Start Frontend
In a second PowerShell terminal:
```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 6. How to Run Automated Tests

Run the complete 17-test automated pytest suite:
```powershell
$env:PYTHONPATH="backend"
& .\backend\.venv\Scripts\pytest.exe backend/tests -v
```

Run frontend typechecking and production build:
```powershell
cd frontend
npm run build
```

---

## 7. Model Providers & SDK Integrations

### Local Ollama (Default Demo Mode)
- Base URL: `http://localhost:11434`
- Model: `qwen2.5:3b`
- Works 100% offline with zero cloud API keys.

### Pi Coding Agent SDK (`pi-agent`)
- Package: `pi-coding-agent` (v0.6.0)
- Identifiable integration in `backend/app/agents/pi_agent_provider.py`.
- Select `PI-AGENT` from the UI model dropdown or set `LLM_PROVIDER=pi-agent`.

### Anthropic Claude & Claude Agent SDK
- Package: `claude-agent-sdk` (v0.2.165) and `anthropic` (v1.13.0).
- Identifiable integration in `backend/app/agents/anthropic_provider.py`.
- Set `ANTHROPIC_API_KEY=your_key_here` in `.env`.

### OpenAI
- Package: `openai` (v3.28.0).
- Identifiable integration in `backend/app/agents/openai_provider.py`.
- Set `OPENAI_API_KEY=your_key_here` in `.env`.

---

## 8. REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check for PostgreSQL, active provider, and provider readiness |
| `GET` | `/api/providers` | Lists all model providers, models, and live connection status |
| `GET` | `/api/conversations` | Lists recent conversation sessions |
| `POST` | `/api/conversations` | Creates a new isolated conversation session |
| `GET` | `/api/conversations/{id}` | Fetches conversation message history, citations, and artifacts |
| `DELETE` | `/api/conversations/{id}` | Deletes a conversation session |
| `POST` | `/api/chat` | Processes a query with retrieval, citations, and abstention enforcement |
| `POST` | `/api/skills/ship-30-for-30` | Generates an evidence-grounded ~1,250-word Atomic Essay |
| `POST` | `/api/artifacts` | Generates and sanitizes HTML or Markdown deliverables |
| `GET` | `/api/artifacts/{id}` | Fetches an artifact deliverable by ID |
| `GET` | `/api/sources` | Lists all ingested transcript documents and chunk counts |
| `POST` | `/api/ingestion` | Triggers file or directory ingestion |

---

## 9. Troubleshooting & Known Limitations

1. **Local Ollama Inference Speed:** Local CPU/GPU generation of long essays takes 30–90 seconds. A 180s HTTP timeout and frontend loading indicator are configured to prevent dropped requests.
2. **PostgreSQL Service on Windows:** Ensure service `postgresql-x64-18` is running (`Get-Service *postgres*`). If stopped, start via Services manager or PowerShell as Administrator (`Start-Service postgresql-x64-18`).
3. **CORS Configuration:** If connecting from another host, add the host URL to `CORS_ORIGINS` in `.env`.

---

## 10. Public Submission Handoff

When authorized to push to public GitHub, run:
```powershell
git add .
git commit -m "feat: complete The Lenny Growth Assistant production take-home implementation"
git branch -M main
git remote add origin https://github.com/<YOUR_USER>/lenny-growth-assistant.git
git push -u origin main
```
See [`docs/demo-and-test-plan.md`](docs/demo-and-test-plan.md) for the 2–3 minute video demo recording script and checklist.
