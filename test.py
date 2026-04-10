from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts.parser_prompt import PARSER_SYSTEM_PROMPT, PARSER_USER_TEMPLATE
import json
import fitz #PyMu
import docx
import os

load_dotenv()

# The new client automatically picks up GOOGLE_API_KEY from the environment
client = genai.Client()

def parse_resume(resume_text: str):
    user_prompt = PARSER_USER_TEMPLATE.format(resume_text=resume_text)

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview", 
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=PARSER_SYSTEM_PROMPT,
            response_mime_type="application/json",
        )
    )
    return response.text

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

if __name__ == "__main__":
    # Replace this with the path to a real PDF or DOCX file
    sample_file = "Chiklit-Gohil-Resume.pdf"
    
    if os.path.exists(sample_file):
        print(f"Extracting text from {sample_file}...")
        extracted_text = extract_text(sample_file)
        print("Parsing extracted text with Gemini...\n")
        print(parse_resume(extracted_text))
    else:
        print(f"Please place a '{sample_file}' in the project root to test.")
