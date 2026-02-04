"""
Configuration module for Seoul Daycare Search AI Service
Loads environment variables and provides application settings
"""

from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    VECTOR_INDEX_DIR: Path = DATA_DIR / "vector_index"

    # OpenAI API Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"

    # Azure OpenAI Configuration (Optional)
    AOAI_API_KEY: Optional[str] = None
    AOAI_ENDPOINT: Optional[str] = None
    AOAI_API_VERSION: str = "2024-05-01-preview"
    AOAI_DEPLOY_GPT4O: Optional[str] = None
    AOAI_EMBEDDING_DEPLOYMENT: Optional[str] = None

    # Database Configuration
    DB_PATH: str = "data/processed/daycare.db"

    # Vector Index Configuration
    VECTOR_INDEX_PATH: str = "data/vector_index/faiss.index"
    VECTOR_METADATA_PATH: str = "data/vector_index/metadata.json"

    # API Configuration
    API_HOST: str = "localhost"
    API_PORT: int = 8000

    # Streamlit Configuration
    STREAMLIT_PORT: int = 8501

    # Search Configuration
    TOP_K: int = 10
    SIMILARITY_THRESHOLD: float = 0.7

    # Embedding Configuration
    EMBEDDING_DIMENSION: int = 3072  # text-embedding-3-large dimension
    BATCH_SIZE: int = 100

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False

    def get_db_path(self) -> Path:
        """Get absolute database path"""
        if Path(self.DB_PATH).is_absolute():
            return Path(self.DB_PATH)
        return self.PROJECT_ROOT / self.DB_PATH

    def get_vector_index_path(self) -> Path:
        """Get absolute vector index path"""
        if Path(self.VECTOR_INDEX_PATH).is_absolute():
            return Path(self.VECTOR_INDEX_PATH)
        return self.PROJECT_ROOT / self.VECTOR_INDEX_PATH

    def get_vector_metadata_path(self) -> Path:
        """Get absolute vector metadata path"""
        if Path(self.VECTOR_METADATA_PATH).is_absolute():
            return Path(self.VECTOR_METADATA_PATH)
        return self.PROJECT_ROOT / self.VECTOR_METADATA_PATH


# Global settings instance
settings = Settings()


# Ensure directories exist
settings.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.VECTOR_INDEX_DIR.mkdir(parents=True, exist_ok=True)
