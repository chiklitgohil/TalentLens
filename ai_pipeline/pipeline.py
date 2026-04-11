from parser import llm_extract_fields
from normalizer import NormalizationAgent
from matcher import compute_match

normalizer = NormalizationAgent()

def run_pipeline(resume_text: str, job_description: str) -> dict:
    # Step 1: Parse
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
    
    # Step 3: Match
    result = compute_match(parsed, job_description)
    
    return result