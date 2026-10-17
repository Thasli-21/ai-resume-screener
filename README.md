# AI Resume Screening System

Upload a resume → extract skills → compare with job requirements → predict suitability → score (0-100).

## Folder layout (all 5 files go in ONE folder called `resume-screener`)

```
resume-screener/
├── requirements.txt   # libraries to install
├── skills_db.py       # list of skills the system knows (edit to add more)
├── parser.py          # reads PDF / DOCX / TXT resume -> text
├── screener.py        # extracts skills, compares, scores, predicts
└── app.py             # the web page (upload + results)
```

## Setup (type these in Command Prompt / Terminal)

1. Install Python 3.9+ from python.org (tick "Add Python to PATH").
2. Open Terminal (Mac/Linux) or Command Prompt (Windows) and go into the folder:
   ```
   cd path/to/resume-screener
   ```
3. Install libraries (type once):
   ```
   pip install -r requirements.txt
   ```
4. Start the app:
   ```
   streamlit run app.py
   ```
5. Your browser opens at http://localhost:8501

## Using it (type/click inside the web page)

- Left box: click **Browse files** and upload the resume (PDF, DOCX or TXT).
- Right box: paste the job description (skills, years of experience).
- Click **Screen resume**.

## How the score is made

| Part | Weight | How |
|---|---|---|
| Skill match | 60% | skills in resume that the job also asks for |
| Text similarity | 25% | TF-IDF cosine similarity of resume vs job text |
| Experience | 15% | years in resume vs years asked in job |

Prediction: 75+ strong fit, 55-74 moderate, 35-54 weak, below 35 not suitable.

## Customize

- Add skills: open `skills_db.py`, add a line like `"figma": ["figma design"],`
- Change weights / cut-offs: open `screener.py`, edit the `score = ...` line and the `if score >= ...` lines.

## Limits

Scanned-image PDFs have no text and cannot be read (needs OCR). Skills not in `skills_db.py` are not detected.
