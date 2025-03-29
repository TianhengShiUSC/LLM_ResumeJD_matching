# Resume-ATS-Tracking-LLM-Project-With-Google-Gemini-Pro (Forked & Enhanced)

## 🚀 Overview

This is a customized fork of the original [Gemini Pro ATS project](https://github.com/praj2408/End-To-End-Resume-ATS-Tracking-LLM-Project-With-Google-Gemini-Pro), enhanced with structured information extraction, cosine similarity scoring, visa sponsorship estimation, and offline CLI support.

---

## ✨ Features Added in This Fork

- ✅ LLM-based structured feature extraction (skills, GPA, school, responsibilities, etc.)
- ✅ Dual similarity scores: full-text + structured features
- ✅ Visa sponsorship assessment (explicit + heuristic-based)
- ✅ Offline command-line support with `app_offline.py`
- ✅ JSON output saved in `./output/`
- ✅ Batch processing via `run_batch.sh` script

---

## 📦 Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`
- Google Gemini Pro API key (via [Makersuite](https://makersuite.google.com/))

---

## ⚙️ Installation

```bash
git clone https://github.com/<your-username>/End-To-End-Resume-ATS-Tracking-LLM-Project-With-Google-Gemini-Pro
cd End-To-End-Resume-ATS-Tracking-LLM-Project-With-Google-Gemini-Pro

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

---

## 🔐 API Key Setup

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_google_api_key
```

---

## 🖥️ Run Web App (Optional)

```bash
streamlit run app.py
```

Open your browser at: http://localhost:8501

---

## ⚙️ Run Offline Inference

```bash
python app_offline.py --jd /abs/path/to/jd.txt --resume /abs/path/to/resume.pdf
```

Gemini will:
- Extract structured info
- Compute two cosine similarity scores
- Return a JSON-style evaluation
- Save to `./output/<jd>_<resume>.json`

---

## 📁 Output Example

```json
{
  "response": {
    "JD Match": "87%",
    "MissingKeywords": ["pytorch", "docker"],
    "Profile Summary": "...",
    "VisaSponsorshipAssessment": {
      "explicit_mention_in_jd": "no",
      "estimated_likelihood": "High",
      "reasoning": "Google usually sponsors interns in research/tech roles."
    }
  },
  "jd_features": { ... },
  "resume_features": { ... },
  "text_similarity": 0.87,
  "structured_similarity": 0.78
}
```

---

## 📂 Run Batch Inference

Create a `batch_input.txt` file like:

```
/path/to/jd1.txt /path/to/resume1.pdf T
/path/to/jd2.txt /path/to/resume2.pdf F
```

Run:

```bash
bash run_batch.sh batch_input.txt
```

---

## 📦 Ignored Files/Folders

This repo excludes the following folders from git tracking:

```
dummy_data/
output/
.env
```

---

## 🙏 Credits

Forked from [Prajwal Krishna’s original project](https://github.com/praj2408/End-To-End-Resume-ATS-Tracking-LLM-Project-With-Google-Gemini-Pro)

---

## 📝 License

MIT License

---

## 👤 Maintainer

Tianheng Shi  tshi9875@usc.edu


