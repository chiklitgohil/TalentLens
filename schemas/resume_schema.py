RESUME_SCHEMA = {
    "name": "string | null",
    "email": "string | null",
    "phone": "string | null",
    "location": "string | null",
    "skills": [
        {
            "raw": "string",
            "normalized": "string"
        }
    ],
    "experience": [
        {
            "company": "string | null",
            "role": "string | null",
            "start_date": "string | null",
            "end_date": "string | null",
            "duration_months": "number | null",
            "responsibilities": ["string"]
        }
    ],
    "education": [
        {
            "institution": "string | null",
            "degree": "string | null",
            "field": "string | null",
            "year": "string | null"
        }
    ],
    "projects": [
        {
            "name": "string | null",
            "description": "string | null",
            "technologies": ["string"]
        }
    ]
}