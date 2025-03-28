import pandas as pd
import numpy as np
import json
from preprocess import LLMDataPreprocessor

file_path = r"D:\VScode\Code\CSCI544\ResumeJDProject\OurOwnCode\Dataset\Resume.csv"

# Read the CSV file
df = pd.read_csv(file_path)

# Extract the "Resume_str" column and convert it to a 1D NumPy array
resume_array = np.array(df["Resume_str"])

cleaned_resumes = np.array([resume.strip().replace('\n', ' ').replace('  ', ' ').replace('\t', ' ') for resume in resume_array])

# Print the number of resumes and a sample to verify
#print("Number of people:", len(cleaned_resumes))
#print("Sample of Resume_str array:", cleaned_resumes[:1])  # Display first 1 resumes


import google.generativeai as genai
from tqdm import tqdm 

genai.configure(api_key="AIzaSyCqhPd6wk9WsphB3iAH5C1DlZ21ExKkKFY")
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Constructing the resume prompt dynamically
prompt_beginning = """
Extract the following attributes from the applicant's resume:

- School name
- GPA (if available)
- Research area (if mentioned)
- Technical skills (as a list)

Resume:
"""

# Adding instructions for the expected output format
prompt_ending = """

Return your response in this JSON format:
{
  "school": "",
  "gpa": "",
  "research_area": "",
  "skills": []
}
"""

resume_features = []
for resume_text in tqdm(cleaned_resumes, desc="Processing Resumes", unit="resume"):
    llm_input = prompt_beginning + resume_text + prompt_ending
    llm_output = model.generate_content(llm_input).text
    resume_features.append(llm_output)

# Save results as JSON
output_file = "resume_features.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(resume_features, f, indent=4)

print(f"✅ Results saved to {output_file}")