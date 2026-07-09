"""Application configuration."""
from functools import lru_cache
from typing import Optional

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Database
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="dssat_rag")
    POSTGRES_SCHEMA: str = Field(default="public")

    @property
    def DATABASE_URL(self) -> PostgresDsn:
        """Build PostgreSQL database URL."""
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # Qdrant
    QDRANT_HOST: str = Field(default="localhost")
    QDRANT_PORT: int = Field(default=6333)
    QDRANT_API_KEY: Optional[str] = None

    @property
    def QDRANT_URL(self) -> str:
        """Build Qdrant URL."""
        if self.QDRANT_API_KEY:
            return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"
        return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"

    # Application
    APP_NAME: str = Field(default="DSSAT RAG Backend")
    APP_VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=False)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
