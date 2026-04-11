from parser import parse_resume
from normalizer import normalise_skills
from matcher import match_candidate

def run_pipeline(resume_text: str, job_description: str) -> dict:
    # Step 1: Parse
    parsed = parse_resume(resume_text)
    
    # Step 2: Normalise
    normalised = normalise_skills(parsed)
    
    # Step 3: Match
    result = match_candidate(normalised, job_description)
    
    return result