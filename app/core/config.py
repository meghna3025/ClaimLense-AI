"""
Application configuration via pydantic-settings.
All values can be overridden through environment variables or a .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Google Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_vision_model: str = "gemini-2.0-flash"

    # FAISS index base directory (sub-dirs: policies/, repair_catalog/, etc.)
    chroma_persist_dir: str = "./rag/faiss_db"

    # RAG source paths
    rag_policies_dir: str = "./rag/policies"
    rag_repair_dir: str = "./rag/repair_catalog"
    rag_fraud_dir: str = "./rag/fraud_rules"
    rag_claims_dir: str = "./rag/claims_history"

    # Application
    app_env: str = "development"
    log_level: str = "INFO"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
