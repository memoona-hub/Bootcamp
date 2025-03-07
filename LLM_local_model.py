import requests
import re
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
from fpdf import FPDF
from docx import Document
import io
from PyPDF2 import PdfReader

#-------------------------------------------------
# Title of the application
st.markdown(
    "<h1 style='text-align: center;'>E-Exam Generator</h1>",
    unsafe_allow_html=True
)

# Header
st.text("Upload a document and AI will generate mcqs and short questions for you!")

#------------------------------------------------Functions & Crew

# Extract text from the PDF
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""  # Handle empty pages
    return text

# text cleaning
def preprocess_text(text):
    # Remove extra spaces and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Function to create a PDF file to download
def create_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=content)
    return pdf.output(dest="S").encode("latin1")  # Return PDF as bytes

# Function to create a Word file to download
def create_word(content):
    doc = Document()
    doc.add_paragraph(content)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()  # Return Word file as bytes

#----------------------------------------multi agents to generate mcqs and short questions
#Agent1 : Generate MCQs using the Mistral model via Ollama WebUI
def generate_mcqs(text, num_questions=5):
    """
    Sends the extracted text to the Mistral model running locally via Ollama WebUI
    to generate multiple-choice questions (MCQs).
    """
    # Ollama WebUI endpoint
    ollama_url = "http://localhost:11434/api/generate"  # Replace with your actual endpoint

    # Prepare the prompt for MCQ generation
    prompt = (
        f"Generate {num_questions} multiple-choice questions (MCQs) based on the following text:\n\n"
        f"{text}\n\n"
        "Each question should have 4 options and a correct answer. Format the output as:\n"
        "1. Question?\n"
        "   A) Option 1\n"
        "   B) Option 2\n"
        "   C) Option 3\n"
        "   D) Option 4\n"
        "   Correct Answer: A\n\n"
    )

    # Send the request to the Mistral model
    try:
        response = requests.post(
            ollama_url,
            json={
                "model": "llama3",  # Replace with the correct model name if different
                "prompt": prompt,
                "stream": False
            },
            proxies = {"http": None, "https": None}
        )

        if response.status_code == 200:
            return response.json().get("response", "No response generated.")
        else:
            raise Exception(f"Failed to generate MCQs. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        raise Exception(f"Error communicating with Ollama WebUI: {e}")

#--------------------------------------------------------------------------------------------------
#Agent2 : Generate short questions using the Mistral model via Ollama WebUI
def generate_short_qa(text, num_questions=5):
    """
    Sends the extracted text to the Mistral model running locally via Ollama WebUI
    to generate short questions.
    """
    # Ollama WebUI endpoint
    ollama_url = "http://localhost:11434/api/generate"  # Replace with your actual endpoint

    # Prepare the prompt for MCQ generation
    prompt = (
        f"Generate {num_questions} short question-answer pairs based on the following text:\n\n"
        f"{text}\n\n"
        "Format each pair as follows:\n"
        "1. Question?\n"
        "Answer: Answer here.\n\n"
    )
    # Send the request to the Mistral model
    try:
        response = requests.post(
            ollama_url,
            json={
                "model": "llama3",  # Replace with the correct model name if different
                "prompt": prompt,
                "stream": False
            },
            proxies = {"http": None, "https": None}
        )

        if response.status_code == 200:
            return response.json().get("response", "No response generated.")
        else:
            raise Exception(f"Failed to generate short Q&A. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        raise Exception(f"Error communicating with Ollama WebUI: {e}")

#------------------------------------------------main starts
#container = st.container(border=True)
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
if uploaded_file is not None:
    st.success("File uploaded successfully!")
    # Extract text from the PDF
    print("Extracting text from the PDF...")
    text = extract_text_from_pdf(uploaded_file)
    print("Text extraction complete.\n")

    # text cleaning
    cleaned_text = preprocess_text(text)
    print("Cleaned Text:", cleaned_text[:500])
    print("Text cleaning complete.\n")

    # Generate MCQs and short questions
    mcqs = generate_mcqs(cleaned_text, num_questions=5)
    print("Generated MCQs:\n", mcqs)

    # Generate Short Q&A
    short_questions = generate_short_qa(cleaned_text, num_questions=5)
    print("Generated Short Q&A:\n", short_questions)


# ------------------------------------------------
