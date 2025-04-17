#!/usr/bin/env python3
"""
Batch‑clean job description .txt files by removing generic / non‑technical requirements
using Google’s Gemini API, with retry logic and a secondary pass for any empty outputs.
"""

import os
import sys
import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, GoogleAPICallError

# ─── Configuration ─────────────────────────────────────────────────────────────
API_KEY     = "AIzaSyAn8g2wYgTrjfW52LrlhR6V37tDewRsO9g"  # ← replace this!
MODEL_NAME  = "gemini-2.0-flash"

input_dir   = "./data_folder/JD"
output_dir  = "./data_folder/cleaned_JD"
os.makedirs(output_dir, exist_ok=True)

MAX_RETRIES   = 5
INITIAL_DELAY = 2

CLEAN_PROMPT = """You are helping clean job descriptions.
Please remove any generic or non‑technical requirements, including but not limited to:
- Having a computer with internet access
- Quiet working area away from distractions
- Ability to work independently and get the job done
- Flexible hours or willingness to work overtime
- Reliable transportation to and from work
- Excellent communication or interpersonal skills
- Proficiency in Microsoft Office (Word, Excel, PowerPoint)
- Willingness to learn or eagerness to grow
- Ability to multitask or handle multiple priorities
- Positive attitude or self‑motivated
- Ability to lift/move up to XX lbs (if not role‑specific)
- Comfortable in a fast‑paced environment
- Team player mentality
- Detail‑oriented and highly organized
- Commitment to company values or culture fit

Keep only the role‑specific responsibilities, technical skills, and qualifications directly relevant to the job.  
Return the cleaned version of the input below:

--- INPUT START ---
{jd_text}
--- INPUT END ---
"""

def generate_with_retries(model, prompt, max_retries=MAX_RETRIES, initial_delay=INITIAL_DELAY):
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            resp = model.generate_content(prompt)
            return resp.text.strip()
        except ResourceExhausted:
            print(f"⚠️  Quota exhausted (429). Retry {attempt}/{max_retries} in {delay}s...")
            time.sleep(delay)
            delay *= 2
        except GoogleAPICallError as e:
            print(f"❌  API error on attempt {attempt}: {e}")
            break
    return ""

def retry_empty_files(model):
    empty = []
    for fname in os.listdir(input_dir):
        out_path = os.path.join(output_dir, fname)
        if not fname.lower().endswith(".txt"):
            continue
        if os.path.exists(out_path) and os.path.getsize(out_path) == 0:
            empty.append(fname)

    if not empty:
        return

    print(f"\n🔄 Retrying {len(empty)} empty file(s)...")
    for fname in empty:
        in_path  = os.path.join(input_dir, fname)
        out_path = os.path.join(output_dir, fname)
        jd_text = open(in_path, "r", encoding="utf-8").read().strip()
        # On retry, use the full text (not truncated)
        prompt  = CLEAN_PROMPT.format(jd_text=jd_text)
        cleaned = generate_with_retries(model, prompt)
        if cleaned:
            with open(out_path, "w", encoding="utf-8") as out_f:
                out_f.write(cleaned)
            print(f"✅  Retried and cleaned: {fname}")
        else:
            print(f"❌  Still empty after retry: {fname}")

def main():
    if API_KEY.startswith("YOUR_API_KEY"):
        sys.stderr.write("⚠️  Please set a valid API_KEY\n")
        sys.exit(1)

    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)

    for fname in os.listdir(input_dir):
        if not fname.lower().endswith(".txt"):
            continue

        in_path  = os.path.join(input_dir, fname)
        out_path = os.path.join(output_dir, fname)

        jd_text = open(in_path, "r", encoding="utf-8").read().strip()
        snippet = jd_text if len(jd_text) < 3000 else jd_text[:3000]

        prompt  = CLEAN_PROMPT.format(jd_text=snippet)
        cleaned = generate_with_retries(model, prompt)

        # write whatever (even empty) so we can detect it later
        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.write(cleaned)

        print(f"✅  Finished: {fname}")

    # second pass for any empty outputs
    retry_empty_files(model)

if __name__ == "__main__":
    main()
