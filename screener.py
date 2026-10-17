"""Skill extraction, matching and scoring."""
import re
from functools import lru_cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skills_db import SKILLS
from parser import lowest_required_education, required_years

# Single letters / common words: only match their longer aliases ("golang", "c programming")
AMBIGUOUS = {"go", "c", "r"}

DEFAULT_WEIGHTS = {"skills": 55, "similarity": 20, "experience": 15, "education": 10}
DEFAULT_CUTOFFS = (75, 55, 35)      # strong, moderate, weak


def _pattern(names):
    body = "|".join(re.escape(n) for n in sorted(set(names), key=len, reverse=True))
    return re.compile(r"(?<![A-Za-z0-9+#.])(" + body + r")(?![A-Za-z0-9+#])", re.I)


@lru_cache(maxsize=32)
def _patterns(extra: tuple):
    pats = {}
    for skill, aliases in SKILLS.items():
        names = list(aliases) if skill in AMBIGUOUS else [skill] + list(aliases)
        if names:
            pats[skill] = _pattern(names)
    for s in extra:                       # skills typed in by the user
        s = s.strip().lower()
        if s and s not in pats:
            pats[s] = _pattern([s])
    return pats


def extract_skills(text: str, extra=()) -> set:
    """Find which known (or user-added) skills appear in the text."""
    text = re.sub(r"\s+", " ", text)      # PDFs often split phrases across lines
    return {skill for skill, pat in _patterns(tuple(extra)).items() if pat.search(text)}


def text_similarity(resume: str, job: str) -> float:
    """Overall wording similarity (0-1) using TF-IDF."""
    try:
        m = TfidfVectorizer(stop_words="english").fit_transform([resume, job])
        return float(cosine_similarity(m[0], m[1])[0][0])
    except ValueError:
        return 0.0


def analyze_job(job_text: str, extra=()) -> dict:
    """What the job description seems to ask for (the user can adjust this in the app)."""
    return {
        "skills": sorted(extract_skills(job_text, extra)),
        "years": required_years(job_text),
        "edu_level": lowest_required_education(job_text),
    }


def verdict_for(score: float, cutoffs=DEFAULT_CUTOFFS) -> str:
    strong, moderate, weak = cutoffs
    if score >= strong:
        return "Strong fit - recommend interview"
    if score >= moderate:
        return "Moderate fit - worth a closer look"
    if score >= weak:
        return "Weak fit - missing key requirements"
    return "Not suitable for this role"


def _suggestions(r: dict, job: dict) -> list:
    tips = []
    if r["missing_must"]:
        tips.append("Required skills not found: " + ", ".join(r["missing_must"]))
    if r["missing_nice"]:
        tips.append("Nice-to-have skills not found: " + ", ".join(r["missing_nice"]))
    if job.get("min_years") and r["years"] < job["min_years"]:
        tips.append(f"Job asks for {job['min_years']:g} years of experience; the resume shows "
                    f"{r['years']:g}. Dated jobs or internships under an 'Experience' heading help.")
    if job.get("min_edu") and r["edu_level"] < job["min_edu"]:
        tips.append("Education level looks lower than the job asks for (or is not stated clearly).")
    if r["similarity_pct"] < 30:
        tips.append("Wording is quite different from the job description; using the job's own "
                    "keywords (where true) improves the match.")
    if not r["email"]:
        tips.append("No email address found in the resume.")
    if not r["phone"]:
        tips.append("No phone number found in the resume.")
    if not tips:
        tips.append("Nothing major missing. Good match for this job.")
    return tips


def score_candidate(resume_text: str, info: dict, job: dict, weights=None,
                    extra=(), cutoffs=DEFAULT_CUTOFFS) -> dict:
    """Compare one resume with a job.

    job = {"text": str, "must": set, "nice": set, "min_years": float, "min_edu": int}
    """
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    total_w = sum(w.values()) or 1

    have = extract_skills(resume_text, extra)
    must, nice = set(job["must"]), set(job["nice"])
    got_must, got_nice = have & must, have & nice

    denom = 2 * len(must) + len(nice)                 # must-have skills count double
    skills_c = (2 * len(got_must) + len(got_nice)) / denom if denom else 0.0

    sim = text_similarity(resume_text, job["text"])
    sim_c = min(sim * 2, 1.0)

    min_years = job.get("min_years", 0) or 0
    exp_c = min(info["years"] / min_years, 1.0) if min_years else 1.0

    min_edu = job.get("min_edu", 0) or 0
    level = info["edu_level"]
    if min_edu:
        edu_c = 1.0 if level >= min_edu else (level / min_edu if level else 0.0)
    else:
        edu_c = 1.0

    comps = {"skills": skills_c, "similarity": sim_c, "experience": exp_c, "education": edu_c}
    points = {k: 100 * w[k] / total_w * comps[k] for k in comps}
    score = round(sum(points.values()), 1)

    r = {
        **info,
        "score": score,
        "verdict": verdict_for(score, cutoffs),
        "matched_must": sorted(got_must),
        "missing_must": sorted(must - have),
        "matched_nice": sorted(got_nice),
        "missing_nice": sorted(nice - have),
        "extra": sorted(have - must - nice),
        "skill_match_pct": round(skills_c * 100, 1),
        "similarity_pct": round(sim * 100, 1),
        "components": {k: round(v * 100, 1) for k, v in comps.items()},
        "points": {k: round(v, 1) for k, v in points.items()},
    }
    r["suggestions"] = _suggestions(r, job)
    return r


# Old single-resume helper, kept so earlier code still works
def screen(resume_text: str, job_text: str) -> dict:
    from parser import candidate_info
    found = extract_skills(job_text)
    job = {"text": job_text, "must": found, "nice": set(),
           "min_years": required_years(job_text), "min_edu": 0}
    return score_candidate(resume_text, candidate_info(resume_text), job)
