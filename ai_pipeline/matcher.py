from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')


def compute_match_score(candidate_skills, job_description):
    candidate_text = " ".join(candidate_skills)

    emb1 = model.encode(candidate_text, convert_to_tensor=True)
    emb2 = model.encode(job_description, convert_to_tensor=True)

    score = util.cos_sim(emb1, emb2).item()

    # 🔥 Boost if direct overlap exists
    overlap = sum(1 for skill in candidate_skills if skill in job_description.lower())
    score += 0.05 * overlap

    return round(min(score, 1.0), 3)