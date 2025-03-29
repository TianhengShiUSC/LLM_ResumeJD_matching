import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
from preprocess import LLMDataPreprocessor
from similiarityGenerator import SimilarityScorer
UNDER_DEVELOP = True

load_dotenv() ## load all our environment variables

genai.configure(api_key="AIzaSyAn8g2wYgTrjfW52LrlhR6V37tDewRsO9g")

def get_gemini_repsonse(input):
    model=genai.GenerativeModel('gemini-2.0-flash')
    response=model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader=pdf.PdfReader(uploaded_file)
    text=""
    for page in range(len(reader.pages)):
        page=reader.pages[page]
        text+=str(page.extract_text())
    return text

#Prompt Template

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


## streamlit app

with st.sidebar:
    st.title("Smart ATS for Resumes")
    st.subheader("About")
    st.write("This sophisticated ATS project, developed with Gemini Pro and Streamlit, seamlessly incorporates advanced features including resume match percentage, keyword analysis to identify missing criteria, and the generation of comprehensive profile summaries, enhancing the efficiency and precision of the candidate evaluation process for discerning talent acquisition professionals.")
    
    st.markdown("""
    - [Streamlit](https://streamlit.io/)
    - [Gemini Pro](https://deepmind.google/technologies/gemini/#introduction)
    - [makersuit API Key](https://makersuite.google.com/)
    - [Github](https://github.com/praj2408/End-To-End-Resume-ATS-Tracking-LLM-Project-With-Google-Gemini-Pro) Repository
                
    """)
    
    add_vertical_space(5)
    st.write("Made with ❤ by Prajwal Krishna.")
    
    


st.title("Smart Application Tracking System")
st.text("Improve Your Resume ATS")
jd=st.text_area("Paste the Job Description")
uploaded_file=st.file_uploader("Upload Your Resume",type="pdf",help="Please uplaod the pdf")

submit = st.button("Submit")
scorer = SimilarityScorer()

if submit:
    if uploaded_file is not None and jd:
        text = input_pdf_text(uploaded_file)
        # formatted_prompt = input_prompt.format(text=text, jd=jd)


        resume_text = input_pdf_text(uploaded_file)

        # Create instance of LLM preprocessor
        api_key = "AIzaSyAn8g2wYgTrjfW52LrlhR6V37tDewRsO9g"
        processor = LLMDataPreprocessor(jd_text=jd, resume_text=resume_text, api_key=api_key)
        processor.process()
        jd_features, resume_features = processor.get_features()

        scores = scorer.score(
            jd_text=jd,
            resume_text=text,
            jd_features=jd_features,
            resume_features=resume_features
        )
        if UNDER_DEVELOP:
            st.subheader("🔍 Similarity Scores")
            st.metric("Text Similarity", f"{scores['text_similarity']*100:.1f}%")
            st.metric("Structured Feature Similarity", f"{scores['structured_similarity']*100:.1f}%")

            # Display extracted features on web
            st.subheader("📄 Extracted Job Description Features")
            st.json(jd_features)

            st.subheader("👤 Extracted Resume Features")
            st.json(resume_features)
        formatted_prompt = input_prompt.format(
            text=text,
            jd=jd,
            jd_features=json.dumps(jd_features, indent=2),
            resume_features=json.dumps(resume_features, indent=2),
            text_score=scores['text_similarity'] * 100,
            structured_score=scores['structured_similarity'] * 100
        )

        response = get_gemini_repsonse(formatted_prompt)
        st.subheader("Gemini's Analysis")
        st.write(response)
    else:
        st.warning("Please make sure you've uploaded a resume and pasted the job description.")
