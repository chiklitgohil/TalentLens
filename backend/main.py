from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# ✅ FIX: Proper path handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AI_PIPELINE_PATH = os.path.join(BASE_DIR, "../ai_pipeline")
sys.path.append(AI_PIPELINE_PATH)

from pipeline import run_pipeline
from parser import extract_text_from_pdf, extract_text_from_docx

app = FastAPI()

# ✅ Keep CORS (good)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    try:
        file_bytes = await resume.read()

        # ✅ safer file type check
        filename = resume.filename.lower()

        if filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(file_bytes)
        elif filename.endswith(".docx"):
            resume_text = extract_text_from_docx(file_bytes)
        else:
            return {"error": "Only PDF and DOCX supported"}

        result = run_pipeline(resume_text, job_description)

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }