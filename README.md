# 🎓 UniAdvisor

A full-stack Django web application designed to streamline the student admissions process for universities and academic programs. Officers can manage applicants, track events, parse resumes, and make data-informed decisions — all in one place.

🌐 **Live Demo**: [admissionsite-c25a7306aecd.herokuapp.com](https://admissionsite-c25a7306aecd.herokuapp.com)

---

## Features

- Role-based login system: Admins and officers
- Resume parsing using NLP (via `pydparser`, spaCy, NLTK)
- Candidate dashboard with filters by program, college, status, and score
- In-app messaging system between officers and candidates
- Event scheduling and timeline view
- Multi-document upload and preview for each candidate
- Ranking candidates based on customizable criteria

---

## Tech Stack

- **Backend**: Django, PostgreSQL, Gunicorn
- **Frontend**: HTML/CSS, Bootstrap
- **NLP**: spaCy, NLTK, `pydparser`
- **Storage**: Amazon S3 (optional), Django `FileSystemStorage` (default)
- **Deployment**: Heroku

---

## Resume Parsing

Resumes uploaded by officers are automatically parsed using `pydparser`, which extracts:

- Name, Email
- Degree & GPA
- Skills, Experience


**NLP Dependencies (auto-installed at runtime):**
```bash
python -m spacy download en_core_web_sm
python -m nltk.downloader words
python -m nltk.downloader stopwords
