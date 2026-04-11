from parser import llm_extract_fields
from normalizer import NormalizationAgent
from matcher import compute_match

normalizer = NormalizationAgent()

def parse_resume_text(resume_text: str) -> dict:
    parsed = llm_extract_fields(resume_text)
    
    # Ensure candidate dict exists to prevent NoneType errors
    if not parsed.get("candidate"):
        parsed["candidate"] = {}

    # Step 2: Normalise
    # Extract raw skills list to feed into the normalizer
    skills = parsed["candidate"].get("skills") or []
    raw_skills = [s.get("raw", "") for s in skills if isinstance(s, dict) and s.get("raw")]
    normalised_result = normalizer.normalize({"skills": raw_skills}, resume_text)
    
    # Attach normalised skills to the parsed payload as expected by the matcher
    parsed["candidate"]["normalised_skills"] = [{"canonical": s["skill"]} for s in normalised_result.get("normalized_skills", [])]
    
    return parsed

def match_pipeline(parsed_data: dict, job_description: str) -> dict:
    return compute_match(parsed_data, job_description)

def run_pipeline(resume_text: str, job_description: str) -> dict:
    # Kept for backwards compatibility if needed
    parsed = parse_resume_text(resume_text)
    result = match_pipeline(parsed, job_description)
    
    return result