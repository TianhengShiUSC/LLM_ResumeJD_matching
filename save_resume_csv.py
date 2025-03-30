import json
import pandas as pd
import re

# Load the raw JSON file (list of strings with embedded JSON blocks)
with open("resume_features.json", "r") as f:
    raw_resume_content = f.read()

# Parse the list of strings
raw_json_blocks = json.loads(raw_resume_content)

# Extract and decode each embedded JSON object
parsed_resumes = []
for block in raw_json_blocks:
    match = re.search(r'```json\s*(\{.*?\})\s*```', block, re.DOTALL)
    if match:
        try:
            resume = json.loads(match.group(1))
            parsed_resumes.append(resume)
        except json.JSONDecodeError:
            continue  # skip invalid JSON

# Convert to a DataFrame
resumes_df = pd.DataFrame(parsed_resumes)

# Save as CSV
resumes_df.to_csv("resume_features.csv", index=False)
