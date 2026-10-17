"""AI Resume Screener v2.  Run with:  python -m streamlit run app.py"""
import hashlib
import io
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

from jobs_db import JOB_PRESETS
from parser import LEVEL_LABELS, candidate_info, extract_text_from_bytes
from screener import DEFAULT_WEIGHTS, analyze_job, score_candidate

# ---- change the name here and it updates everywhere ----
APP_NAME = "TalentLens"
TAGLINE = "Upload resumes → extract skills and details → compare with the job → rank candidates"

try:                                             # logo.png sits next to this file
    LOGO = Image.open(Path(__file__).parent / "logo.png")
except Exception:
    LOGO = None

st.set_page_config(page_title=f"{APP_NAME} | AI Resume Screener",
                   page_icon=LOGO if LOGO else "📄", layout="wide")

PRESETS = JOB_PRESETS                            # the example jobs live in jobs_db.py


@st.cache_data(show_spinner=False)
def read_resume(name: str, data: bytes) -> str:
    return extract_text_from_bytes(name, data)


def load_preset():
    text = PRESETS.get(st.session_state.get("preset", ""), "")
    if text:
        st.session_state["jd"] = text


def chips(items):
    return " ".join(f"`{i}`" for i in items) if items else "none"


def to_excel(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Ranking")
    return buf.getvalue()


st.session_state.setdefault("jd", "")

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    st.subheader("Score weights")
    st.caption("They are scaled to add up to 100%, so only the balance matters.")
    w_skills = st.slider("Skills match", 0, 100, DEFAULT_WEIGHTS["skills"])
    w_sim = st.slider("Wording similarity", 0, 100, DEFAULT_WEIGHTS["similarity"])
    w_exp = st.slider("Experience", 0, 100, DEFAULT_WEIGHTS["experience"])
    w_edu = st.slider("Education", 0, 100, DEFAULT_WEIGHTS["education"])

    st.subheader("Prediction cut-offs")
    strong_cut = st.slider("Strong fit from", 0, 100, 75)
    moderate_cut = st.slider("Moderate fit from", 0, 100, 55)
    weak_cut = st.slider("Weak fit from", 0, 100, 35)

    st.subheader("Your own skills")
    custom_text = st.text_input("Extra skills to look for (comma separated)",
                                placeholder="wine service, cocktail making")
    st.caption("🔒 Files are read in memory for this session only. Nothing is saved.")

weights = {"skills": w_skills, "similarity": w_sim, "experience": w_exp, "education": w_edu}
if sum(weights.values()) == 0:
    st.sidebar.warning("All weights are 0, so every score will be 0. Raise at least one slider.")
cutoffs = (strong_cut, moderate_cut, weak_cut)
extra = tuple(s.strip().lower() for s in custom_text.split(",") if s.strip())

# ------------------------------------------------------------------ inputs
head_logo, head_text = st.columns([1, 12])
if LOGO:
    head_logo.image(LOGO, width=80)
head_text.title(APP_NAME)
head_text.caption(TAGLINE)

left, right = st.columns(2)
with left:
    st.subheader("1. Upload resumes")
    files = st.file_uploader("PDF, DOCX or TXT. Select as many as you like.",
                             type=["pdf", "docx", "txt"], accept_multiple_files=True)
with right:
    st.subheader("2. Job description")
    st.selectbox("Load an example job", list(PRESETS), key="preset", on_change=load_preset,
                 help=f"{len(PRESETS) - 1} example jobs. Click and type to search, e.g. 'nurse' or 'python'.")
    jd = st.text_area("Paste the job description", key="jd", height=200,
                      placeholder="e.g. We need a Python developer with 3+ years of experience "
                                  "in Django, SQL, Docker and AWS...")

if not files or not jd.strip():
    st.info("👆 Upload one or more resumes and paste (or pick) a job description to start.")
    st.stop()

# ------------------------------------------------------------------ requirements
detected = analyze_job(jd, extra)
h = hashlib.md5((jd + "|".join(extra)).encode()).hexdigest()[:8]

st.subheader("3. Fine-tune the requirements")
if not detected["skills"]:
    st.warning("No known skills were found in this job description, so the score will rely on "
               "wording, experience and education only. Add skills in the sidebar or use the "
               "job's usual keywords.")
c1, c2, c3 = st.columns([3, 1, 1])
must = c1.multiselect("Must-have skills (other detected skills count as nice-to-have)",
                      detected["skills"], default=detected["skills"], key=f"must_{h}")
min_years = c2.number_input("Minimum years of experience", 0.0, 40.0,
                            float(detected["years"]), 0.5, key=f"yrs_{h}")
edu_options = ["Not required"] + [LEVEL_LABELS[i] for i in range(1, 6)]
edu_label = c3.selectbox("Minimum education", edu_options,
                         index=detected["edu_level"], key=f"edu_{h}")

job = {
    "text": jd,
    "must": set(must),
    "nice": set(detected["skills"]) - set(must),
    "min_years": min_years,
    "min_edu": edu_options.index(edu_label),
}

# ------------------------------------------------------------------ screening
results, problems = [], []
for f in files:
    try:
        text = read_resume(f.name, f.getvalue())
    except Exception as exc:                                   # corrupt or password-protected file
        problems.append(f"{f.name}: could not be opened ({exc})")
        continue
    if not text.strip():
        problems.append(f"{f.name}: no readable text (scanned image PDFs are not supported)")
        continue
    r = score_candidate(text, candidate_info(text, f.name), job, weights, extra, cutoffs)
    r["file"], r["text"] = f.name, text
    results.append(r)

for p in problems:
    st.warning(p)
if not results:
    st.stop()

results.sort(key=lambda r: r["score"], reverse=True)
seen = {}
for i, r in enumerate(results, 1):
    r["rank"] = i
    seen[r["name"]] = seen.get(r["name"], 0) + 1
    r["label"] = r["name"] if seen[r["name"]] == 1 else f"{r['name']} ({r['file']})"

table = pd.DataFrame([{
    "Rank": r["rank"], "Candidate": r["label"], "Score": r["score"], "Prediction": r["verdict"],
    "Skill match %": r["skill_match_pct"], "Experience (yrs)": r["years"],
    "Education": r["education"], "Email": r["email"], "Phone": r["phone"],
    "Missing must-have": ", ".join(r["missing_must"]), "File": r["file"],
} for r in results])

# ------------------------------------------------------------------ results
st.divider()
st.subheader("Results")
scores = [r["score"] for r in results]
m1, m2, m3, m4 = st.columns(4)
m1.metric("Candidates", len(results))
m2.metric("Top score", f"{max(scores):.1f}")
m3.metric("Average score", f"{sum(scores) / len(scores):.1f}")
m4.metric("Strong fits", sum(s >= strong_cut for s in scores))

st.dataframe(
    table, hide_index=True,
    column_config={"Score": st.column_config.ProgressColumn(
        "Score", min_value=0, max_value=100, format="%.1f")})

d1, d2, _ = st.columns([1, 1, 4])
d1.download_button("⬇️ CSV", table.to_csv(index=False).encode("utf-8"),
                   "screening_results.csv", "text/csv")
d2.download_button("⬇️ Excel", to_excel(table), "screening_results.xlsx",
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if len(results) > 1:
    ch1, ch2 = st.columns(2)
    with ch1:
        st.caption("Score by candidate")
        st.bar_chart(table.set_index("Candidate")["Score"])
    with ch2:
        st.caption("Where each score comes from (points)")
        st.bar_chart(pd.DataFrame(
            [{"Candidate": r["label"], "Skills": r["points"]["skills"],
              "Wording": r["points"]["similarity"], "Experience": r["points"]["experience"],
              "Education": r["points"]["education"]} for r in results]).set_index("Candidate"))

# ------------------------------------------------------------------ one candidate
st.divider()
st.subheader("Candidate details")
labels = [r["label"] for r in results]
pick = st.selectbox("Pick a candidate", labels)
r = results[labels.index(pick)]

st.markdown(f"### #{r['rank']}  {r['name']}")
st.caption(" · ".join(x for x in [r["email"], r["phone"], r["education"],
                                  f"{r['years']:g} yrs experience", r["file"]] if x))

banner = f"Prediction: {r['verdict']}  (score {r['score']} / 100)"
if r["score"] >= strong_cut:
    st.success(banner)
elif r["score"] >= moderate_cut:
    st.info(banner)
elif r["score"] >= weak_cut:
    st.warning(banner)
else:
    st.error(banner)

k = st.columns(4)
k[0].metric("Skills", f"{r['components']['skills']:.0f}%")
k[1].metric("Wording", f"{r['components']['similarity']:.0f}%")
k[2].metric("Experience", f"{r['components']['experience']:.0f}%")
k[3].metric("Education", f"{r['components']['education']:.0f}%")

a, b, c = st.columns(3)
a.markdown("**✅ Must-have found**")
a.markdown(chips(r["matched_must"]))
a.markdown("**✅ Nice-to-have found**")
a.markdown(chips(r["matched_nice"]))
b.markdown("**❌ Must-have missing**")
b.markdown(chips(r["missing_must"]))
b.markdown("**⚠️ Nice-to-have missing**")
b.markdown(chips(r["missing_nice"]))
c.markdown("**➕ Other skills in resume**")
c.markdown(chips(r["extra"]))

st.markdown("**💡 Gaps and suggestions**")
for tip in r["suggestions"]:
    st.markdown(f"- {tip}")

with st.expander("Extracted resume text"):
    st.text(r["text"])

with st.expander("How the score is calculated"):
    total = sum(weights.values()) or 1
    st.markdown(
        f"- **Skills match ({100 * w_skills / total:.0f}%)**: must-have skills count double.\n"
        f"- **Wording similarity ({100 * w_sim / total:.0f}%)**: TF-IDF cosine similarity of resume and job text.\n"
        f"- **Experience ({100 * w_exp / total:.0f}%)**: years found in the resume against the minimum.\n"
        f"- **Education ({100 * w_edu / total:.0f}%)**: highest level found against the minimum.\n\n"
        "Experience comes from phrases like '3 years' or dated jobs under an Experience heading. "
        "Skills are matched against the skills list in `skills_db.py` plus any you add in the sidebar.")
