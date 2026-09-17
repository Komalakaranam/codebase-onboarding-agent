"""
Repo overview service — backs the Overview tab.

Files/chunks/languages are cheap facts we already have on disk or in
ChromaDB, so we compute those directly instead of asking the LLM (fast,
free, deterministic). Only the project description needs the LLM: it
reads the repo's README if there is one, or falls back to a handful of
chunks retrieved from ChromaDB, and asks Groq for 2-3 plain sentences.
"""

from __future__ import annotations

from pathlib import Path

from app.config import settings
from app.models.schemas import RepoOverviewResponse
from app.services.embeddings import embed_texts
from app.services.llm_client import get_groq_client
from app.services.qa import RepoNotIndexedError
from app.services.vector_store import get_stored_chunk_count, query_similar_chunks

LANGUAGE_BY_EXTENSION = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
}

DESCRIPTION_SYSTEM_PROMPT = (
    "You're a senior developer writing a one-paragraph project summary for "
    "a teammate's first look at this repo. In 2-3 plain sentences, say what "
    "the project does and how it's put together. No headings, no bullet "
    "points, no hedging phrases — just the summary."
)

README_MAX_CHARS = 4000


def _local_repo_path(repo_id: str) -> Path:
    return settings.data_dir / repo_id


def _detect_languages(local_path: Path) -> list[str]:
    found = set()
    for path in local_path.rglob("*"):
        if not path.is_file():
            continue
        if any(skip in path.parts for skip in settings.skip_dirs):
            continue
        language = LANGUAGE_BY_EXTENSION.get(path.suffix.lower())
        if language:
            found.add(language)
    return sorted(found)


def _count_source_files(local_path: Path) -> int:
    count = 0
    for path in local_path.rglob("*"):
        if not path.is_file():
            continue
        if any(skip in path.parts for skip in settings.skip_dirs):
            continue
        if path.suffix.lower() in settings.supported_extensions:
            count += 1
    return count


def _find_readme(local_path: Path) -> str | None:
    for entry in sorted(local_path.iterdir()):
        if entry.is_file() and entry.name.lower().startswith("readme"):
            try:
                return entry.read_text(encoding="utf-8", errors="ignore")[:README_MAX_CHARS]
            except OSError:
                return None
    return None


def _context_from_chunks(repo_id: str) -> str | None:
    """Fallback when there's no README: summarize from a few retrieved chunks."""
    query_vector = embed_texts(
        ["project overview, main purpose, entry point, and setup"]
    )[0]
    chunks = query_similar_chunks(repo_id, query_vector, top_k=5)
    if not chunks:
        return None

    blocks = []
    for chunk in chunks:
        meta = chunk["metadata"]
        blocks.append(f"# {meta['file_path']}\n{chunk['document']}")
    return "\n\n".join(blocks)


def _generate_description(repo_id: str, local_path: Path) -> str:
    readme = _find_readme(local_path)
    if readme:
        source_label = "the project's README"
        material = readme
    else:
        material = _context_from_chunks(repo_id)
        source_label = "a sample of the project's code"
        if material is None:
            return "No README or indexed code was available to summarize this project."

    client = get_groq_client()
    completion = client.chat.completions.create(
        model=settings.groq_model_name,
        messages=[
            {"role": "system", "content": DESCRIPTION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Here is {source_label}:\n\n{material}\n\nSummarize this project.",
            },
        ],
        temperature=0.3,
        max_tokens=200,
    )
    return (completion.choices[0].message.content or "").strip()


def get_repo_overview(repo_id: str) -> RepoOverviewResponse:
    chunks_found = get_stored_chunk_count(repo_id)
    if chunks_found == 0:
        raise RepoNotIndexedError(
            f"Repo '{repo_id}' has no indexed chunks. Run POST /repos/index first."
        )

    local_path = _local_repo_path(repo_id)
    if not local_path.is_dir():
        raise RepoNotIndexedError(
            f"Repo '{repo_id}' is indexed but its local clone is missing "
            "(was backend/data/ cleared?). Re-index to restore it."
        )

    return RepoOverviewResponse(
        repo_id=repo_id,
        files_scanned=_count_source_files(local_path),
        chunks_found=chunks_found,
        languages=_detect_languages(local_path),
        description=_generate_description(repo_id, local_path),
    )
