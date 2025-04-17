import pandas as pd
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# === Load Data ===
job_df = pd.read_csv("training_data.csv")               # Job file
resume_df = pd.read_csv("resume_features.csv")          # Resume file

# === Prepare Text for TF-IDF ===
job_corpus = job_df['job_description'].fillna('').astype(str).tolist()

# Ensure 'skills' column is list-like, then join into strings
resume_corpus = resume_df['skills'].fillna('').apply(
    lambda x: ' '.join(ast.literal_eval(x)) if isinstance(x, str) and x.startswith('[') else str(x)
).tolist()

# === TF-IDF Vectorization ===
all_text = job_corpus + resume_corpus
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(all_text)

job_vectors = tfidf_matrix[:len(job_corpus)]
resume_vectors = tfidf_matrix[len(job_corpus):]

# === Cosine Similarity ===
similarities = cosine_similarity(job_vectors, resume_vectors)

# === Top 10 Matches for Each Job ===
results = []
for job_idx, sims in enumerate(similarities):
    top_indices = sims.argsort()[-10:][::-1]
    for rank, idx in enumerate(top_indices):
        results.append({
            'job_index': job_idx,
            'resume_index': idx,
            'rank': rank + 1,
            'similarity': float(sims[idx])
        })

# === Top 6 Best and 4 Worst Matches for Each Job ===
mixed_result = []
for job_idx, sims in enumerate(similarities):
    sorted_indices = sims.argsort()  # Ascending order

    # Bottom 4 (least similar)
    bottom_indices = sorted_indices[:4]
    for rank, idx in enumerate(bottom_indices):
        mixed_result.append({
            'job_index': job_idx,
            'resume_index': idx,
            'rank': -(rank + 1),  # negative rank to indicate 'worst'
            'similarity': float(sims[idx]),
            'match_type': 'worst'
        })

    # Top 6 (most similar)
    top_indices = sorted_indices[-6:][::-1]
    for rank, idx in enumerate(top_indices):
        mixed_result.append({
            'job_index': job_idx,
            'resume_index': idx,
            'rank': rank + 1,
            'similarity': float(sims[idx]),
            'match_type': 'best'
        })

# === Convert to DataFrame ===
matches_df = pd.DataFrame(results)
mixed_df = pd.DataFrame(mixed_result)

# === Merge Job Descriptions ===
matches_df = matches_df.merge(job_df[['job_description']], left_on='job_index', right_index=True, how='left')
mixed_df = mixed_df.merge(job_df[['job_description']], left_on='job_index', right_index=True, how='left')

# === Merge Resume Info ===
matches_df = matches_df.merge(resume_df, left_on='resume_index', right_index=True, how='left')
mixed_df = mixed_df.merge(resume_df, left_on='resume_index', right_index=True, how='left')

# === Save Final Output ===
matches_df.to_csv("job_resume_top10_with_full_details.csv", index=False)
mixed_df.to_csv("job_resume_top6_bottom4_with_full_details.csv", index=False)
