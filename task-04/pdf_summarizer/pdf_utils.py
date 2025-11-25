# src/pdf_utils.py
import io
import pypdf

def extract_text(pdf_bytes):
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def clean_text(text):
    # Basic cleaning for now
    # TODO: Implement more robust cleaning (headers/footers, hyphenation, etc.)
    cleaned_text = ' '.join(text.split()) # Normalize whitespace
    return cleaned_text
