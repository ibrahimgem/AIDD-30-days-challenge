# agent_config.py
import os
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel
from tools import read_pdf_document

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_MODEL_NAME = "gemini-2.5-flash"

def create_study_agent() -> Agent:
    if "GEMINI_API_KEY" not in os.environ:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    gemini_client = AsyncOpenAI(
        api_key=os.environ["GEMINI_API_KEY"],
        base_url=GEMINI_BASE_URL,
    )

    model_instance = OpenAIChatCompletionsModel(
        model=GEMINI_MODEL_NAME,
        openai_client=gemini_client,
    )

    system_prompt = (
        "You are a Study Notes Summarizer and Quiz Generator Agent. "
        "1. When a file path is provided, call the `read_pdf_document` tool. "
        "2. After extracting text, create a clean summary. "
        "3. If the user requests a quiz, generate MCQs and open-ended questions using the original text."
    )

    return Agent(
        name='Study_Helper',
        instructions=system_prompt,
        model=model_instance,
        tools=[read_pdf_document]
    )
