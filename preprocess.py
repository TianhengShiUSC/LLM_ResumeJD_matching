import google.generativeai as genai
import json

class LLMDataPreprocessor:
    def __init__(self, jd_text: str, resume_text: str, api_key: str):
        self.jd_text = jd_text
        self.resume_text = resume_text
        self.jd_features = {}
        self.resume_features = {}

        # Setup Gemini API
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro-latest")

    def extract_from_llm(self, prompt: str) -> dict:
        response = self.model.generate_content(prompt)
        raw = response.text.strip()

        # Remove markdown code block if present
        if raw.startswith("```json"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            print("⚠️ Failed to parse cleaned LLM response. Returning raw text.")
            return {"raw_response": raw}


    def extract_jd_features(self):
        jd_prompt = f"""
        Extract the following structured attributes from this job description:

        - Company name
        - Job title
        - Job Level(one of the following: entry-level, senior-level, management-level)
        - Required skills (as a list, use keywords-like format, exclude work condition(such as "must have computer"))
        - Job responsibilities (as a paragraph)

        Job Description:
        """
        jd_prompt += f""""{self.jd_text}"""

        jd_prompt += """

        Return your response in the following JSON format:
        {
          "company_name": "",
          "job_title": "",
          "required_skills": [],
          "job_responsibilities": ""
        }
        """

        self.jd_features = self.extract_from_llm(jd_prompt)

    def extract_resume_features(self):
        resume_prompt = f"""
        Extract the following attributes from the applicant's resume:

        - School name
        - GPA (if available)
        - Research area (if mentioned)
        - Job Level(one of the following: entry-level, senior-level, management-level) based on the exprience and skill.
        - Technical skills (as a list, dont simply check skills section, check experience to get the skills as well)

        Resume:
        """
        resume_prompt += f""""{self.resume_text}"""

        resume_prompt += """

        Return your response in this JSON format:
        {
          "school": "",
          "gpa": "",
          "research_area": "",
          "Job Level": "",
          "skills": []
        }
        """

        self.resume_features = self.extract_from_llm(resume_prompt)

    def process(self):
        self.extract_jd_features()
        self.extract_resume_features()

    def get_features(self):
        return self.jd_features, self.resume_features