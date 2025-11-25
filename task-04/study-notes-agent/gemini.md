# 💾 Study Notes Summarizer & Quiz Generator Agent — Specifications

## 🚀 Project Overview: Study Notes Agent
This document outlines the specifications for building a **Study Notes Summarizer & Quiz Generator Agent** using the **openai-agents SDK** configured for the **Gemini API**.

## 🧠 Agent Core Functionality

| Function | Description |
|---------|-------------|
| **A. PDF Summarizer** | Extract text from a user-uploaded PDF and generate a clean, concise, meaningful summary. |
| **B. Quiz Generator** | Generate a mixed-style quiz (MCQs + Short Answers) based strictly on the original PDF text. |

## ⚙️ Critical Technical Constraints (Zero-Bloat Protocol)

### Zero-Bloat Rules
- No extra code — only essential logic.
- Strict integration with **Streamlit**.
- No imaginary SDK features.
- Use only **openai-agents SDK** official syntax.

### Gemini API Configuration via OpenAI Adapter
- **SDK:** `openai-agents`
- **Base URL:** `https://generativelanguage.googleapis.com/v1beta/openai/`
- **API Key:** Load via `.env` (`GEMINI_API_KEY`)
- **Model Adapter:** `OpenAIChatCompletionsModel`
- **Model Name:** `gemini-2.5-flash`
- **Execution:** Always use `RunConfig`
- **Runner:** Use Runner from agents
- **Error Protocol:** On any SDK-related error → verify docs before coding further
- **Dependency Management:** Use `uv` for package management.


## 📂 Project Structure

```
study-notes-agent/
├── .env
├── pyproject.toml
├── app.py
├── agent.py
└── tools.py
```

## 1️⃣ Dependencies & Environment

### `.env`

```
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
```

### `pyproject.toml`

```toml
[project]
name = "study-notes-agent"
version = "0.1.0"
description = "PDF Summarizer and Quiz Generator Agent using OpenAI Agents SDK (for Gemini) and Streamlit."
dependencies = [
    "streamlit",
    "pypdf",
    "openai-agents",
    "python-dotenv",
    "openai",
]

[build-system]
requires = ["setuptools>=61.0.0"]
build-backend = "setuptools.build_meta"
```

## 2️⃣ Tool Definitions (`tools.py`)

```python
import io
from pypdf import PdfReader
from agents import function_tool, FunctionTool

@function_tool
def extract_text_from_pdf(pdf_file_bytes: bytes) -> str:
    pdf_stream = io.BytesIO(pdf_file_bytes)
    reader = PdfReader(pdf_stream)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    if not text.strip():
        return "ERROR: Could not extract meaningful text from the PDF."

    return text

TOOL_LIST = [extract_text_from_pdf]
```

## 3️⃣ Agent Configuration (`agent.py`)

```python
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, RunConfig
from tools import extract_text_from_pdf

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_MODEL_NAME = "gemini-2.0-flash"

gemini_client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
gemini_model = OpenAIChatCompletionsModel(client=gemini_client, model=GEMINI_MODEL_NAME)
run_config = RunConfig()

summarizer_agent = Agent(
    name="PDF Summarizer Agent",
    instructions="Summarize the text concisely without extra remarks.",
    model=gemini_model,
    tools=[extract_text_from_pdf],
)

quiz_generator_agent = Agent(
    name="Quiz Generator Agent",
    instructions="Generate a JSON quiz (3 MCQs, 2 short answers) based only on the provided text.",
    model=gemini_model,
)

AGENT_RUN_CONFIG = run_config
SUMMARIZER_AGENT = summarizer_agent
QUIZ_GENERATOR_AGENT = quiz_generator_agent
```

## 4️⃣ Streamlit UI & Runner (`app.py`)
(Full Streamlit implementation included in original prompt.)
