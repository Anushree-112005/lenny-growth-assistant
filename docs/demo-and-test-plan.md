# Demo Script & Manual QA Test Plan — The Lenny Growth Assistant

This guide provides a structured 2–3 minute video presentation script and a step-by-step manual quality assurance checklist for evaluating **The Lenny Growth Assistant**.

---

## Part 1: 2–3 Minute Video Demo Script

### Setup Before Recording
1. Open PowerShell and start the backend:
   ```powershell
   $env:PYTHONPATH="backend"
   .\backend\.venv\Scripts\uvicorn.exe app.main:app --port 8000
   ```
2. In a second terminal, start the frontend:
   ```powershell
   cd frontend
   npm run dev
   ```
3. Open `http://localhost:5173` in your browser.
4. Camera: ON (as required by Oogway Labs submission guidelines).

---

### Step-by-Step Script

| Timestamp | Screen Action | Spoken Narration |
|---|---|---|
| **0:00 - 0:25** | Show browser at `http://localhost:5173`. Point out sidebar, model pill (`Ollama: qwen2.5:3b`), and calm editorial canvas. | *"Hi! I'm presenting The Lenny Growth Assistant for Oogway Labs. This is a production-minded AI research workspace that ingests Lenny Rachitsky's podcast and newsletter archive, performs grounded retrieval with PostgreSQL, enforces strict abstention, produces Ship 30 for 30 essays, and renders deliverables in a secure Artifact Viewer. We're running 100% locally on Windows using PostgreSQL 18 and Ollama with qwen2.5:3b."* |
| **0:25 - 0:50** | Click the recommendation chip: *"How does Elena Verna explain B2B PLG vs sales-assisted models?"* or submit the question. | *"First, let's ask about B2B Product-Led Growth. The assistant queries PostgreSQL using full-text and lexical search, extracts top evidence chunks, and passes them to the local model. Notice the answer is strictly grounded in Elena Verna's frameworks: PLG as an end-user adoption engine and Product-Led Sales as the enterprise monetizer."* |
| **0:50 - 1:10** | Expand the **Verified Citations** drawer beneath the message. Hover over relevance score and excerpt. | *"Crucially, every claim has verifiable citations. Expanding the citation card reveals the exact document title, episode link, match percentage, and the verbatim transcript excerpt. Nothing is fabricated or hallucinatory."* |
| **1:10 - 1:30** | Type an unsupported query in the composer: *"What is quantum gravity in black hole astrophysics?"* Press Enter. | *"Now let's test grounding integrity. I'll ask an astrophysics question completely outside our ingested corpus. Watch how the assistant immediately triggers our abstention gate: it transparently states that the transcripts lack sufficient evidence, avoids making up facts, and suggests valid growth topics instead."* |
| **1:30 - 1:55** | Click the **Ship 30 Essay** button in the header. Select *"Self-sustaining product-led growth loops vs linear funnels"*. | *"Next, we showcase the dedicated Ship 30 for 30 skill. This synthesizes transcript evidence into an authoritative, ~1,250-word Atomic Essay following Nicolas Cole and Dickie Bush's methodology: 1-3-1 hook, central thesis, narrative sections with skimmable headings, practical action steps, and citation footnotes."* |
| **1:55 - 2:20** | Click **"Inspect in Artifact Viewer"** or click **"Create Landing Page Artifact"** in chat. Toggle between Preview and Source Code. | *"Now let's view the deliverable in the Artifact Viewer. For security, HTML is rendered inside an isolated iframe with sandbox allow-scripts and server-side sanitization, preventing any access to cookies or session credentials. Users can switch between live interactive preview and raw code, copy with one click, or download the deliverable."* |
| **2:20 - 2:45** | Click **New Conversation**, send a brief message, then click back to the previous session in the sidebar. | *"Sessions are fully persistent in PostgreSQL and strictly isolated. Clicking previous sessions instantly restores message history and associated deliverables across refreshes."* |
| **2:45 - 3:00** | Switch to terminal showing passing test suite (`17 passed in 4.55s`). Wrap up. | *"Under the hood, we integrated both Pi Coding Agent and the Anthropic Claude SDK with a clean ModelRouter, supported by a 17-test automated pytest suite and full TypeScript validation. Thank you!"* |

---

## Part 2: Manual QA Test Checklist

Use this checklist to manually verify every feature before submission:

- [x] **Database Connectivity:** PostgreSQL 18 connects to `lenny_growth` and tables exist.
- [x] **Ingestion Engine:** Ingests 5 documents and creates 32 searchable chunks with GIN index.
- [x] **Health Endpoint:** `GET /health` returns `status: "healthy"` and lists model providers.
- [x] **Grounded Chat:** Answering PMF question includes verified citations from Casey Winters or Brian Balfour.
- [x] **Abstention Gate:** Querying physics, recipes, or movies returns `abstained: true` with zero citations.
- [x] **Provider Switching:** Provider dropdown shows Ollama (`qwen2.5:3b`), Pi Coding Agent, Anthropic, and OpenAI.
- [x] **Ship 30 for 30 Skill:** Generates structured long-form essay with word count and citations.
- [x] **Artifact Sandboxing:** Malicious `<script>` tags and `javascript:` URLs are sanitized; iframe is isolated.
- [x] **Session Isolation:** Two simultaneous conversations keep their messages completely separate.
- [x] **Session Persistence:** Reloading the browser restores previous conversation history from PostgreSQL.
