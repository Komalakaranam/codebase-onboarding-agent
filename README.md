# Codebase Onboarding Agent

AI-powered tool that lets developers ask natural language questions about a GitHub codebase and get answers with source references (RAG-based).

## Tech stack

| Layer | Choice |
|-------|--------|
| Backend | FastAPI (Python) |
| Frontend | React + Vite *(step 7)* |
| Database | SQLite |
| Vector store | ChromaDB |
| LLM | Groq (Llama 3.1) |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |

## Project layout

```
code-base-project/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── config.py        # Settings & paths
│   │   ├── models/          # Request/response schemas
│   │   ├── routers/         # API routes
│   │   └── services/        # Clone, parse, embed, retrieve
│   ├── data/                # Cloned repos (gitignored)
│   ├── requirements.txt
│   └── .env.example
└── frontend/                # Added in step 7
```

## Backend setup (step 1)

**Prerequisites:** Python 3.11+, [Git](https://git-scm.com/) installed.

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Start the API:

```powershell
uvicorn app.main:app --reload --port 8000
```

Open **http://127.0.0.1:8000/docs** and try `POST /repos/index` with:

```json
{
  "repo_url": "https://github.com/tiangolo/fastapi"
}
```

## Current progress

- [x] **Step 1** — Clone GitHub repo + parse Python/JS files
- [ ] Step 2 — Intelligent chunking refinements
- [ ] Step 3 — Embeddings + ChromaDB
- [ ] Step 4 — Question answering via Groq
- [ ] Step 5 — Source references in answers
- [ ] Step 6 — SQLite chat history
- [ ] Step 7 — React frontend
