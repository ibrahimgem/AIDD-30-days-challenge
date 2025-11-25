import streamlit as st
import os
from dotenv import load_dotenv
from agent import SUMMARIZER_AGENT, QUIZ_GENERATOR_AGENT, AGENT_RUN_CONFIG
from tools import extract_text_from_pdf
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
        extracted_text = extract_text_from_pdf(pdf_bytes)
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
                if not quiz_data or ("questions" not in quiz_data) or not quiz_data["questions"]:
                    st.warning("The quiz agent did not return any questions. Please try again.")
                    st.error("Agent response (raw):") # Add this for debugging
                    st.code(response_text)            # Add this for debugging
                    st.session_state.show_quiz = False # Ensure quiz is not shown if empty
                else:
                    st.session_state.quiz_data = quiz_data
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
            if "questions" in quiz_data:
                st.header(quiz_data.get("quiz_title", "Quiz"))
                
                # Collect answers only if quiz not submitted
                if not st.session_state.quiz_submitted:
                    for i, q in enumerate(quiz_data["questions"]):
                        st.write(f"**Question {i+1}:** {q['question']}")
                        
                        if q["type"] == "multiple_choice":
                            st.session_state.user_answers[i] = st.radio(
                                "Your answer:",
                                q["options"],
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
                        st.session_state.quiz_submitted = True
                        st.experimental_rerun() # Rerun to show results
                else: # Quiz has been submitted, show results
                    score = 0
                    st.subheader("Results")
                    for i, q in enumerate(quiz_data["questions"]):
                        is_correct = False
                        user_ans = st.session_state.user_answers.get(i, "") # Get user's stored answer

                        if q["type"] == "multiple_choice":
                            if user_ans == q["correct_answer"]:
                                score += 1
                                is_correct = True
                        
                        st.write(f"**Question {i+1}:** {q['question']}")
                        if is_correct:
                            st.success(f"Your answer: {user_ans} (Correct)")
                        else:
                            if q["type"] == "multiple_choice":
                                st.error(f"Your answer: {user_ans} (Incorrect)")
                                st.info(f"Correct answer: {q['correct_answer']}")
                            else: # short answer
                                st.info(f"Your answer: {user_ans}")
                                st.info(f"Suggested answer: {q['correct_answer']}")
                            
                            if "explanation" in q and q["explanation"]:
                                st.warning(f"Explanation: {q['explanation']}")
                        st.markdown("---")
                    
                    num_mcqs = len([q for q in quiz_data["questions"] if q["type"] == "multiple_choice"])
                    if num_mcqs > 0:
                        st.balloons()
                        st.success(f"You scored {score} out of {num_mcqs} on the multiple choice questions.")

        except (json.JSONDecodeError, KeyError) as e:
            st.error("Failed to process the quiz data. The format might be incorrect.")
            st.text("Raw response from session state:")
            st.code(st.session_state.get("quiz_data", "No quiz data found in session state."))


if uploaded_file and not (st.session_state.show_summary or st.session_state.show_quiz):
    # This block ensures that if a file is uploaded, and no action is taken yet,
    # the async function is not run immediately without a button click.
    # It also handles initial load or re-uploads.
    pass
