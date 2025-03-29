import pandas as pd
from sklearn.metrics import f1_score

# Function to read dummy_data.txt and extract labels
def read_labels_from_txt(file_path):
    data = []
    with open(file_path, "r") as f:
        for line in f:
            parts = line.strip().split(" ")
            if len(parts) == 3:  # Ensure correct format
                data.append((parts[0], parts[1], parts[2]))  # JD path, Resume path, Label
    return pd.DataFrame(data, columns=["jd_path", "resume_path", "label"])

# Load ground truth labels from dummy_data.txt (BERT labels)
bert_labels_df = read_labels_from_txt(r"LLM_ResumeJD_matching/dummy_data.txt")
bert_labels_df["label"] = bert_labels_df["label"].map({"T": 1, "F": 0})  # Convert to binary

# Load LLM-generated labels (Assume stored in a similar format)r
llm_labels_df = read_labels_from_txt(r"path/to/llm_predictions.txt")
llm_labels_df["label"] = llm_labels_df["label"].map({"T": 1, "F": 0})  # Convert to binary

# Merge both dataframes on JD and Resume paths (ensure alignment)
merged_df = pd.merge(bert_labels_df, llm_labels_df, on=["jd_path", "resume_path"], suffixes=("_bert", "_llm"))

# Compute F1-score
f1 = f1_score(merged_df["label_bert"], merged_df["label_llm"])
print(f"F1-score: {f1:.4f}")
