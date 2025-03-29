from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SimilarityScorer:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def compute_similarity(self, text1: str, text2: str) -> float:
        if not text1.strip() or not text2.strip():
            return 0.0
        embeddings = self.model.encode([text1, text2])
        score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return round(float(score), 4)

    def clean_text(self, text):
        if isinstance(text, str):
            return text.lower().strip()
        return ""

    def normalize_list(self, items):
        cleaned = []
        for item in items:
            if isinstance(item, str):
                # Split comma-separated values
                sub_items = item.split(",")
                cleaned.extend([self.clean_text(x) for x in sub_items if x.strip()])
        return cleaned

    def average_structured_features(self, features: dict, keys: list) -> str:
        collected = []
        for key in keys:
            val = features.get(key)
            if isinstance(val, list):
                collected.extend(self.normalize_list(val))
            elif isinstance(val, str):
                collected.extend(self.normalize_list([val]))
        return ", ".join(collected)

    def score(self, jd_text: str, resume_text: str, jd_features: dict, resume_features: dict) -> dict:
        # 1. Full-text similarity
        text_similarity = self.compute_similarity(jd_text, resume_text)

        # 2. Structured attribute similarity (e.g., skills + responsibilities)
        jd_structured = self.average_structured_features(jd_features, ["required_skills", "job_responsibilities"])
        resume_structured = self.average_structured_features(resume_features, ["skills", "research_area"])

        structured_similarity = self.compute_similarity(jd_structured, resume_structured)

        return {
            "text_similarity": text_similarity,
            "structured_similarity": structured_similarity
        }
