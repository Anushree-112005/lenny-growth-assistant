# Product Requirement Document (PRD) — The Lenny Growth Assistant

**Product Name:** The Lenny Growth Assistant  
**Client / Evaluator:** Oogway Labs  
**Date:** 11–12 October 2026  
**Status:** Implemented & Verified  

---

## 1. Forward Deployment Brief

### User and Problem
- **Primary Users:** Early-stage startup founders, Growth Product Managers, Product Marketers, and Content Creators.
- **Job to Complete:** Discover, validate, and apply proven product and growth principles (Product-Market Fit diagnosis, PLG monetization gates, retention curves, pricing models) without spending hours hunting through hundreds of transcript pages.
- **Pain Removed:** Eliminates hallucinations and generic AI advice by strictly grounding every insight in verified Lenny Rachitsky podcast/newsletter transcripts with clickable, verifiable source excerpts.

### Success Metrics
- **Grounding Accuracy Rate:** ≥ 98% of claims verifiable against cited transcript chunks in automated evaluations.
- **Abstention Precision:** 100% abstention on out-of-domain or unverified queries (0 false citations generated).
- **Time-to-Insight:** < 5 seconds for evidence retrieval and citation linking.
- **Local Operability:** 100% functional demo running locally on Windows using PostgreSQL and Ollama with 0 cloud API costs.

### Assumptions
- Transcripts are supplied as structured Markdown (`.md`), plain text (`.txt`), or JSON (`.json`) files containing frontmatter or headers (title, doc_id, source URL).
- Evaluators test on a local Windows machine with PostgreSQL (port 5432) and Ollama (`qwen2.5:3b`) installed.
- Cloud providers (Anthropic Claude, OpenAI) are optional enhancements enabled via `.env` keys.

### Scope Choices
- **Included:**
  - Full-text and lexical hybrid search using PostgreSQL with GIN indexing (`to_tsvector` / `ts_rank_cd`).
  - Strict relevance threshold abstention gate (0.05).
  - Multi-turn persistent conversational sessions stored in PostgreSQL.
  - ModelRouter supporting Ollama, Pi Coding Agent SDK (`pi-agent`), Anthropic Claude (`claude-agent-sdk`), and OpenAI.
  - Dedicated Ship 30 for 30 essay generation skill (~1,250 words).
  - Sandboxed Artifact Viewer for interactive HTML deliverables.
- **Intentionally Excluded & Why:**
  - Audio transcription pipeline (Whisper): Raw transcripts are already available; avoids unnecessary heavy compute overhead.
  - Paid embedding APIs (OpenAI text-embedding-3): Replaced by PostgreSQL native full-text search to ensure zero-cost offline operability.

### Risks and Trade-offs
- **Local Model Latency vs. Cost:** Local Ollama on CPU/GPU takes 30–90 seconds for long essays. *Trade-off accepted* to guarantee a free, offline local demo; mitigated via 180s HTTPX timeouts and live progress indicators.
- **Model Grounding Drift:** Small local models (`qwen2.5:3b`) can stray if prompts are ambiguous. *Mitigated* by strictly formatted system prompts and linking citations directly from database chunk records rather than trusting model text alone.
- **Untrusted HTML Artifacts:** User-generated or model-generated HTML could introduce XSS. *Mitigated* by server-side regex sanitization and strict iframe sandboxing (`sandbox="allow-scripts"` without `allow-same-origin`).

---

## 2. Goals & Non-Goals

### Goals
- **Grounded Intelligence:** Every factual claim must be backed by retrieved transcript chunks with verifiable title, document ID, URL, and excerpt.
- **Strict Abstention:** When evidence is insufficient or irrelevant, the assistant must transparently refuse to speculate and explain the limitation.
- **Model Agnostic Architecture:** Plug-and-play support for local Ollama (`qwen2.5:3b`), the Pi Coding Agent SDK (`pi-agent`), Anthropic Claude (`claude-agent-sdk` / `anthropic`), and OpenAI (`openai`) without application code changes.
- **Session Isolation & Persistence:** Multi-turn sessions stored in PostgreSQL with complete isolation across conversations.
- **Dedicated Ship 30 for 30 Skill:** Turn growth concepts into structured ~1,250-word atomic essays featuring 1-3-1 hooks, central theses, narrative sections, and concrete takeaways.
- **Sandboxed Artifact Viewer:** Render model-generated HTML/CSS landing pages and experiment briefs in an isolated iframe (`sandbox="allow-scripts"`), preventing access to host cookies or storage.
- **Offline/Local First Demo:** Provide a 100% free, zero-paid-API local workflow using PostgreSQL 18 and Ollama on Windows.

