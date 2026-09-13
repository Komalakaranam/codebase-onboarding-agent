"""
Pydantic models define the shape of API requests and responses.

FastAPI uses these for automatic validation and OpenAPI docs.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class IndexStatus(str, Enum):
    """Lifecycle of a repo indexing job."""

    pending = "pending"
    cloning = "cloning"
    parsing = "parsing"
    completed = "completed"
    failed = "failed"


class IndexRepoRequest(BaseModel):
    """Body sent when a user submits a GitHub repo URL."""

    repo_url: HttpUrl = Field(
        ...,
        description="Public GitHub repository URL, e.g. https://github.com/user/repo",
        examples=["https://github.com/tiangolo/fastapi"],
    )


class ParsedChunkPreview(BaseModel):
    """
    One logical unit of code extracted from a file.

    In step 2 we'll refine chunking; for step 1 this shows what the parser found.
    """

    file_path: str
    chunk_type: str  # e.g. "function", "class", "module"
    name: str | None = None
    start_line: int
    end_line: int
    content_preview: str  # First ~200 chars so responses stay small


class IndexRepoResponse(BaseModel):
    """Returned after cloning + parsing a repository."""

    repo_id: str
    repo_url: str
    repo_name: str
    local_path: str
    status: IndexStatus
    files_scanned: int
    chunks_found: int
    chunks: list[ParsedChunkPreview]
    indexed_at: datetime
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
