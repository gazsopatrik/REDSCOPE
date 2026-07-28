from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of backend package
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_FILE = BASE_DIR / "redscope_dev.db"


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "RedScope"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "redscope_super_secret_development_key_change_in_production_32bytes"

    # Persistent SQLite Database URL (absolute path prevents working directory mismatches)
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DEFAULT_DB_FILE.as_posix()}"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Scanner & Paths
    NMAP_PATH: str = "nmap"
    NMAP_DEFAULT_TIMEOUT: int = 1800
    SCANS_DIR: Path = BASE_DIR / "scans_raw"
    REPORTS_DIR: Path = BASE_DIR / "reports_gen"

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
