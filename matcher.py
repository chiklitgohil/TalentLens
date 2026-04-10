from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')


def compute_match_score(candidate_skills, job_description):
    candidate_text = " ".join(candidate_skills)

    emb1 = model.encode(candidate_text, convert_to_tensor=True)
    emb2 = model.encode(job_description, convert_to_tensor=True)

    score = util.cos_sim(emb1, emb2).item()

    return round(score, 3)