import os
import json
import re
from sklearn.metrics import f1_score, accuracy_score, recall_score, precision_score
import argparse

parser = argparse.ArgumentParser(description="Evaluate prediction results")
parser.add_argument('--mode', choices=['baseline', 'full'], required=True, help="Evaluation mode")
parser.add_argument('--label_file', default='pairs_labels_sample.txt', help="Path to label file")
args = parser.parse_args()

# Mode-based config
if args.mode == 'baseline':
    output_folder = 'output_baseline/'
    json_pattern = "{jd}_{resume}_baseline.json"
else:
    output_folder = 'output/'
    json_pattern = "{jd}_{resume}.json"

# Load available JSON filenames into a set for quick lookup
available_json_files = set(os.listdir(output_folder))

# Containers
predictions = []
ground_truth = []
wrong_lines = []

# Process each line in the label file
with open(args.label_file, 'r') as f:
    for index, line in enumerate(f, start=1):
        try:
            jd_path, resume_path, label = line.strip().split()
            jd_name = os.path.splitext(os.path.basename(jd_path))[0]
            resume_name = os.path.splitext(os.path.basename(resume_path))[0]
            json_filename = json_pattern.format(jd=jd_name, resume=resume_name)
        except Exception as e:
            print(f"[Line {index}] Failed to parse line: {line.strip()} — {e}")
            continue

        if json_filename not in available_json_files:
            print(f"[Line {index}] JSON not found: {json_filename}")
            continue

        json_path = os.path.join(output_folder, json_filename)
        try:
            with open(json_path, 'r', encoding='utf-8') as jf:
                data = json.load(jf)

            response_raw = data['response']
            response_clean = re.sub(r'^```json\n|```$', '', response_raw.strip(), flags=re.MULTILINE)
            response_json = json.loads(response_clean)

            jd_match_str = response_json.get("JD Match", "0")

            match = re.search(r'\d+(\.\d+)?', jd_match_str)
            if match:
                jd_match_score = float(match.group())
            else:
                raise ValueError(f"Could not extract float from: {jd_match_str}")

            prediction = jd_match_score >= 40.0

        except Exception as e:
            print(f"[{json_filename}] Failed to parse JD Match: {e}")
            continue

        true_label = label.lower() == 'true'
        predictions.append(prediction)
        ground_truth.append(true_label)

        if prediction != true_label:
            wrong_lines.append({
                "line_num": index,
                "json_file": json_filename,
                "true_label": true_label,
                "predicted": prediction,
                "line_content": line.strip()
            })

# Metrics
if predictions:
    f1 = f1_score(ground_truth, predictions)
    accuracy = accuracy_score(ground_truth, predictions)
    recall = recall_score(ground_truth, predictions)
    precision = precision_score(ground_truth, predictions)

    print("\n=== Evaluation Metrics ===")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    if wrong_lines:
        print("\n=== Wrong Predictions ===")
        for item in wrong_lines:
            print(f"[Line {item['line_num']}] {item['json_file']} | Pred: {item['predicted']} | True: {item['true_label']}")
            print(f"  → {item['line_content']}")
    else:
        print("\n✅ All predictions were correct.")
else:
    print("❌ No predictions were made. Please check your input files.")