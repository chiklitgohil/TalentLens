import fitz
from dotenv import load_dotenv
from google import genai
import json
from skills_db import skills_db
import os

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def extract_skills(text):
    text_lower = text.lower()
    found_skills = []

    for skill in skills_db:
        if skill in text_lower:
            found_skills.append(skill)

    return list(set(found_skills))


def simple_extract_fields(text):
    lines = text.split("\n")

    return {
        "name": lines[0] if lines else "Unknown",
        "skills": extract_skills(text)
    }


def extract_text_from_pdf(file_bytes):
    text = ""
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    for page in pdf:
        text += page.get_text()
    return text


def llm_extract_fields(text):
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
Extract structured information from this resume.

Return STRICT JSON only (no explanation):
{{
  "name": "",
  "skills": [],
  "experience": [
    {{"role": "", "years": 0}}
  ]
}}

Resume:
{text}
"""

    response = model.generate_content(prompt)

    content = response.text.strip()

    # 🔥 Clean JSON (important)
    try:
        # Remove ```json if present
        if content.startswith("```"):
            content = content.split("```")[1]

        return json.loads(content)
    except:
        return {
            "name": "Unknown",
            "skills": [],
            "experience": []
        }