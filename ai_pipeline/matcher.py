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
    
    # Print to the backend terminal for debugging
    print(f"\n--- DEBUG: JD EXTRACTION ---")
    print(f"Raw LLM Extraction: {raw_reqs}")
    print(f"Normalized for Matcher: {{'required': {required}, 'preferred': {preferred}}}\n")

    return {"required": required, "preferred": preferred}

def compute_match(parsed: dict, job_description: str) -> dict:
    # Get candidate skills as a single string
    candidate_skills = [
        s["canonical"] for s in parsed["candidate"]["normalised_skills"]
        if s["canonical"] != "Unknown"
    ]
    
    # Gap analysis
    jd_requirements = extract_jd_requirements(job_description)
    
    gaps = []
    matched_skills = []
    
    for req in jd_requirements.get("required", []):
        req_lower = req.lower()
        found = False
        for skill in candidate_skills:
            if skill.lower() in req_lower or req_lower in skill.lower():
                found = True
                if skill not in matched_skills:
                    matched_skills.append(skill)
                    
        if not found and len(req) > 1:
            gaps.append({
                "skill": req,
                "importance": "required"
            })
    
    for pref in jd_requirements.get("preferred", []):
        pref_lower = pref.lower()
        found = False
        for skill in candidate_skills:
            if skill.lower() in pref_lower or pref_lower in skill.lower():
                found = True
                if skill not in matched_skills:
                    matched_skills.append(skill)
                    
        if not found and len(pref) > 1:
            gaps.append({
                "skill": pref,
                "importance": "preferred"
            })
            
    # Semantic Embedding Similarity
    candidate_text = " ".join(candidate_skills) if candidate_skills else "unknown"
    candidate_embedding = model.encode(candidate_text)
    jd_embedding = model.encode(job_description)
    
    similarity = np.dot(candidate_embedding, jd_embedding) / (
        np.linalg.norm(candidate_embedding) * np.linalg.norm(jd_embedding)
    )
    semantic_score = float(similarity) * 100
    
    # Weighted Final Score (70% Explicit Skills, 30% Semantic Context)
    total_jd_skills = len(jd_requirements.get("required", [])) + len(jd_requirements.get("preferred", []))
    
    if total_jd_skills > 0:
        explicit_score = (len(matched_skills) / total_jd_skills) * 100
        match_score = round((explicit_score * 0.7) + (semantic_score * 0.3), 1)
    else:
        match_score = round(semantic_score, 1)
        
    match_score = min(match_score, 100.0) # Cap at 100% just in case
    
    return {
        "candidate": parsed["candidate"],
        "job_requirements": jd_requirements,  # Added to API response for debugging
        "match_score": match_score,
        "matched_skills": matched_skills,
        "gaps": gaps[:10]  # Limit to top 10 gaps
    }
