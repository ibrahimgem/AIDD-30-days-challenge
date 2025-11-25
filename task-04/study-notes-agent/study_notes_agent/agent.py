import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, RunConfig
from study_notes_agent.tools import extract_text_from_pdf_tool

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
