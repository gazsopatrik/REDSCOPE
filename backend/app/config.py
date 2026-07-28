from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "RedScope"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "redscope_super_secret_development_key_change_in_production_32bytes"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./redscope_dev.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Scanner & Paths
    NMAP_PATH: str = "nmap"
    NMAP_DEFAULT_TIMEOUT: int = 1800
    SCANS_DIR: Path = Path("./scans_raw")
    REPORTS_DIR: Path = Path("./reports_gen")

    # Safety Thresholds
    MAX_CONCURRENT_SCANS: int = 4
    MAX_TARGETS_PER_PROJECT: int = 256
    MAX_CIDR_PREFIX: int = 20
    SAFE_VALIDATION_REQUIRE_APPROVAL: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
