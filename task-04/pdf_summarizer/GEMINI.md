# Study Notes Summarizer & Quiz Generator — specifications.md

## 1. Project Overview

Build an agent that ingests a PDF (study notes, lecture slides, textbook chapter), summarizes its content, and optionally generates a quiz (MCQs or mixed) based on the original PDF. The agent will be implemented using:

* **OpenAgents SDK** — orchestrate agent, tools and actions
* **Streamlit** — UI (recommended); HTML/CSS allowed for alternative UI
* **PyPDF** — extract text from PDF
* **Gemini CLI** — local/remote LLM access for inference (used for generation prompts)
* **Context7 MCP (tool provider)** — provide auxiliary tools (e.g., semantic search, vector store, metadata store, or custom QA helpers)

## 2. High-level Features

**A. PDF Summarizer**

* Upload PDF via UI
* Extract text using PyPDF
* Clean / normalize text (remove headers/footers, handle columns)
* Generate a concise, meaningful summary (configurable length: short / medium / long)
* Display summary in UI (cards / blocks)

**B. Quiz Generator**

* User clicks **Create Quiz** after summary or directly
* Agent reads original PDF text (not the summary) to produce questions
* Support: MCQs only or Mixed-style (MCQs + short answer)
* Configurable number of questions, difficulty (easy/medium/hard), and shuffle options
* Each MCQ must include one correct answer + 3 plausible distractors

## 3. Tech Stack & Dependencies

* Python 3.10+
* OpenAgents SDK (latest stable)
* Streamlit
* pypdf (PyPDF2 fork / PyPDF)
* transformers / or Gemini CLI for LLM access
* context7 MCP (SDK / client for tool provider)
* (Optional) sentence-transformers + FAISS / vector DB if adding semantic search
* Packaging: poetry / pip

## 4. Architecture & Data Flow

1. **UI (Streamlit)**: user uploads PDF -> triggers `upload_handler`
2. **PDF Processor**: PyPDF extracts pages -> `text_cleaner` normalizes
3. **Agent (OpenAgents SDK)**: orchestrates two flows — `summarize` and `generate_quiz`

   * Calls LLM via Gemini CLI for generation
   * Uses Context7 MCP tools where helpful (e.g., compute embeddings, fetch metadata)
4. **Results**: summary + quiz returned -> UI displays and allows export (JSON/CSV)

```
[Streamlit UI] -> [PDF] -> [PyPDF extraction] -> [Cleaner] -> [OpenAgents Agent]
                                    |-> [Context7 MCP tools] -> [LLM via Gemini CLI]
                                    -> [Summary / Quiz] -> [UI / Export]
```

## 5. Component Specifications

### 5.1 Streamlit UI

* Pages / Controls:

  * `Upload PDF` file uploader
  * `Summary Options`: length selector (short/medium/long), include key takeaways toggle
  * `Create Quiz` button + options (num_questions, difficulty, style)
  * Display area: summary card, and Quiz area with question list and answers hidden/show toggle
  * Export buttons: `Download summary (.txt)`, `Download quiz (.json/.csv)`
* UX details:

  * Show progress / loading spinner while agent runs
  * Show PDF metadata (title, pages)
  * Allow re-run with different settings

### 5.2 PDF Extraction (PyPDF)

* Read file bytes into `PdfReader`
* For each page: extract text with `page.extract_text()`
* Preprocessing:

  * Remove repeated headers/footers: detect using frequency heuristics (first/last 5 lines repeated)
  * Normalize whitespace, fix hyphenation at line-breaks
  * Optionally split into logical chunks (by headings or by ~1000–2500 token windows)
* Output: `raw_text`, `page_indexed_text` (list of page strings)

### 5.3 Agent design with OpenAgents SDK

* Agent responsibilities:

  1. Accept cleaned text or page-indexed text
  2. Summarize text by running generation prompt
  3. Generate quiz questions by referencing the original PDF text
  4. Optionally call Context7 MCP tools for: embeddings, retrieval, or content tagging
* Tools the agent should expose to the SDK:

  * `extract_text(pdf_bytes) -> str` (local tool)
  * `summarize(text, length) -> summary` (calls LLM)
  * `generate_quiz(text, n, difficulty, style) -> questions` (calls LLM)
  * `semantic_search(query, top_k) -> passages` (Context7 MCP tool)
  * `save_artifact(metadata, payload)` (Context7 MCP tool for storing results)

### 5.4 LLM Integration (Gemini CLI)

* Use Gemini CLI for inference: run subprocess calls or SDK wrapper
* Example invocation pattern:

  * `gemini-cli generate --model [MODEL] --prompt-file prompt.txt --max-tokens 512` (adapt to CLI)