### Non-Goals
- Real-time voice synthesis or audio transcription streaming.
- Scraping paid Substack paywalls without explicit user-provided text files.
- Arbitrary code execution in the host environment (all code preview is sandboxed).

---

## 3. Core User Personas & Use Cases

1. **The Early-Stage Founder:** Diagnosing whether their startup has reached Product-Market Fit by querying Casey Winters' and Brian Balfour's retention and 4-Fits frameworks.
2. **The Growth Product Manager:** Exploring monetization gates (feature gating vs usage limits vs seat barriers) based on Elena Verna's B2B PLG frameworks.
3. **The Product Marketer & Creator:** Using the Ship 30 for 30 skill to synthesize internal growth takeaways into viral, skimmable atomic essays for company distribution.
4. **The Growth Designer:** Generating interactive landing page deliverables and pricing calculator artifacts directly from conversation context.

---

## 4. User Journey & Core Flows

```
[ User Input / Query ]
          │
          ▼
[ Conversation Session Managed (PostgreSQL) ]
          │
          ▼
[ Hybrid Retrieval: Postgres FTS + Lexical Matching ]
          │
          ├── Score < Threshold (0.05) ──► [ Transparent Abstention Response ]
          │
          └── Score >= Threshold ─────────► [ Grounded Prompt Built with Source Chunks ]
                                                           │
                                                           ▼
                                            [ Model Provider Router ]
                                         (Ollama / Pi-Agent / Claude / OpenAI)
                                                           │
                                                           ▼
                                            [ Assistant Response + Verifiable Citations ]
                                                           │
                                            ┌──────────────┴──────────────┐
                                            ▼                             ▼
                            [ Draft Ship 30 Essay ]        [ Generate Artifact Deliverable ]
                                    (1,250w)                    (Sandboxed Iframe)
```

---

## 5. Acceptance Criteria

| ID | Requirement | Acceptance Criteria | Verified Status |
|---|---|---|---|
| AC-1 | Ingestion & Search | Ingests `.md`, `.txt`, `.json` into Postgres chunks with metadata and GIN full-text search. | PASS |
| AC-2 | Citations | Answers link to source chunks with title, doc ID, URL, relevance score, and excerpt. | PASS |
| AC-3 | Abstention | Irrelevant queries (e.g., astrophysics) trigger transparent abstention with zero fake citations. | PASS |
| AC-4 | Model Router | Switches between Ollama, Pi Coding Agent, Anthropic, and OpenAI via config or UI. | PASS |
| AC-5 | Local Demo | Local Ollama (`qwen2.5:3b`) works out-of-the-box on Windows without API keys. | PASS |
| AC-6 | Session Isolation | Conversations persist across refreshes; messages from Session A never bleed into Session B. | PASS |
| AC-7 | Ship 30 Skill | Generates structured ~1,250-word atomic essay with hook, thesis, takeaways, and citations. | PASS |
| AC-8 | Artifact Viewer | Renders HTML deliverables in an isolated sandbox with sanitized script protections. | PASS |
| AC-9 | Quality Gates | 100% passing automated pytest suite and TypeScript Vite production build. | PASS |

---

## 6. Risks & Mitigations

1. **Local Model Latency:** Ollama running on local hardware can take 30–90 seconds for long generation.
   * *Mitigation:* Configured 180s HTTPX timeouts and live UI loading spinners.
2. **Hallucinated Metadata:** Models inventing episode numbers or guests.
   * *Mitigation:* Strict system grounding prompt requiring references only to supplied chunks; citations structured directly from retrieved database rows, not model free-text hallucinations.
3. **Malicious HTML Injection in Artifacts:**
   * *Mitigation:* Regex-based HTML sanitizer stripping cookie access, localStorage manipulation, and nested iframes, coupled with restrictive `sandbox="allow-scripts"` without `allow-same-origin`.
