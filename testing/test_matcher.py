from ai_pipeline.matcher import compute_match
from ai_pipeline.normalizer import NormalizationAgent

# Initialize normalizer
normalizer = NormalizationAgent()

# Sample parsed data
parsed_data = {
    "candidate": {
        "normalised_skills": [
            {"canonical": "Python"},
            {"canonical": "JavaScript"},
            {"canonical": "Kubernetes"},
            {"canonical": "PyTorch"}
        ]
    }
}

resume_text = "I have 5 years of Python experience and worked with PyTorch."

# Normalize if needed
normalized = parsed_data

# Job description
job_description = """
Looking for a developer with experience in Python, JavaScript, Docker, and Kubernetes.
Must have knowledge of Machine Learning and PyTorch.
"""

# Match
result = compute_match(normalized, job_description)

print("\n=== MATCH RESULT ===\n")
print(result)