"""
Repository indexing endpoints.

POST /repos/index — clone a GitHub repo and parse its source files.
This is step 1 of the RAG pipeline (ingestion).
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    IndexRepoRequest,
    IndexRepoResponse,
    IndexStatus,
    ParsedChunkPreview,
)
from app.services.github import GitHubCloneError, clone_github_repo
from app.services.parser import parse_repository

router = APIRouter(prefix="/repos", tags=["repos"])

# In-memory store for parsed repos until we add SQLite/Chroma in later steps.
# Key = repo_id (owner__repo), value = full parse result metadata.
_index_cache: dict[str, dict] = {}


def _preview_content(content: str, limit: int = 200) -> str:
    text = content.strip().replace("\n", " ")
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


@router.post("/index", response_model=IndexRepoResponse)
def index_repository(request: IndexRepoRequest) -> IndexRepoResponse:
    """
    Clone a public GitHub repository and parse Python/JS source files.

    Flow:
      1. Validate & clone the repo to backend/data/
      2. Walk the file tree and parse each supported file
      3. Return a summary + preview of extracted code chunks
    """
    repo_url = str(request.repo_url)

    try:
        local_path, owner, repo_name = clone_github_repo(repo_url)
    except GitHubCloneError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    repo_id = f"{owner}__{repo_name}"

    try:
        chunks, files_scanned = parse_repository(local_path)
    except Exception as exc:  # noqa: BLE001 — surface unexpected parse errors clearly
        raise HTTPException(
            status_code=500,
            detail=f"Repository cloned but parsing failed: {exc}",
        ) from exc

    indexed_at = datetime.now(timezone.utc)

    preview_chunks = [
        ParsedChunkPreview(
            file_path=chunk.file_path,
            chunk_type=chunk.chunk_type,
            name=chunk.name,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            content_preview=_preview_content(chunk.content),
        )
        for chunk in chunks[:50]  # cap preview list so response stays readable
    ]

    response = IndexRepoResponse(
        repo_id=repo_id,
        repo_url=repo_url,
        repo_name=f"{owner}/{repo_name}",
        local_path=str(local_path),
        status=IndexStatus.completed,
        files_scanned=files_scanned,
        chunks_found=len(chunks),
        chunks=preview_chunks,
        indexed_at=indexed_at,
        message=(
            f"Successfully indexed {files_scanned} files and extracted "
            f"{len(chunks)} code chunks. Embedding step comes next."
        ),
    )

    # Cache full chunk list for later embedding step
    _index_cache[repo_id] = {
        "response": response,
        "chunks": chunks,
    }

    return response


@router.get("/{repo_id}/summary")
def get_repo_summary(repo_id: str) -> dict:
    """Quick lookup to see if a repo was already indexed in this server session."""
    cached = _index_cache.get(repo_id)
    if not cached:
        raise HTTPException(status_code=404, detail="Repo not indexed in this session.")
    resp: IndexRepoResponse = cached["response"]
    return {
        "repo_id": resp.repo_id,
        "repo_name": resp.repo_name,
        "files_scanned": resp.files_scanned,
        "chunks_found": resp.chunks_found,
        "indexed_at": resp.indexed_at,
    }
