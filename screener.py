"""Steps 2-5: extract skills, compare with job, predict suitability, score."""
import re
from skills_db import SKILLS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _build_patterns():
    patterns = {}
    for skill, aliases in SKILLS.items():
        names = [skill] + aliases
        body = "|".join(re.escape(n) for n in names)
        patterns[skill] = re.compile(
            r"(?<![A-Za-z0-9+#.])(" + body + r")(?![A-Za-z0-9+#])", re.I
        )
    return patterns


_PATTERNS = _build_patterns()


def extract_skills(text: str) -> set:
    """Step 2: find which known skills appear in the text."""
    # PDFs often break phrases across lines ("front\noffice"), so flatten whitespace first
    text = re.sub(r"\s+", " ", text)
    return {skill for skill, pat in _PATTERNS.items() if pat.search(text)}


def extract_years(text: str) -> int:
    """Largest 'N years' number mentioned (rough experience estimate)."""
    nums = [int(n) for n in re.findall(r"(\d{1,2})\+?\s*(?:years?|yrs?)", text, re.I)]
    return max(nums) if nums else 0


def text_similarity(resume: str, job: str) -> float:
    """Overall wording similarity (0-1) using TF-IDF."""
    try:
        vec = TfidfVectorizer(stop_words="english")
        m = vec.fit_transform([resume, job])
        return float(cosine_similarity(m[0], m[1])[0][0])
    except ValueError:
        return 0.0


def screen(resume_text: str, job_text: str) -> dict:
    """Steps 3-5: compare, predict, score (0-100)."""
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)

    matched = resume_skills & job_skills
    missing = job_skills - resume_skills
    extra = resume_skills - job_skills

    skill_score = len(matched) / len(job_skills) if job_skills else 0.0
    sim = text_similarity(resume_text, job_text)

    resume_years = extract_years(resume_text)
    job_years = extract_years(job_text)
    exp_score = min(resume_years / job_years, 1.0) if job_years else 1.0

    # Weights: skills 60%, wording similarity 25%, experience 15%
    score = round(100 * (0.60 * skill_score + 0.25 * min(sim * 2, 1.0) + 0.15 * exp_score), 1)

    if score >= 75:
        verdict = "Strong fit - recommend interview"
    elif score >= 55:
        verdict = "Moderate fit - worth a closer look"
    elif score >= 35:
        verdict = "Weak fit - missing key requirements"
    else:
        verdict = "Not suitable for this role"

    return {
        "score": score,
        "verdict": verdict,
        "matched": sorted(matched),
        "missing": sorted(missing),
        "extra": sorted(extra),
        "skill_match_pct": round(skill_score * 100, 1),
        "text_similarity_pct": round(sim * 100, 1),
        "resume_years": resume_years,
        "job_years": job_years,
    }
