"""The web page. Run with:  streamlit run app.py"""
import streamlit as st
from parser import extract_text
from screener import screen

st.set_page_config(page_title="AI Resume Screener", page_icon="📄", layout="wide")
st.title("📄 AI Resume Screening System")
st.caption("Upload a resume → extract skills → compare with job requirements → get a suitability score")

left, right = st.columns(2)
with left:
    st.subheader("1. Upload resume")
    resume_file = st.file_uploader("PDF, DOCX or TXT", type=["pdf", "docx", "txt"])
with right:
    st.subheader("2. Paste job description")
    job_text = st.text_area("Job requirements", height=220,
                            placeholder="e.g. We need a Python developer with 3+ years of experience in Django, SQL, Docker and AWS...")

if st.button("Screen resume", type="primary"):
    if not resume_file or not job_text.strip():
        st.warning("Please upload a resume and paste a job description.")
    else:
        resume_text = extract_text(resume_file)
        if not resume_text.strip():
            st.error("Could not read any text from this file (scanned image PDFs are not supported).")
        else:
            r = screen(resume_text, job_text)
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("Overall score", f"{r['score']} / 100")
            c2.metric("Skill match", f"{r['skill_match_pct']}%")
            c3.metric("Experience", f"{r['resume_years']} yrs" + (f" (needs {r['job_years']})" if r['job_years'] else ""))
            st.progress(min(int(r["score"]), 100))

            if r["score"] >= 75:
                st.success(f"Prediction: {r['verdict']}")
            elif r["score"] >= 55:
                st.info(f"Prediction: {r['verdict']}")
            else:
                st.error(f"Prediction: {r['verdict']}")

            a, b, c = st.columns(3)
            a.markdown("**✅ Matched skills**")
            a.write(", ".join(r["matched"]) or "None")
            b.markdown("**❌ Missing skills**")
            b.write(", ".join(r["missing"]) or "None")
            c.markdown("**➕ Extra skills**")
            c.write(", ".join(r["extra"]) or "None")

            with st.expander("Extracted resume text"):
                st.text(resume_text)
