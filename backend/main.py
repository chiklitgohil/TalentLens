from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import docx
import io
import sys
sys.path.append("../ai_pipeline")
from pipeline import run_pipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    return " ".join(page.get_text() for page in doc)

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return " ".join(para.text for para in doc.paragraphs)

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