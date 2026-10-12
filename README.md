# AI Resume Screening System

Upload a resume, extract skills, compare with job requirements, and get a suitability score.

**Live demo:** PASTE-YOUR-STREAMLIT-LINK-HERE

**Tech:** Python, Streamlit, scikit-learn (TF-IDF), pdfplumber, python-docx

**How it works:**
1. Reads PDF, DOCX or TXT resumes
2. Extracts skills using a custom skill dictionary
3. Compares them with the job description
4. Scores 0-100: skill match 60%, text similarity 25%, experience 15%
