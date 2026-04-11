import json
import re
import os
from typing import Dict, List


class NormalizationAgent:

    def __init__(self, taxonomy_path: str = None):
        
        if taxonomy_path is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))  
            taxonomy_path = os.path.join(base_dir, "taxonomy", "skills.json")

        print("📂 Using taxonomy path:", taxonomy_path)  # DEBUG

        self.taxonomy = self.load_taxonomy(taxonomy_path)
        print("Loaded taxonomy:", self.taxonomy)      # DEBUG

        self.synonym_map = self.build_synonym_map(self.taxonomy)
        print("Synonym map:", self.synonym_map)       # DEBUG
        # -------------------------------
        # Load taxonomy
        # -------------------------------
    def load_taxonomy(self, path: str) -> Dict:
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    # -------------------------------
    # Build synonym lookup
    # -------------------------------
    def build_synonym_map(self, taxonomy: Dict) -> Dict:
        synonym_map = {}

        for skill, data in taxonomy.items():
            synonym_map[skill.lower()] = skill

            for syn in data.get("synonyms", []):
                synonym_map[syn.lower()] = skill

        return synonym_map

    # -------------------------------
    # Normalize skills
    # -------------------------------
    def normalize_skills(self, extracted_skills: List[str]) -> Dict:
        normalized = []
        unknown_skills = []

        for skill in extracted_skills:
            key = skill.lower().strip()

            if key in self.synonym_map:
                canonical = self.synonym_map[key]
                normalized.append(self.build_skill_entry(canonical))
            else:
                unknown_skills.append(skill)

        return {
            "normalized_skills": normalized,
            "emerging_skills": unknown_skills
        }

    # -------------------------------
    # Build structured skill entry
    # -------------------------------
    def build_skill_entry(self, skill: str) -> Dict:
        data = self.taxonomy.get(skill, {})

        return {
            "skill": skill,
            "category": data.get("category"),
            "parent": data.get("parent"),
        }

    # -------------------------------
    # Infer higher-level skills
    # -------------------------------
    def infer_hierarchy(self, skills: List[str]) -> List[str]:
        inferred = set()

        if "TensorFlow" in skills or "PyTorch" in skills:
            inferred.add("Deep Learning")

        if "Deep Learning" in inferred:
            inferred.add("Machine Learning")

        return list(inferred)

    # -------------------------------
    # Estimate proficiency
    # -------------------------------
    def estimate_proficiency(self, resume_text: str, skills: List[str]) -> Dict:
        proficiency = {}

        for skill in skills:
            level = "unknown"

            # Simple rules (can be improved with LLM later)
            if re.search(rf"{skill}.*(\d+)\s+years", resume_text, re.IGNORECASE):
                level = "advanced"
            elif re.search(rf"familiar with {skill}", resume_text, re.IGNORECASE):
                level = "beginner"
            elif re.search(rf"experience with {skill}", resume_text, re.IGNORECASE):
                level = "intermediate"

            proficiency[skill] = level

        return proficiency

    # -------------------------------
    # Main normalize function
    # -------------------------------
    def normalize(self, parsed_data: Dict, resume_text: str) -> Dict:
        extracted_skills = parsed_data.get("skills", [])

        # Step 1: Normalize skills
        result = self.normalize_skills(extracted_skills)

        normalized_names = [s["skill"] for s in result["normalized_skills"]]

        # Step 2: Infer hierarchy
        inferred = self.infer_hierarchy(normalized_names)

        # Step 3: Estimate proficiency
        proficiency = self.estimate_proficiency(resume_text, normalized_names)

        return {
            "normalized_skills": result["normalized_skills"],
            "emerging_skills": result["emerging_skills"],
            "inferred_skills": inferred,
            "proficiency": proficiency
        }