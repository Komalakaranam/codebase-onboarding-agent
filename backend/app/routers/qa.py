"""
Question-answering endpoint — step 4 of the RAG pipeline.

POST /repos/{repo_id}/ask
    1. Embed the question (sentence-transformers)
    2. Retrieve the top-k most similar code chunks (ChromaDB)
    3. Ask the Groq LLM to answer using those chunks (generation)
    4. Return the answer plus the file/line references it was grounded in
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import AskQuestionRequest, AskQuestionResponse
from app.services.qa import RepoNotIndexedError, answer_question

router = APIRouter(prefix="/repos", tags=["qa"])


@router.post("/{repo_id}/ask", response_model=AskQuestionResponse)
def ask_question(repo_id: str, request: AskQuestionRequest) -> AskQuestionResponse:
    try:
        return answer_question(repo_id, request.question, top_k=request.top_k)
    except RepoNotIndexedError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        # e.g. GROQ_API_KEY missing from backend/.env
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Groq request failed: {exc}") from exc
