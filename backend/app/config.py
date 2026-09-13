"""
Application settings loaded from environment variables.

We use pydantic-settings so values can come from a .env file or the shell.
This keeps secrets (like GROQ_API_KEY) out of source code.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# backend/ directory (one level above app/)
BACKEND_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Groq LLM key — required later for the Q&A step, optional for step 1
    groq_api_key: str = ""

    # Where cloned GitHub repos are stored on disk
    data_dir: Path = BACKEND_ROOT / "data"

    # SQLite database file (used in step 6)
    database_url: str = f"sqlite:///{BACKEND_ROOT / 'onboarding_agent.db'}"

    # File extensions we index in step 1
    supported_extensions: tuple[str, ...] = (".py", ".js", ".jsx", ".ts", ".tsx")

    # Directories to skip when walking a cloned repo
    skip_dirs: tuple[str, ...] = (
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
        ".next",
        "coverage",
    )


settings = Settings()

# Ensure runtime folders exist
settings.data_dir.mkdir(parents=True, exist_ok=True)
