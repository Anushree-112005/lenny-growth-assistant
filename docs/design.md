# UI/UX & Design Specification — The Lenny Growth Assistant

## 1. Visual Direction & Design Philosophy

The interface is designed as an **editorial research workspace**, taking aesthetic cues from high-signal publications (Substack, Linear, Stripe Press, The Economist). It rejects cluttered, playful chat bubbles in favor of calm typography, structured white space, and clear hierarchy.

### Design Principles:
1. **Calm Neutral Canvas:** A warm paper background (`#FCFBF9`) paired with soft stone cards (`#FFFFFF`) and warm-zinc borders (`#E4E4E7`).
2. **Editorial Typography:**
   - **Primary UI & Paragraphs:** `Plus Jakarta Sans` (clean, modern, highly legible).
   - **Headings & Long-Form Essays:** `Newsreader` (refined serif providing book-like readability).
   - **Code & Metadata:** `JetBrains Mono` (crisp monospace for document IDs, tokens, and code).
3. **Restrained Accents:** Slate charcoal (`#18181B`) for primary buttons and user speech, subtle royal blue (`#2563EB`) for interactive links, emerald (`#16A34A`) for online status, and warm amber (`#D97706`) for abstention notices.

---

## 2. Layout Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [Sidebar - 280px]          │ [Main Panel - Flexible]              │ [Artifact Viewer - 480px]    │
│                            │                                      │                              │
│ • App Identity & Badge     │ • Top Header: Session Title,         │ • Header: Title, Type Badge  │
│ • "+ New Conversation"     │   Model Selector Pill, Ship 30 Pill, │ • Controls: Copy, Download,  │
│ • Session History List     │   Artifact Viewer Toggle             │   Close                      │
│   - Active indicator       │ • Chat Stream (Max-width: 780px)     │ • Tabs: Live Preview vs Code │
│   - Delete action          │   - User message bubble              │ • Sandboxed Iframe Container │
│ • Bottom: Sources Counter  │   - Assistant editorial bubble       │ • Security Isolation Badge   │
│   (Click to open modal)    │   - Expandable Citation Cards        │                              │
│                            │   - Action toolbar (Ship 30/Artifact)│                              │
│                            │ • Fixed Bottom Composer              │                              │
└────────────────────────────┴──────────────────────────────────────┴──────────────────────────────┘
```

---

## 3. Key UI States

### 1. Welcome State (0 Messages)
- Centered editorial headline and description.
- 4 quick-start recommendation cards covering key Lenny frameworks:
  - *"What are common approaches to finding product-market fit?"*
  - *"Summarize the strongest growth lessons in these sources."*
  - *"How does Elena Verna explain B2B PLG vs sales-assisted models?"*
  - *"What are the Four Fits according to Brian Balfour?"*

### 2. Evidence-Grounded Response State
- Formatted markdown with serif headings and concise paragraphs.
- Provider and model tag in header (e.g. `OLLAMA · qwen2.5:3b`).
- Expandable citation drawer displaying verified source titles, clickable links, relevance percentage badge (`Match: 85%`), and exact quotation excerpts.
- Quick action pills: *"Draft Ship 30 Essay"* and *"Create Landing Page Artifact"*.

### 3. Transparent Abstention State
- Prominent amber banner with alert icon:
  `Insufficient Evidence In Transcripts: This response was abstained because the question is outside the verified scope of the ingested materials.`
- Explanatory message with bulleted suggestions of what *is* covered in the knowledge base.
- Zero citations rendered (preventing false attribution).

### 4. Artifact Viewer State
- Two-tab layout: **Preview** and **Source Code**.
- HTML deliverables render inside an isolated `<iframe>` with `sandbox="allow-scripts"`.
- One-click "Copy Code" with checkmark confirmation.
- One-click "Download" (.html or .md file).

---

## 4. Accessibility & Responsive Design

- **Keyboard Navigation:** Full support for `Enter` to submit, `Shift + Enter` for newlines, and `Tab` traversal.
- **Contrast Ratios:** All text elements exceed WCAG AA 4.5:1 contrast standards.
- **Responsive Adaptations:**
  - On screens `< 1024px`, the Artifact Viewer transitions into a full-width overlay drawer.
  - On screens `< 768px`, the sidebar collapses into a slide-over panel.
