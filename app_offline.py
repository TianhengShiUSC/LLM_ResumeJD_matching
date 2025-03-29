import argparse
import json
import os
import PyPDF2 as pdf
import google.generativeai as genai
from dotenv import load_dotenv
from preprocess import LLMDataPreprocessor
from similiarityGenerator import SimilarityScorer

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY") or "AIzaSyAn8g2wYgTrjfW52LrlhR6V37tDewRsO9g"
genai.configure(api_key=api_key)

# Prompt Template
input_prompt = """
Hey, act like a highly skilled Applicant Tracking System (ATS) with deep knowledge of the tech hiring process. 
Evaluate the resume against the given job description. In addition to the raw texts, I am providing:
- Extracted structured features from both the job description and the resume
- Cosine similarity scores (full text and structured features)

Use all of this information to provide an accurate and thorough evaluation. 
Your analysis should reflect both the overall content match and the alignment of key skills and qualifications.

Job Description (Raw):
{jd}

Resume (Raw):
{text}

Extracted Job Description Features:
{jd_features}

Extracted Resume Features:
{resume_features}

Text Similarity Score: {text_score:.2f}
Structured Feature Similarity Score: {structured_score:.2f}

Now, based on the above, respond in the following JSON format:
{{
  "JD Match": "%",
  "MissingKeywords": [],
  "Profile Summary": "",
  "VisaSponsorshipAssessment": {{
    "explicit_mention_in_jd": "<yes/no/unclear>",
    "estimated_likelihood": "<Low/Medium/High>",
    "reasoning": "<In under 40 words, explain your reasoning. Assume that large tech firms like Google, Meta, and Microsoft typically offer visa sponsorship, especially for research or engineering internships. If the JD is silent on sponsorship, rely on company and role heuristics.>"
  }}
}}
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
    os.makedirs("output", exist_ok=True)
    jd_name = os.path.splitext(os.path.basename(jd_path))[0]
    resume_name = os.path.splitext(os.path.basename(resume_path))[0]
    output_file = f"output/{jd_name}_{resume_name}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Saved output to {output_file}\n")

def main(jd_path, resume_path):
    with open(jd_path, 'r', encoding='utf-8') as f:
        jd_text = f.read()

    resume_text = extract_text_from_pdf(resume_path)

    # Preprocess
    processor = LLMDataPreprocessor(jd_text=jd_text, resume_text=resume_text, api_key=api_key)
    processor.process()
    jd_features, resume_features = processor.get_features()

    # Similarity
    scorer = SimilarityScorer()
    scores = scorer.score(
        jd_text=jd_text,
        resume_text=resume_text,
        jd_features=jd_features,
        resume_features=resume_features
    )

    # Format prompt
    formatted_prompt = input_prompt.format(
        text=resume_text,
        jd=jd_text,
        jd_features=json.dumps(jd_features, indent=2),
        resume_features=json.dumps(resume_features, indent=2),
        text_score=scores['text_similarity'] * 100,
        structured_score=scores['structured_similarity'] * 100
    )

    # Get Gemini Response
    print("\n================ Gemini ATS Evaluation ================")
    response = get_gemini_response(formatted_prompt)
    print(response)
    print("=======================================================\n")

    # Save output
    output_data = {
        "response": response,
        "jd_features": jd_features,
        "resume_features": resume_features,
        "text_similarity": scores['text_similarity'],
        "structured_similarity": scores['structured_similarity']
    }
    save_output(jd_path, resume_path, output_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Offline ATS Resume Evaluator with Gemini")
    parser.add_argument("--jd", required=True, help="Absolute path to job description .txt file")
    parser.add_argument("--resume", required=True, help="Absolute path to resume .pdf file")
    args = parser.parse_args()
    main(args.jd, args.resume)
