from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sys
import os

# Safely resolve the absolute path to ai_pipeline and prioritize it in the module search path
ai_pipeline_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai_pipeline"))
sys.path.insert(0, ai_pipeline_dir)

from pipeline import run_pipeline
from parser import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from normalizer import NormalizationAgent

app = FastAPI()

# ✅ Keep CORS (good)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

normalizer = NormalizationAgent()

@app.get("/api/v1/skills/taxonomy")
async def get_taxonomy():
    return {"taxonomy": normalizer.taxonomy}

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
        elif filename.endswith(".txt"):
            resume_text = extract_text_from_txt(file_bytes)
        else:
            return {"error": "Only PDF, DOCX, and TXT supported"}

        result = run_pipeline(resume_text, job_description)
        return result

    except Exception as e:
        return {"error": str(e)}

# Mount the frontend directory to serve the UI at the root (http://localhost:8000/)
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
