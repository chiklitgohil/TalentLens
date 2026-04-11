from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.Client()

def extract_jd_requirements(job_description: str) -> dict:
    # Simple extraction: split JD into required and preferred
    # You can make this smarter with Gemini later if time allows
    lines = job_description.lower().split("\n")
    required = []
    preferred = []
    
    is_preferred_section = False
    for line in lines:
        if "preferred" in line or "nice to have" in line:
            is_preferred_section = True
        if "required" in line or "must have" in line:
            is_preferred_section = False
        
        if len(line.strip()) > 3:
            if is_preferred_section:
                preferred.append(line.strip())
            else:
                required.append(line.strip())
    
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
    for req in jd_requirements["required"]:
        found = any(skill in req or req in skill 
                   for skill in candidate_skill_names)
        if not found and len(req) > 3:
            gaps.append({
                "skill": req,
                "importance": "required"
            })
    
    for pref in jd_requirements["preferred"]:
        found = any(skill in pref or pref in skill 
                   for skill in candidate_skill_names)
        if not found and len(pref) > 3:
            gaps.append({
                "skill": pref,
                "importance": "preferred"
            })
    
    return {
        "candidate": parsed["candidate"],
        "match_score": match_score,
        "gaps": gaps[:10]  # Limit to top 10 gaps
    }
