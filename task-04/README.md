# AI-Driven Development - 30-Day Challenge Task-4 

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
├── tools.py
└── .gitignore
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

[tool.setuptools]
py-modules = ["tools", "agent", "app"]
```

## 2️⃣ Tool Definitions (`tools.py`)

```python
import io
from pypdf import PdfReader
from agents import function_tool

def extract_text_from_pdf(pdf_file_bytes: bytes) -> str:
    pdf_stream = io.BytesIO(pdf_file_bytes)
    reader = PdfReader(pdf_stream)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    if not text.strip():
        return "ERROR: Could not extract meaningful text from the PDF."

    return text

# The decorated version for the agent
extract_text_from_pdf_tool = function_tool(extract_text_from_pdf)

TOOL_LIST = [extract_text_from_pdf_tool]
```

## 3️⃣ Agent Configuration (`agent.py`)

```python
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, RunConfig
from tools import extract_text_from_pdf_tool

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_MODEL_NAME = "gemini-2.5-flash"

gemini_client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
gemini_model = OpenAIChatCompletionsModel(openai_client=gemini_client, model=GEMINI_MODEL_NAME)
run_config = RunConfig()

summarizer_agent = Agent(
    name="PDF Summarizer Agent",
    instructions="Summarize the text concisely without extra remarks.",
    model=gemini_model,
    tools=[extract_text_from_pdf_tool],
)

quiz_generator_agent = Agent(
    name="Quiz Generator Agent",
    instructions="Generate a JSON quiz with a 'quizTitle' and a list of 'questions'. Each question should have 'id', 'type' ('multiple_choice' or 'short_answer'), 'question', 'options' (for MCQs), 'correctAnswer', and 'explanation'. Generate 3 MCQs and 2 short answers based only on the provided text.",
    model=gemini_model,
)

AGENT_RUN_CONFIG = run_config
SUMMARIZER_AGENT = summarizer_agent
QUIZ_GENERATOR_AGENT = quiz_generator_agent
```

## 4️⃣ Streamlit UI & Runner (`app.py`)
```python
import streamlit as st
import os
from dotenv import load_dotenv
from agent import SUMMARIZER_AGENT, QUIZ_GENERATOR_AGENT, AGENT_RUN_CONFIG
from tools import extract_text_from_pdf_tool
from agents import Runner
import asyncio
import json

load_dotenv()

st.title("📚 Study Notes Agent")

# Initialize session state variables
if "show_summary" not in st.session_state:
    st.session_state.show_summary = False
if "summary_text" not in st.session_state:
    st.session_state.summary_text = ""
if "show_quiz" not in st.session_state:
    st.session_state.show_quiz = False
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "quiz_submitted" not in st.session_state: # New state for quiz submission
    st.session_state.quiz_submitted = False
if "user_answers" not in st.session_state: # Store user answers
    st.session_state.user_answers = {}


uploaded_file = st.file_uploader("Upload a PDF to summarize and generate a quiz", type="pdf")

async def run_agents_async(pdf_bytes, action_type):
    # Extract text once
    with st.spinner("Extracting text from PDF..."):
        # Use the tool directly here, as it's synchronous and doesn't need Runner
        extracted_text = extract_text_from_pdf_tool(pdf_file_bytes=pdf_bytes)
        if "ERROR" in extracted_text:
            st.error(extracted_text)
            return

    if action_type == "summarize":
        with st.spinner("Summarizing..."):
            summary_response = await Runner.run(
                starting_agent=SUMMARIZER_AGENT,
                input=extracted_text,
                run_config=AGENT_RUN_CONFIG,
            )
            st.session_state.summary_text = summary_response.final_output
            st.session_state.show_summary = True
    
    elif action_type == "generate_quiz":
        with st.spinner("Generating quiz..."):
            quiz_response = await Runner.run(
                starting_agent=QUIZ_GENERATOR_AGENT,
                input=extracted_text,
                run_config=AGENT_RUN_CONFIG,
            )
            
            response_text = quiz_response.final_output
            # Improved JSON extraction to handle agents potentially not returning JSON always
            try:
                if "```json" in response_text:
                    json_part = response_text.split("```json")[1].split("```")[0]
                else:
                    json_part = response_text
                
                quiz_data = json.loads(json_part)
                
                # Try to find questions in various possible locations
                questions_list = []
                if "questions" in quiz_data and isinstance(quiz_data["questions"], list):
                    questions_list = quiz_data["questions"]
                elif "quiz" in quiz_data and "questions" in quiz_data["quiz"] and isinstance(quiz_data["quiz"]["questions"], list):
                    questions_list = quiz_data["quiz"]["questions"]
                
                if not questions_list: # Check if questions_list is empty after trying both structures
                    st.warning("The quiz agent did not return any questions. Please try again.")
                    st.error("Agent response (raw):") # Add this for debugging
                    st.code(response_text)            # Add this for debugging
                    st.session_state.show_quiz = False # Ensure quiz is not shown if empty
                else:
                    st.session_state.quiz_data = quiz_data # Store the full quiz_data
                    st.session_state.show_quiz = True
                    st.session_state.quiz_submitted = False # Reset submission state
                    st.session_state.user_answers = {} # Clear previous answers
            except (json.JSONDecodeError, KeyError) as e:
                st.error(f"Failed to parse the quiz JSON from the agent's response: {e}")
                st.code(response_text)
                st.session_state.show_quiz = False


