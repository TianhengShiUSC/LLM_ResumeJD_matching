import argparse
import json
import os
import PyPDF2 as pdf
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Prompt Template (Baseline)
input_prompt = """
Hey Act Like a skilled or very experience ATS(Application Tracking System)
with a deep understanding of tech field,software engineering,data science ,data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving thr resumes. Assign the percentage Matching based 
on Jd and
the missing keywords with high accuracy
resume:{text}
description:{jd}

I want the response as per below structure
{{"JD Match": "%", "MissingKeywords": [], "Profile Summary": ""}}
"""

def get_gemini_response(prompt):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text

def extract_text_from_pdf(file_path):
    reader = pdf.PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def save_output(jd_path, resume_path, output_data):
    os.makedirs("output_baseline", exist_ok=True)
    jd_name = os.path.splitext(os.path.basename(jd_path))[0]
    resume_name = os.path.splitext(os.path.basename(resume_path))[0]
    output_file = f"output_baseline/{jd_name}_{resume_name}_baseline.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Saved output to {output_file}\n")

def main(jd_path, resume_path, api_key):
    genai.configure(api_key=api_key)
    with open(jd_path, 'r', encoding='utf-8') as f:
        jd_text = f.read()

    resume_text = extract_text_from_pdf(resume_path)

    # Format prompt (Baseline)
    formatted_prompt = input_prompt.format(text=resume_text, jd=jd_text)

    # Get Gemini Response
    print("\n================ Gemini ATS Evaluation (Baseline) ================")
    response = get_gemini_response(formatted_prompt)
    print(response)
    print("=================================================================")

    # Save output
    output_data = {
        "response": response,
        "jd_text": jd_text,
        "resume_text": resume_text
    }
    save_output(jd_path, resume_path, output_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Baseline ATS Resume Evaluator with Gemini")
    parser.add_argument("--jd", required=True, help="Absolute path to job description .txt file")
    parser.add_argument("--resume", required=True, help="Absolute path to resume .pdf file")
    parser.add_argument("--api_key", required=True, help="Gemini API key")
    args = parser.parse_args()
    main(args.jd, args.resume, args.api_key)