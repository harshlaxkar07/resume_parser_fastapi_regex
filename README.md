# Resume Parser API

Turn a PDF résumé into structured fields using pattern matching — no model, no API key, no network call. Text comes out of the PDF, a set of rules runs over it, and the result lands in MySQL ready to read, correct or delete.

Because everything is deterministic, the same résumé always parses the same way, and a run takes milliseconds.

Ships with a web console served by the API itself.

---

## Highlights

| | |
|---|---|
| **No model needed** | Pure pattern matching — deterministic, instant and entirely offline |
| **Twelve fields** | Contact details, links, summary, skills, education, experience, projects, certifications and languages |
| **Editable results** | Every field can be corrected through the API or the console |
| **Original kept** | The uploaded PDF is stored and tracked alongside the parsed data |
| **Full CRUD** | Upload, list, fetch, update and delete |
| **Web console** | Upload, review coverage and correct fields at `/` |

---

## The console

The API serves its own front end — start the server and open the root URL.

**Overview** — headline counts, plus a **field coverage** chart showing how often each of the twelve fields is matched across the whole collection. That view makes it obvious at a glance which fields your résumé set actually carries.

**Upload** — drop in one or several PDFs. Each reports how many of the twelve fields were matched, and the parsed result renders next to the dropzone.

**Résumés** — the full collection in a filterable table. Open a row to read everything that was matched, or open the editor to correct any field in place — list fields are edited one entry per line.

---

## How it works

```
PDF upload
   │
   ├─ 1. Store    the file is written with a UUID name under resumes/
   ├─ 2. Extract  PyMuPDF pulls the text out page by page
   ├─ 3. Clean    whitespace, bullets and layout artefacts are normalised
   ├─ 4. Match    the pattern set pulls out each of the twelve fields
   └─ 5. Save     scalar fields go to columns, list fields are stored as JSON
```

---

## Extracted fields

| Field | Kind |
|---|---|
| `full_name` | text |
| `email` | text |
| `phone_number` | text |
| `linkedin` | text |
| `github` | text |
| `summary` | text |
| `skills` | list |
| `education` | list |
| `experience` | list |
| `projects` | list |
| `certifications` | list |
| `languages` | list |

---

## Tech stack

**API** FastAPI · Uvicorn · Pydantic v2
**Database** MySQL via PyMySQL
**Documents** PyMuPDF
**Front end** Vanilla HTML, CSS and JavaScript — no build step

---

## Getting started

### Prerequisites

- Python 3.12 or newer
- MySQL 8

### 1. Install

```bash
git clone https://github.com/harshlaxkar07/resume_parser_fastapi_regex.git
cd resume_parser_fastapi_regex

# with uv (recommended)
uv sync

# or with pip
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

### 2. Create the schema

```bash
mysql -u root -p < database/schema.sql
```

### 3. Configure

Set your MySQL connection details in `database/connection.py`, or supply them through your environment.

### 4. Run

```bash
uvicorn main:app --reload
```

| URL | What it is |
|---|---|
| `http://localhost:8000/` | The console |
| `http://localhost:8000/docs` | Interactive OpenAPI documentation |
| `http://localhost:8000/health` | Health probe |

---

## API reference

| Method | Path | What it does |
|---|---|---|
| `POST` | `/upload` | Upload a PDF, parse it and store the result |
| `GET` | `/resume` | Every résumé in the collection |
| `GET` | `/resume/{pdf_id}` | One résumé with all its fields |
| `POST` | `/resume/{pdf_id}` | Update any of the twelve fields |
| `DELETE` | `/resume/{pdf_id}` | Remove a résumé and its stored PDF |

### Uploading

```bash
curl -X POST http://localhost:8000/upload -F "file=@resume.pdf"
```

```json
{
  "message": "Resume uploaded successfully.",
  "pdf_id": 7,
  "metadata": {
    "full_name": "Aarav Sharma",
    "email": "aarav.sharma@example.com",
    "phone_number": "+91 98100 11234",
    "linkedin": "https://linkedin.com/in/aarav-sharma",
    "github": "https://github.com/aarav",
    "summary": "Backend engineer focused on reliable services and data pipelines.",
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "education": ["B.Tech Computer Science, Institute of Technology, 2017-2021"],
    "experience": ["Backend Engineer, Razorpay, 2021-present"],
    "projects": ["Document Search Platform"],
    "certifications": ["AWS Certified Developer"],
    "languages": ["English", "Hindi"]
  }
}
```

### Correcting a field

```bash
curl -X POST http://localhost:8000/resume/7 \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Aarav Sharma", "skills": ["Python", "FastAPI", "Kubernetes"]}'
```

---

## Project structure

```
resume_parser_fastapi_regex/
├── main.py                       FastAPI application, CORS and the static mount
├── api/
│   ├── routes.py                 Upload, list, fetch, update and delete endpoints
│   └── schemas.py                Pydantic request and response models
├── extractor/
│   ├── pdf_reader.py             Text extraction with PyMuPDF
│   ├── text_cleaner.py           Normalisation
│   ├── extractor.py              The pattern set
│   └── database_writer.py        Reads and writes
├── database/
│   ├── connection.py             MySQL connection handling
│   └── schema.sql                Table definition
├── crud/resume.py                Query helpers
├── schemas/resume.py             Shared models
├── resumes/                      Stored PDFs
└── frontend/                     The console
```