# Create tabs
tab1, tab2 = st.tabs(["Summarizer", "Quiz Generator"])

with tab1:
    st.header("PDF Summarizer")
    if uploaded_file:
        if st.button("Summarize PDF", key="summarize_pdf_button"):
            asyncio.run(run_agents_async(uploaded_file.read(), "summarize"))

    if st.session_state.show_summary:
        st.subheader("Summary")
        st.write(st.session_state.summary_text)

with tab2:
    st.header("Quiz Generator")
    if uploaded_file:
        if st.button("Generate Quiz", key="generate_quiz_button"):
            asyncio.run(run_agents_async(uploaded_file.read(), "generate_quiz"))

    if st.session_state.show_quiz:
        st.subheader("Quiz")
        quiz_data = st.session_state.quiz_data
        
        try:
            questions_list = []
            if "questions" in quiz_data and isinstance(quiz_data["questions"], list):
                questions_list = quiz_data["questions"]
            elif "quiz" in quiz_data and "questions" in quiz_data["quiz"] and isinstance(quiz_data["quiz"]["questions"], list):
                questions_list = quiz_data["quiz"]["questions"]
            
            if questions_list:
                quiz_title = quiz_data.get("quizTitle", quiz_data.get("quiz", {}).get("title", "Quiz"))
                st.header(quiz_title)
                
                # Collect answers only if quiz not submitted
                if not st.session_state.quiz_submitted:
                    for i, q in enumerate(questions_list):
                        st.write(f"**Question {i+1}:** {q['question']}")
                        
                        if q["type"] == "multiple_choice":
                            options_with_placeholder = ["Select an option..."] + q["options"]
                            st.session_state.user_answers[i] = st.radio(
                                "Your answer:",
                                options_with_placeholder,
                                index=0, # Preselect the placeholder
                                key=f"quiz_q_{i}", # Unique key for quiz display
                                label_visibility="collapsed"
                            )
                        elif q["type"] == "short_answer":
                            st.session_state.user_answers[i] = st.text_input(
                                "Your answer:", 
                                key=f"quiz_q_{i}", 
                                label_visibility="collapsed"
                            )
                        st.markdown("---")

                    if st.button("Submit Quiz", key="submit_quiz_button"):
                        # Check if all questions are answered
                        all_answered = True
                        for i, q in enumerate(questions_list):
                            if q["type"] == "short_answer" and not st.session_state.user_answers.get(i):
                                all_answered = False
                                break
                            elif q["type"] == "multiple_choice" and st.session_state.user_answers.get(i) == "Select an option...":
                                all_answered = False
                                break
                        
                        if not all_answered:
                            st.warning("Please answer all questions before submitting.")
                        else:
                            st.session_state.quiz_submitted = True
                            st.rerun() # Rerun to show results
                else: # Quiz has been submitted, show results
                    score = 0
                    st.subheader("Results")
                    for i, q in enumerate(questions_list):
                        is_correct = False
                        user_ans = st.session_state.user_answers.get(i, "") # Get user's stored answer

                        if q["type"] == "multiple_choice":
                            if user_ans == q["correctAnswer"]:
                                score += 1
                                is_correct = True
                        
                        st.write(f"**Question {i+1}:** {q['question']}")
                        if is_correct:
                            st.success(f"Your answer: {user_ans} (Correct)")
                        else:
                            if q["type"] == "multiple_choice":
                                st.error(f"Your answer: {user_ans} (Incorrect)")
                                st.info(f"Correct answer: {q['correctAnswer']}")
                            else: # short answer
                                st.info(f"Your answer: {user_ans}")
                                st.info(f"Suggested answer: {q['correctAnswer']}")
                            
                            if "explanation" in q and q["explanation"]:
                                st.warning(f"Explanation: {q['explanation']}")
                        st.markdown("---")
                    
                    num_mcqs = len([q for q in questions_list if q["type"] == "multiple_choice"])
                    if num_mcqs > 0:
                        st.balloons()
                        st.success(f"You scored {score} out of {num_mcqs} on the multiple choice questions.")
            else: # If "questions" key is missing or empty
                st.warning("The quiz data does not contain any questions to display.")
        except (json.JSONDecodeError, KeyError) as e:
            st.error("Failed to process the quiz data. The format might be incorrect.")
            st.text("Raw response from session state:")
            st.code(st.session_state.get("quiz_data", "No quiz data found in session state."))


if uploaded_file and not (st.session_state.show_summary or st.session_state.show_quiz):
    # This block ensures that if a file is uploaded, and no action is taken yet,
    # the async function is not run immediately without a button click.
    # It also handles initial load or re-uploads.
    pass
```