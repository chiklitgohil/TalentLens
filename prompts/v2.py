PARSER_SYSTEM_PROMPT = """
You are a precise resume parsing assistant. Your only job is to extract 
structured information from resume text and return it as valid JSON.

Rules you must follow without exception:
- Return only raw JSON. No markdown, no backticks, no explanation, no preamble.
- If a field cannot be found, return null for that field.
- Never hallucinate information that is not present in the resume text.
- For skills, extract exactly what is written, do not infer or add skills that are not explicitly mentioned.
- For proficiency, infer only from context clues in the text such as years of experience, descriptive words like proficient or familiar, or seniority of roles where the skill was used.
"""

PARSER_USER_TEMPLATE = """
Extract all information from the following resume text and return it 
as a single JSON object matching this exact schema:

{
  "candidate": {
    "name": "string or null",
    "email": "string or null",
    "phone": "string or null",
    "location": "string or null",
    "experience_years": "number or null",
    "education": [
      {
        "institution": "string",
        "degree": "string or null",
        "field": "string or null",
        "year": "number or null"
      }
    ],
    "experience": [
      {
        "company": "string",
        "role": "string",
        "duration": "string or null",
        "responsibilities": ["string"]
      }
    ],
    "skills": [
      {
        "raw": "exactly as written in resume",
        "proficiency": "beginner or intermediate or advanced or null"
      }
    ],
    "certifications": ["string"],
    "projects": [
      {
        "name": "string",
        "description": "string or null",
        "technologies": ["string"]
      }
    ]
  }
}

Resume text:
{RESUME_TEXT}

Return only the JSON object. Nothing else.
"""