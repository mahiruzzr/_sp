from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model: str = Field(
        default="gemini/gemini-3-flash-preview",
        validation_alias=AliasChoices("MODEL", "OPENAI_MODEL"),
        serialization_alias="MODEL",
    )
    google_api_version: str = Field(default="", alias="GOOGLE_API_VERSION")
    google_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GOOGLE_API_KEY", "GEMINI_API_KEY"),
        serialization_alias="GOOGLE_API_KEY",
    )
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    tavily_api_key: str = Field(default="", alias="TAVILY_API_KEY")
    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    frontend_origin: str = Field(default="http://localhost:3000", alias="FRONTEND_ORIGIN")
    max_concurrent_runs: int = Field(default=2, alias="MAX_CONCURRENT_RUNS")
    task_store_limit: int = Field(default=50, alias="TASK_STORE_LIMIT")
    reports_dir: Path = ROOT_DIR / "backend" / "reports"

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    return settings
