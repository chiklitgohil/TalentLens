from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File
from parser import extract_text_from_pdf, extract_text_from_docx, simple_extract_fields
from normalizer import normalize_skills
from matcher import compute_match_score
from parser import llm_extract_fields
app = FastAPI()


@app.post("/match")
async def match_resume(file: UploadFile = File(...), job_description: str = ""):
    # Read file
    file_bytes = await file.read()

    # Parse resume
    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        text = extract_text_from_docx(file_bytes)
    else:
        return {"error": "Unsupported file format. Please upload a .pdf or .docx file."}

    parsed = llm_extract_fields(text)

    # Normalize skills
    normalized_skills = normalize_skills(parsed["skills"])

    # Compute match
    score = compute_match_score(normalized_skills, job_description)

    return {
        "name": parsed["name"],
        "skills": normalized_skills,
        "match_score": score
    }