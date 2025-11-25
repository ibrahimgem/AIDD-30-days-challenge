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
