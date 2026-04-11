from parser import llm_extract_fields
from normalizer import NormalizationAgent
from matcher import compute_match

normalizer = NormalizationAgent()

def run_pipeline(resume_text: str, job_description: str) -> dict:
    # Step 1: Parse
    parsed = llm_extract_fields(resume_text)
    
    if not parsed.get("candidate"):
        parsed["candidate"] = {}

    # Step 2: Normalize
    skills = parsed["candidate"].get("skills") or []

    # ✅ FIX: safer extraction
    raw_skills = []
    for s in skills:
        if isinstance(s, dict) and s.get("raw"):
            raw_skills.append(s["raw"])

    normalised_result = normalizer.normalize({"skills": raw_skills}, resume_text)

    # ✅ FIX: ensure structure always exists
    parsed["candidate"]["normalised_skills"] = [
        {"canonical": s["skill"]}
        for s in normalised_result.get("normalized_skills", [])
    ]

    # ✅ fallback to avoid empty embedding crash
    if not parsed["candidate"]["normalised_skills"]:
        parsed["candidate"]["normalised_skills"] = [{"canonical": "Unknown"}]

    # Step 3: Match
    result = compute_match(parsed, job_description)

    return result