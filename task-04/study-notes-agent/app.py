import streamlit as st
import os
from dotenv import load_dotenv
from agent import SUMMARIZER_AGENT, QUIZ_GENERATOR_AGENT, AGENT_RUN_CONFIG
from tools import extract_text_from_pdf
from agents import Runner
import asyncio

load_dotenv()

st.title("📚 Study Notes Agent")

uploaded_file = st.file_uploader("Upload a PDF to summarize and generate a quiz", type="pdf")

async def run_agents_async(pdf_bytes):
    # Extract text once
    extracted_text = None
    with st.spinner("Extracting text from PDF..."):
        extracted_text = extract_text_from_pdf(pdf_bytes)
        if "ERROR" in extracted_text:
            st.error(extracted_text)
            return

    if st.button("Summarize PDF"):
        with st.spinner("Summarizing..."):
            summary_response = await Runner.run(
                starting_agent=SUMMARIZER_AGENT,
                input=extracted_text,
                run_config=AGENT_RUN_CONFIG,
            )
            st.subheader("Summary")
            st.write(summary_response.final_output)

    if st.button("Generate Quiz"):
        with st.spinner("Generating quiz..."):
            quiz_response = await Runner.run(
                starting_agent=QUIZ_GENERATOR_AGENT,
                input=extracted_text,
                run_config=AGENT_RUN_CONFIG,
            )
            st.subheader("Quiz")
            st.json(quiz_response.final_output)

if uploaded_file:
    asyncio.run(run_agents_async(uploaded_file.read()))