* Keep prompts small and structured; chunk long inputs and apply retrieval before generation
* Use temperature and top-p tuned for deterministic outputs (e.g., temperature 0.2 for summaries; 0.6 for quiz creativity)

### 5.5 Context7 MCP (Tool Provider)

* Use for:

  * Creating embeddings of PDF chunks
  * Fast retrieval of relevant passages to ground question generation (reduces hallucination)
  * Storing generated quizzes and summaries as artifacts with metadata
* Expected workflow for quiz generation:

  1. Chunk PDF -> embeddings via MCP tool
  2. For each candidate question, run retrieval for the supporting passage(s)
  3. Send supporting passage + instruction to Gemini to fabricate question + answers

## 6. Prompt Templates (examples)

### 6.1 Summarizer prompt (short)

```
You are a helpful study assistant. Produce a concise summary (3-5 bullet points) of the following text. Keep language clear and focus on key concepts, definitions, and examples.

TEXT:
{{chunk_text}}

OUTPUT:
- Bullet 1
- Bullet 2
- Bullet 3
```

### 6.2 Quiz generation prompt (MCQ)

```
You are a quiz generator. Using the passage below, produce 1 multiple-choice question with 4 answer options and mark the correct answer. Also include a short explanation (1-2 sentences) for the correct answer.

PASSAGE:
{{passage}}

RETURN JSON:
{
 "question": "...",
 "options": ["A...","B...","C...","D..."],
 "answer_index": 1,
 "explanation": "..."
}
```

### 6.3 Mixed-style prompt

* Combine MCQ and short-answer formats in a single request when user selected `mixed` style.

## 7. Chunking & Retrieval Strategy

* Chunk size: ~800–1500 tokens (adjust based on model limits)
* Create embeddings per chunk (Context7 MCP or sentence-transformers)
* For quiz generation: use retrieval to fetch top-K relevant chunks for each question prompt
* This ensures questions are grounded in the source text

## 8. Data & Privacy

* No PDF or extracted content should be stored without explicit user consent
* If storing artifacts (via Context7 MCP), mark them private and scope by user session id
* Encrypted storage if persisted; otherwise ephemeral in memory during a session
* Explicit user consent UI toggle `Save results` (Yes/No)

## 9. Error Handling & Edge Cases

* Empty or scanned PDFs:

  * If `extract_text()` returns little text, detect scanned image PDF and show a message: "PDF appears scanned — OCR required" (OCR not implemented initially)
* Very long PDFs:

  * Provide warning and chunking progress; offer to limit to first N pages
* Poorly formatted text:

  * Use heuristics to remove noise; if >50% noise, ask user to upload cleaner notes

## 10. Testing & Acceptance Criteria

* Unit tests for:

  * `extract_text` (sample PDFs)
  * `clean_text` heuristics
  * `summarize` prompt outputs (assert presence of key terms)
  * `generate_quiz` JSON schema and correctness (answer index points to an option matching explanation)
* Integration tests:

  * Full end-to-end run with a 5-page PDF -> summary + 5-question quiz
  * Verify that quiz questions reference material present in PDF (via retrieval)

## 11. Deployment & Dev Flow

* Local dev: Streamlit app running on port 8501
* Use `.env` for API keys (Gemini CLI creds, Context7 creds)
* Containerize with Dockerfile for deployment
* CI: run tests and linting; on push to `main`, build Docker image and optionally deploy to a cloud provider

## 12. Example Implementation Sketch (pseudo-code)

```python
# main.py (Streamlit)
import streamlit as st
from openagents import Agent
from pdf_utils import extract_text, clean_text

st.file_uploader(...)
if uploaded:
    raw = extract_text(uploaded.getvalue())
    cleaned = clean_text(raw)
    summary = agent.call_tool('summarize', cleaned, length='short')
    st.markdown(summary)
    if st.button('Create Quiz'):
        quiz = agent.call_tool('generate_quiz', raw, n=5, difficulty='medium')
        st.json(quiz)
```

## 13. Acceptance checklist

* [ ] Upload & text extraction works for standard PDFs
* [ ] Summaries are concise and accurate (user-tested)
* [ ] Quizzes are grounded in source text and follow schema
* [ ] UI responsive and exports work
* [ ] Privacy / opt-in storage implemented

## 14. Next actions / Milestones

1. Setup project skeleton + environment
2. Implement PDF extraction & cleaning
3. Integrate OpenAgents agent + local tool wrappers
4. Hook Gemini CLI for LLM calls
5. Integrate Context7 MCP for embeddings/retrieval
6. Build Streamlit UI and wire flows
7. Testing, QA, deploy

---

*End of specifications.*
