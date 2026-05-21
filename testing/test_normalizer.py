from ai_pipeline.normalizer import NormalizationAgent

# Initialize agent
agent = NormalizationAgent()

# Simulated parser output (large and realistic)
parsed_data = {
    "skills": [
        "Python", "JS", "K8s", "PyTorch", "TensorFlow",
        "React", "Node.js", "MongoDB", "AWS", "Docker",
        "Git", "SQL", "Postgres", "HTML", "CSS",
        "Flask", "Django", "FastAPI", "NumPy", "Pandas",
        "UnknownSkill1", "UnknownSkill2", "C++", "Java",
        "Machine Learning", "Deep Learning", "NLP"
    ]
}

# Simulated resume text
resume_text = """
I have 5 years of experience in Python and 3 years in JavaScript.
Worked with React and Node.js for building web applications.
Experience with Docker and Kubernetes (K8s) in production.
Familiar with TensorFlow and PyTorch.
Used Pandas and NumPy for data analysis.
Experience with AWS cloud services.
Worked on NLP and Deep Learning projects.
"""

# Run normalization
result = agent.normalize(parsed_data, resume_text)

# Pretty print results
print("\n================= FINAL RESULT =================\n")

print("NORMALIZED SKILLS:")
for skill in result["normalized_skills"]:
    print(skill)

print("\nEMERGING / UNKNOWN SKILLS:")
print(result["emerging_skills"])

print("\nINFERRED SKILLS:")
print(result["inferred_skills"])

print("\nPROFICIENCY:")
for skill, level in result["proficiency"].items():
    print(f"{skill}: {level}")

print("\n===============================================\n")