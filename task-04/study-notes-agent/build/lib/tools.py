# tools.py
import PyPDF2
from agents import function_tool

@function_tool
def read_pdf_document(file_path: str) -> str:
    """
    Extracts text from a PDF file.
    """
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                extracted_page_text = page.extract_text()
                if extracted_page_text:
                    text += extracted_page_text + "\n"
            return text
    except FileNotFoundError:
        return f"Error: PDF file not found at path: {file_path}"
    except Exception as e:
        return f"An error occurred during PDF processing: {e}"

