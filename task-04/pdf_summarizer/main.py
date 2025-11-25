# src/main.py
import streamlit as st
# from openagents import Agent
# from pdf_utils import extract_text, clean_text

st.title("PDF Summarizer and Quiz Generator")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file is not None:
    # raw_text = extract_text(uploaded_file.getvalue())
    # cleaned_text = clean_text(raw_text)
    
    st.success("PDF uploaded successfully!")
    st.write("Processing PDF...")

    # For now, just display a placeholder
    st.subheader("Summary (Placeholder)")
    st.write("Summary will appear here.")

    if st.button('Create Quiz'):
        st.subheader("Quiz (Placeholder)")
        st.write("Quiz will appear here.")
