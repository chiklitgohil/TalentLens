from fastapi import FastAPI, UploadFile, File
from parser import extract_text_from_pdf, simple_extract_fields
from normalizer import normalize_skills
from matcher import compute_match_score

app = FastAPI()


@app.post("/match")
async def match_resume(file: UploadFile = File(...), job_description: str = ""):
    # Read file
    file_bytes = await file.read()

    # Parse resume
    text = extract_text_from_pdf(file_bytes)
    parsed = simple_extract_fields(text)

    # Normalize skills
    normalized_skills = normalize_skills(parsed["skills"])

    # Compute match
    score = compute_match_score(normalized_skills, job_description)

    return {
        "name": parsed["name"],
        "skills": normalized_skills,
        "match_score": score
    }