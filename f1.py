import json
import os
from sklearn.metrics import f1_score

# Path to the folder containing JSON files
output_folder = 'output/'

# Path to pairs_labels_sample.txt
pairs_labels_file = 'pairs_labels_sample.txt'

# Read the pairs_labels_sample.txt file and store the ground truth, skipping line 109
ground_truth = []
with open(pairs_labels_file, 'r') as f:
    for index, line in enumerate(f, start=1):
        # Skip line 109
        if index == 109:
            print("Line 109 in pairs_lables_sample.txt is skipped.")
            continue

        # Split each line into JD, resume, and ground truth (True/False)
        _, _, label = line.strip().split()
        ground_truth.append(True if label.lower() == 'true' else False)

# List of JSON files in the output folder
json_files = [f for f in os.listdir(output_folder) if f.endswith('.json')]

# List to store the JD Match predictions
predictions = []

# Loop through each JSON file and extract JD Match prediction
for json_file in json_files:
    json_path = os.path.join(output_folder, json_file)
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Extract JD Match percentage (convert to binary)
        jd_match_percentage_str = data['response'].split('"JD Match": "')[1].split('"')[0]
        
        # Remove the percentage sign and convert to float
        jd_match_percentage = float(jd_match_percentage_str.replace('%', '').strip())
        
        # Convert JD Match percentage to binary (1 if JD Match >= 50, else 0)
        prediction = jd_match_percentage >= 50.0
        predictions.append(prediction)

# Compute F1 score
f1 = f1_score(ground_truth, predictions)

print(f"F1 Score: {f1:.4f}")