skill_map = {
    "react.js": "react",
    "reactjs": "react",
    "ml": "machine learning"
}

# 🔥 Skill inference rules
skill_inference = {
    "tensorflow": ["deep learning"],
    "pytorch": ["deep learning"],
    "react": ["frontend"],
    "node.js": ["backend"]
}


def normalize_skills(skills):
    normalized = set()

    for skill in skills:
        s = skill.lower()
        s = skill_map.get(s, s)
        normalized.add(s)

        # 🔥 Add inferred skills
        if s in skill_inference:
            for inferred in skill_inference[s]:
                normalized.add(inferred)

    return list(normalized)