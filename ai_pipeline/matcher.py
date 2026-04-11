from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np
from parser import llm_extract_jd_skills
from normalizer import NormalizationAgent

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.Client()
normalizer = NormalizationAgent()

def extract_jd_requirements(job_description: str) -> dict:
    # Smarter extraction using Gemini LLM to parse out specific skills instead of entire lines
    raw_reqs = llm_extract_jd_skills(job_description)
    
    # Normalize JD skills to perfectly match the candidate's taxonomy
    req_norm = normalizer.normalize_skills(raw_reqs.get("required", []))
    pref_norm = normalizer.normalize_skills(raw_reqs.get("preferred", []))
    
    # Combine canonical taxonomy skills with any emerging/unknown skills
    required = [s["skill"] for s in req_norm["normalized_skills"]] + req_norm["emerging_skills"]
    preferred = [s["skill"] for s in pref_norm["normalized_skills"]] + pref_norm["emerging_skills"]
    
    return {"required": required, "preferred": preferred}

def compute_match(parsed: dict, job_description: str) -> dict:
    # Get candidate skills as a single string
    candidate_skills = [
        s["canonical"] for s in parsed["candidate"]["normalised_skills"]
        if s["canonical"] != "Unknown"
    ]
    candidate_text = " ".join(candidate_skills) if candidate_skills else "unknown"
    
    # Embed both
    candidate_embedding = model.encode(candidate_text)
    jd_embedding = model.encode(job_description)
    
    # Cosine similarity
    similarity = np.dot(candidate_embedding, jd_embedding) / (
        np.linalg.norm(candidate_embedding) * np.linalg.norm(jd_embedding)
    )
    match_score = round(float(similarity) * 100, 1)
    
    # Gap analysis
    jd_requirements = extract_jd_requirements(job_description)
    candidate_skill_names = [s.lower() for s in candidate_skills]
    
    gaps = []
    for req in jd_requirements.get("required", []):
        req_lower = req.lower()
        found = any(skill in req_lower or req_lower in skill 
                   for skill in candidate_skill_names)
        if not found and len(req) > 1:
            gaps.append({
                "skill": req,
                "importance": "required"
            })
    
    for pref in jd_requirements.get("preferred", []):
        pref_lower = pref.lower()
        found = any(skill in pref_lower or pref_lower in skill 
                   for skill in candidate_skill_names)
        if not found and len(pref) > 1:
            gaps.append({
                "skill": pref,
                "importance": "preferred"
            })
    
    return {
        "candidate": parsed["candidate"],
        "match_score": match_score,
        "gaps": gaps[:10]  # Limit to top 10 gaps
    }
