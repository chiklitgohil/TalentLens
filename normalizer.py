skill_map = {
    "react.js": "react",
    "reactjs": "react",
    "ml": "machine learning",
    "machine learning": "machine learning",
    "js": "javascript"
}


def normalize_skills(skills):
    normalized = []
    for skill in skills:
        s = skill.lower()
        normalized.append(skill_map.get(s, s))
    return list(set(normalized))