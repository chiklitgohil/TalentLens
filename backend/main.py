from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import docx
import io
import sys
import os

# Safely resolve the absolute path to ai_pipeline and prioritize it in the module search path
ai_pipeline_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai_pipeline"))
sys.path.insert(0, ai_pipeline_dir)

from pipeline import run_pipeline
from parser import extract_text_from_pdf, extract_text_from_docx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    file_bytes = await resume.read()
    
    if resume.filename.endswith(".pdf"):
        resume_text = extract_text_from_pdf(file_bytes)
    elif resume.filename.endswith(".docx"):
        resume_text = extract_text_from_docx(file_bytes)
    else:
        return {"error": "Only PDF and DOCX supported"}
    
    result = run_pipeline(resume_text, job_description)
    return result